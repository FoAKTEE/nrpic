#!/usr/bin/env bash
# Smoke test of inputs/conv.athinput with core's requests-b processor executable: eight
# cycles at 32^3 (eps = 1 initial data of run B-20261115-165357-37d0477), output intervals
# shortened so that both bin outputs and a restart file are written; then the single- and
# the double-precision dump of the same cycle are read with fslib/binread.py and compared.
#   smoke_conv.sh            (output: $NRPIC_RUN_DIR)
set -euo pipefail
out=${NRPIC_RUN_DIR:?run through nrpic-run}
WT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
EXE=${ATHENA_CPU_EXE:-/data/haiyangw/nrpic/scratch/core/exe/core_requests-b/athena_cpu}
IC=/data/haiyangw/nrpic/scratch/B-emd-gw/B-20261115-165357-37d0477/eps1
export OMP_NUM_THREADS=1
cd "$out"
"$EXE" -i "$WT/tracks/B-emd-gw/first_source/inputs/conv.athinput" -d "$out" \
  mesh/nx1=32 mesh/nx2=32 mesh/nx3=32 meshblock/nx1=16 meshblock/nx2=16 meshblock/nx3=16 \
  particles/traj_ntrack=190 particles/particle_file=$IC/particles.nrp problem/id_file=$IC/fields.bin \
  time/nlim=8 output2/dt=0.05 output3/dt=0.05 output4/dt=0.1 > athena.log 2>&1
ls -l bin rst | head -20
python3 - "$out" "$WT" <<'EOF'
import glob, os, sys
sys.path.insert(0, os.path.join(sys.argv[2], "tracks/B-emd-gw/first_source/fslib"))
import paths  # noqa: F401
import numpy as np
from fslib import binread
out = sys.argv[1]
s = sorted(glob.glob(os.path.join(out, "bin", "*.z4c.*.bin")))
d = sorted(glob.glob(os.path.join(out, "bin", "*.z4cd.*.bin")))
print("single:", [os.path.basename(p) for p in s])
print("double:", [os.path.basename(p) for p in d])
for ps, pd in zip(s, d):
    a, b = binread.read_bin(ps), binread.read_bin(pd)
    dmax = max(float(np.abs(a[n] - b[n]).max()) for n in a["variables"])
    rel = max(float(np.abs(a[n] - b[n]).max() / max(np.abs(b[n]).max(), 1e-300)) for n in a["variables"])
    print(os.path.basename(ps), a["var_size"], b["var_size"], a["cycle"], b["cycle"], a["time"], b["time"],
          "max|single-double| =", dmax, "max relative =", rel)
EOF
