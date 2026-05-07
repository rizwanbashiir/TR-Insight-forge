import pandas as pd
import json
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from io import BytesIO
from datetime import datetime

from app.models.uploaded_file import UploadedFile, FileType, FileStatus
from app.models.raw_data_row import RawDataRow

# ── Column name mappings per file type ──────────────────────────────
# We try to auto-detect which column is "date" and which is "amount"
# by checking common column name variations

DATE_ALIASES = [
    "Date", "order_date", "transaction_date", "invoice_date",
    "sale_date", "expense_date", "period", "month", "day" , "CPI", "Temperature"
]

AMOUNT_ALIASES = {
    "sales"    : ["revenue", "sales", "amount", "total", "sales_amount",
                  "total_revenue", "price", "net_sales"],
    "expenses" : ["amount", "expense", "cost", "total", "expense_amount",
                  "spend", "expenditure"],
    "income"   : ["amount", "income", "revenue", "total", "income_amount",
                  "earnings", "gross_income"],
    "inventory": ["quantity", "qty", "stock", "units", "quantity_on_hand"],
    "custom"   : ["amount", "value", "total", "revenue", "cost"],
}
def parse_uploaded_file(file: UploadFile) -> tuple[pd.DataFrame, str]:
    filename = file.filename.lower()
    contents = file.file.read()

    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(BytesIO(contents))
            fmt = "csv"
        elif filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(BytesIO(contents))
            fmt = "xlsx"
        elif filename.endswith(".json"):
            df = pd.read_json(BytesIO(contents))
            fmt = "json"
        elif filename.endswith(".tsv"):
            df = pd.read_csv(BytesIO(contents), sep="\t")
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

    # Normalize column names — lowercase, no spaces
    df.columns = [
        str(c).strip().lower().replace(" ", "_")
        for c in df.columns
    ]

    return df, fmt


# ── Column detectors ─────────────────────────────────────────────────
def detect_date_column(df: pd.DataFrame):
    for col in df.columns:
        if col in DATE_ALIASES:
            return col
    return None


def detect_amount_column(df: pd.DataFrame, file_type: str):
    aliases = AMOUNT_ALIASES.get(file_type, AMOUNT_ALIASES["custom"])
    for col in df.columns:
        if col in aliases:
            return col
    return None


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


# ── Main service function ─────────────────────────────────────────────
def save_uploaded_file(
    db       : Session,
    file     : UploadFile,
    file_type: str,
    user_id  : int
) -> UploadedFile:
    """
    Full pipeline:
    1. Parse the uploaded file into a DataFrame
    2. Create uploaded_files record in DB
    3. Save every row into raw_data_rows
    4. Return the UploadedFile record
    """

    # Step 1 — parse
    df, file_format = parse_uploaded_file(file)

    # Step 2 — detect key columns
    date_col_name   = detect_date_column(df)
    amount_col_name = detect_amount_column(df, file_type)

    # Step 3 — create uploaded_files record
    uploaded_file = UploadedFile(
        user_id          = user_id,
        original_filename= file.filename,
        file_format      = file_format,
        file_type        = file_type,
        row_count        = len(df),
        column_count     = len(df.columns),
        status           = FileStatus.raw,
    )
    db.add(uploaded_file)
    db.flush()      # get auto-generated ID before inserting rows

    # Step 4 — save every row to raw_data_rows
    raw_rows = []

    for idx, row in df.iterrows():

        # Build clean JSON-serializable dict for this row
        raw_dict = {}
        for col, val in row.items():
            if pd.isna(val):
                raw_dict[col] = None
            elif isinstance(val, (int, float)):
                raw_dict[col] = val
            else:
                raw_dict[col] = str(val)

        # Extract date and amount separately for fast ML queries
        date_value = (
            parse_date_safe(row[date_col_name])
            if date_col_name else None
        )
        amount_value = (
            parse_numeric_safe(row[amount_col_name])
            if amount_col_name else None
        )

        raw_rows.append(RawDataRow(
            file_id   = uploaded_file.id,
            row_index = int(idx),
            raw_data  = raw_dict,
            date_col  = date_value,
            amount_col= amount_value,
        ))

    # Bulk insert — much faster than adding one by one
    db.bulk_save_objects(raw_rows)
    db.commit()
    db.refresh(uploaded_file)

    return uploaded_file