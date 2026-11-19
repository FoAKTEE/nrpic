#!/usr/bin/env bash
# Initial data of the second round of first_source (convergence and small amplitude) with
# cosmo/ic/make_east.py, the tool of the wave-2 scan (build_ic.sh): crossed waves with
# amplitude ratios (1, eps, 0), box 4, cubic cloud with the compensation of the production
# configuration, no filter.
#   build_ic2.sh [<outdir>]    (default $NRPIC_RUN_DIR) writes <outdir>/<name>/{particles.nrp,fields.bin,id.json}
# CASES: space-separated specs name:delta:n:ppc:eps:threads; the default is the second round
# (particles per cell and direction 1 and 3 at 64^3, 1 at 128^3, delta = 0.0025 at 64^3).
set -euo pipefail
out=${1:-${NRPIC_RUN_DIR:?give an output directory}}
WT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
cd "$WT/cosmo/ic"
CASES=${CASES:-"e1_p1_n64:0.01:64:1:1:1 e1_p3_n64:0.01:64:3:1:2 e1_p1_n128:0.01:128:1:1:3 d0025_e1:0.0025:64:2:1:2 d0025_e0p3:0.0025:64:2:0.3:2"}
pids=()
names=()
for spec in $CASES; do
  IFS=: read -r name delta n ppc eps th <<< "$spec"
  d="$out/$name"
  mkdir -p "$d"
  ( export OMP_NUM_THREADS=$th OPENBLAS_NUM_THREADS=$th MKL_NUM_THREADS=$th
    exec python3 make_east.py --delta "$delta" --n "$n" --ppc "$ppc" --L 4 --ratios "1,$eps,0" \
      --shape pcs --dep-comp-c 0.16666666666666666 --dep-comp-c2 0.4666666666666667 \
      --nfilter 0 --out "$d" ) > "$d.log" 2>&1 &
  pids+=($!)
  names+=("$name")
done
rc=0
for p in "${pids[@]}"; do wait "$p" || rc=1; done
for name in "${names[@]}"; do echo "== $name"; tail -6 "$out/$name.log"; done
exit $rc
