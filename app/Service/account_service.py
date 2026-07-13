from sqlalchemy.orm import Session

from app.domain.account import Account
from app.domain.account_balance import AccountBalance
from app.repository.account_repository import AccountRepository
from app.schemas.account_request import AccountCreateRequest

class AccountService:
    def __init__(self):
        self.account_repository = AccountRepository()

    def create_account(
            self,
            db: Session,
            request: AccountCreateRequest
    ) -> Account:

        account = Account(
            account_number = request.account_number,
            customer_name = request.customer_name,
            balance = request.balance,
            customer_id = request.customer_id,
            balance_currency = request.balance_currency,
            account_type = request.account_type,
            account_status = request.account_status,
            is_primary = request.is_primary,
            account_email = request.account_email
        )

        saved_account = self.account_repository.save(db,account)

        account_balance = AccountBalance(
            account_id=saved_account.id,
            balance=request.balance,
            balance_currency=request.balance_currency,
            overdraft_limit=request.overdraft_limit,
            overdraft_currency=request.overdraft_currency,
            blocked_balance=request.blocked_balance,
            blocked_balance_currency=request.blocked_balance_currency,
            debit_transaction_blocked=request.debit_transaction_blocked,
            credit_transaction_blocked=request.credit_transaction_blocked
        )

        self.account_repository.save_account_balance(db,account_balance)

        return saved_account