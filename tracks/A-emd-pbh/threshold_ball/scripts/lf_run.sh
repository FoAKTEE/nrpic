#!/usr/bin/env bash
# Entry 18 of threshold_ball (LF): the smooth S2 ball with the matter inside ONE refinement level (U4) against its
# twin with a level face at |x| = 4 inside the matter (N4), both finest M/4, outer faces at 16, live gauge, CIC
# without compensation (as S2c-A), to t = 2. Data: prep_bh.py as edge_data.sh's S2 with the two custom lattices.
# v0.6 threaded build (as S2c-A), one thread per member, both members at once.
#   lf_run.sh <outdir>
set -uo pipefail
OUT=$1
EXE=/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v06/athena_cpu_omp
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../../.." && pwd)
P=$HERE/../../conv_ball/scripts/prep_bh.py
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
python "$P" --out "$OUT/S2" --profile smooth_tophat --R1 0.30 --R2 0.80 --edge-w 0.8 --nlat \
  --custom uni4:1:16x1,8x0.25 nest4:1:16x1,8x0.5,4x0.25 > "$OUT/S2.log" 2>&1 || { tail -n 20 "$OUT/S2.log"; exit 1; }
tail -n 4 "$OUT/S2.log"
tab=$(ls "$OUT/S2"/*.tab | head -n 1)
pids=()
for m in U4:uni4:uni4_L16 N4:nest4:nest4_L16; do
  IFS=: read -r name lat deck <<< "$m"
  nrp=$(ls "$OUT/S2/$lat"/*_track.nrp | head -n 1)
  nt=$(python -c "import json,sys; print(json.load(open(sys.argv[1]))['n_track'])" "$OUT/S2/$lat/tracked.json")
  mkdir -p "$OUT/$name"
  ATHENA_EXE=$EXE THREADS=1 "$ROOT/scripts/cpu_run.sh" "$OUT/$name" "$HERE/../decks/$deck.athinput" \
    problem/comp0_file=$tab particles/particle_file=$nrp particles/traj_ntrack=$nt \
    particles/deposit_shape=cic particles/deposit_comp_c=0.0 particles/deposit_comp_c2=0.0 \
    time/tlim=2.0 output2/dt=4.0 > "$OUT/$name.out" 2>&1 &
  pids+=($!)
done
rc=0
for p in "${pids[@]}"; do wait "$p" || rc=$?; done
for name in U4 N4; do echo "== $name"; tail -n 3 "$OUT/$name/athena.log"; done
exit $rc
