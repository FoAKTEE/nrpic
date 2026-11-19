#!/bin/bash
# Lead's wave-2b rechecks L13 (box_rerun), L14 (collisional cluster runs), L15 (King fluid
# onset); predictions in tracks/C-sidm/JOURNAL.md 2026-11-19T15:15Z.
# Run from the worktree root through nrpic-run (output in $NRPIC_RUN_DIR), two cores.
set -euo pipefail
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
D=tracks/C-sidm/stage/review_wave2
O=${NRPIC_RUN_DIR:?}
( python3 $D/rv_cc.py > "$O/rv_cc.log" 2>&1
  python3 $D/rv_king_onset.py > "$O/rv_king_onset.log" 2>&1 ) &
p1=$!
python3 $D/rv_box2b.py > "$O/rv_box2b.log" 2>&1 &
p2=$!
rc=0
wait $p1 || rc=1
wait $p2 || rc=1
echo "review 2b done rc=$rc"
exit $rc
