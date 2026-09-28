from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String

from app.database import Base
from app.enum.user_role import UserRole


class User(Base):
    __tablename__ = "app_user"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String, unique=True, index=True, nullable=False)

    hashed_password = Column(String, nullable=False)

    role = Column(
        Enum(UserRole),
        default=UserRole.CUSTOMER,
        nullable=False
    )

    is_active = Column(Boolean, default=True, nullable=False)

    create_time = Column(DateTime, default=datetime.now)

    update_time = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now
    )
