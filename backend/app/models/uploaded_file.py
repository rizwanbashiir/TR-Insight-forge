from beanie import Document, PydanticObjectId
from pydantic import Field
from typing import Optional
from datetime import datetime, timezone
import enum

class FileType(str, enum.Enum):
    sales     = "sales"
    expenses  = "expenses"
    income    = "income"
    inventory = "inventory"
    custom    = "custom"

class FileStatus(str, enum.Enum):
    raw        = "raw"
    processing = "processing"
    processed  = "processed"
    failed     = "failed"

class UploadedFile(Document):
    user_id: PydanticObjectId
    organization_id: Optional[PydanticObjectId] = None
    original_filename: str
    file_format: Optional[str] = None
    file_type: FileType
    row_count: Optional[int] = None
    column_count: Optional[int] = None
    status: FileStatus = FileStatus.raw
    error_message: Optional[str] = None
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "uploaded_files"
