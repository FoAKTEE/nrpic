#!/bin/bash
# Publish the executables of branch core/gauge-2 for the tracks' scouting runs (decision
# 0013):
#   /data/haiyangw/nrpic/scratch/core/exe/core_gauge-2/{athena_gpu,athena_cpu,COMMIT,SHA256SUMS,READY}
# What is published is what the tests of tracks/core/JOURNAL-gauge-2.md ran: the builds
# .work/build_gpu_g2 and .work/build_cpu_g2 of this worktree, made from the source of
# commit SRC.  The script refuses to publish if athenak/src of HEAD (or of the working
# tree) differs from SRC, or if a build is older than the newest source file.  READY is
# copied last, so that a track that waits for it finds the rest complete.
#   tracks/core/analysis/gauge2/publish_exe.sh SRC
set -euo pipefail
SRC=${1:?source commit of the tested builds}
WT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
DST=/data/haiyangw/nrpic/scratch/core/exe/core_gauge-2
cd "$WT"
if [[ -n $(git status --porcelain -- athenak/src) ]]; then
  echo "ERROR: athenak/src of the working tree differs from HEAD" >&2; exit 1
fi
if [[ -n $(git diff "$SRC" HEAD -- athenak/src) ]]; then
  echo "ERROR: athenak/src of HEAD differs from $SRC; rebuild and test first" >&2; exit 1
fi
for b in gpu cpu; do
  exe=.work/build_${b}_g2/src/athena
  [[ -x $exe ]] || { echo "ERROR: $exe missing" >&2; exit 1; }
  if [[ -n $(find athenak/src -newer "$exe" -type f | head -1) ]]; then
    echo "ERROR: a source file is newer than $exe" >&2; exit 1
  fi
done
mkdir -p "$DST"
rm -f "$DST/READY"
cp .work/build_gpu_g2/src/athena "$DST/athena_gpu"
cp .work/build_cpu_g2/src/athena "$DST/athena_cpu"
chmod 755 "$DST/athena_gpu" "$DST/athena_cpu"
(cd "$DST" && sha256sum athena_gpu athena_cpu > SHA256SUMS)
{
  echo "branch core/gauge-2"
  echo "source commit (athenak/src of the executables): $(git rev-parse "$SRC")"
  echo "HEAD at publication (same athenak/src): $(git rev-parse HEAD)"
  echo "built 2026-11-21 by scripts/build_gpu.sh (CUDA 12.6) and scripts/build_cpu.sh in"
  echo "$WT/.work/build_{gpu,cpu}_g2 from that source"
  echo "published: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  cat "$DST/SHA256SUMS"
} > "$DST/COMMIT"
cp tracks/core/analysis/gauge2/READY.md "$DST/READY"
cat "$DST/COMMIT"
