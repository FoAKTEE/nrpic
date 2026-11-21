#!/usr/bin/env bash
# Test of hypothesis H1 of journal entry 18 (prediction P15): the Jeans deck with the
# diagnostic executable of mg_diag_build.sh, MG_AVERAGE unset / ordered / comp, at 1, 2,
# 4 and 6 threads, MeshBlocks of 8^3 and 32^3, one cycle with the defect after every V
# cycle; then the 20-cycle Jeans case of the regression at 1 and 4 threads (mesh outputs
# compared by mg_cause.py). One run at a time, at most six threads.
#   mg_cause.sh <diagnostic exe> <threaded exe O3>    (run inside the output directory)
# THREADS: thread counts of the probe (default "1 2 4 6"); the 20-cycle case runs at the
# first and at the last but one of them, or at the two if only two are given.
set -uo pipefail
WT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
X=$1; O=$2
deck=$WT/athenak/inputs/tests/jeans_wave.athinput
read -r -a TH <<< "${THREADS:-1 2 4 6}"
T20=("${TH[0]}" "${TH[$(( ${#TH[@]} > 2 ? ${#TH[@]} - 2 : ${#TH[@]} - 1 ))]}")
one() {  # dir exe mode threads [args]
  local d=$1 e=$2 mode=$3 n=$4; shift 4
  mkdir -p "$d"
  ( cd "$d"
    if [[ $mode == plain ]]; then unset MG_AVERAGE; else export MG_AVERAGE=$mode; fi
    OMP_NUM_THREADS=$n OMP_PROC_BIND=false "$e" -i "$deck" gravity/show_defect=2 "$@" \
        > run.log 2>&1 )
  echo "== $d: exit $? $(grep -c 'MG iteration' "$d/run.log") V cycles; defects:" \
       $(grep 'MG iteration' "$d/run.log" | awk '{print $NF}' | head -10)
}
for mb in mb8 mb32; do
  extra=(time/nlim=1)
  [[ $mb == mb32 ]] && extra+=(meshblock/nx1=32 meshblock/nx2=32 meshblock/nx3=32)
  for n in "${TH[@]}"; do
    [[ $n -le 4 ]] && one "probe/$mb/O3_t$n" "$O" plain "$n" "${extra[@]}"
  done
  for mode in plain ordered comp; do
    for n in "${TH[@]}"; do one "probe/$mb/${mode}_t$n" "$X" "$mode" "$n" "${extra[@]}"; done
  done
done
for mode in plain ordered comp; do
  for n in "${T20[@]}"; do one "jeans20/${mode}_t$n" "$X" "$mode" "$n" time/nlim=20; done
done
