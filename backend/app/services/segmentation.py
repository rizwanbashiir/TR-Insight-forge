import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import warnings
warnings.filterwarnings("ignore")
from beanie import PydanticObjectId
from typing import Union, List

from app.models.raw_data_row import RawDataRow
from app.models.segment_result import SegmentResult
from app.models.uploaded_file import UploadedFile
from app.utils.column_mapping import detect_key_columns


async def load_data_for_segmentation(
    db,
    file_ids: Union[str, List[str]]
) -> pd.DataFrame:
    if isinstance(file_ids, (str, PydanticObjectId)):
        file_ids = [file_ids]

    oids = [PydanticObjectId(fid) if isinstance(fid, str) else fid for fid in file_ids]

    rows = await RawDataRow.find({"file_id": {"$in": oids}}).to_list()

    if not rows:
        raise ValueError(f"No data found for file_ids {file_ids}")

    records = [row.raw_data for row in rows]
    df = pd.DataFrame(records)

    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    return df


def compute_rfm(df: pd.DataFrame, cols: dict) -> pd.DataFrame:
    customer_col = cols["customer"]
    date_col = cols["date"]
    amount_col = cols["amount"]
    order_col = cols["order"]

    if not customer_col or not amount_col:
        raise ValueError(
            "Could not detect customer_id or amount column. "
            f"Available columns: {list(df.columns)}"
        )

    df[amount_col] = pd.to_numeric(
        df[amount_col].astype(str)
        .str.replace(",", "")
        .str.replace("₹", "")
        .str.replace("$", ""),
        errors="coerce"
    ).fillna(0)

    if not date_col:
        rfm = df.groupby(customer_col).agg(
            Frequency=(amount_col, "count"),
            Monetary=(amount_col, "sum"),
        ).reset_index()
        rfm["Recency"] = 0
        return rfm

    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=[date_col])

    latest_date = df[date_col].max()

    if order_col:
        rfm = df.groupby(customer_col).agg(
            Recency=(date_col, lambda x: (latest_date - x.max()).days),
            Frequency=(order_col, "nunique"),
            Monetary=(amount_col, "sum"),
        ).reset_index()
    else:
        rfm = df.groupby(customer_col).agg(
            Recency=(date_col, lambda x: (latest_date - x.max()).days),
            Frequency=(amount_col, "count"),
            Monetary=(amount_col, "sum"),
        ).reset_index()

    return rfm


def run_kmeans(rfm: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    features = rfm[["Recency", "Frequency", "Monetary"]].copy()

    features["Recency"] = np.log1p(features["Recency"])
    features["Frequency"] = np.log1p(features["Frequency"])
    features["Monetary"] = np.log1p(features["Monetary"])

    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)

    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    rfm["Cluster"] = kmeans.fit_predict(features_scaled)

    if len(rfm) > 4:
        sil_score = silhouette_score(features_scaled, rfm["Cluster"])
    else:
        sil_score = 0.0

    return rfm, round(float(sil_score), 4)


def label_segments(rfm: pd.DataFrame) -> list[dict]:
    cluster_stats = rfm.groupby("Cluster").agg(
        avg_recency=("Recency", "mean"),
        avg_frequency=("Frequency", "mean"),
        avg_monetary=("Monetary", "mean"),
        customer_count=("Cluster", "count"),
    ).reset_index()

    total_customers = len(rfm)
    total_revenue = rfm["Monetary"].sum()

    cluster_stats["rfm_score"] = (
        (1 / (cluster_stats["avg_recency"] + 1)) *
        cluster_stats["avg_frequency"] *
        cluster_stats["avg_monetary"]
    )

    cluster_stats = cluster_stats.sort_values("rfm_score", ascending=False)
    cluster_stats["rank"] = range(len(cluster_stats))

    segment_labels = {
        0: {
            "label": "Champions",
            "strategy": "Reward loyalty · upsell premium",
            "color": "#2ECC71",
        },
        1: {
            "label": "Loyal",
            "strategy": "Cross-sell · gather reviews",
            "color": "#3498DB",
        },
        2: {
            "label": "At Risk",
            "strategy": "Trigger win-back campaign",
            "color": "#E74C3C",
        },
        3: {
            "label": "Needs Attention",
            "strategy": "Re-engage with offer",
            "color": "#F39C12",
        },
    }

    segments = []
    for _, row in cluster_stats.iterrows():
        rank = int(row["rank"])
        label = segment_labels[rank]

        cust_pct = round(row["customer_count"] / total_customers * 100, 1)
        rev_pct = round(
            rfm[rfm["Cluster"] == row["Cluster"]]["Monetary"].sum()
            / total_revenue * 100, 1
        ) if total_revenue > 0 else 0

        segments.append({
            "cluster_id": int(row["Cluster"]),
            "label": label["label"],
            "color": label["color"],
            "customer_count": int(row["customer_count"]),
            "customer_pct": cust_pct,
            "revenue_pct": rev_pct,
            "avg_recency": round(float(row["avg_recency"]), 1),
            "avg_frequency": round(float(row["avg_frequency"]), 1),
            "avg_monetary": round(float(row["avg_monetary"]), 2),
            "strategy": label["strategy"],
        })

    return segments


def run_fallback_segmentation(rfm: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    rfm = rfm.copy()

    med_monetary = rfm["Monetary"].median() if len(rfm) > 1 else 0
    med_recency = rfm["Recency"].median() if len(rfm) > 1 else 0

    clusters = []
    for _, row in rfm.iterrows():
        is_recent = row["Recency"] <= med_recency
        is_high_value = row["Monetary"] >= med_monetary

        if is_recent and is_high_value:
            cluster = 0
        elif is_recent and not is_high_value:
            cluster = 1
        elif not is_recent and is_high_value:
            cluster = 2
        else:
            cluster = 3

        clusters.append(cluster)

    rfm["Cluster"] = clusters
    return rfm, 0.0


async def run_segmentation_pipeline(
    db,
    file_ids: Union[str, List[str]],
) -> SegmentResult:
    if isinstance(file_ids, (str, PydanticObjectId)):
        file_ids = [file_ids]

    primary_file_id = file_ids[0]
    primary_oid = PydanticObjectId(primary_file_id) if isinstance(primary_file_id, str) else primary_file_id

    df = await load_data_for_segmentation(db, file_ids)

    cols = detect_key_columns(df)

    rfm = compute_rfm(df, cols)

    if len(rfm) == 0:
        raise ValueError("No customer data found for segmentation.")

    if len(rfm) < 4:
        rfm_clustered, sil_score = run_fallback_segmentation(rfm)
    else:
        rfm_clustered, sil_score = run_kmeans(rfm)

    segments = label_segments(rfm_clustered)

    for s in segments:
        s["associated_file_ids"] = [str(f) for f in file_ids]

    customer_col = cols["customer"] or "index"
    rfm_records = rfm_clustered.rename(
        columns={customer_col: "customer_id"}
        if customer_col in rfm_clustered.columns else {}
    ).to_dict(orient="records")

    for r in rfm_records:
        for k, v in r.items():
            if isinstance(v, (np.integer,)):
                r[k] = int(v)
            elif isinstance(v, (np.floating,)):
                r[k] = round(float(v), 4)

    existing = await SegmentResult.find_one(
        SegmentResult.file_id == primary_oid
    )

    if existing:
        existing.silhouette_score = sil_score
        existing.segment_data = segments
        existing.rfm_scores = rfm_records[:500]
        result = existing
        await result.save()
    else:
        result = SegmentResult(
            file_id=primary_oid,
            silhouette_score=sil_score,
            segment_data=segments,
            rfm_scores=rfm_records[:500],
        )
        await result.insert()

    return result


def run_customer_segmentation(df: pd.DataFrame) -> dict:
    df_copy = df.copy()
    df_copy.columns = [c.strip().lower().replace(" ", "_") for c in df_copy.columns]

    cols = detect_key_columns(df_copy)

    rfm = compute_rfm(df_copy, cols)

    if len(rfm) == 0:
        raise ValueError("No customer data found for segmentation.")

    if len(rfm) < 4:
        rfm_clustered, sil_score = run_fallback_segmentation(rfm)
    else:
        rfm_clustered, sil_score = run_kmeans(rfm)

    segments = label_segments(rfm_clustered)

    customer_col = cols["customer"] or "index"
    rfm_records = rfm_clustered.rename(
        columns={customer_col: "customer_id"}
        if customer_col in rfm_clustered.columns else {}
    ).to_dict(orient="records")

    for r in rfm_records:
        for k, v in r.items():
            if isinstance(v, (np.integer,)):
                r[k] = int(v)
            elif isinstance(v, (np.floating,)):
                r[k] = round(float(v), 4)

    return {
        "silhouette_score": sil_score,
        "segments": segments,
        "rfm_scores": rfm_records[:500]
    }