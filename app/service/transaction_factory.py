from app.ai.prediction_result import PredictionResult
from app.domain.monetary_transaction import MonetaryTransaction
from app.enum.transaction_direction import TransactionDirection
from app.enum.transaction_status import TransactionStatus
from app.enum.transaction_type import TransactionType


def build_transaction(
        account_id: int,
        transaction_type: TransactionType,
        direction: TransactionDirection,
        amount: float,
        currency: str,
        branch: str,
        description: str | None = None,
        related_account_id: int | None = None,
        transfer_reference: str | None = None,
        status: TransactionStatus = TransactionStatus.COMPLETED,
        reversal_of_transaction_id: int | None = None,
        assessment: PredictionResult | None = None
) -> MonetaryTransaction:
    """Single construction point for every monetary transaction row.

    Keeps the risk columns from being silently left empty, which is what
    happened while each service built its own MonetaryTransaction.
    """

    return MonetaryTransaction(
        account_id=account_id,
        transaction_type=transaction_type.value,
        direction=direction.value,
        amount=amount,
        currency=str(getattr(currency, "value", currency)),
        branch=branch,
        description=description,
        related_account_id=related_account_id,
        transfer_reference=transfer_reference,
        status=status.value,
        reversal_of_transaction_id=reversal_of_transaction_id,
        risk_level=assessment.risk_level if assessment else None,
        risk_score=assessment.risk_score if assessment else None,
        fraud_score=assessment.fraud_score if assessment else None,
        is_fraud_suspected=(
            assessment.is_fraud_suspected if assessment else False
        )
    )
