from enum import Enum


class Currency(str, Enum):
    TRY = "TRY"
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
