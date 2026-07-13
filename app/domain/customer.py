from sqlalchemy import Column, Integer, String, DateTime

from app.database import Base
from datetime import datetime

class Customer(Base):
    __tablename__ = "customer"

    id = Column(Integer, primary_key=True, index=True)

    customer_number = Column(String, unique=True)

    customer_email = Column(String)

    first_name = Column(String)

    last_name = Column(String)

    phone_number = Column(String)

    email = Column(String)

    address = Column(String)

    language = Column(String)

    city = Column(String)

    state = Column(String)

    zip_code = Column(String)

    country = Column(String)

    create_time = Column(DateTime, default=datetime.now)

    update_time = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now
    )
