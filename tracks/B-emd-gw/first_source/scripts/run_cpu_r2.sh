#!/usr/bin/env bash
# Processor companion of the second round of first_source: cases at 32^3 (two particles per
# cell and direction) with inputs/conv.athinput on core's requests-b processor executable,
# one serial AthenaK process each, in parallel.
#   run_cpu_r2.sh name=<ic dir> [name=<ic dir> ...]      (output: $NRPIC_RUN_DIR/<name>/)
# Environment: ATHENA_CPU_EXE (default: scratch/core/exe/core_requests-b/athena_cpu).
set -euo pipefail
out=${NRPIC_RUN_DIR:?run through nrpic-run}
WT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
EXE=${ATHENA_CPU_EXE:-/data/haiyangw/nrpic/scratch/core/exe/core_requests-b/athena_cpu}
IN=$WT/tracks/B-emd-gw/first_source/inputs/conv.athinput
MESH="mesh/nx1=32 mesh/nx2=32 mesh/nx3=32 meshblock/nx1=16 meshblock/nx2=16 meshblock/nx3=16 particles/traj_ntrack=190"
export OMP_NUM_THREADS=1
pids=()
names=()
for spec in "$@"; do
  c=${spec%%=*}
  ic=${spec#*=}
  d=$out/$c
  mkdir -p "$d"
  cp "$IN" "$d/"
  ( cd "$d" && "$EXE" -i "$IN" -d "$d" $MESH \
      particles/particle_file="$ic/particles.nrp" problem/id_file="$ic/fields.bin" \
      > "$d/athena.log" 2>&1; echo "rc=$?" >> "$d/athena.log" ) &
  pids+=($!)
  names+=("$c")
done
rc=0
for p in "${pids[@]}"; do wait "$p" || rc=1; done
for c in "${names[@]}"; do echo "== $c: $(tail -n 3 "$out/$c/athena.log" | tr '\n' ' ')"; done
exit $rc
