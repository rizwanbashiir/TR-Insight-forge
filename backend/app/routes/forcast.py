from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from app.config.database import get_db
from app.utils.dependencies import get_current_user, require_role
from app.models.users import User
from app.services.forecasting import run_arima_forecast

router = APIRouter()

class MultiForecastRequest(BaseModel):
    file_ids: List[int]
    steps: int = 6

@router.post("/", status_code=200)
def forecast_multiple(
    body        : MultiForecastRequest,
    db          : Session = Depends(get_db),
    current_user: User    = Depends(require_role("admin", "analyst")),
):
    """
    Run time-series forecasting on a selection of one or more uploaded sales files.
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
                detail=f"File '{file_record.original_filename}' (ID {file_record.id}) must be preprocessed first."
            )

    try:
        result = run_arima_forecast(
            db       = db,
            file_ids = body.file_ids,
            steps    = body.steps,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "file_ids"   : body.file_ids,
        "model"      : result.model_name,
        "arima_order": result.arima_order,
        "mape_score" : float(result.mape_score),
        "accuracy"   : f"{round(100 - float(result.mape_score), 2)}%",
        "forecast"   : result.forecast_data,
        "message"    : f"Forecast complete for {len(body.file_ids)} files."
    }

@router.post("/{file_id}", status_code=200)
def forecast(
    file_id     : int,
    steps       : int  = 6,
    db          : Session = Depends(get_db),
    current_user: User    = Depends(require_role("admin", "analyst")),
):
    """
    Run ARIMA forecasting on a single uploaded sales file.
    """
    req = MultiForecastRequest(file_ids=[file_id], steps=steps)
    res = forecast_multiple(req, db, current_user)
    res["file_id"] = file_id
    return res


@router.get("/{file_id}", status_code=200)
def get_forecast(
    file_id     : int,
    db          : Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    """Get previously computed forecast for a file."""
    from app.models.forecast_result import ForecastResult
    from app.models.uploaded_file import UploadedFile

    db.query(UploadedFile).filter(
        UploadedFile.id      == file_id,
        UploadedFile.organization_id == current_user.organization_id
    ).first() or (_ for _ in ()).throw(
        HTTPException(status_code=404, detail="File not found.")
    )

    result = db.query(ForecastResult).filter(
        ForecastResult.file_id == file_id
    ).first()

    if not result:
        raise HTTPException(
            status_code=404,
            detail="No forecast found. Run POST /forecast/{file_id} first."
        )

    return {
        "file_id"    : file_id,
        "model"      : result.model_name,
        "arima_order": result.arima_order,
        "mape_score" : float(result.mape_score),
        "accuracy"   : f"{round(100 - float(result.mape_score), 2)}%",
        "forecast"   : result.forecast_data,
        "generated_at": result.generated_at,
    }