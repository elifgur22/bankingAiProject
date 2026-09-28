from enum import Enum


class AccountValidationRule(Enum):

    ACCOUNT_NOT_FOUND = (
        "ACC_001",
        "Account not found.",
        404
    )

    ACCOUNT_BALANCE_NOT_FOUND = (
        "ACC_002",
        "Account balance not found.",
        404
    )

    INSUFFICIENT_BALANCE = (
        "ACC_003",
        "Insufficient balance."
    )

    DEBIT_TRANSACTION_BLOCKED = (
        "ACC_004",
        "Debit transactions are blocked."
    )

    CREDIT_TRANSACTION_BLOCKED = (
        "ACC_005",
        "Credit transactions are blocked."
    )

    ACCOUNT_IS_NOT_ACTIVE = (
        "ACC_006",
        "Account is not active."
    )

    ACCOUNT_NUMBER_ALREADY_EXISTS = (
        "ACC_007",
        "Account number already exists.",
        409
    )

    CURRENCY_MISMATCH = (
        "ACC_008",
        "Account currency does not match the transaction currency."
    )

    def __init__(self, code: str, message: str, http_status: int = 400):
        self.code = code
        self.message = message
        self.http_status = http_status
