#!/usr/bin/env bash
# Reconstruct a variant from the pinned upstream tree and its exact patch.
# Supports both a local Git clone and the vendored tree committed here. In the
# vendored case the content is checked against the pinned Git tree hash.
#
# Usage: reconstruct_variant.sh {clean|vulnerable} TARGET_DIR [candidate|recovered-v1]
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VARIANT="${1:?usage: reconstruct_variant.sh clean-or-vulnerable TARGET_DIR [candidate|recovered-v1]}"
TARGET="${2:?usage: reconstruct_variant.sh clean-or-vulnerable TARGET_DIR [candidate|recovered-v1]}"
GENERATION="${3:-candidate}"
COMMIT="7ff2daaf78290ea5350e6373367f3d2172d4c6a4"
UPSTREAM_TREE="7741d0fcbf487cf9270785c212d7617898e349e9"
UPSTREAM="$ROOT/upstream/django-saas-starter"

case "$GENERATION" in
  candidate) PATCH_DIR="$ROOT/patches" ;;
  recovered-v1) PATCH_DIR="$ROOT/patches/recovered-v1" ;;
  *) echo "Unknown generation: $GENERATION" >&2; exit 2 ;;
esac

case "$VARIANT" in
  clean)
    PATCH="$PATCH_DIR/0001-feature-clean.patch"
    ;;
  vulnerable)
    PATCH="$PATCH_DIR/0001-feature-vulnerable.patch"
    ;;
  *)
    echo "Unknown variant: $VARIANT" >&2
    exit 2
    ;;
esac

if [[ ! -d "$UPSTREAM" ]]; then
  echo "Missing upstream tree: $UPSTREAM" >&2
  exit 2
fi

rm -rf "$TARGET"
mkdir -p "$TARGET"

if [[ -e "$UPSTREAM/.git" ]]; then
  # Local development clone: clone the pinned commit exactly.
  git clone --quiet "$UPSTREAM" "$TARGET"
  git -C "$TARGET" checkout --quiet "$COMMIT"
  ACTUAL_TREE="$(git -C "$TARGET" rev-parse HEAD^{tree})"
else
  # Committed review copy: copy the pinned working tree and verify its Git tree
  # hash, which is content- and mode-identical to the pinned commit's tree.
  rsync -a --exclude='.git' "$UPSTREAM/" "$TARGET/"
  ACTUAL_TREE="$(
    cd "$TARGET"
    git init --quiet
    git add -A -f
    git write-tree
  )"
fi

if [[ "$ACTUAL_TREE" != "$UPSTREAM_TREE" ]]; then
  echo "Upstream tree mismatch: $ACTUAL_TREE != $UPSTREAM_TREE" >&2
  exit 1
fi

git -C "$TARGET" apply --check "$PATCH"
git -C "$TARGET" apply "$PATCH"

echo "Reconstructed $VARIANT at $TARGET from upstream tree $UPSTREAM_TREE"
echo "Pinned commit: $COMMIT"
