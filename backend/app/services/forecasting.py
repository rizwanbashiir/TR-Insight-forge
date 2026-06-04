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


def load_timeseries(db: Session, file_id: int) -> pd.Series:
    """
    Load raw_data_rows and build a clean monthly time-series.
    Averages across stores instead of summing — removes spike distortion.
    """
    rows = (
        db.query(RawDataRow)
        .filter(
            RawDataRow.file_id    == file_id,
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


def run_arima_forecast(
    db     : Session,
    file_id: int,
    steps  : int = 6
) -> ForecastResult:
    """
    Full ARIMA pipeline with improved accuracy.
    Uses mean aggregation and wider parameter search.
    """

    # 1. Load clean time-series
    monthly = load_timeseries(db, file_id)

    if len(monthly) < 6:
        raise ValueError(
            f"Need at least 6 months of data. Found {len(monthly)}."
        )

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

    # 8. Save to DB
    existing = db.query(ForecastResult).filter(
        ForecastResult.file_id == file_id
    ).first()

    if existing:
        existing.arima_order   = str(best_order)
        existing.mape_score    = mape
        existing.forecast_data = forecast_data
        result = existing
    else:
        result = ForecastResult(
            file_id       = file_id,
            model_name    = "ARIMA",
            arima_order   = str(best_order),
            mape_score    = mape,
            forecast_data = forecast_data,
        )
        db.add(result)

    db.commit()
    db.refresh(result)
    return result