#!/usr/bin/env python3
"""Triage a Frappe site over REST. Read-only: it sends GET requests only.

Usage:
    export FRAPPE_API_KEY=... FRAPPE_API_SECRET=...
    python3 scripts/triage_rest.py --url https://erp.example.com
    python3 scripts/triage_rest.py --url https://erp.example.com --doctype "Sales Invoice"
    python3 scripts/triage_rest.py --url https://erp.example.com --doctype "Sales Invoice" --show-scripts

Without --doctype it prints the site block: versions, Server Scripts, DocTypes with Custom
DocPerm rows. With --doctype it prints what runs when that DocType is saved (its DocType Event
Server Scripts) and its Custom DocPerm rows: read it before any REST write (GOTCHAS-frappe.md, 7).

Credentials come from the environment only, never from arguments, so they stay out of shell
history and process lists. The API user needs read access to Server Script and Custom DocPerm
(System Manager has it).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter

# Server Script event names, from EVENT_MAP in frappe/core/doctype/server_script/
# server_script_utils.py (v15 and v16 union; "Discard" and the payment charge events are v16).
# Sorted roughly in the order a save runs them, for display only.
EVENT_ORDER = [
    "Before Insert", "Before Validate", "Before Save", "After Insert", "After Save",
    "Before Submit", "After Submit", "Before Save (Submitted Document)",
    "After Save (Submitted Document)", "Before Cancel", "After Cancel",
    "Before Discard", "After Discard", "Before Rename", "After Rename",
    "Before Delete", "After Delete", "Before Print",
    "On Payment Authorization", "On Payment Paid", "On Payment Failed",
    "On Payment Charge Processed", "On Payment Mandate Charge Processed",
    "On Payment Mandate Acquisition Processed",
]

RIGHTS = ["read", "write", "create", "delete", "submit", "cancel", "amend",
          "report", "export", "print", "email", "share"]


class Client:
    def __init__(self, url: str, key: str, secret: str, opener=urllib.request.urlopen):
        self.base = url.rstrip("/")
        self.auth = f"token {key}:{secret}"
        self.opener = opener

    def get(self, path: str, params: dict | None = None):
        query = ""
        if params:
            query = "?" + urllib.parse.urlencode(
                {k: v if isinstance(v, str) else json.dumps(v) for k, v in params.items()}
            )
        url = f"{self.base}{urllib.parse.quote(path)}{query}"
        req = urllib.request.Request(url, method="GET", headers={
            "Authorization": self.auth,
            "Accept": "application/json",
            "User-Agent": "exoskeleton-integrator",
        })
        try:
            with self.opener(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as err:
            if err.code in (401, 403):
                raise SystemExit(f"HTTP {err.code} on {path}: the API user lacks read access here.") from None
            raise SystemExit(f"HTTP {err.code} on {path}") from None

    def resource(self, doctype: str, fields: list[str], filters: list | None = None):
        params = {"fields": fields, "limit_page_length": "0"}
        if filters:
            params["filters"] = filters
        return self.get(f"/api/resource/{doctype}", params).get("data", [])


def site_block(client: Client) -> str:
    versions = client.get("/api/method/frappe.utils.change_log.get_versions").get("message", {})
    scripts = client.resource("Server Script", [
        "name", "script_type", "reference_doctype", "doctype_event", "api_method", "disabled"])
    perm_parents = Counter(r["parent"] for r in client.resource("Custom DocPerm", ["parent"]))

    lines = ["## Frappe triage (REST)", "", "| Item | Value |", "|---|---|", f"| Site | {client.base} |"]
    for app, info in sorted(versions.items()):
        lines.append(f"| {app} | {info.get('version', '?')} ({info.get('branch') or 'no branch'}) |")
    lines += [
        "| developer_mode | not visible over REST |",
        "| server_script_enabled | not visible over REST (bench-wide setting) |",
        "",
        f"### Server Scripts ({len(scripts)})",
        "",
    ]
    if scripts:
        lines += ["| Name | Type | DocType | Event | API method | Disabled |", "|---|---|---|---|---|---|"]
        for s in sorted(scripts, key=lambda s: (s.get("script_type") or "", s.get("reference_doctype") or "", s["name"])):
            lines.append(
                f"| {s['name']} | {s.get('script_type') or ''} | {s.get('reference_doctype') or ''} "
                f"| {s.get('doctype_event') or ''} | {s.get('api_method') or ''} | {bool(s.get('disabled'))} |"
            )
    else:
        lines.append("None.")
    lines += ["", f"### DocTypes with Custom DocPerm rows ({len(perm_parents)})", "",
              "On these DocTypes only the Custom DocPerm rows count (GOTCHAS-frappe.md, 1).", ""]
    if perm_parents:
        lines += ["| DocType | Rows |", "|---|---|"]
        lines += [f"| {p} | {n} |" for p, n in sorted(perm_parents.items())]
    else:
        lines.append("None.")
    return "\n".join(lines)


def doctype_block(client: Client, doctype: str, show_scripts: bool) -> str:
    fields = ["name", "doctype_event", "disabled", "modified"] + (["script"] if show_scripts else [])
    scripts = client.resource("Server Script", fields, [
        ["script_type", "=", "DocType Event"], ["reference_doctype", "=", doctype]])
    order = {name: i for i, name in enumerate(EVENT_ORDER)}
    scripts.sort(key=lambda s: (order.get(s.get("doctype_event"), 99), s["name"]))
    perms = client.resource("Custom DocPerm", ["role", "permlevel", "if_owner"] + RIGHTS,
                            [["parent", "=", doctype]])

    lines = [f"## What runs when `{doctype}` is saved", "",
             "A REST update calls `doc.save()`: the save events below run (insert, submit and "
             "cancel events only on those actions), plus the controller hooks of the DocType's app "
             "(GOTCHAS-frappe.md, 7).", ""]
    active = [s for s in scripts if not s.get("disabled")]
    if scripts:
        lines += ["| Event | Script | Disabled | Modified |", "|---|---|---|---|"]
        for s in scripts:
            lines.append(f"| {s.get('doctype_event')} | {s['name']} | {bool(s.get('disabled'))} | {s.get('modified', '')} |")
        lines.append("")
        lines.append(f"{len(active)} active event script(s).")
    else:
        lines.append("No DocType Event Server Scripts. Controller hooks still run.")
    if show_scripts:
        for s in active:
            lines += ["", f"#### {s['name']} ({s.get('doctype_event')})", "", "```python", s.get("script") or "", "```"]
    lines += ["", f"### Custom DocPerm rows on `{doctype}` ({len(perms)})", ""]
    if perms:
        lines.append("These rows replace the DocType's standard permissions (GOTCHAS-frappe.md, 1).")
        lines += ["", "| Role | Level | If owner | " + " | ".join(RIGHTS) + " |",
                  "|---|---|---|" + "---|" * len(RIGHTS)]
        for p in sorted(perms, key=lambda p: (p.get("role") or "", p.get("permlevel") or 0)):
            lines.append(f"| {p.get('role')} | {p.get('permlevel', 0)} | {p.get('if_owner', 0)} | "
                         + " | ".join(str(p.get(r, 0)) for r in RIGHTS) + " |")
    else:
        lines.append("None: the standard DocPerm rows apply.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", required=True, help="site URL, e.g. https://erp.example.com")
    ap.add_argument("--doctype", help="show what runs when this DocType is saved")
    ap.add_argument("--show-scripts", action="store_true", help="with --doctype: print active script bodies")
    args = ap.parse_args(argv)

    key, secret = os.environ.get("FRAPPE_API_KEY"), os.environ.get("FRAPPE_API_SECRET")
    if not key or not secret:
        ap.error("set FRAPPE_API_KEY and FRAPPE_API_SECRET in the environment")
    client = Client(args.url, key, secret)
    out = doctype_block(client, args.doctype, args.show_scripts) if args.doctype else site_block(client)
    sys.stdout.write(out + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
