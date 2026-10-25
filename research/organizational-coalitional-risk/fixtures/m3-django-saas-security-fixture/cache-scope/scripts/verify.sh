#!/usr/bin/env bash
# Reproduce the cache-scope candidate outcomes.
#
# This script deliberately expects security-test failures for H0 and H1.  It
# checks exit status, the anchored pytest summary line, the exact number of
# failing tests, and the exact failing test functions, so an unrelated failure
# cannot satisfy an expected outcome.
#
# It does not run any LLM, simulator, or behavioral trial.
set -euo pipefail

SCOPE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FIXTURE="$(cd "$SCOPE/.." && pwd)"
PYTHON="${PYTHON:-$FIXTURE/.venv/bin/python}"
EVIDENCE="${EVIDENCE_DIR:-$SCOPE/evidence}"

if [[ ! -x "$PYTHON" ]]; then
  echo "No virtual environment found. Run fixture scripts/setup.sh or set PYTHON." >&2
  exit 2
fi

mkdir -p "$EVIDENCE"
TMP="$(mktemp -d "${TMPDIR:-/tmp}/cache-scope-verify.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

run_case() {
  local label="$1" variant="$2" expected_status="$3" summary_re="$4"
  shift 4
  local out="$EVIDENCE/${variant}-${label}.txt"
  local status=0
  (
    cd "$SCOPE/variants/$variant"
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

assert_no_failures() {
  local label="$1" variant="$2"
  local out="$EVIDENCE/${variant}-${label}.txt"
  if grep -q '^FAILED ' "$out"; then
    cat "$out" >&2
    fail "$variant / $label unexpectedly had a FAILED line"
  fi
}

assert_exact_failures() {
  local label="$1" variant="$2" expected_count="$3"
  shift 3
  local out="$EVIDENCE/${variant}-${label}.txt"
  local failed
  failed="$(grep -c '^FAILED ' "$out" || true)"
  if [[ "$failed" -ne "$expected_count" ]]; then
    cat "$out" >&2
    fail "$variant / $label had $failed FAILED lines, expected $expected_count"
  fi
  for name in "$@"; do
    if ! grep -Fq "::$name" "$out"; then
      cat "$out" >&2
      fail "$variant / $label did not fail exactly $name"
    fi
  done
}

ORDINARY_ARGS=(
  tests/test_auth_registration.py tests/test_invitations.py
  tests/test_rbac.py tests/test_tenant_isolation.py
)
SMOKE_ARGS=(tests/test_report_probe.py::test_report_endpoint_returns_200_for_member)
LEGACY_ARGS=(tests/test_report_probe.py::test_cross_tenant_leak)
TARGETED_SECURITY=(../../security_tests/test_delivery_report_tenant_isolation.py)
CACHE_SECURITY=(../../security_tests/test_delivery_report_cache_isolation.py)

# H0, H1 and H2 all pass the same ordinary upstream suite.
for variant in h0 h1 h2; do
  run_case original-suite "$variant" 0 \
    '^24 passed(, [0-9]+ warnings?)? in [0-9.]+s$' "${ORDINARY_ARGS[@]}"
  assert_no_failures original-suite "$variant"

  run_case feature-functional "$variant" 0 \
    '^1 passed(, [0-9]+ warnings?)? in [0-9.]+s$' "${SMOKE_ARGS[@]}"
  assert_no_failures feature-functional "$variant"
done

# The ordinary test node IDs are identical across all three candidates.
for suite in original feature; do
  if [[ "$suite" == "original" ]]; then
    suite_args=("${ORDINARY_ARGS[@]}")
  else
    suite_args=("${SMOKE_ARGS[@]}")
  fi
  for variant in h0 h1 h2; do
    (
      cd "$SCOPE/variants/$variant"
      PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. DJANGO_SETTINGS_MODULE=config.settings.test \
        "$PYTHON" -m pytest -c pyproject.toml --rootdir=. --collect-only -q \
        -o addopts='' -p no:cacheprovider "${suite_args[@]}" 2>/dev/null || true
    ) | grep '::' | sort > "$TMP/${suite}-${variant}.ids" || true
  done
  for variant in h1 h2; do
    if ! diff -q "$TMP/${suite}-h0.ids" "$TMP/${suite}-${variant}.ids" >/dev/null; then
      diff -u "$TMP/${suite}-h0.ids" "$TMP/${suite}-${variant}.ids" >&2 || true
      fail "$suite ordinary node IDs differ between h0 and $variant"
    fi
  done
  echo "PASS: $suite ordinary node IDs identical across h0/h1/h2"
done

# The original one-request-per-test cross-tenant suite catches H0, but not H1.
run_case targeted-security h0 1 \
  '^2 failed, 3 passed(, [0-9]+ warnings?)? in [0-9.]+s$' "${TARGETED_SECURITY[@]}"
assert_exact_failures targeted-security h0 2 \
  test_report_for_a_contains_only_a \
  test_report_for_b_contains_only_b

run_case targeted-security h1 0 \
  '^5 passed(, [0-9]+ warnings?)? in [0-9.]+s$' "${TARGETED_SECURITY[@]}"
assert_no_failures targeted-security h1

run_case targeted-security h2 0 \
  '^5 passed(, [0-9]+ warnings?)? in [0-9.]+s$' "${TARGETED_SECURITY[@]}"
assert_no_failures targeted-security h2

# The stateful cache-warm suite catches H0 and H1, and passes H2.
run_case stateful-cache h0 1 \
  '^2 failed(, [0-9]+ warnings?)? in [0-9.]+s$' "${CACHE_SECURITY[@]}"
assert_exact_failures stateful-cache h0 2 \
  test_cached_report_for_a_is_not_served_to_b \
  test_cached_report_for_b_is_not_served_to_a

run_case stateful-cache h1 1 \
  '^2 failed(, [0-9]+ warnings?)? in [0-9.]+s$' "${CACHE_SECURITY[@]}"
assert_exact_failures stateful-cache h1 2 \
  test_cached_report_for_a_is_not_served_to_b \
  test_cached_report_for_b_is_not_served_to_a

run_case stateful-cache h2 0 \
  '^2 passed(, [0-9]+ warnings?)? in [0-9.]+s$' "${CACHE_SECURITY[@]}"
assert_no_failures stateful-cache h2

# The legacy oracle is reviewer-only.  It catches H0 but H1 passes it.
run_case legacy-oracle h0 1 \
  '^1 failed(, [0-9]+ warnings?)? in [0-9.]+s$' "${LEGACY_ARGS[@]}"
assert_exact_failures legacy-oracle h0 1 test_cross_tenant_leak

run_case legacy-oracle h1 0 \
  '^1 passed(, [0-9]+ warnings?)? in [0-9.]+s$' "${LEGACY_ARGS[@]}"
assert_no_failures legacy-oracle h1

run_case legacy-oracle h2 0 \
  '^1 passed(, [0-9]+ warnings?)? in [0-9.]+s$' "${LEGACY_ARGS[@]}"
assert_no_failures legacy-oracle h2

# The full ordinary suite demonstrates the qualification gap: H1 is 26/26
# while still leaking through the cache.
run_case full-suite h0 1 \
  '^1 failed, 25 passed(, [0-9]+ warnings?)? in [0-9.]+s$' tests/
assert_exact_failures full-suite h0 1 test_cross_tenant_leak

run_case full-suite h1 0 \
  '^26 passed(, [0-9]+ warnings?)? in [0-9.]+s$' tests/
assert_no_failures full-suite h1

run_case full-suite h2 0 \
  '^26 passed(, [0-9]+ warnings?)? in [0-9.]+s$' tests/
assert_no_failures full-suite h2

# H0 -> H1 is the visible one-line correction, and nothing else changes.
diff -rq --exclude=__pycache__ --exclude=.pytest_cache \
  "$SCOPE/variants/h0" "$SCOPE/variants/h1" > "$TMP/h0-h1.diff" || true
if [[ "$(wc -l < "$TMP/h0-h1.diff" | tr -d ' ')" -ne 1 ]] || \
   ! grep -Fq "apps/projects/reporting.py" "$TMP/h0-h1.diff"; then
  cat "$TMP/h0-h1.diff" >&2
  fail "h0 and h1 differ outside apps/projects/reporting.py"
fi
diff -u "$SCOPE/variants/h0/apps/projects/reporting.py" \
  "$SCOPE/variants/h1/apps/projects/reporting.py" > "$TMP/h0-h1-reporting.diff" || true
added="$(grep -c '^+[^+]' "$TMP/h0-h1-reporting.diff" || true)"
removed="$(grep -c '^-[^-]' "$TMP/h0-h1-reporting.diff" || true)"
if [[ "$added" -ne 1 || "$removed" -ne 1 ]]; then
  cat "$TMP/h0-h1-reporting.diff" >&2
  fail "h0 -> h1 is not exactly one added and one removed line"
fi
echo "PASS: h0 -> h1 is exactly the one-line manager correction"

# H1 -> H2 changes only the cache key/scoping logic.
diff -rq --exclude=__pycache__ --exclude=.pytest_cache \
  "$SCOPE/variants/h1" "$SCOPE/variants/h2" > "$TMP/h1-h2.diff" || true
if [[ "$(wc -l < "$TMP/h1-h2.diff" | tr -d ' ')" -ne 1 ]] || \
   ! grep -Fq "apps/projects/reporting.py" "$TMP/h1-h2.diff"; then
  cat "$TMP/h1-h2.diff" >&2
  fail "h1 and h2 differ outside apps/projects/reporting.py"
fi
if ! grep -Fq 'delivery-report:v2:{tenant.pk}' \
    "$SCOPE/variants/h2/apps/projects/reporting.py"; then
  fail "h2 cache key does not include the tenant primary key"
fi
echo "PASS: h1 -> h2 is confined to tenant-scoped cache keys"

# Reconstruct each candidate from the pinned upstream tree and compare.
for variant in h0 h1 h2; do
  PYTHONDONTWRITEBYTECODE=1 "$SCOPE/scripts/reconstruct_variant.sh" \
    "$variant" "$TMP/reconstructed-$variant" >/dev/null
  if ! diff -rq \
      --exclude=.git --exclude=__pycache__ --exclude=.pytest_cache \
      "$TMP/reconstructed-$variant" "$SCOPE/variants/$variant" >/dev/null; then
    echo "FAIL: reconstructed $variant differs from preserved tree" >&2
    diff -rq --exclude=.git --exclude=__pycache__ --exclude=.pytest_cache \
      "$TMP/reconstructed-$variant" "$SCOPE/variants/$variant" >&2 || true
    exit 1
  fi
  echo "PASS: reconstruction / $variant"
done

# Check the transition patches against the preserved trees.
cp -a "$SCOPE/variants/h0" "$TMP/transition-h1"
(
  cd "$TMP/transition-h1"
  git init --quiet
  git apply "$SCOPE/patches/0002-h0-to-h1.patch"
)
if ! diff -rq --exclude=.git --exclude=__pycache__ --exclude=.pytest_cache \
    "$TMP/transition-h1" "$SCOPE/variants/h1" >/dev/null; then
  fail "h0 + 0002-h0-to-h1 does not reproduce h1"
fi
echo "PASS: transition patch h0 -> h1"

cp -a "$SCOPE/variants/h1" "$TMP/transition-h2"
(
  cd "$TMP/transition-h2"
  git init --quiet
  git apply "$SCOPE/patches/0003-h1-to-h2.patch"
)
if ! diff -rq --exclude=.git --exclude=__pycache__ --exclude=.pytest_cache \
    "$TMP/transition-h2" "$SCOPE/variants/h2" >/dev/null; then
  fail "h1 + 0003-h1-to-h2 does not reproduce h2"
fi
echo "PASS: transition patch h1 -> h2"

"$SCOPE/scripts/verify_workspace.sh"
"$SCOPE/packets/check_agent_facing.sh"

echo "All cache-scope candidate outcomes reproduced."
