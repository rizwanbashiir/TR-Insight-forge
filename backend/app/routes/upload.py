from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks
import asyncio
from beanie import PydanticObjectId

from app.schemas.upload import UploadResponse, FileType, FileStatus
from app.services.upload_service import save_uploaded_file
from app.utils.dependencies import get_current_user, require_role
from app.services.preprocessing import run_preprocessing_pipeline
from app.services.pinecone_service import embed_and_store
from app.models.uploaded_file import UploadedFile
from app.models.processed_dataset import ProcessedDataset
from app.models.users import User
from app.models.forecast_result import ForecastResult
from app.models.segment_result import SegmentResult
from app.models.ai_insight import AIInsight

router = APIRouter()


async def run_background_ingestion(file_id: str):
    """
    Background worker — auto preprocessing + Pinecone embedding after upload.
    """
    try:
        await run_preprocessing_pipeline(db=None, file_id=file_id)
        await embed_and_store(db=None, file_id=file_id)
    except Exception as e:
        print(f"Error running automated background ingestion for file {file_id}: {str(e)}")


@router.post("/", response_model=UploadResponse, status_code=201)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    file_type: FileType = Form(...),
    current_user: User = Depends(require_role("admin", "analyst")),
):
    MAX_SIZE = 50 * 1024 * 1024
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > MAX_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File too large. Maximum size is 50MB."
        )

    from app.services.quotas import verify_limits_and_tier
    await verify_limits_and_tier(None, current_user.organization_id, "upload")

    uploaded = await save_uploaded_file(
        db=None,
        file=file,
        file_type=file_type,
        user_id=str(current_user.id),
        organization_id=str(current_user.organization_id) if current_user.organization_id else None,
    )

    background_tasks.add_task(run_background_ingestion, str(uploaded.id))

    return UploadResponse(
        file_id=str(uploaded.id),
        original_filename=uploaded.original_filename,
        file_type=uploaded.file_type,
        file_format=uploaded.file_format,
        row_count=uploaded.row_count,
        column_count=uploaded.column_count,
        columns_detected=[],
        status=uploaded.status,
        uploaded_at=uploaded.uploaded_at,
        message=f"File uploaded. {uploaded.row_count} rows saved. Preprocessing running in background."
    )


@router.post("/preprocess/{file_id}", status_code=200)
async def preprocess_file(
    file_id: str,
    current_user: User = Depends(require_role("admin", "analyst")),
):
    oid = PydanticObjectId(file_id)
    file_record = await UploadedFile.find_one(
        UploadedFile.id == oid,
        UploadedFile.user_id == current_user.id
    )

    if not file_record:
        raise HTTPException(status_code=404, detail="File not found.")

    if file_record.status == FileStatus.processing:
        raise HTTPException(status_code=400, detail="Already processing.")

    result = await run_preprocessing_pipeline(db=None, file_id=file_id)

    return {
        "file_id": file_id,
        "status": "processed",
        "total_rows": result.total_rows,
        "duplicates_removed": result.duplicate_count,
        "missing_values": result.missing_values,
        "outliers_detected": result.outliers_detected,
        "column_types": result.column_types,
        "kpi_summary": result.kpi_summary,
        "message": "Preprocessing complete."
    }


@router.post("/embed/{file_id}", status_code=200)
async def embed_file(
    file_id: str,
    current_user: User = Depends(require_role("admin", "analyst")),
):
    oid = PydanticObjectId(file_id)
    file_record = await UploadedFile.find_one(
        UploadedFile.id == oid,
        UploadedFile.user_id == current_user.id
    )

    if not file_record:
        raise HTTPException(status_code=404, detail="File not found.")

    result = await embed_and_store(db=None, file_id=file_id)

    return {
        "message": "Embedded into Pinecone.",
        "file_id": result["file_id"],
        "chunks_stored": result["chunks_stored"],
        "vector_dim": result["vector_dim"],
    }


@router.get("/", status_code=200)
async def list_my_files(
    current_user: User = Depends(get_current_user),
):
    if current_user.organization_id:
        files = await UploadedFile.find(
            UploadedFile.organization_id == current_user.organization_id
        ).sort("-uploaded_at").to_list()
    else:
        files = await UploadedFile.find(
            UploadedFile.user_id == current_user.id
        ).sort("-uploaded_at").to_list()

    return [
        {
            "file_id": str(f.id),
            "filename": f.original_filename,
            "file_type": f.file_type,
            "row_count": f.row_count,
            "status": f.status,
            "uploaded_at": f.uploaded_at,
        }
        for f in files
    ]


@router.get("/details/{file_id}", status_code=200)
async def get_project_details(
    file_id: str,
    current_user: User = Depends(get_current_user),
):
    oid = PydanticObjectId(file_id)
    file_record = await UploadedFile.find_one(
        UploadedFile.id == oid,
        UploadedFile.user_id == current_user.id
    )

    if not file_record:
        raise HTTPException(status_code=404, detail="File not found.")

    processed = await ProcessedDataset.find_one(ProcessedDataset.file_id == oid)
    forecast = await ForecastResult.find_one(ForecastResult.file_id == oid)
    segment = await SegmentResult.find_one(SegmentResult.file_id == oid)
    ai_insight = await AIInsight.find_one(AIInsight.file_id == oid)

    return {
        "file_info": {
            "id": str(file_record.id),
            "filename": file_record.original_filename,
            "file_type": file_record.file_type,
            "row_count": file_record.row_count,
            "status": file_record.status,
            "uploaded_at": file_record.uploaded_at,
            "error_message": file_record.error_message,
        },
        "preprocessing": {
            "is_processed": processed is not None,
            "kpi_summary": processed.kpi_summary if processed else None,
            "missing_values": processed.missing_values if processed else None,
            "outliers_detected": processed.outliers_detected if processed else None,
        },
        "forecast": {
            "has_forecast": forecast is not None,
            "mape_score": float(forecast.mape_score) if forecast and forecast.mape_score else None,
            "accuracy": f"{round(100 - float(forecast.mape_score), 2)}%" if forecast and forecast.mape_score else None,
            "forecast_data": forecast.forecast_data if forecast else None,
        },
        "segmentation": {
            "has_segmentation": segment is not None,
            "silhouette_score": float(segment.silhouette_score) if segment and segment.silhouette_score else None,
            "segments": segment.segment_data if segment else None,
        },
        "ai_insights": {
            "has_insights": ai_insight is not None,
            "ai_response": ai_insight.ai_response if ai_insight else None,
        }
    }


@router.get("/{file_id}", status_code=200)
async def get_file_status(
    file_id: str,
    current_user: User = Depends(get_current_user),
):
    oid = PydanticObjectId(file_id)
    record = await UploadedFile.find_one(
        UploadedFile.id == oid,
        UploadedFile.user_id == current_user.id
    )

    if not record:
        raise HTTPException(status_code=404, detail="File not found.")

    return {
        "file_id": str(record.id),
        "filename": record.original_filename,
        "file_type": record.file_type,
        "row_count": record.row_count,
        "status": record.status,
        "uploaded_at": record.uploaded_at,
    }