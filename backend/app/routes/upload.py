from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, List

from app.config.database import get_db, SessionLocal
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
from app.models.ai_insight import AiInsight

router = APIRouter()

def run_background_ingestion(file_id: int):
    """
    Background worker to automatically clean data, compute KPIs,
    and store vector embeddings in Pinecone immediately after upload.
    """
    db = SessionLocal()
    try:
        # 1. Run Preprocessing Pipeline (cleans data, computes KPIs)
        run_preprocessing_pipeline(db=db, file_id=file_id)
        # 2. Run Embedding & Pinecone Upsert
        embed_and_store(db=db, file_id=file_id)
    except Exception as e:
        print(f"Error running automated background ingestion for file {file_id}: {str(e)}")
    finally:
        db.close()

@router.post("/", response_model=List[UploadResponse], status_code=201)
async def upload_file(
    background_tasks: BackgroundTasks,
    file     : Optional[UploadFile] = File(None),
    files    : Optional[List[UploadFile]] = File(None),
    file_type: FileType   = Form(...),      # user tells us: sales/expenses/etc
    db       : Session    = Depends(get_db),
    current_user: User    = Depends(require_role("admin", "analyst")),
):
    """
    Upload one or more business data files (CSV, Excel, JSON, TSV).
    The file_type field tells the system how to interpret the data.
    Raw data is saved to PostgreSQL immediately, and preprocessing + embedding
    are automatically run in the background.
    """
    uploaded_files_list = []
    if file:
        uploaded_files_list.append(file)
    if files:
        uploaded_files_list.extend(files)

    if not uploaded_files_list:
        raise HTTPException(
            status_code=400,
            detail="No files uploaded. Use 'file' or 'files' parameter."
        )

    responses = []
    MAX_SIZE = 50 * 1024 * 1024

    from app.services.quotas import verify_limits_and_tier

    for f in uploaded_files_list:
        # Verify file count limit for organization
        verify_limits_and_tier(db, current_user.organization_id, "upload")

        # Validate file size before reading (max 50MB)
        f.file.seek(0, 2)            # seek to end
        file_size = f.file.tell()
        f.file.seek(0)               # reset to start

        if file_size > MAX_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File '{f.filename}' is too large. Maximum size is 50MB."
            )

        uploaded = save_uploaded_file(
            db        = db,
            file      = f,
            file_type = file_type,
            user_id   = current_user.id,
            organization_id = current_user.organization_id,
        )

        # Queue background task for automatic preprocessing and embedding
        background_tasks.add_task(run_background_ingestion, uploaded.id)

        responses.append(UploadResponse(
            file_id          = uploaded.id,
            original_filename= uploaded.original_filename,
            file_type        = uploaded.file_type,
            file_format      = uploaded.file_format,
            row_count        = uploaded.row_count,
            column_count     = uploaded.column_count,
            columns_detected = [],
            status           = uploaded.status,
            uploaded_at      = uploaded.uploaded_at,
            message          = f"File '{f.filename}' uploaded successfully. "
                               f"{uploaded.row_count} rows saved to database."
        ))

    return responses

@router.get("/{file_id}", status_code=200)
def get_file_status(
    file_id     : int,
    db          : Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    """Check the status of an uploaded file."""
    from app.models.uploaded_file import UploadedFile

    record = db.query(UploadedFile).filter(
        UploadedFile.id      == file_id,
        UploadedFile.organization_id == current_user.organization_id   # users can only see their organization's files
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="File not found.")

    return {
        "file_id"  : record.id,
        "filename" : record.original_filename,
        "file_type": record.file_type,
        "row_count": record.row_count,
        "status"   : record.status,
        "uploaded_at": record.uploaded_at,
    }

@router.get("/details/{file_id}", status_code=200)
def get_project_details(
    file_id     : int,
    db          : Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    """
    Get all details, ML results, and RAG histories associated with a file (project).
    Includes preprocessing status, KPI summaries, ARIMA forecasts, RFM segments, and AI insights.
    """
    file_record = db.query(UploadedFile).filter(
        UploadedFile.id      == file_id,
        UploadedFile.organization_id == current_user.organization_id
    ).first()

    if not file_record:
        raise HTTPException(status_code=404, detail="File/Project not found.")

    # Fetch dependent results
    processed = db.query(ProcessedDataset).filter(ProcessedDataset.file_id == file_id).first()
    forecast = db.query(ForecastResult).filter(ForecastResult.file_id == file_id).first()
    segment = db.query(SegmentResult).filter(SegmentResult.file_id == file_id).first()
    ai_insight = db.query(AiInsight).filter(AiInsight.file_id == file_id).first()

    return {
        "file_info": {
            "id": file_record.id,
            "filename": file_record.original_filename,
            "file_type": file_record.file_type,
            "file_format": file_record.file_format,
            "row_count": file_record.row_count,
            "column_count": file_record.column_count,
            "status": file_record.status,
            "uploaded_at": file_record.uploaded_at,
            "error_message": file_record.error_message,
        },
        "preprocessing": {
            "is_processed": processed is not None,
            "processed_at": processed.processed_at if processed else None,
            "missing_values": processed.missing_values if processed else None,
            "outliers_detected": processed.outliers_detected if processed else None,
            "column_types": processed.column_types if processed else None,
            "kpi_summary": processed.kpi_summary if processed else None,
        },
        "forecast": {
            "has_forecast": forecast is not None,
            "model_name": forecast.model_name if forecast else None,
            "mape_score": float(forecast.mape_score) if forecast and forecast.mape_score else None,
            "accuracy": f"{round(100 - float(forecast.mape_score), 2)}%" if forecast and forecast.mape_score else None,
            "forecast_data": forecast.forecast_data if forecast else None,
            "generated_at": forecast.generated_at if forecast else None,
        },
        "segmentation": {
            "has_segmentation": segment is not None,
            "silhouette_score": float(segment.silhouette_score) if segment and segment.silhouette_score is not None else None,
            "segments": segment.segment_data if segment else None,
            "generated_at": segment.generated_at if segment else None,
        },
        "ai_insights": {
            "has_insights": ai_insight is not None,
            "model_name": ai_insight.model_name if ai_insight else None,
            "ai_response": ai_insight.ai_response if ai_insight else None,
            "generated_at": ai_insight.generated_at if ai_insight else None,
        }
    }


@router.get("/", status_code=200)
def list_my_files(
    db          : Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    """List all files uploaded by the current user's organization."""
    from app.models.uploaded_file import UploadedFile

    files = db.query(UploadedFile).filter(
        UploadedFile.organization_id == current_user.organization_id
    ).order_by(UploadedFile.uploaded_at.desc()).all()

    return [
        {
            "file_id"    : f.id,
            "filename"   : f.original_filename,
            "file_type"  : f.file_type,
            "row_count"  : f.row_count,
            "status"     : f.status,
            "uploaded_at": f.uploaded_at,
        }
        for f in files
    ]


@router.post("/preprocess/{file_id}", status_code=200)
def preprocess_file(
    file_id     : int,
    db          : Session    = Depends(get_db),
    current_user: User       = Depends(require_role("admin", "analyst")),
):
    """
    Trigger preprocessing for an uploaded file.
    Cleans data, detects issues, computes KPIs.
    Saves results to processed_datasets table.
    """
    from app.models.uploaded_file import UploadedFile

    # Verify file belongs to this user's organization
    file_record = db.query(UploadedFile).filter(
        UploadedFile.id      == file_id,
        UploadedFile.organization_id == current_user.organization_id
    ).first()

    if not file_record:
        raise HTTPException(status_code=404, detail="File not found.")

    if file_record.status == FileStatus.processing:
        raise HTTPException(status_code=400, detail="File is already being processed.")

    # Run the full pipeline
    result = run_preprocessing_pipeline(db=db, file_id=file_id)

    return {
        "file_id"          : file_id,
        "status"           : "processed",
        "total_rows"       : result.total_rows,
        "duplicates_removed": result.duplicate_count,
        "missing_values"   : result.missing_values,
        "outliers_detected": result.outliers_detected,
        "column_types"     : result.column_types,
        "kpi_summary"      : result.kpi_summary,
        "message"          : "Preprocessing complete. KPIs computed successfully."
    }


@router.post("/embed/{file_id}", status_code=200)
def embed_file(
    file_id     : int,
    db          : Session = Depends(get_db),
    current_user: User    = Depends(require_role("admin", "analyst")),
):
    """
    Embed processed KPI data into Pinecone for RAG.
    Must run /preprocess/{file_id} first.
    """
    from app.models.uploaded_file import UploadedFile

    file_record = db.query(UploadedFile).filter(
        UploadedFile.id      == file_id,
        UploadedFile.organization_id == current_user.organization_id
    ).first()

    if not file_record:
        raise HTTPException(status_code=404, detail="File not found.")

    if file_record.status != FileStatus.processed:
        raise HTTPException(
            status_code=400,
            detail="File must be preprocessed before embedding. "
                   "Call /upload/preprocess/{file_id} first."
        )

    result = embed_and_store(db=db, file_id=file_id)

    return {
        "message"      : "Data successfully embedded into Pinecone.",
        "file_id"      : result["file_id"],
        "chunks_stored": result["chunks_stored"],
        "vector_dim"   : result["vector_dim"],
        "chunk_ids"    : result["chunk_ids"],
    }