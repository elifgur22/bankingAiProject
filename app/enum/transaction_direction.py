from enum import Enum


class TransactionDirection(str, Enum):
    """Direction of a sundry (bank internal) posting on a customer account."""

    CREDIT = "CREDIT"
    DEBIT = "DEBIT"
