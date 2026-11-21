#!/usr/bin/env bash
# binary_conv: `athena -m` start trees of the P1b inputs (release core-v0.5 processor build).
set -euo pipefail
WT=$(cd "$(dirname "$0")/../../../.." && pwd)
OUT=${NRPIC_RUN_DIR:?}
EXE=/data/haiyangw/nrpic/.work/build_cpu_v05/src/athena
for r in R16n R12; do
  mkdir -p "$OUT/p1b_$r"
  ( cd "$OUT/p1b_$r" && "$EXE" -i "$WT/tracks/F-hills/binary_conv/inputs/p1b_$r.athinput" -m 1 > athena_m.log 2>&1 || true )
  echo "$r $(grep 'Total number of MeshBlocks' "$OUT/p1b_$r/athena_m.log")"
done
