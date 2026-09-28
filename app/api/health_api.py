from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.ai.prediction_service import PredictionService
from app.core.config import get_settings
from app.core.idempotency import get_idempotency_store
from app.database import get_db
from app.schemas.responses import HealthResponse

router = APIRouter(tags=["Health"])

prediction_service = PredictionService()


@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    settings = get_settings()

    database_status = _check_database(db)

    return HealthResponse(
        status="UP" if database_status == "UP" else "DEGRADED",
        database=database_status,
        redis="UP" if get_idempotency_store().enabled else "DISABLED",
        risk_model="LOADED" if prediction_service.available else "MISSING",
        environment=settings.environment
    )


def _check_database(db: Session) -> str:
    try:
        db.execute(text("SELECT 1"))

        return "UP"
    except Exception:
        return "DOWN"
