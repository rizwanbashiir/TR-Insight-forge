# TR-insight-forge
Implementation Plan: Automated Ingestion & Robustness Fallbacks
We will automate the ingestion pipeline (preprocessing + Pinecone embedding) immediately after file upload, and add robust fallback models for forecasting and segmentation when dataset counts are too small.

Proposed Changes
1. Ingestion Automation
We will integrate FastAPI BackgroundTasks into the file upload route. When a user uploads a CSV, Excel, or JSON spreadsheet, the system will save the raw data to PostgreSQL and immediately return a 201 Created response. In the background, it will automatically clean the data, calculate KPIs, and upsert vector embeddings to Pinecone.

[MODIFY] 
upload.py
Import BackgroundTasks from fastapi and SessionLocal from app.config.database.
Implement run_background_ingestion(file_id: int) worker function.
Update upload_file() router path to accept background_tasks: BackgroundTasks and call background_tasks.add_task(run_background_ingestion, uploaded.id).
2. Time-Series Forecasting Robustness
If a dataset contains less than 6 months of historical data, ARIMA fails. We will implement a linear regression trend-line fallback that mimics the ARIMA return format.

[MODIFY] 
forecasting.py
Add run_fallback_forecast(monthly: pd.Series, steps: int) -> dict helper function.
Update run_arima_forecast to detect if len(monthly) < 6. If so, invoke run_fallback_forecast to compute a linear regression or flat trend, and populate ForecastResult seamlessly.
3. Customer Segmentation Robustness
If a dataset contains less than 4 unique customers, K-Means clustering with $K=4$ fails. We will implement a rule-based RFM heuristic fallback.

[MODIFY] 
segmentation.py
Add run_fallback_segmentation(rfm: pd.DataFrame) -> tuple[pd.DataFrame, float] helper function.
Update run_segmentation_pipeline to detect if len(rfm) < 4. If so, call run_fallback_segmentation to assign customers to segments based on simple median thresholds and return a silhouette score of 0.0.
Verification Plan
Automated Tests
We will write a python script 
test_robustness.py
 to:

Validate that the background task runs automatically on upload.
Verify that forecasting works with < 6 months of data using the linear regression fallback.
Verify that customer segmentation works with < 4 customers using the heuristic fallback.