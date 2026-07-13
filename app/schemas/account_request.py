from pydantic import BaseModel

from app.domain.account_status import AccountStatus
from app.domain.account_type import AccountType

class AccountCreateRequest(BaseModel):
    account_name: str
    customer_id: int
    account_type: AccountType
    account_status: AccountStatus
    account_number: str
    is_primary: bool = False
    account_email: str | None = None

    balance: float = 0.0
    balance_currency: str
    overdraft_limit: float = 0.0
    overdraft_currency: str | None = None
    blocked_balance: float = 0.0
    blocked_balance_currency: str | None = None
    debit_transaction_blocked: bool = False
    credit_transaction_blocked: bool = False


