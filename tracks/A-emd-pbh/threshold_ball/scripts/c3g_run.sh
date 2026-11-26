#!/usr/bin/env bash
# Entry 17 of threshold_ball (C3-G): S2c-A (as edge_cic.sh, c3f_run.sh) to t = 1 with the gauge frozen
# (static lapse at its table value, zero shift). v0.6 threaded build, four threads.
#   c3g_run.sh <outdir>
set -uo pipefail
OUT=$1
D=/data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261125-160436-462452d
EXE=/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v06/athena_cpu_omp
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../../.." && pwd)
DECKS=$HERE/../../conv_ball/decks
tab=$(ls "$D/S2"/*.tab | head -n 1)
nrp=$(ls "$D/S2/nestA"/*_track.nrp | head -n 1)
nt=$(python -c "import json,sys; print(json.load(open(sys.argv[1]))['n_track'])" "$D/S2/nestA/tracked.json")
mkdir -p "$OUT/S2c-Afrozen"
ATHENA_EXE=$EXE THREADS=4 "$ROOT/scripts/cpu_run.sh" "$OUT/S2c-Afrozen" "$DECKS/nest16_L16.athinput" \
  problem/comp0_file=$tab particles/particle_file=$nrp particles/traj_ntrack=$nt \
  particles/deposit_shape=cic particles/deposit_comp_c=0.0 particles/deposit_comp_c2=0.0 \
  z4c/lapse_oplog=0.0 z4c/lapse_advect=0.0 z4c/lapse_leak=0.0 \
  z4c/shift_Gamma=0.0 z4c/shift_eta=0.0 z4c/shift_advect=0.0 \
  time/tlim=1.0 output2/dt=4.0
rc=$?
tail -n 3 "$OUT/S2c-Afrozen/athena.log"
exit $rc
