from app.domain.account import Account
from app.domain.account_balance import AccountBalance
from app.schemas.monetary_transaction_request import MonetaryTransactionRequest


class TransactionFeatureBuilder:

    def build_features(
            self,
            account: Account,
            account_balance: AccountBalance,
            request: MonetaryTransactionRequest,
            available_balance: float
    ) -> dict:
        return {
            "transaction_amount": request.amount,
            "available_balance": available_balance,
            "current_balance": account_balance.balance or 0.0,
            "overdraft_limit": account_balance.overdraft_limit or 0.0,
            "blocked_balance": account_balance.blocked_balance or 0.0,
            "debit_transaction_blocked": int(account_balance.debit_transaction_blocked),
            "credit_transaction_blocked": int(account_balance.credit_transaction_blocked),
            "is_primary_account":  int(account.is_primary),
            "account_type": str(account.account_type),
            "transaction_tye": request.transaction_type,
            "currency": request.currency
        }