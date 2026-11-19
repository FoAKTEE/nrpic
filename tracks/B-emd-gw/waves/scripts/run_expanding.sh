#!/usr/bin/env bash
# Test X: the free tensor mode in the expanding box at several resolutions: initial data
# (make_expanding_ic.py) and one serial AthenaK process per resolution, in parallel
# (processor executable of core/requests-b).
#   run_expanding.sh       (through nrpic-run; output $NRPIC_RUN_DIR/N<n>/, data in N<n>/ic)
# Environment: NS (default "16 32 64"), ATHENA_CPU_EXE, EXTRA (more athena arguments),
# PYTHON (default python3).
set -euo pipefail
out=${NRPIC_RUN_DIR:?run through nrpic-run}
WT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
PKG=$WT/tracks/B-emd-gw/waves
EXE=${ATHENA_CPU_EXE:-/data/haiyangw/nrpic/scratch/core/exe/core_requests-b/athena_cpu}
IN=$PKG/inputs/expanding.athinput
NS=${NS:-16 32 64}
PY=${PYTHON:-python3}
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
for n in $NS; do
  mkdir -p "$out/N$n/ic"
  "$PY" "$PKG/scripts/make_expanding_ic.py" --n "$n" --out "$out/N$n/ic" > "$out/N$n/ic.log"
done
pids=()
for n in $NS; do
  d=$out/N$n
  cp "$IN" "$d/"
  ( cd "$d" && /usr/bin/time -v "$EXE" -i "$IN" -d "$d" mesh/nx1=$n mesh/nx2=$n mesh/nx3=$n \
      meshblock/nx1=$n meshblock/nx2=$n meshblock/nx3=$n \
      particles/particle_file="$d/ic/particles.nrp" problem/id_file="$d/ic/fields.bin" ${EXTRA:-} \
      > "$d/athena.log" 2> "$d/time.log"; echo "rc=$?" >> "$d/athena.log" ) &
  pids+=($!)
done
rc=0
for p in "${pids[@]}"; do wait "$p" || rc=1; done
for n in $NS; do
  echo "== N$n: $(grep -E 'zone-cycles/cpu_second|rc=' "$out/N$n/athena.log" | tr '\n' ' ')"
  grep -E "Elapsed|Maximum resident" "$out/N$n/time.log" || true
done
exit $rc
