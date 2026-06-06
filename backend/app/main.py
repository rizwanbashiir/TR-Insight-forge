# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from app.routes import auth_routes
# from app.routes import upload
# from app.routes import analytics
# from app.config.database import Base,engine
# import app.models.users

# Base.metadata.create_all(bind=engine)
# app = FastAPI(
#     title="TR InsightForge Backend",
#     description="Business Analytics + ML + AI Recommendation Engine",
#     version="1.0.0"
# )

# # CORS — allow React dev server
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:5173", "http://localhost:3000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Register Routes
# app.include_router(
#     auth_routes.router,      
#     prefix="/auth",      
#     tags=["Auth"]
# )
# app.include_router(
#     upload.router,
#     prefix="/upload",
#     tags=["File Upload"]
# )
# app.include_router(
#     analytics.router,
#     prefix="/analytics",
#     tags=["Analytics"]
# )
# @app.get("/")
# def root():
#     return {"message": "TR InsightForge Backend Running Successfully"}


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
from app.services.ollama_service import check_ollama_health
from app.config.settings import settings
from app.routes import auth_routes, upload, ai, forcast, segments, billing


from sqlalchemy import text

# Run raw SQL migrations to ensure users table has verification columns and organization relations
try:
    with engine.connect() as connection:
        connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS verification_code VARCHAR(6)"))
        connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS verification_expires TIMESTAMP WITH TIME ZONE"))
        connection.execute(text("ALTER TABLE users ALTER COLUMN is_active SET DEFAULT FALSE"))
        
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
        connection.commit()
except Exception as e:
    print(f"Migration warning: {str(e)}")

Base.metadata.create_all(bind=engine)

# Data Migration for multi-tenancy & Predefined Admins
def migrate_existing_data():
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
                    role="admin",
                    is_active=True,
                    organization_id=org.id
                )
                db.add(admin_user)
                db.commit()
                print(f"Predefined admin created. Email: {admin_email}, Default Password: AdminPassword123!")

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
            print("Multi-tenant data migration completed successfully.")
    except Exception as e:
        db.rollback()
        print(f"Data migration/admin creation error: {str(e)}")
    finally:
        db.close()

migrate_existing_data()

app = FastAPI(
    title="TR InsightForge Backend",
    description="Business Analytics + ML + AI Recommendation Engine",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router,   prefix="/auth",   tags=["Auth"])
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(ai.router, prefix="/ai", tags=["AI"])
app.include_router(forcast.router, prefix="/forecast", tags=["Forecast"])
app.include_router(segments.router, prefix="/segment", tags=["Segmentation"])
app.include_router(billing.router, prefix="/billing", tags=["Billing"])

@app.get("/")
def root():
    return {"message": "TR InsightForge Backend Running Successfully"}


# app.include_router(ai.router, prefix="/ai", tags=["AI"])