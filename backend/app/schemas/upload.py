from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from typing import Optional

class FileType(str, Enum):
    sales     = "sales"
    expenses  = "expenses"
    income    = "income"
    inventory = "inventory"
    custom    = "custom"

class FileStatus(str, Enum):
    raw        = "raw"
    processing = "processing"
    processed  = "processed"
    failed     = "failed"

# What we return after a successful upload
class UploadResponse(BaseModel):
    file_id          : int
    original_filename: str
    file_type        : FileType
    file_format      : str
    row_count        : int
    column_count     : int
    columns_detected : list[str]
    status           : FileStatus
    uploaded_at      : datetime
    message          : str

    class Config:
        from_attributes = True