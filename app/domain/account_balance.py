from datetime import datetime

from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, ForeignKey

from app.database import Base


class AccountBalance(Base):
    __tablename__ = "account_balance"

    id = Column(Integer, primary_key=True, index=True)

    account_id = Column(Integer, ForeignKey("account.id"), index=True)

    balance = Column(Float, default=0.0)

    balance_currency = Column(String)

    overdraft_limit = Column(Float, default=0.0)

    overdraft_currency = Column(String)

    blocked_balance = Column(Float, default=0.0)

    blocked_balance_currency = Column(String)

    debit_transaction_blocked = Column(Boolean, default=False)

    credit_transaction_blocked = Column(Boolean, default=False)

    create_time = Column(DateTime, default=datetime.now)

    update_time = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now
    )