#!/usr/bin/env bash
# Entry 18 of threshold_ball (FR): S2c-A (as edge_cic.sh) on nest16_L16 (faces at 16) with the outer-face set of core-v0.6 (z4c_faces.md section 4), live gauge, to t = 2
# v0.6 threaded build, four threads: extrap_order 4, ghost_falloff, sbc_variant nonwave, sbc_speed metric.
#   fr_run.sh <outdir>
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
mkdir -p "$OUT/S2c-AFR"
ATHENA_EXE=$EXE THREADS=4 "$ROOT/scripts/cpu_run.sh" "$OUT/S2c-AFR" "$HERE/../decks/nest16_L16_fr.athinput" \
  problem/comp0_file=$tab particles/particle_file=$nrp particles/traj_ntrack=$nt \
  particles/deposit_shape=cic particles/deposit_comp_c=0.0 particles/deposit_comp_c2=0.0 \
  time/tlim=2.0 output2/dt=4.0
rc=$?
tail -n 3 "$OUT/S2c-AFR/athena.log"
exit $rc
