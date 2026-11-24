#!/usr/bin/env bash
# D0 of periodic_threshold (JOURNAL 2026-11-24 13:40Z): processor smoke test of
# inputs/peak_leak6.athinput (six static levels) for P0L, a few cycles, finder from t = 0.
#   smoke_leak6.sh <outdir> [nlim]
set -euo pipefail
OUT=$1; NLIM=${2:-4}
EXE=/data/haiyangw/nrpic/.work/build_cpu_v06/src/athena
DECK=/data/haiyangw/nrpic/wt/A-emd-pbh/tracks/A-emd-pbh/periodic_threshold/inputs/peak_leak6.athinput
P0=/data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261120-223123-f436c39/P0_mu0.3
export OMP_NUM_THREADS=1
mkdir -p "$OUT/P0L6"
rc=0
"$EXE" -i "$DECK" -d "$OUT/P0L6" problem/id_file=$P0/fields.bin \
    particles/particle_file=$P0/particles_track.nrp particles/traj_ntrack=317 \
    time/nlim=$NLIM fastflow/start_time_0=0.0 fastflow/find_every=2 > "$OUT/P0L6/athena.log" 2>&1 || rc=$?
echo "P0L6 exit $rc"
grep -i -E "cycle=|guard|Terminat|MeshBlocks|error" "$OUT/P0L6/athena.log" | tail -n 14
grep -c . "$OUT/P0L6/peak.horizon_status_0.txt" || true
exit $rc
