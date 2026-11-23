#!/bin/bash
# Reruns every check of repro/equations into one output directory (argument 1, or
# $NRPIC_RUN_DIR when started through harness/bin/nrpic-run). Processors only, 1 thread.
set -euo pipefail
OUT="${1:-${NRPIC_RUN_DIR:?give an output directory}}"
D="$(cd "$(dirname "$0")" && pwd)"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
mkdir -p "$OUT"/{equations,noise_amp,langevin,code_map,figures}
python3 "$D/check_code_map.py" --out "$OUT/code_map" | tee "$OUT/code_map/log.txt"
python3 "$D/check_langevin.py" --out "$OUT/langevin" | tee "$OUT/langevin/log.txt"
python3 "$D/check_noise_amp.py" --out "$OUT/noise_amp" 2>&1 | tee "$OUT/noise_amp/log.txt"
python3 "$D/check_equations.py" --out "$OUT/equations" | tee "$OUT/equations/log.txt"
python3 "$D/make_figures.py" --eq "$OUT/equations/results.json" \
  --code "$OUT/code_map/code_map.json" --out "$OUT/figures" | tee "$OUT/figures/log.txt"
