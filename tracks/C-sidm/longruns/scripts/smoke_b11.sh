#!/usr/bin/env bash
# smoke test of the batch-11 decks on the threaded processor build: a few cycles each
set -euo pipefail
OUT=$1
EXE=/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v06/athena_cpu_omp
export OMP_NUM_THREADS=4 OMP_PROC_BIND=false
for d in D2M16_cc2_kn10_f4_s1 A8N_y0p33403_N1e6_s1_ctrl; do
  mkdir -p "$OUT/$d"
  ( cd "$OUT/$d" && "$EXE" -i /data/haiyangw/nrpic/wt/C-sidm/tracks/C-sidm/longruns/inputs/$d.athinput -d "$OUT/$d" time/nlim=3 time/ndiag=1 output2/dt=1e9 > athena.log 2>&1; echo "$d rc=$?" )
  grep -E "MeshBlock|Setup complete|cycle=|Terminating|nbtotal|blocks" "$OUT/$d/athena.log" | head -12
done
