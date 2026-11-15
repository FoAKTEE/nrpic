#!/bin/bash
# Verifier suite V1-V7 (own code of this directory). Output: $NRPIC_RUN_DIR/{mono,king,puls,rate,costs}.
# Run from the worktree root (nrpic-run does); one thread per numerical library.
set -euo pipefail
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
V=tracks/C-sidm/stage/G0/verifier
O=${NRPIC_RUN_DIR:?}
python3 $V/v_mono.py "$O/mono"
python3 $V/v_king.py "$O/king"
python3 $V/v_pulsation.py "$O/puls"
python3 $V/v_rate.py "$O/rate"
python3 $V/v_costs.py "$O/costs" "$O/king/v_king.json" "$O/mono/v_mono.json"
echo "verifier suite done"
