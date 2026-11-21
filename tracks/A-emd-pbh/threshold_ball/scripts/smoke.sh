#!/usr/bin/env bash
# Processor smoke test of the threshold_ball decks with the release core-v0.6 processor build:
# the A-mesh and B-mesh members of delta_c = 0.42 with every option of the queue, three cycles,
# finder searching from cycle 0 (so that <fastflow> diagnostics and hmean_tol_0 are exercised).
#   bash tracks/A-emd-pbh/threshold_ball/scripts/smoke.sh <out dir>
set -uo pipefail
OUT=$1; WT=/data/haiyangw/nrpic/wt/A-emd-pbh
EXE=/data/haiyangw/nrpic/.work/build_cpu_v06/src/athena
P=/data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261121-202812-cae4436/dc0p42
STEM=expball_tophat_HRb0p7_dc0p42_R10p65_R20p95_rm4p25
common=(problem/comp0_file=$P/$STEM.tab time/nlim=3 fastflow/hmean_tol_0=1e30 fastflow/diagnostics=true
        fastflow/find_every=1 fastflow/start_time_0=0.0 particles/field_time1=20.25 particles/field_time2=41.75
        particles/field_time3=43.75 particles/field_time4=47.75)
rc_all=0
for m in A:nest16_L32:nestA:1317 B:nest32_L32:nestB:1319; do
  IFS=: read -r name deck lat ntr <<< "$m"
  d=$OUT/$name; mkdir -p "$d"
  ( cd "$d" && "$EXE" -i "$WT/tracks/A-emd-pbh/threshold_ball/decks/$deck.athinput" -d "$d" "${common[@]}" \
      particles/particle_file=$P/$lat/${STEM}_${lat}_track.nrp particles/traj_ntrack=$ntr > athena.log 2>&1 )
  rc=$?; echo "$name rc=$rc"; [ $rc -ne 0 ] && rc_all=1
  grep -i -m3 "warn\|not used\|unknown\|error" "$d/athena.log"
  tail -6 "$d/athena.log"; ls "$d" | head -30
done
exit $rc_all
