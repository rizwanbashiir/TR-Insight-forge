import pandas as pd
from typing import List, Dict, Optional

# Standardized, lowercase aliases for detecting column types
DATE_ALIASES = [
    "date", "order_date", "transaction_date", "invoice_date",
    "sale_date", "expense_date", "period", "month", "day",
    "timestamp", "created_at", "cpi", "temperature"
]

AMOUNT_ALIASES = [
    "amount", "revenue", "sales", "total_sales", "sales_amount",
    "total", "total_revenue", "price", "net_sales", "weekly_sales",
    "expense", "cost", "expense_amount", "spend", "expenditure",
    "income", "income_amount", "earnings", "gross_income", "value",
    "monetary", "quantity", "qty", "stock", "units", "quantity_on_hand"
]

ENTITY_ALIASES = [
    "customer_id", "client_id", "user_id", "customer", "client", "buyer_id",
    "store", "store_id", "branch", "entity_id", "account_id"
]

ORDER_ALIASES = [
    "order_id", "invoice_id", "transaction_id", "order_no", "receipt_id", "id"
]

def find_matching_column(df_columns: List[str], candidates: List[str]) -> Optional[str]:
    """
    Finds the first matching column from the candidates list.
    Tries exact matches first, then partial substring matches.
    """
    # Exact match first
    for candidate in candidates:
        if candidate in df_columns:
            return candidate
            
    # Partial match
    for candidate in candidates:
        for col in df_columns:
            if candidate in col:
                return col
                
    return None

def detect_key_columns(df: pd.DataFrame) -> Dict[str, Optional[str]]:
    """
    Analyzes DataFrame columns and attempts to find mapping for 
    date, amount, customer/entity, and order columns.
    Assumes df.columns have already been normalized (lowercased, spaces to underscores).
    """
    # Ensure columns are treated as lowercase strings for detection
    columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    
    return {
        "date": find_matching_column(columns, DATE_ALIASES),
        "amount": find_matching_column(columns, AMOUNT_ALIASES),
        "customer": find_matching_column(columns, ENTITY_ALIASES),
        "order": find_matching_column(columns, ORDER_ALIASES),
    }

