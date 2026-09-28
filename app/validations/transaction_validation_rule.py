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

    TRANSACTION_NOT_FOUND = (
        "TRN_004",
        "Transaction not found.",
        404
    )

    SAME_SOURCE_AND_TARGET_ACCOUNT = (
        "TRN_005",
        "Source and target accounts must be different."
    )

    TRANSACTION_ALREADY_REVERSED = (
        "TRN_006",
        "Transaction is already reversed.",
        409
    )

    TRANSACTION_NOT_REVERSIBLE = (
        "TRN_007",
        "Only completed deposit, withdraw, transfer or sundry "
        "transactions can be reversed."
    )

    EMPTY_SUNDRY_BATCH = (
        "TRN_008",
        "Sundry batch must contain at least one item."
    )

    SUNDRY_BATCH_TOO_LARGE = (
        "TRN_009",
        "Sundry batch exceeds the maximum allowed item count."
    )

    def __init__(self, code: str, message: str, http_status: int = 400):
        self.code = code
        self.message = message
        self.http_status = http_status
