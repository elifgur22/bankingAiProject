import logging
from logging.config import dictConfig

from app.core.config import get_settings

_LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)


def configure_logging() -> None:
    settings = get_settings()

    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": _LOG_FORMAT
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "level": settings.log_level
            }
        },
        "loggers": {
            "app": {
                "handlers": ["console"],
                "level": settings.log_level,
                "propagate": False
            },
            "uvicorn.error": {
                "handlers": ["console"],
                "level": settings.log_level,
                "propagate": False
            },
            "uvicorn.access": {
                "handlers": ["console"],
                "level": settings.log_level,
                "propagate": False
            }
        },
        "root": {
            "handlers": ["console"],
            "level": "WARNING"
        }
    })


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
