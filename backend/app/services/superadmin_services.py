from fastapi import HTTPException
from beanie import PydanticObjectId
from app.models.organizations import Organization
from app.models.subscriptions import Subscription
from app.models.users import User, UserRole
from app.schemas.superadmin import SuperAdminDashboardResponse, OrganizationOverview, CreateEnterpriseRequest, OverrideSubscriptionRequest
from app.schemas.organizations import OrganizationInfo, SubscriptionInfo, UserInfo
from app.services.auth_services import hash_password

async def get_superadmin_dashboard(db) -> SuperAdminDashboardResponse:
    orgs = await Organization.find_all().to_list()
    all_db_users = await User.find_all().to_list()

    total_organizations = len(orgs)
    total_users = len(all_db_users)
    active_subscriptions = 0
    free_subscriptions = 0
    enterprise_subscriptions = 0
    pro_subscriptions = 0

    all_user_infos = [
        UserInfo(
            id=str(u.id),
            name=u.name,
            email=u.email,
            role=u.role,
            is_active=u.is_active,
            password_changed=u.password_changed,
            created_at=u.created_at
        ) for u in all_db_users
    ]

    org_overviews = []

    for org in orgs:
        sub = await Subscription.find_one(Subscription.organization_id == org.id)
        org_users = await User.find(User.organization_id == org.id).to_list()
        user_count = len(org_users)

        org_user_infos = [
            UserInfo(
                id=str(u.id),
                name=u.name,
                email=u.email,
                role=u.role,
                is_active=u.is_active,
                password_changed=u.password_changed,
                created_at=u.created_at
            ) for u in org_users
        ]

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
                    id=str(org.id),
                    name=org.name,
                    stripe_customer_id=org.stripe_customer_id,
                    created_at=org.created_at
                ),
                subscription=SubscriptionInfo(
                    plan_tier=sub.plan_tier if sub else "free",
                    status=sub.status if sub else "active",
                    current_period_end=sub.current_period_end if sub else None
                ),
                user_count=user_count,
                users=org_user_infos
            )
        )

    return SuperAdminDashboardResponse(
        total_organizations=total_organizations,
        total_users=total_users,
        active_subscriptions=active_subscriptions,
        free_subscriptions=free_subscriptions,
        enterprise_subscriptions=enterprise_subscriptions,
        pro_subscriptions=pro_subscriptions,
        organizations=org_overviews,
        all_users=all_user_infos
    )

async def create_enterprise_organization(db, data: CreateEnterpriseRequest) -> dict:
    existing_user = await User.find_one(User.email == data.admin_email)
    if existing_user:
        raise HTTPException(status_code=400, detail="A user with this email already exists.")

    org = Organization(
        name=data.name,
        stripe_customer_id=data.stripe_customer_id
    )
    await org.insert()

    sub = Subscription(
        organization_id=org.id,
        plan_tier="enterprise",
        status="active"
    )
    await sub.insert()

    admin_user = User(
        name=data.admin_name,
        email=data.admin_email,
        password=hash_password("TempPassword123!"),
        role=UserRole.admin,
        is_active=True,
        organization_id=org.id
    )
    await admin_user.insert()

    return {"message": "Enterprise organization created successfully.", "organization_id": str(org.id)}

async def override_organization_subscription(db, data: OverrideSubscriptionRequest) -> dict:
    if data.plan_tier not in ["free", "pro", "enterprise"]:
        raise HTTPException(status_code=400, detail="Invalid plan tier. Choose 'free', 'pro', or 'enterprise'.")

    try:
        oid = PydanticObjectId(data.organization_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid organization ID")

    org = await Organization.get(oid)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    sub = await Subscription.find_one(Subscription.organization_id == org.id)
    if not sub:
        sub = Subscription(
            organization_id=org.id,
            plan_tier=data.plan_tier,
            status="active"
        )
        await sub.insert()
    else:
        sub.plan_tier = data.plan_tier
        sub.status = "active"
        await sub.save()

    return {
        "message": f"Successfully overridden subscription tier to '{data.plan_tier}'",
        "organization_id": str(org.id),
        "plan_tier": sub.plan_tier
    }
