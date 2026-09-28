import json

from app.core.config import get_settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

_KEY_PREFIX = "banking:idempotency:"


class IdempotencyStore:
    """Redis backed replay guard for money moving endpoints.

    A retried POST (network timeout, impatient client, at-least-once
    message delivery) must not move money twice. The first request stores
    its response under the caller supplied ``Idempotency-Key``; retries with
    the same key get that stored response back instead of a second transfer.

    Redis is optional: when ``redis_url`` is unset the store is disabled and
    every request is processed normally.
    """

    def __init__(self, client=None):
        settings = get_settings()

        self.ttl_seconds = settings.idempotency_ttl_seconds
        self.client = client

        if self.client is None and settings.redis_url:
            self.client = self._build_client(settings.redis_url)

    @staticmethod
    def _build_client(redis_url: str):
        try:
            import redis

            client = redis.Redis.from_url(
                redis_url,
                decode_responses=True
            )

            client.ping()

            return client
        except Exception as error:
            logger.warning(
                "Redis unavailable at %s, idempotency disabled (%s)",
                redis_url,
                error
            )

            return None

    @property
    def enabled(self) -> bool:
        return self.client is not None

    def get(self, key: str) -> dict | None:
        if not self.enabled or not key:
            return None

        stored = self.client.get(_KEY_PREFIX + key)

        if stored is None:
            return None

        return json.loads(stored)

    def save(self, key: str, response: dict) -> None:
        if not self.enabled or not key:
            return

        self.client.set(
            _KEY_PREFIX + key,
            json.dumps(response, default=str),
            ex=self.ttl_seconds
        )


_store: IdempotencyStore | None = None


def get_idempotency_store() -> IdempotencyStore:
    global _store

    if _store is None:
        _store = IdempotencyStore()

    return _store
