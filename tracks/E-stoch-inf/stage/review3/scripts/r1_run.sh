#!/bin/bash
# Risk R1 on processors (lead batch 2a): L32p, L32m of the slow-roll ladder with the release
# core-v0.4 processor executable, then a word-by-word comparison with the same rungs of
# E-20261115-172636-ce98836 (core/scalar-2 a58e95b).
#   bash r1_run.sh OUT     (OUT = $NRPIC_RUN_DIR)
set -e
OUT="$1"
WT=/data/haiyangw/nrpic/wt/E-stoch-inf
cd "$WT"
MAXJOBS=2 bash tracks/E-stoch-inf/ladder/scripts/run_list_cpu.sh /data/haiyangw/nrpic/.work/build_cpu_v04/src/athena tracks/E-stoch-inf/stage/review3/inputs/r1_proc32.list "$OUT"
cat "$OUT/status.txt"
export OMP_NUM_THREADS=1 MPLBACKEND=Agg
python3 tracks/E-stoch-inf/stage/review3/scripts/r1_compare.py "$OUT" /data/haiyangw/nrpic/scratch/E-stoch-inf/E-20261115-172636-ce98836 "$OUT/compare"
