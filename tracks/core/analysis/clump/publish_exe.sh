#!/usr/bin/env bash
# Publish the tested executables of branch core/clump-curvature for the tracks' scouting
# runs (decision 0013) into scratch/core/exe/core_clump-curvature/: athena_gpu,
# athena_cpu, COMMIT, examples/, generator/, SHA256SUMS, and READY last (tracks wait for
# READY). Refuses if READY is already there (publish a new version into a new directory).
#
#   tracks/core/analysis/clump/publish_exe.sh      (from the root of wt/core-clump)
#
# The card executable is the one tested in run core-20261115-163141-ee2a188 (kept as
# .work/keep/athena_gpu_e1a4d0c); the processor executable is the one of every processor
# test and of test R (.work/build_cpu/src/athena, rebuilt from the tip byte-identically).
set -euo pipefail

ROOT=$(git rev-parse --show-toplevel)
cd "$ROOT"
DEST=/data/haiyangw/nrpic/scratch/core/exe/core_clump-curvature
SRC=e1a4d0c8
GPU=.work/keep/athena_gpu_e1a4d0c
CPU=.work/build_cpu/src/athena
SHA_GPU=661b5534b162f026b541ced8f52c763f13ce3cf8f1a420e0aba556d0dd236312
SHA_CPU=53c0d32b6b1c5af2a18bdbe2a13edc62930a37a9582629d2baf78ecfa40e20e1

[[ -e $DEST/READY ]] && { echo "already published: $DEST/READY" >&2; exit 1; }
[[ $(sha256sum "$GPU" | cut -d' ' -f1) == "$SHA_GPU" ]] || { echo "card executable changed" >&2; exit 1; }
[[ $(sha256sum "$CPU" | cut -d' ' -f1) == "$SHA_CPU" ]] || { echo "processor executable changed" >&2; exit 1; }
# the source of the builds and of the tip differ only in comment lines
if git diff "$SRC" HEAD -- athenak/src | grep -E '^[+-][^+-]' | grep -vE '^[+-]//' ; then
  echo "athenak/src at HEAD differs from $SRC in more than comments" >&2; exit 1
fi
full=$(git rev-parse "$SRC")
tip=$(git rev-parse HEAD)

mkdir -p "$DEST/examples" "$DEST/generator"
cp "$GPU" "$DEST/athena_gpu"
cp "$CPU" "$DEST/athena_cpu"
chmod a-w "$DEST/athena_gpu" "$DEST/athena_cpu"
git archive "$SRC" python/nrpic problems/ic | tar -x -C "$DEST/generator"
cp problems/clump/clump_moving.athinput problems/clump/clump_spin.athinput \
   problems/tests/clump_puncture.athinput problems/jeans/jeans_mc.athinput "$DEST/examples/"
{
  echo "$full"
  echo "Both executables and generator/ are built from this commit of branch"
  echo "core/clump-curvature (base: main 4ebb05f, whose athenak/src is release core-v0.3)."
  echo "Branch tip at publication: $tip. Its athenak/src differs from the commit above only in"
  echo "two comment lines of pgen/nrpic/nrpic_clump_curvature.hpp; the processor executable"
  echo "rebuilt from the tip is byte-identical. examples/ are taken from the tip."
} > "$DEST/COMMIT"
( cd "$DEST" && sha256sum athena_gpu athena_cpu COMMIT examples/* > SHA256SUMS )
cp tracks/core/analysis/clump/READY.txt "$DEST/READY"
echo "published in $DEST"
cat "$DEST/SHA256SUMS"
