#!/usr/bin/env bash
# Is the restart of the cluster of test T3 exact on one rank?  For each executable given:
# the uninterrupted run (40 cycles, restart dumps at 0, 20, 40) and the run restarted from
# the dump of cycle 20, compared by mpi_tests.py (restart mode, pair 1:1).
#   restart_one_rank.sh <outdir> <label>=<exe> [<label>=<exe> ...]
set -u
OUT=$1; shift
PY=/data/haiyangw/nrpic/wt/core-mpi/.venv/bin/python
T=/data/haiyangw/nrpic/wt/core-mpi/tracks/core/analysis/mpi/mpi_tests.py
pids=()
for spec in "$@"; do
  label=${spec%%=*}; exe=${spec#*=}
  (
    "$PY" "$T" --case t3_cluster --ranks 1 --exe "$exe" --out "$OUT/$label/full" \
      > "$OUT/$label.full.log" 2>&1
    "$PY" "$T" --restart-of "$OUT/$label/full" --pairs 1:1 --rst rst/cl.00001.rst \
      --exe "$exe" --out "$OUT/$label/restart" > "$OUT/$label.restart.log" 2>&1
  ) &
  pids+=($!)
done
rc=0
for p in "${pids[@]}"; do wait "$p" || rc=1; done
for spec in "$@"; do
  label=${spec%%=*}
  echo "== $label"; grep -v "^figure" "$OUT/$label.restart.log"
done
exit $rc
