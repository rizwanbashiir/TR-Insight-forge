from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.config.database import get_db
from app.utils.dependencies import require_role, get_current_user
from app.models.users import User
from app.schemas.organizations import AddUserRequest, AddUserResponse, UserInfo
from app.services.org_services import add_user_to_organization, get_organization_users, resend_invite

router = APIRouter()

@router.post("/users", response_model=AddUserResponse)
def add_user(
    data: AddUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "super_admin"))
):
    """
    Add a user to the current organization. Enforces limits based on plan_tier.
    """
    return add_user_to_organization(db, data, current_user)

@router.get("/users", response_model=List[UserInfo])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all users in the current organization.
    """
    return get_organization_users(db, current_user)

@router.post("/users/{user_id}/resend-invite")
def resend_user_invite(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "super_admin"))
):
    """
    Resend the invite (password reset link) to a user who hasn't changed their temp password yet.
    """
    return resend_invite(db, user_id, current_user)
