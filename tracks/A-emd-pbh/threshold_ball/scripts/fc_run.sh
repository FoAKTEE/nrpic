#!/usr/bin/env bash
# Entry 19 of threshold_ball (FC, batch 40): does the outer-face part of the section-3 line ratio converge with the
# mesh when core-v0.6's outer-face set is on? A pair whose EVERY cell is halved, with the inner levels kept coarse
# (the band 13-16 cannot see the matter, r < 4.9, before t ~ 5.7 even at the 1+log gauge speed sqrt(2)):
#   N4F  = nest4_L16 (N4 of entry 18, root dx 1) + face set,   lattice nest4 of LF's data (same table and particles)
#   N8   = nest8h_L16 (all cells halved, root dx 0.5), stock,  lattice nest8h (one particle per local cell)
#   N8F  = nest8h_L16 + face set,                              lattice nest8h
# The stock partner of N8 at root dx 1 is LF's N4 (A-20261128-005331-874ec88/N4). v0.6 threaded build (as LF, FR),
# CIC without compensation, live gauge, to t = 1; threads 1 + 2 + 3 = 6.
#   fc_run.sh <outdir>
set -uo pipefail
OUT=$1
EXE=/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v06/athena_cpu_omp
LF=/data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261128-005331-874ec88/S2
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../../.." && pwd)
P=$HERE/../../conv_ball/scripts/prep_bh.py
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
python "$P" --out "$OUT/S2" --profile smooth_tophat --R1 0.30 --R2 0.80 --edge-w 0.8 --nlat \
  --custom nest8h:1:16x0.5,8x0.25,4x0.125 > "$OUT/S2.log" 2>&1 || { tail -n 20 "$OUT/S2.log"; exit 1; }
tail -n 4 "$OUT/S2.log"
tab_lf=$(ls "$LF"/*.tab | head -n 1)
tab=$(ls "$OUT/S2"/*.tab | head -n 1)
echo "table of LF: $(sha256sum "$tab_lf" | cut -c1-16)  table here: $(sha256sum "$tab" | cut -c1-16)"
pids=()
for m in N4F:nest4:nest4_L16_fr:1:$LF:$tab_lf N8:nest8h:nest8h_L16:2:$OUT/S2:$tab N8F:nest8h:nest8h_L16_fr:3:$OUT/S2:$tab; do
  IFS=: read -r name lat deck nth dd tb <<< "$m"
  nrp=$(ls "$dd/$lat"/*_track.nrp | head -n 1)
  nt=$(python -c "import json,sys; print(json.load(open(sys.argv[1]))['n_track'])" "$dd/$lat/tracked.json")
  mkdir -p "$OUT/$name"
  ATHENA_EXE=$EXE THREADS=$nth "$ROOT/scripts/cpu_run.sh" "$OUT/$name" "$HERE/../decks/$deck.athinput" \
    problem/comp0_file=$tb particles/particle_file=$nrp particles/traj_ntrack=$nt \
    particles/deposit_shape=cic particles/deposit_comp_c=0.0 particles/deposit_comp_c2=0.0 \
    time/tlim=1.0 output2/dt=4.0 > "$OUT/$name.out" 2>&1 &
  pids+=($!)
done
rc=0
for p in "${pids[@]}"; do wait "$p" || rc=$?; done
for name in N4F N8 N8F; do echo "== $name"; tail -n 3 "$OUT/$name/athena.log"; done
exit $rc
