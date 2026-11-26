#!/usr/bin/env bash
# Processor smoke test of the half-amplitude member S1L-h (prediction SM-h, periodic_threshold
# JOURNAL 2026-11-25 19:25 PST): inputs/peak_leak.athinput with the mu = 0.15 data and the card
# overrides of the queue entry, a few cycles with the release core-v0.7 processor executable, the
# finder switched on from t = 0 every 2 cycles so that one search with diagnostics = true runs.
#   smoke_half.sh <data dir with fields.bin, particles.nrp> <outdir> [nlim]
set -euo pipefail
DATA=$1; OUT=$2; NLIM=${3:-4}
EXE=/data/haiyangw/nrpic/.work/build_cpu_v07/src/athena
DECK=/data/haiyangw/nrpic/wt/A-emd-pbh/tracks/A-emd-pbh/periodic_threshold/inputs/peak_leak.athinput
export OMP_NUM_THREADS=1
mkdir -p "$OUT/S1Lh"
rc=0
"$EXE" -i "$DECK" -d "$OUT/S1Lh" problem/id_file=$DATA/fields.bin \
    particles/particle_file=$DATA/particles.nrp time/tlim=220.0 particles/snap_dt=5.0 output7/dt=30.0 \
    time/nlim=$NLIM fastflow/start_time_0=0.0 fastflow/find_every=2 > "$OUT/S1Lh/athena.log" 2>&1 || rc=$?
echo "S1Lh exit $rc"
grep -i -E "cycle=|dt=|guard|horizon|error|warn|Terminat|gauge|particles from" "$OUT/S1Lh/athena.log" | tail -n 20
ls "$OUT/S1Lh" | head -40
exit $rc
