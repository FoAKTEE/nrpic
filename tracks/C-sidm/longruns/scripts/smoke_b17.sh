#!/usr/bin/env bash
# smoke test of the batch-17 decks on the threaded processor build of the series (core-v0.6):
# three cycles each, to check that the deck and its particle file load (no physics is read)
#   smoke_b17.sh OUTDIR DECK [DECK ...]     (DECK: name under tracks/C-sidm/longruns/inputs/)
set -euo pipefail
OUT=$1; shift
EXE=/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v06/athena_cpu_omp
export OMP_NUM_THREADS=4 OMP_PROC_BIND=false
for d in "$@"; do
  mkdir -p "$OUT/$d"
  ( cd "$OUT/$d" && "$EXE" -i /data/haiyangw/nrpic/wt/C-sidm/tracks/C-sidm/longruns/inputs/$d.athinput -d "$OUT/$d" time/nlim=3 time/ndiag=1 output2/dt=1e9 > athena.log 2>&1; echo "$d rc=$?" )
  grep -E "Setup complete|cycle=|Terminating|particles|nbtotal" "$OUT/$d/athena.log" | head -8
done
