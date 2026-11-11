"""watch_sources.py: pinned-link extraction and the three checks, with a fake GitHub."""

import json
from pathlib import Path

import watch_sources as ws

V15 = "2e9ecdc03fa5b5b8d1ba05224a1aff7dad832bd0"
ROOT = Path(__file__).resolve().parent.parent


def fake(routes):
    """A fetcher that answers from a dict keyed by (path, frozen params); unknown paths 404."""
    calls = []

    def get(path, params=None):
        calls.append((path, params))
        key = (path, tuple(sorted((params or {}).items())))
        return routes.get(key, routes.get(path))
    get.calls = calls
    return get


def commit(sha, date, msg="m"):
    return {"sha": sha, "commit": {"committer": {"date": date}, "message": msg}}


def test_extract_pins_reads_blob_and_tree_links_and_who_cites_them(tmp_path):
    a = tmp_path / "A.md"
    a.write_text(
        f"[x](https://github.com/frappe/frappe/blob/{V15}/frappe/permissions.py#L800-L820) "
        f"[x2](https://github.com/frappe/frappe/blob/{V15}/frappe/permissions.py#L839) "
        f"[y](https://github.com/frappe/frappe/tree/{V15}/frappe/tests/) "
        "[z](https://github.com/frappe/frappe/blob/version-15/frappe/x.py)", encoding="utf-8")
    b = tmp_path / "B.md"
    b.write_text(f"https://github.com/frappe/frappe/blob/{V15}/frappe/permissions.py", encoding="utf-8")
    pins = ws.extract_pins([a, b])
    assert pins == {
        ("frappe/frappe", V15, "frappe/permissions.py"): ["A.md", "B.md"],
        ("frappe/frappe", V15, "frappe/tests"): ["A.md"],
    }


def test_check_pins_reports_only_files_changed_after_the_pin():
    pins = {("frappe/frappe", V15, "a.py"): ["G.md"], ("frappe/frappe", V15, "b.py"): ["G.md"]}
    since = "2026-10-01T00:00:00Z"
    base = {"sha": "version-15", "since": since, "per_page": 20}
    get = fake({
        f"/repos/frappe/frappe/commits/{V15}": commit(V15, since),
        ("/repos/frappe/frappe/commits", tuple(sorted({**base, "path": "a.py"}.items()))):
            [commit("f" * 40, "2026-11-01T00:00:00Z", "fix: perms\nbody"), commit(V15, since)],
        ("/repos/frappe/frappe/commits", tuple(sorted({**base, "path": "b.py"}.items()))):
            [commit(V15, since)],
    })
    changed, unknown = ws.check_pins(pins, {"frappe/frappe": {V15: "version-15"}}, get)
    assert unknown == []
    assert [c["path"] for c in changed] == ["a.py"]
    assert changed[0]["commits"] == 1
    assert changed[0]["latest"]["message"] == "fix: perms"
    # the pinned commit's date is fetched once, not per file
    assert sum(1 for p, _ in get.calls if p.endswith(V15)) == 1


def test_check_pins_flags_a_pin_with_no_branch():
    pins = {("frappe/crm", "a" * 40, "crm/x.py"): ["C.md"]}
    get = fake({})
    changed, unknown = ws.check_pins(pins, {}, get)
    assert changed == [] and unknown[0]["repo"] == "frappe/crm"
    assert get.calls == [], "a pin with no branch must not cost API calls"


def test_check_repos_baseline_then_new_commits_and_licence_change():
    meta = {"pushed_at": "2026-11-10T00:00:00Z", "license": {"spdx_id": "MIT"}, "archived": False}
    routes = {
        "/repos/o/r": meta,
        ("/repos/o/r/commits", (("per_page", 1), ("sha", "main"))): [commit("b" * 40, "x")],
        f"/repos/o/r/compare/{'a' * 40}...{'b' * 40}": {
            "total_commits": 2, "commits": [commit("1", "x", "one"), commit("2", "x", "two")]},
    }
    repos = [{"repo": "o/r", "branch": "main"}]
    first, state = ws.check_repos(repos, {}, fake(routes))
    assert first[0]["status"] == "baseline" and state["o/r"]["head"] == "b" * 40

    old = {"o/r": {"head": "a" * 40, "license": None, "archived": False}}
    second, _ = ws.check_repos(repos, old, fake(routes))
    assert second[0]["status"] == "new commits"
    assert second[0]["new_commits"] == 2 and second[0]["messages"] == ["one", "two"]
    assert second[0]["license_changed_from"] is None


def test_check_repos_reports_a_deleted_repository():
    out, state = ws.check_repos([{"repo": "o/gone", "branch": "main"}], {}, fake({}))
    assert out == [{"repo": "o/gone", "status": "gone"}] and state == {}


def test_releases_and_render_end_to_end(tmp_path):
    routes = {"/repos/frappe/crm/releases/latest": {"tag_name": "v1.78.0"}}
    layer = tmp_path / "L.md"
    layer.write_text("no links here", encoding="utf-8")
    sources = {"pins": {}, "repos": [], "releases": ["frappe/crm"]}
    report, state = ws.run(fake(routes), sources, {"releases": {"frappe/crm": {"tag": "v1.77.3"}}}, [layer])
    assert report["releases"][0]["status"] == "new release (was v1.77.3)"
    assert state["releases"]["frappe/crm"]["tag"] == "v1.78.0"
    text = ws.render(report)
    assert "None: every file the layer cites is unchanged" in text
    assert "`frappe/crm`: v1.78.0" in text


def test_every_pinned_commit_in_the_layer_has_a_branch_in_sources():
    sources = json.loads((ROOT / "watch" / "sources.json").read_text(encoding="utf-8"))
    pins = ws.extract_pins(sorted((ROOT / "frappe-layer").rglob("*.md")))
    missing = {(repo, sha) for repo, sha, _ in pins if sha not in sources["pins"].get(repo, {})}
    assert not missing, f"add these pins to watch/sources.json: {missing}"
