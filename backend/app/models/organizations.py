from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base

class Organization(Base):
    __tablename__ = "organizations"

    id                 = Column(Integer, primary_key=True, index=True)
    name               = Column(String(255), nullable=False)
    industry           = Column(String(100), nullable=True)
    team_size          = Column(String(50), nullable=True)
    stripe_customer_id = Column(String(255), nullable=True)
    created_at         = Column(DateTime(timezone=True), server_default=func.now())

    users              = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    uploaded_files     = relationship("UploadedFile", back_populates="organization", cascade="all, delete-orphan")
    subscription       = relationship("Subscription", back_populates="organization", uselist=False, cascade="all, delete-orphan")
