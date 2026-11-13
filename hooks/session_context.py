#!/usr/bin/env python3
"""SessionStart hook: tell the agent which bench, site and Frappe version it is in.

Finds the bench from FRAPPE_BENCH_PATH, or by walking up from the working directory to a
folder that has sites/apps.txt and apps/frappe. Outside a bench it prints nothing.
Reads only named, non-secret keys from the config files.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path


def find_bench(start: Path) -> Path | None:
    env = os.environ.get("FRAPPE_BENCH_PATH")
    if env and (Path(env) / "sites" / "apps.txt").is_file():
        return Path(env)
    for folder in [start, *start.parents]:
        if (folder / "sites" / "apps.txt").is_file() and (folder / "apps" / "frappe").is_dir():
            return folder
    return None


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def frappe_version(bench: Path) -> str:
    init = bench / "apps" / "frappe" / "frappe" / "__init__.py"
    try:
        match = re.search(r'^__version__\s*=\s*["\']([^"\']+)', init.read_text(encoding="utf-8"), re.M)
    except OSError:
        return "unknown"
    return match.group(1) if match else "unknown"


def describe(bench: Path) -> str:
    sites_dir = bench / "sites"
    apps = [a.strip() for a in (sites_dir / "apps.txt").read_text(encoding="utf-8").splitlines() if a.strip()]
    sites = sorted(p.name for p in sites_dir.iterdir() if (p / "site_config.json").is_file())
    current = os.environ.get("FRAPPE_SITE")
    if not current:
        try:
            current = (sites_dir / "currentsite.txt").read_text(encoding="utf-8").strip() or None
        except OSError:
            current = None
    common = read_json(sites_dir / "common_site_config.json")
    lines = [
        "Frappe bench detected (Exoskeleton Integrator).",
        f"- bench: {bench}",
        f"- frappe version: {frappe_version(bench)}",
        f"- apps: {', '.join(apps)}",
        f"- sites: {', '.join(sites) or 'none'}",
        f"- default site: {current or 'not set (use --site)'}",
        f"- server_script_enabled (bench-wide): {bool(common.get('server_script_enabled'))}",
    ]
    if current and (sites_dir / current / "site_config.json").is_file():
        site_conf = read_json(sites_dir / current / "site_config.json")
        lines.append(f"- {current}: developer_mode={bool(site_conf.get('developer_mode', common.get('developer_mode')))}, "
                     f"allow_tests={bool(site_conf.get('allow_tests'))}")
    lines.append("Read docs/context/FRAPPE.md and GOTCHAS-frappe.md before planning; "
                 "run .exoskeleton-integrator/scripts/triage_console.py for the full triage.")
    lines.append("Before planning code, write the light way in CONTEXT.md (FRAPPE.md, 'The light way'): "
                 "what the existing modules cover without code; the owner chooses.")
    return "\n".join(lines)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        payload = {}
    cwd = Path(payload.get("cwd") or os.getcwd())
    bench = find_bench(cwd)
    if bench is None:
        return 0
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": describe(bench),
    }}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
