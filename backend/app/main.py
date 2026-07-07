from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from pydantic_settings import BaseSettings

from app.config.database import Base, engine

# Import ALL models so SQLAlchemy sees them before create_all
import app.models.users
import app.models.uploaded_file
import app.models.raw_data_row
import app.models.processed_dataset
import app.models.forecast_result
import app.models.segment_result
import app.models.ai_insight
import app.models.organizations
import app.models.subscriptions

from app.routes import ai
from app.routes import upload
from app.config.settings import settings
from app.routes import auth_routes, upload, ai, forcast, segments, billing, organizations, superadmin

from sqlalchemy import text

# ============ ENVIRONMENT CONFIGURATION ============
class DeploymentSettings(BaseSettings):
    """Load environment variables for Railway deployment"""
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = ""
    GROQ_API_KEY: str = ""
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:5174,http://localhost:3000"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

deployment_settings = DeploymentSettings()

# ============ DATABASE MIGRATIONS ============
def run_migrations():
    """Run database migrations on startup"""
    try:
        with engine.connect() as connection:
            # Add super_admin to enum if not exists (Postgres specific)
            connection.execute(text("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'super_admin'"))
            
            connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS verification_code VARCHAR(6)"))
            connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS verification_expires TIMESTAMP WITH TIME ZONE"))
            connection.execute(text("ALTER TABLE users ALTER COLUMN is_active SET DEFAULT FALSE"))
            
            # New columns for password reset
            connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS password_changed BOOLEAN DEFAULT FALSE"))
            connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_password_token VARCHAR(255) UNIQUE"))
            connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_password_expires TIMESTAMP WITH TIME ZONE"))
            
            # Organizations & Subscriptions tables creation
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS organizations (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    stripe_customer_id VARCHAR(255),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """))
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id SERIAL PRIMARY KEY,
                    organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE UNIQUE,
                    stripe_subscription_id VARCHAR(255),
                    plan_tier VARCHAR(50) DEFAULT 'free',
                    status VARCHAR(50) DEFAULT 'active',
                    current_period_end TIMESTAMP WITH TIME ZONE
                )
            """))
            
            # Add foreign key columns if they don't exist
            connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS organization_id INTEGER REFERENCES organizations(id) ON DELETE SET NULL"))
            connection.execute(text("ALTER TABLE uploaded_files ADD COLUMN IF NOT EXISTS organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE"))

            # New columns for signup fields
            connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS first_name VARCHAR(100)"))
            connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_name VARCHAR(100)"))
            connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS org_name VARCHAR(255)"))
            connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS industry VARCHAR(100)"))
            connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS team_size VARCHAR(50)"))
            connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS plan VARCHAR(50)"))
            connection.execute(text("ALTER TABLE organizations ADD COLUMN IF NOT EXISTS industry VARCHAR(100)"))
            connection.execute(text("ALTER TABLE organizations ADD COLUMN IF NOT EXISTS team_size VARCHAR(50)"))
            connection.commit()
            print("✅ Database migrations completed successfully")
    except Exception as e:
        print(f"⚠️ Migration warning: {str(e)}")

# ============ DATA MIGRATION FOR MULTI-TENANCY ============
def migrate_existing_data():
    """Migrate existing data to multi-tenant structure"""
    from app.config.database import SessionLocal
    from app.models.users import User
    from app.models.organizations import Organization
    from app.models.subscriptions import Subscription
    from app.models.uploaded_file import UploadedFile
    from app.config.settings import settings
    from app.services.auth_services import hash_password

    db = SessionLocal()
    try:
        # 1. Create Predefined System Admins if they don't exist
        predefined_admins = [e.strip().lower() for e in settings.PREDEFINED_ADMIN_EMAILS.split(",") if e.strip()]
        for admin_email in predefined_admins:
            existing_admin = db.query(User).filter(User.email == admin_email).first()
            if not existing_admin:
                print(f"Creating predefined system admin account: {admin_email}...")
                org = Organization(name="System Admin Workspace")
                db.add(org)
                db.flush()
                
                sub = Subscription(organization_id=org.id, plan_tier="enterprise", status="active")
                db.add(sub)
                
                admin_user = User(
                    name="System Admin",
                    email=admin_email,
                    password=hash_password("AdminPassword123!"),
                    role="super_admin",
                    is_active=True,
                    password_changed=False,
                    organization_id=org.id
                )
                db.add(admin_user)
                db.commit()
                print(f"✅ Predefined super_admin created. Email: {admin_email}")
            else:
                if existing_admin.role != "super_admin":
                    existing_admin.role = "super_admin"
                    db.commit()

        # 2. Existing Users migration
        users = db.query(User).filter(User.organization_id == None).all()
        if users:
            print(f"Migrating {len(users)} users to their own personal organizations...")
            for user in users:
                org = Organization(name=f"{user.name}'s Workspace")
                db.add(org)
                db.flush()
                
                sub = Subscription(organization_id=org.id, plan_tier="free", status="active")
                db.add(sub)
                
                user.organization_id = org.id
                
                # Update files
                db.query(UploadedFile).filter(
                    UploadedFile.user_id == user.id,
                    UploadedFile.organization_id == None
                ).update({UploadedFile.organization_id: org.id}, synchronize_session=False)
            db.commit()
            print("✅ Multi-tenant data migration completed successfully")
    except Exception as e:
        db.rollback()
        print(f"⚠️ Data migration/admin creation error: {str(e)}")
    finally:
        db.close()

# ============ INITIALIZE DATABASE TABLES ============
Base.metadata.create_all(bind=engine)

# ============ RUN MIGRATIONS AND DATA MIGRATIONS ============
run_migrations()
migrate_existing_data()

# ============ FASTAPI APP INITIALIZATION ============
app = FastAPI(
    title="TR InsightForge Backend",
    description="Business Analytics + ML + AI Recommendation Engine",
    version="1.0.0"
)

# ============ CORS MIDDLEWARE - DYNAMIC FOR PRODUCTION ============
# Parse allowed origins from environment variable
allowed_origins = [origin.strip() for origin in deployment_settings.ALLOWED_ORIGINS.split(",")]

# In production (Railway), allow your frontend domain
if deployment_settings.ENVIRONMENT == "production":
    # Add your production frontend URLs here
    allowed_origins.extend([
        "https://your-frontend-domain.com",
        # Add more production domains as needed
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ REGISTER ROUTES ============
app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(ai.router, prefix="/ai", tags=["AI"])
app.include_router(forcast.router, prefix="/forecast", tags=["Forecast"])
app.include_router(segments.router, prefix="/segment", tags=["Segmentation"])
# app.include_router(billing.router, prefix="/billing", tags=["Billing"]) # Disabled for now
app.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])
app.include_router(superadmin.router, prefix="/superadmin", tags=["SuperAdmin"])

# ============ HEALTH CHECK ENDPOINT (Required by Railway) ============
@app.get("/health")
async def health_check():
    """Health check endpoint - Railway uses this to verify app is running"""
    return {
        "status": "healthy",
        "environment": deployment_settings.ENVIRONMENT,
        "service": "TR InsightForge Backend",
        "version": "1.0.0"
    }

# ============ ROOT ENDPOINT ============
@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "TR InsightForge Backend Running Successfully",
        "docs": "/docs",
        "version": "1.0.0"
    }

# ============ STARTUP & SHUTDOWN EVENTS ============
@app.on_event("startup")
async def startup_event():
    """Run on app startup"""
    print(f"🚀 TR InsightForge Backend started in {deployment_settings.ENVIRONMENT} mode")
    print(f"📍 Environment: {deployment_settings.ENVIRONMENT}")
    print(f"🔐 Allowed Origins: {allowed_origins}")

@app.on_event("shutdown")
async def shutdown_event():
    """Run on app shutdown"""
    print("🛑 TR InsightForge Backend shutting down gracefully")

# ============ ENTRY POINT ============
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    debug = deployment_settings.ENVIRONMENT == "development"
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=debug,
        log_level="info"
    )