#!/usr/bin/env bash
# E2 of nr_first/JOURNAL.md (run C0): Hamiltonian residual of the q = 4 three-black-hole
# data at t = 0 against resolution, on processors, with the release executable.
#   approx (the input: closed-form corrections with the background factor) at 9, 10, 11
#   levels (members at m/4, m/8, m/16); none (no correction) at the same three; plain sum
#   (corr_background = false) at 10 levels. The m/8 approx case runs one cycle (trackers and
#   horizon finders write their first rows), the others none.
# The slot limit is set to the t = 0 tree plus 64 (athena -m first), so that the memory is
# what the tree needs. Restart files written at t = 0 are not needed by the analysis.
# Usage (from the worktree root, through nrpic-run): c0_t0.sh <outdir>
set -euo pipefail
EXE=/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena
WT=/data/haiyangw/nrpic/wt/F-hills
Q4=$WT/tracks/F-hills/three_punctures/inputs/hills_q4_m8.athinput
OUT=$(cd "${1:?outdir}" && pwd)
NONE="problem/comp0_corr=none problem/comp1_corr=none problem/comp2_corr=none"
: > "$OUT/cases.txt"

one() {  # <name> <num_levels> <nlim> [extra args]
  local name=$1 nl=$2 nlim=$3; shift 3
  local d=$OUT/$name
  mkdir -p "$d/tree"
  # shellcheck disable=SC2068
  (cd "$d/tree" && "$EXE" -i "$Q4" mesh_refinement/num_levels=$nl $@ -m > athena_m.log 2>&1)
  local n
  n=$(grep -c '^#MeshBlock' "$d/tree/mesh_structure.dat")
  local t0 t1
  t0=$(date +%s)
  # shellcheck disable=SC2068
  "$EXE" -i "$Q4" -d "$d" mesh_refinement/num_levels=$nl \
      mesh_refinement/max_nmb_per_rank=$((n + 64)) time/nlim=$nlim $@ > "$d/athena.log" 2>&1
  t1=$(date +%s)
  echo "$name num_levels=$nl nlim=$nlim blocks=$n wall_s=$((t1 - t0)) args=$*" >> "$OUT/cases.txt"
}

one approx_L10 10 1
one none_L10   10 0 $NONE
one plain_L10  10 0 problem/corr_background=false
one approx_L9   9 0
one none_L9     9 0 $NONE
one approx_L11 11 0
one none_L11   11 0 $NONE
cat "$OUT/cases.txt"
