from beanie import Document, PydanticObjectId
from typing import Optional, Dict, Any
from datetime import date

class RawDataRow(Document):
    file_id: PydanticObjectId
    row_index: int
    raw_data: Dict[str, Any]
    date_col: Optional[date] = None
    amount_col: Optional[float] = None

    class Settings:
        name = "raw_data_rows"
        indexes = [
            "file_id",
            [("file_id", 1), ("row_index", 1)],
            [("file_id", 1), ("date_col", 1)],
        ]