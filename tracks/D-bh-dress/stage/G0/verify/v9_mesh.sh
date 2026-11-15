#!/bin/bash
# C8b: MeshBlock counts of the D-pre-4 mesh family from AthenaK itself (-m: build the tree,
# write mesh_structure.dat, quit), for the finest level 5..8 with the calibration input's
# refined region (|x| < 1.5 M requested) and for level 7, 8 with |x| < 2 M (horizon inside
# the finest level for 500 M). Runs in $NRPIC_RUN_DIR (the -m file is written to the cwd).
set -euo pipefail
OUT="${NRPIC_RUN_DIR:?}"
EXE=/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena
INP=/data/haiyangw/nrpic/wt/D-bh-dress/tracks/D-bh-dress/puncture_drift/inputs/drift_dx16.athinput
cd "$OUT"
for spec in "L5 5 1.5" "L6 6 1.5" "L7 7 1.5" "L8 8 1.5" "L7r2 7 2.0" "L8r2 8 2.0"; do
  set -- $spec
  r=$3
  "$EXE" -i "$INP" -m refined_region2/level=$2 \
     refined_region2/x1min=-$r refined_region2/x1max=$r refined_region2/x2min=-$r \
     refined_region2/x2max=$r refined_region2/x3min=-$r refined_region2/x3max=$r > "mesh_$1.log" 2>&1
  mv mesh_structure.dat "mesh_$1.dat"
  echo "$1 level=$2 region=+-$r $(grep 'Total number of MeshBlocks' mesh_$1.log)"
done
