from sqlalchemy import Column, Integer, ForeignKey, Date, Numeric, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.config.database import Base

class RawDataRow(Base):
    __tablename__ = "raw_data_rows"

    id         = Column(Integer, primary_key=True, index=True)
    file_id    = Column(Integer, ForeignKey("uploaded_files.id", ondelete="CASCADE"), nullable=False)
    row_index  = Column(Integer, nullable=False)
    raw_data   = Column(JSONB, nullable=False)
    date_col   = Column(Date)
    amount_col = Column(Numeric)

    file       = relationship("UploadedFile", back_populates="raw_rows")

    __table_args__ = (
        Index("ix_raw_data_file_date", "file_id", "date_col"),
    )