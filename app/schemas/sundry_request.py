from pydantic import BaseModel, Field

from app.enum.currency import Currency
from app.enum.transaction_direction import TransactionDirection

MAX_SUNDRY_BATCH_SIZE = 500


class SundryTransactionRequest(BaseModel):
    """Bank internal posting (fee, correction, interest) on one account."""

    account_id: int = Field(gt=0)

    direction: TransactionDirection

    amount: float = Field(gt=0)

    currency: Currency

    branch: str = Field(min_length=1, max_length=64)

    description: str | None = Field(default=None, max_length=255)


class SundryBatchRequest(BaseModel):
    """All-or-nothing batch of sundry postings."""

    items: list[SundryTransactionRequest] = Field(
        min_length=1,
        max_length=MAX_SUNDRY_BATCH_SIZE
    )

    batch_reference: str | None = Field(default=None, max_length=64)
