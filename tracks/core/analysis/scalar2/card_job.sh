#!/usr/bin/env bash
# Card runs of package scalar2 inside one Slurm job on one A100:
#   sbatch --wait -p preempt --gres=gpu:1 -c 1 -t 00:20:00 -J core-sf2 -o DIR/slurm.out \
#          tracks/core/analysis/scalar2/card_job.sh <card exe> DIR
# DIR/runs.list (card_prepare.py): <name> <-i | -r> <file> [athena arguments...]; each
# run lands in DIR/<name>/.  DIR/status.txt gets one line per run (exit status, seconds);
# DIR/card_seconds.txt the seconds between the start and the end of the job.
set -uo pipefail
EXE=$1
DIR=$2
t0=$(date +%s)
nvidia-smi -L
cd "$DIR" || exit 1
: > status.txt
while read -r name flag file rest; do
  [[ -z $name || $name == \#* ]] && continue
  mkdir -p "$name"
  s0=$(date +%s.%N)
  # shellcheck disable=SC2086
  (cd "$name" && "$EXE" $flag "$file" $rest -d . > athena.log 2>&1)
  rc=$?
  s1=$(date +%s.%N)
  echo "$name rc=$rc seconds=$(awk -v a="$s0" -v b="$s1" 'BEGIN{printf "%.2f", b - a}')" >> status.txt
done < runs.list
t1=$(date +%s)
echo $((t1 - t0)) > card_seconds.txt
echo "card_job finished after $((t1 - t0)) s"
