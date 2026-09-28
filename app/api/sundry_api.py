from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import require_roles
from app.database import get_db
from app.enum.transaction_direction import TransactionDirection
from app.enum.user_role import UserRole
from app.schemas.responses import SundryBatchResponse, TransactionResponse
from app.schemas.sundry_request import (
    SundryBatchRequest,
    SundryTransactionRequest
)
from app.service.sundry_service import SundryService

router = APIRouter(prefix="/sundry", tags=["Sundry"])

sundry_service = SundryService()


@router.post("", response_model=TransactionResponse, status_code=201)
def create_sundry_transaction(
        request: SundryTransactionRequest,
        db: Session = Depends(get_db),
        _=Depends(require_roles(UserRole.TELLER, UserRole.ADMIN))
):
    transaction = sundry_service.create_sundry_transaction(db, request)

    return TransactionResponse.model_validate(transaction)


@router.post("/batch", response_model=SundryBatchResponse, status_code=201)
def create_sundry_batch(
        request: SundryBatchRequest,
        db: Session = Depends(get_db),
        _=Depends(require_roles(UserRole.TELLER, UserRole.ADMIN))
):
    batch_reference, transactions = sundry_service.create_sundry_batch(
        db,
        request
    )

    return SundryBatchResponse(
        batch_reference=batch_reference,
        item_count=len(transactions),
        total_credit=_total(transactions, TransactionDirection.CREDIT),
        total_debit=_total(transactions, TransactionDirection.DEBIT),
        transactions=[
            TransactionResponse.model_validate(transaction)
            for transaction in transactions
        ]
    )


def _total(transactions: list, direction: TransactionDirection) -> float:
    return round(
        sum(
            transaction.amount
            for transaction in transactions
            if transaction.direction == direction.value
        ),
        2
    )
