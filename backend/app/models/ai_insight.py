from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base

class AiInsight(Base):
    __tablename__ = "ai_insights"

    id           = Column(Integer, primary_key=True, index=True)
    file_id      = Column(Integer, ForeignKey("uploaded_files.id", ondelete="CASCADE"), unique=True)
    model_name   = Column(String(100))
    prompt_used  = Column(Text)
    ai_response  = Column(Text)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

    file         = relationship("UploadedFile", back_populates="ai_insight")