from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.schemas.upload import UploadResponse, FileType
from app.services.upload_service import save_uploaded_file
from app.utils.dependencies import get_current_user
from app.services.preprocessing import run_preprocessing_pipeline
from app.schemas.upload import UploadResponse, FileType, FileStatus
from app.services.pinecone_service import embed_and_store
from app.models.uploaded_file import UploadedFile
from app.models.processed_dataset import ProcessedDataset
from app.services.pinecone_service import embedding_model, get_pinecone_index
from app.models.users import User

router = APIRouter()

@router.post("/", response_model=UploadResponse, status_code=201)
async def upload_file(
    file     : UploadFile = File(...),
    file_type: FileType   = Form(...),      # user tells us: sales/expenses/etc
    db       : Session    = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    """
    Upload a business data file (CSV, Excel, JSON, TSV).
    The file_type field tells the system how to interpret the data.
    Raw data is saved to PostgreSQL immediately.
    """

    # Validate file size before reading (max 50MB)
    MAX_SIZE = 50 * 1024 * 1024
    file.file.seek(0, 2)            # seek to end
    file_size = file.file.tell()
    file.file.seek(0)               # reset to start

    if file_size > MAX_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File too large. Maximum size is 50MB."
        )

    uploaded = save_uploaded_file(
        db        = db,
        file      = file,
        file_type = file_type,
        user_id   = current_user.id,
    )

    return UploadResponse(
        file_id          = uploaded.id,
        original_filename= uploaded.original_filename,
        file_type        = uploaded.file_type,
        file_format      = uploaded.file_format,
        row_count        = uploaded.row_count,
        column_count     = uploaded.column_count,
        columns_detected = [],      # will populate in 2B
        status           = uploaded.status,
        uploaded_at      = uploaded.uploaded_at,
        message          = f"File uploaded successfully. "
                           f"{uploaded.row_count} rows saved to database."
    )


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
        UploadedFile.user_id == current_user.id   # users can only see their own files
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


@router.get("/", status_code=200)
def list_my_files(
    db          : Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    """List all files uploaded by the current user."""
    from app.models.uploaded_file import UploadedFile

    files = db.query(UploadedFile).filter(
        UploadedFile.user_id == current_user.id
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
    current_user: User       = Depends(get_current_user),
):
    """
    Trigger preprocessing for an uploaded file.
    Cleans data, detects issues, computes KPIs.
    Saves results to processed_datasets table.
    """
    from app.models.uploaded_file import UploadedFile

    # Verify file belongs to this user
    file_record = db.query(UploadedFile).filter(
        UploadedFile.id      == file_id,
        UploadedFile.user_id == current_user.id
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
    current_user: User    = Depends(get_current_user),
):
    """
    Embed processed KPI data into Pinecone for RAG.
    Must run /preprocess/{file_id} first.
    """
   

    file_record = db.query(UploadedFile).filter(
        UploadedFile.id      == file_id,
        UploadedFile.user_id == current_user.id
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