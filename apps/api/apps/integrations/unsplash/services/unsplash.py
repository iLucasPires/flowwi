import hashlib
import json
import logging
from typing import Any
from urllib.parse import urlparse

import httpx
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

UNSPLASH_API_URL = "https://api.unsplash.com"
UNSPLASH_API_VERSION = "v1"
UNSPLASH_TIMEOUT_SECONDS = 10

CACHE_PREFIX = "unsplash"


class UnsplashNotConfiguredError(Exception):
    """Raised when UNSPLASH_ACCESS_KEY is missing from the environment."""


class UnsplashUnavailableError(Exception):
    """Raised when Unsplash failed and there is no cached copy to fall back on."""


class UnsplashService:
    """
    Read-only proxy for the Unsplash API.

    Every response is cached in Redis under two keys: the payload itself (kept for
    `UNSPLASH_CACHE_STALE_TTL`) and a short-lived freshness marker (`UNSPLASH_CACHE_TTL`).
    While the marker is alive nothing leaves the server; once it expires the payload is
    refetched, and if Unsplash is unreachable or the hourly quota is spent the stale
    payload is served instead of an error.
    """

    def __init__(self) -> None:
        self.access_key: str = settings.UNSPLASH_ACCESS_KEY
        self.fresh_ttl: int = settings.UNSPLASH_CACHE_TTL
        self.stale_ttl: int = settings.UNSPLASH_CACHE_STALE_TTL

    @property
    def is_configured(self) -> bool:
        return bool(self.access_key)

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def search_photos(
        self,
        query: str,
        page: int = 1,
        per_page: int = 24,
        orientation: str | None = "landscape",
    ) -> dict[str, Any]:
        """Search the Unsplash library. Returns `{results, total, total_pages}`."""
        params: dict[str, Any] = {
            "query": query,
            "page": page,
            "per_page": per_page,
            "content_filter": "high",
        }

        if orientation:
            params["orientation"] = orientation

        return self._get("/search/photos", params)

    def list_photos(
        self,
        page: int = 1,
        per_page: int = 24,
        order_by: str = "popular",
    ) -> list[dict[str, Any]]:
        """The default gallery shown before the user types anything."""
        return self._get(
            "/photos",
            {
                "page": page,
                "per_page": per_page,
                "order_by": order_by,
            },
        )

    def track_download(self, download_location: str) -> None:
        """
        Ping the photo's `download_location`, as the Unsplash API guidelines require
        whenever a user picks a photo. Never cached, and never fatal for the caller.
        """
        self._assert_configured()

        if not self.is_valid_download_location(download_location):
            raise ValueError("download_location must be an Unsplash API URL")

        try:
            with httpx.Client(timeout=UNSPLASH_TIMEOUT_SECONDS) as client:
                client.get(download_location, headers=self._headers())

        except httpx.HTTPError:
            logger.warning("Unsplash download tracking failed", exc_info=True)

    @staticmethod
    def is_valid_download_location(url: str) -> bool:
        """Guard against the endpoint being used to make the server call arbitrary hosts."""
        parsed = urlparse(url)

        return parsed.scheme == "https" and parsed.netloc == "api.unsplash.com"

    # -------------------------------------------------------------------------
    # Internals
    # -------------------------------------------------------------------------

    def _assert_configured(self) -> None:
        if not self.is_configured:
            raise UnsplashNotConfiguredError("UNSPLASH_ACCESS_KEY is not set")

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Client-ID {self.access_key}",
            "Accept-Version": UNSPLASH_API_VERSION,
        }

    def _cache_keys(self, path: str, params: dict[str, Any]) -> tuple[str, str]:
        raw = json.dumps([path, sorted(params.items())], default=str)
        digest = hashlib.sha256(raw.encode()).hexdigest()

        return f"{CACHE_PREFIX}:data:{digest}", f"{CACHE_PREFIX}:fresh:{digest}"

    def _get(self, path: str, params: dict[str, Any]) -> Any:
        self._assert_configured()

        data_key, fresh_key = self._cache_keys(path, params)
        cached = cache.get(data_key)

        if cached is not None and cache.get(fresh_key):
            return cached

        try:
            with httpx.Client(timeout=UNSPLASH_TIMEOUT_SECONDS) as client:
                response = client.get(
                    f"{UNSPLASH_API_URL}{path}",
                    params=params,
                    headers=self._headers(),
                )
                response.raise_for_status()
                payload = response.json()

        except (httpx.HTTPError, ValueError):
            logger.warning("Unsplash request to %s failed", path, exc_info=True)

            if cached is not None:
                return cached

            raise UnsplashUnavailableError(path) from None

        cache.set(data_key, payload, self.stale_ttl)
        cache.set(fresh_key, True, self.fresh_ttl)

        return payload
