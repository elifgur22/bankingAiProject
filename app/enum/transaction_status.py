from enum import Enum


class TransactionStatus(str, Enum):
    COMPLETED = "COMPLETED"
    REVERSED = "REVERSED"
    REVERSAL = "REVERSAL"
