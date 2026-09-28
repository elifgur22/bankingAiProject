from datetime import datetime

from sqlalchemy.orm import Session

from app.domain.monetary_transaction import MonetaryTransaction
from app.enum.transaction_type import TransactionType
from app.exceptions.business_exception import BusinessException
from app.repository.monetary_transaction_repository import (
    MonetaryTransactionRepository
)
from app.service.account_service import AccountService
from app.validations.transaction_validation_rule import (
    TransactionValidationRule
)

MAX_PAGE_SIZE = 200


class TransactionHistoryService:
    """Read side of the transaction ledger."""

    def __init__(
            self,
            transaction_repository: MonetaryTransactionRepository | None = None,
            account_service: AccountService | None = None
    ):
        self.transaction_repository = (
            transaction_repository or MonetaryTransactionRepository()
        )

        self.account_service = account_service or AccountService()

    def get_account_history(
            self,
            db: Session,
            account_id: int,
            transaction_type: TransactionType | None = None,
            date_from: datetime | None = None,
            date_to: datetime | None = None,
            limit: int = 50,
            offset: int = 0
    ) -> tuple[list[MonetaryTransaction], int]:

        self.account_service.get_required_account(db, account_id)

        type_value = (
            transaction_type.value
            if transaction_type is not None
            else None
        )

        limit = max(1, min(limit, MAX_PAGE_SIZE))
        offset = max(0, offset)

        items = self.transaction_repository.find_by_account_id(
            db,
            account_id=account_id,
            transaction_type=type_value,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset
        )

        total = self.transaction_repository.count_by_account_id(
            db,
            account_id=account_id,
            transaction_type=type_value,
            date_from=date_from,
            date_to=date_to
        )

        return items, total

    def get_required_transaction(
            self,
            db: Session,
            transaction_id: int
    ) -> MonetaryTransaction:

        transaction = self.transaction_repository.find_by_id(
            db,
            transaction_id
        )

        if transaction is None:
            raise BusinessException(
                TransactionValidationRule.TRANSACTION_NOT_FOUND
            )

        return transaction
