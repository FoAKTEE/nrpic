#!/usr/bin/env bash
# Test F: the oblique linear wave at several resolutions, one serial AthenaK process per
# resolution, in parallel (processor executable of core/requests-b).
#   run_flat.sh            (through nrpic-run; output $NRPIC_RUN_DIR/N<n>/)
# Environment: NS (default "16 32 64"), ATHENA_CPU_EXE (default: core/requests-b's
# athena_cpu, scratch/core/exe/core_requests-b/READY), EXTRA (more athena arguments).
set -euo pipefail
out=${NRPIC_RUN_DIR:?run through nrpic-run}
WT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
EXE=${ATHENA_CPU_EXE:-/data/haiyangw/nrpic/scratch/core/exe/core_requests-b/athena_cpu}
IN=$WT/tracks/B-emd-gw/waves/inputs/flat_oblique.athinput
NS=${NS:-16 32 64}
export OMP_NUM_THREADS=1
pids=()
for n in $NS; do
  d=$out/N$n
  mkdir -p "$d"
  cp "$IN" "$d/"
  ( cd "$d" && /usr/bin/time -v "$EXE" -i "$IN" -d "$d" mesh/nx1=$n mesh/nx2=$n mesh/nx3=$n \
      meshblock/nx1=$n meshblock/nx2=$n meshblock/nx3=$n ${EXTRA:-} \
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
