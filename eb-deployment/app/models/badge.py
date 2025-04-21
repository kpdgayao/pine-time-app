from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base


class Badge(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    badge_type_id = Column(Integer, ForeignKey("badge_types.id"), nullable=False)  # FK to BadgeType
    badge_type = Column(String, nullable=False)  # event_master, trivia_champion, etc.
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    image_url = Column(String, nullable=True)
    earned_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="badges")
    badge_type_obj = relationship("BadgeType", back_populates="badges")