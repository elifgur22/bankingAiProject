from sqlalchemy.orm import Session

from app.domain.account_balance import AccountBalance
from app.enum.transaction_direction import TransactionDirection
from app.exceptions.business_exception import BusinessException
from app.repository.account_balance_repository import AccountBalanceRepository
from app.validations.account_validation_rule import AccountValidationRule


class AccountBalanceService:
    """Owns every read, guard and mutation of an account balance."""

    def __init__(
            self,
            account_balance_repository: AccountBalanceRepository | None = None
    ):
        self.account_balance_repository = (
            account_balance_repository or AccountBalanceRepository()
        )

    def get_required_balance(
            self,
            db: Session,
            account_id: int
    ) -> AccountBalance:

        account_balance = (
            self.account_balance_repository.find_by_account_id(
                db,
                account_id
            )
        )

        if account_balance is None:
            raise BusinessException(
                AccountValidationRule.ACCOUNT_BALANCE_NOT_FOUND
            )

        return account_balance

    def calculate_available_balance(
            self,
            account_balance: AccountBalance
    ) -> float:
        """Spendable amount: own funds plus overdraft, minus blocked funds.

        Never negative: a blocked amount larger than the balance means
        nothing is spendable, not that the customer owes the difference.
        """

        balance = account_balance.balance or 0.0
        overdraft_limit = account_balance.overdraft_limit or 0.0
        blocked_balance = account_balance.blocked_balance or 0.0

        return max(balance + overdraft_limit - blocked_balance, 0.0)

    def ensure_debit_allowed(self, account_balance: AccountBalance) -> None:
        if account_balance.debit_transaction_blocked:
            raise BusinessException(
                AccountValidationRule.DEBIT_TRANSACTION_BLOCKED
            )

    def ensure_credit_allowed(self, account_balance: AccountBalance) -> None:
        if account_balance.credit_transaction_blocked:
            raise BusinessException(
                AccountValidationRule.CREDIT_TRANSACTION_BLOCKED
            )

    def ensure_sufficient_balance(
            self,
            account_balance: AccountBalance,
            amount: float
    ) -> float:

        available_balance = self.calculate_available_balance(account_balance)

        if amount > available_balance:
            raise BusinessException(
                AccountValidationRule.INSUFFICIENT_BALANCE
            )

        return available_balance

    def ensure_currency_matches(
            self,
            account_balance: AccountBalance,
            currency: str
    ) -> None:

        expected = account_balance.balance_currency

        if expected is None:
            return

        # str() on a str-Enum member yields "Currency.TRY", not "TRY".
        if self._currency_value(expected) != self._currency_value(currency):
            raise BusinessException(
                AccountValidationRule.CURRENCY_MISMATCH
            )

    @staticmethod
    def _currency_value(currency) -> str:
        return str(getattr(currency, "value", currency))

    def apply_movement(
            self,
            db: Session,
            account_balance: AccountBalance,
            direction: TransactionDirection,
            amount: float
    ) -> AccountBalance:

        if direction is TransactionDirection.CREDIT:
            return self.increase_balance(db, account_balance, amount)

        return self.decrease_balance(db, account_balance, amount)

    def increase_balance(
            self,
            db: Session,
            account_balance: AccountBalance,
            amount: float
    ) -> AccountBalance:

        account_balance.balance = (account_balance.balance or 0.0) + amount

        return self.account_balance_repository.save(db, account_balance)

    def decrease_balance(
            self,
            db: Session,
            account_balance: AccountBalance,
            amount: float
    ) -> AccountBalance:

        account_balance.balance = (account_balance.balance or 0.0) - amount

        return self.account_balance_repository.save(db, account_balance)
