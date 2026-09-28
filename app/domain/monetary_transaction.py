from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String

from app.database import Base
from app.enum.transaction_status import TransactionStatus


class MonetaryTransaction(Base):
    __tablename__ = "monetary_transaction"

    id = Column(Integer, primary_key=True, index=True)

    account_id = Column(Integer, index=True)

    transaction_type = Column(String, index=True)

    # CREDIT increases the account balance, DEBIT decreases it. Storing it
    # explicitly is what makes reversal a generic operation.
    direction = Column(String, index=True)

    amount = Column(Float)

    currency = Column(String)

    branch = Column(String)

    # Populated for transfers so both legs can be traced back to each other.
    related_account_id = Column(Integer, index=True)

    transfer_reference = Column(String, index=True)

    description = Column(String)

    status = Column(
        String,
        index=True,
        default=TransactionStatus.COMPLETED.value
    )

    # Points at the original transaction when this row is a reversal leg.
    reversal_of_transaction_id = Column(Integer, index=True)

    create_time = Column(DateTime, default=datetime.now)

    update_time = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now
    )

    risk_score = Column(Float)

    risk_level = Column(String)

    fraud_score = Column(Float)

    is_fraud_suspected = Column(Boolean, default=False)
