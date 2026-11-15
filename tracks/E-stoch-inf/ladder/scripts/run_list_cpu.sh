#!/usr/bin/env bash
# Runs the entries of a list file (`<name> <athinput> [athena args...]`, paths relative to
# the worktree root) with a processor executable, all entries at once (one core each),
# each in OUT/<name>/ (athena's working directory, so relative paths of the input resolve
# there).  OUT/status.txt gets one line per entry: name, exit status, seconds.
#
#   scripts/run_list_cpu.sh <exe> <list> [<out>]
#
# <out> defaults to $NRPIC_RUN_DIR (set by harness/bin/nrpic-run for a registered run);
# it must be an existing absolute directory.  nrpic-run passes its command without a
# shell, so a literal '$NRPIC_RUN_DIR' on its command line is not expanded: leave <out>
# out (run E-20261115-172521-e098160 wrote into a directory named '$NRPIC_RUN_DIR').
set -uo pipefail
EXE=$1
LIST=$2
OUT=${3:-${NRPIC_RUN_DIR:-}}
if [[ $OUT != /* || ! -d $OUT ]]; then
  echo "run_list_cpu.sh: output directory '$OUT' is not an existing absolute path" >&2
  exit 2
fi
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
