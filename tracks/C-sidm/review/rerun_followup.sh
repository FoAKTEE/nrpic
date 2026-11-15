#!/bin/bash
# Follow-up of the lead's rerun C-sidm-20261115-131135-3077a99 (prediction L1 failed for two
# items). (a) polytrope check of gravothermal with one thread, as the original run;
# (b) T6-0 with the collide code of the original commit 313d399 (make_box.py changed in
# abd9c2e). Compares with the original outputs. Run through review/register.py.
set -uo pipefail
OUT=${NRPIC_RUN_DIR:?run through review/register.py}
WT=$(pwd)
S=/data/haiyangw/nrpic/scratch/C-sidm
status=0
echo "== (a) polytrope check, 1 thread"
mkdir -p "$OUT/polytrope_1thread"
(cd "$WT/tracks/C-sidm/gravothermal" && OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  python3 -E pulsation_check.py "$OUT/polytrope_1thread") > "$OUT/polytrope_1thread/log.txt" 2>&1 || status=1
cmp "$OUT/polytrope_1thread/polytrope_check.json" "$S/C-sidm-20261115-121524-5cebcf5/polytrope_check.json" \
  && echo "polytrope_check.json identical to run C-sidm-20261115-121524-5cebcf5" || { echo "polytrope_check.json DIFFERS"; status=1; }
echo "== (b) T6-0 with the code of commit 313d399"
mkdir -p "$OUT/src313" "$OUT/t6_313"
git -C "$WT" archive 313d3996e4176108b49468a9083d754737868509 python tracks/C-sidm/collide | tar -x -C "$OUT/src313"
NRPIC_RUN_DIR="$OUT/t6_313" OMP_NUM_THREADS=4 bash "$OUT/src313/tracks/C-sidm/collide/analysis/run_step_collisionless.sh" 100000 \
  > "$OUT/t6_313/stdout.log" 2>&1 || status=1
O=$S/C-sidm-20261115-121302-313d399
n=0; same=0
for f in "$O"/step.nrp "$O"/step.part.*.bin "$O"/step.nrpic.hst; do
  b=$(basename "$f"); n=$((n+1))
  cmp -s "$f" "$OUT/t6_313/$b" && same=$((same+1)) || echo "differs: $b"
done
echo "T6-0 files bit-identical to run C-sidm-20261115-121302-313d399: $same/$n"
[ "$same" -eq "$n" ] || status=1
echo "== done, status $status"
exit $status
