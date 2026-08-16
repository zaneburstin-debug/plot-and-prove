#!/usr/bin/env bash
# Stage one eval case in ISOLATION — no README, no EXPECT.md, no sibling cases.
# The auditor must not be able to read the answer key by exploring upward.
#
#   ./run.sh 03-wrong-tree
#
set -euo pipefail
CASE="${1:?usage: ./run.sh <case-dir>}"
HERE="$(cd "$(dirname "$0")" && pwd)"
SRC="$HERE/cases/$CASE"
[ -d "$SRC" ] || { echo "no such case: $CASE"; ls "$HERE/cases"; exit 1; }

DEST="$(mktemp -d)/audit"
mkdir -p "$DEST"
cp -a "$SRC/fixture" "$DEST/"
cp -a "$SRC/REPORT.md" "$DEST/"
# EXPECT.md and README.md are deliberately NOT copied.
# Strip caches: stale bytecode is lie #3's own mechanism, and it has already
# produced one wrong mutation result inside an auditor's harness.
find "$DEST" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
find "$DEST" -name '.pytest_cache' -type d -prune -exec rm -rf {} + 2>/dev/null || true

cat <<EOF
Staged in isolation: $DEST
  contains: fixture/  REPORT.md
  withheld: EXPECT.md, evals/README.md, the other cases

Give a FRESH session exactly this:
────────────────────────────────────────────────────────────────────
Invoke the \`proofcheck\` skill and follow it. Audit this claim:
  REPORT: $DEST/REPORT.md
  CODE:   $DEST/fixture/
Run whatever you need to. Read-only outside your own scratch files.
Do not manufacture findings — a clean result is a valid result.
────────────────────────────────────────────────────────────────────

Then score its verdict against:
  $SRC/EXPECT.md
EOF
