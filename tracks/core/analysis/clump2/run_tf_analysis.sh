#!/usr/bin/env bash
# Analysis of the card tests TF (gauge) and M2 (merged card build), and the comparison G3 of the
# card run v0.3 of TC with the processor run that test D started by mistake (journal, session
# clump2-4). Run through nrpic-run:  run_tf_analysis.sh <run id of TF> [<run id of M2>]
set -u
out=${NRPIC_RUN_DIR:?run through nrpic-run}
a=tracks/core/analysis/clump2
tf=${1:?run id of TF}
m2=${2:-}
tc=core-20261119-145433-8c4083d
te=core-20261119-155219-32602d2
st=0
python3 $a/gauge_evolution_check.py \
  --runs "eta2=$tc/v0.3,eta0.3=$tf/v0.3_e03,eta0.1=$tf/v0.3_e01,eta0.03=$tf/v0.3_e003,eta2_shift=$tc/v0.3s,eta0.1_shift=$tf/v0.3s_e01,eta2_n4=$tf/v0.3_n4" \
  --rest "rest=$tc/v0" --rest2 "rest_e01=$tf/v0_e01" --v 0.3 --out "$out/tf" > "$out/tf.log" 2>&1 || st=1
python3 $a/binary_evolution_check.py --dir $tf/orbit_e01 --tmax 125 --tag _e01 --out "$out/orbit_e01" > "$out/orbit_e01.log" 2>&1 || st=1
python3 $a/binary_evolution_check.py --dir $te/orbit --tmax 125 --tag _te125 --out "$out/te125" > "$out/te125.log" 2>&1 || st=1
python3 $a/compare_two_runs.py --a $tc/v0.3 --b core-20261120-223538-742c0b7/v0.3_t0 --out "$out/g3" > "$out/g3.log" 2>&1 || st=1
if [[ -n $m2 ]]; then
  python3 $a/compare_two_runs.py --a $m2/v0.3 --b $tc/v0.3 --out "$out/m2" > "$out/m2.log" 2>&1 || st=1
fi
exit $st
