#!/usr/bin/env bash
# Initial data of the pancake cases with cosmo/ic/make_east.py (plane wave: --ratios 1,0,0).
#   build_ic.sh <outdir>      writes <outdir>/{L1_n32,L1_n64,L1_n96,L4_n64}/
set -euo pipefail
out=$1
WT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
cd "$WT/cosmo/ic"
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4
for c in "1 32" "1 64" "1 96" "4 64"; do
  set -- $c
  L=$1; n=$2
  d="$out/L${L}_n${n}"
  echo "== L=$L n=$n -> $d"
  python3 make_east.py --delta 0.05 --n "$n" --ppc 1 --L "$L" --ratios 1,0,0 \
    --shape pcs --dep-comp-c 0.16666666666666666 --dep-comp-c2 0.4666666666666667 \
    --nfilter 0 --out "$d" > "$d.log" 2>&1 || { mkdir -p "$d"; cat "$d.log"; exit 1; }
  tail -14 "$d.log"
done
