from pydantic import BaseModel, Field, model_validator

from app.enum.currency import Currency


class TransferRequest(BaseModel):
    source_account_id: int = Field(gt=0)

    target_account_id: int = Field(gt=0)

    amount: float = Field(gt=0)

    currency: Currency

    branch: str = Field(min_length=1, max_length=64)

    description: str | None = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def validate_accounts_differ(self) -> "TransferRequest":
        if self.source_account_id == self.target_account_id:
            raise ValueError(
                "Source and target accounts must be different."
            )

        return self
