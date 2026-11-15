#!/usr/bin/env bash
# E8 of nr_first/JOURNAL.md: the P1 data at m/8 for one cycle on processors with the
# finders' verbose output, to see why horizon 1 (m2) is not found at t = 0.
# Usage (from the worktree root, through nrpic-run): finderdiag.sh [outdir]
set -euo pipefail
EXE=/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena
IN=/data/haiyangw/nrpic/wt/F-hills/tracks/F-hills/nr_first/inputs/p1_q4_finderdiag.athinput
OUT=$(cd "${1:-${NRPIC_RUN_DIR:?outdir}}" && pwd)
(cd "$OUT" && "$EXE" -i "$IN" -d "$OUT" time/nlim=1 mesh_refinement/max_nmb_per_rank=1780 \
    output5/dt=1.0e9 output6/dt=1.0e9 > "$OUT/athena.log" 2>&1)
for n in 0 1 2; do
  echo "== horizon $n"; tail -n 25 "$OUT"/hills.horizon_verbose_$n.txt 2>/dev/null || ls "$OUT"
done
