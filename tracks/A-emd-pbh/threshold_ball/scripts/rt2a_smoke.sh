#!/usr/bin/env bash
# Entry 20 of threshold_ball (RT2a): processor smoke test of the two card decks before they are queued.
# core-v0.9 serial processor build, the bracket member d0.42 on mesh A (nest16_L32_fr) and mesh B (nest32_L32_fr) with
# the overrides of the card entries, 3 cycles each, one core each, both at once.
# Checks: the face set and the region keys parse on a fresh start, the 'deposit' and the first steps are finite, the
# region file is written.
#   rt2a_smoke.sh <outdir>
set -uo pipefail
OUT=$1
EXE=/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v09/athena_cpu
D=/data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261121-202812-cae4436/dc0p42
TAB=$D/expball_tophat_HRb0p7_dc0p42_R10p65_R20p95_rm4p25.tab
HERE=$(cd "$(dirname "$0")" && pwd)
export OMP_NUM_THREADS=1
pids=()
for m in A:nest16_L32_fr:nestA:1317 B:nest32_L32_fr:nestB:1319; do
  IFS=: read -r name deck lat nt <<< "$m"
  mkdir -p "$OUT/$name"
  "$EXE" -i "$HERE/../decks/$deck.athinput" -d "$OUT/$name" problem/comp0_file=$TAB \
    particles/particle_file=$D/$lat/expball_tophat_HRb0p7_dc0p42_R10p65_R20p95_rm4p25_${lat}_track.nrp \
    particles/traj_ntrack=$nt time/tlim=51.0 time/nlim=3 fastflow/hmean_tol_0=1e30 fastflow/diagnostics=true \
    fastflow/find_every=8 fastflow/start_time_0=21.75 > "$OUT/$name/athena.log" 2>&1 &
  pids+=($!)
done
rc=0
for p in "${pids[@]}"; do wait "$p" || rc=$?; done
for name in A B; do
  echo "== $name"; grep -i -E "cycle=|warn|error|not found|guard|Terminat|unused" "$OUT/$name/athena.log" | tail -n 8
  ls "$OUT/$name" | tr '\n' ' '; echo
done
exit $rc
