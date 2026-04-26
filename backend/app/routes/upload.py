from fastapi import APIRouter, UploadFile, File, HTTPException
import pandas as pd

from app.services.preprocessing import clean_data

router = APIRouter()


@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    try:
        filename = file.filename.lower()

        # CSV
        if filename.endswith(".csv"):
            df = pd.read_csv(file.file)

        # Excel
        elif filename.endswith(".xlsx") or filename.endswith(".xls"):
            df = pd.read_excel(file.file)

        else:
            raise HTTPException(
                status_code=400,
                detail="Only CSV and Excel files are supported"
            )

        # Run preprocessing
        cleaned_df, report = clean_data(df)

        return {
            "filename": file.filename,
            "columns": cleaned_df.columns.tolist(),
            "total_rows_after_cleaning": len(cleaned_df),
            "preprocessing_report": report,
            "preview": cleaned_df.head(5).to_dict(orient="records")
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )