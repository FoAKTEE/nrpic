#!/usr/bin/env bash
# Runs the entries of a list file (`<name> <athinput> [athena args...]`, paths relative to the worktree
# root) on the processors with the release processor build core-v0.7, at most MAXJOBS at a time (one core
# each), each in OUT/<name>/. OUT/status.txt: name, exit status, seconds. Adapted from
# ../usr/scripts/run_list.sh (one executable, bounded concurrency).
#
#   zeta/run_list_v07.sh <list> [<out>]      (<out> defaults to $NRPIC_RUN_DIR; MAXJOBS defaults to 2)
set -uo pipefail
LIST=$1
OUT=${2:-${NRPIC_RUN_DIR:-}}
MAXJOBS=${MAXJOBS:-2}
EXE=/data/haiyangw/nrpic/.work/build_cpu_v07/src/athena
if [[ $OUT != /* || ! -d $OUT ]]; then
  echo "run_list_v07.sh: output directory '$OUT' is not an existing absolute path" >&2
  exit 2
fi
ROOT=$(pwd)
export OMP_NUM_THREADS=1
: > "$OUT/status.txt"
sha256sum "$EXE" > "$OUT/executable.sha256"
fail=0
while read -r name deck rest; do
  [[ -z ${name:-} || $name == \#* ]] && continue
  while (( $(jobs -rp | wc -l) >= MAXJOBS )); do wait -n || fail=1; done
  mkdir -p "$OUT/$name"
  (
    cd "$OUT/$name" || exit 1
    s0=$(date +%s.%N)
    # shellcheck disable=SC2086
    "$EXE" -i "$ROOT/$deck" $rest -d . > athena.log 2>&1
    rc=$?
    s1=$(date +%s.%N)
    echo "$name rc=$rc seconds=$(awk -v a="$s0" -v b="$s1" 'BEGIN{printf "%.1f", b - a}')" >> "$OUT/status.txt"
    exit $rc
  ) &
done < "$LIST"
while (( $(jobs -rp | wc -l) > 0 )); do wait -n || fail=1; done
exit $fail
