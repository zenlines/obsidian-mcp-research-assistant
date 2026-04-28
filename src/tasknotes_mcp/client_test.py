"""Smoke test: hit the live TaskNotes API and print results.

Run with:
    python -m tasknotes_mcp.client_test

Use this to verify your .env is correct and the API is reachable
before registering the MCP server with Claude Desktop.
"""

from __future__ import annotations

import asyncio
import json
import sys

from .client import TaskNotesAPIError, TaskNotesClient, TaskNotesUnreachable
from .config import Config


async def _run() -> int:
    config = Config.from_env()
    print(f"API URL:    {config.api_url}")
    print(f"Auth:       {'token set' if config.api_token else '(none)'}")
    print(f"Vault path: {config.vault_path}")
    print()

    async with TaskNotesClient(config) as client:
        # 1. Health
        print("--- /api/health ---")
        try:
            health = await client.health()
            print(json.dumps(health, indent=2))
        except (TaskNotesUnreachable, TaskNotesAPIError) as e:
            print(f"FAIL: {e}", file=sys.stderr)
            return 1

        # 2. Filter options
        print("\n--- /api/filter-options ---")
        try:
            options = await client.filter_options()
            # Print just the keys of interest, summarized.
            print("statuses:  ", [s.get("value") for s in options.get("statuses", [])])
            print("priorities:", [p.get("value") for p in options.get("priorities", [])])
            print("contexts:  ", options.get("contexts", []))
            print("projects:  ", options.get("projects", []))
            print("tags:      ", options.get("tags", []))
        except (TaskNotesUnreachable, TaskNotesAPIError) as e:
            print(f"FAIL: {e}", file=sys.stderr)
            return 1

    print("\nOK — API is reachable and responding.")
    return 0


def main() -> None:
    sys.exit(asyncio.run(_run()))


if __name__ == "__main__":
    main()
