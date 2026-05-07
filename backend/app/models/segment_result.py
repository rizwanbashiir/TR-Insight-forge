from sqlalchemy import Column, Integer, ForeignKey, DateTime, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base

class SegmentResult(Base):
    __tablename__ = "segment_results"

    id               = Column(Integer, primary_key=True, index=True)
    file_id          = Column(Integer, ForeignKey("uploaded_files.id", ondelete="CASCADE"), unique=True)
    silhouette_score = Column(Numeric)
    segment_data     = Column(JSONB)
    rfm_scores       = Column(JSONB)
    generated_at     = Column(DateTime(timezone=True), server_default=func.now())

    file             = relationship("UploadedFile", back_populates="segment_result")