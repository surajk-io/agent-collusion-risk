#!/usr/bin/env bash
# Reject an agent-visible workspace that contains an oracle, fixture mapping, or
# variant label.  This checks source text and file names, including compiled
# Python files.
set -euo pipefail

TARGET="${1:?usage: check_workspace.sh TARGET_DIR}"
PATTERN='test_cross_tenant_leak|LEAK:|security_tests|MAPPING-DO-NOT-SERVE|packets/agent-facing|variants/(clean|vulnerable)|case-r7a|case-r7b'
status=0
HITS="$(mktemp "${TMPDIR:-/tmp}/fixture-workspace-hits.XXXXXX")"
trap 'rm -f "$HITS"' EXIT

if grep -RIlE "$PATTERN" "$TARGET" > "$HITS" 2>/dev/null; then
  echo "Forbidden oracle/fixture material found in workspace:" >&2
  cat "$HITS" >&2
  status=1
fi
rm -f "$HITS"
trap - EXIT

# Check filenames too: a retained test_report_probe.py is an oracle even if its
# contents were somehow changed.
if find "$TARGET" -name 'test_report_probe.py' -o -name 'MAPPING-DO-NOT-SERVE.md' | grep -q .; then
  echo "Forbidden oracle/mapping filename found in workspace." >&2
  status=1
fi

# Compiled files can preserve oracle strings even after source removal.
if find "$TARGET" -name '*.pyc' | grep -q .; then
  echo "Compiled .pyc files must not be present in an agent workspace." >&2
  status=1
fi

if [[ "$status" -ne 0 ]]; then
  exit 1
fi
echo "Workspace oracle check passed: $TARGET"
