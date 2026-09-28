from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.database import transactional
from app.domain.monetary_transaction import MonetaryTransaction
from app.enum.transaction_direction import TransactionDirection
from app.enum.transaction_type import TransactionType
from app.exceptions.business_exception import BusinessException
from app.schemas.transfer_request import TransferRequest
from app.service.transaction_posting_service import TransactionPostingService
from app.validations.transaction_validation_rule import (
    TransactionValidationRule
)

logger = get_logger(__name__)


class TransferService:
    """Account to account transfer, recorded as two linked legs."""

    def __init__(
            self,
            posting_service: TransactionPostingService | None = None
    ):
        self.posting_service = posting_service or TransactionPostingService()

    def transfer(
            self,
            db: Session,
            request: TransferRequest
    ) -> tuple[MonetaryTransaction, MonetaryTransaction]:

        if request.source_account_id == request.target_account_id:
            raise BusinessException(
                TransactionValidationRule.SAME_SOURCE_AND_TARGET_ACCOUNT
            )

        transfer_reference = uuid4().hex

        with transactional(db):
            source = self.posting_service.post(
                db=db,
                account_id=request.source_account_id,
                transaction_type=TransactionType.TRANSFER,
                direction=TransactionDirection.DEBIT,
                amount=request.amount,
                currency=request.currency,
                branch=request.branch,
                description=request.description,
                related_account_id=request.target_account_id,
                transfer_reference=transfer_reference
            )

            # The target leg reuses the source assessment: one transfer is
            # one risk decision, scored on the paying side.
            target = self.posting_service.post(
                db=db,
                account_id=request.target_account_id,
                transaction_type=TransactionType.TRANSFER,
                direction=TransactionDirection.CREDIT,
                amount=request.amount,
                currency=request.currency,
                branch=request.branch,
                description=request.description,
                related_account_id=request.source_account_id,
                transfer_reference=transfer_reference,
                assessment=source.assessment
            )

        logger.info(
            "TRANSFER reference=%s %s->%s amount=%s risk=%s",
            transfer_reference,
            request.source_account_id,
            request.target_account_id,
            request.amount,
            source.assessment.risk_level if source.assessment else "N/A"
        )

        return source.transaction, target.transaction
