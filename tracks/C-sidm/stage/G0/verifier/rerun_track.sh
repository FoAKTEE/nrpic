#!/bin/bash
# Reruns of the track's own scripts and tests that support claims V1-V6, outputs only under
# $NRPIC_RUN_DIR (no byte code, no pytest cache written into the packages).
set -uo pipefail
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONDONTWRITEBYTECODE=1
T=tracks/C-sidm
O=${NRPIC_RUN_DIR:?}
rc=0
step() { local name=$1; shift; mkdir -p "$O/$name"; echo "== $name: $*";
         ( export NRPIC_RUN_DIR="$O/$name"; "$@" ) > "$O/$name/stdout.txt" 2>&1;
         local e=$?; echo "$name exit $e" | tee -a "$O/exits.txt"; [ $e -eq 0 ] || rc=1; }
step seq_mono python3 $T/scope/scripts/seq_monoenergetic.py
step king_seq python3 $T/scope/scripts/king_sequence.py
step knudsen_costs python3 $T/scope/scripts/knudsen_costs.py
step test_tmb bash -c "cd $T/gravothermal && python3 -E test_tmb.py"
step pytest_refs bash -c "cd $T/collide && python3 -m pytest -q -p no:cacheprovider REFERENCES/tests"
step knudsen_conv bash -c "cd $T/equilibria && python3 knudsen.py --out $O/knudsen_conv --N 10000"
exit $rc
