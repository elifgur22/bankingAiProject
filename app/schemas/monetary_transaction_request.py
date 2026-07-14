from pydantic import BaseModel

class MonetaryTransactionRequest(BaseModel):
    account_id: int
    transaction_type: str
    amount: float
    currency: str
    branch: str