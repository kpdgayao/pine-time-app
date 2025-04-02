from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base


class Registration(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("event.id"), nullable=False)
    registration_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="registered")  # registered, attended, cancelled, etc.
    payment_status = Column(String, default="pending")  # pending, completed, refunded
    
    # Relationships
    user = relationship("User", back_populates="registrations")
    event = relationship("Event", back_populates="registrations")