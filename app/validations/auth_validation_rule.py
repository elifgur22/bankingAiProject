from enum import Enum


class AuthValidationRule(Enum):

    USERNAME_ALREADY_EXISTS = (
        "AUT_001",
        "Username already exists.",
        409
    )

    INVALID_CREDENTIALS = (
        "AUT_002",
        "Invalid username or password.",
        401
    )

    NOT_AUTHENTICATED = (
        "AUT_003",
        "Authentication required.",
        401
    )

    INVALID_TOKEN = (
        "AUT_004",
        "Invalid or expired access token.",
        401
    )

    INSUFFICIENT_PERMISSIONS = (
        "AUT_005",
        "The current role is not allowed to perform this operation.",
        403
    )

    USER_IS_NOT_ACTIVE = (
        "AUT_006",
        "User is not active.",
        403
    )

    def __init__(self, code: str, message: str, http_status: int = 400):
        self.code = code
        self.message = message
        self.http_status = http_status
