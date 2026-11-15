#!/usr/bin/env bash
# One AthenaK run of the newton_tests package in $NRPIC_RUN_DIR/<name>/ (processor build).
#
#   run_case.sh <name> <generator kind> "<generator args>" <athinput | none> [athena args...]
#
# Writes the particle file with scripts/make_particles.py into the case directory, then
# runs the executable of the release core-v0.3 there ($NRPIC_CPU_EXE, set by nrpic-env;
# default .work/build_cpu_v03) with the input and the command-line overrides. Called
# through harness/bin/nrpic-run submit (local launcher) from the worktree root.
set -euo pipefail
name=$1; kind=$2; genargs=$3; input=$4; shift 4
here=$(cd "$(dirname "$0")" && pwd)
: "${NRPIC_RUN_DIR:?run through nrpic-run}"
exe=${NRPIC_CPU_EXE:-/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena}
case_dir="$NRPIC_RUN_DIR/$name"
mkdir -p "$case_dir"
# shellcheck disable=SC2086
python3 "$here/make_particles.py" "$kind" --out "$case_dir" $genargs
# <athinput> = none: particle file only (for card runs started from a batch list)
[[ $input == none ]] && exit 0
inp=$(cd "$(dirname "$input")" && pwd)/$(basename "$input")
cp "$inp" "$case_dir/input.athinput"
printf '%s\n' "$exe -i input.athinput particles/particle_file=particles.nrp $*" \
    > "$case_dir/command.txt"
cd "$case_dir"
start=$(date +%s)
"$exe" -i input.athinput particles/particle_file=particles.nrp "$@" > athena.log 2>&1
end=$(date +%s)
echo "wall_s $((end - start))" >> athena.log
echo "$name done in $((end - start)) s"
