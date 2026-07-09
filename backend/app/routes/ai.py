from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from beanie import PydanticObjectId

from app.utils.dependencies import get_current_user, require_role
from app.models.users import User
from app.models.uploaded_file import UploadedFile, FileStatus
from app.models.ai_insight import AIInsight
from app.services.ai_service import get_ai_answer

router = APIRouter()

class AIRequest(BaseModel):
    file_id: Optional[str] = None
    file_ids: Optional[List[str]] = None
    question: Optional[str] = None


@router.post("/ask", status_code=200)
async def ask_ai(
    body: AIRequest,
    current_user: User = Depends(require_role("admin", "analyst")),
):
    """
    Ask a specific business question about your data.
    Leave question empty for general business health report.
    """
    from app.services.quotas import verify_limits_and_tier
    await verify_limits_and_tier(None, current_user.organization_id, "ai_chat")

    resolved_file_ids = body.file_ids
    if not resolved_file_ids:
        if body.file_id is not None:
            resolved_file_ids = [body.file_id]
        else:
            raise HTTPException(status_code=400, detail="Either file_id or file_ids must be provided.")

    oids = [PydanticObjectId(fid) for fid in resolved_file_ids]
    files = await UploadedFile.find(
        {"_id": {"$in": oids}, "organization_id": current_user.organization_id}
    ).to_list()

    if len(files) != len(resolved_file_ids):
        raise HTTPException(status_code=404, detail="One or more files not found.")

    for file_record in files:
        if file_record.status not in [FileStatus.processed]:
            raise HTTPException(
                status_code=400,
                detail=f"File '{file_record.original_filename}' must be preprocessed first."
            )

    try:
        result = await get_ai_answer(
            db=None,
            file_ids=resolved_file_ids,
            user_id=str(current_user.id),
            user_question=body.question,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights", status_code=200)
async def get_ai_insights(
    file_id: Optional[str] = Query(None, description="File ID"),
    file_ids: Optional[List[str]] = Query(None, description="Optional list of file IDs"),
    question: Optional[str] = Query(None, description="Optional question"),
    current_user: User = Depends(require_role("admin", "analyst")),
):
    from app.services.quotas import verify_limits_and_tier
    await verify_limits_and_tier(None, current_user.organization_id, "ai_chat")

    resolved_file_ids = file_ids
    if not resolved_file_ids:
        if file_id is not None:
            resolved_file_ids = [file_id]
        else:
            raise HTTPException(status_code=400, detail="Either file_id or file_ids must be provided.")

    oids = [PydanticObjectId(fid) for fid in resolved_file_ids]
    files = await UploadedFile.find(
        {"_id": {"$in": oids}, "organization_id": current_user.organization_id}
    ).to_list()

    if len(files) != len(resolved_file_ids):
        raise HTTPException(status_code=404, detail="One or more files not found.")

    for file_record in files:
        if file_record.status not in [FileStatus.processed]:
            raise HTTPException(
                status_code=400,
                detail=f"File '{file_record.original_filename}' must be preprocessed first."
            )

    try:
        result = await get_ai_answer(
            db=None,
            file_ids=resolved_file_ids,
            user_id=str(current_user.id),
            user_question=question,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", status_code=200)
def ai_health():
    from app.services.grok_service import check_grok_health
    return check_grok_health()


@router.get("/history", status_code=200)
async def list_ai_history(
    current_user: User = Depends(get_current_user),
):
    files = await UploadedFile.find(
        UploadedFile.organization_id == current_user.organization_id
    ).to_list()

    file_ids = [f.id for f in files]
    file_map = {f.id: f.original_filename for f in files}

    insights = await AIInsight.find(
        {"file_id": {"$in": file_ids}}
    ).sort("-generated_at").to_list()

    return [
        {
            "id": str(insight.id),
            "file_id": str(insight.file_id),
            "filename": file_map.get(insight.file_id, "Dataset"),
            "model": insight.model_name,
            "ai_response": insight.ai_response,
            "generated_at": insight.generated_at,
        }
        for insight in insights
    ]


@router.get("/history/{file_id}", status_code=200)
async def get_ai_history(
    file_id: str,
    current_user: User = Depends(get_current_user),
):
    oid = PydanticObjectId(file_id)
    file_record = await UploadedFile.find_one(
        UploadedFile.id == oid,
        UploadedFile.organization_id == current_user.organization_id
    )
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found.")

    insight = await AIInsight.find_one(
        AIInsight.file_id == oid
    )

    if not insight:
        raise HTTPException(
            status_code=404,
            detail="No insights found. Run GET /ai/insights?file_id first."
        )

    return {
        "file_id": file_id,
        "model": insight.model_name,
        "ai_response": insight.ai_response,
        "generated_at": insight.generated_at,
    }