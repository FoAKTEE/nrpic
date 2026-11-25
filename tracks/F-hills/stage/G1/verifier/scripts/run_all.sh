#!/bin/bash
# The verifier's registered analysis: reader tests, the passage (A + A2) and its Newtonian
# reference, mesh members, P1 and the horizon scan. Usage: run_all.sh <output dir>
set -euo pipefail
OUT="$1"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
python "$HERE/vtest.py" --out "$OUT"
python "$HERE/vpassage.py" --out "$OUT" > "$OUT/vpassage.log"
python "$HERE/vmesh.py" --out "$OUT"
ls -l "$OUT"
