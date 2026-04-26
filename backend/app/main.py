from fastapi import FastAPI
from app.routes import upload
from app.routes import analytics

app = FastAPI(
    title="TR InsightForge Backend",
    description="Business Analytics + ML + AI Recommendation Engine",
    version="1.0.0"
)

# Register Routes
app.include_router(
    upload.router,
    prefix="/upload",
    tags=["File Upload"]
)
app.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["Analytics"]
)
@app.get("/")
def root():
    return {
        "message": "TR InsightForge Backend Running Successfully"
    }