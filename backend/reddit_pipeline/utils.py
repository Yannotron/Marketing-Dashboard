from __future__ import annotations

"""Utility helpers for retries, backoff, and JSON logging."""

import json
import logging
import random
import time
from functools import wraps
from typing import Any, Callable, Type, TypeVar


T = TypeVar("T")


def get_json_logger(name: str) -> logging.Logger:
    """Return a logger that emits structured JSON."""

    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()

        class JsonFormatter(logging.Formatter):
            def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
                payload = {
                    "level": record.levelname,
                    "name": record.name,
                    "message": record.getMessage(),
                    "time": int(time.time()),
                }
                if record.exc_info:
                    payload["exc_info"] = self.formatException(record.exc_info)
                return json.dumps(payload)

        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger


def retry_with_backoff(
    *,
    exceptions: tuple[Type[BaseException], ...] = (Exception,),
    max_attempts: int = 5,
    base_delay_seconds: float = 0.5,
    max_delay_seconds: float = 8.0,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Simple exponential backoff decorator with jitter.

    - Retries on specified exceptions (default: all Exceptions)
    - Uses exponential backoff with full jitter
    - Caps attempts and max delay
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            attempt = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:  # pragma: no cover - behaviour tested separately
                    attempt += 1
                    if attempt >= max_attempts:
                        raise
                    delay = min(max_delay_seconds, base_delay_seconds * (2 ** (attempt - 1)))
                    delay = random.uniform(0, delay)
                    time.sleep(delay)

        return wrapper

    return decorator


