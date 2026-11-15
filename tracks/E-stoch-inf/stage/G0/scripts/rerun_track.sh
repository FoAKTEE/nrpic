#!/usr/bin/env bash
# Rerun of the track's own tests behind V1-V4 (scripts of tracks/E-stoch-inf/spec/ref/, read
# only, run unchanged) and leaf-by-leaf comparison with the outputs of the original runs:
#   T1/T2 ms_reference.py         -> run E-stoch-inf-20261115-122806-ef0d039 (summary.json)
#   T3    norm_test.py --n 64 --seeds 8 -> run E-stoch-inf-20261115-122934-9ac98d8 (norm_test.json)
#   T4    ic_constraint_check.py  -> run E-stoch-inf-20261115-123146-82d2fd4 (ic_check.json)
# Usage: rerun_track.sh <output directory>
set -euo pipefail
OUT=$1
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../../../.." && pwd)
PY=$ROOT/.venv/bin/python
REF=$ROOT/tracks/E-stoch-inf/spec/ref
SCR=/data/haiyangw/nrpic/scratch/E-stoch-inf
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
mkdir -p "$OUT"/T1T2 "$OUT"/T3 "$OUT"/T4
"$PY" "$REF/ms_reference.py" --out "$OUT/T1T2" > "$OUT/T1T2/stdout.txt" 2>&1
OMP_NUM_THREADS=4 "$PY" "$REF/norm_test.py" --out "$OUT/T3" --n 64 --seeds 8 > "$OUT/T3/stdout.txt" 2>&1
"$PY" "$REF/ic_constraint_check.py" --out "$OUT/T4" > "$OUT/T4/stdout.txt" 2>&1
"$PY" "$HERE/cmp_tree.py" "$OUT/compare.json" \
  "$SCR/E-stoch-inf-20261115-122806-ef0d039/summary.json" "$OUT/T1T2/summary.json" \
  "$SCR/E-stoch-inf-20261115-122806-ef0d039/quadratic.json" "$OUT/T1T2/quadratic.json" \
  "$SCR/E-stoch-inf-20261115-122806-ef0d039/inflection.json" "$OUT/T1T2/inflection.json" \
  "$SCR/E-stoch-inf-20261115-122934-9ac98d8/norm_test.json" "$OUT/T3/norm_test.json" \
  "$SCR/E-stoch-inf-20261115-123146-82d2fd4/ic_check.json" "$OUT/T4/ic_check.json"
