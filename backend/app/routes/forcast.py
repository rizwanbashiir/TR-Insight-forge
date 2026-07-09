from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from beanie import PydanticObjectId

from app.utils.dependencies import get_current_user, require_role
from app.models.users import User
from app.models.uploaded_file import UploadedFile, FileStatus
from app.models.forecast_result import ForecastResult
from app.services.forecasting import run_arima_forecast

router = APIRouter()

class MultiForecastRequest(BaseModel):
    file_ids: List[str]
    steps: int = 6
    model: Optional[str] = None
    confidence: Optional[float] = 0.95
    confidence_interval: Optional[float] = 0.95

@router.post("/", status_code=200)
async def forecast_multiple(
    body: MultiForecastRequest,
    current_user: User = Depends(require_role("admin", "analyst")),
):
    """
    Run time-series forecasting on a selection of one or more uploaded sales files.
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
                detail=f"File '{file_record.original_filename}' must be preprocessed first."
            )

    try:
        result = await run_arima_forecast(
            db=None,
            file_ids=body.file_ids,
            steps=body.steps,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    conf_val = body.confidence or body.confidence_interval or 0.95
    conf_str = f"{round(conf_val * 100)}%"

    return {
        "file_ids": body.file_ids,
        "model": body.model or result.model_name,
        "arima_order": result.arima_order,
        "mape_score": float(result.mape_score),
        "mape": f"{round(float(result.mape_score), 1)}%",
        "accuracy": f"{round(100 - float(result.mape_score), 1)}%",
        "confidence": conf_str,
        "forecast": result.forecast_data,
        "message": f"Forecast complete for {len(body.file_ids)} files."
    }

@router.post("/{file_id}", status_code=200)
async def forecast(
    file_id: str,
    steps: int = 6,
    model: Optional[str] = None,
    confidence: Optional[float] = 0.95,
    current_user: User = Depends(require_role("admin", "analyst")),
):
    """
    Run ARIMA forecasting on a single uploaded sales file.
    """
    req = MultiForecastRequest(file_ids=[file_id], steps=steps, model=model, confidence=confidence)
    res = await forecast_multiple(req, current_user)
    res["file_id"] = file_id
    return res


@router.get("/{file_id}", status_code=200)
async def get_forecast(
    file_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get previously computed forecast for a file."""
    oid = PydanticObjectId(file_id)
    file_record = await UploadedFile.find_one(
        UploadedFile.id == oid,
        UploadedFile.organization_id == current_user.organization_id
    )
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found.")

    result = await ForecastResult.find_one(
        ForecastResult.file_id == oid
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="No forecast found. Run POST /forecast/{file_id} first."
        )

    return {
        "file_id": file_id,
        "model": result.model_name,
        "arima_order": result.arima_order,
        "mape_score": float(result.mape_score),
        "mape": f"{round(float(result.mape_score), 1)}%",
        "accuracy": f"{round(100 - float(result.mape_score), 1)}%",
        "confidence": "95%",
        "forecast": result.forecast_data,
        "generated_at": result.generated_at,
    }