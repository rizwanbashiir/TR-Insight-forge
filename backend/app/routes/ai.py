from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List

from app.config.database import get_db
from app.utils.dependencies import get_current_user, require_role
from app.models.users import User

router = APIRouter()

class AIRequest(BaseModel):
    file_id : Optional[int] = None
    file_ids: Optional[List[int]] = None
    question: Optional[str] = None


@router.post("/ask", status_code=200)
def ask_ai(
    body        : AIRequest,
    db          : Session = Depends(get_db),
    current_user: User    = Depends(require_role("admin", "analyst")),
):
    """
    Ask a specific business question about your data.
    Leave question empty for general business health report.
    Body: {"file_ids": [11, 12], "question": "Which months had highest sales?"}
    """
    from app.services.ai_service import get_ai_answer
    from app.models.uploaded_file import UploadedFile, FileStatus
    from app.services.quotas import verify_limits_and_tier

    # Enforce AI Chat feature gate
    verify_limits_and_tier(db, current_user.organization_id, "ai_chat")

    resolved_file_ids = body.file_ids
    if not resolved_file_ids:
        if body.file_id is not None:
            resolved_file_ids = [body.file_id]
        else:
            raise HTTPException(status_code=400, detail="Either file_id or file_ids must be provided.")

    if not resolved_file_ids:
        raise HTTPException(status_code=400, detail="Must provide at least one file ID.")

    # Verify all files exist and belong to this user's organization
    files = db.query(UploadedFile).filter(
        UploadedFile.id.in_(resolved_file_ids),
        UploadedFile.organization_id == current_user.organization_id
    ).all()

    if len(files) != len(resolved_file_ids):
        raise HTTPException(status_code=404, detail="One or more files not found.")

    for file_record in files:
        if file_record.status not in [FileStatus.processed]:
            raise HTTPException(
                status_code=400,
                detail=f"File '{file_record.original_filename}' (ID {file_record.id}) must be preprocessed first."
            )

    try:
        result = get_ai_answer(
            db           = db,
            file_ids     = resolved_file_ids,
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
    file_id     : Optional[int]= Query(None, description="File ID"),
    file_ids    : Optional[List[int]]= Query(None, description="Optional list of file IDs"),
    question    : Optional[str]= Query(None, description="Optional question"),
    db          : Session      = Depends(get_db),
    current_user: User         = Depends(require_role("admin", "analyst")),
):
    """
    Generate AI-powered business recommendations.
    Usage: GET /ai/insights?file_id=11
    Or multiple: GET /ai/insights?file_ids=11&file_ids=12
    With question: GET /ai/insights?file_id=11&question=Why did sales drop?
    """
    from app.services.ai_service import get_ai_answer
    from app.models.uploaded_file import UploadedFile, FileStatus
    from app.services.quotas import verify_limits_and_tier

    # Enforce AI Chat feature gate
    verify_limits_and_tier(db, current_user.organization_id, "ai_chat")

    resolved_file_ids = file_ids
    if not resolved_file_ids:
        if file_id is not None:
            resolved_file_ids = [file_id]
        else:
            raise HTTPException(status_code=400, detail="Either file_id or file_ids must be provided.")

    if not resolved_file_ids:
        raise HTTPException(status_code=400, detail="Must provide at least one file ID.")

    # Verify all files exist and belong to this user's organization
    files = db.query(UploadedFile).filter(
        UploadedFile.id.in_(resolved_file_ids),
        UploadedFile.organization_id == current_user.organization_id
    ).all()

    if len(files) != len(resolved_file_ids):
        raise HTTPException(status_code=404, detail="One or more files not found.")

    for file_record in files:
        if file_record.status not in [FileStatus.processed]:
            raise HTTPException(
                status_code=400,
                detail=f"File '{file_record.original_filename}' (ID {file_record.id}) must be preprocessed first."
            )

    try:
        result = get_ai_answer(
            db           = db,
            file_ids     = resolved_file_ids,
            user_id      = current_user.id,
            user_question= question,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", status_code=200)
def ai_health():
    """Check if Grok API is reachable."""
    from app.services.grok_service import check_grok_health
    return check_grok_health()


@router.get("/history", status_code=200)
def list_ai_history(
    db          : Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    """List all saved AI chat insights/history for the organization's CHAT HISTORY panel."""
    from app.models.ai_insight import AiInsight
    from app.models.uploaded_file import UploadedFile

    insights = (
        db.query(AiInsight)
        .join(UploadedFile, AiInsight.file_id == UploadedFile.id)
        .filter(UploadedFile.organization_id == current_user.organization_id)
        .order_by(AiInsight.generated_at.desc())
        .all()
    )

    return [
        {
            "id"          : insight.id,
            "file_id"     : insight.file_id,
            "filename"    : insight.file.original_filename if insight.file else "Dataset",
            "model"       : insight.model_name,
            "ai_response" : insight.ai_response,
            "generated_at": insight.generated_at,
        }
        for insight in insights
    ]


@router.get("/history/{file_id}", status_code=200)
def get_ai_history(
    file_id     : int,
    db          : Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    """Get last saved AI insight for a file."""
    from app.models.ai_insight import AiInsight
    from app.models.uploaded_file import UploadedFile

    # Verify file belongs to this user's organization
    db.query(UploadedFile).filter(
        UploadedFile.id      == file_id,
        UploadedFile.organization_id == current_user.organization_id
    ).first() or (_ for _ in ()).throw(
        HTTPException(status_code=404, detail="File not found.")
    )

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