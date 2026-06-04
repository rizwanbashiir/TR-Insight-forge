import sys
import os
from datetime import datetime
import pandas as pd

# Adjust path to find app module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config.database import SessionLocal, engine
from app.models.users import User
from app.models.uploaded_file import UploadedFile, FileStatus
from app.models.raw_data_row import RawDataRow
from app.models.processed_dataset import ProcessedDataset
from app.models.forecast_result import ForecastResult
from app.models.segment_result import SegmentResult
from app.models.ai_insight import AiInsight

from app.routes.upload import run_background_ingestion
from app.services.forecasting import run_arima_forecast
from app.services.segmentation import run_segmentation_pipeline

def test_pipeline():
    print("--- Starting Backend Robustness Integration Tests ---")
    db = SessionLocal()
    
    # 1. Setup a test user
    test_user = db.query(User).filter(User.email == "test_robustness@example.com").first()
    if not test_user:
        test_user = User(
            email="test_robustness@example.com",
            password="hashedpassword123",
            name="Robustness Tester",
            is_active=True,
            role="analyst"
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
    
    # 2. Setup a test file record
    test_file = UploadedFile(
        user_id=test_user.id,
        original_filename="short_test_data.csv",
        file_format="csv",
        file_type="sales",
        row_count=3,
        column_count=4,
        status=FileStatus.raw
    )
    db.add(test_file)
    db.commit()
    db.refresh(test_file)
    
    file_id = test_file.id
    print(f"Created test file with ID: {file_id}")
    
    try:
        # 3. Add 3 raw rows (short data: < 6 months, < 4 unique customers)
        raw_rows = [
            RawDataRow(
                file_id=file_id,
                row_index=0,
                raw_data={"customer_id": "cust_101", "order_date": "2026-01-15", "sales_amount": 100.0, "order_id": "1"},
                date_col=datetime(2026, 1, 15).date(),
                amount_col=100.0
            ),
            RawDataRow(
                file_id=file_id,
                row_index=1,
                raw_data={"customer_id": "cust_102", "order_date": "2026-02-20", "sales_amount": 150.0, "order_id": "2"},
                date_col=datetime(2026, 2, 20).date(),
                amount_col=150.0
            ),
            RawDataRow(
                file_id=file_id,
                row_index=2,
                raw_data={"customer_id": "cust_101", "order_date": "2026-03-25", "sales_amount": 200.0, "order_id": "3"},
                date_col=datetime(2026, 3, 25).date(),
                amount_col=200.0
            )
        ]
        db.bulk_save_objects(raw_rows)
        db.commit()
        print("Inserted 3 raw rows of short test data.")
        
        # 4. Test Ingestion Automation (run_background_ingestion)
        print("Testing automated background ingestion (preprocessing + embedding)...")
        run_background_ingestion(file_id)
        
        # Refresh records from database
        db.refresh(test_file)
        processed = db.query(ProcessedDataset).filter(ProcessedDataset.file_id == file_id).first()
        
        assert test_file.status == FileStatus.processed, f"Expected status 'processed', got {test_file.status}"
        assert processed is not None, "Processed dataset record should exist"
        assert processed.kpi_summary["total_amount"] == 450.0, f"Expected KPI total 450.0, got {processed.kpi_summary['total_amount']}"
        print("SUCCESS: Automated background ingestion ran successfully and computed correct KPIs.")
        
        # 5. Test Forecasting Fallback (should fall back to Linear Regression)
        print("Testing time-series forecasting fallback (< 6 months of data)...")
        forecast_res = run_arima_forecast(db, file_id, steps=3)
        db.refresh(forecast_res)
        
        assert "Linear Regression" in forecast_res.model_name, f"Expected fallback model name, got {forecast_res.model_name}"
        assert len(forecast_res.forecast_data["forecast"]) == 3, f"Expected 3 steps, got {len(forecast_res.forecast_data['forecast'])}"
        print(f"SUCCESS: Forecasting fallback model '{forecast_res.model_name}' ran successfully.")
        
        # 6. Test Customer Segmentation Fallback (< 4 customers)
        print("Testing customer segmentation fallback (< 4 unique customers)...")
        segment_res = run_segmentation_pipeline(db, file_id)
        db.refresh(segment_res)
        
        assert segment_res.silhouette_score == 0.0, f"Expected silhouette score 0.0, got {segment_res.silhouette_score}"
        assert len(segment_res.segment_data) > 0, "Should generate segments metadata"
        print(f"SUCCESS: Customer segmentation fallback ran successfully. Segments generated: {[s['label'] for s in segment_res.segment_data]}")
        
    except Exception as e:
        print(f"FAILED: Test encountered an exception: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # 7. Clean up database
        print("Cleaning up database test records...")
        try:
            test_file_ids = [f.id for f in db.query(UploadedFile).filter(UploadedFile.user_id == test_user.id).all()]
            if test_file_ids:
                db.query(SegmentResult).filter(SegmentResult.file_id.in_(test_file_ids)).delete(synchronize_session=False)
                db.query(ForecastResult).filter(ForecastResult.file_id.in_(test_file_ids)).delete(synchronize_session=False)
                db.query(ProcessedDataset).filter(ProcessedDataset.file_id.in_(test_file_ids)).delete(synchronize_session=False)
                db.query(RawDataRow).filter(RawDataRow.file_id.in_(test_file_ids)).delete(synchronize_session=False)
                db.query(UploadedFile).filter(UploadedFile.user_id == test_user.id).delete(synchronize_session=False)
            db.query(User).filter(User.id == test_user.id).delete()
            db.commit()
            print("Cleanup completed.")
        except Exception as cleanup_err:
            db.rollback()
            print(f"Cleanup failed: {str(cleanup_err)}")
        db.close()
        print("--- All tests finished ---")

if __name__ == "__main__":
    test_pipeline()
