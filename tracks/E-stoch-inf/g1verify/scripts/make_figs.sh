#!/usr/bin/env bash
# All figures of VERIFIER.md and the V4/V5 addendum, from the registered analysis runs.
#   make_figs.sh OUTDIR
set -eu
OUT=$1
S=/data/haiyangw/nrpic/scratch/E-stoch-inf
D=$(dirname "$0")
V123=$S/E-20261121-030207-fb6f090
V6=$S/E-20261121-030522-c6907b6
V7=$S/E-20261121-030520-5a23d64
CON=$S/E-20261121-030657-c1afe38
V45=$S/E-20261121-031951-82984f8
python3 "$D/v45_addendum.py" "$OUT" "$V45"
python3 "$D/fig_v1.py" "$V123" "$OUT/fig_v1"
python3 "$D/fig_v2.py" "$V123" "$OUT/fig_v2"
python3 "$D/fig_v3.py" "$V123" "$OUT/fig_v3"
python3 "$D/fig_v4.py" "$V45" "$OUT/fig_v4"
python3 "$D/fig_v5.py" "$V45" "$CON" "$OUT/fig_v5"
python3 "$D/fig_v6.py" "$V6" "$OUT/fig_v6"
python3 "$D/fig_v7.py" "$V7" "$OUT/fig_v7"
ls -la "$OUT"
