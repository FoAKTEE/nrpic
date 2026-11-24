#!/bin/bash
# Publish the executables of branch core/step-limit for the tracks' scouting runs
# (decision 0013):
#   /data/haiyangw/nrpic/scratch/core/exe/core_step-limit/
#       athena_cpu  athena_cpu_omp  athena_gpu  COMMIT  SHA256SUMS  READY
# What is published is what the tests of tracks/core/JOURNAL-step-limit.md ran: the
# builds .work/build_{cpu,omp,gpu}_sl of this worktree made from the source of commit
# SRC, frozen as copies under scratch/core/tmp/sl_exe/ at the start of the second
# session (journal entry 9; the build directories are reused afterwards for the second
# item of the package).  The script refuses if a frozen copy does not have the checksum
# recorded in entry 9.  Two stages, so that the card job can be queued before the last
# processor test has ended:
#   tracks/core/analysis/step_limit/publish_exe.sh SRC exe     executables, SHA256SUMS, COMMIT
#   tracks/core/analysis/step_limit/publish_exe.sh SRC ready   READY (copied from READY.md)
# A track that waits for READY finds the executables and COMMIT complete.
set -euo pipefail
SRC=${1:?usage: publish_exe.sh <source commit> exe|ready}
STAGE=${2:?usage: publish_exe.sh <source commit> exe|ready}
W=/data/haiyangw/nrpic/wt/core-s3
F=/data/haiyangw/nrpic/scratch/core/tmp/sl_exe
D=/data/haiyangw/nrpic/scratch/core/exe/core_step-limit
cd "$W"
if [[ $STAGE == ready ]]; then
  [[ -s $D/COMMIT ]] || { echo "ERROR: stage exe first" >&2; exit 1; }
  ( cd "$D" && sha256sum --quiet -c SHA256SUMS )
  cp "$W/tracks/core/analysis/step_limit/READY.md" "$D/READY"
  echo "READY published"; exit 0
fi
[[ $STAGE == exe ]] || { echo "ERROR: stage is exe or ready" >&2; exit 1; }
sha256sum --quiet -c - <<EOF_SUMS
be2a1a7b24bb9b4e566acdc9a5a08c49f600ed6baf0e0b74daf3990338696241  $F/athena_cpu
4cea2bbb86871d2101fc2e3d1b7b98de0071bf73a92f423378c03f43f3c15eb1  $F/athena_cpu_omp
4b336bbec9c7a0d52306ad9fadbc1807a92cbd8eeee9e79cb006f6f9dc9ead6d  $F/athena_gpu
EOF_SUMS
src=$(git rev-parse "$SRC")
head=$(git rev-parse HEAD)
mkdir -p "$D"
cd "$D"
rm -f READY
cp "$F/athena_cpu" athena_cpu
cp "$F/athena_cpu_omp" athena_cpu_omp
cp "$F/athena_gpu" athena_gpu
chmod 755 athena_cpu athena_cpu_omp athena_gpu
sha256sum athena_cpu athena_cpu_omp athena_gpu > SHA256SUMS
{
  echo "branch core/step-limit (work package step-limit of core, batches 11 and 13)"
  echo "source commit (athenak/ and scripts/ of the three executables): $src"
  echo "HEAD at publication: $head"
  echo "contains release core-v0.6 (git diff core-v0.6 $SRC -- athenak/src: z4c/z4c_newdt_gauge.cpp new;"
  echo "  z4c/z4c_newdt.cpp, z4c/z4c.cpp, z4c/z4c.hpp, CMakeLists.txt changed)"
  echo "athena_cpu:     scripts/build_cpu.sh .work/build_cpu_sl in wt/core-s3 (g++ 11.4.0, Kokkos Serial, -O2 -g)"
  echo "athena_cpu_omp: scripts/build_cpu_omp.sh .work/build_omp_sl (Kokkos OpenMP, -O3 -DNDEBUG -g)"
  echo "athena_gpu:     scripts/build_gpu.sh .work/build_gpu_sl (nvcc CUDA 12.6, host g++ 11.4.0, A100)"
  echo "linked: $(ls -l --time-style=+%Y-%m-%dT%H:%M:%S%z "$F/athena_cpu" "$F/athena_cpu_omp" "$F/athena_gpu" | awk '{print $6}' | tr '\n' ' ')"
  echo "Kokkos $(cd "$W" && git -C athenak/kokkos rev-parse HEAD)"
  echo "published: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  sed 's/^/sha256 /' SHA256SUMS
} > COMMIT
cat COMMIT
