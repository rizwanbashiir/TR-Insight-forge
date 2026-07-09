from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime, timezone

class Organization(Document):
    name: str
    industry: Optional[str] = None
    team_size: Optional[str] = None
    stripe_customer_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "organizations"
