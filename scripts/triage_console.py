# Triage a Frappe site from inside the bench. Read-only.
#
# Usage (from the bench directory):
#     bench --site <site> console < /path/to/exoskeleton-integrator/scripts/triage_console.py
#
# Prints one markdown block for the task's CONTEXT.md: versions, apps, developer mode,
# Server Script switch, Server Scripts on the site, DocTypes with Custom DocPerm rows.
# The file is fed to the IPython console line by line, so it avoids blank lines inside blocks.
import json
import frappe
from frappe.utils.change_log import get_versions
from frappe.utils.safe_exec import is_safe_exec_enabled
def _exo_triage():
    versions = get_versions()
    apps = frappe.get_installed_apps()
    scripts = frappe.get_all(
        "Server Script",
        fields=["name", "script_type", "reference_doctype", "doctype_event", "api_method", "disabled"],
        order_by="script_type asc, reference_doctype asc, name asc",
    )
    perm_parents = frappe.get_all("Custom DocPerm", pluck="parent")
    counts = {}
    for parent in perm_parents:
        counts[parent] = counts.get(parent, 0) + 1
    lines = ["## Frappe triage", "", "| Item | Value |", "|---|---|"]
    lines.append(f"| Site | `{frappe.local.site}` |")
    for app, info in versions.items():
        lines.append(f"| {app} | {info.get('version', '?')} ({info.get('branch') or 'no branch'}) |")
    lines.append(f"| Installed apps | {', '.join(apps)} |")
    lines.append(f"| developer_mode | {bool(frappe.conf.developer_mode)} |")
    lines.append(f"| allow_tests | {bool(frappe.conf.allow_tests)} |")
    lines.append(f"| server_script_enabled | {is_safe_exec_enabled()} |")
    lines.append("")
    lines.append(f"### Server Scripts ({len(scripts)})")
    lines.append("")
    if scripts:
        lines.append("| Name | Type | DocType | Event | API method | Disabled |")
        lines.append("|---|---|---|---|---|---|")
        for s in scripts:
            lines.append(
                f"| {s.name} | {s.script_type} | {s.reference_doctype or ''} | {s.doctype_event or ''} "
                f"| {s.api_method or ''} | {bool(s.disabled)} |"
            )
    else:
        lines.append("None.")
    lines.append("")
    lines.append(f"### DocTypes with Custom DocPerm rows ({len(counts)})")
    lines.append("")
    lines.append("On these DocTypes only the Custom DocPerm rows count (GOTCHAS-frappe.md, 1).")
    lines.append("")
    if counts:
        lines.append("| DocType | Rows |")
        lines.append("|---|---|")
        for parent in sorted(counts):
            lines.append(f"| {parent} | {counts[parent]} |")
    else:
        lines.append("None.")
    print("\n".join(lines))

_exo_triage()
