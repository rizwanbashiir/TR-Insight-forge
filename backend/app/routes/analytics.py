from fastapi import APIRouter
import pandas as pd

from app.services.kpi_service import generate_kpis

router = APIRouter()


@router.get("/kpi")
def get_kpis():
    """
    Generate KPIs using sample dataset
    """

    df = pd.read_csv("data/raw/dirty_sales_data.csv")

    kpis = generate_kpis(df)

    return {
        "status": "success",
        "kpi_report": kpis
    }