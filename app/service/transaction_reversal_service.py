from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.database import transactional
from app.domain.monetary_transaction import MonetaryTransaction
from app.enum.transaction_direction import TransactionDirection
from app.enum.transaction_status import TransactionStatus
from app.enum.transaction_type import TransactionType
from app.exceptions.business_exception import BusinessException
from app.repository.monetary_transaction_repository import (
    MonetaryTransactionRepository
)
from app.service.transaction_history_service import TransactionHistoryService
from app.service.transaction_posting_service import TransactionPostingService
from app.validations.transaction_validation_rule import (
    TransactionValidationRule
)

logger = get_logger(__name__)

REVERSIBLE_TYPES = {
    TransactionType.DEPOSIT.value,
    TransactionType.WITHDRAW.value,
    TransactionType.TRANSFER.value,
    TransactionType.SUNDRY.value
}

OPPOSITE_DIRECTION = {
    TransactionDirection.CREDIT: TransactionDirection.DEBIT,
    TransactionDirection.DEBIT: TransactionDirection.CREDIT
}


class TransactionReversalService:
    """Books the compensating entry for an already settled transaction.

    Nothing is deleted or edited in place: the original row is marked
    REVERSED and a new REVERSAL row carries the opposite movement, so the
    ledger stays append-only and auditable.
    """

    def __init__(
            self,
            posting_service: TransactionPostingService | None = None,
            transaction_repository: MonetaryTransactionRepository | None = None,
            history_service: TransactionHistoryService | None = None
    ):
        self.posting_service = posting_service or TransactionPostingService()

        self.transaction_repository = (
            transaction_repository or MonetaryTransactionRepository()
        )

        self.history_service = history_service or TransactionHistoryService()

    def reverse(
            self,
            db: Session,
            transaction_id: int
    ) -> list[MonetaryTransaction]:

        with transactional(db):
            original = self.history_service.get_required_transaction(
                db,
                transaction_id
            )

            self._ensure_reversible(db, original)

            legs = self._legs_to_reverse(db, original)

            reversals = [self._reverse_leg(db, leg) for leg in legs]

        logger.info(
            "REVERSAL transaction_id=%s legs=%s",
            transaction_id,
            len(reversals)
        )

        return reversals

    def _ensure_reversible(
            self,
            db: Session,
            transaction: MonetaryTransaction
    ) -> None:

        if transaction.transaction_type not in REVERSIBLE_TYPES:
            raise BusinessException(
                TransactionValidationRule.TRANSACTION_NOT_REVERSIBLE
            )

        if transaction.status != TransactionStatus.COMPLETED.value:
            raise BusinessException(
                TransactionValidationRule.TRANSACTION_ALREADY_REVERSED
            )

        already_reversed = self.transaction_repository.find_reversal_of(
            db,
            transaction.id
        )

        if already_reversed is not None:
            raise BusinessException(
                TransactionValidationRule.TRANSACTION_ALREADY_REVERSED
            )

    def _legs_to_reverse(
            self,
            db: Session,
            transaction: MonetaryTransaction
    ) -> list[MonetaryTransaction]:
        """A transfer is reversed as a whole: both legs or neither."""

        if (
            transaction.transaction_type == TransactionType.TRANSFER.value
            and transaction.transfer_reference
        ):
            legs = self.transaction_repository.find_by_transfer_reference(
                db,
                transaction.transfer_reference
            )

            return [
                leg for leg in legs
                if leg.status == TransactionStatus.COMPLETED.value
            ] or [transaction]

        return [transaction]

    def _reverse_leg(
            self,
            db: Session,
            leg: MonetaryTransaction
    ) -> MonetaryTransaction:

        direction = OPPOSITE_DIRECTION[TransactionDirection(leg.direction)]

        result = self.posting_service.post(
            db=db,
            account_id=leg.account_id,
            transaction_type=TransactionType(leg.transaction_type),
            direction=direction,
            amount=leg.amount,
            currency=leg.currency,
            branch=leg.branch,
            description=f"Reversal of transaction {leg.id}",
            related_account_id=leg.related_account_id,
            transfer_reference=leg.transfer_reference,
            status=TransactionStatus.REVERSAL,
            reversal_of_transaction_id=leg.id,
            enforce_block_guards=False,
            score_risk=False
        )

        leg.status = TransactionStatus.REVERSED.value

        self.transaction_repository.save(db, leg)

        return result.transaction
