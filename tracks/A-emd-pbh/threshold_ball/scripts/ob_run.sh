#!/usr/bin/env bash
# Entry 18 of threshold_ball (OB): S2c-A (as edge_cic.sh) on the deck nest16_L32 (outer faces at |x| = 32), live gauge, to t = 2
# v0.6 threaded build, two threads; levels inside |x| < 16 equal those of nest16_L16 (same table and lattice).
#   ob_run.sh <outdir>
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
mkdir -p "$OUT/S2c-AL32"
ATHENA_EXE=$EXE THREADS=2 "$ROOT/scripts/cpu_run.sh" "$OUT/S2c-AL32" "$DECKS/nest16_L32.athinput" \
  problem/comp0_file=$tab particles/particle_file=$nrp particles/traj_ntrack=$nt \
  particles/deposit_shape=cic particles/deposit_comp_c=0.0 particles/deposit_comp_c2=0.0 \
  time/tlim=2.0 output2/dt=4.0
rc=$?
tail -n 3 "$OUT/S2c-AL32/athena.log"
exit $rc
