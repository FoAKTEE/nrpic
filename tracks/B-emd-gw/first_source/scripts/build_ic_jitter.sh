#!/usr/bin/env bash
# Initial data of the jittered-lattice null of first_source with core's
# problems/cosmo/make_waves.py (branch core/requests-b, not on main): a single plane wave
# (ratios 1, 0, 0), delta = 0.01, 64^3, two particles per cell and direction, the cloud and
# compensation of the production configuration, the lattice displaced along y and z by a
# uniform deviate in (-A, A) cells (counter-based generator of the code, seed 7; the same
# deviates for every A, so the noise field is exactly proportional to A). A = 0 is the
# parity case against cosmo/ic/make_east.py (run B-20261115-161656-03d75e1, eps0).
#   build_ic_jitter.sh [<outdir>]   (default $NRPIC_RUN_DIR) writes <outdir>/<name>/... and
#                                   <outdir>/tool/ (the tool files at the pinned commit)
# The tool is taken from the pinned commit with git archive, so the run does not depend on
# the state of core's worktree. CASES: specs name:A:seed:threads.
set -euo pipefail
out=${1:-${NRPIC_RUN_DIR:?give an output directory}}
WT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
COMMIT=${TOOL_COMMIT:-7db34a5a9ce5216079b6bbc7d458205c21d12883}
CASES=${CASES:-"jit0p3:0.3:7:2 jit0p1:0.1:7:2 jit0:0.0:7:2"}
mkdir -p "$out/tool"
git -C "$WT" archive "$COMMIT" problems/cosmo/make_waves.py python/nrpic | tar -x -C "$out/tool"
echo "$COMMIT" > "$out/tool/COMMIT"
( cd "$out/tool" && sha256sum problems/cosmo/make_waves.py python/nrpic/*.py > sha256sums.txt )
pids=()
names=()
for spec in $CASES; do
  IFS=: read -r name A seed th <<< "$spec"
  d="$out/$name"
  mkdir -p "$d"
  ( export OMP_NUM_THREADS=$th OPENBLAS_NUM_THREADS=$th MKL_NUM_THREADS=$th
    exec python3 -B "$out/tool/problems/cosmo/make_waves.py" --delta 0.01 --n 64 --ppc 2 --L 4 \
      --ratios 1,0,0 --shape pcs --dep-comp-c 0.16666666666666666 \
      --dep-comp-c2 0.4666666666666667 --nfilter 0 \
      --jitter "$A" --jitter-axes y,z --seed "$seed" --out "$d" ) > "$d.log" 2>&1 &
  pids+=($!)
  names+=("$name")
done
rc=0
for p in "${pids[@]}"; do wait "$p" || rc=1; done
for name in "${names[@]}"; do echo "== $name"; tail -6 "$out/$name.log"; done
exit $rc
