#!/usr/bin/env bash
# Entry 10 of threshold_ball (K4): conv_ball member A on processors to t = 5 (K4 judges t = 2-5), three variants in
# parallel with 2 threads each (6 cores).   k4_floor.sh <outdir>
set -uo pipefail
OUT=$1
EXE=/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v06/athena_cpu_omp
DECK=/data/haiyangw/nrpic/wt/A-emd-pbh/tracks/A-emd-pbh/conv_ball/decks/nest16_L16.athinput
D=/data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261121-075356-1ad4c81
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../../.." && pwd)
COMMON=(problem/comp0_file=$D/expball_tophat_HRb0p7_dc1p5_R10p65_R20p95_rm4p25.tab
        particles/particle_file=$D/nestA/expball_tophat_HRb0p7_dc1p5_R10p65_R20p95_rm4p25_nestA_track.nrp
        particles/traj_ntrack=1313 time/tlim=5.0)
pids=()
for spec in "K4-ref:" "K4-dt:time/cfl_number=0.125" "K4-src:particles/source_extrap=false"; do
  NAME=${spec%%:*}; EXTRA=${spec#*:}
  mkdir -p "$OUT/$NAME"
  # shellcheck disable=SC2086
  ATHENA_EXE=$EXE THREADS=2 "$ROOT/scripts/cpu_run.sh" "$OUT/$NAME" "$DECK" "${COMMON[@]}" $EXTRA > "$OUT/$NAME.out" 2>&1 &
  pids+=($!)
done
rc=0
for p in "${pids[@]}"; do wait "$p" || rc=$?; done
for n in K4-ref K4-dt K4-src; do echo "== $n"; tail -3 "$OUT/$n/athena.log"; done
exit $rc
