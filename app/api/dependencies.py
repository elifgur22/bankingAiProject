from collections.abc import Callable

from fastapi import Depends, Header, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.idempotency import IdempotencyStore, get_idempotency_store
from app.core.security import decode_access_token
from app.database import get_db
from app.domain.user import User
from app.enum.user_role import UserRole
from app.exceptions.business_exception import BusinessException
from app.service.auth_service import AuthService
from app.validations.auth_validation_rule import AuthValidationRule

bearer_scheme = HTTPBearer(auto_error=False)

auth_service = AuthService()


def get_current_user(
        credentials: HTTPAuthorizationCredentials | None = Depends(
            bearer_scheme
        ),
        db: Session = Depends(get_db)
) -> User:

    if credentials is None:
        raise BusinessException(AuthValidationRule.NOT_AUTHENTICATED)

    payload = decode_access_token(credentials.credentials)

    if payload is None or not payload.get("sub"):
        raise BusinessException(AuthValidationRule.INVALID_TOKEN)

    user = auth_service.get_user_by_username(db, payload["sub"])

    if user is None:
        raise BusinessException(AuthValidationRule.INVALID_TOKEN)

    if not user.is_active:
        raise BusinessException(AuthValidationRule.USER_IS_NOT_ACTIVE)

    return user


def require_roles(*allowed_roles: UserRole) -> Callable[..., User]:
    """Dependency factory for role based authorization."""

    def dependency(user: User = Depends(get_current_user)) -> User:
        if allowed_roles and user.role not in allowed_roles:
            raise BusinessException(
                AuthValidationRule.INSUFFICIENT_PERMISSIONS
            )

        return user

    return dependency


def get_idempotency_key(
        idempotency_key: str | None = Header(
            default=None,
            alias="Idempotency-Key",
            description=(
                "Optional replay guard. Retrying a money moving request "
                "with the same key returns the first response instead of "
                "moving money twice. Requires Redis."
            )
        )
) -> str | None:

    return idempotency_key


def replayed_response(
        request: Request,
        idempotency_key: str | None,
        store: IdempotencyStore | None = None
) -> dict | None:
    """Return the stored response for this key, if the call is a retry."""

    store = store or get_idempotency_store()

    if not idempotency_key or not store.enabled:
        return None

    cached = store.get(_scoped_key(request, idempotency_key))

    return cached


def remember_response(
        request: Request,
        idempotency_key: str | None,
        payload: dict,
        store: IdempotencyStore | None = None
) -> None:

    store = store or get_idempotency_store()

    if not idempotency_key or not store.enabled:
        return

    store.save(_scoped_key(request, idempotency_key), payload)


def _scoped_key(request: Request, idempotency_key: str) -> str:
    # Scoped per route so the same key on /deposit and /withdraw does not
    # collide.
    return f"{request.url.path}:{idempotency_key}"
