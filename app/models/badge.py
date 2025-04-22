from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base


class Badge(Base):
    __tablename__ = "badges"  # Using plural table name to match existing database
    id = Column(Integer, primary_key=True, index=True)
    badge_type_id = Column(Integer, ForeignKey("badge_types.id"), nullable=False)  # FK to BadgeType
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    icon_url = Column(String, nullable=True)
    category = Column(String, nullable=True)  # events, social, achievements, etc.
    max_level = Column(Integer, default=5, nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    badge_type_obj = relationship("BadgeType", back_populates="badges")
    user_badges = relationship("UserBadge", back_populates="badge")