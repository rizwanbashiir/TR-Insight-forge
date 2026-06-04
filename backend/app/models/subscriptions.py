from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base

class Subscription(Base):
    __tablename__ = "subscriptions"

    id                     = Column(Integer, primary_key=True, index=True)
    organization_id        = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, unique=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    plan_tier              = Column(String(50), default="free")
    status                 = Column(String(50), default="active")
    current_period_end     = Column(DateTime(timezone=True), nullable=True)

    organization           = relationship("Organization", back_populates="subscription")
