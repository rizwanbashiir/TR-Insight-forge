from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.utils.dependencies import get_current_user
from app.models.users import User
from app.services.forecasting import run_arima_forecast

router = APIRouter()

@router.post("/{file_id}", status_code=200)
def forecast(
    file_id     : int,
    steps       : int  = 6,
    db          : Session = Depends(get_db),
    current_user: User    = Depends(get_current_user),
):
    """
    Run ARIMA forecasting on uploaded sales data.
    Returns 6-month revenue forecast with 95% confidence intervals.
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
            detail="File must be preprocessed first."
        )

    try:
        result = run_arima_forecast(
            db     = db,
            file_id= file_id,
            steps  = steps,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "file_id"    : file_id,
        "model"      : "ARIMA",
        "arima_order": result.arima_order,
        "mape_score" : float(result.mape_score),
        "accuracy"   : f"{round(100 - float(result.mape_score), 2)}%",
        "forecast"   : result.forecast_data,
        "message"    : (
            f"Forecast complete. "
            f"Model accuracy: {round(100 - float(result.mape_score), 2)}%"
        )
    }


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
        UploadedFile.user_id == current_user.id
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