#!/usr/bin/env bash
# Entry 16 of threshold_ball (C3-F): S2c-A exactly as edge_cic.sh ran it (v0.6 threaded build, one thread, deck
# nest16_L16, CIC without compensation, S2 data of A-20261125-160436-462452d, lattice nestA) to t = 0.25, with the
# history and the x-line tables every cycle (dt = 0.015625, the step of this deck).
#   c3f_run.sh <outdir>
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
mkdir -p "$OUT/S2c-Aevery"
DT=0.015625
ATHENA_EXE=$EXE THREADS=1 "$ROOT/scripts/cpu_run.sh" "$OUT/S2c-Aevery" "$DECKS/nest16_L16.athinput" \
  problem/comp0_file=$tab particles/particle_file=$nrp particles/traj_ntrack=$nt \
  particles/deposit_shape=cic particles/deposit_comp_c=0.0 particles/deposit_comp_c2=0.0 \
  time/tlim=0.25 output2/dt=1.0 output1/dt=$DT output3/dt=$DT output4/dt=$DT output5/dt=$DT output6/dt=$DT
rc=$?
tail -n 3 "$OUT/S2c-Aevery/athena.log"
exit $rc
