from typing import List, Optional
from sqlalchemy import Boolean, Column, Integer, String, Enum
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    user_type = Column(String, default="regular")  # regular, business, admin
    
    # Relationships
    registrations = relationship("Registration", back_populates="user")
    badges = relationship("Badge", back_populates="user")
    points_transactions = relationship(
        "PointsTransaction",
        back_populates="user",
        foreign_keys="PointsTransaction.user_id"
    )
    admin_points_transactions = relationship(
        "PointsTransaction",
        back_populates="admin",
        foreign_keys="PointsTransaction.admin_id"
    )