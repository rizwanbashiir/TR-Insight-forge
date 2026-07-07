from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.utils.dependencies import require_role
from app.models.users import User
from app.schemas.superadmin import SuperAdminDashboardResponse, CreateEnterpriseRequest, OverrideSubscriptionRequest
from app.services.superadmin_services import get_superadmin_dashboard, create_enterprise_organization, override_organization_subscription

router = APIRouter()

@router.get("/dashboard", response_model=SuperAdminDashboardResponse)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("super_admin"))
):
    """
    Get the superadmin dashboard stats.
    """
    return get_superadmin_dashboard(db)

@router.post("/organizations")
def create_enterprise_org(
    data: CreateEnterpriseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("super_admin"))
):
    """
    Create a new Enterprise organization manually.
    """
    return create_enterprise_organization(db, data)

@router.post("/override-subscription")
def override_subscription(
    data: OverrideSubscriptionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("super_admin"))
):
    """
    Override the subscription of any organization manually.
    """
    return override_organization_subscription(db, data)

