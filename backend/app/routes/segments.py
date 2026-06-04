from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.utils.dependencies import get_current_user
from app.models.users import User
from app.services.segmentation import run_segmentation_pipeline

router = APIRouter()

@router.post("/{file_id}", status_code=200)
def segment(
    file_id     : int,
    db          : Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    """
    Run K-Means + RFM customer segmentation.
    Segments customers into: Retention, Upsell, Win-back, Nurture.
    """
    from app.models.uploaded_file import UploadedFile, FileStatus

    file_record = db.query(UploadedFile).filter(
        UploadedFile.id      == file_id,
        UploadedFile.user_id == current_user.id
    ).first()

    if not file_record:
        raise HTTPException(status_code=404, detail="File not found.")

    if file_record.status not in [FileStatus.processed]:
        raise HTTPException(
            status_code=400,
            detail="File must be preprocessed first. "
                   "Call POST /upload/preprocess/{file_id}"
        )

    try:
        result = run_segmentation_pipeline(db=db, file_id=file_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "file_id"         : file_id,
        "silhouette_score": float(result.silhouette_score),
        "total_segments"  : len(result.segment_data),
        "segments"        : result.segment_data,
        "message"         : (
            f"Segmentation complete. "
            f"Silhouette score: {result.silhouette_score}"
        )
    }


@router.get("/{file_id}", status_code=200)
def get_segmentation(
    file_id     : int,
    db          : Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    """Get previously computed segmentation for a file."""
    from app.models.segment_result import SegmentResult

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