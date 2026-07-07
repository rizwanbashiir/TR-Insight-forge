from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List
import secrets
from datetime import datetime, timedelta

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

def add_user_to_organization(db: Session, data: AddUserRequest, current_user: User) -> AddUserResponse:
    if current_user.role != "admin" and current_user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Only admins can add users to the organization.")

    org_id = current_user.organization_id
    if not org_id:
        raise HTTPException(status_code=400, detail="You do not belong to any organization.")

    # # Commented out subscription based user registration module for now
    # sub = db.query(Subscription).filter(Subscription.organization_id == org_id).first()
    # if not sub:
    #     raise HTTPException(status_code=400, detail="Organization has no active subscription.")
    #
    # plan_tier = sub.plan_tier.lower()
    # 
    # # Get current users in the organization
    # org_users = db.query(User).filter(User.organization_id == org_id).all()
    # 
    # # Enforce Limits
    # if plan_tier == "free":
    #     if len(org_users) >= 1:
    #         raise HTTPException(status_code=400, detail="Free plan is limited to 1 user.")
    # elif plan_tier == "pro":
    #     if len(org_users) >= 3:
    #         raise HTTPException(status_code=400, detail="Pro plan is limited to 3 users.")
    #     
    #     # Enforce exactly 1 admin, 1 analyst, 1 viewer if they want strictly those roles.
    #     # Check current roles to prevent duplicates
    #     role_counts = {"admin": 0, "analyst": 0, "viewer": 0}
    #     for u in org_users:
    #         if u.role in role_counts:
    #             role_counts[u.role] += 1
    #     
    #     requested_role = data.role.lower()
    #     if requested_role not in role_counts:
    #         raise HTTPException(status_code=400, detail="Invalid role. Must be analyst or viewer.")
    #     
    #     if role_counts[requested_role] >= 1:
    #         raise HTTPException(status_code=400, detail=f"Pro plan only allows 1 {requested_role}.")
    #         
    # # Enterprise has no limits

    requested_role = data.role.lower()
    if requested_role not in ["admin", "analyst", "viewer"]:
        raise HTTPException(status_code=400, detail="Invalid role. Must be admin, analyst, or viewer.")

    # Check if user email already exists globally
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="A user with this email already exists.")

    # Generate temporary password and reset token
    temp_password = secrets.token_urlsafe(8)
    reset_token = generate_reset_token()
    reset_expires = datetime.utcnow() + timedelta(hours=6)

    new_user = User(
        name=data.name,
        email=data.email,
        password=hash_password(temp_password),
        role=data.role.lower(),
        is_active=True, # Activate them immediately for ease of use
        organization_id=org_id,
        password_changed=False,
        reset_password_token=reset_token,
        reset_password_expires=reset_expires
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # In a real app, send an email here. We simulate it via print.
    print("\n" + "="*50)
    print(f"EMAIL SENT TO: {data.email}")
    print(f"Subject: You have been invited to {current_user.organization.name}")
    print(f"Body: Hello {data.name},\n")
    print(f"You have been added as a(n) {data.role}.")
    print(f"Your temporary password is: {temp_password}")
    print(f"Please log in and change your password, or use this reset link:")
    print(f"http://localhost:5173/reset-password?token={reset_token}")
    print(f"(Link valid for 6 hours)")
    print("="*50 + "\n")

    user_info = UserInfo(
        id=new_user.id,
        name=new_user.name,
        email=new_user.email,
        role=new_user.role,
        is_active=new_user.is_active,
        password_changed=new_user.password_changed,
        created_at=new_user.created_at
    )

    return AddUserResponse(message="User added successfully.", user=user_info)

def get_organization_users(db: Session, current_user: User) -> List[UserInfo]:
    org_id = current_user.organization_id
    if not org_id:
        raise HTTPException(status_code=400, detail="You do not belong to any organization.")
        
    users = db.query(User).filter(User.organization_id == org_id).all()
    return [
        UserInfo(
            id=u.id,
            name=u.name,
            email=u.email,
            role=u.role,
            is_active=u.is_active,
            password_changed=u.password_changed,
            created_at=u.created_at
        ) for u in users
    ]

def resend_invite(db: Session, user_id: int, current_user: User):
    if current_user.role != "admin" and current_user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Only admins can resend invites.")
        
    target_user = db.query(User).filter(User.id == user_id, User.organization_id == current_user.organization_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found in your organization.")
        
    if target_user.password_changed:
        raise HTTPException(status_code=400, detail="User has already changed their password. They should use 'Forgot Password'.")
        
    reset_token = generate_reset_token()
    reset_expires = datetime.utcnow() + timedelta(hours=6)
    
    target_user.reset_password_token = reset_token
    target_user.reset_password_expires = reset_expires
    db.commit()
    
    # Simulate email
    print("\n" + "="*50)
    print(f"RESENT INVITE / PASSWORD RESET EMAIL TO: {target_user.email}")
    print(f"Subject: Reminder: You have been invited to {current_user.organization.name}")
    print(f"Please use this reset link to set your password:")
    print(f"http://localhost:5173/reset-password?token={reset_token}")
    print(f"(Link valid for 6 hours)")
    print("="*50 + "\n")
    
    return {"message": "Invite link resent successfully."}

def get_organization_dashboard(db: Session, current_user: User) -> OrganizationDashboardResponse:
    org_id = current_user.organization_id
    if not org_id:
        raise HTTPException(status_code=400, detail="You do not belong to any organization.")
    
    org = db.query(Organization).filter(Organization.id == org_id).first()
    sub = db.query(Subscription).filter(Subscription.organization_id == org_id).first()
    users = get_organization_users(db, current_user)
    
    org_info = OrganizationInfo(
        id=org.id,
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
