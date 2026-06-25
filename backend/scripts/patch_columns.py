import os
import sys

# Add the project root to python path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

# Import ALL models so SQLAlchemy sees them before create_all
import app.models.users
import app.models.uploaded_file
import app.models.raw_data_row
import app.models.processed_dataset
import app.models.forecast_result
import app.models.segment_result
import app.models.ai_insight
import app.models.organizations
import app.models.subscriptions

from app.config.database import SessionLocal
from app.models.uploaded_file import UploadedFile
from app.models.raw_data_row import RawDataRow
from app.utils.column_mapping import detect_key_columns
from app.services.upload_service import parse_date_safe, parse_numeric_safe

def patch_database_columns():
    db = SessionLocal()
    try:
        files = db.query(UploadedFile).all()
        print(f"Found {len(files)} files to patch.")
        
        for file in files:
            # Get one row to determine the schema
            sample_row = db.query(RawDataRow).filter(RawDataRow.file_id == file.id).first()
            if not sample_row or not sample_row.raw_data:
                continue
                
            # Simulate a dataframe to use our column mapping
            df = pd.DataFrame([sample_row.raw_data])
            detected = detect_key_columns(df)
            
            date_col = detected.get("date")
            amount_col = detected.get("amount")
            
            print(f"File {file.id} ({file.original_filename}): Detected date='{date_col}', amount='{amount_col}'")
            
            if not date_col and not amount_col:
                continue
                
            # Update all rows for this file
            rows = db.query(RawDataRow).filter(RawDataRow.file_id == file.id).all()
            updates = 0
            for row in rows:
                raw = row.raw_data
                if not raw:
                    continue
                    
                # Extract new values
                if date_col and date_col in raw:
                    row.date_col = parse_date_safe(raw[date_col])
                if amount_col and amount_col in raw:
                    row.amount_col = parse_numeric_safe(raw[amount_col])
                    
                updates += 1
                
            print(f"  -> Updated {updates} rows for file {file.id}")
            db.commit()
            
        print("Patch complete!")
    except Exception as e:
        db.rollback()
        print(f"Error during patch: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    patch_database_columns()
