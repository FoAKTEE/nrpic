#!/bin/bash
# Lead's rerun of one wave-1 helper package from its committed scripts (prediction L1 of
# tracks/A-emd-pbh/JOURNAL.md). Usage, from the worktree root, through nrpic-run:
#   harness/bin/nrpic-run submit --kind scouting --gate G1 --cores 4 --purpose "..." \
#       -- bash tracks/A-emd-pbh/analysis/lead_rerun.sh <scope|expball|criteria|newton|gauge>
# Output goes to $NRPIC_RUN_DIR (set by nrpic-run). Scripts that register themselves
# (expball, criteria, newton) also write their own run directories and manifests.
set -euo pipefail
pkg=${1:?package}
WT=$(pwd)
T=$WT/tracks/A-emd-pbh
OUT=${NRPIC_RUN_DIR:?run directory}
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-4} OPENBLAS_NUM_THREADS=${OMP_NUM_THREADS:-4} MKL_NUM_THREADS=${OMP_NUM_THREADS:-4}
echo "rerun of $pkg at $(git rev-parse --short=7 HEAD), $(date -u +%FT%TZ)"
case $pkg in
  scope)
    mkdir -p "$OUT/scope"
    python3 "$T/scope/scope_calc.py" --out "$OUT/scope"
    ;;
  expball)
    cd "$T/expball"
    python3 sym/sym_ltb_4d.py > "$OUT/sym_ltb_4d.txt" 2>&1; tail -3 "$OUT/sym_ltb_4d.txt"
    python3 sym/sym_slice.py > "$OUT/sym_slice.txt" 2>&1; tail -3 "$OUT/sym_slice.txt"
    python3 sym/sym_growing.py > "$OUT/sym_growing.txt" 2>&1; tail -3 "$OUT/sym_growing.txt"
    python3 -m pytest -q -p no:cacheprovider tests/ > "$OUT/pytest.txt" 2>&1 || true; tail -3 "$OUT/pytest.txt"
    python3 scripts/check_dataset.py /data/haiyangw/nrpic/scratch/A-emd-pbh/A-emd-pbh-20261115-121749-90764e1 > "$OUT/check_ds1.txt" 2>&1; tail -5 "$OUT/check_ds1.txt"
    python3 scripts/check_dataset.py /data/haiyangw/nrpic/scratch/A-emd-pbh/A-emd-pbh-20261115-121753-90764e1 > "$OUT/check_ds2.txt" 2>&1; tail -5 "$OUT/check_ds2.txt"
    python3 scripts/run_convergence.py --tag _leadrerun > "$OUT/convergence.txt" 2>&1; tail -30 "$OUT/convergence.txt"
    python3 scripts/run_noise.py > "$OUT/noise.txt" 2>&1; tail -20 "$OUT/noise.txt"
    ;;
  criteria)
    cd "$T/criteria"
    python3 predict.py --delta 0.1 --e 0.1 --p 0 --sigv 0 --aend 100 --sigmaH 0.01 > "$OUT/predict_example.txt" 2>&1
    python3 check_criteria.py > "$OUT/check_criteria.txt" 2>&1 || true; tail -60 "$OUT/check_criteria.txt"
    ;;
  newton)
    python3 "$T/newton/run_and_register.py" validate.py "lead rerun of P1-P7 (L1)" > "$OUT/validate.txt" 2>&1; tail -40 "$OUT/validate.txt"
    python3 "$T/newton/run_and_register.py" compare_snapshots.py "lead rerun of the snapshot self-test (L1)" --selftest > "$OUT/selftest.txt" 2>&1; tail -20 "$OUT/selftest.txt"
    ;;
  gauge)
    python3 "$T/gauge/scripts/vonneumann.py" --out "$OUT/t2" --n 49 > "$OUT/t2.txt" 2>&1; tail -15 "$OUT/t2.txt"
    python3 "$T/gauge/scripts/lapse_toy.py" --out "$OUT/t1" --X 56 > "$OUT/t1.txt" 2>&1; tail -15 "$OUT/t1.txt"
    python3 "$T/gauge/scripts/bh2_onset.py" --vn "$OUT/t2/vonneumann.json" --out "$OUT/t3" > "$OUT/t3.txt" 2>&1; tail -15 "$OUT/t3.txt"
    python3 "$T/gauge/scripts/kd_compare.py" --out "$OUT/t4" > "$OUT/t4.txt" 2>&1; tail -15 "$OUT/t4.txt"
    ;;
  *) echo "unknown package $pkg"; exit 2 ;;
esac
echo "end $(date -u +%FT%TZ)"
