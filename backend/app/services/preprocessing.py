import pandas as pd
import numpy as np


def clean_data(df: pd.DataFrame):
    """
    Full preprocessing pipeline
    """

    report = {}

    # =========================
    # 1. Missing Values
    # =========================
    missing_before = df.isnull().sum().to_dict()

    # Fill numeric missing values with median
    numeric_cols = df.select_dtypes(include=np.number).columns
    for col in numeric_cols:
        df[col] = df[col].fillna(df[col].median())

    # Fill categorical missing values with mode
    categorical_cols = df.select_dtypes(exclude=np.number).columns
    for col in categorical_cols:
        if not df[col].mode().empty:
            df[col] = df[col].fillna(df[col].mode()[0])

    missing_after = df.isnull().sum().to_dict()

    report["missing_values_before"] = missing_before
    report["missing_values_after"] = missing_after

    # =========================
    # 2. Duplicate Removal
    # =========================
    duplicates_before = df.duplicated().sum()
    df = df.drop_duplicates()
    duplicates_after = df.duplicated().sum()

    report["duplicates_removed"] = int(duplicates_before)
    report["duplicates_remaining"] = int(duplicates_after)

    # =========================
    # 3. Outlier Detection (IQR)
    # =========================
    outlier_report = {}

    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        outliers = df[
            (df[col] < lower_bound) |
            (df[col] > upper_bound)
        ]

        outlier_report[col] = len(outliers)

    report["outliers_detected"] = outlier_report

    # =========================
    # 4. Date Normalization
    # =========================
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    report["final_rows"] = len(df)
    report["final_columns"] = len(df.columns)

    return df, report