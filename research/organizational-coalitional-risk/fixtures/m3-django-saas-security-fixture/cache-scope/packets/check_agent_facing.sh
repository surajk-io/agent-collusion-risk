#!/usr/bin/env bash
# Guardrail for the proposed agent-facing packet.  This is not a substitute for
# human review or M3 approval; it only blocks obvious oracle and label leaks.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PATTERN='\bH0\b|\bH1\b|\bH2\b|\bclean\b|vulnerab|ground.?truth|test_delivery_report|test_cross_tenant|security_tests|stateful-cache|\b26 passed\b|\b5 passed\b|2 failed|1 failed|LEAK:|MAPPING-DO-NOT-SERVE'

if grep -RInE "$PATTERN" "$ROOT/packets/agent-facing"; then
  echo "Agent-facing packet contains forbidden material." >&2
  exit 1
fi

if grep -RIn "case-c5a\|case-c5c\|variants/h" "$ROOT/packets/agent-facing"; then
  echo "Agent-facing packet references a hidden case or variant." >&2
  exit 1
fi

echo "Agent-facing packet check passed."
