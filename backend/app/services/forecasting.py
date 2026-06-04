import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
import warnings
warnings.filterwarnings("ignore")

from app.models.raw_data_row import RawDataRow
from app.models.forecast_result import ForecastResult
from app.models.uploaded_file import UploadedFile


from typing import Union, List

def load_timeseries(db: Session, file_ids: Union[int, List[int]]) -> pd.Series:
    """
    Load raw_data_rows and build a clean monthly time-series.
    Averages across stores instead of summing — removes spike distortion.
    """
    if isinstance(file_ids, int):
        file_ids = [file_ids]

    rows = (
        db.query(RawDataRow)
        .filter(
            RawDataRow.file_id.in_(file_ids),
            RawDataRow.date_col   != None,
            RawDataRow.amount_col != None,
        )
        .order_by(RawDataRow.date_col)
        .all()
    )

    if not rows:
        raise ValueError(
            "No rows with date and amount columns found. "
            "Make sure your file has date and sales/amount columns, "
            "then re-upload or run the patch script."
        )

    records = [
        {"date": row.date_col, "amount": float(row.amount_col)}
        for row in rows
    ]

    df         = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    df         = df.set_index("date")

    # Use MEAN per month instead of SUM
    # This removes the distortion caused by multiple stores
    monthly = df["amount"].resample("M").mean()

    # Remove any extreme outliers using IQR
    Q1    = monthly.quantile(0.25)
    Q3    = monthly.quantile(0.75)
    IQR   = Q3 - Q1
    lower = Q1 - 3.0 * IQR
    upper = Q3 + 3.0 * IQR
    monthly = monthly.clip(lower=lower, upper=upper)

    return monthly


def find_best_arima_order(series: pd.Series) -> tuple:
    """
    Find best ARIMA order using AIC score.
    Wider search range for better accuracy.
    """
    best_aic   = float("inf")
    best_order = (1, 1, 1)

    # Check stationarity
    try:
        adf_pvalue = adfuller(series.dropna())[1]
        d = 0 if adf_pvalue < 0.05 else 1
    except Exception:
        d = 1

    # Wider grid search
    for p in range(0, 5):
        for q in range(0, 5):
            for d_val in [d, 1]:
                try:
                    model  = ARIMA(series, order=(p, d_val, q))
                    fitted = model.fit()
                    if fitted.aic < best_aic:
                        best_aic   = fitted.aic
                        best_order = (p, d_val, q)
                except Exception:
                    continue

    return best_order


def compute_mape(actual: pd.Series, predicted: pd.Series) -> float:
    """Mean Absolute Percentage Error — target < 15%."""
    actual    = actual.replace(0, np.nan).dropna()
    predicted = predicted.reindex(actual.index).dropna()
    common    = actual.index.intersection(predicted.index)

    if len(common) == 0:
        return 0.0

    mape = (
        abs(actual[common] - predicted[common]) / abs(actual[common])
    ).mean() * 100

    return round(float(mape), 2)


def run_fallback_forecast(monthly: pd.Series, steps: int) -> dict:
    """
    Fallback forecasting for short time-series (< 6 months).
    Fits a linear regression trend line or projects flat.
    """
    n = len(monthly)
    historical = [
        {"date": str(d.strftime("%Y-%m")), "value": round(float(v), 2)}
        for d, v in monthly.items()
    ]

    forecast_list = []
    last_date = monthly.index[-1]
    # Generate future dates
    future_dates = pd.date_range(
        start=last_date + pd.offsets.MonthEnd(1),
        periods=steps,
        freq="M"
    )

    if n >= 2:
        x = np.arange(n)
        y = monthly.values
        m, c = np.polyfit(x, y, 1)

        # Estimate standard deviation of residuals for confidence intervals
        residuals = y - (m * x + c)
        std_err = np.std(residuals) if len(residuals) > 1 else np.std(y) * 0.1
        if std_err == 0:
            std_err = y.mean() * 0.1 if y.mean() != 0 else 1.0

        for i, date in enumerate(future_dates):
            val = m * (n + i) + c
            # Prevent negative sales sales forecast if historical data is strictly non-negative
            if (y >= 0).all() and val < 0:
                val = 0.0
            lower = val - 1.96 * std_err
            upper = val + 1.96 * std_err
            forecast_list.append({
                "date"    : str(date.strftime("%Y-%m")),
                "value"   : round(float(val), 2),
                "lower_ci": round(float(max(0.0, lower) if (y >= 0).all() else lower), 2),
                "upper_ci": round(float(upper), 2),
            })
        mape_score = compute_mape(monthly, pd.Series(m * x + c, index=monthly.index))
        arima_order = "Fallback (LR)"
    else:
        val = float(monthly.values[0]) if n == 1 else 0.0
        std_err = val * 0.1 if val != 0 else 1.0
        for date in future_dates:
            lower = val - 1.96 * std_err
            upper = val + 1.96 * std_err
            forecast_list.append({
                "date"    : str(date.strftime("%Y-%m")),
                "value"   : round(val, 2),
                "lower_ci": round(float(max(0.0, lower)), 2),
                "upper_ci": round(float(upper), 2),
            })
        mape_score = 0.0
        arima_order = "Fallback (Flat)"

    return {
        "historical": historical,
        "forecast"  : forecast_list,
        "mape_score": mape_score,
        "arima_order": arima_order,
    }


def run_arima_forecast(
    db      : Session,
    file_ids: Union[int, List[int]],
    steps   : int = 6
) -> ForecastResult:
    """
    Full ARIMA pipeline with improved accuracy.
    Uses mean aggregation and wider parameter search.
    """
    if isinstance(file_ids, int):
        file_ids = [file_ids]

    primary_file_id = file_ids[0]

    # 1. Load clean time-series
    monthly = load_timeseries(db, file_ids)

    if len(monthly) == 0:
        raise ValueError("No historical monthly data found to run forecast.")

    model_name = "ARIMA"
    if len(monthly) < 6:
        # Fallback to linear regression/flat projection
        fallback_res = run_fallback_forecast(monthly, steps)
        best_order = fallback_res["arima_order"]
        mape = fallback_res["mape_score"]
        forecast_data = {
            "historical": fallback_res["historical"],
            "forecast"  : fallback_res["forecast"],
        }
        model_name = "Linear Regression (Fallback)" if len(monthly) >= 2 else "Flat Projection (Fallback)"
    else:
        # 2. Train/test split 80/20
        split_idx = int(len(monthly) * 0.8)
        train     = monthly.iloc[:split_idx]
        test      = monthly.iloc[split_idx:]

        # 3. Find best order on training data
        best_order = find_best_arima_order(train)

        # 4. Fit on full data
        model  = ARIMA(monthly, order=best_order)
        fitted = model.fit()

        # 5. Validate on test set
        test_pred = fitted.predict(
            start=test.index[0],
            end  =test.index[-1],
        )
        mape = compute_mape(test, test_pred)

        # 6. Forecast next N months
        fc_result = fitted.get_forecast(steps=steps)
        fc_mean   = fc_result.predicted_mean
        fc_ci     = fc_result.conf_int(alpha=0.05)

        # 7. Build response data
        historical = [
            {"date": str(d.strftime("%Y-%m")), "value": round(float(v), 2)}
            for d, v in monthly.items()
        ]

        forecast_list = []
        for date, val in fc_mean.items():
            lower = float(fc_ci.loc[date].iloc[0])
            upper = float(fc_ci.loc[date].iloc[1])
            forecast_list.append({
                "date"    : str(date.strftime("%Y-%m")),
                "value"   : round(float(val), 2),
                "lower_ci": round(lower, 2),
                "upper_ci": round(upper, 2),
            })

        forecast_data = {
            "historical": historical,
            "forecast"  : forecast_list,
        }

    # Store associated file IDs in the forecast data
    forecast_data["associated_file_ids"] = file_ids

    # 8. Save to DB under primary file ID
    existing = db.query(ForecastResult).filter(
        ForecastResult.file_id == primary_file_id
    ).first()

    if existing:
        existing.model_name    = model_name
        existing.arima_order   = str(best_order)
        existing.mape_score    = mape
        existing.forecast_data = forecast_data
        result = existing
    else:
        result = ForecastResult(
            file_id       = primary_file_id,
            model_name    = model_name,
            arima_order   = str(best_order),
            mape_score    = mape,
            forecast_data = forecast_data,
        )
        db.add(result)

    db.commit()
    db.refresh(result)
    return result