from beanie import Document, PydanticObjectId
from pydantic import Field
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

class ForecastResult(Document):
    file_id: PydanticObjectId
    model_name: str = "ARIMA"
    arima_order: Optional[str] = None
    mape_score: Optional[float] = None
    forecast_data: Optional[Any] = None
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "forecast_results"
        indexes = ["file_id"]