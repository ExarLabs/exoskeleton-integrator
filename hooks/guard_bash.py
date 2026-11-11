#!/usr/bin/env python3
"""PreToolUse hook (Bash): ask a human before destructive or live-site commands.

It does not block: it turns the command into a confirmation prompt with the reason, so the
human stays the gate (FRAPPE.md, "Live sites"). Local throwaway sites (*.localhost, *.test,
names starting with "test") are trusted for migrate, but never for dropping or restoring.
"""

from __future__ import annotations

import json
import re
import sys

SITE = re.compile(r"--site[ =]+(\S+)")
LOCAL_SITE = re.compile(r"(\.localhost|\.test|\.local)$|^test", re.I)

ALWAYS_ASK = [
    (re.compile(r"\bbench\b.*\b(drop-site|reinstall|restore|partial-restore)\b"),
     "drops or overwrites a site's data"),
    (re.compile(r"\bbench\b.*\bset-config\b.*\bserver_script_enabled\b"),
     "changes the bench-wide Server Script switch (a security decision)"),
    (re.compile(r"\bdocker\s+(system\s+prune|volume\s+(rm|prune))\b"),
     "deletes Docker data"),
    (re.compile(r"\b(mysql|mariadb)\b.*\b(drop|truncate|delete\s+from|update\s+\S+\s+set)\b", re.I),
     "changes database rows directly, without Frappe's validation"),
    (re.compile(r"\bbench\b.*\b(mariadb|db-console)\b.*\b(drop|truncate|delete|update)\b", re.I),
     "changes database rows directly, without Frappe's validation"),
    (re.compile(r"\bgit\s+push\b.*(--force|-f\b)"),
     "force-pushes"),
]

LIVE_SITE_ASK = [
    (re.compile(r"\bbench\b.*\bmigrate\b"), "runs migrate (schema changes, patches, fixtures)"),
    (re.compile(r"\bbench\b.*\b(execute|console|run-patch)\b"), "runs code against the site"),
]

REST_WRITE = re.compile(
    r"\bcurl\b.*(-X\s*|--request\s+)(PUT|POST|PATCH|DELETE)\b.*?/api/(resource|v2/document|method)/", re.I)


def decide(command: str) -> str | None:
    for pattern, reason in ALWAYS_ASK:
        if pattern.search(command):
            return reason
    site = SITE.search(command)
    if site and not LOCAL_SITE.search(site.group(1)):
        for pattern, reason in LIVE_SITE_ASK:
            if pattern.search(command):
                return f"{reason} on `{site.group(1)}`, which does not look like a local test site"
    if REST_WRITE.search(command):
        return ("writes over REST; a save runs every event script of the DocType "
                "(GOTCHAS-frappe.md, 7): run .exoskeleton-integrator/scripts/triage_rest.py --doctype first")
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0
    command = (payload.get("tool_input") or {}).get("command") or ""
    reason = decide(command)
    if reason:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": f"Exoskeleton Integrator: this command {reason}. A human confirms it.",
        }}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
