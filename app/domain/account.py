from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Enum

from app.database import Base
from app.domain.account_type import AccountType
from app.domain.account_status import AccountStatus


class Account(Base):
    __tablename__ = "account"

    id = Column(Integer, primary_key=True, index=True)

    account_name = Column(String)

    customer_id = Column(Integer, ForeignKey("customer.id"))

    account_type = Column(Enum(AccountType))

    account_status = Column(Enum(AccountStatus))

    account_number = Column(String, unique=True, index=True)

    is_primary = Column(Boolean, default=False)

    account_email = Column(String)

    create_time = Column(DateTime, default=datetime.now)

    update_time = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now
    )