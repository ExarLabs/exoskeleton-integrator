"""The Frappe layer's source links stay pinned, and every context file is in the index."""

import re
from pathlib import Path

LAYER = Path(__file__).resolve().parent.parent / "frappe-layer"
CONTEXT = LAYER / "docs" / "context"

# github.com/frappe/<repo>/(blob|tree)/<ref>/...
LINK = re.compile(r"https://github\.com/frappe/[\w.-]+/(?:blob|tree)/([^/\s)#]+)")
COMMIT = re.compile(r"[0-9a-f]{40}")


def unpinned(text):
    """Every ref in a frappe source link that is not a full 40-character commit."""
    return [ref for ref in LINK.findall(text) if not COMMIT.fullmatch(ref)]


def test_checker_flags_branches_and_short_shas():
    text = (
        "[a](https://github.com/frappe/frappe/blob/version-15/frappe/permissions.py#L1) "
        "[b](https://github.com/frappe/crm/blob/ead04d4/crm/x.py) "
        "[c](https://github.com/frappe/crm/tree/develop) "
        "[d](https://github.com/frappe/frappe/blob/2e9ecdc03fa5b5b8d1ba05224a1aff7dad832bd0/f.py#L2)"
    )
    assert unpinned(text) == ["version-15", "ead04d4", "develop"]


def test_every_frappe_link_in_the_layer_is_pinned():
    bad = {}
    for path in LAYER.rglob("*.md"):
        refs = unpinned(path.read_text(encoding="utf-8"))
        if refs:
            bad[str(path.relative_to(LAYER))] = refs
    assert not bad, f"links to a branch or short sha instead of a commit: {bad}"


def test_every_gotcha_says_how_to_find_it():
    """Each numbered trap tells the agent how to find it in its own code or site."""
    missing = []
    for path in CONTEXT.glob("GOTCHAS-*.md"):
        sections = re.split(r"^## (?=\d+\.)", path.read_text(encoding="utf-8"), flags=re.M)[1:]
        assert sections, f"{path.name}: no numbered traps"
        for section in sections:
            if "**Find it.**" not in section:
                missing.append(f"{path.name}: {section.splitlines()[0]}")
    assert not missing, f"traps without a 'Find it.' line: {missing}"


def test_the_light_way_comes_before_planning():
    """The light way is written at build-context, per intent line, and the owner chooses."""
    index = (CONTEXT / "FRAPPE.md").read_text(encoding="utf-8")
    section = index.split("## The light way, at build-context", 1)
    assert len(section) == 2, "FRAPPE.md lost its light way section"
    body = section[1].split("\n## ", 1)[0]
    for needle in ("`## Light way`", "intent line", "owner chooses", "A separate app"):
        assert needle in body, f"light way section lost: {needle}"


def test_every_context_file_is_in_the_frappe_index():
    index = (CONTEXT / "FRAPPE.md").read_text(encoding="utf-8")
    missing = [
        p.relative_to(CONTEXT).as_posix()
        for p in CONTEXT.rglob("*.md")
        if f"`{p.relative_to(CONTEXT).as_posix()}`" not in index
    ]
    assert not missing, f"not listed in FRAPPE.md: {missing}"
