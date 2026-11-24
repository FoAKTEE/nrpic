#!/bin/bash
# Post-verdict check (after VERIFIER.md was committed): the definitions of the note's scripts
# (entry window 0.05 < N <= ln 8; shells with more than 10 modes) applied with MY readers.
set -e
OUT="$1"; S=/data/haiyangw/nrpic/scratch/E-stoch-inf; V=tracks/E-stoch-inf/repro/verify/scripts
python3 $V/entrywin.py --out "$OUT/entrywin"
python3 $V/compare.py --case sr --lat $S/E-20261124-182136-518eee2 --deck $S/E-20261121-202935-31520bc/P256/sr_base.athinput \
  --modes tracks/E-stoch-inf/ladder/inputs/modes_n4096.txt --run $S/E-20261121-202935-31520bc --out "$OUT/sr" > /dev/null
python3 $V/compare.py --case usr --lat $S/E-20261124-182151-93742a3 --deck $S/E-20261123-021204-2f573ec/chain/input.athinput \
  --modes tracks/E-stoch-inf/usr/inputs/modes_usr_n4096.txt --run $S/E-20261123-021204-2f573ec --out "$OUT/usr" > /dev/null
for n in 32 64 128; do
  python3 $V/compare.py --case sr --lat $S/E-20261124-183222-02ff27c/lat_C${n}S \
    --deck $S/E-20261123-020704-2b99463/C${n}S/sr_paper.athinput --modes tracks/E-stoch-inf/ladder/inputs/modes_n64.txt \
    --run $S/E-20261123-020704-2b99463/C${n}S --out "$OUT/C${n}S" > /dev/null
done
