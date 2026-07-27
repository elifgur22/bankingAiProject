from sqlalchemy.orm import Session

from app.domain.monetary_transaction import MonetaryTransaction
from app.enum.transaction_type import TransactionType
from app.exceptions.business_exception import BusinessException
from app.repository.account_repository import AccountRepository
from app.repository.monetary_transaction_repository import MonetaryTransactionRepository
from app.schemas.monetary_transaction_request import MonetaryTransactionRequest
from app.service.account_balance_service import AccountBalanceService
from app.enum.account_validation_rule import AccountValidationRule
from app.ai.prediction_service import  PredictionService

class MonetaryTransactionService:

    def __init__(self):
        self.transaction_repository = MonetaryTransactionRepository()
        self.account_repository = AccountRepository()
        self.account_balance_service = AccountBalanceService()
        self.prediction_service = PredictionService()

    def deposit(
            self,
            db: Session,
            request: MonetaryTransactionRequest
    ) -> MonetaryTransaction:

        self._validate_account_exists(
            db,
            request.account_id
        )

        account_balance = (
            self.account_balance_service.get_required_balance(
                db,
                request.account_id
            )
        )

        self.account_balance_service.increase_balance(
            db,
            account_balance,
            request.amount
        )

        return self._create_and_save_transaction(
            db=db,
            request=request,
            transaction_type=TransactionType.DEPOSIT
        )

    def withdraw(
            self,
            db: Session,
            request: MonetaryTransactionRequest
    ) -> MonetaryTransaction:

        self._validate_account_exists(
            db,
            request.account_id
        )

        account_balance = (
            self.account_balance_service.get_required_balance(
                db,
                request.account_id
            )
        )

        if account_balance.debit_transaction_blocked:
            raise BusinessException(
                AccountValidationRule.DEBIT_TRANSACTION_BLOCKED
            )

        available_balance = (
            self.account_balance_service.calculate_available_balance(
                account_balance
            )
        )

        if request.amount > available_balance:
            raise BusinessException(
                AccountValidationRule.INSUFFICIENT_BALANCE
            )
        prediction_result = self.prediction_service.predict_risk(
            transaction_amount=request.amount,
            available_balance=available_balance,
            blocked_balance=account_balance.blocked_balance,
            debit_blocked=account_balance.debit_transaction_blocked
        )

        self.account_balance_service.decrease_balance(
            db,
            account_balance,
            request.amount
        )

        return self._create_and_save_transaction(
            db=db,
            request=request,
            transaction_type=TransactionType.WITHDRAW
        )

    def _validate_account_exists(
            self,
            db: Session,
            account_id: int
    ) -> None:

        account = self.account_repository.find_by_id(
            db,
            account_id
        )

        if account is None:
            raise BusinessException(
                AccountValidationRule.ACCOUNT_NOT_FOUND
            )

    def _create_and_save_transaction(
            self,
            db: Session,
            request: MonetaryTransactionRequest,
            transaction_type: TransactionType,
            risk_level: str | None = None,
            risk_score: float | None = None
    ) -> MonetaryTransaction:

        transaction = MonetaryTransaction(
            account_id=request.account_id,
            transaction_type=transaction_type,
            amount=request.amount,
            currency=request.currency,
            branch=request.branch,
            risk_level=risk_level,
            risk_score=risk_score
        )

        return self.transaction_repository.save(
            db,
            transaction
        )