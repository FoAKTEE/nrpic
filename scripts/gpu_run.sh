#!/usr/bin/env bash
# Run AthenaK on one A100 through Slurm (partition preempt).
#
#   scripts/gpu_run.sh <rundir> <athinput | file.rst> [extra athena args...]
#
# - <athinput> is passed as -i; a file ending in .rst is passed as -r (restart).
# - athena runs with its working directory set to <rundir> and with -d <rundir>, so all
#   outputs (hst, tab, bin, vtk, rst/, pvtk/, trk/...) land in <rundir>. Relative paths
#   inside the input file are therefore relative to <rundir>.
# - stdout+stderr go to <rundir>/athena.<timestamp>.log (symlink athena.log -> latest);
#   GPU memory is sampled into athena.<timestamp>.gpumem.csv and the peak is printed.
# - Extra args are passed through, e.g. time/nlim=50 -t 00:20:00 mesh/nx1=64
#
# Modes:
#   default    blocking srun (new allocation, 1 GPU, 1 core); returns athena's status
#   BATCH=1    non-blocking sbatch; the executable is first copied into <rundir> so a
#              rebuild while the job is queued does not change what runs
#   inside an existing Slurm job that already sees a GPU: runs directly, no new srun
#
# Environment: ATHENA_EXE (default build_gpu/src/athena), TIME (Slurm limit, default
#   00:30:00, max 01:00:00), CPUS (default 1), PARTITION (default preempt),
#   JOB_NAME (default athena), SLURM_EXTRA (extra srun/sbatch options)
set -euo pipefail

if [[ $# -lt 2 ]]; then
  awk 'NR>1 && /^#/ {sub(/^# ?/, ""); print; next} NR>1 {exit}' "$0"
  exit 1
fi

SCRIPTS=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO=$(dirname "$SCRIPTS")
EXE=${ATHENA_EXE:-$REPO/build_gpu/src/athena}
TIME=${TIME:-00:30:00}
CPUS=${CPUS:-1}
PARTITION=${PARTITION:-preempt}
JOB_NAME=${JOB_NAME:-athena}
# shellcheck disable=SC2206
SLURM_EXTRA=( ${SLURM_EXTRA:-} )

mkdir -p "$1"
rundir=$(cd "$1" && pwd)
input=$(cd "$(dirname "$2")" && pwd)/$(basename "$2")
shift 2
[[ -f $input ]] || { echo "ERROR: no such file: $input" >&2; exit 1; }
[[ -x $EXE ]]   || { echo "ERROR: executable not found: $EXE (build it or set ATHENA_EXE)" >&2; exit 1; }
EXE=$(cd "$(dirname "$EXE")" && pwd)/$(basename "$EXE")

ts=$(date +%Y%m%d-%H%M%S)
if [[ $input == *.rst ]]; then
  inflag=-r
else
  inflag=-i
  # keep a copy of the input next to the outputs (provenance), unless it is already there
  if [[ $(dirname "$input") != "$rundir" ]]; then
    cp "$input" "$rundir/$(basename "$input")"
  fi
fi
log=$rundir/athena.$ts.log
ln -sfn "athena.$ts.log" "$rundir/athena.log"
athargs=("$inflag" "$input" -d "$rundir" "$@")

if [[ ${BATCH:-0} == 1 ]]; then
  snap=$rundir/athena.$ts.exe
  cp "$EXE" "$snap"
  jid=$(sbatch --parsable -p "$PARTITION" --gres=gpu:1 -c "$CPUS" -t "$TIME" \
          -J "$JOB_NAME" -o "$rundir/slurm-%j.out" "${SLURM_EXTRA[@]}" \
          "$SCRIPTS/_athena_job.sh" "$rundir" "$log" "$snap" "${athargs[@]}")
  echo "submitted job $jid  (log: $log)"
  exit 0
fi

set +e
if [[ -n ${SLURM_JOB_ID:-} ]] && nvidia-smi -L >/dev/null 2>&1; then
  "$SCRIPTS/_athena_job.sh" "$rundir" "$log" "$EXE" "${athargs[@]}"
  rc=$?
else
  srun -p "$PARTITION" --gres=gpu:1 -c "$CPUS" -t "$TIME" -J "$JOB_NAME" \
       "${SLURM_EXTRA[@]}" "$SCRIPTS/_athena_job.sh" "$rundir" "$log" "$EXE" "${athargs[@]}"
  rc=$?
fi
set -e
echo "----- tail of $log"
tail -n 12 "$log"
exit $rc
