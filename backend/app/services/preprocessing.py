import pandas as pd
import numpy as np
from sqlalchemy.orm import Session

from app.models.raw_data_row import RawDataRow
from app.models.uploaded_file import UploadedFile, FileStatus
from app.models.processed_dataset import ProcessedDataset


# ── Step 1: Load raw rows from DB into a DataFrame ───────────────────
def load_raw_data(db: Session, file_id: int) -> pd.DataFrame:
    """
    Read all raw_data_rows for a file from PostgreSQL
    and return as a pandas DataFrame.
    """
    rows = (
        db.query(RawDataRow)
        .filter(RawDataRow.file_id == file_id)
        .order_by(RawDataRow.row_index)
        .all()
    )

    if not rows:
        raise ValueError(f"No raw data found for file_id {file_id}")

    # Each row.raw_data is a dict — build DataFrame from list of dicts
    records = [row.raw_data for row in rows]
    df = pd.DataFrame(records)

    return df


# ── Step 2: Clean the DataFrame ──────────────────────────────────────
def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Full preprocessing pipeline.
    Returns (cleaned_df, quality_report).
    """
    report = {}

    # ── Missing values ──
    missing_before = df.isnull().sum().to_dict()
    missing_before = {k: int(v) for k, v in missing_before.items() if v > 0}

    numeric_cols     = df.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = df.select_dtypes(exclude=np.number).columns.tolist()

    for col in numeric_cols:
        df[col] = df[col].fillna(df[col].median())

    for col in categorical_cols:
        if not df[col].mode().empty:
            df[col] = df[col].fillna(df[col].mode()[0])

    missing_after = {
        k: int(v)
        for k, v in df.isnull().sum().to_dict().items()
        if v > 0
    }

    report["missing_values_before"] = missing_before
    report["missing_values_after"]  = missing_after

    # ── Duplicates ──
    duplicates_removed = int(df.duplicated().sum())
    df = df.drop_duplicates()
    report["duplicates_removed"] = duplicates_removed

    # ── Outlier detection (IQR method) ──
    outlier_report = {}
    for col in numeric_cols:
        Q1  = df[col].quantile(0.25)
        Q3  = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        count = int(((df[col] < lower) | (df[col] > upper)).sum())
        if count > 0:
            outlier_report[col] = count

    report["outliers_detected"] = outlier_report

    # ── Date normalization ──
    for col in df.columns:
        if "date" in col.lower():
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # ── Column type inference ──
    col_types = {}
    for col in df.columns:
        dtype = str(df[col].dtype)
        if "datetime" in dtype:
            col_types[col] = "date"
        elif "float" in dtype or "int" in dtype:
            col_types[col] = "numeric"
        else:
            col_types[col] = "string"

    report["column_types"]  = col_types
    report["final_rows"]    = len(df)
    report["final_columns"] = len(df.columns)

    return df, report


# ── Step 3: Compute KPIs ─────────────────────────────────────────────
def compute_kpis(df: pd.DataFrame, file_type: str) -> dict:
    """
    Compute KPIs based on what columns are available.
    Uses smart fuzzy matching so any column containing
    'sales', 'revenue', 'amount' etc. gets detected.
    """
    kpis = {}

    # ── Smart column finder ──────────────────────────────────────────
    def find_col(df, keywords):
        """
        Find a column whose name contains any of the keywords.
        Checks exact match first, then partial match.
        """
        cols = df.columns.tolist()

        # Exact match first
        for kw in keywords:
            if kw in cols:
                return kw

        # Partial match — e.g. "weekly_sales" contains "sales"
        for kw in keywords:
            for col in cols:
                if kw in col.lower():
                    return col

        return None

    # ── Amount / revenue column ──
    amount_col = find_col(df, [
        "revenue", "sales", "amount", "income",
        "expense", "cost", "total", "price", "value"
    ])

    if amount_col:
        kpis["total_amount"]       = round(float(df[amount_col].sum()), 2)
        kpis["average_amount"]     = round(float(df[amount_col].mean()), 2)
        kpis["max_amount"]         = round(float(df[amount_col].max()), 2)
        kpis["min_amount"]         = round(float(df[amount_col].min()), 2)
        kpis["amount_column_used"] = amount_col

    # ── Profit column ──
    profit_col = find_col(df, ["profit", "margin", "net", "gross"])
    if profit_col and profit_col != amount_col:
        kpis["total_profit"]      = round(float(df[profit_col].sum()), 2)
        kpis["profit_column_used"] = profit_col

    # ── Order count ──
    order_col = find_col(df, ["order_id", "invoice", "transaction", "order"])
    if order_col:
        kpis["total_orders"] = int(df[order_col].nunique())

    # ── Customer count ──
    customer_col = find_col(df, ["customer", "client", "user", "buyer"])
    if customer_col:
        kpis["unique_customers"] = int(df[customer_col].nunique())

    # ── Store / branch count ──
    store_col = find_col(df, ["store", "branch", "location", "region", "shop"])
    if store_col:
        kpis["unique_stores"] = int(df[store_col].nunique())

    # ── Top category ──
    category_col = find_col(df, [
        "category", "segment", "department",
        "type", "product", "group"
    ])
    if category_col:
        mode_val = df[category_col].mode()
        if not mode_val.empty:
            kpis["top_category"]      = str(mode_val[0])
            kpis["category_col_used"] = category_col

    # ── Date column ──
    date_col = find_col(df, [
        "date", "order_date", "transaction_date",
        "invoice_date", "sale_date", "period", "month"
    ])

    # ── Monthly trend ──
    if date_col and amount_col:
        try:
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
            monthly = (
                df.groupby(df[date_col].dt.to_period("M"))[amount_col]
                .sum()
                .reset_index()
            )
            monthly[date_col] = monthly[date_col].astype(str)
            kpis["monthly_trend"] = monthly.rename(
                columns={date_col: "month", amount_col: "value"}
            ).to_dict(orient="records")
        except Exception as e:
            kpis["monthly_trend_error"] = str(e)

    # ── Extra numeric summaries ──
    # For any numeric column not already captured, add basic stats
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    extra_stats  = {}
    already_used = {amount_col, profit_col, order_col, store_col}

    for col in numeric_cols:
        if col not in already_used and col is not None:
            extra_stats[col] = {
                "mean" : round(float(df[col].mean()), 4),
                "min"  : round(float(df[col].min()), 4),
                "max"  : round(float(df[col].max()), 4),
            }

    if extra_stats:
        kpis["additional_metrics"] = extra_stats

    kpis["total_rows"] = len(df)
    kpis["file_type"]  = file_type

    return kpis

# ── Step 4: Main pipeline — called from the route ────────────────────
def run_preprocessing_pipeline(
    db     : Session,
    file_id: int
) -> ProcessedDataset:
    """
    Full pipeline:
    1. Load raw rows from DB
    2. Clean the data
    3. Compute KPIs
    4. Save processed_dataset record
    5. Update file status to 'processed'
    """

    # Mark file as processing
    file_record = db.query(UploadedFile).filter(
        UploadedFile.id == file_id
    ).first()

    if not file_record:
        raise ValueError(f"File {file_id} not found")

    file_record.status = FileStatus.processing
    db.commit()

    try:
        # 1. Load
        df = load_raw_data(db, file_id)

        # 2. Clean
        cleaned_df, quality_report = clean_data(df)

        # 3. KPIs
        kpi_summary = compute_kpis(cleaned_df, file_record.file_type)

        # 4. Save processed result
        existing = db.query(ProcessedDataset).filter(
            ProcessedDataset.file_id == file_id
        ).first()

        if existing:
            # Update if already exists
            existing.total_rows        = quality_report["final_rows"]
            existing.valid_rows        = quality_report["final_rows"]
            existing.duplicate_count   = quality_report["duplicates_removed"]
            existing.missing_values    = quality_report["missing_values_before"]
            existing.outliers_detected = quality_report["outliers_detected"]
            existing.column_types      = quality_report["column_types"]
            existing.kpi_summary       = kpi_summary
            processed = existing
        else:
            processed = ProcessedDataset(
                file_id           = file_id,
                total_rows        = quality_report["final_rows"],
                valid_rows        = quality_report["final_rows"],
                duplicate_count   = quality_report["duplicates_removed"],
                missing_values    = quality_report["missing_values_before"],
                outliers_detected = quality_report["outliers_detected"],
                column_types      = quality_report["column_types"],
                kpi_summary       = kpi_summary,
            )
            db.add(processed)

        # 5. Update file status
        file_record.status = FileStatus.processed
        db.commit()
        db.refresh(processed)

        return processed

    except Exception as e:
        # Mark as failed if anything goes wrong
        file_record.status        = FileStatus.failed
        file_record.error_message = str(e)
        db.commit()
        raise