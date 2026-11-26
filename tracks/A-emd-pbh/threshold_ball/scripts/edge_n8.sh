#!/usr/bin/env bash
# Entry 15 (prediction H): particle-number leg of the smooth CIC member. Data S2 (as edge_data.sh) on the nested
# lattice nestA8 (SUB = 2, eight particles per cell), then S2c-A8 = S2c-A of edge_cic.sh with that lattice:
# t = 0 slice (one thread), then mesh A to t = 2 (two threads).
#   edge_n8.sh <outdir>
set -uo pipefail
OUT=$1
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../../.." && pwd)
P=$HERE/../../conv_ball/scripts/prep_bh.py
DECKS=$HERE/../../conv_ball/decks
EXE=/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v06/athena_cpu_omp
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
python "$P" --out "$OUT/S2" --profile smooth_tophat --R1 0.30 --R2 0.80 --edge-w 0.8 --nlat --nested nestA8:16:16:2 > "$OUT/S2.log" 2>&1 || { echo "data failed"; tail -n 20 "$OUT/S2.log"; exit 1; }
D=$OUT
CIC=(particles/deposit_shape=cic particles/deposit_comp_c=0.0 particles/deposit_comp_c2=0.0)
tab=$(ls "$D/S2"/*.tab | head -n 1)
nrp=$(ls "$D/S2/nestA8"/*_track.nrp | head -n 1)
nt=$(python -c "import json,sys; print(json.load(open(sys.argv[1]))['n_track'])" "$D/S2/nestA8/tracked.json")
A=(problem/comp0_file=$tab particles/particle_file=$nrp particles/traj_ntrack=$nt)
rc=0
mkdir -p "$OUT/S2c-A80" "$OUT/S2c-A8"
ATHENA_EXE=$EXE THREADS=1 "$ROOT/scripts/cpu_run.sh" "$OUT/S2c-A80" "$DECKS/nest16_L16.athinput" "${A[@]}" "${CIC[@]}" time/nlim=0 > "$OUT/S2c-A80.out" 2>&1 || rc=$?
ATHENA_EXE=$EXE THREADS=2 "$ROOT/scripts/cpu_run.sh" "$OUT/S2c-A8" "$DECKS/nest16_L16.athinput" "${A[@]}" "${CIC[@]}" time/tlim=2.0 output2/dt=1.0 > "$OUT/S2c-A8.out" 2>&1 || rc=$?
for n in S2c-A80 S2c-A8; do echo "== $n"; tail -n 3 "$OUT/$n/athena.log"; done
exit $rc
