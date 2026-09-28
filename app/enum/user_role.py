from enum import Enum


class UserRole(str, Enum):
    """Role based authorization levels.

    CUSTOMER: may read and move money on accounts.
    TELLER:   may additionally run sundry postings and batches.
    ADMIN:    may additionally reverse transactions.
    """

    CUSTOMER = "CUSTOMER"
    TELLER = "TELLER"
    ADMIN = "ADMIN"
