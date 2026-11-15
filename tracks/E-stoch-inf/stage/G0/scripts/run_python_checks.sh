#!/usr/bin/env bash
# The verifier's own computations V1-V5 and V8 (scripts in this directory).
# Usage: run_python_checks.sh <output directory>
set -euo pipefail
OUT=$1
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../../../.." && pwd)
PY=$ROOT/.venv/bin/python
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd "$HERE"
"$PY" v1_background.py --out "$OUT/v1" > "$OUT/v1.log" 2>&1
"$PY" v3_initial_data.py --out "$OUT/v3" > "$OUT/v3.log" 2>&1
OMP_NUM_THREADS=2 "$PY" v4_draw_norm.py --out "$OUT/v4" > "$OUT/v4.log" 2>&1
"$PY" v5_kicks.py --out "$OUT/v5" > "$OUT/v5.log" 2>&1
"$PY" v2_freezing.py --out "$OUT/v2" > "$OUT/v2.log" 2>&1
"$PY" v8_deltaN_reference.py --out "$OUT/v8" --v2 "$OUT/v2/v2.json" > "$OUT/v8.log" 2>&1
echo done
