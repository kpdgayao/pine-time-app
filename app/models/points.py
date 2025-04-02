from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base


class PointsTransaction(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    points = Column(Integer, nullable=False)
    transaction_type = Column(String, nullable=False)  # earned, redeemed, expired
    description = Column(Text, nullable=False)
    event_id = Column(Integer, ForeignKey("event.id"), nullable=True)
    transaction_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="points_transactions")
    event = relationship("Event")