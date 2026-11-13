#!/usr/bin/env python3
"""Find and rank repositories whose agent instructions talk about Frappe. Read-only.

`watch_sources.py` follows a fixed list. This script finds new candidates for that list:
repositories that keep agent instructions (SKILL.md, AGENTS.md, CLAUDE.md) mentioning Frappe,
ranked by what suggests real, maintained knowledge rather than early popularity.

Stars do not count. The score adds up:
  - Frappe specificity: Frappe terms (DocType, bench --site, frappe.whitelist, ...) in the
    agent files, capped (weight 3)
  - field signal: the repository is itself a Frappe app (hooks.py and modules.txt), so the
    instructions serve production work (weight 2)
  - sustained activity: months with commits in the last six (weight 2), commits and authors
    in the last 90 days (weight 1 each)

Usage:
  python3 scripts/discover_sources.py                  # markdown ranking to stdout
  python3 scripts/discover_sources.py --json out.json  # every candidate with its numbers

Uses the same token rules as watch_sources.py. GitHub code search allows about ten requests
a minute, so a full run takes several minutes.
"""

import argparse
import base64
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from watch_sources import github_token, make_fetcher  # noqa: E402

QUERIES = [
    "frappe filename:SKILL.md", "erpnext filename:SKILL.md",
    "frappe filename:AGENTS.md", "frappe filename:CLAUDE.md", "erpnext filename:CLAUDE.md",
]
MIRRORS = ("registry", "directory", "awesome", "meta-skill", "codex-plugins", "cursor-settings",
           "memory-bank", "skill-collection", "skills-collection", "prompts")
TERMS = re.compile(
    r"\b(doctype|frappe\.(?:whitelist|get_doc|get_all|get_list|db|throw|call|enqueue|cache)|"
    r"bench\s+(?:--site|migrate|start|new-app|get-app|build|run-tests|console)|hooks\.py|"
    r"erpnext|server script|custom field|docperm|frappe-ui|frappe\.ui|frm\.|"
    r"patches\.txt|safe_exec|frappe framework|frappe app)\b", re.I)


def is_mirror(repo):
    return any(m in repo.lower() for m in MIRRORS)


def count_terms(text):
    return len(TERMS.findall(text or ""))


def is_frappe_app(tree_paths):
    names = {Path(p).name for p in tree_paths}
    return "hooks.py" in names and "modules.txt" in names


def activity(commit_dates, now):
    """Months with commits in the last six, and commits in the last 90 days."""
    six = now - timedelta(days=183)
    ninety = now - timedelta(days=90)
    dates = [d for d in commit_dates if d >= six]
    months = {d.strftime("%Y-%m") for d in dates}
    return min(len(months), 6), sum(1 for d in dates if d >= ninety)


def score(terms, frappe_app, months6, commits90, authors90):
    if terms < 5:
        return 0.0
    return round(3 * min(terms, 60) / 60 + 2 * bool(frappe_app) + 2 * min(months6, 6) / 6
                 + min(commits90, 50) / 50 + min(authors90, 4) / 4, 2)


def search(get, query, sleep=7.0):
    hits = []
    for page in range(1, 11):
        res = get("/search/code", {"q": query, "per_page": 100, "page": page}) or {}
        items = res.get("items") or []
        hits += [(it["repository"]["full_name"], it["path"]) for it in items]
        if sleep:
            time.sleep(sleep)
        if len(items) < 100:
            break
    return hits


def inspect(get, repo, paths, now):
    meta = get(f"/repos/{repo}")
    if not meta or meta.get("fork") or meta.get("archived"):
        return None
    since = (now - timedelta(days=183)).strftime("%Y-%m-%dT%H:%M:%SZ")
    commits = get(f"/repos/{repo}/commits", {"since": since, "per_page": 100}) or []
    dates = [datetime.fromisoformat(c["commit"]["committer"]["date"].replace("Z", "+00:00")) for c in commits]
    months6, commits90 = activity(dates, now)
    ninety = now - timedelta(days=90)
    authors90 = len({(c.get("author") or {}).get("login") or c["commit"]["author"]["name"]
                     for c, d in zip(commits, dates) if d >= ninety})
    tree = get(f"/repos/{repo}/git/trees/{meta['default_branch']}", {"recursive": 1}) or {}
    app = is_frappe_app([t["path"] for t in tree.get("tree", [])])
    terms = 0
    for p in paths[:12]:
        blob = get(f"/repos/{repo}/contents/{p}") or {}
        try:
            terms += count_terms(base64.b64decode(blob.get("content", "")).decode("utf-8", "replace"))
        except ValueError:
            pass
    return {"repo": repo, "stars": meta.get("stargazers_count", 0), "pushed": (meta.get("pushed_at") or "")[:10],
            "license": (meta.get("license") or {}).get("spdx_id"), "agent_files": len(paths),
            "frappe_terms": terms, "frappe_app": app, "months_active_6": months6,
            "commits90": commits90, "authors90": authors90,
            "score": score(terms, app, months6, commits90, authors90)}


def rank(get, now=None, workers=8, sleep=7.0):
    now = now or datetime.now(timezone.utc)
    paths = {}
    for q in QUERIES:
        for repo, p in search(get, q, sleep):
            paths.setdefault(repo, [])
            if p not in paths[repo]:
                paths[repo].append(p)
    cands = [r for r in paths if not is_mirror(r)]
    with ThreadPoolExecutor(workers) as ex:
        rows = [r for r in ex.map(lambda r: inspect(get, r, paths[r], now), cands) if r]
    return sorted(rows, key=lambda r: -r["score"])


def render(rows, top=30):
    relevant = [r for r in rows if r["score"] > 0]
    core = [r for r in relevant if r["repo"].startswith("frappe/")]
    field = [r for r in relevant if not r["repo"].startswith("frappe/")][:top]
    head = "| Repository | Score | Frappe app | Active months | Commits 90d | Authors 90d | Frappe terms | Stars |\n|---|---|---|---|---|---|---|---|"
    def line(r):
        return (f"| `{r['repo']}` | {r['score']} | {'yes' if r['frappe_app'] else '-'} | {r['months_active_6']}/6 "
                f"| {r['commits90']} | {r['authors90']} | {r['frappe_terms']} | {r['stars']} |")
    return "\n".join([f"# Frappe agent knowledge: ranking", "",
                      f"{len(rows)} repositories scanned, {len(relevant)} Frappe-specific. Stars are not in the score.", "",
                      f"## Frappe's own ({len(core)})", "", head, *map(line, core), "",
                      f"## Field apps, top {len(field)}", "", head, *map(line, field), ""])


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", type=Path)
    ap.add_argument("--top", type=int, default=30)
    args = ap.parse_args(argv)
    token = github_token()
    if not token:
        print("error: code search needs a GitHub token (GITHUB_TOKEN, GH_TOKEN or gh auth login)", file=sys.stderr)
        return 2
    rows = rank(make_fetcher(token))
    if args.json:
        args.json.write_text(json.dumps(rows, indent=1), encoding="utf-8")
    print(render(rows, args.top))
    return 0


if __name__ == "__main__":
    sys.exit(main())
