"""triage_rest.py against a fake opener: GET only, credentials in the header, right tables."""

import io
import json
import urllib.parse

import triage_rest as tr


class FakeOpener:
    def __init__(self, routes):
        self.routes = routes
        self.requests = []

    def __call__(self, req, timeout=None):
        self.requests.append(req)
        parsed = urllib.parse.urlparse(req.full_url)
        path = urllib.parse.unquote(parsed.path)
        body = self.routes[path](urllib.parse.parse_qs(parsed.query))
        resp = io.BytesIO(json.dumps(body).encode())
        resp.__enter__ = lambda *a: resp
        resp.__exit__ = lambda *a: None
        return _Ctx(resp)


class _Ctx:
    def __init__(self, resp):
        self.resp = resp

    def __enter__(self):
        return self.resp

    def __exit__(self, *a):
        return False


SCRIPTS = [
    {"name": "SI Before Save", "script_type": "DocType Event", "reference_doctype": "Sales Invoice",
     "doctype_event": "Before Save", "api_method": None, "disabled": 0, "modified": "2026-11-01"},
    {"name": "SI After Save", "script_type": "DocType Event", "reference_doctype": "Sales Invoice",
     "doctype_event": "After Save", "api_method": None, "disabled": 1, "modified": "2026-11-02"},
    {"name": "ping", "script_type": "API", "reference_doctype": None,
     "doctype_event": None, "api_method": "ping", "disabled": 0, "modified": "2026-11-03"},
]


def routes():
    def scripts(q):
        filters = json.loads(q["filters"][0]) if "filters" in q else []
        rows = SCRIPTS
        for field, _, value in filters:
            rows = [r for r in rows if r.get(field) == value]
        return {"data": rows}

    def perms(q):
        rows = [{"parent": "Sales Invoice", "role": "Accounts User", "permlevel": 0, "if_owner": 0, "read": 1, "write": 1},
                {"parent": "Sales Invoice", "role": "System Manager", "permlevel": 0, "if_owner": 0, "read": 1},
                {"parent": "Customer", "role": "Sales User", "permlevel": 0, "if_owner": 0, "read": 1}]
        if "filters" in q:
            parent = json.loads(q["filters"][0])[0][2]
            rows = [r for r in rows if r["parent"] == parent]
        return {"data": rows}

    return {
        "/api/method/frappe.utils.change_log.get_versions":
            lambda q: {"message": {"frappe": {"version": "16.26.3", "branch": "version-16"}}},
        "/api/resource/Server Script": scripts,
        "/api/resource/Custom DocPerm": perms,
    }


def client(opener):
    return tr.Client("https://erp.example.com/", "KEY", "SECRET", opener=opener)


def test_site_block():
    opener = FakeOpener(routes())
    text = tr.site_block(client(opener))
    assert "16.26.3" in text
    assert "### Server Scripts (3)" in text
    assert "| Customer | 1 |" in text and "| Sales Invoice | 2 |" in text
    assert all(r.get_method() == "GET" for r in opener.requests)
    assert all(r.get_header("Authorization") == "token KEY:SECRET" for r in opener.requests)
    assert "SECRET" not in text


def test_doctype_block_orders_events_and_counts_active():
    opener = FakeOpener(routes())
    text = tr.doctype_block(client(opener), "Sales Invoice", show_scripts=False)
    assert text.index("Before Save") < text.index("After Save")
    assert "1 active event script(s)." in text
    assert "### Custom DocPerm rows on `Sales Invoice` (2)" in text
    assert "ping" not in text


def test_missing_credentials_exit(monkeypatch, capsys):
    monkeypatch.delenv("FRAPPE_API_KEY", raising=False)
    monkeypatch.delenv("FRAPPE_API_SECRET", raising=False)
    try:
        tr.main(["--url", "https://erp.example.com"])
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("expected exit")
