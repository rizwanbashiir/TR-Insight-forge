from fastapi import APIRouter
import pandas as pd

from app.services.kpi_service import generate_kpis
from app.services.forecasting import run_arima_forecast
from app.services.segmentation import run_customer_segmentation
from app.services.prompt_builder import build_business_prompt
from app.services.grok_service import get_grok_recommendations

router = APIRouter()


@router.get("/insights")
def generate_ai_insights():
    """
    Generate AI-powered business recommendations
    """

    df = pd.read_csv("data/raw/dirty_sales_data.csv")
    forecast_df = pd.read_csv("data/raw/forecast_sales_data.csv")

    kpis = generate_kpis(df)
    forecast = run_arima_forecast(forecast_df)
    segments = run_customer_segmentation(df)

    prompt = build_business_prompt(
        kpis,
        forecast,
        segments
    )

    result = get_grok_recommendations(prompt)

    return {
        "status": "success",
        "ai_recommendations": result
    }