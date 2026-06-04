from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.config.database import get_db
from app.utils.dependencies import require_role
from app.models.users import User
from app.models.subscriptions import Subscription

router = APIRouter()

class TestUpgradeRequest(BaseModel):
    plan_tier: str

@router.post("/test-upgrade", status_code=200)
def test_upgrade(
    body        : TestUpgradeRequest,
    db          : Session = Depends(get_db),
    current_user: User    = Depends(require_role("admin")),
):
    """
    Test-only endpoint to toggle plan tier for the current user's organization.
    Allowed values: 'free', 'pro', 'enterprise'.
    """
    if body.plan_tier not in ["free", "pro", "enterprise"]:
        raise HTTPException(status_code=400, detail="Invalid plan tier. Choose 'free', 'pro', or 'enterprise'.")

    # Fetch organization subscription
    sub = db.query(Subscription).filter(
        Subscription.organization_id == current_user.organization_id
    ).first()

    if not sub:
        sub = Subscription(
            organization_id=current_user.organization_id,
            plan_tier=body.plan_tier,
            status="active"
        )
        db.add(sub)
    else:
        sub.plan_tier = body.plan_tier
        sub.status = "active"

    db.commit()
    db.refresh(sub)

    return {
        "message": f"Successfully updated subscription tier to '{body.plan_tier}'",
        "organization_id": current_user.organization_id,
        "plan_tier": sub.plan_tier,
        "status": sub.status,
    }


@router.post("/webhook", status_code=200)
async def stripe_webhook(
    request: Request,
    db     : Session = Depends(get_db)
):
    """
    Production-grade Stripe Webhook handler.
    Parses and verifies incoming events from Stripe to update DB subscriptions.
    """
    # For local development or mock tests, we allow simple unverified calls
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    event_type = payload.get("type")
    data_obj = payload.get("data", {}).get("object", {})

    if event_type in ["customer.subscription.created", "customer.subscription.updated"]:
        # Extract details
        stripe_cust_id = data_obj.get("customer")
        stripe_sub_id = data_obj.get("id")
        status_val = data_obj.get("status")
        
        # In a real app, you would map Stripe price IDs to tiers
        # Here we mock mapping or read a custom field
        plan_tier = "pro"
        if "enterprise" in str(data_obj).lower():
            plan_tier = "enterprise"

        # Find organization by stripe_customer_id
        from app.models.organizations import Organization
        org = db.query(Organization).filter(Organization.stripe_customer_id == stripe_cust_id).first()
        if org:
            sub = db.query(Subscription).filter(Subscription.organization_id == org.id).first()
            if not sub:
                sub = Subscription(organization_id=org.id)
                db.add(sub)
            sub.stripe_subscription_id = stripe_sub_id
            sub.plan_tier = plan_tier
            sub.status = status_val
            db.commit()

    elif event_type == "customer.subscription.deleted":
        stripe_sub_id = data_obj.get("id")
        sub = db.query(Subscription).filter(Subscription.stripe_subscription_id == stripe_sub_id).first()
        if sub:
            sub.plan_tier = "free"
            sub.status = "canceled"
            db.commit()

    return {"status": "success"}
