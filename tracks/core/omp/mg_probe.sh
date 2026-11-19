#!/usr/bin/env bash
# Probe of the gas multigrid solver under threads: the Jeans-wave deck (uniform periodic
# mesh, self-gravity) for one cycle with the serial build S and the threaded build O3 at
# 1, 2, 4 and 8 threads (two runs at 4), with the defect after every V cycle printed;
# then the same with the multigrid on a single MeshBlock (meshblock = mesh).
#   mg_probe.sh <O3 exe> <S exe>       (run inside the output directory)
set -uo pipefail
WT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
O=$1; S=$2
deck=$WT/athenak/inputs/tests/jeans_wave.athinput
one() {  # dir exe threads [args]
  local d=$1 e=$2 n=$3; shift 3
  mkdir -p "$d"
  (cd "$d" && OMP_NUM_THREADS=$n OMP_PROC_BIND=false "$e" -i "$deck" time/nlim=1 \
       gravity/show_defect=2 "$@" > run.log 2>&1)
  echo "== $d: $(grep -c 'MG iteration' "$d/run.log") V cycles; defects:" \
       $(grep 'MG iteration' "$d/run.log" | awk '{print $NF}' | head -8)
}
for mb in default single; do
  extra=()
  [[ $mb == single ]] && extra=(meshblock/nx1=64 meshblock/nx2=32 meshblock/nx3=32)
  one "$mb/S1" "$S" 1 "${extra[@]}"
  one "$mb/O1" "$O" 1 "${extra[@]}"
  one "$mb/O2" "$O" 2 "${extra[@]}"
  one "$mb/O4a" "$O" 4 "${extra[@]}"
  one "$mb/O4b" "$O" 4 "${extra[@]}"
  one "$mb/O8" "$O" 8 "${extra[@]}"
done
grep -h "nx1\|nx2\|nx3" "$deck" | head -6
