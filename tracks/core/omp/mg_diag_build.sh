#!/usr/bin/env bash
# Diagnostic executable of work package omp (journal entry 18): the threaded build of this
# worktree (.work/build_omp, read only) with tools/mg_average_diag.patch applied to a
# copy of athenak/src/multigrid/multigrid.cpp. Only that file is compiled again, with the
# flags of the build, and linked with the other objects of the build. The patch adds the
# environment variable MG_AVERAGE (ordered | comp) to Multigrid::CalculateAverage; unset,
# the executable computes what the threaded build computes. Nothing of this enters the
# source tree.
#   mg_diag_build.sh [outdir]     (default scratch/core/omp/mgdiag)
set -euo pipefail
WT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
B=$WT/.work/build_omp
OUT=${1:-/data/haiyangw/nrpic/scratch/core/omp/mgdiag}
D=$B/src/CMakeFiles/athena.dir
mkdir -p "$OUT/src" "$OUT/obj"
cp "$WT/athenak/src/multigrid/multigrid.cpp" "$OUT/src/multigrid.cpp"
patch -s "$OUT/src/multigrid.cpp" < "$WT/tracks/core/omp/tools/mg_average_diag.patch"
flags=$(sed -n 's/^CXX_FLAGS = //p' "$D/flags.make")
defs=$(sed -n 's/^CXX_DEFINES = //p' "$D/flags.make")
incs=$(sed -n 's/^CXX_INCLUDES = //p' "$D/flags.make")
# shellcheck disable=SC2086
/usr/bin/g++ $defs $incs -I"$WT/athenak/src/multigrid" $flags \
    -c "$OUT/src/multigrid.cpp" -o "$OUT/obj/multigrid.cpp.o"
link=$(sed -e "s|CMakeFiles/athena.dir/multigrid/multigrid.cpp.o|$OUT/obj/multigrid.cpp.o|" \
           -e "s| -o athena | -o $OUT/athena |" "$D/link.txt")
grep -q "$OUT/obj/multigrid.cpp.o" <<< "$link"
grep -q -- "-o $OUT/athena " <<< "$link"
(cd "$B/src" && eval "$link")
{ echo "base build: $B (sha256 $(sha256sum "$B/src/athena" | cut -d' ' -f1))"
  echo "patch: tracks/core/omp/tools/mg_average_diag.patch (sha256 $(sha256sum "$WT/tracks/core/omp/tools/mg_average_diag.patch" | cut -d' ' -f1))"
  echo "commit: $(git -C "$WT" rev-parse HEAD)"
  echo "built: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  sha256sum "$OUT/athena"; } > "$OUT/BUILD.txt"
cat "$OUT/BUILD.txt"
