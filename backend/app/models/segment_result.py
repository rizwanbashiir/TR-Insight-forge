from beanie import Document, PydanticObjectId
from pydantic import Field
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

class SegmentResult(Document):
    file_id: PydanticObjectId
    silhouette_score: Optional[float] = None
    segment_data: Optional[Any] = None
    rfm_scores: Optional[Any] = None
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "segment_results"
        indexes = ["file_id"]