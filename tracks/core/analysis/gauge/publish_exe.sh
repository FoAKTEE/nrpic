#!/bin/bash
# Publish the executables of branch core/gauge for the tracks' scouting runs (decision
# 0013):
#   /data/haiyangw/nrpic/scratch/core/exe/core_gauge/{athena_cpu,athena_gpu,COMMIT,READY}
# What is published is what the tests of tracks/core/JOURNAL-gauge.md ran: the pinned
# copies scratch/core/gauge/exe/athena_{cpu,gpu}_<SRC>, built from the source of commit
# SRC.  The script refuses to publish if athenak/src of HEAD (or of the working tree)
# differs from SRC.  READY is copied from tracks/core/analysis/gauge/READY.md last, so
# that a track that waits for it finds the executables and COMMIT complete.
#   tracks/core/analysis/gauge/publish_exe.sh [SRC]        (default b4430da)
set -euo pipefail
WT=/data/haiyangw/nrpic/wt/core-gauge
DST=/data/haiyangw/nrpic/scratch/core/exe/core_gauge
PIN=/data/haiyangw/nrpic/scratch/core/gauge/exe
SRC=${1:-b4430da}
cd "$WT"
if [[ -n $(git status --porcelain -- athenak/src) ]]; then
  echo "ERROR: athenak/src of the working tree differs from HEAD" >&2; exit 1
fi
if [[ -n $(git diff "$SRC" HEAD -- athenak/src) ]]; then
  echo "ERROR: athenak/src of HEAD differs from $SRC; rebuild and test first" >&2; exit 1
fi
src=$(git rev-parse "$SRC")
head=$(git rev-parse HEAD)
mkdir -p "$DST"
rm -f "$DST/READY"
cp "$PIN/athena_cpu_$SRC" "$DST/athena_cpu"
cp "$PIN/athena_gpu_$SRC" "$DST/athena_gpu"
chmod 755 "$DST/athena_cpu" "$DST/athena_gpu"
{
  echo "branch core/gauge"
  echo "source commit (athenak/src of the executables): $src"
  echo "HEAD at publication (same athenak/src): $head"
  echo "built 2026-11-15 by scripts/build_cpu.sh and scripts/build_gpu.sh (CUDA 12.6) from"
  echo "the source of $SRC; copies of $PIN/athena_{cpu,gpu}_$SRC"
  echo "published: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "sha256 athena_cpu: $(sha256sum "$DST/athena_cpu" | cut -d' ' -f1)"
  echo "sha256 athena_gpu: $(sha256sum "$DST/athena_gpu" | cut -d' ' -f1)"
} > "$DST/COMMIT"
cp tracks/core/analysis/gauge/READY.md "$DST/READY"
cat "$DST/COMMIT"
