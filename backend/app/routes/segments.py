from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from beanie import PydanticObjectId

from app.utils.dependencies import get_current_user, require_role
from app.models.users import User
from app.models.uploaded_file import UploadedFile, FileStatus
from app.models.segment_result import SegmentResult
from app.services.segmentation import run_segmentation_pipeline

router = APIRouter()

class MultiSegmentRequest(BaseModel):
    file_ids: List[str]

@router.post("/", status_code=200)
async def segment_multiple(
    body: MultiSegmentRequest,
    current_user: User = Depends(require_role("admin", "analyst")),
):
    """
    Run customer segmentation on a selection of one or more uploaded transaction files.
    """
    if not body.file_ids:
        raise HTTPException(status_code=400, detail="Must provide at least one file ID.")

    oids = [PydanticObjectId(fid) for fid in body.file_ids]
    files = await UploadedFile.find(
        {"_id": {"$in": oids}, "organization_id": current_user.organization_id}
    ).to_list()

    if len(files) != len(body.file_ids):
        raise HTTPException(status_code=404, detail="One or more files not found.")

    for file_record in files:
        if file_record.status not in [FileStatus.processed]:
            raise HTTPException(
                status_code=400,
                detail=f"File '{file_record.original_filename}' must be preprocessed first. "
                       f"Call POST /upload/preprocess/{file_record.id}"
            )

    try:
        result = await run_segmentation_pipeline(db=None, file_ids=body.file_ids)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    total_customers = sum(s.get("customer_count", 0) for s in result.segment_data)
    cluster_lookup = {s["cluster_id"]: {"label": s["label"], "color": s.get("color", "#3498DB")} for s in result.segment_data}
    chart_data = []
    for r in (result.rfm_scores or []):
        cid = r.get("Cluster", 0)
        meta = cluster_lookup.get(cid, {"label": "Other", "color": "#888888"})
        chart_data.append({
            "customer_id": r.get("customer_id", ""),
            "x": r.get("Frequency", 0),
            "y": r.get("Recency", 0),
            "z": r.get("Monetary", 0),
            "cluster_id": cid,
            "label": meta["label"],
            "color": meta["color"]
        })

    return {
        "file_ids": body.file_ids,
        "total_customers": int(total_customers),
        "silhouette_score": round(float(result.silhouette_score), 2),
        "total_segments": len(result.segment_data),
        "segments": result.segment_data,
        "chart_data": chart_data,
        "rfm_scores": result.rfm_scores,
        "message": f"Segmentation complete for {len(body.file_ids)} files."
    }

@router.post("/{file_id}", status_code=200)
async def segment(
    file_id: str,
    current_user: User = Depends(require_role("admin", "analyst")),
):
    """
    Run customer segmentation on a single uploaded transaction file.
    """
    req = MultiSegmentRequest(file_ids=[file_id])
    res = await segment_multiple(req, current_user)
    res["file_id"] = file_id
    return res


@router.get("/{file_id}", status_code=200)
async def get_segmentation(
    file_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get previously computed segmentation for a file."""
    oid = PydanticObjectId(file_id)
    file_record = await UploadedFile.find_one(
        UploadedFile.id == oid,
        UploadedFile.organization_id == current_user.organization_id
    )
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found.")

    result = await SegmentResult.find_one(
        SegmentResult.file_id == oid
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="No segmentation found. Run POST /segment/{file_id} first."
        )

    total_customers = sum(s.get("customer_count", 0) for s in result.segment_data)
    cluster_lookup = {s["cluster_id"]: {"label": s["label"], "color": s.get("color", "#3498DB")} for s in result.segment_data}
    chart_data = []
    for r in (result.rfm_scores or []):
        cid = r.get("Cluster", 0)
        meta = cluster_lookup.get(cid, {"label": "Other", "color": "#888888"})
        chart_data.append({
            "customer_id": r.get("customer_id", ""),
            "x": r.get("Frequency", 0),
            "y": r.get("Recency", 0),
            "z": r.get("Monetary", 0),
            "cluster_id": cid,
            "label": meta["label"],
            "color": meta["color"]
        })

    return {
        "file_id": file_id,
        "total_customers": int(total_customers),
        "silhouette_score": round(float(result.silhouette_score), 2),
        "total_segments": len(result.segment_data),
        "segments": result.segment_data,
        "chart_data": chart_data,
        "rfm_scores": result.rfm_scores,
        "generated_at": result.generated_at,
    }