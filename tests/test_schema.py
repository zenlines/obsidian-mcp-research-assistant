from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from tasknotes_mcp.schema import TaskCreateInput


class TestTaskCreateInput:
    def test_minimal_task_only_title(self):
        task = TaskCreateInput(title="Test task")
        payload = task.to_api_payload()
        assert payload == {
            "title": "Test task",
            "status": "open",
            "priority": "normal",
        }

    def test_full_task_serializes_dates_as_iso(self):
        task = TaskCreateInput(
            title="Full task",
            priority="high",
            due=date(2026, 5, 1),
            scheduled=date(2026, 4, 30),
            contexts=["work", "urgent"],
            projects=["[[Recipe Book]]"],
            tags=["followup"],
            time_estimate=60,
            details="Some context here.",
        )
        payload = task.to_api_payload()
        assert payload["due"] == "2026-05-01"
        assert payload["scheduled"] == "2026-04-30"
        assert payload["timeEstimate"] == 60
        assert payload["projects"] == ["[[Recipe Book]]"]
        assert payload["details"] == "Some context here."

    def test_none_status_and_priority_omitted(self):
        """The 'none' value is a real status/priority but adds noise to
        the payload; we omit it so the plugin uses its default."""
        task = TaskCreateInput(title="X", status="none", priority="none")
        payload = task.to_api_payload()
        assert "status" not in payload
        assert "priority" not in payload

    def test_strips_leading_hashes_from_contexts_and_tags(self):
        task = TaskCreateInput(title="X", contexts=["#work"], tags=["#followup"])
        payload = task.to_api_payload()
        assert payload["contexts"] == ["work"]
        assert payload["tags"] == ["followup"]

    def test_empty_lists_are_omitted(self):
        task = TaskCreateInput(title="X", contexts=[], projects=[], tags=[])
        payload = task.to_api_payload()
        assert "contexts" not in payload
        assert "projects" not in payload
        assert "tags" not in payload

    def test_invalid_status_rejected(self):
        with pytest.raises(ValidationError):
            TaskCreateInput(title="X", status="not-a-status")  # type: ignore[arg-type]

    def test_invalid_priority_rejected(self):
        with pytest.raises(ValidationError):
            TaskCreateInput(title="X", priority="urgent")  # type: ignore[arg-type]

    def test_empty_title_rejected(self):
        with pytest.raises(ValidationError):
            TaskCreateInput(title="")

    def test_negative_time_estimate_rejected(self):
        with pytest.raises(ValidationError):
            TaskCreateInput(title="X", time_estimate=0)