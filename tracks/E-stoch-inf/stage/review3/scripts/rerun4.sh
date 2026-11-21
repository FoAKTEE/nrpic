#!/bin/bash
# Lead review of wave 3 (E-stoch-inf, batch 3): rerun the analyses of the packages `note`
# and `usr` (batch 2b) from their registered outputs, unchanged, into OUT; compare every JSON
# leaf with the registered run's output and with the copy committed in the package
# (compare_json.py); compare the note's PNGs in pixels and its tables in bytes.
# Predictions LR4 (a)-(d) of ../../../JOURNAL.md, entry 2026-11-21T12:58Z.
#
#   bash rerun4.sh OUT
set -e
OUT="$1"
S=/data/haiyangw/nrpic/scratch/E-stoch-inf
WT=/data/haiyangw/nrpic/wt/E-stoch-inf
T=$WT/tracks/E-stoch-inf
mkdir -p "$OUT"
export OMP_NUM_THREADS=3 OPENBLAS_NUM_THREADS=3 MKL_NUM_THREADS=3 MPLBACKEND=Agg
cd "$WT"
date -u
# --- (d) note: run_all.py as in E-20261121-080840-6112292 (two threads)
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 python3 $T/note/scripts/run_all.py --out "$OUT/note"
date -u
# --- (a) usr group 1: E-20261121-075307-4542ce1, -080134-a0cc3eb, -075022-7f76477
cd $T/usr/scripts
python3 analyse_cards.py --group g1 --run $S/E-20261120-222621-ba66218 --ref ../results --out "$OUT/usr/g1" --workers 3
OMP_NUM_THREADS=1 python3 floor_split.py --summary "$OUT/usr/g1/summary.json" --out "$OUT/usr/floor"
OMP_NUM_THREADS=1 python3 quick_records.py --run $S/E-20261120-222621-ba66218 --ref ../results --out "$OUT/usr/quick"
date -u
# --- (b) usr pair U256/U256m: E-20261121-101756-6bffd0c
python3 analyse_cards.py --group u256 --run $S/E-20261121-075255-8cf90e7 --run $S/E-20261121-085221-1f579fe --ref ../results --out "$OUT/usr/pair" --workers 3
date -u
# --- (c) lockstep: E-20261121-103157-96fee1d (coefficients of the rerun's pair analysis)
OMP_NUM_THREADS=2 python3 lockstep_shells.py --g1 $S/E-20261120-222621-ba66218 --u256 $S/E-20261121-075255-8cf90e7 --coeffs "$OUT/usr/pair/coeffs_N256.npz" --ref ../results --out "$OUT/usr/lock"
date -u
# --- comparison
cd "$WT"
R=$T/usr/results/runs
python3 $T/stage/review3/scripts/compare_json.py --out "$OUT/compare" \
  usr.g1="$OUT/usr/g1/summary.json|$S/E-20261121-075307-4542ce1/summary.json|$R/summary_E-20261121-075307-4542ce1.json" \
  usr.floor="$OUT/usr/floor/floor_split.json|$S/E-20261121-080134-a0cc3eb/floor_split.json|$R/floor_split_E-20261121-080134-a0cc3eb.json" \
  usr.quick="$OUT/usr/quick/quick_records.json|$S/E-20261121-075022-7f76477/quick_records.json|$R/quick_records_E-20261121-075022-7f76477.json" \
  usr.pair="$OUT/usr/pair/summary.json|$S/E-20261121-101756-6bffd0c/summary.json|$R/summary_E-20261121-101756-6bffd0c.json" \
  usr.lock="$OUT/usr/lock/lockstep_shells.json|$S/E-20261121-103157-96fee1d/lockstep_shells.json|$R/lockstep_shells_E-20261121-103157-96fee1d.json" \
  usr.u256single="$OUT/usr/pair/summary.json|$S/E-20261121-084815-63462b8/summary.json|$R/summary_E-20261121-084815-63462b8.json"
python3 $T/stage/review3/scripts/note_compare.py --new "$OUT/note" --committed $T/note --registered $S/E-20261121-080840-6112292 --out "$OUT/compare/note_compare.json"
date -u
