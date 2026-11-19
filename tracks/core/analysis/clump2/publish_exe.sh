#!/usr/bin/env bash
# Publish the tested executables of branch core/clump-table for the tracks' scouting runs
# (decision 0013) into scratch/core/exe/core_clump-table/: athena_gpu, athena_cpu, COMMIT,
# examples/, generator/, SHA256SUMS, and READY last (tracks wait for READY). Refuses if
# READY is already there (publish a new version into a new directory).
#
#   tracks/core/analysis/clump2/publish_exe.sh <source commit>   (from the root of the worktree)
#
# <source commit>: the commit whose athenak/src the two executables in .work/build_cpu and
# .work/build_gpu were built from; the script refuses if athenak/src differs between that
# commit and HEAD (generator/ and examples/ are taken from HEAD).
set -euo pipefail

ROOT=$(git rev-parse --show-toplevel)
cd "$ROOT"
DEST=/data/haiyangw/nrpic/scratch/core/exe/core_clump-table
SRC=${1:?source commit}
GPU=.work/build_gpu/src/athena
CPU=.work/build_cpu/src/athena

[[ -e $DEST/READY ]] && { echo "already published: $DEST/READY" >&2; exit 1; }
git diff --quiet "$SRC" HEAD -- athenak/src || {
  echo "athenak/src at HEAD differs from $SRC" >&2; exit 1; }
[[ -z $(git status --porcelain -- athenak/src python/nrpic problems) ]] || {
  echo "uncommitted changes in the source" >&2; exit 1; }
full=$(git rev-parse "$SRC")
tip=$(git rev-parse HEAD)

mkdir -p "$DEST/examples" "$DEST/generator"
cp "$GPU" "$DEST/athena_gpu"
cp "$CPU" "$DEST/athena_cpu"
chmod a-w "$DEST/athena_gpu" "$DEST/athena_cpu"
git archive "$tip" python/nrpic problems/ic | tar -x -C "$DEST/generator"
cp problems/clump/cluster_moving.athinput problems/clump/cluster_binary.athinput \
   problems/tests/clump_table_static.athinput problems/tests/clump_table_binary.athinput \
   problems/clump/clump_moving.athinput "$DEST/examples/"
{
  echo "$full"
  echo "Both executables are built from the athenak/src of this commit of branch"
  echo "core/clump-table (which starts from core/clump-curvature and has main merged on"
  echo "2026-11-19: release core-v0.3 plus the Gaussian clump curvature of the first pass)."
  echo "Branch tip at publication: $tip; athenak/src is unchanged between the two."
  echo "generator/ (python/nrpic, problems/ic) and examples/ are those of the tip."
} > "$DEST/COMMIT"
( cd "$DEST" && sha256sum athena_gpu athena_cpu COMMIT examples/* > SHA256SUMS )
cp tracks/core/analysis/clump2/READY.txt "$DEST/READY"
echo "published in $DEST"
cat "$DEST/SHA256SUMS"
