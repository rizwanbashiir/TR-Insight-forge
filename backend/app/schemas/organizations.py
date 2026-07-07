from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class AddUserRequest(BaseModel):
    name: str
    email: EmailStr
    role: str # admin, analyst, viewer

class UserInfo(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_active: bool
    password_changed: bool
    created_at: datetime

class OrganizationInfo(BaseModel):
    id: int
    name: str
    industry: Optional[str] = None
    team_size: Optional[str] = None
    stripe_customer_id: Optional[str] = None
    created_at: datetime

class SubscriptionInfo(BaseModel):
    plan_tier: str
    status: str
    current_period_end: Optional[datetime] = None

class OrganizationDashboardResponse(BaseModel):
    organization: OrganizationInfo
    subscription: SubscriptionInfo
    users: List[UserInfo]

class AddUserResponse(BaseModel):
    message: str
    user: UserInfo
