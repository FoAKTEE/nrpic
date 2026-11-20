#!/usr/bin/env bash
# Initial data of flrw_conv with the existing tools of cosmo/ic (decision 0010):
#   leg F: make_lattice.py (lattice at rest, ppc per direction, optional position noise
#          --noise-x A, uniform in (-A, A) per component, fixed seed), then ic_stats.py
#          (deposited contrast with the production cloud);
#   leg B: make_east.py --delta 1e-7 --ratios 1,0,0 (test B of arXiv:1904.07841), cubic
#          cloud with the compensation of the production configuration.
# Box 1.35085 (128 Mpc/h of the source paper in initial Hubble radii) for both legs.
#   build_ic.sh [<outdir>]    (default $NRPIC_RUN_DIR) writes <outdir>/<name>/
# CASES: space-separated specs
#   f:<name>:<n>:<ppc per direction>:<noise amplitude A>:<seed>
#   b:<name>:<n>:<ppc per direction>
# JOBS: processes at a time (default 6); each process gets one thread.
set -euo pipefail
out=${1:-${NRPIC_RUN_DIR:?give an output directory}}
WT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
PKG=$WT/tracks/B-emd-gw/flrw_conv
L=1.35085
JOBS=${JOBS:-6}
CASES=${CASES:?set CASES}
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
cd "$WT/cosmo/ic"
one() {
  IFS=: read -r kind name n ppc A seed <<< "$1"
  d="$out/$name"
  mkdir -p "$d"
  if [[ $kind == f ]]; then
    args=(--n "$n" --ppc "$ppc" --L "$L" --H0 1 --out "$d")
    if [[ $A != 0 ]]; then args+=(--noise-x "$A" --seed "$seed"); fi
    python3 make_lattice.py "${args[@]}"
    python3 "$PKG/scripts/ic_stats.py" "$d" "$n" "$L"
  else
    python3 make_east.py --delta 1e-7 --n "$n" --ppc "$ppc" --L "$L" --ratios 1,0,0 \
      --shape pcs --dep-comp-c 0.16666666666666666 --dep-comp-c2 0.4666666666666667 \
      --nfilter 0 --out "$d"
  fi
}
pids=()
names=()
rc=0
for spec in $CASES; do
  name=$(cut -d: -f2 <<< "$spec")
  ( one "$spec" ) > "$out/$name.log" 2>&1 &
  pids+=($!)
  names+=("$name")
  while (( $(jobs -rp | wc -l) >= JOBS )); do wait -n || rc=1; done
done
for p in "${pids[@]}"; do wait "$p" 2>/dev/null || true; done
for name in "${names[@]}"; do
  echo "== $name"; tail -4 "$out/$name.log"
  [[ -f $out/$name/particles.nrp ]] || { echo "MISSING $name"; rc=1; }
done
exit $rc
