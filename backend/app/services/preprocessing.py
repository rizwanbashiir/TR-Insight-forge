import pandas as pd
import numpy as np
from beanie import PydanticObjectId

from app.models.raw_data_row import RawDataRow
from app.models.uploaded_file import UploadedFile, FileStatus
from app.models.processed_dataset import ProcessedDataset


async def load_raw_data(db, file_id) -> pd.DataFrame:
    oid = PydanticObjectId(file_id) if isinstance(file_id, str) else file_id
    rows = await RawDataRow.find(RawDataRow.file_id == oid).sort("row_index").to_list()

    if not rows:
        raise ValueError(f"No raw data found for file_id {file_id}")

    records = [row.raw_data for row in rows]
    df = pd.DataFrame(records)
    return df


def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    report = {}

    missing_before = df.isnull().sum().to_dict()
    missing_before = {k: int(v) for k, v in missing_before.items() if v > 0}

    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
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
    report["missing_values_after"] = missing_after

    duplicates_removed = int(df.duplicated().sum())
    df = df.drop_duplicates()
    report["duplicates_removed"] = duplicates_removed

    outlier_report = {}
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        count = int(((df[col] < lower) | (df[col] > upper)).sum())
        if count > 0:
            outlier_report[col] = count

    report["outliers_detected"] = outlier_report

    for col in df.columns:
        if "date" in col.lower():
            df[col] = pd.to_datetime(df[col], errors="coerce")

    col_types = {}
    for col in df.columns:
        dtype = str(df[col].dtype)
        if "datetime" in dtype:
            col_types[col] = "date"
        elif "float" in dtype or "int" in dtype:
            col_types[col] = "numeric"
        else:
            col_types[col] = "string"

    report["column_types"] = col_types
    report["final_rows"] = len(df)
    report["final_columns"] = len(df.columns)

    return df, report


def compute_kpis(df: pd.DataFrame, file_type: str) -> dict:
    import re

    kpis = {}

    def find_col(df, keywords):
        cols = df.columns.tolist()
        for kw in keywords:
            if kw in cols:
                return kw
        for kw in keywords:
            for col in cols:
                if kw in col.lower():
                    return col
        return None

    def clean_numeric_series(series):
        def clean_val(val):
            if pd.isna(val):
                return 0.0
            s = str(val).strip()
            if s.count("₹") > 1:
                parts = [p for p in s.split("₹") if p.strip()]
                s = parts[0] if parts else "0"
            s = re.sub(r"[₹$£€,\s]", "", s)
            match = re.search(r"[\d.]+", s)
            if match:
                try:
                    return float(match.group())
                except Exception:
                    return 0.0
            return 0.0

        return series.apply(clean_val)

    amount_col = find_col(df, [
        "revenue", "sales", "amount", "income",
        "expense", "cost", "total", "price", "value"
    ])

    if amount_col:
        clean_amt = clean_numeric_series(df[amount_col])
        kpis["total_amount"] = round(float(clean_amt.sum()), 2)
        kpis["average_amount"] = round(float(clean_amt.mean()), 2)
        kpis["max_amount"] = round(float(clean_amt.max()), 2)
        kpis["min_amount"] = round(float(clean_amt.min()), 2)
        kpis["amount_column_used"] = amount_col

    profit_col = find_col(df, ["profit", "margin", "net", "gross"])
    if profit_col and profit_col != amount_col:
        clean_profit = clean_numeric_series(df[profit_col])
        kpis["total_profit"] = round(float(clean_profit.sum()), 2)
        kpis["profit_column_used"] = profit_col

    order_col = find_col(df, ["order_id", "invoice", "transaction", "order"])
    if order_col:
        kpis["total_orders"] = int(df[order_col].nunique())

    customer_col = find_col(df, ["customer", "client", "user", "buyer"])
    if customer_col:
        kpis["unique_customers"] = int(df[customer_col].nunique())

    store_col = find_col(df, ["store", "branch", "location", "region", "shop"])
    if store_col:
        kpis["unique_stores"] = int(df[store_col].nunique())

    category_col = find_col(df, ["category", "segment", "department", "type", "product"])
    if category_col:
        mode_val = df[category_col].mode()
        if not mode_val.empty:
            kpis["top_category"] = str(mode_val[0])
            kpis["category_col_used"] = category_col

    date_col = find_col(df, [
        "date", "order_date", "transaction_date",
        "invoice_date", "sale_date", "period", "month"
    ])

    if date_col and amount_col:
        try:
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
            temp = df[[date_col, amount_col]].copy()
            temp[amount_col] = clean_numeric_series(temp[amount_col])
            monthly = (
                temp.groupby(temp[date_col].dt.to_period("M"))[amount_col]
                .sum()
                .reset_index()
            )
            monthly[date_col] = monthly[date_col].astype(str)
            kpis["monthly_trend"] = monthly.rename(
                columns={date_col: "month", amount_col: "value"}
            ).to_dict(orient="records")
        except Exception as e:
            kpis["monthly_trend_error"] = str(e)

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    already_used = {amount_col, profit_col, order_col, store_col}
    extra_stats = {}

    for col in numeric_cols:
        if col not in already_used and col is not None:
            try:
                extra_stats[col] = {
                    "mean": round(float(df[col].mean()), 4),
                    "min": round(float(df[col].min()), 4),
                    "max": round(float(df[col].max()), 4),
                }
            except Exception:
                pass

    if extra_stats:
        kpis["additional_metrics"] = extra_stats

    kpis["total_rows"] = len(df)
    kpis["file_type"] = str(file_type)

    return kpis


async def run_preprocessing_pipeline(
    db,
    file_id
) -> ProcessedDataset:
    oid = PydanticObjectId(file_id) if isinstance(file_id, str) else file_id

    file_record = await UploadedFile.get(oid)
    if not file_record:
        raise ValueError(f"File {file_id} not found")

    file_record.status = FileStatus.processing
    await file_record.save()

    try:
        df = await load_raw_data(db, oid)

        cleaned_df, quality_report = clean_data(df)

        kpi_summary = compute_kpis(cleaned_df, file_record.file_type)

        existing = await ProcessedDataset.find_one(ProcessedDataset.file_id == oid)

        if existing:
            existing.total_rows = quality_report["final_rows"]
            existing.valid_rows = quality_report["final_rows"]
            existing.duplicate_count = quality_report["duplicates_removed"]
            existing.missing_values = quality_report["missing_values_before"]
            existing.outliers_detected = quality_report["outliers_detected"]
            existing.column_types = quality_report["column_types"]
            existing.kpi_summary = kpi_summary
            processed = existing
            await processed.save()
        else:
            processed = ProcessedDataset(
                file_id=oid,
                total_rows=quality_report["final_rows"],
                valid_rows=quality_report["final_rows"],
                duplicate_count=quality_report["duplicates_removed"],
                missing_values=quality_report["missing_values_before"],
                outliers_detected=quality_report["outliers_detected"],
                column_types=quality_report["column_types"],
                kpi_summary=kpi_summary,
            )
            await processed.insert()

        file_record.status = FileStatus.processed
        await file_record.save()

        return processed

    except Exception as e:
        file_record.status = FileStatus.failed
        file_record.error_message = str(e)
        await file_record.save()
        raise