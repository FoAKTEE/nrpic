#!/usr/bin/env bash
# Publishes the executables of branch core/build-openmp for the tracks (decision 0013):
#   scratch/core/exe/core_build-openmp/{athena_cpu, athena_cpu_serial, athena_gpu,
#                                       COMMIT, SHA256SUMS, READY}
# athena_cpu is the threaded build (scripts/build_cpu_omp.sh), athena_cpu_serial the
# serial build (scripts/build_cpu.sh), athena_gpu the card build (scripts/build_gpu.sh),
# all three from the build directories of this worktree. Refuses unless athenak/ has no
# change against HEAD; each build directory is brought up to date first (an incremental
# make that must not compile anything), so the executables are those of the source of HEAD.
# READY is tracks/core/omp/READY.txt.
set -euo pipefail
WT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
DEST=/data/haiyangw/nrpic/scratch/core/exe/core_build-openmp
cd "$WT"
if [[ -n $(git status --porcelain -- athenak scripts) ]]; then
  echo "refused: athenak/ or scripts/ has uncommitted changes" >&2; exit 1
fi
for b in build_omp build_cpu build_gpu; do
  out=$(cmake --build ".work/$b" --parallel 4 2>&1)
  if grep -q "Building CXX" <<< "$out"; then
    echo "refused: .work/$b was not up to date with the source (it rebuilt now); run again" >&2
    exit 1
  fi
done
head=$(git rev-parse HEAD)
src=$(git log -1 --format=%H -- athenak)
mkdir -p "$DEST"
rm -f "$DEST/READY"
install -m 0555 .work/build_omp/src/athena "$DEST/athena_cpu"
install -m 0555 .work/build_cpu/src/athena "$DEST/athena_cpu_serial"
install -m 0555 .work/build_gpu/src/athena "$DEST/athena_gpu"
(cd "$DEST" && sha256sum athena_cpu athena_cpu_serial athena_gpu > SHA256SUMS)
cat > "$DEST/COMMIT" <<EOF
branch core/build-openmp
source commit (last change of athenak/): $src
HEAD at publication (same athenak/): $head
built in wt/core-omp/.work/{build_omp,build_cpu,build_gpu} from the clean worktree
(git status of athenak/ and scripts/ empty; incremental make compiled nothing):
  athena_cpu         scripts/build_cpu_omp.sh   (Kokkos OpenMP, g++ $(g++ -dumpfullversion), -O3 -DNDEBUG -g, ICX)
  athena_cpu_serial  scripts/build_cpu.sh       (Kokkos Serial, -O2 -g)
  athena_gpu         scripts/build_gpu.sh       (CUDA 12.6, sm_80)
Kokkos $(git -C athenak/kokkos rev-parse --short HEAD 2>/dev/null || echo '?')
published: $(date -u +%Y-%m-%dT%H:%M:%SZ)
EOF
cp tracks/core/omp/READY.txt "$DEST/READY"
ls -la "$DEST"
cat "$DEST/SHA256SUMS"
