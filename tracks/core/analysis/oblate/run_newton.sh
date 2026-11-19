#!/usr/bin/env bash
# Test T4 of tracks/core/JOURNAL-oblate.md (entry 7): the Newtonian reference of the
# oblate collapse in AthenaK, the particles of T3 at 64^3 and 128^3 cells, side by side
# on two processor cores. Run under nrpic-run (NRPIC_RUN_DIR is the output directory):
#   harness/bin/nrpic-run submit --kind scouting --gate G2 --cores 2 ... -- \
#     bash tracks/core/analysis/oblate/run_newton.sh EXE PARTICLE_FILE
set -u
EXE=$1
IC=$2
INP=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)/problems/oblate/oblate_newton.athinput
OUT=${NRPIC_RUN_DIR:?run under nrpic-run}
export OMP_NUM_THREADS=1
run() {  # name, extra arguments
  local name=$1; shift
  mkdir -p "$OUT/$name"
  cd "$OUT/$name" && "$EXE" -i "$INP" -d "$OUT/$name" particles/particle_file="$IC" "$@" \
     > athena.log 2>&1
}
run n64 & p1=$!
run n128 mesh/nx1=128 mesh/nx2=128 mesh/nx3=128 & p2=$!
wait $p1; r1=$?
wait $p2; r2=$?
echo "n64 rc=$r1 n128 rc=$r2"
exit $(( r1 != 0 || r2 != 0 ))
