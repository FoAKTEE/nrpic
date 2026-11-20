#!/usr/bin/env bash
# The strong-scaling series of work package omp, one phase per call (each phase is one
# registered run). Threads are placed by scripts/omp_places.py (the least busy cores of
# one NUMA node at the start of each run) unless PLACES/BIND say otherwise.
#   scaling_series.sh t1        one thread, the four cases side by side (4 cores)
#   scaling_series.sh t4        four threads, the four cases side by side (16 cores)
#   scaling_series.sh t6        6 threads, one case after the other, two repeats
#   scaling_series.sh t1solo    one thread, cosmo and newton, one run at a time
#   scaling_series.sh collapse  the isolated Newtonian collapse at one and six threads
#   scaling_series.sh t16       16 threads, one case after the other, two repeats
#   scaling_series.sh t32|t64   32 or 64 threads, one case after the other, two repeats
#   scaling_series.sh serial    the serial executable S, the four cases side by side
# Environment: EXE (default O3), BIND (default true), PLACES (default auto)
set -euo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
EXE=${EXE:-O3}; BIND=${BIND:-true}; PLACES=${PLACES:-auto}
phase=$1
run() {  # case threads nlim-factor repeats tag [places]
  python3 "$HERE/scaling.py" --exe "$EXE" --cases "$1" --threads "$2" --nlim-factor "$3" \
      --repeat "$4" --bind "$BIND" --places "${6:-$PLACES}" --tag "$5" --out .
}
# Side-by-side phases: the places of the four runs are chosen once (the 4 n least busy
# cores) and split into four disjoint groups of n; four separate calls of omp_places.py
# at the same moment pick the same cores (run core-20261119-160404-beddeac, stopped).
split4() {  # threads -> sets G0..G3
  local n=$1 all
  if [[ $PLACES == auto ]]; then
    all=$(python3 "$HERE/../../../scripts/omp_places.py" $((4*n)))
    mapfile -t parts < <(sed 's/},{/}\n{/g' <<< "$all")
    G0=$(IFS=,; echo "${parts[*]:0:n}"); G1=$(IFS=,; echo "${parts[*]:n:n}")
    G2=$(IFS=,; echo "${parts[*]:$((2*n)):n}"); G3=$(IFS=,; echo "${parts[*]:$((3*n)):n}")
  else
    G0=$PLACES; G1=$PLACES; G2=$PLACES; G3=$PLACES
  fi
}
case $phase in
  t1)
    split4 1
    run punc 1 0.1 1 t1 "$G0" & run cluster 1 0.19 1 t1 "$G1" & run cosmo 1 0.25 1 t1 "$G2" &
    run newton 1 0.5 1 t1 "$G3" & wait ;;
  serial)
    EXE=S; BIND=none; PLACES=none
    run punc 1 0.1 1 serial & run cluster 1 0.19 1 serial & run cosmo 1 0.25 1 serial &
    run newton 1 0.5 1 serial & wait ;;
  t4)
    split4 4
    run punc 4 0.125 2 t4 "$G0" & run cluster 4 0.25 2 t4 "$G1" & run cosmo 4 0.25 2 t4 "$G2" &
    run newton 4 1.0 2 t4 "$G3" & wait ;;
  t6)   # the limit per session since decision 0019: one case after the other
    run punc 6 0.125 2 t6; run cluster 6 0.25 2 t6
    run cosmo 6 0.25 2 t6; run newton 6 1.0 2 t6 ;;
  t1solo)   # one thread, one run at a time (the side-by-side runs of t1 share caches)
    run cosmo 1 0.125 1 t1solo; run newton 1 0.5 1 t1solo ;;
  collapse) # Newtonian mode with isolated boundaries at one and at six threads
    run collapse 1 0.5 1 t1solo; run collapse 6 1.0 2 t6 ;;
  t16|t32|t64)
    n=${phase#t}
    run punc "$n" 0.25 2 "$phase"; run cluster "$n" 0.5 2 "$phase"
    run cosmo "$n" 0.5 2 "$phase"; run newton "$n" 1.0 2 "$phase" ;;
  *) echo "unknown phase $phase" >&2; exit 1 ;;
esac
