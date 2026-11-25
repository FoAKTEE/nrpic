#!/usr/bin/env bash
# Entry 13 of threshold_ball (C3S, the smoothed-edge test; amended 08:12 PST): data of members S1 (smooth_tophat,
# R1 = 0.40 R_b, R2 = 0.95 R_b, outer edge of data set 3: rm = 4.25) and S2 (smooth_tophat, R1 = 0.30 R_b,
# R2 = 0.80 R_b, outer taper half width 0.8 M: --edge-w 0.8) on the nested lattices of meshes A (nest16_L16) and
# B (nest32_L16). Member W (data set 3 with --edge-w 0.918) is not admissible (R2 <= R_b - w; run A-20261125-160221-b68396f).
#   edge_data.sh <outdir>
set -euo pipefail
OUT=$1
HERE=$(cd "$(dirname "$0")" && pwd)
P=$HERE/../../conv_ball/scripts/prep_bh.py
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
python "$P" --out "$OUT/S1" --profile smooth_tophat --R1 0.40 --R2 0.95 --rm 4.25 --nlat --nested nestA:16:16:1 nestB:32:16:1 > "$OUT/S1.log" 2>&1 &
p1=$!
python "$P" --out "$OUT/S2" --profile smooth_tophat --R1 0.30 --R2 0.80 --edge-w 0.8 --nlat --nested nestA:16:16:1 nestB:32:16:1 > "$OUT/S2.log" 2>&1 &
p2=$!
rc=0
wait $p1 || rc=$?
wait $p2 || rc=$?
for f in "$OUT/S1.log" "$OUT/S2.log"; do echo "== $f"; tail -n 4 "$f"; done
exit $rc
