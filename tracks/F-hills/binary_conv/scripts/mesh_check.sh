#!/usr/bin/env bash
# binary_conv BC-0: start trees of the three inputs from `athena -m` (release core-v0.5,
# processor build; no evolution) against the tree model, and the model along the Newtonian
# tracks to 100 M with the card cost (scripts/tree_cost.py). Output in $NRPIC_RUN_DIR.
set -euo pipefail
WT=$(cd "$(dirname "$0")/../../../.." && pwd)
OUT=${NRPIC_RUN_DIR:?}
EXE=/data/haiyangw/nrpic/.work/build_cpu_v05/src/athena
for r in m8 m12 m16; do
  mkdir -p "$OUT/mesh_$r"
  ( cd "$OUT/mesh_$r" && "$EXE" -i "$WT/tracks/F-hills/binary_conv/inputs/bin_$r.athinput" -m 1 > athena_m.log 2>&1 || true )
  grep -E -i 'MeshBlock|level|Total' "$OUT/mesh_$r/athena_m.log" | tail -20 || true
done
for r in m8 m12 m16; do
  python3 "$WT/tracks/F-hills/binary_conv/scripts/tree_cost.py" \
    "$WT/tracks/F-hills/binary_conv/inputs/bin_$r.athinput" "$OUT/tree_cost_$r.json" --dt 0.5
done
