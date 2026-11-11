#!/usr/bin/env python3
"""List what a Frappe Server Script can call, read from the framework source.

Server Scripts run in a restricted namespace built in frappe/utils/safe_exec.py.
Hand-written lists of that namespace go wrong (frappe.get_roles is the classic
case), so this script reads the source itself, with the standard library only.

Usage:
    python3 scripts/safe_exec_names.py --branch version-15 --branch version-16
    python3 scripts/safe_exec_names.py --source path/to/safe_exec.py --label local
    python3 scripts/safe_exec_names.py --branch version-16 --out docs/context/SAFE_EXEC-frappe.md

It reads source statically. It does not import Frappe and needs no bench.
Exception classes added at runtime (add_module_properties) are not listed.
"""

from __future__ import annotations

import argparse
import ast
import sys
import urllib.request
from dataclasses import dataclass, field

RAW_URL = "https://raw.githubusercontent.com/frappe/frappe/{ref}/frappe/utils/safe_exec.py"

# Names that models and other skill packages often assume exist in a Server Script.
# For each, the report says where it really lives, or that it is missing.
COMMONLY_ASSUMED = [
    "get_roles",
    "has_permission",
    "generate_hash",
    "parse_json",
    "cache",
    "get_traceback",
    "get_value",
    "set_value",
    "get_single_value",
    "flt",
    "cint",
    "nowdate",
    "add_days",
    "getdate",
    "enqueue",
    "sendmail",
    "commit",
]


@dataclass
class Namespace:
    label: str
    top: set[str] = field(default_factory=set)
    frappe: set[str] = field(default_factory=set)
    db: set[str] = field(default_factory=set)
    website: set[str] = field(default_factory=set)
    utils: set[str] = field(default_factory=set)
    removed_in_doc_events: set[str] = field(default_factory=set)
    notes: list[str] = field(default_factory=list)


def _is_namespace_call(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "NamespaceDict"
    )


def _keywords(call: ast.Call) -> dict[str, ast.AST]:
    return {kw.arg: kw.value for kw in call.keywords if kw.arg}


def _attr_chain(node: ast.AST) -> str:
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return ".".join(reversed(parts))


def _function(tree: ast.Module, name: str) -> ast.FunctionDef | None:
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def parse(source: str, label: str) -> Namespace:
    tree = ast.parse(source)
    ns = Namespace(label=label)

    # frappe.utils.* comes from the VALID_UTILS tuple.
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "VALID_UTILS" for t in node.targets
        ):
            if isinstance(node.value, (ast.Tuple, ast.List)):
                ns.utils = {
                    e.value for e in node.value.elts
                    if isinstance(e, ast.Constant) and isinstance(e.value, str)
                }

    render = _function(tree, "render_safe_globals")
    if render is None:
        raise ValueError(f"{label}: render_safe_globals() not found; the source layout changed")
    for node in ast.walk(render):
        if isinstance(node, ast.Assign) and _is_namespace_call(node.value):
            targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
            if "out" not in targets:
                continue
            kws = _keywords(node.value)
            ns.top |= set(kws)
            frappe_call = kws.get("frappe")
            if frappe_call is not None and _is_namespace_call(frappe_call):
                fkws = _keywords(frappe_call)
                ns.frappe |= set(fkws)
                if _is_namespace_call(fkws.get("db")):
                    ns.db |= set(_keywords(fkws["db"]))
                if _is_namespace_call(fkws.get("website")):
                    ns.website |= set(_keywords(fkws["website"]))

    execf = _function(tree, "exec_safe_globals")
    if execf is None:
        raise ValueError(f"{label}: exec_safe_globals() not found; the source layout changed")
    for node in ast.walk(execf):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "update"
            and node.args
            and _is_namespace_call(node.args[0])
        ):
            owner = _attr_chain(node.func.value)
            names = set(_keywords(node.args[0]))
            if owner == "out":
                ns.top |= names
            elif owner == "out.frappe":
                ns.frappe |= names
            elif owner == "out.frappe.db":
                ns.db |= names

    safe_exec = _function(tree, "safe_exec")
    if safe_exec is not None:
        for node in ast.walk(safe_exec):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "pop"
                and _attr_chain(node.func.value).endswith("frappe.db")
                and node.args
                and isinstance(node.args[0], ast.Constant)
            ):
                ns.removed_in_doc_events.add(node.args[0].value)

    # "frappe" and "utils" are containers, not callables a script uses directly.
    ns.frappe.discard("db")
    ns.frappe.discard("website")
    ns.frappe.discard("utils")
    if not ns.frappe or not ns.utils:
        raise ValueError(f"{label}: parsed an empty namespace; the source layout changed")
    return ns


def where(ns: Namespace, name: str) -> str:
    places = []
    if name in ns.frappe:
        places.append(f"`frappe.{name}`")
    if name in ns.db:
        extra = " (not in DocType Event scripts)" if name in ns.removed_in_doc_events else ""
        places.append(f"`frappe.db.{name}`{extra}")
    if name in ns.utils:
        places.append(f"`frappe.utils.{name}`")
    if name in ns.top:
        places.append(f"`{name}`")
    return ", ".join(places) if places else "**missing**"


def render_markdown(spaces: list[Namespace], sources: dict[str, str]) -> str:
    lines = [
        "# Server Script namespace (generated)",
        "",
        "> Generated by `scripts/safe_exec_names.py` from `frappe/utils/safe_exec.py`. Do not edit by hand; regenerate.",
        "",
        "Sources:",
    ]
    lines += [f"- {label}: {src}" for label, src in sources.items()]
    lines += [
        "",
        "## Names that are often assumed",
        "",
        "| Name | " + " | ".join(ns.label for ns in spaces) + " |",
        "|---|" + "---|" * len(spaces),
    ]
    for name in COMMONLY_ASSUMED:
        lines.append(f"| `{name}` | " + " | ".join(where(ns, name) for ns in spaces) + " |")
    lines += [
        "",
        "Bare names such as `flt` or `nowdate` are not defined: use `frappe.utils.flt`.",
        "",
    ]
    for ns in spaces:
        lines += [f"## {ns.label}", ""]
        lines.append("**Top level:** " + ", ".join(f"`{n}`" for n in sorted(ns.top)))
        lines.append("")
        lines.append("**`frappe.*`:** " + ", ".join(f"`{n}`" for n in sorted(ns.frappe)))
        lines.append("")
        lines.append("**`frappe.db.*`:** " + ", ".join(f"`{n}`" for n in sorted(ns.db)))
        lines.append("")
        if ns.removed_in_doc_events:
            lines.append(
                "**Removed in DocType Event scripts:** "
                + ", ".join(f"`frappe.db.{n}`" for n in sorted(ns.removed_in_doc_events))
            )
            lines.append("")
        lines.append("**`frappe.utils.*`:** " + ", ".join(f"`{n}`" for n in sorted(ns.utils)))
        lines.append("")
    return "\n".join(lines)


def fetch(ref: str) -> str:
    url = RAW_URL.format(ref=ref)
    req = urllib.request.Request(url, headers={"User-Agent": "exoskeleton-integrator"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--branch", action="append", default=[], help="frappe/frappe branch or tag, repeatable")
    ap.add_argument("--source", action="append", default=[], help="local safe_exec.py, repeatable")
    ap.add_argument("--label", action="append", default=[], help="label for each --source, in order")
    ap.add_argument("--out", help="write markdown here instead of stdout")
    args = ap.parse_args(argv)

    if not args.branch and not args.source:
        ap.error("give at least one --branch or --source")

    spaces, sources = [], {}
    for ref in args.branch:
        spaces.append(parse(fetch(ref), ref))
        sources[ref] = RAW_URL.format(ref=ref)
    for i, path in enumerate(args.source):
        label = args.label[i] if i < len(args.label) else path
        with open(path, encoding="utf-8") as fh:
            spaces.append(parse(fh.read(), label))
        sources[label] = path

    text = render_markdown(spaces, sources)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
    else:
        sys.stdout.write(text + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
