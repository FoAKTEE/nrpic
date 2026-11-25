#!/usr/bin/env bash
# the processor run FX/EN of work package clump2 (journal, session clump2-3); run through nrpic-run
set -u
out=${NRPIC_RUN_DIR:?run through nrpic-run}
id=${NRPIC_RUN_ID:?run through nrpic-run}
a=tracks/core/analysis/clump2
st=0
python3 $a/energy_check.py --out "$out/en" > "$out/en.log" 2>&1 || st=1
python3 $a/binary_evolution_check.py --dir core-20261119-155219-32602d2/orbit --tmax 125 --tag _te125 --out "$out/te125" > "$out/te125.log" 2>&1 || st=1
python3 $a/card_vs_cpu.py --tc core-20261119-145433-8c4083d --te core-20261119-155219-32602d2 --t0 core-20261119-160021-b153852 --early core-20261119-161758-47f52ad --out "$out/g" > "$out/g.log" 2>&1 || st=1
python3 $a/run_boost_static.py --jobs 2 --n 32,64,128 --v 0.1,0.3 --kinds curv,corr --no-stratified --out "$out/tb" > "$out/tb.log" 2>&1 || st=1
python3 $a/tb_residual_diag.py --run "$id/tb" --out "$out/diag" > "$out/diag.log" 2>&1 || st=1
python3 $a/corr_surface_check.py --tb "$id/tb" --out "$out/surf" > "$out/surf.log" 2>&1 || st=1
exit $st
