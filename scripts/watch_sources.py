#!/usr/bin/env python3
"""Report what changed in the sources this package learns from. Read-only.

Two questions, answered from the GitHub API:

1. Pinned sources. Every Frappe link in the Frappe layer points at a commit. For each linked
   file, has the branch that commit belongs to changed that file since? If so, the trap or
   rule citing it may be out of date.
2. Watched repositories and releases (watch/sources.json). What is new since the last run:
   commits, a release, a licence change, an archived repository.

Usage:
  python3 scripts/watch_sources.py                 # markdown report, state saved
  python3 scripts/watch_sources.py --json          # the same as data
  python3 scripts/watch_sources.py --no-save       # do not record this run as seen

A token makes the run reliable (unauthenticated GitHub allows 60 requests an hour): the
GITHUB_TOKEN or GH_TOKEN environment variable, else `gh auth token` if the GitHub CLI is
logged in. The token is sent to api.github.com only and never printed.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LAYER = ROOT / "frappe-layer"
SOURCES = ROOT / "watch" / "sources.json"
DEFAULT_STATE = Path.home() / ".exoskeleton-integrator" / "watch_state.json"
API = "https://api.github.com"

# github.com/<owner>/<repo>/(blob|tree)/<40-hex sha>/<path>
PIN = re.compile(
    r"https://github\.com/([\w.-]+/[\w.-]+)/(?:blob|tree)/([0-9a-f]{40})/([^\s)#?]+)"
)


def extract_pins(files):
    """{(repo, sha, path): [cited by files]} for every pinned source link."""
    pins = {}
    for f in files:
        text = Path(f).read_text(encoding="utf-8")
        for repo, sha, path in PIN.findall(text):
            path = path.rstrip("/")
            pins.setdefault((repo, sha, path), [])
            name = Path(f).name
            if name not in pins[(repo, sha, path)]:
                pins[(repo, sha, path)].append(name)
    return pins


def github_token():
    for var in ("GITHUB_TOKEN", "GH_TOKEN"):
        if os.environ.get(var):
            return os.environ[var]
    try:
        out = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, timeout=10)
        return out.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def make_fetcher(token):
    def get(path, params=None):
        url = API + path
        if params:
            url += "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "exoskeleton-integrator-watch",
        })
        if token:
            req.add_header("Authorization", f"Bearer {token}")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            raise RuntimeError(f"GitHub API {e.code} on {path}") from None
    return get


def check_pins(pins, branches, get):
    """Changes on the pinned branch to each linked file since the pinned commit."""
    changed, unknown = [], []
    dates = {}
    for (repo, sha, path), cited in sorted(pins.items()):
        branch = branches.get(repo, {}).get(sha)
        if not branch:
            unknown.append({"repo": repo, "sha": sha, "path": path, "cited_by": cited})
            continue
        if (repo, sha) not in dates:
            commit = get(f"/repos/{repo}/commits/{sha}")
            dates[(repo, sha)] = commit["commit"]["committer"]["date"] if commit else None
        since = dates[(repo, sha)]
        if since is None:
            unknown.append({"repo": repo, "sha": sha, "path": path, "cited_by": cited})
            continue
        commits = get(f"/repos/{repo}/commits",
                      {"sha": branch, "path": path, "since": since, "per_page": 20}) or []
        newer = [c for c in commits if c["sha"] != sha]
        if newer:
            changed.append({
                "repo": repo, "branch": branch, "path": path, "cited_by": cited,
                "commits": len(newer),
                "latest": {"sha": newer[0]["sha"][:7],
                           "date": newer[0]["commit"]["committer"]["date"][:10],
                           "message": newer[0]["commit"]["message"].splitlines()[0][:100]},
            })
    return changed, unknown


def check_repos(repos, state, get):
    """New commits, licence or archive changes since the last recorded run."""
    out, new_state = [], {}
    for entry in repos:
        repo, branch = entry["repo"], entry["branch"]
        meta = get(f"/repos/{repo}")
        if meta is None:
            out.append({"repo": repo, "status": "gone"})
            continue
        head_list = get(f"/repos/{repo}/commits", {"sha": branch, "per_page": 1}) or []
        head = head_list[0]["sha"] if head_list else None
        licence = (meta.get("license") or {}).get("spdx_id")
        seen = state.get(repo, {})
        item = {"repo": repo, "why": entry.get("why", ""), "head": head and head[:7],
                "pushed_at": (meta.get("pushed_at") or "")[:10], "license": licence,
                "archived": bool(meta.get("archived"))}
        if not seen:
            item["status"] = "baseline"
        elif seen.get("head") == head:
            item["status"] = "unchanged"
        else:
            cmp = get(f"/repos/{repo}/compare/{seen['head']}...{head}") or {}
            item["status"] = "new commits"
            item["new_commits"] = cmp.get("total_commits")
            item["messages"] = [c["commit"]["message"].splitlines()[0][:100]
                                for c in (cmp.get("commits") or [])][-10:]
        if seen and seen.get("license") != licence:
            item["license_changed_from"] = seen.get("license")
        if seen and not seen.get("archived") and item["archived"]:
            item["newly_archived"] = True
        out.append(item)
        new_state[repo] = {"head": head, "license": licence, "archived": item["archived"]}
    return out, new_state


def check_releases(repos, state, get):
    out, new_state = [], {}
    for repo in repos:
        rel = get(f"/repos/{repo}/releases/latest")
        tag = rel.get("tag_name") if rel else None
        seen = state.get(repo, {}).get("tag")
        out.append({"repo": repo, "tag": tag,
                    "status": "baseline" if repo not in state else
                              ("unchanged" if seen == tag else f"new release (was {seen})")})
        new_state[repo] = {"tag": tag}
    return out, new_state


def render(report):
    lines = ["# Watched sources", ""]
    changed = report["pins_changed"]
    lines.append(f"## Pinned sources that changed since their pin ({len(changed)})")
    lines.append("")
    if not changed:
        lines.append("None: every file the layer cites is unchanged on its branch.")
    for c in changed:
        lines.append(f"- `{c['repo']}` {c['branch']} `{c['path']}`: {c['commits']} commit(s), "
                     f"latest {c['latest']['sha']} {c['latest']['date']} \"{c['latest']['message']}\". "
                     f"Cited by: {', '.join(c['cited_by'])}.")
    if report["pins_unknown"]:
        lines.append("")
        lines.append("Pins with no branch in watch/sources.json (add one): " + ", ".join(
            f"`{u['repo']}@{u['sha'][:7]}`" for u in report["pins_unknown"]))
    lines += ["", "## Watched repositories", ""]
    for r in report["repos"]:
        line = f"- `{r['repo']}`: {r['status']}"
        if r.get("new_commits"):
            line += f", {r['new_commits']} new commit(s)"
        line += f" (head {r.get('head')}, pushed {r.get('pushed_at')}, licence {r.get('license')})"
        if r.get("license_changed_from") is not None:
            line += f"; LICENCE CHANGED from {r['license_changed_from']}"
        if r.get("newly_archived"):
            line += "; ARCHIVED"
        lines.append(line)
        for m in r.get("messages") or []:
            lines.append(f"  - {m}")
    lines += ["", "## Releases", ""]
    for r in report["releases"]:
        lines.append(f"- `{r['repo']}`: {r['tag']} ({r['status']})")
    return "\n".join(lines) + "\n"


def run(get, sources, state, layer_files):
    pins = extract_pins(layer_files)
    changed, unknown = check_pins(pins, sources.get("pins", {}), get)
    repos, repo_state = check_repos(sources.get("repos", []), state.get("repos", {}), get)
    releases, rel_state = check_releases(sources.get("releases", []), state.get("releases", {}), get)
    report = {"pins_checked": len(pins), "pins_changed": changed, "pins_unknown": unknown,
              "repos": repos, "releases": releases}
    return report, {"repos": repo_state, "releases": rel_state}


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-save", action="store_true")
    ap.add_argument("--state", type=Path, default=DEFAULT_STATE)
    ap.add_argument("--sources", type=Path, default=SOURCES)
    args = ap.parse_args(argv)

    sources = json.loads(args.sources.read_text(encoding="utf-8"))
    state = json.loads(args.state.read_text(encoding="utf-8")) if args.state.exists() else {}
    token = github_token()
    if not token:
        print("warning: no GitHub token, the run may hit the 60 requests an hour limit",
              file=sys.stderr)
    try:
        report, new_state = run(make_fetcher(token), sources, state, sorted(LAYER.rglob("*.md")))
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2) if args.json else render(report), end="" if not args.json else "\n")
    if not args.no_save:
        args.state.parent.mkdir(parents=True, exist_ok=True)
        args.state.write_text(json.dumps(new_state, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
