#!/usr/bin/env bash
# Figure and table of the strong scaling of work package omp (figs.py scaling, table),
# from the registered phases: one thread, serial build, 4 (disjoint places), 16, 32, 64.
#   analyse_scaling.sh [card output dir]      (run inside the output directory)
# RUNS2: run ids of further phases of the second series (t1solo, collapse1, collapse6 of
# journal entry 20; punc16 of entry 26), separated by spaces
set -uo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PY=${PY:-python3}
S=/data/haiyangw/nrpic/scratch/core
runs=("$S/core-20261119-154725-1c3e906" "$S/core-20261119-154729-1c3e906"
      "$S/core-20261119-163647-53000b7" "$S/core-20261119-161025-820e057"
      "$S/core-20261119-162248-f2f3758" "$S/core-20261119-163017-11fe2fd")
# second series: one and six threads on 2026-11-20 (load average 22 to 56; six cores are
# the limit per session since decision 0019), and the isolated Newtonian collapse
runs2=("$S/core-20261120-220756-0eaaf74")
for r in ${RUNS2:-}; do runs2+=("$S/$r"); done
L2="2026-11-20, load 11 to 56, best of the runs of that day (first table: 2026-11-19, load 97 to 157)"
mkdir -p figs
"$PY" "$HERE/figs.py" scaling --runs "${runs[@]}" --card "${1:-}" --out figs/scaling \
    --runs2 "${runs2[@]}" --label2 "2026-11-20 (quieter machine)"
"$PY" "$HERE/figs.py" table --runs "${runs[@]}" --card "${1:-}" --out scaling_table.md \
    --runs2 "${runs2[@]}" --label2 "$L2"
cp figs/scaling.png figs/scaling.pdf "$HERE/figs/"
cp scaling_table.md "$HERE/scaling_table.md"
