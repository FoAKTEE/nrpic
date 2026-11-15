#!/usr/bin/env bash
# Initial data of the first-source scan with cosmo/ic/make_east.py: crossed waves with
# amplitude ratios (1, eps, 0), delta = 0.01, box 4, 64^3 cells, two particles per cell
# and direction, cubic cloud with the compensation of the production configuration.
#   build_ic.sh [<outdir>]    (default $NRPIC_RUN_DIR) writes <outdir>/eps{0,0p1,0p3,1}/{particles.nrp,fields.bin,id.json}
# Four cases in parallel with four threads each (16 cores). CASES="eps1" (names) builds a subset;
# N=32 (default 64) the mesh, THREADS (default 4) the threads per case.
set -euo pipefail
out=${1:-${NRPIC_RUN_DIR:?give an output directory}}
WT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
cd "$WT/cosmo/ic"
N=${N:-64}
TH=${THREADS:-4}
export OMP_NUM_THREADS=$TH OPENBLAS_NUM_THREADS=$TH MKL_NUM_THREADS=$TH
pids=()
CASES=${CASES:-eps0 eps0p1 eps0p3 eps1}
declare -A EPS=([eps0]=0 [eps0p1]=0.1 [eps0p3]=0.3 [eps1]=1)
for name in $CASES; do
  eps=${EPS[$name]}
  d="$out/$name"
  mkdir -p "$d"
  python3 make_east.py --delta 0.01 --n "$N" --ppc 2 --L 4 --ratios "1,$eps,0" \
    --shape pcs --dep-comp-c 0.16666666666666666 --dep-comp-c2 0.4666666666666667 \
    --nfilter 0 --out "$d" > "$d.log" 2>&1 &
  pids+=($!)
done
rc=0
for p in "${pids[@]}"; do wait "$p" || rc=1; done
for name in $CASES; do echo "== $name"; tail -6 "$out/$name.log"; done
exit $rc
