#!/bin/bash
# C4 variants of v4_shells.py (run through hand_run.py / nrpic-run; output in $NRPIC_RUN_DIR)
set -euo pipefail
P=/data/haiyangw/nrpic/wt/D-bh-dress/tracks/D-bh-dress/stage/G0/verify
OUT="${NRPIC_RUN_DIR:?}"
PY=/data/haiyangw/nrpic/wt/D-bh-dress/.venv/bin/python
mkdir -p "$OUT/figs_variants"
$PY $P/v4_shells.py --out "$OUT/N4000_af100_s2" --N 4000 --af 100 --soft 2
$PY $P/v4_shells.py --out "$OUT/N2000_af100_s2" --N 2000 --af 100 --soft 2 --figdir "$OUT/figs_variants"
$PY $P/v4_shells.py --out "$OUT/N4000_af100_s1" --N 4000 --af 100 --soft 1 --figdir "$OUT/figs_variants"
$PY $P/v4_shells.py --out "$OUT/N4000_af100_s2_eta0.025" --N 4000 --af 100 --soft 2 --eta 0.025 --figdir "$OUT/figs_variants"
$PY $P/v4_shells.py --out "$OUT/N3000_af300_s2" --N 3000 --af 300 --soft 2 --figdir "$OUT/figs_variants"
