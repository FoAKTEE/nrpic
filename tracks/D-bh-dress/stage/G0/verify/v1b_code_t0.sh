#!/bin/bash
# Verifier check C1b: rerun the start-time code check of D-pre-1 on the RELEASE processor
# executable (core-v0.3, main) instead of the branch build of wave 1, and compare the raw
# constraint fields with the wave-1 dumps cell by cell.
#   v1b_code_t0.sh   (run through nrpic-run; output in $NRPIC_RUN_DIR)
set -euo pipefail
WT=/data/haiyangw/nrpic/wt/D-bh-dress
TAB=/data/haiyangw/nrpic/scratch/D-bh-dress/D-bh-dress-20261115-042653-f3da881/es.tab
EXE=/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena
OUT="${NRPIC_RUN_DIR:?run through nrpic-run}"
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-8}"
for spec in "dx1 1.0" "dx05 0.5"; do
  set -- $spec
  mkdir -p "$OUT/$1"
  python3 "$WT/tracks/D-bh-dress/einstein_straus/code_t0_check.py" prep --tab "$TAB" --dx "$2" --half 48 --out "$OUT/$1"
  "$EXE" -i "$OUT/$1/es_t0.athinput" -d "$OUT/$1" > "$OUT/$1/log.txt" 2>&1
done
python3 "$WT/tracks/D-bh-dress/stage/G0/verify/v1b_compare.py" --out "$OUT" \
  --new "$OUT/dx1" "$OUT/dx05" \
  --old /data/haiyangw/nrpic/scratch/D-bh-dress/D-bh-dress-20261115-043002-d51c7f2 \
        /data/haiyangw/nrpic/scratch/D-bh-dress/D-bh-dress-20261115-043033-4df1e76
