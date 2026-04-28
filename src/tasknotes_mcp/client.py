"""Async HTTP client for the TaskNotes plugin API.

Thin wrapper. Each method maps to one endpoint we care about. We don't
try to model the full API — the OpenAPI spec at /api/docs is the source
of truth for anything not covered here.

Error handling philosophy:
  - HTTPStatusError surfaces with the response body when possible, so the
    MCP layer can return useful messages to the agent (and through it, the
    user) instead of opaque 500s.
  - Network errors (timeout, connection refused) raise TaskNotesUnreachable
    so the agent can suggest "is Obsidian running?" rather than retrying
    blindly.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from .config import Config

log = logging.getLogger(__name__)


class TaskNotesError(Exception):
    """Base exception for TaskNotes client errors."""


class TaskNotesUnreachable(TaskNotesError):
    """Raised when the API can't be reached at all (Obsidian closed,
    plugin disabled, wrong port). Distinct from API-level errors."""


class TaskNotesAPIError(TaskNotesError):
    """Raised when the API returns a non-2xx response."""

    def __init__(self, status_code: int, body: str):
        self.status_code = status_code
        self.body = body
        super().__init__(f"TaskNotes API returned {status_code}: {body}")


class TaskNotesClient:
    """Async client. Use as a context manager or share one instance across
    the MCP server's lifetime — httpx handles connection pooling."""

    def __init__(self, config: Config):
        self._config = config
        self._client = httpx.AsyncClient(
            base_url=config.api_url,
            headers=config.auth_header(),
            timeout=config.request_timeout_s,
        )

    async def __aenter__(self) -> "TaskNotesClient":
        return self

    async def __aexit__(self, *exc_info) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._client.aclose()

    # --- internal -----------------------------------------------------

    async def _request(
        self, method: str, path: str, *, json: dict | None = None
    ) -> dict[str, Any]:
        try:
            response = await self._client.request(method, path, json=json)
        except httpx.TimeoutException as e:
            raise TaskNotesUnreachable(
                f"Timed out after {self._config.request_timeout_s}s "
                f"talking to {self._config.api_url}. Is Obsidian running and the "
                f"TaskNotes HTTP API enabled?"
            ) from e
        except httpx.ConnectError as e:
            raise TaskNotesUnreachable(
                f"Could not connect to {self._config.api_url}. Is Obsidian "
                f"running and the TaskNotes HTTP API enabled on this port?"
            ) from e

        if response.status_code >= 400:
            # Try to surface the API's own error message; fall back to text.
            try:
                body_data = response.json()
                body = body_data.get("error") or body_data.get("message") or str(body_data)
            except Exception:
                body = response.text
            raise TaskNotesAPIError(response.status_code, body)

        # All TaskNotes endpoints return {"success": bool, "data": ...}
        envelope = response.json()
        if not envelope.get("success", False):
            raise TaskNotesAPIError(
                response.status_code,
                envelope.get("error", "API returned success=false"),
            )
        return envelope.get("data", {})

    # --- public endpoints ---------------------------------------------

    async def health(self) -> dict[str, Any]:
        """GET /api/health — liveness check; returns vault metadata."""
        return await self._request("GET", "/api/health")

    async def filter_options(self) -> dict[str, Any]:
        """GET /api/filter-options — returns valid statuses, priorities,
        and the existing contexts/projects/tags in this vault."""
        return await self._request("GET", "/api/filter-options")

    async def create_task(self, payload: dict[str, Any]) -> dict[str, Any]:
        """POST /api/tasks — create a single task."""
        return await self._request("POST", "/api/tasks", json=payload)

    async def list_tasks(
        self, *, completed: bool | None = None, limit: int = 20
    ) -> list[dict[str, Any]]:
        """GET /api/tasks — basic pagination. For filtering, use POST
        /api/tasks/query instead (not currently exposed)."""
        # Build query string carefully — the docs warn that filter params
        # on GET return 400. So we only ever send pagination params here.
        params: dict[str, str] = {"limit": str(limit)}
        if completed is not None:
            params["completed"] = str(completed).lower()
        # httpx accepts params kwarg, but our _request doesn't; build URL.
        query = "&".join(f"{k}={v}" for k, v in params.items())
        path = f"/api/tasks?{query}"
        data = await self._request("GET", path)
        # Endpoint returns {"items": [...], ...} based on observed shape;
        # tolerate both list and dict-with-items.
        if isinstance(data, list):
            return data
        return data.get("items", []) or data.get("tasks", [])
