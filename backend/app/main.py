from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.database import Base, engine
from app.routes import upload, analytics,auth_routes
# import app.models.user so SQLAlchemy sees the table before create_all
import app.models.users  # noqa: F401

# Create all tables automatically on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TR InsightForge Backend",
    description="Business Analytics + ML + AI Recommendation Engine",
    version="1.0.0"
)

# CORS — allow React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(auth_routes.router,      prefix="/auth",      tags=["Auth"])
app.include_router(upload.router,    prefix="/upload",    tags=["Upload"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])

@app.get("/")
def root():
    return {"message": "TR InsightForge Backend Running Successfully"}