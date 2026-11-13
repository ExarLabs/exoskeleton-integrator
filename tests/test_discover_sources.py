"""discover_sources.py: scoring, filters and a full ranking against a fake GitHub."""

import base64
from datetime import datetime, timedelta, timezone

import discover_sources as ds

NOW = datetime(2026, 11, 13, tzinfo=timezone.utc)


def b64(text):
    return base64.b64encode(text.encode()).decode()


def test_stars_do_not_count_and_non_frappe_scores_zero():
    assert ds.score(terms=4, frappe_app=True, months6=6, commits90=100, authors90=9) == 0.0
    active = ds.score(terms=60, frappe_app=True, months6=6, commits90=50, authors90=4)
    assert active == 9.0
    # a popular but abandoned package: Frappe-specific, no app, no recent work
    assert ds.score(terms=60, frappe_app=False, months6=0, commits90=0, authors90=0) == 3.0


def test_terms_count_frappe_specific_words_only():
    text = "Use frappe.whitelist and bench --site x migrate. Add a DocType. Write small functions."
    assert ds.count_terms(text) == 3
    assert ds.count_terms("taper à la machine: frappe rapide") == 0


def test_frappe_app_needs_hooks_and_modules():
    assert ds.is_frappe_app(["my_app/hooks.py", "my_app/modules.txt", "README.md"])
    assert not ds.is_frappe_app(["hooks.py", "README.md"])


def test_activity_counts_distinct_months_capped_at_six():
    dates = [NOW - timedelta(days=d) for d in (1, 2, 40, 70, 100, 130, 160, 400)]
    months, c90 = ds.activity(dates, NOW)
    assert c90 == 4
    assert 1 <= months <= 6
    # 183 days can touch seven calendar months; the score must see at most six
    spread = [NOW - timedelta(days=d) for d in (1, 32, 63, 94, 125, 156, 182)]
    assert ds.activity(spread, NOW)[0] == 6


def test_mirrors_are_filtered():
    assert ds.is_mirror("someone/claude-skill-registry")
    assert ds.is_mirror("x/awesome-codex-plugins")
    assert not ds.is_mirror("alyf-de/banking")


def test_rank_end_to_end_with_fake_github():
    skill = b64("frappe.whitelist frappe.get_doc DocType bench --site a migrate hooks.py erpnext")
    recent = (NOW - timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%SZ")

    def get(path, params=None):
        if path == "/search/code":
            if params["q"] == "frappe filename:SKILL.md" and params["page"] == 1:
                return {"items": [
                    {"repository": {"full_name": "field/app"}, "path": "SKILL.md"},
                    {"repository": {"full_name": "x/claude-skill-registry"}, "path": "a/SKILL.md"},
                    {"repository": {"full_name": "popular/stale"}, "path": "SKILL.md"},
                ]}
            return {"items": []}
        if path == "/repos/x/claude-skill-registry":
            return {"stargazers_count": 5000, "default_branch": "main", "pushed_at": recent}
        if path == "/repos/field/app":
            return {"stargazers_count": 0, "default_branch": "main", "pushed_at": recent}
        if path == "/repos/popular/stale":
            return {"stargazers_count": 900, "default_branch": "main", "pushed_at": "2026-03-01T00:00:00Z"}
        if path == "/repos/field/app/commits":
            return [{"commit": {"committer": {"date": recent}, "author": {"name": "a"}}, "author": {"login": "a"}}]
        if path == "/repos/popular/stale/commits":
            return []
        if path.endswith("/git/trees/main"):
            return {"tree": [{"path": "app/hooks.py"}, {"path": "app/modules.txt"}]} if "field" in path else {"tree": []}
        if path.endswith("/contents/SKILL.md"):
            return {"content": skill}
        return None

    rows = ds.rank(get, now=NOW, workers=1, sleep=0)
    assert [r["repo"] for r in rows] == ["field/app", "popular/stale"]
    assert rows[0]["frappe_app"] and rows[0]["score"] > rows[1]["score"]
    text = ds.render(rows)
    assert "Stars are not in the score" in text and "`field/app`" in text
