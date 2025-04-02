from sqlalchemy import Boolean, Column, Integer, String, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Event(Base):
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=False)
    event_type = Column(String, nullable=False)  # trivia, murder_mystery, game_night, etc.
    location = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    max_participants = Column(Integer, nullable=True)
    points_reward = Column(Integer, default=0)
    is_active = Column(Boolean(), default=True)
    image_url = Column(String, nullable=True)
    price = Column(Float, default=0.0)
    
    # Relationships
    registrations = relationship("Registration", back_populates="event")