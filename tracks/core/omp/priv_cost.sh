#!/usr/bin/env bash
# P9d: cost of the private copies of the deposit (deposit_threads = private) against the
# atomic additions, at THREADS threads (default 16), with the time per kernel
# (tools/kernel_timer.cpp), for the cosmology box and the Newtonian box; atomic and private
# interleaved, ROUNDS rounds (default 2), so that the load of the machine affects both alike.
#   priv_cost.sh            (run inside the output directory)
set -euo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PY=${PY:-python3}
NT=${THREADS:-16}; ROUNDS=${ROUNDS:-2}
for r in $(seq 1 "$ROUNDS"); do
  for c in "cosmo 0.25" "newton 1.0"; do
    set -- $c
    "$PY" "$HERE/scaling.py" --exe O3 --cases "$1" --threads "$NT" --repeat 1 --nlim-factor "$2" \
        --bind true --places auto --profile --tag "atomic$r" --out .
    "$PY" "$HERE/scaling.py" --exe O3 --cases "$1" --threads "$NT" --repeat 1 --nlim-factor "$2" \
        --bind true --places auto --profile --mode priv --tag "priv$r" --out .
  done
done
