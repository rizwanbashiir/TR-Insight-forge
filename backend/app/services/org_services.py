from fastapi import HTTPException, status
from typing import List
import secrets
from datetime import datetime, timedelta, timezone

from app.models.users import User, UserRole
from app.models.organizations import Organization
from app.models.subscriptions import Subscription
from app.schemas.organizations import (
    AddUserRequest, AddUserResponse, UserInfo,
    OrganizationInfo, SubscriptionInfo, OrganizationDashboardResponse
)
from app.services.auth_services import hash_password

def generate_reset_token():
    return secrets.token_urlsafe(32)

async def add_user_to_organization(db, data: AddUserRequest, current_user: User) -> AddUserResponse:
    if current_user.role != "admin" and current_user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Only admins can add users to the organization.")

    org_id = current_user.organization_id
    if not org_id:
        raise HTTPException(status_code=400, detail="You do not belong to any organization.")

    requested_role = data.role.lower()
    if requested_role not in ["admin", "analyst", "viewer"]:
        raise HTTPException(status_code=400, detail="Invalid role. Must be admin, analyst, or viewer.")

    existing_user = await User.find_one(User.email == data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="A user with this email already exists.")

    temp_password = secrets.token_urlsafe(8)
    reset_token = generate_reset_token()
    reset_expires = datetime.now(timezone.utc) + timedelta(hours=6)

    new_user = User(
        name=data.name,
        email=data.email,
        password=hash_password(temp_password),
        role=data.role.lower(),
        is_active=True,
        organization_id=org_id,
        password_changed=False,
        reset_password_token=reset_token,
        reset_password_expires=reset_expires
    )
    await new_user.insert()

    org = await Organization.get(org_id)
    org_name = org.name if org else "Workspace"

    print("\n" + "="*50)
    print(f"EMAIL SENT TO: {data.email}")
    print(f"Subject: You have been invited to {org_name}")
    print(f"Body: Hello {data.name},\n")
    print(f"You have been added as a(n) {data.role}.")
    print(f"Your temporary password is: {temp_password}")
    print(f"Please log in and change your password, or use this reset link:")
    print(f"http://localhost:5173/reset-password?token={reset_token}")
    print(f"(Link valid for 6 hours)")
    print("="*50 + "\n")

    user_info = UserInfo(
        id=str(new_user.id),
        name=new_user.name,
        email=new_user.email,
        role=new_user.role,
        is_active=new_user.is_active,
        password_changed=new_user.password_changed,
        created_at=new_user.created_at
    )

    return AddUserResponse(message="User added successfully.", user=user_info)

async def get_organization_users(db, current_user: User) -> List[UserInfo]:
    org_id = current_user.organization_id
    if not org_id:
        raise HTTPException(status_code=400, detail="You do not belong to any organization.")

    users = await User.find(User.organization_id == org_id).to_list()
    return [
        UserInfo(
            id=str(u.id),
            name=u.name,
            email=u.email,
            role=u.role,
            is_active=u.is_active,
            password_changed=u.password_changed,
            created_at=u.created_at
        ) for u in users
    ]

async def resend_invite(db, user_id: str, current_user: User):
    if current_user.role != "admin" and current_user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Only admins can resend invites.")

    from beanie import PydanticObjectId
    try:
        oid = PydanticObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    target_user = await User.find_one(User.id == oid, User.organization_id == current_user.organization_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found in your organization.")

    if target_user.password_changed:
        raise HTTPException(status_code=400, detail="User has already changed their password. They should use 'Forgot Password'.")

    reset_token = generate_reset_token()
    reset_expires = datetime.now(timezone.utc) + timedelta(hours=6)

    target_user.reset_password_token = reset_token
    target_user.reset_password_expires = reset_expires
    await target_user.save()

    org = await Organization.get(current_user.organization_id)
    org_name = org.name if org else "Workspace"

    print("\n" + "="*50)
    print(f"RESENT INVITE / PASSWORD RESET EMAIL TO: {target_user.email}")
    print(f"Subject: Reminder: You have been invited to {org_name}")
    print(f"Please use this reset link to set your password:")
    print(f"http://localhost:5173/reset-password?token={reset_token}")
    print(f"(Link valid for 6 hours)")
    print("="*50 + "\n")

    return {"message": "Invite link resent successfully."}

async def get_organization_dashboard(db, current_user: User) -> OrganizationDashboardResponse:
    org_id = current_user.organization_id
    if not org_id:
        raise HTTPException(status_code=400, detail="You do not belong to any organization.")

    org = await Organization.get(org_id)
    sub = await Subscription.find_one(Subscription.organization_id == org_id)
    users = await get_organization_users(db, current_user)

    if not org:
        raise HTTPException(status_code=404, detail="Organization not found.")

    org_info = OrganizationInfo(
        id=str(org.id),
        name=org.name,
        industry=org.industry,
        team_size=org.team_size,
        stripe_customer_id=org.stripe_customer_id,
        created_at=org.created_at
    )

    sub_info = SubscriptionInfo(
        plan_tier=sub.plan_tier if sub and sub.plan_tier else "free",
        status=sub.status if sub and sub.status else "active",
        current_period_end=sub.current_period_end if sub else None
    )

    return OrganizationDashboardResponse(
        organization=org_info,
        subscription=sub_info,
        users=users
    )
