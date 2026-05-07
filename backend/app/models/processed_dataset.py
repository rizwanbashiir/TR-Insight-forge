from sqlalchemy import Column, Integer, ForeignKey, DateTime, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base

class ProcessedDataset(Base):
    __tablename__ = "processed_datasets"

    id                = Column(Integer, primary_key=True, index=True)
    file_id           = Column(Integer, ForeignKey("uploaded_files.id", ondelete="CASCADE"), unique=True)
    total_rows        = Column(Integer)
    valid_rows        = Column(Integer)
    duplicate_count   = Column(Integer)
    missing_values    = Column(JSONB)
    outliers_detected = Column(JSONB)
    column_types      = Column(JSONB)
    kpi_summary       = Column(JSONB)
    processed_at      = Column(DateTime(timezone=True), server_default=func.now())

    file              = relationship("UploadedFile", back_populates="processed_dataset")