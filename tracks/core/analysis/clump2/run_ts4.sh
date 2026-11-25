#!/usr/bin/env bash
# Test TS4 of work package clump2: the mesh solve against the radial correction with the Robin
# faces at 16 M and at 32 M, both at dx = 1 (cluster at rest and moving at v = 0.3 with the
# curvature of the boost table). Run through nrpic-run on one core.
set -u
out=${NRPIC_RUN_DIR:?run through nrpic-run}
a=tracks/core/analysis/clump2
st=0
python3 $a/run_idsolve_static.py --box 16 --cells 32 --kinds rest,curv --out "$out/box16" > "$out/box16.log" 2>&1 || st=1
python3 $a/run_idsolve_static.py --box 32 --cells 64 --kinds rest,curv --out "$out/box32" > "$out/box32.log" 2>&1 || st=1
exit $st
