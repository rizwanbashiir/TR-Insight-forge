from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config.database import init_db
from app.config.settings import settings
from app.routes import auth_routes, upload, ai, forcast, segments, billing, organizations, superadmin


async def ensure_predefined_admins():
    from app.models.users import User, UserRole
    from app.models.organizations import Organization
    from app.models.subscriptions import Subscription
    from app.services.auth_services import hash_password

    predefined_admins = [
        e.strip().lower()
        for e in settings.PREDEFINED_ADMIN_EMAILS.split(",")
        if e.strip()
    ]
    for admin_email in predefined_admins:
        existing_admin = await User.find_one(User.email == admin_email)
        if not existing_admin:
            print(f"Creating predefined system admin account: {admin_email}...")
            org = Organization(name="System Admin Workspace")
            await org.insert()

            sub = Subscription(
                organization_id=org.id,
                plan_tier="enterprise",
                status="active"
            )
            await sub.insert()

            admin_user = User(
                name="System Admin",
                email=admin_email,
                password=hash_password("AdminPassword123!"),
                role=UserRole.super_admin,
                is_active=True,
                password_changed=False,
                organization_id=org.id
            )
            await admin_user.insert()
            print(f"Predefined super_admin created. Email: {admin_email}, Default Password: AdminPassword123!")
        elif existing_admin.role != UserRole.super_admin:
            existing_admin.role = UserRole.super_admin
            await existing_admin.save()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    print("Connected to MongoDB Atlas and initialized Beanie ODM.")
    try:
        await ensure_predefined_admins()
    except Exception as e:
        print(f"Admin seed warning: {e}")
    yield
    # Shutdown logic if any
    print("Shutting down TR InsightForge Backend.")


app = FastAPI(
    title="TR InsightForge Backend",
    description="Business Analytics + ML + AI Recommendation Engine",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router,   prefix="/auth",          tags=["Auth"])
app.include_router(upload.router,        prefix="/upload",        tags=["Upload"])
app.include_router(ai.router,            prefix="/ai",            tags=["AI"])
app.include_router(forcast.router,       prefix="/forecast",      tags=["Forecast"])
app.include_router(segments.router,      prefix="/segment",       tags=["Segmentation"])
# app.include_router(billing.router, prefix="/billing", tags=["Billing"]) # Disabled billing and subscription APIs for now
app.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])
app.include_router(superadmin.router,    prefix="/superadmin",    tags=["SuperAdmin"])


@app.get("/")
def root():
    return {"message": "TR InsightForge Backend Running Successfully on MongoDB Atlas"}