"""The generator must report what the pinned Frappe sources really contain."""

from pathlib import Path

import pytest

import safe_exec_names as sen

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="module", params=["version-15", "version-16"])
def ns(request):
    source = (FIXTURES / f"safe_exec_{request.param}.py").read_text(encoding="utf-8")
    return sen.parse(source, request.param)


def test_missing_names_are_missing(ns):
    for name in ("get_roles", "has_permission", "cache", "get_traceback"):
        assert sen.where(ns, name) == "**missing**", name


def test_helpers_live_under_utils_only(ns):
    for name in ("flt", "cint", "nowdate", "add_days", "getdate", "generate_hash"):
        assert name in ns.utils, name
        assert name not in ns.frappe, name
        assert name not in ns.top, name


def test_commit_is_removed_in_doc_events(ns):
    assert {"commit", "rollback", "add_index"} <= ns.removed_in_doc_events
    assert "not in DocType Event scripts" in sen.where(ns, "commit")


def test_db_and_frappe_core_names(ns):
    assert {"get_value", "set_value", "get_all", "exists", "sql"} <= ns.db
    assert {"get_doc", "get_all", "throw", "enqueue", "sendmail", "session"} <= ns.frappe


def test_parse_json_differs_between_versions():
    v15 = sen.parse((FIXTURES / "safe_exec_version-15.py").read_text(encoding="utf-8"), "v15")
    v16 = sen.parse((FIXTURES / "safe_exec_version-16.py").read_text(encoding="utf-8"), "v16")
    assert sen.where(v15, "parse_json") == "**missing**"
    assert sen.where(v16, "parse_json") == "`frappe.utils.parse_json`"


def test_layout_change_is_loud():
    with pytest.raises(ValueError):
        sen.parse("def unrelated():\n    pass\n", "broken")


def test_markdown_has_both_versions(tmp_path):
    out = tmp_path / "SAFE_EXEC.md"
    rc = sen.main([
        "--source", str(FIXTURES / "safe_exec_version-15.py"), "--label", "v15",
        "--source", str(FIXTURES / "safe_exec_version-16.py"), "--label", "v16",
        "--out", str(out),
    ])
    text = out.read_text(encoding="utf-8")
    assert rc == 0
    assert "| `get_roles` | **missing** | **missing** |" in text
    assert "## v15" in text and "## v16" in text
