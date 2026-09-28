from app.domain.account import Account
from app.domain.account_balance import AccountBalance

NUMERIC_FEATURES: list[str] = [
    "transaction_amount",
    "available_balance",
    "current_balance",
    "overdraft_limit",
    "blocked_balance",
    "amount_to_available_ratio"
]

BINARY_FEATURES: list[str] = [
    "debit_transaction_blocked",
    "credit_transaction_blocked",
    "is_primary_account"
]

CATEGORICAL_FEATURES: list[str] = [
    "account_type",
    "transaction_type",
    "currency"
]

FEATURE_COLUMNS: list[str] = (
    NUMERIC_FEATURES + BINARY_FEATURES + CATEGORICAL_FEATURES
)

RISK_TARGET_COLUMN = "risk_level"

FRAUD_TARGET_COLUMN = "is_fraud"


class TransactionFeatureBuilder:
    """Single source of truth for the model feature contract.

    Training (``app.ai.dataset_generator``) and inference
    (``app.ai.prediction_service``) both go through this class, so the two
    can never drift apart silently.
    """

    def build_features(
            self,
            account: Account | None,
            account_balance: AccountBalance,
            transaction_type: str,
            amount: float,
            currency: str,
            available_balance: float
    ) -> dict:

        current_balance = account_balance.balance or 0.0
        overdraft_limit = account_balance.overdraft_limit or 0.0
        blocked_balance = account_balance.blocked_balance or 0.0

        return {
            "transaction_amount": float(amount),
            "available_balance": float(available_balance),
            "current_balance": float(current_balance),
            "overdraft_limit": float(overdraft_limit),
            "blocked_balance": float(blocked_balance),
            "amount_to_available_ratio": self.amount_to_available_ratio(
                amount,
                available_balance
            ),
            "debit_transaction_blocked": int(
                bool(account_balance.debit_transaction_blocked)
            ),
            "credit_transaction_blocked": int(
                bool(account_balance.credit_transaction_blocked)
            ),
            "is_primary_account": int(
                bool(account.is_primary) if account is not None else False
            ),
            "account_type": self._enum_value(
                account.account_type if account is not None else None
            ),
            "transaction_type": self._enum_value(transaction_type),
            "currency": self._enum_value(currency)
        }

    @staticmethod
    def amount_to_available_ratio(
            amount: float,
            available_balance: float
    ) -> float:
        """Amount relative to what the account can actually spend.

        The denominator is floored at 1.0 so an empty or negative available
        balance produces a large finite ratio instead of a division error.
        """
        return float(amount) / max(float(available_balance), 1.0)

    @staticmethod
    def _enum_value(value) -> str:
        if value is None:
            return "UNKNOWN"

        return str(getattr(value, "value", value))
