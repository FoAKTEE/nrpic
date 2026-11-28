#!/usr/bin/env bash
# RX (periodic_threshold JOURNAL 2026-11-27 23:47 PST): is a run of the box deck continued from a restart file exact?
# Deck peak_leak.athinput with S1L's data (S_mu0.3), processor builds of core-v0.6 and core-v0.8, one core each:
#   A: 8 cycles straight, restart files written every 0.012 in t (first after cycle 4);
#   B: continued with -r from A's restart file of cycle 4 to cycle 8 (batch 40: shortened from 24 cycles, ~60 s per cycle on one core).
# Then rx_compare.py compares the history rows of the cycles after the restart.
#   rx_run.sh <outdir>
set -uo pipefail
OUT=$1
DATA=/data/haiyangw/nrpic/scratch/A-emd-pbh/A-emd-pbh-20261115-155802-9a6596f/S_mu0.3
HERE=$(cd "$(dirname "$0")" && pwd)
DECK=$HERE/../inputs/peak_leak.athinput
export OMP_NUM_THREADS=1
rc=0
for v in 06 08; do
  EXE=/data/haiyangw/nrpic/.work/build_cpu_v$v/src/athena
  A=$OUT/v$v/A; B=$OUT/v$v/B
  mkdir -p "$A" "$B"
  "$EXE" -i "$DECK" -d "$A" problem/id_file=$DATA/fields.bin particles/particle_file=$DATA/particles.nrp \
      time/nlim=8 output7/dt=0.012 > "$A/athena.log" 2>&1 || rc=$?
  ls "$A/rst"
  n=$(ls "$A"/rst/*.rst | wc -l)                   # with a file at t = 0 there are three, else two
  if [ "$n" -ge 3 ]; then R=$(ls "$A"/rst/*.rst | sort | sed -n 2p); else R=$(ls "$A"/rst/*.rst | sort | sed -n 1p); fi
  echo "v$v continue from $R"
  "$EXE" -r "$R" -d "$B" time/nlim=8 > "$B/athena.log" 2>&1 || rc=$?
  grep -E "cycle=" "$A/athena.log" | tail -n 1; grep -E "cycle=" "$B/athena.log" | tail -n 1
done
exit $rc
