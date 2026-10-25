#!/usr/bin/env bash
# Check that tracked sanitized workspaces match fresh exports and pass their
# ordinary tests.  This does not run the hidden report-security tests.
set -euo pipefail

SCOPE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FIXTURE="$(cd "$SCOPE/.." && pwd)"
PYTHON="${PYTHON:-$FIXTURE/.venv/bin/python}"
TMP="$(mktemp -d "${TMPDIR:-/tmp}/cache-scope-workspace.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

for variant in h1 h2; do
  tracked="$SCOPE/workspace/$variant"
  fresh="$TMP/$variant"
  "$SCOPE/scripts/export_workspace.sh" "$variant" "$fresh" >/dev/null

  if ! diff -rq --exclude=.git --exclude=__pycache__ --exclude=.pytest_cache \
      "$fresh" "$tracked" >/dev/null; then
    diff -rq --exclude=.git --exclude=__pycache__ --exclude=.pytest_cache \
      "$fresh" "$tracked" >&2 || true
    fail "tracked workspace $variant differs from a fresh export"
  fi
  echo "PASS: workspace $variant matches fresh export"

  status=0
  (
    cd "$tracked"
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. DJANGO_SETTINGS_MODULE=config.settings.test \
      "$PYTHON" -m pytest -c pyproject.toml --rootdir=. \
      -p no:cacheprovider --disable-warnings tests/
  ) || status=$?
  if [[ "$status" -ne 0 ]]; then
    fail "workspace $variant ordinary tests failed"
  fi
  echo "PASS: workspace $variant ordinary tests"
done

echo "All sanitized workspace checks passed."
