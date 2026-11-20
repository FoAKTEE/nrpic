#!/usr/bin/env bash
# Test T4 of tracks/core/JOURNAL-oblate.md (entry 9): the Newtonian reference of the
# oblate collapse with a threaded processor executable, 64^3 and then 128^3 cells, one
# after the other with THREADS threads each (default 6).  The serial pair is
# run_newton.sh.  Run under nrpic-run (NRPIC_RUN_DIR is the output directory):
#   harness/bin/nrpic-run submit --kind scouting --gate G2 --cores 6 ... -- \
#     bash tracks/core/analysis/oblate/run_newton_omp.sh EXE PARTICLE_FILE [CASES]
# CASES: "n64 n128" (default), or one of them.
set -u
EXE=$1
IC=$2
CASES=${3:-"n64 n128"}
INP=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)/problems/oblate/oblate_newton.athinput
OUT=${NRPIC_RUN_DIR:?run under nrpic-run}
export OMP_NUM_THREADS=${THREADS:-6}
export OMP_PROC_BIND=false
rc=0
for name in $CASES; do
  case $name in
    n64)  extra=() ;;
    n128) extra=(mesh/nx1=128 mesh/nx2=128 mesh/nx3=128) ;;
    *) echo "unknown case $name" >&2; exit 2 ;;
  esac
  mkdir -p "$OUT/$name"
  ( cd "$OUT/$name" && "$EXE" -i "$INP" -d "$OUT/$name" particles/particle_file="$IC" \
      "${extra[@]}" > athena.log 2>&1 )
  r=$?
  echo "$name rc=$r threads=$OMP_NUM_THREADS"
  (( r != 0 )) && rc=1
done
exit $rc
