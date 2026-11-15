#!/usr/bin/env bash
# Largest amplitude that cosmo/ic/make_field.py solves (e = 0.2, eps_i = 1, 64^3).
#   mu_convergence.sh <outdir> mu [mu ...]
set -euo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PY=/data/haiyangw/nrpic/wt/A-emd-pbh/.venv/bin/python
OUT=$1; shift
for mu in "$@"; do
  "$PY" -I "$HERE/make_peak_ic.py" --mu $mu --e 0.2 --eps-i 1 --n 64 --nfilter 2 \
      --compensate --out "$OUT/S_mu$mu" > "$OUT/S_mu$mu.log" 2>&1 &
done
wait
for mu in "$@"; do echo "mu $mu"; grep -E "^outer 17|max_hamiltonian|solve_change" "$OUT/S_mu$mu.log"; done
