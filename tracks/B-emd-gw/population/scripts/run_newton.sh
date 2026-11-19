#!/usr/bin/env bash
# One case of the population package: initial data with scripts/make_ic.py, then the
# Newtonian mode of the release core-v0.3 processor build in $NRPIC_RUN_DIR/<name>/.
#
#   run_newton.sh <name> "<make_ic args without --out>" [athena args...]
#
# The executable is $NRPIC_CPU_EXE (set by nrpic-env; default .work/build_cpu_v03).
# Called through harness/bin/nrpic-run submit (local launcher) from the worktree root.
set -euo pipefail
name=$1; icargs=$2; shift 2
here=$(cd "$(dirname "$0")" && pwd)
: "${NRPIC_RUN_DIR:?run through nrpic-run}"
exe=${NRPIC_CPU_EXE:-/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena}
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
case_dir="$NRPIC_RUN_DIR/$name"
mkdir -p "$case_dir"
# shellcheck disable=SC2086
python3 "$here/make_ic.py" $icargs --out "$case_dir" > "$case_dir/make_ic.log" 2>&1
cp "$here/../inputs/pop_newton.athinput" "$case_dir/input.athinput"
printf '%s\n' "$exe -i input.athinput $*" > "$case_dir/command.txt"
cd "$case_dir"
start=$(date +%s)
"$exe" -i input.athinput "$@" > athena.log 2>&1
end=$(date +%s)
echo "wall_s $((end - start))" >> athena.log
echo "$name done in $((end - start)) s"
