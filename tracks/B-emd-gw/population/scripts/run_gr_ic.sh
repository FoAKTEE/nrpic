#!/usr/bin/env bash
# Relativistic initial data of the population box (scripts/make_ic.py --gr: dictionary
# plus constraint solve on the torus) for several box sizes, one after the other, in
# $NRPIC_RUN_DIR/gr_L<L>_n<n>/.
#
#   run_gr_ic.sh <n> "<L list>" "<other make_ic args>"
set -euo pipefail
n=$1; Ls=$2; extra=${3:-}
here=$(cd "$(dirname "$0")" && pwd)
: "${NRPIC_RUN_DIR:?run through nrpic-run}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
for L in $Ls; do
  out="$NRPIC_RUN_DIR/gr_L${L}_n${n}"
  mkdir -p "$out"
  start=$(date +%s)
  # shellcheck disable=SC2086
  python3 "$here/make_ic.py" --n "$n" --L "$L" --gr $extra --out "$out" > "$out/make_ic.log" 2>&1 \
    || echo "L=$L failed" >> "$NRPIC_RUN_DIR/failures.txt"
  echo "L=$L done in $(( $(date +%s) - start )) s"
done
