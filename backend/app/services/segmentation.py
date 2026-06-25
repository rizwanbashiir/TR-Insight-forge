import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import warnings
warnings.filterwarnings("ignore")

from app.models.raw_data_row import RawDataRow
from app.models.segment_result import SegmentResult
from app.models.uploaded_file import UploadedFile
from app.utils.column_mapping import detect_key_columns


from typing import Union, List

def load_data_for_segmentation(
    db      : Session,
    file_ids: Union[int, List[int]]
) -> pd.DataFrame:
    if isinstance(file_ids, int):
        file_ids = [file_ids]

    rows = (
        db.query(RawDataRow)
        .filter(RawDataRow.file_id.in_(file_ids))
        .all()
    )

    if not rows:
        raise ValueError(f"No data found for file_ids {file_ids}")

    records = [row.raw_data for row in rows]
    df      = pd.DataFrame(records)

    # Normalize column names
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    return df


# ── Step 2: Detect required columns ──────────────────────────────────
# Using centralized detect_key_columns from app.utils.column_mapping

# ── Step 3: Compute RFM scores ────────────────────────────────────────
def compute_rfm(df: pd.DataFrame, cols: dict) -> pd.DataFrame:
    """
    Compute Recency, Frequency, Monetary per customer.
    """
    customer_col = cols["customer"]
    date_col     = cols["date"]
    amount_col   = cols["amount"]
    order_col    = cols["order"]

    # Need at minimum customer + amount
    if not customer_col or not amount_col:
        raise ValueError(
            "Could not detect customer_id or amount column. "
            f"Available columns: {list(df.columns)}"
        )

    # Clean amount column
    df[amount_col] = pd.to_numeric(
        df[amount_col].astype(str)
        .str.replace(",", "")
        .str.replace("₹", "")
        .str.replace("$", ""),
        errors="coerce"
    ).fillna(0)

    # If no date column — use frequency + monetary only
    if not date_col:
        rfm = df.groupby(customer_col).agg(
            Frequency=(amount_col, "count"),
            Monetary =(amount_col, "sum"),
        ).reset_index()
        rfm["Recency"] = 0    # no date data — set to 0
        return rfm

    # Parse dates
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df           = df.dropna(subset=[date_col])

    latest_date = df[date_col].max()

    # Compute RFM
    if order_col:
        rfm = df.groupby(customer_col).agg(
            Recency  =(date_col,   lambda x: (latest_date - x.max()).days),
            Frequency=(order_col,  "nunique"),
            Monetary =(amount_col, "sum"),
        ).reset_index()
    else:
        rfm = df.groupby(customer_col).agg(
            Recency  =(date_col,   lambda x: (latest_date - x.max()).days),
            Frequency=(amount_col, "count"),
            Monetary =(amount_col, "sum"),
        ).reset_index()

    return rfm


# ── Step 4: Cluster with K-Means ─────────────────────────────────────
def run_kmeans(rfm: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    """
    Normalize RFM features and apply K-Means with k=4.
    Returns (rfm_with_clusters, silhouette_score).
    """
    features = rfm[["Recency", "Frequency", "Monetary"]].copy()

    # Log transform to reduce skewness
    features["Recency"]   = np.log1p(features["Recency"])
    features["Frequency"] = np.log1p(features["Frequency"])
    features["Monetary"]  = np.log1p(features["Monetary"])

    # Standardize
    scaler          = StandardScaler()
    features_scaled = scaler.fit_transform(features)

    # K-Means with k=4
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    rfm["Cluster"] = kmeans.fit_predict(features_scaled)

    # Silhouette score — target >= 0.3 (realistic for business data)
    if len(rfm) > 4:
        sil_score = silhouette_score(features_scaled, rfm["Cluster"])
    else:
        sil_score = 0.0

    return rfm, round(float(sil_score), 4)


# ── Step 5: Label clusters ────────────────────────────────────────────
def label_segments(rfm: pd.DataFrame) -> list[dict]:
    """
    Map cluster numbers to meaningful business segment names.
    Logic based on RFM centroid characteristics:
    - High Monetary + Low Recency  → Retention (best customers)
    - High Monetary + High Recency → Win-back   (lapsed big spenders)
    - Low Monetary  + Low Recency  → Upsell     (recent but small)
    - Low Monetary  + High Recency → Nurture    (inactive small spenders)
    """
    cluster_stats = rfm.groupby("Cluster").agg(
        avg_recency  =("Recency",   "mean"),
        avg_frequency=("Frequency", "mean"),
        avg_monetary =("Monetary",  "mean"),
        customer_count=("Cluster",  "count"),
    ).reset_index()

    total_customers = len(rfm)
    total_revenue   = rfm["Monetary"].sum()

    # Score each cluster — lower recency is better
    cluster_stats["rfm_score"] = (
        (1 / (cluster_stats["avg_recency"] + 1)) *
        cluster_stats["avg_frequency"] *
        cluster_stats["avg_monetary"]
    )

    # Rank clusters by score
    cluster_stats = cluster_stats.sort_values("rfm_score", ascending=False)
    cluster_stats["rank"] = range(len(cluster_stats))

    segment_labels = {
        0: {
            "label"   : "Retention",
            "strategy": "Loyalty rewards, early access to new products, VIP treatment",
            "color"   : "#2ECC71",
        },
        1: {
            "label"   : "Upsell",
            "strategy": "Premium product recommendations, bundle offers, upgrade campaigns",
            "color"   : "#3498DB",
        },
        2: {
            "label"   : "Win-back",
            "strategy": "Re-engagement campaigns, special discounts, win-back emails",
            "color"   : "#E67E22",
        },
        3: {
            "label"   : "Nurture",
            "strategy": "Educational content, entry-level offers, build engagement",
            "color"   : "#9B59B6",
        },
    }

    segments = []
    for _, row in cluster_stats.iterrows():
        rank  = int(row["rank"])
        label = segment_labels[rank]

        cust_pct = round(row["customer_count"] / total_customers * 100, 1)
        rev_pct  = round(
            rfm[rfm["Cluster"] == row["Cluster"]]["Monetary"].sum()
            / total_revenue * 100, 1
        ) if total_revenue > 0 else 0

        segments.append({
            "cluster_id"    : int(row["Cluster"]),
            "label"         : label["label"],
            "color"         : label["color"],
            "customer_count": int(row["customer_count"]),
            "customer_pct"  : cust_pct,
            "revenue_pct"   : rev_pct,
            "avg_recency"   : round(float(row["avg_recency"]), 1),
            "avg_frequency" : round(float(row["avg_frequency"]), 1),
            "avg_monetary"  : round(float(row["avg_monetary"]), 2),
            "strategy"      : label["strategy"],
        })

    return segments


def run_fallback_segmentation(rfm: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    """
    Fallback customer segmentation for small datasets (< 4 customers).
    Assigns segments based on simple heuristics instead of K-Means.
    """
    rfm = rfm.copy()

    # Simple heuristics to classify 1-3 customers
    # Median monetary value and median recency (or defaults if only 1 customer)
    med_monetary = rfm["Monetary"].median() if len(rfm) > 1 else 0
    med_recency  = rfm["Recency"].median() if len(rfm) > 1 else 0

    clusters = []
    for _, row in rfm.iterrows():
        # Score-based assignment matching segment ranking:
        # Retention (Best): Low Recency (recent) + High Monetary
        # Upsell (Small but recent): Low Recency + Low Monetary
        # Win-back (Lapsed spender): High Recency + High Monetary
        # Nurture (Inactive small spender): High Recency + Low Monetary

        is_recent = row["Recency"] <= med_recency
        is_high_value = row["Monetary"] >= med_monetary

        if is_recent and is_high_value:
            cluster = 0  # Retention
        elif is_recent and not is_high_value:
            cluster = 1  # Upsell
        elif not is_recent and is_high_value:
            cluster = 2  # Win-back
        else:
            cluster = 3  # Nurture

        clusters.append(cluster)

    rfm["Cluster"] = clusters
    return rfm, 0.0  # Silhouette score is 0.0 since clustering wasn't used


# ── Step 6: Main pipeline ─────────────────────────────────────────────
def run_segmentation_pipeline(
    db      : Session,
    file_ids: Union[int, List[int]],
) -> SegmentResult:
    """
    Full segmentation pipeline:
    1. Load data from DB
    2. Detect columns
    3. Compute RFM scores
    4. K-Means clustering
    5. Label segments
    6. Save to segment_results table
    """
    if isinstance(file_ids, int):
        file_ids = [file_ids]

    primary_file_id = file_ids[0]

    # 1. Load
    df = load_data_for_segmentation(db, file_ids)

    # 2. Detect columns
    cols = detect_key_columns(df)
    print(f"Detected columns: {cols}")

    # 3. RFM
    rfm = compute_rfm(df, cols)

    if len(rfm) == 0:
        raise ValueError("No customer data found for segmentation.")

    # 4. Cluster
    if len(rfm) < 4:
        rfm_clustered, sil_score = run_fallback_segmentation(rfm)
    else:
        rfm_clustered, sil_score = run_kmeans(rfm)

    # 5. Label
    segments = label_segments(rfm_clustered)

    # Store associated file IDs in the segment data
    for s in segments:
        s["associated_file_ids"] = file_ids

    # 6. Save per-customer RFM scores (for export)
    customer_col = cols["customer"] or "index"
    rfm_records  = rfm_clustered.rename(
        columns={customer_col: "customer_id"}
        if customer_col in rfm_clustered.columns else {}
    ).to_dict(orient="records")

    # Serialize safely
    for r in rfm_records:
        for k, v in r.items():
            if isinstance(v, (np.integer,)):
                r[k] = int(v)
            elif isinstance(v, (np.floating,)):
                r[k] = round(float(v), 4)

    # 7. Save to DB under primary file ID
    existing = db.query(SegmentResult).filter(
        SegmentResult.file_id == primary_file_id
    ).first()

    if existing:
        existing.silhouette_score = sil_score
        existing.segment_data     = segments
        existing.rfm_scores       = rfm_records[:500]  # cap at 500 for DB size
        result = existing
    else:
        result = SegmentResult(
            file_id          = primary_file_id,
            silhouette_score = sil_score,
            segment_data     = segments,
            rfm_scores       = rfm_records[:500],
        )
        db.add(result)

    db.commit()
    db.refresh(result)
    return result


def run_customer_segmentation(df: pd.DataFrame) -> dict:
    """
    Runs customer segmentation on a DataFrame and returns a dictionary
    with silhouette score, segment details, and individual RFM scores.
    """
    # 1. Normalize
    df_copy = df.copy()
    df_copy.columns = [c.strip().lower().replace(" ", "_") for c in df_copy.columns]

    # 2. Detect columns
    cols = detect_key_columns(df_copy)

    # 3. RFM
    rfm = compute_rfm(df_copy, cols)

    if len(rfm) == 0:
        raise ValueError("No customer data found for segmentation.")

    # 4. Cluster
    if len(rfm) < 4:
        rfm_clustered, sil_score = run_fallback_segmentation(rfm)
    else:
        rfm_clustered, sil_score = run_kmeans(rfm)

    # 5. Label
    segments = label_segments(rfm_clustered)

    # 6. Prepare RFM scores
    customer_col = cols["customer"] or "index"
    rfm_records  = rfm_clustered.rename(
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