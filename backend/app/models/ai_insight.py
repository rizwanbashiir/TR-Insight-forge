from beanie import Document, PydanticObjectId
from pydantic import Field
from typing import Optional
from datetime import datetime, timezone

class AIInsight(Document):
    file_id: PydanticObjectId
    model_name: Optional[str] = None
    prompt_used: Optional[str] = None
    ai_response: Optional[str] = None
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "ai_insights"
        indexes = ["file_id"]

# Alias for backward compatibility
AiInsight = AIInsight