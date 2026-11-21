#!/usr/bin/env bash
# Runs the timing phases of work package omp one after the other, each as its own
# registered run (tracks/core/tools/run_registered.py): P9d (priv_cost.sh), then the
# scaling phases t16, t32, t64 (scaling_series.sh). Waits first until the run given as $1
# (the four-thread phase) has finished, so that no two timing phases overlap.
#   timing_chain.sh <run_id to wait for> [phases...]     (default: priv t16 t32 t64)
set -uo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
WT=$(cd "$HERE/../../.." && pwd)
PY=$WT/.venv/bin/python
export PATH=$WT/.venv/bin:$PATH PY
wait_for=$1; shift
phases=${*:-priv t16 t32 t64}
until grep -qE '"status": "(completed|failed)"' "$WT/tracks/core/runs/$wait_for/manifest.json"; do
  sleep 30
done
why="Registered by hand: nrpic-run refused (16 cores of core busy in other sessions)"
for ph in $phases; do
  case $ph in
    priv) n=16; cmd=(bash "$HERE/priv_cost.sh")
          what="omp P9d: cost of deposit_threads = private against atomic at 16 threads, cosmology and Newtonian boxes, kernel profile, two interleaved rounds" ;;
    t*)   n=${ph#t}; cmd=(bash "$HERE/scaling_series.sh" "$ph")
          what="omp strong scaling, phase $ph: O3 at $n threads, punc, cluster, cosmo, newton one after the other, two repeats, places from omp_places.py" ;;
  esac
  "$PY" "$WT/tracks/core/tools/run_registered.py" --cores "$n" --tag "omp-$ph" \
      --purpose "$what. $why" -- "${cmd[@]}" | tail -2
done
