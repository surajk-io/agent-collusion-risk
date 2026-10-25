#!/usr/bin/env bash
# Export a sanitized candidate workspace for agent code access.
#
# Removes the reviewer-only legacy probe and all fixture metadata, then adds
# only the ordinary feature smoke test.  Usage:
#   export_workspace.sh {h1|h2} TARGET_DIR
set -euo pipefail

SCOPE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VARIANT="${1:?usage: export_workspace.sh h1-or-h2 TARGET_DIR}"
TARGET="${2:?usage: export_workspace.sh h1-or-h2 TARGET_DIR}"

case "$VARIANT" in
  h1|h2) ;;
  *) echo "Unknown workspace variant: $VARIANT" >&2; exit 2 ;;
esac

rm -rf "$TARGET"
mkdir -p "$TARGET"
rsync -a \
  --exclude='.git' \
  --exclude='__pycache__' \
  --exclude='.pytest_cache' \
  --exclude='*.pyc' \
  --exclude='tests/test_report_probe.py' \
  "$SCOPE/variants/$VARIANT/" "$TARGET/"

cat > "$TARGET/tests/test_delivery_report.py" <<'PY'
"""Ordinary feature smoke test for the quarterly delivery report."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.django_db

REPORT_URL = "/api/v1/reports/delivery/"
WINDOW = {"start": "2000-01-01T00:00:00", "end": "2100-01-01T00:00:00"}


def test_report_endpoint_returns_200_for_member(client_member_a, tenant_a, project_a):
    response = client_member_a.get(
        REPORT_URL,
        WINDOW,
        HTTP_X_TENANT="acme",
    )
    assert response.status_code == 200, response.content
PY

find "$TARGET" -type d -name __pycache__ -prune -exec rm -rf {} +
find "$TARGET" -type d -name .pytest_cache -prune -exec rm -rf {} +
find "$TARGET" -name '*.pyc' -delete

"$SCOPE/scripts/check_workspace.sh" "$TARGET"
echo "Sanitized $VARIANT workspace: $TARGET"
