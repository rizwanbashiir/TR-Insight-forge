import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
import warnings
warnings.filterwarnings("ignore")   # suppress ARIMA convergence warnings

from app.models.raw_data_row import RawDataRow
from app.models.forecast_result import ForecastResult
from app.models.uploaded_file import UploadedFile


# ── Step 1: Load time-series data from DB ────────────────────────────
def load_timeseries(db: Session, file_id: int) -> pd.DataFrame:
    """
    Load raw_data_rows and build a monthly time-series DataFrame.
    Uses the pre-extracted date_col and amount_col for speed.
    """
    rows = (
        db.query(RawDataRow)
        .filter(
            RawDataRow.file_id   == file_id,
            RawDataRow.date_col  != None,
            RawDataRow.amount_col!= None,
        )
        .order_by(RawDataRow.date_col)
        .all()
    )

    if not rows:
        raise ValueError(
            "No rows with date and amount columns found. "
            "Make sure your file has date and sales/amount columns."
        )

    # Build DataFrame from extracted columns
    records = [
        {
            "date"  : row.date_col,
            "amount": float(row.amount_col)
        }
        for row in rows
    ]

    df          = pd.DataFrame(records)
    df["date"]  = pd.to_datetime(df["date"])
    df          = df.set_index("date")

    # Aggregate to monthly totals
    monthly = df["amount"].resample("M").sum()

    return monthly


# ── Step 2: Find best ARIMA order ────────────────────────────────────
def find_best_arima_order(series: pd.Series) -> tuple:
    """
    Try common ARIMA (p,d,q) combinations and pick the one
    with the lowest AIC score. Simple grid search.
    """
    best_aic   = float("inf")
    best_order = (1, 1, 1)      # safe default

    # Check if series needs differencing (d parameter)
    try:
        adf_result = adfuller(series.dropna())
        d = 0 if adf_result[1] < 0.05 else 1
    except Exception:
        d = 1

    # Grid search over p and q
    for p in range(0, 4):
        for q in range(0, 4):
            try:
                model  = ARIMA(series, order=(p, d, q))
                fitted = model.fit()
                if fitted.aic < best_aic:
                    best_aic   = fitted.aic
                    best_order = (p, d, q)
            except Exception:
                continue

    return best_order


# ── Step 3: Compute MAPE ─────────────────────────────────────────────
def compute_mape(actual: pd.Series, predicted: pd.Series) -> float:
    """
    Mean Absolute Percentage Error.
    Target: < 6% (forecast accuracy > 94%).
    """
    actual    = actual.replace(0, np.nan).dropna()
    predicted = predicted.reindex(actual.index).dropna()
    common    = actual.index.intersection(predicted.index)

    if len(common) == 0:
        return 0.0

    mape = (
        abs(actual[common] - predicted[common]) / abs(actual[common])
    ).mean() * 100

    return round(float(mape), 2)


# ── Step 4: Run full ARIMA pipeline ──────────────────────────────────
def run_arima_forecast(
    db      : Session,
    file_id : int,
    steps   : int = 6
) -> ForecastResult:
    """
    Full ARIMA pipeline:
    1. Load monthly time-series from DB
    2. Find best (p,d,q) order
    3. Train on 80% of data, validate on 20%
    4. Forecast next {steps} months
    5. Save to forecast_results table
    """

    # 1. Load
    monthly = load_timeseries(db, file_id)

    if len(monthly) < 6:
        raise ValueError(
            f"Need at least 6 months of data for forecasting. "
            f"Found only {len(monthly)} months."
        )

    # 2. Train/test split (80/20)
    split_idx  = int(len(monthly) * 0.8)
    train      = monthly.iloc[:split_idx]
    test       = monthly.iloc[split_idx:]

    # 3. Find best order
    best_order = find_best_arima_order(train)

    # 4. Train final model on full data
    model      = ARIMA(monthly, order=best_order)
    fitted     = model.fit()

    # 5. Validate — predict on test set
    test_predictions = fitted.predict(
        start=test.index[0],
        end  =test.index[-1],
    )
    mape = compute_mape(test, test_predictions)

    # 6. Forecast next N months
    forecast_result = fitted.get_forecast(steps=steps)
    forecast_mean   = forecast_result.predicted_mean
    forecast_ci     = forecast_result.conf_int(alpha=0.05)  # 95% CI

    # 7. Build historical data list
    historical = [
        {
            "date" : str(date.strftime("%Y-%m")),
            "value": round(float(val), 2),
        }
        for date, val in monthly.items()
    ]

    # 8. Build forecast list with confidence intervals
    forecast_list = []
    for date, val in forecast_mean.items():
        lower = float(forecast_ci.loc[date].iloc[0])
        upper = float(forecast_ci.loc[date].iloc[1])
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

    # 9. Save to DB
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