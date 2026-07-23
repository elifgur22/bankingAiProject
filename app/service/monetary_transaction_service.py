from sqlalchemy.orm import Session

from app.domain.monetary_transaction import MonetaryTransaction
from app.repository.account_balance_repository import AccountBalanceRepository
from app.repository.account_repository import AccountRepository
from app.repository.monetary_transaction_repository import MonetaryTransactionRepository
from app.schemas.monetary_transaction_request import MonetaryTransactionRequest


class MonetaryTransactionService:

    def __init__(self):
        self.transaction_repository = MonetaryTransactionRepository()
        self.account_repository = AccountRepository()
        self.account_balance_repository = AccountBalanceRepository()

    def deposit(
            self,
            db: Session,
            request: MonetaryTransactionRequest
    ) -> MonetaryTransaction:

        account = self.account_repository.find_by_id(db, request.account_id)

        if account is None:
            raise Exception("Account not found")

        account_balance = self.account_balance_repository.find_by_account_id(
            db,
            request.account_id
        )

        if account_balance is None:
            raise Exception("Account balance not found")

        account_balance.balance += request.amount

        self.account_balance_repository.save(
            db,
            account_balance
        )

        transaction = MonetaryTransaction(
            account_id=request.account_id,
            transaction_type=request.transaction_type,
            amount=request.amount,
            currency=request.currency,
            branch=request.branch
        )

        return self.transaction_repository.save(
            db,
            transaction
        )

    def withdraw(
            self,
            db: Session,
            request: MonetaryTransactionRequest
    ) -> MonetaryTransaction:

        account = self.account_repository.find_by_id(db, request.account_id)

        if account is None:
            raise Exception("Account not found")

        account_balance = self.account_balance_repository.find_by_account_id(
            db,
            request.account_id
        )

        if account_balance is None:
            raise Exception("Account balance not found")

        if account_balance.debit_transaction_blocked:
            raise Exception("Debit transactions are blocked for this account")

        available_balance = (
                account_balance.balance
                + account_balance.overdraft_limit
                - account_balance.blocked_balance
        )

        if request.amount > available_balance:
            raise Exception("Insufficient balance")

        # AI comes here👇

        account_balance.balance -= request.amount

        self.account_balance_repository.save(
            db,
            account_balance
        )

        transaction = MonetaryTransaction(
            account_id=request.account_id,
            transaction_type=request.transaction_type,
            amount=request.amount,
            currency=request.currency,
            branch=request.branch
        )

        return self.transaction_repository.save(
            db,
            transaction
        )