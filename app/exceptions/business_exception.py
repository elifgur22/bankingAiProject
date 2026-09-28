from enum import Enum


class BusinessException(Exception):
    """Raised when a business rule is violated.

    ``validation_rule`` is always a ValidationRule enum member exposing
    ``code``, ``message`` and ``http_status``.
    """

    def __init__(self, validation_rule: Enum):
        self.validation_rule = validation_rule

        super().__init__(validation_rule.message)

    @property
    def code(self) -> str:
        return self.validation_rule.code

    @property
    def message(self) -> str:
        return self.validation_rule.message

    @property
    def http_status(self) -> int:
        return getattr(self.validation_rule, "http_status", 400)
