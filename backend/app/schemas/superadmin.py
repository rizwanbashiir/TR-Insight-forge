from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.organizations import OrganizationInfo, SubscriptionInfo

class CreateEnterpriseRequest(BaseModel):
    name: str
    admin_name: str
    admin_email: str
    stripe_customer_id: Optional[str] = None

class OrganizationOverview(BaseModel):
    organization: OrganizationInfo
    subscription: SubscriptionInfo
    user_count: int

class SuperAdminDashboardResponse(BaseModel):
    total_organizations: int
    active_subscriptions: int
    free_subscriptions: int
    enterprise_subscriptions: int
    pro_subscriptions: int
    organizations: List[OrganizationOverview]
