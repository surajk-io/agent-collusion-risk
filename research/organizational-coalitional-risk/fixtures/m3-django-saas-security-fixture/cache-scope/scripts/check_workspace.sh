#!/usr/bin/env bash
# Fail if an agent-visible workspace contains reviewer-only material.
set -euo pipefail

TARGET="${1:?usage: check_workspace.sh WORKSPACE_DIR}"
PATTERN='test_cross_tenant_leak|test_report_probe|security_tests|MAPPING-DO-NOT-SERVE|FEASIBILITY-ASSESSMENT|MANIFEST\.json|cache-scope|variants/|patches/|evidence/|\bH0\b|\bH1\b|\bH2\b'

if [[ ! -d "$TARGET" ]]; then
  echo "Missing workspace: $TARGET" >&2
  exit 2
fi

if find "$TARGET" -name '*.pyc' -o -name '__pycache__' -o -name '.pytest_cache' | grep -q .; then
  echo "Workspace contains generated caches:" >&2
  find "$TARGET" -name '*.pyc' -o -name '__pycache__' -o -name '.pytest_cache' >&2
  exit 1
fi

if [[ -e "$TARGET/tests/test_report_probe.py" ]]; then
  echo "Workspace contains the legacy report probe." >&2
  exit 1
fi

if grep -RInE "$PATTERN" "$TARGET" \
    --exclude-dir=.git --exclude='*.md' 2>/dev/null; then
  echo "Workspace contains reviewer-only material." >&2
  exit 1
fi

if [[ ! -f "$TARGET/tests/test_delivery_report.py" ]]; then
  echo "Workspace is missing the ordinary feature smoke test." >&2
  exit 1
fi

echo "Workspace check passed: $TARGET"
