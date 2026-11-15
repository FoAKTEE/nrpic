#!/bin/bash
# Lead review of C-sidm helper packages: rerun every package's tests and its registered
# reference runs into this run's directory, then compare with the registered outputs
# (compare_reruns.py). Run through harness/bin/nrpic-run (sets NRPIC_RUN_DIR); worktree root
# is the working directory. Processors only.
set -uo pipefail
OUT=${NRPIC_RUN_DIR:?run through nrpic-run}
WT=$(pwd)
T=$WT/tracks/C-sidm
S=/data/haiyangw/nrpic/scratch/C-sidm
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4
status=0
step() { echo "== $1 ($(date -u +%H:%M:%S))"; }

step "collide: REFERENCES tests"
(cd "$T/collide" && python3 -m pytest -q -p no:cacheprovider REFERENCES/tests) > "$OUT/collide_references_pytest.log" 2>&1 || status=1
tail -3 "$OUT/collide_references_pytest.log"
step "collide: analysis pipeline tests"
(cd "$T/collide" && python3 -m pytest -q -p no:cacheprovider analysis/tests) > "$OUT/collide_analysis_pytest.log" 2>&1 || status=1
tail -3 "$OUT/collide_analysis_pytest.log"

step "gravothermal: unit tests"
(cd "$T/gravothermal" && python3 -E test_tmb.py) > "$OUT/gravothermal_test_tmb.log" 2>&1 || status=1
tail -3 "$OUT/gravothermal_test_tmb.log"
step "gravothermal: polytrope turning-point check"
mkdir -p "$OUT/polytrope"
(cd "$T/gravothermal" && python3 -E pulsation_check.py "$OUT/polytrope") > "$OUT/polytrope/log.txt" 2>&1 || status=1
tail -3 "$OUT/polytrope/log.txt"

for s in seq_monoenergetic king_sequence knudsen_costs; do
  step "scope: $s"
  mkdir -p "$OUT/scope_$s"
  NRPIC_RUN_DIR="$OUT/scope_$s" python3 "$T/scope/scripts/$s.py" > "$OUT/scope_$s/stdout.txt" 2>&1 || status=1
  tail -2 "$OUT/scope_$s/stdout.txt"
done

step "collide: T6-0 collisionless step with the processor executable"
mkdir -p "$OUT/t6"
NRPIC_RUN_DIR="$OUT/t6" bash "$T/collide/analysis/run_step_collisionless.sh" 100000 > "$OUT/t6/stdout.log" 2>&1 || status=1
tail -3 "$OUT/t6/stdout.log"

step "equilibria: offline checks of the 13 models"
mkdir -p "$OUT/eqcheck"
(cd "$T/equilibria" && python3 check_equilibria.py --ic "$S/C-sidm-20261115-120610-b4592be" --out "$OUT/eqcheck") > "$OUT/eqcheck/stdout.log" 2>&1 || status=1
tail -3 "$OUT/eqcheck/stdout.log"

step "compare with the registered outputs"
python3 "$T/review/compare_reruns.py" "$OUT" || status=1
step "done, status $status"
exit $status
