#!/usr/bin/env bash
# Initial data of the scouting runs S1 (mu = 0.5) and S2 (mu = 0.03): e = 0.2, eps_i = 1,
# 64^3, one particle per cell, cloud-in-cell with two binomial passes and compensation.
#   build_scouting_ic.sh <outdir>
set -euo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PY=/data/haiyangw/nrpic/wt/A-emd-pbh/.venv/bin/python
for mu in 0.5 0.03; do
  "$PY" -I "$HERE/make_peak_ic.py" --mu $mu --e 0.2 --eps-i 1 --n 64 --nfilter 2 \
      --compensate --out "$1/S_mu$mu" > "$1/S_mu$mu.log" 2>&1 &
done
wait
