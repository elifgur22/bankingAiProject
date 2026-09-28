from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.database import transactional
from app.domain.monetary_transaction import MonetaryTransaction
from app.enum.transaction_direction import TransactionDirection
from app.enum.transaction_type import TransactionType
from app.schemas.monetary_transaction_request import MonetaryTransactionRequest
from app.service.transaction_posting_service import (
    PostingResult,
    TransactionPostingService
)

logger = get_logger(__name__)


class MonetaryTransactionService:
    """Deposit and withdraw orchestration."""

    def __init__(
            self,
            posting_service: TransactionPostingService | None = None
    ):
        self.posting_service = posting_service or TransactionPostingService()

    def deposit(
            self,
            db: Session,
            request: MonetaryTransactionRequest
    ) -> MonetaryTransaction:

        return self._execute(
            db,
            request,
            TransactionType.DEPOSIT,
            TransactionDirection.CREDIT
        )

    def withdraw(
            self,
            db: Session,
            request: MonetaryTransactionRequest
    ) -> MonetaryTransaction:

        return self._execute(
            db,
            request,
            TransactionType.WITHDRAW,
            TransactionDirection.DEBIT
        )

    def _execute(
            self,
            db: Session,
            request: MonetaryTransactionRequest,
            transaction_type: TransactionType,
            direction: TransactionDirection
    ) -> MonetaryTransaction:

        with transactional(db):
            result: PostingResult = self.posting_service.post(
                db=db,
                account_id=request.account_id,
                transaction_type=transaction_type,
                direction=direction,
                amount=request.amount,
                currency=request.currency,
                branch=request.branch,
                description=request.description
            )

        self._log(transaction_type, request, result)

        return result.transaction

    @staticmethod
    def _log(
            transaction_type: TransactionType,
            request: MonetaryTransactionRequest,
            result: PostingResult
    ) -> None:

        assessment = result.assessment

        logger.info(
            "%s account_id=%s amount=%s risk=%s score=%s source=%s",
            transaction_type.value,
            request.account_id,
            request.amount,
            assessment.risk_level if assessment else "N/A",
            assessment.risk_score if assessment else "N/A",
            assessment.source if assessment else "N/A"
        )
