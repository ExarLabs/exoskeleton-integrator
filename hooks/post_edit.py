#!/usr/bin/env python3
"""PostToolUse hook (Write|Edit|MultiEdit): remind the agent when an edit needs a migrate.

The most common Frappe slip: a DocType JSON or hooks.py changes and nobody runs
`bench migrate`, so the next request fails on a missing column or an old hook.
"""

from __future__ import annotations

import json
import re
import sys

RULES = [
    (re.compile(r"/doctype/[^/]+/[^/]+\.json$"),
     "A DocType JSON changed: run `bench --site <site> migrate` before testing, and include it in the plan's rollback."),
    (re.compile(r"/hooks\.py$"),
     "hooks.py changed: run `bench --site <site> migrate` (and `bench --site <site> clear-cache`) before testing."),
    (re.compile(r"/patches\.txt$"),
     "patches.txt changed: the patch runs once per site on the next migrate; make it safe to run twice."),
    (re.compile(r"/fixtures/[^/]+\.json$"),
     "A fixture changed: it is imported on the next migrate and overwrites the matching records on every site that installs the app."),
    (re.compile(r"/(report|page|print_format|workspace)/[^/]+/[^/]+\.json$"),
     "A standard record JSON changed: it is synced on the next migrate."),
]


def message_for(path: str) -> str | None:
    norm = path.replace("\\", "/")
    for pattern, text in RULES:
        if pattern.search(norm):
            return text
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0
    tool_input = payload.get("tool_input") or {}
    path = tool_input.get("file_path") or tool_input.get("path") or ""
    text = message_for(path) if path else None
    if text:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": f"Exoskeleton Integrator: {text}",
        }}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
