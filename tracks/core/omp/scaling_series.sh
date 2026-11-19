#!/usr/bin/env bash
# The strong-scaling series of work package omp, one phase per call (each phase is one
# registered run). Threads are placed by scripts/omp_places.py (the least busy cores of
# one NUMA node at the start of each run) unless PLACES/BIND say otherwise.
#   scaling_series.sh t1        one thread, the four cases side by side (4 cores)
#   scaling_series.sh t4        four threads, the four cases side by side (16 cores)
#   scaling_series.sh t16       16 threads, one case after the other, two repeats
#   scaling_series.sh t32|t64   32 or 64 threads, one case after the other, two repeats
#   scaling_series.sh serial    the serial executable S, the four cases side by side
# Environment: EXE (default O3), BIND (default true), PLACES (default auto)
set -euo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
EXE=${EXE:-O3}; BIND=${BIND:-true}; PLACES=${PLACES:-auto}
phase=$1
run() {  # case threads nlim-factor repeats tag
  python3 "$HERE/scaling.py" --exe "$EXE" --cases "$1" --threads "$2" --nlim-factor "$3" \
      --repeat "$4" --bind "$BIND" --places "$PLACES" --tag "$5" --out .
}
case $phase in
  t1)
    run punc 1 0.1 1 t1 & run cluster 1 0.19 1 t1 & run cosmo 1 0.25 1 t1 &
    run newton 1 0.5 1 t1 & wait ;;
  serial)
    EXE=S; BIND=none; PLACES=none
    run punc 1 0.1 1 serial & run cluster 1 0.19 1 serial & run cosmo 1 0.25 1 serial &
    run newton 1 0.5 1 serial & wait ;;
  t4)
    run punc 4 0.125 2 t4 & run cluster 4 0.25 2 t4 & run cosmo 4 0.25 2 t4 &
    run newton 4 1.0 2 t4 & wait ;;
  t16|t32|t64)
    n=${phase#t}
    run punc "$n" 0.25 2 "$phase"; run cluster "$n" 0.5 2 "$phase"
    run cosmo "$n" 0.5 2 "$phase"; run newton "$n" 1.0 2 "$phase" ;;
  *) echo "unknown phase $phase" >&2; exit 1 ;;
esac
