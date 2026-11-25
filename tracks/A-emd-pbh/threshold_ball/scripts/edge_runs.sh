#!/usr/bin/env bash
# Entry 13 of threshold_ball (C3S): the smoothed members S1, S2 (data run A-20261125-160436-462452d) on meshes A
# (nest16_L16) and B (nest32_L16) with the executable of K4 (core-v0.6 threaded processor build), so that K4-ref
# (A-20261125-120525-8fb946e) is the top-hat twin on mesh A.
#   phase 1: the t = 0 slices of S1 and S2 on A and B (nlim = 0), one thread each, in parallel;
#   phase 2: S2 on A to t = 5 (2 threads), S2 on B to t = 1 (2 threads), S1 on A to t = 5 (1 thread), in parallel.
#   edge_runs.sh <outdir>
set -uo pipefail
OUT=$1
D=/data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261125-160436-462452d
EXE=/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v06/athena_cpu_omp
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../../.." && pwd)
DECKS=$HERE/../../conv_ball/decks
args() {  # member lattice -> common arguments
  local mem=$1 lat=$2 tab nrp nt
  tab=$(ls "$D/$mem"/*.tab | head -n 1)
  nrp=$(ls "$D/$mem/$lat"/*_track.nrp | head -n 1)
  nt=$(python -c "import json,sys; print(json.load(open(sys.argv[1]))['n_track'])" "$D/$mem/$lat/tracked.json")
  echo "problem/comp0_file=$tab particles/particle_file=$nrp particles/traj_ntrack=$nt"
}
launch() {  # name deck threads member lattice extra...
  local name=$1 deck=$2 thr=$3 mem=$4 lat=$5; shift 5
  mkdir -p "$OUT/$name"
  # shellcheck disable=SC2046
  ATHENA_EXE=$EXE THREADS=$thr "$ROOT/scripts/cpu_run.sh" "$OUT/$name" "$DECKS/$deck" $(args "$mem" "$lat") "$@" > "$OUT/$name.out" 2>&1 &
  pids+=($!)
}
rc=0
pids=()
launch S1-A0 nest16_L16.athinput 1 S1 nestA time/nlim=0
launch S2-A0 nest16_L16.athinput 1 S2 nestA time/nlim=0
launch S1-B0 nest32_L16.athinput 1 S1 nestB time/nlim=0
launch S2-B0 nest32_L16.athinput 1 S2 nestB time/nlim=0
for p in "${pids[@]}"; do wait "$p" || rc=$?; done
echo "phase 1 done rc=$rc $(date)"
pids=()
launch S2-A nest16_L16.athinput 2 S2 nestA time/tlim=5.0 output2/dt=1.0
launch S2-B nest32_L16.athinput 2 S2 nestB time/tlim=1.0 output2/dt=0.25
launch S1-A nest16_L16.athinput 1 S1 nestA time/tlim=5.0 output2/dt=1.0
for p in "${pids[@]}"; do wait "$p" || rc=$?; done
for n in S1-A0 S2-A0 S1-B0 S2-B0 S2-A S2-B S1-A; do echo "== $n"; tail -n 3 "$OUT/$n/athena.log"; done
exit $rc
