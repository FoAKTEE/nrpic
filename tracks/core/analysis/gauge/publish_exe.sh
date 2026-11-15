#!/bin/bash
# Publish the executables of branch core/gauge for the tracks' scouting runs (decision
# 0013): builds the processor and the card executable from the committed source of this
# worktree and copies them, with COMMIT and READY, to
#   /data/haiyangw/nrpic/scratch/core/exe/core_gauge/{athena_cpu,athena_gpu,COMMIT,READY}
# Refuses a worktree whose athenak/ differs from HEAD.  READY is copied from
# tracks/core/analysis/gauge/READY.md last, so that a track that waits for it finds the
# executables complete.
set -euo pipefail
WT=/data/haiyangw/nrpic/wt/core-gauge
DST=/data/haiyangw/nrpic/scratch/core/exe/core_gauge
cd "$WT"
if [[ -n $(git status --porcelain -- athenak scripts) ]]; then
  echo "ERROR: athenak/ or scripts/ differ from HEAD; commit first" >&2; exit 1
fi
src=$(git log -1 --format=%H -- athenak/src)       # last commit that changed the source
head=$(git rev-parse HEAD)
scripts/build_cpu.sh .work/build_cpu | tail -1
scripts/build_gpu.sh .work/build_gpu | tail -1
mkdir -p "$DST"
rm -f "$DST/READY"
cp .work/build_cpu/src/athena "$DST/athena_cpu"
cp .work/build_gpu/src/athena "$DST/athena_gpu"
{
  echo "branch core/gauge"
  echo "source commit (last change of athenak/src): $src"
  echo "HEAD at build: $head"
  echo "built: $(date -u +%Y-%m-%dT%H:%M:%SZ) by scripts/build_cpu.sh, scripts/build_gpu.sh"
  echo "sha256 athena_cpu: $(sha256sum "$DST/athena_cpu" | cut -d' ' -f1)"
  echo "sha256 athena_gpu: $(sha256sum "$DST/athena_gpu" | cut -d' ' -f1)"
} > "$DST/COMMIT"
cp tracks/core/analysis/gauge/READY.md "$DST/READY"
cat "$DST/COMMIT"
