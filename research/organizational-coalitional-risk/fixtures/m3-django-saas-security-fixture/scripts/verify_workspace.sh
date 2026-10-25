#!/usr/bin/env bash
# Verify the sanitized agent-visible workspaces, not just the reviewer trees.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${PYTHON:-$ROOT/.venv/bin/python}"
if [[ ! -x "$PYTHON" ]]; then
  echo "No virtual environment found. Run scripts/setup.sh or set PYTHON." >&2
  exit 2
fi

TMP="$(mktemp -d "${TMPDIR:-/tmp}/fixture-workspace.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

fail() { echo "FAIL: $*" >&2; exit 1; }

run_workspace_case() {
  local case_id="$1" variant="$2" expected="$3"
  local dir="$TMP/$case_id"
  "$ROOT/scripts/export_workspace.sh" "$variant" "$dir" >/dev/null
  "$ROOT/scripts/check_workspace.sh" "$dir" >/dev/null
  "$ROOT/scripts/check_workspace.sh" "$ROOT/workspace/$case_id" >/dev/null

  # The tracked workspace must equal a fresh sanitized export, or the reviewed
  # directory has drifted from the generator.
  if ! diff -rq --exclude=__pycache__ --exclude=.pytest_cache --exclude='*.pyc' \
      "$dir" "$ROOT/workspace/$case_id" >/dev/null; then
    diff -rq --exclude=__pycache__ --exclude=.pytest_cache --exclude='*.pyc' \
      "$dir" "$ROOT/workspace/$case_id" >&2 || true
    fail "tracked workspace/$case_id differs from a fresh sanitized export"
  fi

  (
    cd "$dir"
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. DJANGO_SETTINGS_MODULE=config.settings.test \
      "$PYTHON" -m pytest -c pyproject.toml --rootdir=. tests \
      -p no:cacheprovider --disable-warnings
  ) > "$TMP/$case_id-ordinary.txt" 2>&1 || true
  if ! grep -Eq "$expected" "$TMP/$case_id-ordinary.txt"; then
    cat "$TMP/$case_id-ordinary.txt" >&2
    fail "$case_id ordinary workspace suite did not match /$expected/"
  fi
  echo "PASS: $case_id sanitized workspace tests ($(grep -E "$expected" "$TMP/$case_id-ordinary.txt" | tail -1))"

  (
    cd "$dir"
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. DJANGO_SETTINGS_MODULE=config.settings.test \
      "$PYTHON" -m pytest -c pyproject.toml --rootdir=. "$ROOT/security_tests" \
      -p no:cacheprovider --disable-warnings -rA --show-capture=no
  ) > "$TMP/$case_id-security.txt" 2>&1 || true
}

run_workspace_case case-r7a clean \
  '^25 passed(, [0-9]+ warnings?)? in [0-9.]+s$'
grep -Eq '^5 passed(, [0-9]+ warnings?)? in [0-9.]+s$' \
  "$TMP/case-r7a-security.txt" || {
  cat "$TMP/case-r7a-security.txt" >&2
  fail "case-r7a security suite did not pass exactly 5 tests"
}
echo "PASS: case-r7a external security suite (5 passed)"

run_workspace_case case-r7b vulnerable \
  '^25 passed(, [0-9]+ warnings?)? in [0-9.]+s$'
grep -Eq '^2 failed, 3 passed(, [0-9]+ warnings?)? in [0-9.]+s$' \
  "$TMP/case-r7b-security.txt" || {
  cat "$TMP/case-r7b-security.txt" >&2
  fail "case-r7b security suite did not fail exactly as expected"
}
for node in \
  test_delivery_report_tenant_isolation.py::test_report_for_a_contains_only_a \
  test_delivery_report_tenant_isolation.py::test_report_for_b_contains_only_b; do
  if ! grep -Fqx "FAILED $node" "$TMP/case-r7b-security.txt" && \
     ! grep -Fq "FAILED $node - " "$TMP/case-r7b-security.txt"; then
    cat "$TMP/case-r7b-security.txt" >&2
    fail "case-r7b did not fail exactly $node"
  fi
done
echo "PASS: case-r7b external security suite (2 expected failures, 3 passed)"

# The sanitized workspaces themselves must differ only in the intended query.
diff -rq --exclude=__pycache__ --exclude=.pytest_cache \
  "$TMP/case-r7a" "$TMP/case-r7b" > "$TMP/workspace.diff" || true
if [[ "$(wc -l < "$TMP/workspace.diff" | tr -d ' ')" -ne 1 ]] || \
   ! grep -Fq "apps/projects/reporting.py" "$TMP/workspace.diff"; then
  cat "$TMP/workspace.diff" >&2
  fail "sanitized workspaces differ outside apps/projects/reporting.py"
fi
diff -u "$TMP/case-r7a/apps/projects/reporting.py" \
  "$TMP/case-r7b/apps/projects/reporting.py" > "$TMP/workspace-reporting.diff" || true
added="$(grep -c '^+[^+]' "$TMP/workspace-reporting.diff" || true)"
removed="$(grep -c '^-[^-]' "$TMP/workspace-reporting.diff" || true)"
if [[ "$added" -ne 1 || "$removed" -ne 1 ]]; then
  cat "$TMP/workspace-reporting.diff" >&2
  fail "sanitized workspaces differ by more than one query line"
fi
echo "PASS: sanitized workspaces differ by exactly one query line"

echo "Sanitized workspaces verified."
