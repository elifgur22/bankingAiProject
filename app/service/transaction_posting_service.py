from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.ai.prediction_result import PredictionResult
from app.domain.monetary_transaction import MonetaryTransaction
from app.enum.transaction_direction import TransactionDirection
from app.enum.transaction_status import TransactionStatus
from app.enum.transaction_type import TransactionType
from app.repository.monetary_transaction_repository import (
    MonetaryTransactionRepository
)
from app.service.account_balance_service import AccountBalanceService
from app.service.account_service import AccountService
from app.service.transaction_factory import build_transaction
from app.service.transaction_risk_service import TransactionRiskService


@dataclass(frozen=True)
class PostingResult:
    transaction: MonetaryTransaction
    assessment: PredictionResult | None


class TransactionPostingService:
    """Posts a single balance movement together with its transaction row.

    Every money movement in the system - deposit, withdraw, both transfer
    legs, sundry items and reversals - is exactly one call to ``post``.

    It deliberately does NOT commit: the caller owns the transaction
    boundary, which is what keeps a transfer or a sundry batch atomic.
    """

    def __init__(
            self,
            account_service: AccountService | None = None,
            account_balance_service: AccountBalanceService | None = None,
            transaction_repository: MonetaryTransactionRepository | None = None,
            transaction_risk_service: TransactionRiskService | None = None
    ):
        self.account_service = account_service or AccountService()

        self.account_balance_service = (
            account_balance_service or AccountBalanceService()
        )

        self.transaction_repository = (
            transaction_repository or MonetaryTransactionRepository()
        )

        self.transaction_risk_service = (
            transaction_risk_service or TransactionRiskService()
        )

    def post(
            self,
            db: Session,
            account_id: int,
            transaction_type: TransactionType,
            direction: TransactionDirection,
            amount: float,
            currency,
            branch: str,
            description: str | None = None,
            related_account_id: int | None = None,
            transfer_reference: str | None = None,
            status: TransactionStatus = TransactionStatus.COMPLETED,
            reversal_of_transaction_id: int | None = None,
            assessment: PredictionResult | None = None,
            enforce_block_guards: bool = True,
            score_risk: bool = True
    ) -> PostingResult:

        account = self.account_service.get_required_account(db, account_id)

        self.account_service.ensure_account_is_active(account)

        account_balance = self.account_balance_service.get_required_balance(
            db,
            account_id
        )

        self.account_balance_service.ensure_currency_matches(
            account_balance,
            currency
        )

        available_balance = self._guard(
            account_balance,
            direction,
            amount,
            enforce_block_guards
        )

        # Scored before the balance moves so the features describe the state
        # the decision was actually made on.
        if assessment is None and score_risk:
            assessment = self.transaction_risk_service.assess(
                account=account,
                account_balance=account_balance,
                transaction_type=transaction_type.value,
                amount=amount,
                currency=self._currency_value(currency),
                available_balance=available_balance
            )

        self.account_balance_service.apply_movement(
            db,
            account_balance,
            direction,
            amount
        )

        transaction = self.transaction_repository.save(
            db,
            build_transaction(
                account_id=account_id,
                transaction_type=transaction_type,
                direction=direction,
                amount=amount,
                currency=self._currency_value(currency),
                branch=branch,
                description=description,
                related_account_id=related_account_id,
                transfer_reference=transfer_reference,
                status=status,
                reversal_of_transaction_id=reversal_of_transaction_id,
                assessment=assessment
            )
        )

        return PostingResult(transaction=transaction, assessment=assessment)

    def _guard(
            self,
            account_balance,
            direction: TransactionDirection,
            amount: float,
            enforce_block_guards: bool
    ) -> float:
        """Run the direction specific guards, return the available balance.

        ``enforce_block_guards`` is switched off for reversals: a correction
        must still land on an account whose debits are blocked, but it may
        never overdraw it.
        """

        if direction is TransactionDirection.CREDIT:
            if enforce_block_guards:
                self.account_balance_service.ensure_credit_allowed(
                    account_balance
                )

            return self.account_balance_service.calculate_available_balance(
                account_balance
            )

        if enforce_block_guards:
            self.account_balance_service.ensure_debit_allowed(account_balance)

        return self.account_balance_service.ensure_sufficient_balance(
            account_balance,
            amount
        )

    @staticmethod
    def _currency_value(currency) -> str:
        return str(getattr(currency, "value", currency))
