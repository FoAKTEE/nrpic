#!/bin/bash
# C4 (second registered run): v4_shells.py with the velocity step limit (--vstep 1, the
# default since 69d9263^), five variants in parallel (five cores), then the comparison with
# the track's self-similar solution (v4b_compare.py). Output in $NRPIC_RUN_DIR.
set -euo pipefail
P=/data/haiyangw/nrpic/wt/D-bh-dress/tracks/D-bh-dress/stage/G0/verify
OUT="${NRPIC_RUN_DIR:?}"
PY=/data/haiyangw/nrpic/wt/D-bh-dress/.venv/bin/python
SS=/data/haiyangw/nrpic/scratch/D-bh-dress/D-bh-dress-20261115-123813-97afeea
mkdir -p "$OUT/figs_variants"
export OMP_NUM_THREADS=1
$PY $P/v4_shells.py --out "$OUT/N2000"  --N 2000  --af 100 --figdir "$OUT/figs_variants" > "$OUT/N2000.log" 2>&1 &
$PY $P/v4_shells.py --out "$OUT/N4000"  --N 4000  --af 100 --figdir "$OUT/figs_variants" > "$OUT/N4000.log" 2>&1 &
$PY $P/v4_shells.py --out "$OUT/N8000"  --N 8000  --af 100 --figdir "$OUT/figs_variants" > "$OUT/N8000.log" 2>&1 &
$PY $P/v4_shells.py --out "$OUT/N16000" --N 16000 --af 100 > "$OUT/N16000.log" 2>&1 &
$PY $P/v4_shells.py --out "$OUT/N4000_eta0.0125" --N 4000 --af 100 --eta 0.0125 --figdir "$OUT/figs_variants" > "$OUT/N4000_eta0.0125.log" 2>&1 &
wait
$PY $P/v4b_compare.py --shells "$OUT" --ss "$SS"
