#!/bin/bash
# Lead's rerun of the Newtonian point-mass field test (problems/newton/README.md, T1) with
# the merged processor executable, N = 32 and 64, in the current directory.
# Usage: newton_point.sh ATHENA
set -euo pipefail
EXE=$1
WT=/data/haiyangw/nrpic/wt/core
P=$WT/problems/newton
python3 $P/make_ic.py point --out point.nrp --center 0.031 0.017 -0.011
for n in 32 64; do
  mkdir -p n$n
  cp $P/isolated.athinput n$n/   # analyze_field.py reads the input from the run directory
  (cd n$n && $EXE -i isolated.athinput mesh/nx1=$n mesh/nx2=$n mesh/nx3=$n time/nlim=1 \
     particles/dt=1e-6 particles/snap_dt=1e-6 particles/particle_file=../point.nrp > athena.log 2>&1)
done
python3 $P/analyze_field.py point --ic point.json --run 32:n32 --run 64:n64 --out field
