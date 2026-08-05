#!/usr/bin/env bash
# Sync vendored pipelines/gtm_generator/ from the upstream generator repo.
#
# Requires an environment variable pointing at your local checkout of the
# upstream repo:
#
#   export UPSTREAM_GTM_GENERATOR_PATH=/path/to/upstream/checkout
#   ./scripts/sync-from-upstream.sh
#
# The path itself is not committed — different collaborators keep the
# upstream at different absolute paths on disk, and the private repo
# name is deliberately not baked in here. See VENDOR.md for the full
# manual + the copy-up gate you must run before committing sync results.
#
# What this does:
#   1. Verifies UPSTREAM_GTM_GENERATOR_PATH is set and contains
#      pipelines/gtm_generator/.
#   2. Rsyncs the module tree (excluding __pycache__ + .pyc) into
#      this repo's pipelines/gtm_generator/.
#   3. Reapplies the vendor-provenance header block at the top of every
#      copied .py file, injecting the current upstream commit SHA.
#   4. Emits the new SHA to stdout so it can be captured for the commit
#      message + VENDOR.md changelog line.
#
# What this does NOT do:
#   - Run the copy-up private-data gate. That is a manual step per
#     VENDOR.md; do NOT commit the sync result without running it.
#   - Run tests. Do that separately after the sync + before commit.
#   - Push. Local-only sync operation.
set -euo pipefail

UPSTREAM="${UPSTREAM_GTM_GENERATOR_PATH:-}"
if [ -z "$UPSTREAM" ]; then
  echo "error: set UPSTREAM_GTM_GENERATOR_PATH to your upstream checkout root" >&2
  exit 1
fi
if [ ! -d "$UPSTREAM/pipelines/gtm_generator" ]; then
  echo "error: $UPSTREAM/pipelines/gtm_generator not found" >&2
  echo "       set UPSTREAM_GTM_GENERATOR_PATH to the ROOT of the upstream checkout" >&2
  echo "       (the directory that CONTAINS pipelines/, not pipelines/ itself)" >&2
  exit 1
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$REPO_ROOT/pipelines/gtm_generator"

# Capture the upstream SHA before touching anything. If the upstream isn't a
# git repo (unusual but possible), we still want to fail loud rather than
# vendor an unpinned snapshot.
UPSTREAM_SHA="$(git -C "$UPSTREAM" rev-parse HEAD 2>/dev/null || true)"
if [ -z "$UPSTREAM_SHA" ]; then
  echo "error: $UPSTREAM does not appear to be a git checkout" >&2
  echo "       vendoring an unpinned snapshot defeats the purpose of provenance" >&2
  exit 1
fi

echo "syncing from $UPSTREAM (SHA $UPSTREAM_SHA)"

# Rsync module tree. --delete so files removed upstream are removed here too;
# provenance-header rewrite in the next step reintroduces the vendor block.
rsync -av --delete \
  --exclude='__pycache__/' \
  --exclude='*.pyc' \
  "$UPSTREAM/pipelines/gtm_generator/" \
  "$DEST/"

# Reapply provenance headers to every .py file in the vendored tree. Note:
# cli.py is NOT vendored (it lives in the same directory but is strategy-sprint's
# own wrapper), so skip it. Any other locally-authored files in the vendored
# dir would also need a skip line — none today.
HEADER="# -----------------------------------------------------------------------------
# VENDORED code. Do NOT edit here; edit upstream and re-sync.
#
# Upstream: GTM plan generator (private repo, path-parameterised via
# UPSTREAM_GTM_GENERATOR_PATH env var; see VENDOR.md).
# Source SHA: $UPSTREAM_SHA
# Sync procedure: scripts/sync-from-upstream.sh
#
# Any change made directly to this file will be overwritten on the next
# sync. If you need to change behavior, change the upstream file first,
# then re-run the sync script.
# -----------------------------------------------------------------------------
"

while IFS= read -r -d '' f; do
  base="$(basename "$f")"
  if [ "$base" = "cli.py" ]; then
    continue  # cli.py is not vendored
  fi
  # Strip any existing provenance block (marked by the -- boundary lines) so
  # the sync is idempotent. If no header exists yet, the sed no-ops.
  python3 - "$f" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
content = path.read_text()
lines = content.splitlines(keepends=True)

# Detect an existing provenance header: block of comment lines at top of file
# that includes the phrase "VENDORED code". If found, strip until (and
# including) the trailing "----" line.
if lines and lines[0].startswith("#") and any(
    "VENDORED code" in line for line in lines[:20]
):
    end = 0
    for i, line in enumerate(lines[:50]):
        if line.strip().startswith("# --") and i > 5:
            end = i + 1
            break
    if end > 0:
        # Also consume any blank line immediately after the header.
        while end < len(lines) and lines[end].strip() == "":
            end += 1
        content = "".join(lines[end:])
        path.write_text(content)
PY
  # Prepend the current header.
  printf '%s\n%s' "$HEADER" "$(cat "$f")" > "$f"
done < <(find "$DEST" -name '*.py' -print0)

echo ""
echo "sync complete."
echo "vendored SHA: $UPSTREAM_SHA"
echo ""
echo "NEXT STEPS (do NOT skip):"
echo "  1. Run the copy-up private-data gate (see VENDOR.md §Copy-up gate)."
echo "  2. Run tests: pytest tests/gtm_generator/"
echo "  3. Update VENDOR.md changelog with the SHA above."
echo "  4. THEN commit."
