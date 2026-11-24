#!/bin/bash
# Publish the executables of branch core/step-limit for the tracks' scouting runs
# (decision 0013):
#   /data/haiyangw/nrpic/scratch/core/exe/core_step-limit/
#       athena_cpu  athena_cpu_omp  athena_gpu  COMMIT  SHA256SUMS  READY
# What is published is what the tests of tracks/core/JOURNAL-step-limit.md ran: the
# builds .work/build_{cpu,omp,gpu}_sl of this worktree, made from the source of commit
# SRC.  The script refuses if athenak/ or scripts/ of HEAD or of the working tree differ
# from SRC, or if an executable is older than the newest source file of athenak/src/z4c.
# READY is copied from tracks/core/analysis/step_limit/READY.md last, so that a track
# that waits for it finds the executables and COMMIT complete.
#   tracks/core/analysis/step_limit/publish_exe.sh SRC
set -euo pipefail
SRC=${1:?usage: publish_exe.sh <source commit>}
cd /data/haiyangw/nrpic/wt/core-s3
if [[ -n $(git status --porcelain -- athenak scripts) ]]; then
  echo "ERROR: athenak/ or scripts/ of the working tree differ from HEAD" >&2; exit 1
fi
if [[ -n $(git diff "$SRC" HEAD -- athenak scripts) ]]; then
  echo "ERROR: athenak/ or scripts/ of HEAD differ from $SRC; rebuild and test first" >&2
  exit 1
fi
newest=$(ls -t athenak/src/z4c/*.cpp athenak/src/z4c/*.hpp | head -1)
for b in cpu omp gpu; do
  exe=.work/build_${b}_sl/src/athena
  [[ -x $exe ]] || { echo "ERROR: no $exe" >&2; exit 1; }
  [[ $exe -nt $newest ]] || { echo "ERROR: $exe is older than $newest" >&2; exit 1; }
done
src=$(git rev-parse "$SRC")
head=$(git rev-parse HEAD)
mkdir -p /data/haiyangw/nrpic/scratch/core/exe/core_step-limit
cd /data/haiyangw/nrpic/scratch/core/exe/core_step-limit
rm -f READY
W=/data/haiyangw/nrpic/wt/core-s3
cp "$W/.work/build_cpu_sl/src/athena" athena_cpu
cp "$W/.work/build_omp_sl/src/athena" athena_cpu_omp
cp "$W/.work/build_gpu_sl/src/athena" athena_gpu
chmod 755 athena_cpu athena_cpu_omp athena_gpu
sha256sum athena_cpu athena_cpu_omp athena_gpu > SHA256SUMS
{
  echo "branch core/step-limit (work package step-limit of core, batch 11)"
  echo "source commit (athenak/ and scripts/ of the three executables): $src"
  echo "HEAD at publication (same athenak/ and scripts/): $head"
  echo "contains release core-v0.6 (git diff core-v0.6 $SRC -- athenak/src: z4c/z4c_newdt_gauge.cpp new;"
  echo "  z4c/z4c_newdt.cpp, z4c/z4c.cpp, z4c/z4c.hpp, CMakeLists.txt changed)"
  echo "athena_cpu:     scripts/build_cpu.sh .work/build_cpu_sl in wt/core-s3 (g++ 11.4.0, Kokkos Serial, -O2 -g)"
  echo "athena_cpu_omp: scripts/build_cpu_omp.sh .work/build_omp_sl (Kokkos OpenMP, -O3 -DNDEBUG -g)"
  echo "athena_gpu:     scripts/build_gpu.sh .work/build_gpu_sl (nvcc CUDA 12.6, host g++ 11.4.0, A100)"
  echo "linked: $(cd "$W" && ls -l --time-style=+%Y-%m-%dT%H:%M:%S%z .work/build_cpu_sl/src/athena .work/build_omp_sl/src/athena .work/build_gpu_sl/src/athena | awk '{print $6}' | tr '\n' ' ')"
  echo "Kokkos $(cd "$W" && git -C athenak/kokkos rev-parse HEAD)"
  echo "published: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  sed 's/^/sha256 /' SHA256SUMS
} > COMMIT
cp "$W/tracks/core/analysis/step_limit/READY.md" READY
cat COMMIT
