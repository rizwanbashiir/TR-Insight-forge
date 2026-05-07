from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base

class ForecastResult(Base):
    __tablename__ = "forecast_results"

    id            = Column(Integer, primary_key=True, index=True)
    file_id       = Column(Integer, ForeignKey("uploaded_files.id", ondelete="CASCADE"), unique=True)
    model_name    = Column(String(50), default="ARIMA")
    arima_order   = Column(String(20))
    mape_score    = Column(Numeric)
    forecast_data = Column(JSONB)
    generated_at  = Column(DateTime(timezone=True), server_default=func.now())

    file          = relationship("UploadedFile", back_populates="forecast_result")