from beanie import Document, PydanticObjectId
from typing import Optional
from datetime import datetime

class Subscription(Document):
    organization_id: PydanticObjectId
    stripe_subscription_id: Optional[str] = None
    plan_tier: str = "free"
    status: str = "active"
    current_period_end: Optional[datetime] = None

    class Settings:
        name = "subscriptions"
