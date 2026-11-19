#!/usr/bin/env bash
# The processor tests of work package clump2 in one registered run on one core (the
# owner's allotment of cores is shared by several sessions; one slot is held for all):
#   regress/   test R, short cases        (tracks/core/analysis/clump/regress.py)
#   tb/        tests TB                   (run_boost_static.py)
#   td/        test TD                    (run_binary_static.py)
#   regress_jeans/  test R, the first paper's two-overdensity configuration
# Exit status 0 only if all four ran and compared clean.
set -u
out=${NRPIC_RUN_DIR:?run through nrpic-run}
here=tracks/core/analysis
base=/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena
new=.work/build_cpu/src/athena
st=0
python3 $here/clump/regress.py --base $base --new $new --out "$out/regress" \
    --cases regress_cf,cf_table_regress,by_static || st=1
python3 $here/clump2/run_boost_static.py --jobs 1 --out "$out/tb" || st=1
python3 $here/clump2/run_binary_static.py --out "$out/td" || st=1
python3 $here/clump/regress.py --base $base --new $new --out "$out/regress_jeans" \
    --cases jeans || st=1
exit $st
