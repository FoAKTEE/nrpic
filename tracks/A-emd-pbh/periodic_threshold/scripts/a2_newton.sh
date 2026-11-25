#!/usr/bin/env bash
# A2 control (JOURNAL 2026-11-25 08:10 PST): S1L's particles in the Newtonian mode (core-v0.7 processor build), members
# N-z (equal masses, Zel'dovich velocities), N-f (S1L's file as it is), N-z128 (N-z on 128^3), then the first-crossing
# reader on each.   a2_newton.sh <outdir>
set -uo pipefail
OUT=$1
HERE=$(cd "$(dirname "$0")" && pwd)
EXE=/data/haiyangw/nrpic/.work/build_cpu_v07/src/athena
DECK=$HERE/../inputs/a2_newton.athinput
SRC=/data/haiyangw/nrpic/scratch/A-emd-pbh/A-emd-pbh-20261115-155802-9a6596f/S_mu0.3/particles.nrp
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
python "$HERE/a2_newton_ic.py" --src "$SRC" --out "$OUT/ic" || exit 1
rc=0
run() {  # name particle_file [extra args]
  local name=$1 pf=$2; shift 2
  mkdir -p "$OUT/$name"
  ( cd "$OUT/$name" && /usr/bin/time -v "$EXE" -i "$DECK" particles/particle_file="$pf" "$@" > athena.log 2> time.log ) || rc=$?
  tail -n 3 "$OUT/$name/athena.log"
}
run N-z "$OUT/ic/N-z.nrp"
run N-f "$SRC"
run N-z128 "$OUT/ic/N-z.nrp" mesh/nx1=128 mesh/nx2=128 mesh/nx3=128 meshblock/nx1=32 meshblock/nx2=32 meshblock/nx3=32
for name in N-z N-f N-z128; do
  python "$HERE/a2_crossing.py" --run "$OUT/$name" --out "$OUT/$name/a2" --clock newton --label "$name" > "$OUT/$name/a2.log" 2>&1 || rc=$?
done
exit $rc
