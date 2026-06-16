from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.organizations import Organization
from app.models.subscriptions import Subscription
from app.models.users import User
from app.schemas.superadmin import SuperAdminDashboardResponse, OrganizationOverview, CreateEnterpriseRequest
from app.schemas.organizations import OrganizationInfo, SubscriptionInfo
from app.services.auth_services import hash_password

def get_superadmin_dashboard(db: Session) -> SuperAdminDashboardResponse:
    orgs = db.query(Organization).all()
    
    total_organizations = len(orgs)
    active_subscriptions = 0
    free_subscriptions = 0
    enterprise_subscriptions = 0
    pro_subscriptions = 0
    
    org_overviews = []
    
    for org in orgs:
        sub = db.query(Subscription).filter(Subscription.organization_id == org.id).first()
        user_count = db.query(User).filter(User.organization_id == org.id).count()
        
        if sub:
            if sub.status == "active":
                active_subscriptions += 1
            if sub.plan_tier == "free":
                free_subscriptions += 1
            elif sub.plan_tier == "enterprise":
                enterprise_subscriptions += 1
            elif sub.plan_tier == "pro":
                pro_subscriptions += 1
                
            org_overviews.append(
                OrganizationOverview(
                    organization=OrganizationInfo(
                        id=org.id,
                        name=org.name,
                        stripe_customer_id=org.stripe_customer_id,
                        created_at=org.created_at
                    ),
                    subscription=SubscriptionInfo(
                        plan_tier=sub.plan_tier,
                        status=sub.status,
                        current_period_end=sub.current_period_end
                    ),
                    user_count=user_count
                )
            )

    return SuperAdminDashboardResponse(
        total_organizations=total_organizations,
        active_subscriptions=active_subscriptions,
        free_subscriptions=free_subscriptions,
        enterprise_subscriptions=enterprise_subscriptions,
        pro_subscriptions=pro_subscriptions,
        organizations=org_overviews
    )

def create_enterprise_organization(db: Session, data: CreateEnterpriseRequest) -> dict:
    existing_user = db.query(User).filter(User.email == data.admin_email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="A user with this email already exists.")
        
    org = Organization(
        name=data.name,
        stripe_customer_id=data.stripe_customer_id
    )
    db.add(org)
    db.flush()
    
    sub = Subscription(
        organization_id=org.id,
        plan_tier="enterprise",
        status="active"
    )
    db.add(sub)
    
    admin_user = User(
        name=data.admin_name,
        email=data.admin_email,
        password=hash_password("TempPassword123!"), # Standard temp password, should be changed
        role="admin",
        is_active=True,
        organization_id=org.id
    )
    db.add(admin_user)
    db.commit()
    db.refresh(org)
    
    return {"message": "Enterprise organization created successfully.", "organization_id": org.id}
