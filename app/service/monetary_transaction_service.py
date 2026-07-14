from sqlalchemy.orm import Session

from app.domain.monetary_transaction import MonetaryTransaction
from app.repository.monetary_transaction_repository import MonetaryTransactionRepository
from app.schemas.monetary_transaction_request import MonetaryTransactionRequest


class MonetaryTransactionService:

    def __init__(self):
        self.transaction_repository = MonetaryTransactionRepository()

    def create_transaction(
            self,
            db: Session,
            request: MonetaryTransactionRequest
    ) -> MonetaryTransaction:

        transaction = MonetaryTransaction(
            account_id=request.account_id,
            transaction_type=request.transaction_type,
            amount=request.amount,
            currency=request.currency,
            branch=request.branch
        )

        return self.transaction_repository.save(db, transaction)