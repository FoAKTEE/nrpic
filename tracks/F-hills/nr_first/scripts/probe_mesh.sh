#!/usr/bin/env bash
# E1 of nr_first/JOURNAL.md: MeshBlock counts of the package's inputs on processors.
#   (a) athena -m trees at t = 0 of the q = 4 three-black-hole data with 9, 10, 11 levels
#   (b) the single-puncture input at m/8 and m/16 for 16 cycles (the wave zone is refined
#       one level per check, every 4 cycles), with the processor time per cycle
# Usage (from the worktree root, through nrpic-run): probe_mesh.sh <outdir>
# Writes <outdir>/counts.txt (one line per case) and one directory per case.
set -euo pipefail
EXE=/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena
WT=/data/haiyangw/nrpic/wt/F-hills
Q4=$WT/tracks/F-hills/three_punctures/inputs/hills_q4_m8.athinput
S=$WT/tracks/F-hills/nr_first/inputs/single_P025.athinput
OUT=$(cd "${1:?outdir}" && pwd)
: > "$OUT/counts.txt"

count_tree() {  # <dir> <input> [args...]: athena -m in <dir>, prints the number of blocks
  local d=$1; shift
  mkdir -p "$d"
  (cd "$d" && "$EXE" -i "$@" -m > athena_m.log 2>&1)
  grep -c '^#MeshBlock' "$d/mesh_structure.dat"
}

for nl in 9 10 11; do
  n=$(count_tree "$OUT/q4_L$nl" "$Q4" mesh_refinement/num_levels=$nl)
  echo "q4_three_bh num_levels=$nl t0_tree=$n" >> "$OUT/counts.txt"
done

for nl in 7 8; do
  d=$OUT/single_L$nl
  n0=$(count_tree "$d/tree" "$S" mesh_refinement/num_levels=$nl)
  t0=$(date +%s)
  "$EXE" -i "$S" -d "$d/run" mesh_refinement/num_levels=$nl time/nlim=16 time/ndiag=1 \
      > "$d/run.log" 2>&1
  t1=$(date +%s)
  echo "single num_levels=$nl t0_tree=$n0 wall_16_cycles_s=$((t1 - t0))" >> "$OUT/counts.txt"
done
cat "$OUT/counts.txt"
