from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base


class EventAttendee(Base):
    """Model for event attendees."""
    
    __tablename__ = "event_attendees"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    event_id = Column(Integer, ForeignKey("event.id", ondelete="CASCADE"), nullable=False)  # Using singular 'event' table name
    status = Column(String, default="registered", nullable=False)  # registered, attended, cancelled
    registration_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    attendance_date = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="attended_events")
    event = relationship("Event", back_populates="attendees")
    
    def __repr__(self):
        return f"<EventAttendee(id={self.id}, user_id={self.user_id}, event_id={self.event_id}, status={self.status})>"
