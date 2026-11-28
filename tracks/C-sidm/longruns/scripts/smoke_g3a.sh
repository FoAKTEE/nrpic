#!/usr/bin/env bash
# smoke test of the G3 step-1a decks (make_decks_g3a.py) on the threaded processor build of
# release core-v0.8: three cycles each, the finder searching at every cycle, to check that the
# deck, its table and particle file load and that the finder runs and writes its status file
# (no physics is read; at t = 0 nothing is trapped, so every search must end "not found").
#   smoke_g3a.sh OUTDIR DECK [DECK ...]     (DECK: name under tracks/C-sidm/longruns/inputs/)
set -euo pipefail
OUT=$1; shift
EXE=/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v08/athena_cpu_omp
export OMP_NUM_THREADS=4 OMP_PROC_BIND=false
for d in "$@"; do
  mkdir -p "$OUT/$d"
  ( cd "$OUT/$d" && "$EXE" -i /data/haiyangw/nrpic/wt/C-sidm/tracks/C-sidm/longruns/inputs/$d.athinput -d "$OUT/$d" time/nlim=3 time/ndiag=1 output2/dt=1e9 fastflow/find_every=1 > athena.log 2>&1; echo "$d rc=$?" )
  grep -E "Setup complete|cycle=|Terminating|particles|nbtotal|WARNING" "$OUT/$d/athena.log" | head -8
  ls "$OUT/$d" | grep -i horizon || echo "$d: no horizon file"
  head -5 "$OUT/$d"/*horizon_status* 2>/dev/null || true
done
