from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from beanie import PydanticObjectId

from app.utils.dependencies import get_current_user, require_role
from app.models.users import User
from app.models.uploaded_file import UploadedFile, FileStatus
from app.models.ai_insight import AIInsight
from app.services.ai_service import get_ai_answer, generate_business_health_check, DEFAULT_SUGGESTED_QUESTIONS

router = APIRouter()

class AIRequest(BaseModel):
    file_id: Optional[str] = None
    file_ids: Optional[List[str]] = None
    question: Optional[str] = None


async def resolve_workspace_files(file_ids: Optional[List[str]], file_id: Optional[str], current_user: User) -> List[str]:
    if file_ids:
        resolved = file_ids
    elif file_id:
        resolved = [file_id]
    else:
        files = await UploadedFile.find(
            {"organization_id": current_user.organization_id, "status": FileStatus.processed}
        ).to_list()
        if not files:
            raise HTTPException(
                status_code=400,
                detail="No preprocessed files found in your workspace. Please upload and preprocess your datasets first."
            )
        return [str(f.id) for f in files]

    oids = []
    for fid in resolved:
        try:
            oids.append(PydanticObjectId(fid))
        except Exception:
            raise HTTPException(status_code=400, detail=f"Invalid file ID format: '{fid}'.")

    files = await UploadedFile.find(
        {"_id": {"$in": oids}, "organization_id": current_user.organization_id}
    ).to_list()

    if len(files) != len(resolved):
        raise HTTPException(status_code=404, detail="One or more files not found.")

    for file_record in files:
        if file_record.status not in [FileStatus.processed]:
            raise HTTPException(
                status_code=400,
                detail=f"File '{file_record.original_filename}' must be preprocessed first."
            )
    return resolved


@router.get("/suggested-questions", status_code=200)
async def get_suggested_questions():
    """
    Get default suggested business questions (Strengths, Expenses, Dead Inventory, Growth).
    """
    return {"suggested_questions": DEFAULT_SUGGESTED_QUESTIONS}


@router.get("/business-health-check", status_code=200)
async def get_business_health_check(
    file_ids: Optional[List[str]] = Query(None, description="Optional explicit file IDs"),
    current_user: User = Depends(require_role("admin", "analyst")),
):
    """
    Landing Dashboard module: comprehensive Business Health Check across all uploaded workspace files.
    Covers Strengths, Expense Reduction, Dead Inventory, and Strategic Roadmap.
    """
    resolved_file_ids = await resolve_workspace_files(file_ids, None, current_user)
    try:
        report = await generate_business_health_check(resolved_file_ids)
        return report
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ask", status_code=200)
async def ask_ai(
    body: AIRequest,
    current_user: User = Depends(require_role("admin", "analyst")),
):
    """
    Ask a specific business question across your data.
    If file_ids is omitted, automatically queries across all preprocessed workspace datasets.
    """
    from app.services.quotas import verify_limits_and_tier
    await verify_limits_and_tier(None, current_user.organization_id, "ai_chat")

    resolved_file_ids = await resolve_workspace_files(body.file_ids, body.file_id, current_user)

    try:
        result = await get_ai_answer(
            db=None,
            file_ids=resolved_file_ids,
            user_id=str(current_user.id),
            user_question=body.question,
        )
        result["suggested_questions"] = DEFAULT_SUGGESTED_QUESTIONS
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

    resolved_file_ids = await resolve_workspace_files(file_ids, file_id, current_user)

    try:
        result = await get_ai_answer(
            db=None,
            file_ids=resolved_file_ids,
            user_id=str(current_user.id),
            user_question=question,
        )
        result["suggested_questions"] = DEFAULT_SUGGESTED_QUESTIONS
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