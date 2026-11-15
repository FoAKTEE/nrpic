#!/usr/bin/env bash
# Processor companion of the card scan: the five cases of first_source at 32^3 (two
# particles per cell and direction), one serial AthenaK process each, in parallel.
#   run_cpu_scan.sh <ic dir>        (output: $NRPIC_RUN_DIR/<case>/)
# <ic dir> holds eps0, eps0p1, eps0p3, eps1 from build_ic.sh with N=32. The second-gauge case
# cw_eps1_gd uses the eps1 data with the Gamma-driver shift. Environment: ATHENA_CPU_EXE
# (default: the core-v0.3 processor build of the main checkout), CASES (subset of names).
set -euo pipefail
ic=$1
out=${NRPIC_RUN_DIR:?run through nrpic-run}
WT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
EXE=${ATHENA_CPU_EXE:-/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena}
IN=$WT/tracks/B-emd-gw/first_source/inputs/crossed.athinput
GD="z4c/shift_Gamma=0.75 z4c/shift_eta=1.0 z4c/shift_advect=1.0 z4c/lapse_advect=1.0"
MESH="mesh/nx1=32 mesh/nx2=32 mesh/nx3=32 meshblock/nx1=16 meshblock/nx2=16 meshblock/nx3=16 particles/traj_ntrack=190"
CASES=${CASES:-cw_eps0 cw_eps0p1 cw_eps0p3 cw_eps1 cw_eps1_gd}
export OMP_NUM_THREADS=1
pids=()
for c in $CASES; do
  src=${c#cw_}; src=${src%_gd}
  extra=""
  [[ $c == *_gd ]] && extra=$GD
  d=$out/$c
  mkdir -p "$d"
  cp "$IN" "$d/"
  ( cd "$d" && "$EXE" -i "$IN" -d "$d" $MESH \
      particles/particle_file="$ic/$src/particles.nrp" problem/id_file="$ic/$src/fields.bin" $extra \
      > "$d/athena.log" 2>&1; echo "rc=$?" >> "$d/athena.log" ) &
  pids+=($!)
done
rc=0
for p in "${pids[@]}"; do wait "$p" || rc=1; done
for c in $CASES; do echo "== $c: $(tail -n 3 "$out/$c/athena.log" | tr '\n' ' ')"; done
exit $rc
