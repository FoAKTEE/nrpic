#!/usr/bin/env bash
# Entry 13 of threshold_ball (C3S, the smoothed-edge test): data of members W (data set 3's top hat with the outer
# taper widened to half width 0.918 M, rm = 5.0, i.e. prep_bh.py --edge-w 0.9184) and S (smooth_tophat, R1 = 0.40 R_b,
# R2 = 0.95 R_b, same outer taper) on the nested lattices of meshes A (nest16_L16) and B (nest32_L16).
#   edge_data.sh <outdir>
set -euo pipefail
OUT=$1
HERE=$(cd "$(dirname "$0")" && pwd)
P=$HERE/../../conv_ball/scripts/prep_bh.py
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
python "$P" --out "$OUT/W" --rm 5.0 --nlat --nested nestA:16:16:1 nestB:32:16:1 > "$OUT/W.log" 2>&1 &
p1=$!
python "$P" --out "$OUT/S" --profile smooth_tophat --R1 0.40 --R2 0.95 --rm 5.0 --nlat --nested nestA:16:16:1 nestB:32:16:1 > "$OUT/S.log" 2>&1 &
p2=$!
rc=0
wait $p1 || rc=$?
wait $p2 || rc=$?
tail -4 "$OUT/W.log" "$OUT/S.log"
exit $rc
