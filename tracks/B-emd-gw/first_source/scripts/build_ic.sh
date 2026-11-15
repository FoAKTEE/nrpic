#!/usr/bin/env bash
# Initial data of the first-source scan with cosmo/ic/make_east.py: crossed waves with
# amplitude ratios (1, eps, 0), delta = 0.01, box 4, 64^3 cells, two particles per cell
# and direction, cubic cloud with the compensation of the production configuration.
#   build_ic.sh [<outdir>]    (default $NRPIC_RUN_DIR) writes <outdir>/eps{0,0p1,0p3,1}/{particles.nrp,fields.bin,id.json}
# Four cases in parallel with four threads each (16 cores).
set -euo pipefail
out=${1:-${NRPIC_RUN_DIR:?give an output directory}}
WT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
cd "$WT/cosmo/ic"
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4
pids=()
for c in "0 eps0" "0.1 eps0p1" "0.3 eps0p3" "1 eps1"; do
  set -- $c
  eps=$1; name=$2
  d="$out/$name"
  mkdir -p "$d"
  python3 make_east.py --delta 0.01 --n 64 --ppc 2 --L 4 --ratios "1,$eps,0" \
    --shape pcs --dep-comp-c 0.16666666666666666 --dep-comp-c2 0.4666666666666667 \
    --nfilter 0 --out "$d" > "$d.log" 2>&1 &
  pids+=($!)
done
rc=0
for p in "${pids[@]}"; do wait "$p" || rc=1; done
for name in eps0 eps0p1 eps0p3 eps1; do echo "== $name"; tail -6 "$out/$name.log"; done
exit $rc
