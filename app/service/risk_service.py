from app.domain.account import Account
from app.domain.account_balance import AccountBalance
from app.schemas.monetary_transaction_request import MonetaryTransactionRequest


class RiskService:

    def calculate_transaction_risk(
            self,
            account: Account,
            account_balance: AccountBalance,
            request: MonetaryTransactionRequest,
            available_balance: float
    ) -> tuple[float, str]:

        risk_score = 0.0

        if account_balance.debit_transaction_blocked:
            risk_score += 0.70

        if request.amount > available_balance:
            risk_score += 0.50

        if request.amount >= 100_000:
            risk_score += 0.20

        if account_balance.blocked_balance > 0:
            risk_score += 0.10

        risk_score = min(risk_score, 1.0)

        if risk_score >= 0.75:
            risk_level = "HIGH"
        elif risk_score >= 0.40:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return risk_score, risk_level