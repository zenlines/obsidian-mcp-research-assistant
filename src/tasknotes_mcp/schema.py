"""Pydantic models for TaskNotes task payloads.

These exist so that:
  1. Tool inputs from the MCP layer are validated before we hit the API.
  2. The agent gets clear schema info via tool docstrings.
  3. We have one place to evolve the schema if TaskNotes changes.

Field names match what the TaskNotes HTTP API accepts on POST /api/tasks.
The plugin's defaults are assumed (no field remapping in user settings).
"""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator

# Statuses and priorities discovered from /api/filter-options on a default
# install. If a user customizes these, the agent should call
# tasknotes_get_schema at session start and use what it returns instead of
# these literals. We keep the literals here for offline validation /
# documentation.
StatusLiteral = Literal["none", "open", "in-progress", "done"]
PriorityLiteral = Literal["none", "low", "normal", "high"]


class TaskCreateInput(BaseModel):
    """Input for creating a single task.

    Only `title` is required. Everything else is optional so the agent can
    propose minimal tasks for ambiguous items and richer tasks for clear
    ones.
    """

    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Short, action-oriented task title.",
    )
    status: StatusLiteral = Field(
        default="open",
        description="Task status. Defaults to 'open' for newly proposed tasks.",
    )
    priority: PriorityLiteral = Field(
        default="normal",
        description="Priority. Defaults to 'normal' unless urgency is signaled.",
    )
    due: date | None = Field(
        default=None,
        description="Due date (YYYY-MM-DD). Hard deadline.",
    )
    scheduled: date | None = Field(
        default=None,
        description="Scheduled date (YYYY-MM-DD). When you plan to work on it.",
    )
    contexts: list[str] = Field(
        default_factory=list,
        description=(
            "Free-form contexts, e.g. ['work', 'errands']. Grows organically; "
            "no fixed vocabulary."
        ),
    )
    projects: list[str] = Field(
        default_factory=list,
        description=(
            "Wiki-link strings to project notes, e.g. ['[[Recipe Book]]']. "
            "ALWAYS confirm with the user before populating this field."
        ),
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Tags (without leading #).",
    )
    time_estimate: int | None = Field(
        default=None,
        ge=1,
        description="Estimated minutes to complete.",
        alias="timeEstimate",
    )
    details: str | None = Field(
        default=None,
        description=(
            "Free-form markdown body of the note. Use for context, links, "
            "source URLs, or anything that doesn't fit in frontmatter."
        ),
    )

    model_config = {"populate_by_name": True}

    @field_validator("contexts", "tags", mode="before")
    @classmethod
    def _strip_leading_hashes(cls, v: list[str] | None) -> list[str]:
        """Tolerate '#tag' and 'tag' interchangeably."""
        if not v:
            return []
        return [item.lstrip("#").strip() for item in v if item and item.strip()]

    def to_api_payload(self) -> dict:
        """Convert to the JSON body the TaskNotes HTTP API expects.

        - Dates serialized as YYYY-MM-DD strings.
        - `details` mapped to the note body (separate from frontmatter).
        - `time_estimate` sent as `timeEstimate` (camelCase per API).
        - Empty lists and None values omitted to keep the payload tidy.
        """
        payload: dict = {"title": self.title}

        if self.status and self.status != "none":
            payload["status"] = self.status
        if self.priority and self.priority != "none":
            payload["priority"] = self.priority
        if self.due:
            payload["due"] = self.due.isoformat()
        if self.scheduled:
            payload["scheduled"] = self.scheduled.isoformat()
        if self.contexts:
            payload["contexts"] = self.contexts
        if self.projects:
            payload["projects"] = self.projects
        if self.tags:
            payload["tags"] = self.tags
        if self.time_estimate is not None:
            payload["timeEstimate"] = self.time_estimate
        if self.details:
            # The TaskNotes API uses 'details' for the markdown body on
            # create. Verified against the OpenAPI spec at /api/docs.
            payload["details"] = self.details

        return payload


class TaskCreateResult(BaseModel):
    """What we return to the agent after a successful create."""

    path: str = Field(..., description="Vault-relative path to the created note.")
    title: str
    summary: str = Field(
        ...,
        description="One-line summary of what was created, for the agent to relay.",
    )
