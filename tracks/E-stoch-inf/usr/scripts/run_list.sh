#!/usr/bin/env bash
# Runs the entries of a list file (`<name> <exe key> <athinput> [athena args...]`, paths
# relative to the worktree root) on the processors, all entries at once (one core each),
# each in OUT/<name>/.  Executables by key: v03 = release core-v0.3, s2 = core's branch
# executable core_scalar-2 (both read-only).  OUT/status.txt: name, exit status, seconds.
# Adapted from ../../ladder/scripts/run_list_cpu.sh (one executable per entry here).
#
#   scripts/run_list.sh <list> [<out>]      (<out> defaults to $NRPIC_RUN_DIR)
set -uo pipefail
LIST=$1
OUT=${2:-${NRPIC_RUN_DIR:-}}
declare -A EXE=(
  [v03]=/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena
  [s2]=/data/haiyangw/nrpic/scratch/core/exe/core_scalar-2/athena_cpu
)
if [[ $OUT != /* || ! -d $OUT ]]; then
  echo "run_list.sh: output directory '$OUT' is not an existing absolute path" >&2
  exit 2
fi
ROOT=$(pwd)
export OMP_NUM_THREADS=1
: > "$OUT/status.txt"
sha256sum "${EXE[v03]}" "${EXE[s2]}" > "$OUT/executables.sha256"
pids=()
while read -r name key deck rest; do
  [[ -z ${name:-} || $name == \#* ]] && continue
  exe=${EXE[$key]:-}
  if [[ -z $exe ]]; then echo "$name: unknown executable key $key" >> "$OUT/status.txt"; continue; fi
  mkdir -p "$OUT/$name"
  cp "$ROOT/$deck" "$OUT/$name/"
  (
    cd "$OUT/$name" || exit 1
    s0=$(date +%s.%N)
    # shellcheck disable=SC2086
    "$exe" -i "$ROOT/$deck" $rest -d . > athena.log 2>&1
    rc=$?
    s1=$(date +%s.%N)
    echo "$name exe=$key rc=$rc seconds=$(awk -v a="$s0" -v b="$s1" 'BEGIN{printf "%.1f", b - a}')" >> "$OUT/status.txt"
    exit $rc
  ) &
  pids+=($!)
done < "$LIST"
fail=0
for p in "${pids[@]}"; do
  wait "$p" || fail=1
done
cat "$OUT/status.txt"
exit $fail
