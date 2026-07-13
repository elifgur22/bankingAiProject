from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

from app.database import Base


class MonetaryTransaction(Base):
    __tablename__ = "monetary_transaction"

    id = Column(Integer, primary_key=True, index=True)

    account_id = Column(Integer, index=True)

    transaction_type = Column(String, index=True)

    amount = Column(Float)

    currency = Column(String)

    branch = Column(String)

    create_time = Column(DateTime, default=datetime.now)

    update_time = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now
    )

    risk_score = Column(Float)

    risk_level = Column(String)