#!/usr/bin/env bash
# Figure and table of the strong scaling of work package omp (figs.py scaling, table),
# from the registered phases: one thread, serial build, 4 (disjoint places), 16, 32, 64.
#   analyse_scaling.sh [card output dir]      (run inside the output directory)
set -uo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PY=${PY:-python3}
S=/data/haiyangw/nrpic/scratch/core
runs=("$S/core-20261119-154725-1c3e906" "$S/core-20261119-154729-1c3e906"
      "$S/core-20261119-163647-53000b7" "$S/core-20261119-161025-820e057"
      "$S/core-20261119-162248-f2f3758" "$S/core-20261119-163017-11fe2fd")
mkdir -p figs
"$PY" "$HERE/figs.py" scaling --runs "${runs[@]}" --card "${1:-}" --out figs/scaling
"$PY" "$HERE/figs.py" table --runs "${runs[@]}" --card "${1:-}" --out scaling_table.md
cp figs/scaling.png figs/scaling.pdf "$HERE/figs/"
cp scaling_table.md "$HERE/scaling_table.md"
