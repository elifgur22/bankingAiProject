from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.database import transactional
from app.domain.monetary_transaction import MonetaryTransaction
from app.enum.transaction_direction import TransactionDirection
from app.enum.transaction_type import TransactionType
from app.schemas.sundry_request import (
    SundryBatchRequest,
    SundryTransactionRequest
)
from app.service.transaction_posting_service import TransactionPostingService

logger = get_logger(__name__)


class SundryService:
    """Bank internal postings (fees, corrections, interest) and batches.

    A batch is all-or-nothing: one failing item rolls the whole batch back,
    which is what an operations team expects from an end-of-day run.
    """

    def __init__(
            self,
            posting_service: TransactionPostingService | None = None
    ):
        self.posting_service = posting_service or TransactionPostingService()

    def create_sundry_transaction(
            self,
            db: Session,
            request: SundryTransactionRequest
    ) -> MonetaryTransaction:

        with transactional(db):
            transaction = self._post_item(db, request)

        logger.info(
            "SUNDRY account_id=%s direction=%s amount=%s",
            request.account_id,
            request.direction.value,
            request.amount
        )

        return transaction

    def create_sundry_batch(
            self,
            db: Session,
            request: SundryBatchRequest
    ) -> tuple[str, list[MonetaryTransaction]]:

        batch_reference = request.batch_reference or uuid4().hex

        with transactional(db):
            transactions = [
                self._post_item(db, item, batch_reference)
                for item in request.items
            ]

        logger.info(
            "SUNDRY_BATCH reference=%s items=%s",
            batch_reference,
            len(transactions)
        )

        return batch_reference, transactions

    def _post_item(
            self,
            db: Session,
            item: SundryTransactionRequest,
            batch_reference: str | None = None
    ) -> MonetaryTransaction:

        direction = TransactionDirection(item.direction)

        result = self.posting_service.post(
            db=db,
            account_id=item.account_id,
            transaction_type=TransactionType.SUNDRY,
            direction=direction,
            amount=item.amount,
            currency=item.currency,
            branch=item.branch,
            description=item.description,
            transfer_reference=batch_reference
        )

        return result.transaction
