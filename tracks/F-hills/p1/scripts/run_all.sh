#!/usr/bin/env bash
# Package p1: baseline trajectories, the decidable checks, the five figures and the card
# ledger of P1, all written into $NRPIC_RUN_DIR (never into P1's run directory).
#   nrpic-run submit ... --package tracks/F-hills/p1 --cores 1 -- bash tracks/F-hills/p1/scripts/run_all.sh
# Optional argument: the P1 run directory (default: scratch/F-hills/F-20261119-150017-b45ec5f).
set -euo pipefail
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMBA_NUM_THREADS=1
: "${NRPIC_RUN_DIR:?run under nrpic-run}"
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
WT=$(cd "$HERE/../../../.." && pwd)
PY=$WT/.venv/bin/python
PYGB=/data/haiyangw/nrpic/scratch/F-hills/venv-gb/bin/python     # numba, for HRNA
RD=${1:-/data/haiyangw/nrpic/scratch/F-hills/F-20261119-150017-b45ec5f}
O=--out=$NRPIC_RUN_DIR
"$PYGB" "$HERE/baselines_tracks.py" "$O"
for s in checks fig_tracks_plane fig_separations fig_horizons fig_segments fig_energies ledger; do
  echo "== $s"
  "$PY" "$HERE/$s.py" "$O" "--rundir=$RD"
done
