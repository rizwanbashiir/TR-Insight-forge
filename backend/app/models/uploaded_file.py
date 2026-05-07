from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.config.database import Base

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

class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id                = Column(Integer, primary_key=True, index=True)
    user_id           = Column(Integer, ForeignKey("users.id"), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_format       = Column(String(10))
    file_type         = Column(Enum(FileType), nullable=False)
    row_count         = Column(Integer)
    column_count      = Column(Integer)
    status            = Column(Enum(FileStatus), default=FileStatus.raw)
    error_message     = Column(Text)
    uploaded_at       = Column(DateTime(timezone=True), server_default=func.now())

    raw_rows          = relationship("RawDataRow", back_populates="file", cascade="all, delete")
    processed_dataset = relationship("ProcessedDataset", back_populates="file", uselist=False)
    forecast_result   = relationship("ForecastResult", back_populates="file", uselist=False)
    segment_result    = relationship("SegmentResult", back_populates="file", uselist=False)
    ai_insight        = relationship("AiInsight", back_populates="file", uselist=False)
