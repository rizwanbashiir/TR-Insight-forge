from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.config.database import get_db
from app.utils.dependencies import get_current_user
from app.models.users import User

router = APIRouter()

class AIRequest(BaseModel):
    file_id : int
    question: Optional[str] = None


@router.post("/ask", status_code=200)
def ask_ai(
    body        : AIRequest,
    db          : Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    """
    Ask a specific business question about your data.
    Leave question empty for general business health report.
    Body: {"file_id": 11, "question": "Which months had highest sales?"}
    """
    from app.services.ai_service import get_ai_answer
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights", status_code=200)
def get_ai_insights(
    file_id     : int          = Query(..., description="File ID"),
    question    : Optional[str]= Query(None, description="Optional question"),
    db          : Session      = Depends(get_db),
    current_user: User         = Depends(get_current_user),
):
    """
    Generate AI-powered business recommendations.
    Usage: GET /ai/insights?file_id=11
    With question: GET /ai/insights?file_id=11&question=Why did sales drop?
    """
    from app.services.ai_service import get_ai_answer
    try:
        result = get_ai_answer(
            db           = db,
            file_id      = file_id,
            user_id      = current_user.id,
            user_question= question,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", status_code=200)
def ollama_health():
    """Check if Ollama is running."""
    from app.services.ollama_service import check_ollama_health
    return check_ollama_health()


@router.get("/history/{file_id}", status_code=200)
def get_ai_history(
    file_id     : int,
    db          : Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    """Get last saved AI insight for a file."""
    from app.models.ai_insight import AiInsight
    insight = db.query(AiInsight).filter(
        AiInsight.file_id == file_id
    ).first()
    if not insight:
        raise HTTPException(
            status_code=404,
            detail="No insights found. Run GET /ai/insights?file_id first."
        )
    return {
        "file_id"     : file_id,
        "model"       : insight.model_name,
        "ai_response" : insight.ai_response,
        "generated_at": insight.generated_at,
    }