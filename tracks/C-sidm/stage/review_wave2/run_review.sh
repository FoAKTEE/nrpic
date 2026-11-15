#!/bin/bash
# Lead's wave-2 rechecks L8-L11 and the rerun of the verifier suite (stage/G0/verifier).
# Run from the worktree root through nrpic-run (output in $NRPIC_RUN_DIR).
set -euo pipefail
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
D=tracks/C-sidm/stage/review_wave2
O=${NRPIC_RUN_DIR:?}
python3 $D/rv_note.py > "$O/rv_note.log" 2>&1
python3 $D/rv_scan.py > "$O/rv_scan.log" 2>&1
python3 $D/rv_models.py > "$O/rv_models.log" 2>&1
python3 $D/rv_box.py > "$O/rv_box.log" 2>&1
# verifier suite: rerun into a subdirectory and compare with registered run C-20261115-170630-1037f6a
V=/data/haiyangw/nrpic/scratch/C-sidm/C-20261115-170630-1037f6a
NRPIC_RUN_DIR="$O/verifier_rerun" bash tracks/C-sidm/stage/G0/verifier/run_all.sh > "$O/verifier_rerun.log" 2>&1
( cd "$O/verifier_rerun" && for f in $(find . -name '*.json' | sort); do
    if cmp -s "$f" "$V/$f"; then echo "identical $f"; else echo "DIFFERS $f"; fi
  done ) > "$O/verifier_compare.txt"
echo "review done"
