"""MCP server exposing TaskNotes operations as tools for Claude.

Run via:
    python -m tasknotes_mcp.server

Or registered in Claude Desktop's config (see docs/claude-desktop-config.md).

Tool design notes:
  - Tool docstrings are what the agent sees as descriptions. Keep them
    behavioral ("when to use this") rather than implementation-detail
    ("calls POST /api/tasks").
  - Errors are returned as tool results with isError=True so the agent can
    relay them to the user instead of crashing the conversation.
  - All tools are async; the FastMCP runtime handles event-loop integration.
"""

from __future__ import annotations

import logging
from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic import ValidationError

from .client import TaskNotesAPIError, TaskNotesClient, TaskNotesUnreachable
from .config import Config
from .schema import TaskCreateInput, TaskCreateResult

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("tasknotes-mcp")

# Module-level singletons. FastMCP runs in a single process; sharing one
# client instance keeps the connection pool warm.
_config = Config.from_env()
_client = TaskNotesClient(_config)

mcp = FastMCP("tasknotes-agent")


@mcp.tool()
async def tasknotes_health() -> dict[str, Any]:
    """Verify the TaskNotes HTTP API is reachable.

    Use this once at the start of a session, or if a later tool call fails
    with a connection error. Returns vault metadata (name, path) on success.
    If this fails, the user likely needs to open Obsidian or re-enable the
    HTTP API in plugin settings.
    """
    try:
        return await _client.health()
    except TaskNotesUnreachable as e:
        return {"error": "unreachable", "message": str(e)}
    except TaskNotesAPIError as e:
        return {"error": "api_error", "status": e.status_code, "message": e.body}


@mcp.tool()
async def tasknotes_get_schema() -> dict[str, Any]:
    """Get the valid statuses, priorities, and existing contexts/projects/tags.

    Call this once at the start of a task-creation session. The returned
    contexts/projects/tags reflect what the user has already used in their
    vault — useful for staying consistent with their existing taxonomy
    rather than inventing new categories. Statuses and priorities are the
    only fixed-vocabulary fields; everything else grows organically.
    """
    try:
        return await _client.filter_options()
    except TaskNotesUnreachable as e:
        return {"error": "unreachable", "message": str(e)}
    except TaskNotesAPIError as e:
        return {"error": "api_error", "status": e.status_code, "message": e.body}


@mcp.tool()
async def tasknotes_create_task(
    title: str,
    status: str = "open",
    priority: str = "normal",
    due: str | None = None,
    scheduled: str | None = None,
    contexts: list[str] | None = None,
    projects: list[str] | None = None,
    tags: list[str] | None = None,
    time_estimate: int | None = None,
    details: str | None = None,
) -> dict[str, Any]:
    """Create one TaskNote in the user's Obsidian vault.

    Use this AFTER the user has explicitly approved a proposed task. Do not
    call this speculatively or in batch without per-task approval (or batch
    approval the user has confirmed).

    Parameters:
      title: Short, action-oriented (e.g. "Email nschieber harbor setup notes").
        Required. Keep under ~80 chars when possible for readability.
      status: One of "none", "open", "in-progress", "done". Default "open".
      priority: One of "none", "low", "normal", "high". Default "normal".
        Only escalate to "high" when the user signals urgency.
      due: Hard deadline as YYYY-MM-DD. Omit if not specified.
      scheduled: Planned work date as YYYY-MM-DD. Distinct from due.
      contexts: Free-form tags like ["work", "errands", "learning"].
      projects: Wiki-link strings like ["[[ELM Open Source]]"]. ALWAYS
        confirm with the user before populating this — silent
        miscategorization is worse than no link.
      tags: Plain tags (no leading #).
      time_estimate: Estimated minutes. Use only when the user gives a clear
        estimate; do not guess.
      details: Markdown body for the note. Good for source URLs, context
        from the conversation, or anything that doesn't fit in frontmatter.

    Returns:
      On success: {"path": ..., "title": ..., "summary": ...}
      On failure: {"error": ..., "message": ...}
    """
    try:
        validated = TaskCreateInput(
            title=title,
            status=status,  # type: ignore[arg-type]
            priority=priority,  # type: ignore[arg-type]
            due=due,  # type: ignore[arg-type]
            scheduled=scheduled,  # type: ignore[arg-type]
            contexts=contexts or [],
            projects=projects or [],
            tags=tags or [],
            time_estimate=time_estimate,
            details=details,
        )
    except ValidationError as e:
        return {"error": "invalid_input", "message": str(e)}

    try:
        data = await _client.create_task(validated.to_api_payload())
    except TaskNotesUnreachable as e:
        return {"error": "unreachable", "message": str(e)}
    except TaskNotesAPIError as e:
        return {"error": "api_error", "status": e.status_code, "message": e.body}

    # The API returns the full task object including its vault path.
    # The exact key may be `path`, `id`, or `file` depending on plugin
    # version — try the common ones in order.
    path = data.get("path") or data.get("id") or data.get("file") or "(unknown path)"

    parts = [f"Created: {validated.title}"]
    if validated.due:
        parts.append(f"due {validated.due.isoformat()}")
    if validated.priority != "normal" and validated.priority != "none":
        parts.append(f"priority={validated.priority}")
    if validated.contexts:
        parts.append(f"contexts={','.join(validated.contexts)}")
    if validated.projects:
        parts.append(f"projects={','.join(validated.projects)}")
    summary = " | ".join(parts)

    result = TaskCreateResult(path=path, title=validated.title, summary=summary)
    return result.model_dump()


@mcp.tool()
async def tasknotes_list_recent(limit: int = 10) -> dict[str, Any]:
    """List recently created/active tasks. Useful for dedup checks before
    creating a new task that might already exist.

    Returns up to `limit` recent active tasks (default 10, max 50).
    """
    limit = max(1, min(limit, 50))
    try:
        items = await _client.list_tasks(completed=False, limit=limit)
    except TaskNotesUnreachable as e:
        return {"error": "unreachable", "message": str(e)}
    except TaskNotesAPIError as e:
        return {"error": "api_error", "status": e.status_code, "message": e.body}

    # Trim to fields useful for dedup; full payload is verbose.
    trimmed = [
        {
            "title": t.get("title"),
            "path": t.get("path") or t.get("id"),
            "status": t.get("status"),
            "due": t.get("due"),
        }
        for t in items
    ]
    return {"count": len(trimmed), "tasks": trimmed}


def main() -> None:
    """Entrypoint for `python -m tasknotes_mcp.server` and the
    `tasknotes-mcp` console script."""
    log.info("Starting tasknotes-mcp; API URL=%s", _config.api_url)
    mcp.run()


if __name__ == "__main__":
    main()
