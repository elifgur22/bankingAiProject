from pydantic import BaseModel, EmailStr, Field

from app.domain.account_status import AccountStatus
from app.domain.account_type import AccountType
from app.enum.currency import Currency


class AccountCreateRequest(BaseModel):
    account_name: str = Field(min_length=1, max_length=120)
    customer_id: int = Field(gt=0)
    account_type: AccountType
    account_status: AccountStatus = AccountStatus.ACTIVE
    account_number: str = Field(min_length=4, max_length=34)
    is_primary: bool = False
    account_email: EmailStr | None = None

    balance: float = Field(default=0.0, ge=0)
    balance_currency: Currency
    overdraft_limit: float = Field(default=0.0, ge=0)
    overdraft_currency: Currency | None = None
    blocked_balance: float = Field(default=0.0, ge=0)
    blocked_balance_currency: Currency | None = None
    debit_transaction_blocked: bool = False
    credit_transaction_blocked: bool = False
