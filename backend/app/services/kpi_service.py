import pandas as pd


def generate_kpis(df: pd.DataFrame):
    """
    Generate dashboard KPIs
    """

    total_revenue = df["total_sales"].sum()
    total_orders = df["order_id"].nunique()
    unique_customers = df["customer_id"].nunique()
    average_order_value = round(total_revenue / total_orders, 2)

    top_category = (
        df["product_category"]
        .value_counts()
        .idxmax()
    )

    return {
        "total_revenue": float(total_revenue),
        "total_orders": int(total_orders),
        "unique_customers": int(unique_customers),
        "average_order_value": float(average_order_value),
        "top_category": top_category
    }