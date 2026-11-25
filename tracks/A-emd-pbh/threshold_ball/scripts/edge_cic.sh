#!/usr/bin/env bash
# Entry 13, test F: S2 with the CIC cloud and no compensation on meshes A and B (v0.6 threaded build as K4):
# t = 0 slices (one thread each), then A to t = 5 (one thread) and B to t = 1 (two threads), in parallel.
#   edge_cic.sh <outdir>
set -uo pipefail
OUT=$1
D=/data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261125-160436-462452d
EXE=/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v06/athena_cpu_omp
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../../.." && pwd)
DECKS=$HERE/../../conv_ball/decks
CIC=(particles/deposit_shape=cic particles/deposit_comp_c=0.0 particles/deposit_comp_c2=0.0)
args() {
  local lat=$1 tab nrp nt
  tab=$(ls "$D/S2"/*.tab | head -n 1)
  nrp=$(ls "$D/S2/$lat"/*_track.nrp | head -n 1)
  nt=$(python -c "import json,sys; print(json.load(open(sys.argv[1]))['n_track'])" "$D/S2/$lat/tracked.json")
  echo "problem/comp0_file=$tab particles/particle_file=$nrp particles/traj_ntrack=$nt"
}
launch() {  # name deck threads lattice extra...
  local name=$1 deck=$2 thr=$3 lat=$4; shift 4
  mkdir -p "$OUT/$name"
  # shellcheck disable=SC2046
  ATHENA_EXE=$EXE THREADS=$thr "$ROOT/scripts/cpu_run.sh" "$OUT/$name" "$DECKS/$deck" $(args "$lat") "${CIC[@]}" "$@" > "$OUT/$name.out" 2>&1 &
  pids+=($!)
}
rc=0
pids=()
launch S2c-A0 nest16_L16.athinput 1 nestA time/nlim=0
launch S2c-B0 nest32_L16.athinput 1 nestB time/nlim=0
for p in "${pids[@]}"; do wait "$p" || rc=$?; done
pids=()
launch S2c-A nest16_L16.athinput 1 nestA time/tlim=5.0 output2/dt=1.0
launch S2c-B nest32_L16.athinput 2 nestB time/tlim=1.0 output2/dt=0.25
for p in "${pids[@]}"; do wait "$p" || rc=$?; done
for n in S2c-A0 S2c-B0 S2c-A S2c-B; do echo "== $n"; tail -n 3 "$OUT/$n/athena.log"; done
exit $rc
