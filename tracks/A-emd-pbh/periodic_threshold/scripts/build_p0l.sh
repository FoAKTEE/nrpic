#!/usr/bin/env bash
# Initial data of the wave-3 run P0L: the spherical peak (e = p = 0) at mu = 0.3, eps_i = 1,
# 64^3, one particle per cell, cloud-in-cell with two binomial passes and compensation
# (the S1 settings of build_scouting_ic.sh / mu_convergence.sh except e), then the
# particle file reordered so that 448 particles on lattice lines along the axes and the
# diagonal are tracked (track_select.py).
#   build_p0l.sh <outdir>
set -euo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PY=/data/haiyangw/nrpic/wt/A-emd-pbh/.venv/bin/python
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-2} OPENBLAS_NUM_THREADS=${OMP_NUM_THREADS:-2}
out=$1/P0_mu0.3
"$PY" -I "$HERE/make_peak_ic.py" --mu 0.3 --e 0.0 --p 0.0 --eps-i 1 --n 64 --nfilter 2 \
    --compensate --out "$out" > "$1/P0_mu0.3.log" 2>&1
"$PY" -I "$HERE/track_select.py" --data "$out" >> "$1/P0_mu0.3.log" 2>&1
tail -n 25 "$1/P0_mu0.3.log"
