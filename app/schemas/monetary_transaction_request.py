from pydantic import BaseModel, Field

from app.enum.transaction_type import TransactionType

class MonetaryTransactionRequest(BaseModel):
    account_id: int

    transaction_type: TransactionType

    amount: float = Field(
        gt=0,
        description="Transaction amount must be greater than zero"
    )

    currency: str

    branch: str