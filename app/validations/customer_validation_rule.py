from enum import Enum


class CustomerValidationRule(Enum):

    CUSTOMER_NOT_FOUND = (
        "CUS_001",
        "Customer not found."
    )

    CUSTOMER_ALREADY_EXISTS = (
        "CUS_002",
        "Customer already exists."
    )

    CUSTOMER_NUMBER_CAN_NOT_BE_EMPTY = (
        "CUS_003",
        "Customer number can not be empty."
    )

    CUSTOMER_NAME_CAN_NOT_BE_EMPTY = (
        "CUS_004",
        "Customer name can not be empty."
    )

    CUSTOMER_IS_NOT_ACTIVE = (
        "CUS_005",
        "Customer is not active."
    )

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message