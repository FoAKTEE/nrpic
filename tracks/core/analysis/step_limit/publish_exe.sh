#!/bin/bash
# Publish the executables of branch core/step-limit for the tracks' scouting runs
# (decision 0013):
#   /data/haiyangw/nrpic/scratch/core/exe/core_step-limit/
#       athena_cpu  athena_cpu_omp  athena_gpu  COMMIT  SHA256SUMS  READY
# Published are the builds .work/build_{cpu,omp,gpu}_sl of this worktree made from the
# final source of the package (both items: step limit of the gauge sectors, stop on
# SIGTERM).  The tests T0 to T6 of the step limit ran the builds of source 476fe0c
# (frozen copies under scratch/core/tmp/sl_exe/, published here from 15:31 to the
# replacement); checks F1 and F2 of journal entry 14 tie the final builds to them.
# The script refuses if athenak/, scripts/ or problems/ of HEAD or of the working tree
# differ from SRC, or if an executable is older than the newest source file it depends
# on.  Files are replaced by rename, so that a run that executes an old copy goes on.
# Two stages:
#   tracks/core/analysis/step_limit/publish_exe.sh SRC exe     executables, SHA256SUMS, COMMIT
#   tracks/core/analysis/step_limit/publish_exe.sh SRC ready   READY (copied from READY.md)
# A track that waits for READY finds the executables and COMMIT complete.
set -euo pipefail
SRC=${1:?usage: publish_exe.sh <source commit> exe|ready}
STAGE=${2:?usage: publish_exe.sh <source commit> exe|ready}
W=/data/haiyangw/nrpic/wt/core-s3
D=/data/haiyangw/nrpic/scratch/core/exe/core_step-limit
cd "$W"
if [[ $STAGE == ready ]]; then
  [[ -s $D/COMMIT ]] || { echo "ERROR: stage exe first" >&2; exit 1; }
  ( cd "$D" && sha256sum --quiet -c SHA256SUMS )
  cp "$W/tracks/core/analysis/step_limit/READY.md" "$D/READY.tmp" && mv "$D/READY.tmp" "$D/READY"
  echo "READY published"; exit 0
fi
[[ $STAGE == exe ]] || { echo "ERROR: stage is exe or ready" >&2; exit 1; }
if [[ -n $(git status --porcelain -- athenak scripts problems) ]]; then
  echo "ERROR: athenak/, scripts/ or problems/ of the working tree differ from HEAD" >&2; exit 1
fi
if [[ -n $(git diff "$SRC" HEAD -- athenak scripts problems) ]]; then
  echo "ERROR: athenak/, scripts/ or problems/ of HEAD differ from $SRC; rebuild and test first" >&2
  exit 1
fi
newest=$(ls -t athenak/src/main.cpp athenak/src/driver/*.[ch]pp athenak/src/utils/*.[ch]pp \
              athenak/src/z4c/*.[ch]pp athenak/src/CMakeLists.txt | head -1)
for b in cpu omp gpu; do
  exe=.work/build_${b}_sl/src/athena
  [[ -x $exe ]] || { echo "ERROR: no $exe" >&2; exit 1; }
  [[ $exe -nt $newest ]] || { echo "ERROR: $exe is older than $newest" >&2; exit 1; }
done
src=$(git rev-parse "$SRC")
head=$(git rev-parse HEAD)
mkdir -p "$D"
rm -f "$D/READY"
for pair in cpu:athena_cpu omp:athena_cpu_omp gpu:athena_gpu; do
  b=${pair%%:*}; n=${pair##*:}
  cp "$W/.work/build_${b}_sl/src/athena" "$D/$n.tmp"
  chmod 755 "$D/$n.tmp"
  mv "$D/$n.tmp" "$D/$n"
done
cd "$D"
sha256sum athena_cpu athena_cpu_omp athena_gpu > SHA256SUMS
{
  echo "branch core/step-limit (work package step-limit of core, batches 11 and 13)"
  echo "source commit (athenak/, scripts/, problems/ of the three executables): $src"
  echo "HEAD at publication: $head"
  echo "contains release core-v0.6 (git diff core-v0.6 $SRC -- athenak/src: z4c/z4c_newdt_gauge.cpp,"
  echo "  utils/term_signal.cpp, utils/term_signal.hpp new; z4c/z4c_newdt.cpp, z4c/z4c.cpp, z4c/z4c.hpp,"
  echo "  driver/driver.cpp, main.cpp, CMakeLists.txt changed)"
  echo "athena_cpu:     scripts/build_cpu.sh .work/build_cpu_sl in wt/core-s3 (g++ 11.4.0, Kokkos Serial, -O2 -g)"
  echo "athena_cpu_omp: scripts/build_cpu_omp.sh .work/build_omp_sl (Kokkos OpenMP, -O3 -DNDEBUG -g)"
  echo "athena_gpu:     scripts/build_gpu.sh .work/build_gpu_sl (nvcc CUDA 12.6, host g++ 11.4.0, A100)"
  echo "linked: $(ls -l --time-style=+%Y-%m-%dT%H:%M:%S%z "$W/.work/build_cpu_sl/src/athena" "$W/.work/build_omp_sl/src/athena" "$W/.work/build_gpu_sl/src/athena" | awk '{print $6}' | tr '\n' ' ')"
  echo "Kokkos $(cd "$W" && git -C athenak/kokkos rev-parse HEAD)"
  echo "published: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "replaces the builds of source 476fe0c published 2026-11-24T23:31:31Z (step limit only):"
  echo "  sha256 be2a1a7b24bb9b4e566acdc9a5a08c49f600ed6baf0e0b74daf3990338696241  athena_cpu"
  echo "  sha256 4cea2bbb86871d2101fc2e3d1b7b98de0071bf73a92f423378c03f43f3c15eb1  athena_cpu_omp"
  echo "  sha256 4b336bbec9c7a0d52306ad9fadbc1807a92cbd8eeee9e79cb006f6f9dc9ead6d  athena_gpu"
  sed 's/^/sha256 /' SHA256SUMS
} > COMMIT
cat COMMIT
