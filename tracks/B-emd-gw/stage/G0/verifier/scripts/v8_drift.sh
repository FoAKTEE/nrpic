#!/bin/bash
# Verifier of B-emd-gw: amplitude scaling of the homogeneous drift of gxx seen in the
# x-wave runs (C6). N = 32, 10 crossings, A = 2e-6 and 4e-6 (A = 1e-6 is run x_N32 of
# B-20261115-165056-835fddf).   v8_drift.sh [OUTDIR]   (default $NRPIC_RUN_DIR)
set -u
OUT=${1:-${NRPIC_RUN_DIR:?no output directory}}
EXE=/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena
IN=/data/haiyangw/nrpic/wt/B-emd-gw/tracks/B-emd-gw/periodic_z4c/inputs/lw_x.athinput
export OMP_NUM_THREADS=1 OMP_PROC_BIND=false
for A in 2.0e-6 4.0e-6; do
  mkdir -p "$OUT/A$A"
  ( cd "$OUT/A$A" && "$EXE" -i "$IN" -d . mesh/nx1=32 meshblock/nx1=32 mesh/x2max=0.125 \
      mesh/x3max=0.125 output1/slice_x2=0.046875 output1/slice_x3=0.046875 output1/dt=10 \
      output2/dt=1 time/tlim=10 problem/amp=$A > athena.log 2>&1; echo "exit $?" >> athena.log ) &
done
wait
for A in 2.0e-6 4.0e-6; do
  python3 - "$OUT/A$A" "$A" <<'PY'
import glob, sys
import numpy as np
d = sys.argv[1]
f = sorted(glob.glob(d + "/tab/*.tab"))[-1]
cols = open(f).readlines()[1].lstrip("#").split()
a = np.loadtxt(f)
D = {c: a[:, i] for i, c in enumerate(cols)}
print(sys.argv[2], f, "gxx-1 mean %.4e" % (D["z4c_gxx"] - 1).mean(),
      "gyy+gzz-2 mean %.4e" % (D["z4c_gyy"] + D["z4c_gzz"] - 2).mean())
PY
done
