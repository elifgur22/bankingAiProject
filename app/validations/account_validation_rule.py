from enum import Enum


class AccountValidationRule(Enum):

    ACCOUNT_NOT_FOUND = (
        "ACC_001",
        "Account not found."
    )

    ACCOUNT_BALANCE_NOT_FOUND = (
        "ACC_002",
        "Account balance not found."
    )

    INSUFFICIENT_BALANCE = (
        "ACC_003",
        "Insufficient balance."
    )

    DEBIT_TRANSACTION_BLOCKED = (
        "ACC_004",
        "Debit transactions are blocked."
    )

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message