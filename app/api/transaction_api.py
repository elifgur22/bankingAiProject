from datetime import datetime

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_current_user,
    get_idempotency_key,
    remember_response,
    replayed_response,
    require_roles
)
from app.database import get_db
from app.enum.transaction_type import TransactionType
from app.enum.user_role import UserRole
from app.schemas.monetary_transaction_request import MonetaryTransactionRequest
from app.schemas.responses import (
    ReversalResponse,
    TransactionHistoryResponse,
    TransactionResponse,
    TransferResponse
)
from app.schemas.transfer_request import TransferRequest
from app.service.monetary_transaction_service import MonetaryTransactionService
from app.service.transaction_history_service import TransactionHistoryService
from app.service.transaction_reversal_service import TransactionReversalService
from app.service.transfer_service import TransferService

router = APIRouter(prefix="/transactions", tags=["Transactions"])

monetary_transaction_service = MonetaryTransactionService()

transfer_service = TransferService()

transaction_history_service = TransactionHistoryService()

transaction_reversal_service = TransactionReversalService()


@router.post(
    "/deposit",
    response_model=TransactionResponse,
    status_code=201
)
def deposit(
        request: MonetaryTransactionRequest,
        http_request: Request,
        idempotency_key: str | None = Depends(get_idempotency_key),
        db: Session = Depends(get_db),
        _=Depends(get_current_user)
):
    cached = replayed_response(http_request, idempotency_key)

    if cached is not None:
        return cached

    transaction = monetary_transaction_service.deposit(db, request)

    return _remember(
        http_request,
        idempotency_key,
        TransactionResponse.model_validate(transaction)
    )


@router.post(
    "/withdraw",
    response_model=TransactionResponse,
    status_code=201
)
def withdraw(
        request: MonetaryTransactionRequest,
        http_request: Request,
        idempotency_key: str | None = Depends(get_idempotency_key),
        db: Session = Depends(get_db),
        _=Depends(get_current_user)
):
    cached = replayed_response(http_request, idempotency_key)

    if cached is not None:
        return cached

    transaction = monetary_transaction_service.withdraw(db, request)

    return _remember(
        http_request,
        idempotency_key,
        TransactionResponse.model_validate(transaction)
    )


@router.post(
    "/transfer",
    response_model=TransferResponse,
    status_code=201
)
def transfer(
        request: TransferRequest,
        http_request: Request,
        idempotency_key: str | None = Depends(get_idempotency_key),
        db: Session = Depends(get_db),
        _=Depends(get_current_user)
):
    cached = replayed_response(http_request, idempotency_key)

    if cached is not None:
        return cached

    source, target = transfer_service.transfer(db, request)

    response = TransferResponse(
        transfer_reference=source.transfer_reference,
        source_transaction=TransactionResponse.model_validate(source),
        target_transaction=TransactionResponse.model_validate(target)
    )

    return _remember(http_request, idempotency_key, response)


@router.get(
    "/account/{account_id}",
    response_model=TransactionHistoryResponse
)
def get_account_history(
        account_id: int,
        transaction_type: TransactionType | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        limit: int = Query(default=50, ge=1, le=200),
        offset: int = Query(default=0, ge=0),
        db: Session = Depends(get_db),
        _=Depends(get_current_user)
):
    items, total = transaction_history_service.get_account_history(
        db,
        account_id=account_id,
        transaction_type=transaction_type,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset
    )

    return TransactionHistoryResponse(
        account_id=account_id,
        total=total,
        limit=limit,
        offset=offset,
        items=[
            TransactionResponse.model_validate(item)
            for item in items
        ]
    )


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
        transaction_id: int,
        db: Session = Depends(get_db),
        _=Depends(get_current_user)
):
    transaction = transaction_history_service.get_required_transaction(
        db,
        transaction_id
    )

    return TransactionResponse.model_validate(transaction)


@router.post(
    "/{transaction_id}/reversal",
    response_model=ReversalResponse,
    status_code=201
)
def reverse_transaction(
        transaction_id: int,
        db: Session = Depends(get_db),
        _=Depends(require_roles(UserRole.ADMIN))
):
    reversals = transaction_reversal_service.reverse(db, transaction_id)

    return ReversalResponse(
        reversed_transaction_id=transaction_id,
        reversal_transactions=[
            TransactionResponse.model_validate(item)
            for item in reversals
        ]
    )


def _remember(http_request: Request, idempotency_key: str | None, response):
    remember_response(
        http_request,
        idempotency_key,
        response.model_dump(mode="json")
    )

    return response
