#!/usr/bin/env bash
# Smoke test S0 of repro/scope (JOURNAL entry 0): 8 cycles of each deck "as in the paper" at 32^3,
# nmax2 = 64, on the release processor build; then a check of the dump variables and the record.
# Usage (inside a registered run): bash smoke.sh <athena_cpu> <out_dir>
set -euo pipefail
EXE=$1; OUT=$2
WT=/data/haiyangw/nrpic/wt/E-stoch-inf
I=$WT/tracks/E-stoch-inf/repro/scope/inputs
M="mesh/nx1=32 mesh/nx2=32 mesh/nx3=32 meshblock/nx1=32 meshblock/nx2=32 meshblock/nx3=32 time/nlim=8 scalar_field/noise_nmax2=64"
mkdir -p "$OUT/sr" "$OUT/usr"
(cd "$OUT/sr" && "$EXE" -i "$I/sr_paper.athinput" $M \
   scalar_field/noise_mode_file=$WT/tracks/E-stoch-inf/ladder/inputs/modes_n64.txt > athena.log 2>&1)
(cd "$OUT/usr" && "$EXE" -i "$I/usr_paper.athinput" $M \
   scalar_field/noise_mode_file=$WT/tracks/E-stoch-inf/usr/inputs/modes_usr_n64.txt > athena.log 2>&1)
python3 -I "$WT/tracks/E-stoch-inf/repro/scope/scripts/check_dump.py" "$OUT" | tee "$OUT/smoke.json"
