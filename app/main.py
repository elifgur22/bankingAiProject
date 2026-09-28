import time
import uuid

from fastapi import FastAPI, Request

from app.api.account_api import router as account_router
from app.api.auth_api import router as auth_router
from app.api.health_api import router as health_router
from app.api.sundry_api import router as sundry_router
from app.api.transaction_api import router as transaction_router
from app.core.config import get_settings
from app.core.logging_config import configure_logging, get_logger
from app.database import Base, engine
from app.exceptions.exception_handlers import register_exception_handlers

# Imported for their side effect: registering the tables on Base.metadata.
from app.domain.account import Account  # noqa: F401
from app.domain.account_balance import AccountBalance  # noqa: F401
from app.domain.customer import Customer  # noqa: F401
from app.domain.monetary_transaction import MonetaryTransaction  # noqa: F401
from app.domain.user import User  # noqa: F401

configure_logging()

logger = get_logger(__name__)

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description=(
        "Layered banking backend with an educational machine learning "
        "risk and fraud scoring pipeline."
    ),
    version="1.0.0"
)

register_exception_handlers(app)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(account_router)
app.include_router(transaction_router)
app.include_router(sundry_router)

Base.metadata.create_all(engine)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = uuid.uuid4().hex[:12]
    started_at = time.perf_counter()

    response = await call_next(request)

    duration_ms = (time.perf_counter() - started_at) * 1000

    logger.info(
        "%s %s -> %s (%.1f ms) request_id=%s",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
        request_id
    )

    response.headers["X-Request-Id"] = request_id

    return response


@app.get("/", tags=["Health"])
def root():
    return {
        "service": settings.app_name,
        "status": "running",
        "docs": "/docs"
    }
