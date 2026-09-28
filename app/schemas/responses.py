from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.domain.account_status import AccountStatus
from app.domain.account_type import AccountType
from app.enum.user_role import UserRole


class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_name: str | None = None
    account_number: str | None = None
    customer_id: int | None = None
    account_type: AccountType | None = None
    account_status: AccountStatus | None = None
    is_primary: bool | None = None
    account_email: str | None = None
    create_time: datetime | None = None


class AccountBalanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    account_id: int
    balance: float
    balance_currency: str | None = None
    overdraft_limit: float | None = None
    blocked_balance: float | None = None
    debit_transaction_blocked: bool | None = None
    credit_transaction_blocked: bool | None = None
    available_balance: float | None = None


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_id: int
    transaction_type: str
    direction: str | None = None
    amount: float
    currency: str | None = None
    branch: str | None = None
    description: str | None = None
    status: str | None = None
    related_account_id: int | None = None
    transfer_reference: str | None = None
    reversal_of_transaction_id: int | None = None
    risk_level: str | None = None
    risk_score: float | None = None
    fraud_score: float | None = None
    is_fraud_suspected: bool | None = None
    create_time: datetime | None = None


class TransferResponse(BaseModel):
    transfer_reference: str
    source_transaction: TransactionResponse
    target_transaction: TransactionResponse


class TransactionHistoryResponse(BaseModel):
    account_id: int
    total: int
    limit: int
    offset: int
    items: list[TransactionResponse]


class SundryBatchResponse(BaseModel):
    batch_reference: str
    item_count: int
    total_credit: float
    total_debit: float
    transactions: list[TransactionResponse]


class ReversalResponse(BaseModel):
    reversed_transaction_id: int
    reversal_transactions: list[TransactionResponse]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    role: UserRole


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: UserRole
    is_active: bool


class ErrorResponse(BaseModel):
    code: str
    message: str


class HealthResponse(BaseModel):
    status: str
    database: str
    redis: str
    risk_model: str
    environment: str
