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

from app.routes import upload
from app.routes import auth_routes

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TR InsightForge Backend",
    description="Business Analytics + ML + AI Recommendation Engine",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router,   prefix="/auth",   tags=["Auth"])
app.include_router(upload.router, prefix="/upload", tags=["Upload"])

@app.get("/")
def root():
    return {"message": "TR InsightForge Backend Running Successfully"}