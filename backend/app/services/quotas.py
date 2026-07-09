from fastapi import HTTPException, status

from app.models.subscriptions import Subscription
from app.models.uploaded_file import UploadedFile

async def verify_limits_and_tier(db, org_id, action: str, check_value: int = 1):
    """
    Checks if an organization has exceeded quotas or feature gates based on subscription.
    """
    # Billing and quota checks disabled for now
    return
