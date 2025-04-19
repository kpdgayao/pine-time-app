from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class BadgeType(Base):
    __tablename__ = "badge_types"
    id = Column(Integer, primary_key=True, index=True)
    badge_type = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    criteria_type = Column(String, nullable=True)
    criteria_threshold = Column(Integer, nullable=True)
    level = Column(String, nullable=True)
    image_url = Column(String, nullable=True)

    badges = relationship("Badge", back_populates="badge_type_obj")  # One-to-many BadgeType -> Badge
