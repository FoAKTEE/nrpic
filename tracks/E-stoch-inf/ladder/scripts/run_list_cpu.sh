#!/usr/bin/env bash
# Runs the entries of a list file (`<name> <athinput> [athena args...]`, paths relative to
# the worktree root) with a processor executable, all entries at once (one core each),
# each in OUT/<name>/ (athena's working directory, so relative paths of the input resolve
# there).  OUT/status.txt gets one line per entry: name, exit status, seconds.
#
#   scripts/run_list_cpu.sh <exe> <list> <out>
#
# Used inside a registered run (harness/bin/nrpic-run submit --launcher local ... -- bash
# tracks/E-stoch-inf/ladder/scripts/run_list_cpu.sh EXE LIST "$NRPIC_RUN_DIR").
set -uo pipefail
EXE=$1
LIST=$2
OUT=$3
ROOT=$(pwd)
export OMP_NUM_THREADS=1
: > "$OUT/status.txt"
pids=()
names=()
while read -r name deck rest; do
  [[ -z ${name:-} || $name == \#* ]] && continue
  mkdir -p "$OUT/$name"
  cp "$ROOT/$deck" "$OUT/$name/"
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
  pids+=($!)
  names+=("$name")
done < "$LIST"
fail=0
for i in "${!pids[@]}"; do
  wait "${pids[$i]}" || fail=1
done
cat "$OUT/status.txt"
exit $fail
