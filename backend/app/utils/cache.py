"""
AgriVision AI — In-memory cache utility.

Provides a simple TTL-based cache to avoid hammering external APIs with
identical requests (e.g. weather lookups for the same city).

For production deployments, replace with a Redis-backed cache.
"""

import asyncio
import time
from collections.abc import Callable, Awaitable
from typing import Any


class TTLCache:
    """Thread-safe (asyncio-safe) in-memory key-value cache with TTL."""

    def __init__(self, ttl: int = 300) -> None:
        self._ttl = ttl
        self._store: dict[str, tuple[Any, float]] = {}

    def get(self, key: str) -> Any | None:
        """Return cached value or None if missing / expired."""
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if time.monotonic() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        """Store a value with the configured TTL."""
        self._store[key] = (value, time.monotonic() + self._ttl)

    def delete(self, key: str) -> None:
        """Explicitly evict a key."""
        self._store.pop(key, None)

    def clear(self) -> None:
        """Flush the entire cache."""
        self._store.clear()

    async def get_or_set(
        self,
        key: str,
        factory: Callable[[], Awaitable[Any]],
    ) -> Any:
        """
        Return the cached value for *key*, or call *factory* to produce and
        cache a fresh value.

        Args:
            key: Cache key.
            factory: Async callable that produces the value on a cache miss.
        """
        cached = self.get(key)
        if cached is not None:
            return cached
        value = await factory()
        self.set(key, value)
        return value


# Module-level singleton — shared across all requests within the same worker.
default_cache = TTLCache(ttl=300)
