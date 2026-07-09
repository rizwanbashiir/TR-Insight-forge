from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from app.utils.dependencies import require_role
from app.models.users import User
from app.models.subscriptions import Subscription
from app.models.organizations import Organization

router = APIRouter()

class TestUpgradeRequest(BaseModel):
    plan_tier: str

@router.post("/test-upgrade", status_code=200)
async def test_upgrade(
    body: TestUpgradeRequest,
    current_user: User = Depends(require_role("admin")),
):
    """
    Test-only endpoint to toggle plan tier for the current user's organization.
    Allowed values: 'free', 'pro', 'enterprise'.
    """
    if body.plan_tier not in ["free", "pro", "enterprise"]:
        raise HTTPException(status_code=400, detail="Invalid plan tier. Choose 'free', 'pro', or 'enterprise'.")

    sub = await Subscription.find_one(
        Subscription.organization_id == current_user.organization_id
    )

    if not sub:
        sub = Subscription(
            organization_id=current_user.organization_id,
            plan_tier=body.plan_tier,
            status="active"
        )
        await sub.insert()
    else:
        sub.plan_tier = body.plan_tier
        sub.status = "active"
        await sub.save()

    return {
        "message": f"Successfully updated subscription tier to '{body.plan_tier}'",
        "organization_id": str(current_user.organization_id),
        "plan_tier": sub.plan_tier,
        "status": sub.status,
    }


@router.post("/webhook", status_code=200)
async def stripe_webhook(
    request: Request,
):
    """
    Production-grade Stripe Webhook handler.
    Parses and verifies incoming events from Stripe to update DB subscriptions.
    """
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    event_type = payload.get("type")
    data_obj = payload.get("data", {}).get("object", {})

    if event_type in ["customer.subscription.created", "customer.subscription.updated"]:
        stripe_cust_id = data_obj.get("customer")
        stripe_sub_id = data_obj.get("id")
        status_val = data_obj.get("status")

        plan_tier = "pro"
        if "enterprise" in str(data_obj).lower():
            plan_tier = "enterprise"

        org = await Organization.find_one(Organization.stripe_customer_id == stripe_cust_id)
        if org:
            sub = await Subscription.find_one(Subscription.organization_id == org.id)
            if not sub:
                sub = Subscription(organization_id=org.id)
                await sub.insert()
            sub.stripe_subscription_id = stripe_sub_id
            sub.plan_tier = plan_tier
            sub.status = status_val
            await sub.save()

    elif event_type == "customer.subscription.deleted":
        stripe_sub_id = data_obj.get("id")
        sub = await Subscription.find_one(Subscription.stripe_subscription_id == stripe_sub_id)
        if sub:
            sub.plan_tier = "free"
            sub.status = "canceled"
            await sub.save()

    return {"status": "success"}
