from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from app.config.database import get_db
from app.utils.dependencies import get_current_user, require_role
from app.models.users import User
from app.services.segmentation import run_segmentation_pipeline

router = APIRouter()

class MultiSegmentRequest(BaseModel):
    file_ids: List[int]

@router.post("/", status_code=200)
def segment_multiple(
    body        : MultiSegmentRequest,
    db          : Session = Depends(get_db),
    current_user: User    = Depends(require_role("admin", "analyst")),
):
    """
    Run customer segmentation on a selection of one or more uploaded transaction files.
    """
    from app.models.uploaded_file import UploadedFile, FileStatus

    if not body.file_ids:
        raise HTTPException(status_code=400, detail="Must provide at least one file ID.")

    # Verify all files exist and belong to this user's organization
    files = db.query(UploadedFile).filter(
        UploadedFile.id.in_(body.file_ids),
        UploadedFile.organization_id == current_user.organization_id
    ).all()

    if len(files) != len(body.file_ids):
        raise HTTPException(status_code=404, detail="One or more files not found.")

    for file_record in files:
        if file_record.status not in [FileStatus.processed]:
            raise HTTPException(
                status_code=400,
                detail=f"File '{file_record.original_filename}' (ID {file_record.id}) must be preprocessed first. "
                       f"Call POST /upload/preprocess/{file_record.id}"
            )

    try:
        result = run_segmentation_pipeline(db=db, file_ids=body.file_ids)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "file_ids"        : body.file_ids,
        "silhouette_score": float(result.silhouette_score),
        "total_segments"  : len(result.segment_data),
        "segments"        : result.segment_data,
        "message"         : f"Segmentation complete for {len(body.file_ids)} files."
    }

@router.post("/{file_id}", status_code=200)
def segment(
    file_id     : int,
    db          : Session = Depends(get_db),
    current_user: User    = Depends(require_role("admin", "analyst")),
):
    """
    Run customer segmentation on a single uploaded transaction file.
    """
    req = MultiSegmentRequest(file_ids=[file_id])
    res = segment_multiple(req, db, current_user)
    res["file_id"] = file_id
    return res


@router.get("/{file_id}", status_code=200)
def get_segmentation(
    file_id     : int,
    db          : Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    """Get previously computed segmentation for a file."""
    from app.models.segment_result import SegmentResult
    from app.models.uploaded_file import UploadedFile

    db.query(UploadedFile).filter(
        UploadedFile.id      == file_id,
        UploadedFile.organization_id == current_user.organization_id
    ).first() or (_ for _ in ()).throw(
        HTTPException(status_code=404, detail="File not found.")
    )

    result = db.query(SegmentResult).filter(
        SegmentResult.file_id == file_id
    ).first()

    if not result:
        raise HTTPException(
            status_code=404,
            detail="No segmentation found. Run POST /segment/{file_id} first."
        )

    return {
        "file_id"         : file_id,
        "silhouette_score": float(result.silhouette_score),
        "segments"        : result.segment_data,
        "generated_at"    : result.generated_at,
    }