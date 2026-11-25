#!/usr/bin/env bash
# Processor tests of the merged source (main with release core-v0.5, plus work package clump2):
#   M1  the static tests TB with the merged build against the run of the build before the merge
#       (core-20261120-222933-0a01a56: same generator, same inputs)
#   R5  inputs without the new options: release core-v0.5 against the merged build, byte by byte
# Run through nrpic-run on one core; exit status 0 only if everything is identical.
set -u
out=${NRPIC_RUN_DIR:?run through nrpic-run}
id=${NRPIC_RUN_ID:?run through nrpic-run}
a=tracks/core/analysis
rel=/data/haiyangw/nrpic/.work/build_cpu_v05/src/athena
new=.work/build_cpu/src/athena
old=core-20261120-222933-0a01a56
st=0
python3 $a/clump2/run_boost_static.py --jobs 1 --n 32,64 --v 0.1,0.3 --kinds curv,corr --no-stratified --out "$out/tb" > "$out/tb.log" 2>&1 || st=1
python3 $a/clump2/tb_residual_diag.py --run "$id/tb" --n 32,64 --out "$out/diag" > "$out/diag.log" 2>&1 || st=1
python3 $a/clump2/tb_residual_diag.py --run "$old/tb" --n 32,64 --out "$out/diag_old" > "$out/diag_old.log" 2>&1 || st=1
python3 $a/clump2/compare_tb.py --a "$old/tb" --b "$id/tb" --diag-a "$id/diag_old/tb_residual_diag.json" \
    --diag-b "$id/diag/tb_residual_diag.json" --out "$out/m1" > "$out/m1.log" 2>&1 || st=1
python3 $a/clump/regress.py --base $rel --new $new --out "$out/regress" \
    --cases regress_cf,cf_table_regress,by_static > "$out/regress.log" 2>&1 || st=1
python3 $a/clump/regress.py --base $rel --new $new --out "$out/regress_jeans" \
    --cases jeans > "$out/regress_jeans.log" 2>&1 || st=1
exit $st
