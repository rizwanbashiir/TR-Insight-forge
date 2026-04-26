from fastapi import APIRouter
import pandas as pd

from app.services.forecasting import run_arima_forecast

router = APIRouter()


@router.get("/forecast")
def get_forecast():
    """
    Revenue Forecast using ARIMA
    """

    df = pd.read_csv("data/raw/forecast_sales_data.csv")

    result = run_arima_forecast(df)

    return {
        "status": "success",
        "forecast_report": result
    }