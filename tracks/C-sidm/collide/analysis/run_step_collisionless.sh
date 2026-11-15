#!/bin/bash
# Test T6 at sigma/m = 0 with the existing processor executable (no collision module):
# particle file, AthenaK run, analysis. Run through register_run.py, which sets
# NRPIC_RUN_DIR. Usage: run_step_collisionless.sh [N]
set -euo pipefail
N=${1:-100000}
PKG=$(cd "$(dirname "$0")/.." && pwd)
OUT=${NRPIC_RUN_DIR:?run through register_run.py}
EXE=/data/haiyangw/nrpic/.work/build_cpu_c1/src/athena
cd "$OUT"
python3 "$PKG/analysis/make_box.py" step --out "$OUT/step" --n "$N" \
    --box 1.0 0.125 0.125 --theta 0.02 --theta2 0.01 --sigma 0 --seed 1 > make_box.log
"$EXE" -i "$PKG/inputs/box_step_collisionless.athinput" -d "$OUT" \
    particles/particle_file="$OUT/step.nrp" > athena.log 2>&1
python3 "$PKG/analysis/an_step.py" "$OUT" step "$OUT/step.json" "$OUT/step.nrp" "$OUT"
