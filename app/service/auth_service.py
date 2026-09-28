from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.logging_config import get_logger
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password
)
from app.database import transactional
from app.domain.user import User
from app.exceptions.business_exception import BusinessException
from app.repository.user_repository import UserRepository
from app.schemas.auth_request import UserLoginRequest, UserRegisterRequest
from app.schemas.responses import TokenResponse
from app.validations.auth_validation_rule import AuthValidationRule

logger = get_logger(__name__)


class AuthService:

    def __init__(self, user_repository: UserRepository | None = None):
        self.user_repository = user_repository or UserRepository()

    def register(self, db: Session, request: UserRegisterRequest) -> User:
        with transactional(db):
            existing = self.user_repository.find_by_username(
                db,
                request.username
            )

            if existing is not None:
                raise BusinessException(
                    AuthValidationRule.USERNAME_ALREADY_EXISTS
                )

            user = self.user_repository.save(
                db,
                User(
                    username=request.username,
                    hashed_password=hash_password(request.password),
                    role=request.role,
                    is_active=True
                )
            )

        logger.info("USER_REGISTERED username=%s role=%s",
                    user.username, user.role)

        return user

    def login(self, db: Session, request: UserLoginRequest) -> TokenResponse:
        user = self.user_repository.find_by_username(db, request.username)

        if user is None or not verify_password(
            request.password,
            user.hashed_password
        ):
            raise BusinessException(AuthValidationRule.INVALID_CREDENTIALS)

        if not user.is_active:
            raise BusinessException(AuthValidationRule.USER_IS_NOT_ACTIVE)

        settings = get_settings()

        role_value = getattr(user.role, "value", user.role)

        return TokenResponse(
            access_token=create_access_token(
                subject=user.username,
                role=role_value
            ),
            expires_in_minutes=settings.jwt_access_token_expire_minutes,
            role=user.role
        )

    def get_user_by_username(self, db: Session, username: str) -> User | None:
        return self.user_repository.find_by_username(db, username)
