from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.account_request import AccountCreateRequest
from app.service.account_service import AccountService


router = APIRouter(prefix="/account", tags=["Accounts"])

account_service = AccountService()


@router.post("")
def create_account(
        request: AccountCreateRequest,
        db: Session = Depends(get_db)
):
    return account_service.create_account(db, request)