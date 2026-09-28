from collections.abc import Generator, Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.core.config import get_settings

settings = get_settings()

DATABASE_URL = settings.database_url

_connect_args = (
    {"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite")
    else {}
)

engine = create_engine(
    DATABASE_URL,
    echo=settings.sql_echo,
    connect_args=_connect_args
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@contextmanager
def transactional(db: Session) -> Iterator[Session]:
    """Commit once per business operation, roll back on any failure.

    Repositories only add/flush; the service layer owns the transaction
    boundary so multi-step operations such as transfers stay atomic.
    """
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
