from sqlalchemy.orm import Session

from app.database import transactional
from app.domain.account import Account
from app.domain.account_balance import AccountBalance
from app.domain.account_status import AccountStatus
from app.exceptions.business_exception import BusinessException
from app.repository.account_balance_repository import AccountBalanceRepository
from app.repository.account_repository import AccountRepository
from app.schemas.account_request import AccountCreateRequest
from app.service.account_balance_service import AccountBalanceService
from app.validations.account_validation_rule import AccountValidationRule


class AccountService:

    def __init__(
            self,
            account_repository: AccountRepository | None = None,
            account_balance_repository: AccountBalanceRepository | None = None,
            account_balance_service: AccountBalanceService | None = None
    ):
        self.account_repository = account_repository or AccountRepository()

        self.account_balance_repository = (
            account_balance_repository or AccountBalanceRepository()
        )

        self.account_balance_service = (
            account_balance_service or AccountBalanceService()
        )

    def create_account(
            self,
            db: Session,
            request: AccountCreateRequest
    ) -> Account:
        """Create the account and its opening balance in one transaction."""

        with transactional(db):
            self._ensure_account_number_is_free(db, request.account_number)

            account = Account(
                account_name=request.account_name,
                account_number=request.account_number,
                customer_id=request.customer_id,
                account_type=request.account_type,
                account_status=request.account_status,
                is_primary=request.is_primary,
                account_email=request.account_email
            )

            saved_account = self.account_repository.save(db, account)

            account_balance = AccountBalance(
                account_id=saved_account.id,
                balance=request.balance,
                balance_currency=request.balance_currency.value,
                overdraft_limit=request.overdraft_limit,
                overdraft_currency=self._currency_value(
                    request.overdraft_currency,
                    request.balance_currency
                ),
                blocked_balance=request.blocked_balance,
                blocked_balance_currency=self._currency_value(
                    request.blocked_balance_currency,
                    request.balance_currency
                ),
                debit_transaction_blocked=request.debit_transaction_blocked,
                credit_transaction_blocked=request.credit_transaction_blocked
            )

            self.account_balance_repository.save(db, account_balance)

        return saved_account

    def get_required_account(self, db: Session, account_id: int) -> Account:
        account = self.account_repository.find_by_id(db, account_id)

        if account is None:
            raise BusinessException(
                AccountValidationRule.ACCOUNT_NOT_FOUND
            )

        return account

    def ensure_account_is_active(self, account: Account) -> None:
        if account.account_status in (
            AccountStatus.CLOSED,
            AccountStatus.ACCOUNT_BLOCKED
        ):
            raise BusinessException(
                AccountValidationRule.ACCOUNT_IS_NOT_ACTIVE
            )

    def get_account_balance(self, db: Session, account_id: int):
        self.get_required_account(db, account_id)

        return self.account_balance_service.get_required_balance(
            db,
            account_id
        )

    def _ensure_account_number_is_free(
            self,
            db: Session,
            account_number: str
    ) -> None:

        existing = self.account_repository.find_by_account_number(
            db,
            account_number
        )

        if existing is not None:
            raise BusinessException(
                AccountValidationRule.ACCOUNT_NUMBER_ALREADY_EXISTS
            )

    @staticmethod
    def _currency_value(currency, fallback) -> str:
        return (currency or fallback).value
