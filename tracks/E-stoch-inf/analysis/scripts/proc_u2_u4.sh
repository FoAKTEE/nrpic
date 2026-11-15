#!/bin/bash
# Processor runs of the base case of the noise unit test (NOISE_SPEC section 9) that the
# card job cannot give: U2 (8 MeshBlocks of 32^3, N = 64, 300 steps) as the processor
# reference of U9 (test A14), then U4 = U2 restarted from its restart file at cycle 150
# (test A12 on processors). Serial build: about 100 min for U2 and 50 min for U4.
#   proc_u2_u4.sh EXE INPUTDIR OUTDIR
set -u
EXE=$1; IN=$2; OUT=$3
export OMP_NUM_THREADS=1 OMP_PROC_BIND=false
mkdir -p "$OUT/U2" "$OUT/U4"
cp "$IN/U2.athinput" "$OUT/U2/u.athinput"
t0=$(date +%s)
( cd "$OUT/U2" && "$EXE" -i u.athinput > athena.log 2>&1 ); rc2=$?
t1=$(date +%s)
echo "U2 rc=$rc2 wall=$((t1 - t0)) s" | tee -a "$OUT/proc_status.txt"
rst=$OUT/U2/rst/u.00001.rst
if [[ $rc2 -ne 0 || ! -f $rst ]]; then
  echo "U4 not run (U2 rc=$rc2, restart file $rst present: $([[ -f $rst ]] && echo yes || echo no))" \
    | tee -a "$OUT/proc_status.txt"
  exit 1
fi
cp "$OUT/U2/u.athinput" "$OUT/U4/u.athinput"
( cd "$OUT/U4" && "$EXE" -r "$rst" > athena.log 2>&1 ); rc4=$?
t2=$(date +%s)
echo "U4 rc=$rc4 wall=$((t2 - t1)) s" | tee -a "$OUT/proc_status.txt"
exit $((rc2 + rc4))
