#!/usr/bin/env bash
# Reconstruct one cache-scope candidate from the pinned upstream tree.
#
# Usage: reconstruct_variant.sh {h0|h1|h2} TARGET_DIR
set -euo pipefail

SCOPE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FIXTURE="$(cd "$SCOPE/.." && pwd)"
VARIANT="${1:?usage: reconstruct_variant.sh h0-or-h1-or-h2 TARGET_DIR}"
TARGET="${2:?usage: reconstruct_variant.sh h0-or-h1-or-h2 TARGET_DIR}"
COMMIT="7ff2daaf78290ea5350e6373367f3d2172d4c6a4"
UPSTREAM_TREE="7741d0fcbf487cf9270785c212d7617898e349e9"
UPSTREAM="$FIXTURE/upstream/django-saas-starter"

case "$VARIANT" in
  h0|h1|h2) PATCH="$SCOPE/patches/0001-feature-$VARIANT.patch" ;;
  *) echo "Unknown cache-scope variant: $VARIANT" >&2; exit 2 ;;
esac

if [[ ! -d "$UPSTREAM" ]]; then
  echo "Missing pinned upstream tree: $UPSTREAM" >&2
  exit 2
fi

rm -rf "$TARGET"
mkdir -p "$TARGET"
rsync -a --exclude='.git' "$UPSTREAM/" "$TARGET/"
ACTUAL_TREE="$(
  cd "$TARGET"
  git init --quiet
  git add -A -f
  git write-tree
)"
if [[ "$ACTUAL_TREE" != "$UPSTREAM_TREE" ]]; then
  echo "Upstream tree mismatch: $ACTUAL_TREE != $UPSTREAM_TREE" >&2
  exit 1
fi

git -C "$TARGET" apply --check "$PATCH"
git -C "$TARGET" apply "$PATCH"
echo "Reconstructed $VARIANT at $TARGET from upstream tree $UPSTREAM_TREE"
echo "Pinned commit: $COMMIT"
