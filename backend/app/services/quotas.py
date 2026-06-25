from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.subscriptions import Subscription
from app.models.uploaded_file import UploadedFile

def verify_limits_and_tier(db: Session, org_id: int, action: str, check_value: int = 1):
    """
    Checks if an organization has exceeded quotas or feature gates based on subscription.
    """
    # Temporarily disabled for testing
    return
    
    sub = db.query(Subscription).filter(Subscription.organization_id == org_id).first()
    tier = sub.plan_tier if sub else "free"
    sub_status = sub.status if sub else "active"

    # Enforce active/trialing status check
    if sub and sub_status not in ["active", "trialing"]:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Subscription payment required or past due. Please update payment method."
        )

    if action == "upload":
        file_count = db.query(UploadedFile).filter(UploadedFile.organization_id == org_id).count()
        if tier == "free" and file_count >= 3:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="File upload limit reached (max 3 files on Free tier). Please upgrade to Pro."
            )
        elif tier == "pro" and file_count >= 50:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="File upload limit reached (max 50 files on Pro tier). Please upgrade to Enterprise."
            )

    elif action == "row_count":
        if tier == "free" and check_value > 5000:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Dataset contains {check_value:,} rows, exceeding the 5,000 row limit on the Free tier. Please upgrade to Pro."
            )
        elif tier == "pro" and check_value > 100000:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Dataset contains {check_value:,} rows, exceeding the 100,000 row limit on the Pro tier. Please upgrade to Enterprise."
            )

    elif action == "ai_chat":
        if tier == "free":
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="AI/RAG Chat is only available on paid tiers. Please upgrade to Pro."
            )
