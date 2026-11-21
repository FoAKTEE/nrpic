#!/usr/bin/env bash
# Processor smoke test of inputs/peak_leak.athinput for P0L and S1L: a few cycles each with
# the release core-v0.5 processor executable, the finder switched on from t = 0 so that
# one search in the periodic box runs, both runs side by side on one core each.
#   smoke_leak.sh <outdir> [nlim]
set -euo pipefail
OUT=$1; NLIM=${2:-4}
EXE=/data/haiyangw/nrpic/.work/build_cpu_v05/src/athena
DECK=/data/haiyangw/nrpic/wt/A-emd-pbh/tracks/A-emd-pbh/periodic_threshold/inputs/peak_leak.athinput
P0=/data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261120-223123-f436c39/P0_mu0.3
S1=/data/haiyangw/nrpic/scratch/A-emd-pbh/A-emd-pbh-20261115-155802-9a6596f/S_mu0.3
export OMP_NUM_THREADS=1
common=(time/nlim=$NLIM fastflow/start_time_0=0.0 fastflow/find_every=2)
mkdir -p "$OUT/P0L" "$OUT/S1L"
"$EXE" -i "$DECK" -d "$OUT/P0L" problem/id_file=$P0/fields.bin \
    particles/particle_file=$P0/particles_track.nrp particles/traj_ntrack=317 \
    particles/traj_dcycle=1 "${common[@]}" > "$OUT/P0L/athena.log" 2>&1 &
p1=$!
"$EXE" -i "$DECK" -d "$OUT/S1L" problem/id_file=$S1/fields.bin \
    particles/particle_file=$S1/particles.nrp "${common[@]}" > "$OUT/S1L/athena.log" 2>&1 &
p2=$!
rc=0
wait $p1 || rc=$?
echo "P0L exit $rc"
rc2=0
wait $p2 || rc2=$?
echo "S1L exit $rc2"
for r in P0L S1L; do
  echo "== $r"; grep -i -E "cycle=|dt=|guard|horizon|error|warn|Terminat" "$OUT/$r/athena.log" | tail -n 14
done
exit $(( rc + rc2 ))
