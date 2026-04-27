from fastapi import APIRouter
import pandas as pd
from app.services.segmentation import run_customer_segmentation

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
@router.get("/segmentation")
def get_segmentation():
    """
    Customer segmentation using RFM + KMeans
    """

    df = pd.read_csv("data/raw/dirty_sales_data.csv")

    result = run_customer_segmentation(df)

    return {
        "status": "success",
        "segmentation_report": result
    }