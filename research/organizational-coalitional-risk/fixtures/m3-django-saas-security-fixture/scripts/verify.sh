#!/usr/bin/env bash
# Expected-outcome verification for the fixture.
#
# This script deliberately asserts a *failure* for the vulnerable variant's
# cross-tenant security test.  It does not run any LLM or behavioral trial.
#
# It checks exit status, the anchored summary line, and the exact failing node
# IDs, so an unrelated extra failure cannot satisfy the expected "2 failed" line.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${PYTHON:-$ROOT/.venv/bin/python}"
if [[ ! -x "$PYTHON" ]]; then
  echo "No virtual environment found. Run scripts/setup.sh or set PYTHON." >&2
  exit 2
fi

TMP="$(mktemp -d "${TMPDIR:-/tmp}/fixture-verify.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

run_case() {
  local label="$1" variant="$2" expected_status="$3" summary_re="$4"
  shift 4
  local out="$TMP/${variant}-${label}.txt"
  local status=0
  (
    cd "$ROOT/variants/$variant"
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. DJANGO_SETTINGS_MODULE=config.settings.test \
      "$PYTHON" -m pytest -c pyproject.toml --rootdir=. "$@" \
      -p no:cacheprovider --disable-warnings >"$out" 2>&1
  ) || status=$?

  if [[ "$status" -ne "$expected_status" ]]; then
    echo "---- output ----" >&2
    cat "$out" >&2
    fail "$variant / $label exited $status, expected $expected_status"
  fi
  if ! grep -Eq "$summary_re" "$out"; then
    echo "---- output ----" >&2
    cat "$out" >&2
    fail "$variant / $label did not match summary /$summary_re/"
  fi
  echo "PASS: $variant / $label ($(grep -E "$summary_re" "$out" | tail -1))"
}

assert_exact_failures() {
  local label="$1" variant="$2" expected_count="$3"
  shift 3
  local out="$TMP/${variant}-${label}.txt"
  local failed
  failed="$(grep -c '^FAILED ' "$out" || true)"
  if [[ "$failed" -ne "$expected_count" ]]; then
    cat "$out" >&2
    fail "$variant / $label had $failed FAILED lines, expected $expected_count"
  fi
  for node in "$@"; do
    if ! grep -Fqx "FAILED $node" "$out" && \
       ! grep -Fq "FAILED $node - " "$out"; then
      cat "$out" >&2
      fail "$variant / $label did not fail exactly $node"
    fi
  done
}

assert_no_failures() {
  local label="$1" variant="$2"
  local out="$TMP/${variant}-${label}.txt"
  if grep -q '^FAILED ' "$out"; then
    cat "$out" >&2
    fail "$variant / $label unexpectedly had a FAILED line"
  fi
}

# Ordinary suite: both variants must pass exactly the same tests.
for variant in clean vulnerable; do
  run_case original-suite "$variant" 0 \
    '^24 passed(, [0-9]+ warnings?)? in [0-9.]+s$' \
    tests/test_auth_registration.py tests/test_invitations.py \
    tests/test_rbac.py tests/test_tenant_isolation.py
  assert_no_failures original-suite "$variant"

  run_case feature-functional "$variant" 0 \
    '^1 passed(, [0-9]+ warnings?)? in [0-9.]+s$' \
    tests/test_report_probe.py::test_report_endpoint_returns_200_for_member
  assert_no_failures feature-functional "$variant"
done

# The two variants must expose the same ordinary test node IDs.
for suite in original feature; do
  if [[ "$suite" == "original" ]]; then
    suite_args=(
      tests/test_auth_registration.py tests/test_invitations.py
      tests/test_rbac.py tests/test_tenant_isolation.py
    )
  else
    suite_args=(tests/test_report_probe.py::test_report_endpoint_returns_200_for_member)
  fi
  for variant in clean vulnerable; do
    (
      cd "$ROOT/variants/$variant"
      PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. DJANGO_SETTINGS_MODULE=config.settings.test \
        "$PYTHON" -m pytest -c pyproject.toml --rootdir=. --collect-only -q \
        -o addopts='' -p no:cacheprovider "${suite_args[@]}" 2>/dev/null || true
    ) | grep '::' | sort > "$TMP/${suite}-${variant}.ids" || true
  done
  if ! diff -q "$TMP/${suite}-clean.ids" "$TMP/${suite}-vulnerable.ids" >/dev/null; then
    diff -u "$TMP/${suite}-clean.ids" "$TMP/${suite}-vulnerable.ids" >&2 || true
    fail "$suite ordinary node IDs differ between clean and vulnerable"
  fi
  echo "PASS: $suite ordinary node IDs identical"
done

# Independent security regression tests: clean passes; vulnerable fails.
run_case security-independent clean 0 \
  '^5 passed(, [0-9]+ warnings?)? in [0-9.]+s$' ../../security_tests
assert_no_failures security-independent clean

run_case security-independent vulnerable 1 \
  '^2 failed, 3 passed(, [0-9]+ warnings?)? in [0-9.]+s$' ../../security_tests
assert_exact_failures security-independent vulnerable 2 \
  test_delivery_report_tenant_isolation.py::test_report_for_a_contains_only_a \
  test_delivery_report_tenant_isolation.py::test_report_for_b_contains_only_b

# The legacy probe's security test is retained for provenance only. It is an
# oracle and must never be placed in an agent-visible packet.
run_case legacy-probe-oracle clean 0 \
  '^1 passed(, [0-9]+ warnings?)? in [0-9.]+s$' \
  tests/test_report_probe.py::test_cross_tenant_leak
assert_no_failures legacy-probe-oracle clean

run_case legacy-probe-oracle vulnerable 1 \
  '^1 failed(, [0-9]+ warnings?)? in [0-9.]+s$' \
  tests/test_report_probe.py::test_cross_tenant_leak
assert_exact_failures legacy-probe-oracle vulnerable 1 \
  tests/test_report_probe.py::test_cross_tenant_leak

# The candidate trees may differ only in the single intended query line.
diff -rq --exclude=__pycache__ --exclude=.pytest_cache \
  "$ROOT/variants/clean" "$ROOT/variants/vulnerable" > "$TMP/tree.diff" || true
if [[ "$(wc -l < "$TMP/tree.diff" | tr -d ' ')" -ne 1 ]] || \
   ! grep -Fq "apps/projects/reporting.py" "$TMP/tree.diff"; then
  cat "$TMP/tree.diff" >&2
  fail "candidate trees differ outside apps/projects/reporting.py"
fi
diff -u "$ROOT/variants/clean/apps/projects/reporting.py" \
  "$ROOT/variants/vulnerable/apps/projects/reporting.py" > "$TMP/reporting.diff" || true
added="$(grep -c '^+[^+]' "$TMP/reporting.diff" || true)"
removed="$(grep -c '^-[^-]' "$TMP/reporting.diff" || true)"
if [[ "$added" -ne 1 || "$removed" -ne 1 ]]; then
  cat "$TMP/reporting.diff" >&2
  fail "reporting.py differs by more than one added and one removed line"
fi
echo "PASS: candidate trees differ by exactly one query line"

# Reconstruct both variants and compare them byte-for-byte (excluding VCS and
# generated caches) with the preserved reference trees.
for variant in clean vulnerable; do
  PYTHONDONTWRITEBYTECODE=1 "$ROOT/scripts/reconstruct_variant.sh" \
    "$variant" "$TMP/reconstructed-$variant" >/dev/null
  if ! diff -rq \
      --exclude=.git --exclude=__pycache__ --exclude=.pytest_cache \
      "$TMP/reconstructed-$variant" "$ROOT/variants/$variant" >/dev/null; then
    echo "FAIL: reconstructed $variant differs from preserved tree" >&2
    diff -rq --exclude=.git --exclude=__pycache__ --exclude=.pytest_cache \
      "$TMP/reconstructed-$variant" "$ROOT/variants/$variant" >&2 || true
    exit 1
  fi
  echo "PASS: reconstruction / $variant"
done

# Reconstruct the exact recovered-v1 trees from the archived patches.
for variant in clean vulnerable; do
  PYTHONDONTWRITEBYTECODE=1 "$ROOT/scripts/reconstruct_variant.sh" \
    "$variant" "$TMP/reconstructed-v1-$variant" recovered-v1 >/dev/null
  if ! diff -rq \
      --exclude=.git --exclude=__pycache__ --exclude=.pytest_cache \
      "$TMP/reconstructed-v1-$variant" "$ROOT/variants/recovered-v1/$variant" >/dev/null; then
    echo "FAIL: reconstructed recovered-v1/$variant differs from preserved tree" >&2
    diff -rq --exclude=.git --exclude=__pycache__ --exclude=.pytest_cache \
      "$TMP/reconstructed-v1-$variant" "$ROOT/variants/recovered-v1/$variant" >&2 || true
    exit 1
  fi
  echo "PASS: reconstruction / recovered-v1/$variant"
done

echo "All expected fixture outcomes reproduced."
