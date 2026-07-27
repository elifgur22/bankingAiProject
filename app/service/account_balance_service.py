from sqlalchemy.orm import Session

from app.domain.account_balance import AccountBalance
from app.exceptions.business_exception import BusinessException
from app.repository.account_balance_repository import AccountBalanceRepository
from app.validations.account_validation_rule import AccountValidationRule


class AccountBalanceService:

    def __init__(self):
        self.account_balance_repository = AccountBalanceRepository()

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

        return (
            account_balance.balance
            + account_balance.overdraft_limit
            - account_balance.blocked_balance
        )

    def increase_balance(
            self,
            db: Session,
            account_balance: AccountBalance,
            amount: float
    ) -> AccountBalance:

        account_balance.balance += amount

        return self.account_balance_repository.save(
            db,
            account_balance
        )

    def decrease_balance(
            self,
            db: Session,
            account_balance: AccountBalance,
            amount: float
    ) -> AccountBalance:

        account_balance.balance -= amount

        return self.account_balance_repository.save(
            db,
            account_balance
        )