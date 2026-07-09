from fastapi import APIRouter, Depends
from app.utils.dependencies import require_role
from app.models.users import User
from app.schemas.superadmin import SuperAdminDashboardResponse, CreateEnterpriseRequest, OverrideSubscriptionRequest
from app.services.superadmin_services import get_superadmin_dashboard, create_enterprise_organization, override_organization_subscription

router = APIRouter()

@router.get("/dashboard", response_model=SuperAdminDashboardResponse)
async def get_dashboard(
    current_user: User = Depends(require_role("super_admin"))
):
    """
    Get the superadmin dashboard stats.
    """
    return await get_superadmin_dashboard(None)

@router.post("/organizations")
async def create_enterprise_org(
    data: CreateEnterpriseRequest,
    current_user: User = Depends(require_role("super_admin"))
):
    """
    Create a new Enterprise organization manually.
    """
    return await create_enterprise_organization(None, data)

@router.post("/override-subscription")
async def override_subscription(
    data: OverrideSubscriptionRequest,
    current_user: User = Depends(require_role("super_admin"))
):
    """
    Override the subscription of any organization manually.
    """
    return await override_organization_subscription(None, data)
