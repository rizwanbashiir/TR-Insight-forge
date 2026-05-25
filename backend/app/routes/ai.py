from fastapi import APIRouter
import pandas as pd

from app.services.kpi_service import generate_kpis
from app.services.forecasting import run_arima_forecast
from app.services.segmentation import run_customer_segmentation
#from app.services.prompt_builder import build_business_prompt
#from app.services.grok_service import get_grok_recommendations
from app.services.ollama_service import call_ollama, check_ollama_health
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.services.ai_service import get_ai_answer
from app.services.prompt_builder import build_rag_prompt
from app.services.prompt_builder import build_general_insights_prompt

from app.config.database import get_db
from app.utils.dependencies import get_current_user
from app.models.users import User
from app.services.ai_service import get_ai_answer

router = APIRouter()


@router.get("/insights")
def generate_ai_insights():
    """
    Generate AI-powered business recommendations
    """

    df = pd.read_csv("data/raw/dirty_sales_data.csv")
    forecast_df = pd.read_csv("data/raw/forecast_sales_data.csv")

    kpis = generate_kpis(df)
    forecast = run_arima_forecast(forecast_df)
    segments = run_customer_segmentation(df)

    prompt = build_general_insights_prompt(
        kpis,
        forecast,
        segments
    )

    # result = get ollama (prompt)
    result = call_ollama(prompt)

    return {
        "status": "success",
        "ai_recommendations": result
    }



class AIRequest(BaseModel):
    file_id : int
    question: Optional[str] = None    # None = general analysis

@router.post("/ask", status_code=200)
def ask_ai(
    body        : AIRequest,
    db          : Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    """
    Ask a business question about your uploaded data.
    Uses RAG to retrieve relevant context from Pinecone,
    then sends to Grok for a plain-language answer.

    Leave question empty for a general business health report.
    """
    try:
        result = get_ai_answer(
            db           = db,
            file_id      = body.file_id,
            user_id      = current_user.id,
            user_question= body.question,
        )
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/history/{file_id}", status_code=200)
def get_ai_history(
    file_id     : int,
    db          : Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    """Get the last AI insight generated for a file."""
    from app.models.ai_insight import AiInsight

    insight = db.query(AiInsight).filter(
        AiInsight.file_id == file_id
    ).first()

    if not insight:
        raise HTTPException(
            status_code=404,
            detail="No AI insights found for this file yet."
        )

    return {
        "file_id"     : file_id,
        "model"       : insight.model_name,
        "ai_response" : insight.ai_response,
        "generated_at": insight.generated_at,
    }


@router.get("/health", status_code=200)
def ollama_health():
    """Check if Ollama is running and available."""
    return check_ollama_health()