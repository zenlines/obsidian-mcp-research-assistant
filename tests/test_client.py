from __future__ import annotations

import pytest
import respx
from httpx import Response

from tasknotes_mcp.client import TaskNotesAPIError, TaskNotesClient, TaskNotesUnreachable
from tasknotes_mcp.config import Config

BASE_URL = "http://localhost:8080"


def _config(**overrides) -> Config:
    return Config(
        api_url=overrides.get("api_url", BASE_URL),
        api_token=overrides.get("api_token", "test-token"),
        vault_path=None,
        request_timeout_s=5.0,
    )


# ---------------------------------------------------------------------------
# health()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@respx.mock
async def test_health_success():
    respx.get(f"{BASE_URL}/api/health").mock(
        return_value=Response(
            200,
            json={"success": True, "data": {"status": "ok", "vault": {"name": "my-vault"}}},
        )
    )
    async with TaskNotesClient(_config()) as client:
        result = await client.health()
    assert result["status"] == "ok"
    assert result["vault"]["name"] == "my-vault"


@pytest.mark.asyncio
@respx.mock
async def test_health_api_error_raises():
    respx.get(f"{BASE_URL}/api/health").mock(
        return_value=Response(401, json={"error": "Unauthorized"})
    )
    async with TaskNotesClient(_config()) as client:
        with pytest.raises(TaskNotesAPIError) as exc_info:
            await client.health()
    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
@respx.mock
async def test_health_unreachable_raises(monkeypatch):
    import httpx

    respx.get(f"{BASE_URL}/api/health").mock(side_effect=httpx.ConnectError("refused"))
    async with TaskNotesClient(_config()) as client:
        with pytest.raises(TaskNotesUnreachable):
            await client.health()


# ---------------------------------------------------------------------------
# filter_options()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@respx.mock
async def test_filter_options_returns_data():
    respx.get(f"{BASE_URL}/api/filter-options").mock(
        return_value=Response(
            200,
            json={
                "success": True,
                "data": {
                    "statuses": [{"value": "open"}, {"value": "done"}],
                    "priorities": [{"value": "normal"}, {"value": "high"}],
                    "contexts": [],
                    "projects": [],
                    "tags": [],
                },
            },
        )
    )
    async with TaskNotesClient(_config()) as client:
        result = await client.filter_options()
    assert len(result["statuses"]) == 2
    assert result["statuses"][0]["value"] == "open"


# ---------------------------------------------------------------------------
# create_task()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@respx.mock
async def test_create_task_success():
    respx.post(f"{BASE_URL}/api/tasks").mock(
        return_value=Response(
            201,
            json={
                "success": True,
                "data": {
                    "path": "TaskNotes/Tasks/2026-05-16-buy-milk.md",
                    "title": "Buy milk",
                },
            },
        )
    )
    async with TaskNotesClient(_config()) as client:
        result = await client.create_task({"title": "Buy milk", "status": "open"})
    assert result["path"] == "TaskNotes/Tasks/2026-05-16-buy-milk.md"


@pytest.mark.asyncio
@respx.mock
async def test_create_task_api_error_raises():
    respx.post(f"{BASE_URL}/api/tasks").mock(
        return_value=Response(
            400,
            json={"error": "Invalid status value"},
        )
    )
    async with TaskNotesClient(_config()) as client:
        with pytest.raises(TaskNotesAPIError) as exc_info:
            await client.create_task({"title": "X", "status": "bad-status"})
    assert exc_info.value.status_code == 400
    assert "Invalid status" in exc_info.value.body


# ---------------------------------------------------------------------------
# Auth header
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@respx.mock
async def test_auth_header_sent_when_token_set():
    route = respx.get(f"{BASE_URL}/api/health").mock(
        return_value=Response(
            200,
            json={"success": True, "data": {"status": "ok"}},
        )
    )
    async with TaskNotesClient(_config(api_token="secret-token")) as client:
        await client.health()
    sent_headers = route.calls[0].request.headers
    assert sent_headers.get("authorization") == "Bearer secret-token"


@pytest.mark.asyncio
@respx.mock
async def test_no_auth_header_when_no_token():
    route = respx.get(f"{BASE_URL}/api/health").mock(
        return_value=Response(
            200,
            json={"success": True, "data": {"status": "ok"}},
        )
    )
    async with TaskNotesClient(_config(api_token=None)) as client:
        await client.health()
    sent_headers = route.calls[0].request.headers
    assert "authorization" not in sent_headers
