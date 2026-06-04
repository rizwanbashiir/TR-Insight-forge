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


# ── Step 1: Load data from DB into DataFrame ─────────────────────────
def load_data_for_segmentation(
    db     : Session,
    file_id: int
) -> pd.DataFrame:
    """
    Load raw_data_rows and convert to DataFrame.
    We use the full raw_data JSONB for RFM computation.
    """
    rows = (
        db.query(RawDataRow)
        .filter(RawDataRow.file_id == file_id)
        .all()
    )

    if not rows:
        raise ValueError(f"No data found for file_id {file_id}")

    records = [row.raw_data for row in rows]
    df      = pd.DataFrame(records)

    # Normalize column names
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    return df


# ── Step 2: Detect required columns ──────────────────────────────────
def detect_columns(df: pd.DataFrame) -> dict:
    """
    Auto-detect customer, date, and amount columns.
    Returns dict with detected column names.
    """
    customer_candidates = [
        "customer_id", "client_id", "user_id",
        "customer", "client", "buyer_id"
    ]
    date_candidates = [
        "date", "order_date", "transaction_date",
        "invoice_date", "sale_date", "purchase_date"
    ]
    amount_candidates = [
        "revenue", "total_sales", "sales", "amount",
        "weekly_sales", "total", "price", "monetary",
        "income", "spend"
    ]
    order_candidates = [
        "order_id", "invoice_id", "transaction_id",
        "order_no", "receipt_id", "id"
    ]

    def find_col(candidates):
        # Exact match first
        for c in candidates:
            if c in df.columns:
                return c
        # Partial match
        for c in candidates:
            for col in df.columns:
                if c in col.lower():
                    return col
        return None

    return {
        "customer": find_col(customer_candidates),
        "date"    : find_col(date_candidates),
        "amount"  : find_col(amount_candidates),
        "order"   : find_col(order_candidates),
    }


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


# ── Step 6: Main pipeline ─────────────────────────────────────────────
def run_segmentation_pipeline(
    db     : Session,
    file_id: int,
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

    # 1. Load
    df = load_data_for_segmentation(db, file_id)

    # 2. Detect columns
    cols = detect_columns(df)
    print(f"Detected columns: {cols}")

    # 3. RFM
    rfm = compute_rfm(df, cols)

    if len(rfm) < 4:
        raise ValueError(
            f"Need at least 4 unique customers for segmentation. "
            f"Found {len(rfm)}."
        )

    # 4. Cluster
    rfm_clustered, sil_score = run_kmeans(rfm)

    # 5. Label
    segments = label_segments(rfm_clustered)

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

    # 7. Save to DB
    existing = db.query(SegmentResult).filter(
        SegmentResult.file_id == file_id
    ).first()

    if existing:
        existing.silhouette_score = sil_score
        existing.segment_data     = segments
        existing.rfm_scores       = rfm_records[:500]  # cap at 500 for DB size
        result = existing
    else:
        result = SegmentResult(
            file_id          = file_id,
            silhouette_score = sil_score,
            segment_data     = segments,
            rfm_scores       = rfm_records[:500],
        )
        db.add(result)

    db.commit()
    db.refresh(result)
    return result