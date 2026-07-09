import pandas as pd
from fastapi import HTTPException, UploadFile
from io import BytesIO
from datetime import datetime
from beanie import PydanticObjectId

from app.models.uploaded_file import UploadedFile, FileType, FileStatus
from app.models.raw_data_row import RawDataRow
from app.utils.column_mapping import detect_key_columns


def parse_uploaded_file(file: UploadFile) -> tuple[pd.DataFrame, str]:
    filename = file.filename.lower()
    contents = file.file.read()

    try:
        if filename.endswith(".csv"):
            encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
            parsed = False
            for encoding in encodings:
                try:
                    df = pd.read_csv(BytesIO(contents), encoding=encoding)
                    parsed = True
                    break
                except (UnicodeDecodeError, ValueError):
                    continue
            if not parsed:
                df = pd.read_csv(BytesIO(contents), encoding="utf-8")
            fmt = "csv"
        elif filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(BytesIO(contents))
            fmt = "xlsx"
        elif filename.endswith(".json"):
            df = pd.read_json(BytesIO(contents))
            fmt = "json"
        elif filename.endswith(".tsv"):
            encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
            parsed = False
            for encoding in encodings:
                try:
                    df = pd.read_csv(BytesIO(contents), sep="\t", encoding=encoding)
                    parsed = True
                    break
                except (UnicodeDecodeError, ValueError):
                    continue
            if not parsed:
                df = pd.read_csv(BytesIO(contents), sep="\t", encoding="utf-8")
            fmt = "tsv"
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported format. Use CSV, Excel, JSON or TSV."
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot read file: {str(e)}"
        )

    if df.empty:
        raise HTTPException(status_code=400, detail="File is empty.")

    df.columns = [
        str(c).strip().lower().replace(" ", "_")
        for c in df.columns
    ]

    return df, fmt


def parse_date_safe(value):
    if pd.isna(value):
        return None
    try:
        return pd.to_datetime(value).to_pydatetime().date()
    except Exception:
        return None


def parse_numeric_safe(value):
    if pd.isna(value):
        return None
    try:
        cleaned = (
            str(value)
            .replace(",", "")
            .replace("₹", "")
            .replace("$", "")
            .strip()
        )
        return float(cleaned)
    except Exception:
        return None


async def save_uploaded_file(
    db,
    file: UploadFile,
    file_type: str,
    user_id: str,
    organization_id: str
) -> UploadedFile:
    df, file_format = parse_uploaded_file(file)

    from app.services.quotas import verify_limits_and_tier
    await verify_limits_and_tier(db, organization_id, "row_count", len(df))

    detected = detect_key_columns(df)
    date_col_name = detected.get("date")
    amount_col_name = detected.get("amount")

    u_oid = PydanticObjectId(user_id) if isinstance(user_id, str) else user_id
    org_oid = PydanticObjectId(organization_id) if organization_id and isinstance(organization_id, str) else organization_id

    uploaded_file = UploadedFile(
        user_id=u_oid,
        organization_id=org_oid,
        original_filename=file.filename,
        file_format=file_format,
        file_type=file_type,
        row_count=len(df),
        column_count=len(df.columns),
        status=FileStatus.raw,
    )
    await uploaded_file.insert()

    raw_rows = []
    for idx, row in df.iterrows():
        raw_dict = {}
        for col, val in row.items():
            if pd.isna(val):
                raw_dict[col] = None
            elif isinstance(val, (int, float)):
                raw_dict[col] = val
            else:
                raw_dict[col] = str(val)

        date_value = parse_date_safe(row[date_col_name]) if date_col_name else None
        amount_value = parse_numeric_safe(row[amount_col_name]) if amount_col_name else None

        raw_rows.append(RawDataRow(
            file_id=uploaded_file.id,
            row_index=int(idx),
            raw_data=raw_dict,
            date_col=date_value,
            amount_col=amount_value,
        ))

    if raw_rows:
        await RawDataRow.insert_many(raw_rows)

    return uploaded_file