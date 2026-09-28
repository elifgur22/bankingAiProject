from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_roles
from app.database import get_db
from app.domain.user import User
from app.enum.user_role import UserRole
from app.schemas.auth_request import (
    UserCreateRequest,
    UserLoginRequest,
    UserRegisterRequest
)
from app.schemas.responses import TokenResponse, UserResponse
from app.service.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

auth_service = AuthService()


@router.post("/register", response_model=UserResponse, status_code=201)
def register(
        request: UserRegisterRequest,
        db: Session = Depends(get_db)
):
    """Public registration. Creates a CUSTOMER, except for the very first
    user of an empty installation, who becomes the bootstrap ADMIN."""

    return UserResponse.model_validate(auth_service.register(db, request))


@router.post("/users", response_model=UserResponse, status_code=201)
def create_user(
        request: UserCreateRequest,
        db: Session = Depends(get_db),
        _=Depends(require_roles(UserRole.ADMIN))
):
    """Administrative user creation with an explicit role."""

    return UserResponse.model_validate(auth_service.create_user(db, request))


@router.post("/login", response_model=TokenResponse)
def login(
        request: UserLoginRequest,
        db: Session = Depends(get_db)
):
    return auth_service.login(db, request)


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(user: User = Depends(get_current_user)):
    return UserResponse.model_validate(user)
