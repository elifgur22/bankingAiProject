from pydantic import BaseModel, Field

from app.enum.currency import Currency


class MonetaryTransactionRequest(BaseModel):
    """Deposit / withdraw request.

    The transaction type is not part of the payload: it is decided by the
    endpoint, so a caller cannot post a DEPOSIT body to /withdraw.
    """

    account_id: int = Field(gt=0)

    amount: float = Field(
        gt=0,
        description="Transaction amount must be greater than zero"
    )

    currency: Currency

    branch: str = Field(min_length=1, max_length=64)

    description: str | None = Field(default=None, max_length=255)
