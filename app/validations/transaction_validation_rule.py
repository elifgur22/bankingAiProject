from enum import Enum


class TransactionValidationRule(Enum):

    INVALID_TRANSACTION_AMOUNT = (
        "TRN_001",
        "Transaction amount must be greater than zero."
    )

    INVALID_TRANSACTION_TYPE = (
        "TRN_002",
        "Invalid transaction type."
    )

    UNSUPPORTED_CURRENCY = (
        "TRN_003",
        "Unsupported currency."
    )

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message