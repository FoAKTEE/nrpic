#!/usr/bin/env bash
# Run several short AthenaK runs one after another inside one Slurm job on one A100.
#
#   scripts/gpu_batch.sh <listfile>
#
# Each non-empty line of <listfile> that does not start with '#':
#   <rundir> <athinput | file.rst> [extra athena args...]
# The runs go through scripts/gpu_run.sh, which runs directly when it is already inside
# a job that sees a GPU. A failed run does not stop the following ones; the status of
# each is appended to <listfile>.status.
#
# Environment: ATHENA_EXE, TIME (default 00:45:00), JOB_NAME (default batch), PARTITION.
set -euo pipefail
SCRIPTS=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
list=$(cd "$(dirname "$1")" && pwd)/$(basename "$1")
[[ -f $list ]] || { echo "ERROR: no such file: $list" >&2; exit 1; }
if [[ -z ${SLURM_JOB_ID:-} ]]; then
  EXE=${ATHENA_EXE:?set ATHENA_EXE}
  snap=$list.exe
  cp "$EXE" "$snap"
  jid=$(sbatch --parsable -p "${PARTITION:-preempt}" --gres=gpu:1 -c 1 -t "${TIME:-00:45:00}" \
          -J "${JOB_NAME:-batch}" -o "$list.slurm-%j.out" \
          --export=ALL,ATHENA_EXE="$snap" "$0" "$list")
  echo "submitted job $jid for $(grep -cv '^\s*\(#\|$\)' "$list") runs"
  exit 0
fi
cd "$(dirname "$SCRIPTS")"
while read -r line; do
  [[ -z $line || $line == \#* ]] && continue
  # shellcheck disable=SC2086
  set -- $line
  if "$SCRIPTS/gpu_run.sh" "$@" > /dev/null 2>&1; then rc=0; else rc=$?; fi
  echo "$(date +%H:%M:%S) rc=$rc $1" >> "$list.status"
done < "$list"
