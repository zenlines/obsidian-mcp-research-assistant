"""Configuration for the TaskNotes MCP server.

All settings are env-driven. This makes local-dev and future remote
deployment differ only by environment, not by code path. .env files are
loaded automatically when present (local dev); in deployed environments,
real env vars take precedence.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Load .env if present. Never raises if the file is missing.
load_dotenv()


@dataclass(frozen=True)
class Config:
    api_url: str
    api_token: str | None
    vault_path: Path | None
    request_timeout_s: float

    @classmethod
    def from_env(cls) -> "Config":
        api_url = os.getenv("TASKNOTES_API_URL", "http://localhost:8080").rstrip("/")
        api_token = os.getenv("TASKNOTES_API_TOKEN") or None

        vault_str = os.getenv("TASKNOTES_VAULT_PATH")
        vault_path = Path(vault_str).expanduser() if vault_str else None

        timeout = float(os.getenv("TASKNOTES_REQUEST_TIMEOUT", "15"))

        return cls(
            api_url=api_url,
            api_token=api_token,
            vault_path=vault_path,
            request_timeout_s=timeout,
        )

    def auth_header(self) -> dict[str, str]:
        """Bearer auth header. Returns empty dict if no token is set
        (TaskNotes accepts unauthenticated requests in that case)."""
        if not self.api_token:
            return {}
        return {"Authorization": f"Bearer {self.api_token}"}
