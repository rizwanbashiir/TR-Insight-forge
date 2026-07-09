from fastapi import APIRouter, Depends
from typing import List

from app.utils.dependencies import require_role, get_current_user
from app.models.users import User
from app.schemas.organizations import AddUserRequest, AddUserResponse, UserInfo, OrganizationDashboardResponse
from app.services.org_services import add_user_to_organization, get_organization_users, resend_invite, get_organization_dashboard

router = APIRouter()

@router.get("/dashboard", response_model=OrganizationDashboardResponse)
async def get_dashboard(
    current_user: User = Depends(get_current_user)
):
    """
    Get organization dashboard summary including organization info, subscription tier, and user list.
    """
    return await get_organization_dashboard(None, current_user)

@router.post("/users", response_model=AddUserResponse)
async def add_user(
    data: AddUserRequest,
    current_user: User = Depends(require_role("admin", "super_admin"))
):
    """
    Add a user to the current organization. Enforces limits based on plan_tier.
    """
    return await add_user_to_organization(None, data, current_user)

@router.get("/users", response_model=List[UserInfo])
async def list_users(
    current_user: User = Depends(get_current_user)
):
    """
    List all users in the current organization.
    """
    return await get_organization_users(None, current_user)

@router.post("/users/{user_id}/resend-invite")
async def resend_user_invite(
    user_id: str,
    current_user: User = Depends(require_role("admin", "super_admin"))
):
    """
    Resend the invite (password reset link) to a user who hasn't changed their temp password yet.
    """
    return await resend_invite(None, user_id, current_user)
