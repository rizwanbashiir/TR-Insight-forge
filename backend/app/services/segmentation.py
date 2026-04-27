import pandas as pd
from sklearn.cluster import KMeans


def run_customer_segmentation(df: pd.DataFrame):
    """
    RFM + KMeans Customer Segmentation
    """

    # Convert date
    df["date"] = pd.to_datetime(df["date"])

    # Latest date reference
    latest_date = df["date"].max()

    # RFM Calculation
    rfm = df.groupby("customer_id").agg({
        "date": lambda x: (latest_date - x.max()).days,   # Recency
        "order_id": "count",                              # Frequency
        "total_sales": "sum"                              # Monetary
    })

    rfm.columns = ["Recency", "Frequency", "Monetary"]

    # KMeans Clustering
    kmeans = KMeans(
        n_clusters=4,
        random_state=42,
        n_init=10
    )

    rfm["Cluster"] = kmeans.fit_predict(
        rfm[["Recency", "Frequency", "Monetary"]]
    )

    return {
        "customer_segments": rfm.reset_index().to_dict(orient="records")
    }