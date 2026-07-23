from enum import Enum


class AccountValidationRule(Enum):
    ACCOUNT_NOT_FOUND = "Account not found."
    ACCOUNT_BALANCE_NOT_FOUND = "Account balance not found."
    INSUFFICIENT_BALANCE = "Insufficient balance."
    DEBIT_TRANSACTION_BLOCKED = "Debit transactions are blocked."