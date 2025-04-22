from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base


class PointsTransaction(Base):
    __tablename__ = "points_transaction"  # Using singular table name to match existing database
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    points = Column(Integer, nullable=False)
    transaction_type = Column(String, nullable=False)  # earned, redeemed, expired, awarded
    description = Column(Text, nullable=False)
    event_id = Column(Integer, ForeignKey("event.id"), nullable=True)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # For admin actions
    transaction_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="points_transactions")
    event = relationship("Event")
    admin = relationship("User", foreign_keys=[admin_id], lazy="joined", back_populates="admin_points_transactions")  # admin who performed the action