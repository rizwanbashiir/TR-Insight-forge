import pandas as pd
from statsmodels.tsa.arima.model import ARIMA


def run_arima_forecast(df: pd.DataFrame):
    """
    Revenue forecasting using ARIMA
    """

    # Convert date
    df["date"] = pd.to_datetime(df["date"])

    # Monthly revenue aggregation
    monthly_sales = (
        df.groupby(
            pd.Grouper(key="date", freq="M")
        )["total_sales"]
        .sum()
        .reset_index()
    )

    # Need enough data
    if len(monthly_sales) < 3:
        return {
            "error": "Not enough time-series data for ARIMA forecasting"
        }

    # Train model
    model = ARIMA(
        monthly_sales["total_sales"],
        order=(1, 1, 1)
    )

    fitted_model = model.fit()

    # Forecast next 6 months
    forecast = fitted_model.forecast(steps=6)

    forecast_values = [
        round(float(value), 2)
        for value in forecast
    ]

    return {
        "historical_monthly_sales": monthly_sales.to_dict(orient="records"),
        "next_6_month_forecast": forecast_values
    }