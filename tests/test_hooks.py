"""Hooks are run the way Claude Code runs them: JSON on stdin, JSON on stdout."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

HOOKS = Path(__file__).resolve().parent.parent / "hooks"


def run(hook: str, payload: dict, env=None) -> dict | None:
    proc = subprocess.run(
        [sys.executable, str(HOOKS / hook)],
        input=json.dumps(payload), capture_output=True, text=True, env=env, timeout=20,
    )
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout) if proc.stdout.strip() else None


# guard_bash.py

@pytest.mark.parametrize("command", [
    "bench --site erp.example.com drop-site erp.example.com",
    "bench --site dev.localhost reinstall",
    "bench --site erp.example.com restore backup.sql.gz",
    "bench set-config -g server_script_enabled 1",
    "docker system prune -af",
    "bench --site erp.example.com migrate",
    "bench --site erp.example.com execute app.module.fn",
    "mysql -e 'DELETE FROM tabUser'",
    "curl -X PUT https://erp.example.com/api/resource/Sales%20Invoice/SI-1 -d '{}'",
    "git push --force origin main",
])
def test_guard_asks(command):
    out = run("guard_bash.py", {"tool_input": {"command": command}})
    assert out is not None, command
    spec = out["hookSpecificOutput"]
    assert spec["hookEventName"] == "PreToolUse"
    assert spec["permissionDecision"] == "ask"
    assert spec["permissionDecisionReason"]


@pytest.mark.parametrize("command", [
    "bench --site dev.localhost migrate",
    "bench --site test_site migrate",
    "bench --site dev.localhost run-tests --app myapp",
    "bench start",
    "curl https://erp.example.com/api/resource/Customer",
    "git status",
    "python3 .exoskeleton-integrator/scripts/triage_rest.py --url https://erp.example.com",
])
def test_guard_allows(command):
    assert run("guard_bash.py", {"tool_input": {"command": command}}) is None, command


# post_edit.py

@pytest.mark.parametrize("path,needle", [
    ("/b/apps/myapp/myapp/sales/doctype/order/order.json", "DocType JSON"),
    ("/b/apps/myapp/myapp/hooks.py", "hooks.py"),
    ("/b/apps/myapp/myapp/patches.txt", "patches.txt"),
    ("/b/apps/myapp/myapp/fixtures/custom_field.json", "fixture"),
    ("C:\\b\\apps\\myapp\\myapp\\sales\\doctype\\order\\order.json", "DocType JSON"),
])
def test_post_edit_reminds(path, needle):
    out = run("post_edit.py", {"tool_input": {"file_path": path}})
    assert out is not None
    assert needle in out["hookSpecificOutput"]["additionalContext"]


@pytest.mark.parametrize("path", [
    "/b/apps/myapp/myapp/sales/doctype/order/order.py",
    "/b/apps/myapp/README.md",
])
def test_post_edit_quiet(path):
    assert run("post_edit.py", {"tool_input": {"file_path": path}}) is None


# session_context.py

def make_bench(root: Path) -> Path:
    bench = root / "frappe-bench"
    (bench / "apps" / "frappe" / "frappe").mkdir(parents=True)
    (bench / "apps" / "frappe" / "frappe" / "__init__.py").write_text('__version__ = "16.26.3"\n')
    sites = bench / "sites"
    (sites / "dev.localhost").mkdir(parents=True)
    (sites / "apps.txt").write_text("frappe\nerpnext\n")
    (sites / "currentsite.txt").write_text("dev.localhost")
    (sites / "common_site_config.json").write_text(json.dumps({"server_script_enabled": 1, "db_password": "SECRET"}))
    (sites / "dev.localhost" / "site_config.json").write_text(
        json.dumps({"developer_mode": 1, "allow_tests": 1, "db_password": "SECRET"}))
    return bench


def test_session_context_in_bench(tmp_path):
    bench = make_bench(tmp_path)
    out = run("session_context.py", {"cwd": str(bench / "apps" / "frappe")})
    ctx = out["hookSpecificOutput"]["additionalContext"]
    assert out["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    assert "16.26.3" in ctx and "frappe, erpnext" in ctx and "dev.localhost" in ctx
    assert "server_script_enabled (bench-wide): True" in ctx
    assert "SECRET" not in ctx


def test_session_context_outside_bench(tmp_path):
    env = {k: v for k, v in __import__("os").environ.items() if k != "FRAPPE_BENCH_PATH"}
    assert run("session_context.py", {"cwd": str(tmp_path)}, env=env) is None
