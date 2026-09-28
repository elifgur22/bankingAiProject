from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_roles
from app.database import get_db
from app.enum.user_role import UserRole
from app.schemas.account_request import AccountCreateRequest
from app.schemas.responses import AccountBalanceResponse, AccountResponse
from app.service.account_balance_service import AccountBalanceService
from app.service.account_service import AccountService

router = APIRouter(prefix="/accounts", tags=["Accounts"])

account_service = AccountService()

account_balance_service = AccountBalanceService()


@router.post("", response_model=AccountResponse, status_code=201)
def create_account(
        request: AccountCreateRequest,
        db: Session = Depends(get_db),
        _=Depends(require_roles(UserRole.TELLER, UserRole.ADMIN))
):
    account = account_service.create_account(db, request)

    return AccountResponse.model_validate(account)


@router.get("/{account_id}", response_model=AccountResponse)
def get_account(
        account_id: int,
        db: Session = Depends(get_db),
        _=Depends(get_current_user)
):
    account = account_service.get_required_account(db, account_id)

    return AccountResponse.model_validate(account)


@router.get("/{account_id}/balance", response_model=AccountBalanceResponse)
def get_account_balance(
        account_id: int,
        db: Session = Depends(get_db),
        _=Depends(get_current_user)
):
    account_balance = account_service.get_account_balance(db, account_id)

    response = AccountBalanceResponse.model_validate(account_balance)

    response.available_balance = (
        account_balance_service.calculate_available_balance(account_balance)
    )

    return response
