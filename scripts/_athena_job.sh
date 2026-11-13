#!/usr/bin/env bash
# Runs AthenaK inside a Slurm allocation (called by gpu_run.sh and submit_chain.sh;
# self-contained because sbatch spools a copy of the script).
#
#   _athena_job.sh <rundir> <logfile> <exe> [athena args...]
#
# Writes stdout+stderr of athena to <logfile> (with a header and a footer), samples the
# GPU memory every 0.5 s into <logfile minus .log>.gpumem.csv, and exits with athena's
# exit status. SIGTERM/SIGINT are forwarded to athena.
rundir=$1; log=$2; exe=$3; shift 3
mkdir -p "$rundir" && cd "$rundir" || exit 2
ulimit -c 0                      # no multi-GB core files from GPU processes
export OMP_NUM_THREADS=1         # Kokkos host space is Serial; be explicit anyway
export OMP_PROC_BIND=false

gpumem=${log%.log}.gpumem.csv
{
  echo "# host=$(hostname) slurm_job=${SLURM_JOB_ID:-none}" \
       "CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-unset} cpus=$(nproc) start=$(date -Is)"
  echo "# cwd=$PWD"
  echo "# cmd: $exe $*"
  if command -v nvidia-smi >/dev/null && nvidia-smi -L >/dev/null 2>&1; then
    nvidia-smi --query-gpu=index,name,driver_version,memory.total,memory.used \
               --format=csv | sed 's/^/# /'
  else
    echo "# no GPU visible (nvidia-smi failed)"
  fi
} > "$log" 2>&1

base=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | head -1)
mon=
if [[ -n $base ]]; then
  echo "# timestamp, memory.used [MiB], utilization.gpu [%]" > "$gpumem"
  nvidia-smi --query-gpu=timestamp,memory.used,utilization.gpu \
             --format=csv,noheader,nounits -lms 500 >> "$gpumem" 2>/dev/null &
  mon=$!
fi

apid=
forward() { [[ -n $apid ]] && kill -TERM "$apid" 2>/dev/null; }
trap forward TERM INT

"$exe" "$@" >> "$log" 2>&1 &
apid=$!
# 'wait' returns early (status >128) when a trapped signal arrives; keep waiting while
# athena is still alive so that rc is its real exit status
while :; do
  wait "$apid"; rc=$?
  if (( rc > 128 )) && kill -0 "$apid" 2>/dev/null; then continue; fi
  break
done

if [[ -n $mon ]]; then kill "$mon" 2>/dev/null; wait "$mon" 2>/dev/null; fi
peak=$(awk -F', *' '!/^#/ && $2+0>m {m=$2+0} END{print m+0}' "$gpumem" 2>/dev/null)
echo "# exit=$rc end=$(date -Is) gpu_mem_baseline_MiB=${base:-na}" \
     "gpu_mem_peak_MiB=${peak:-na}" >> "$log"
exit $rc
