from beanie import Document, PydanticObjectId
from pydantic import Field
from typing import Optional, Dict, Any
from datetime import datetime, timezone

class ProcessedDataset(Document):
    file_id: PydanticObjectId
    total_rows: Optional[int] = None
    valid_rows: Optional[int] = None
    duplicate_count: Optional[int] = None
    missing_values: Optional[Dict[str, Any]] = None
    outliers_detected: Optional[Dict[str, Any]] = None
    column_types: Optional[Dict[str, Any]] = None
    kpi_summary: Optional[Dict[str, Any]] = None
    processed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "processed_datasets"
        indexes = ["file_id"]