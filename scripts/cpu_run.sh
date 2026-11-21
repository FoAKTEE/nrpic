#!/usr/bin/env bash
# Run the threaded processor build of AthenaK (scripts/build_cpu_omp.sh) on the login node.
#
#   scripts/cpu_run.sh <rundir> <athinput | file.rst> [extra athena args...]
#
# - <athinput> is passed as -i; a file ending in .rst is passed as -r (restart).
# - athena runs with its working directory set to <rundir> and with -d <rundir>, as with
#   scripts/gpu_run.sh; relative paths inside the input file are relative to <rundir>.
# - stdout+stderr go to <rundir>/athena.<timestamp>.log (symlink athena.log -> latest),
#   with a header (threads, places, load of the machine) and a footer (exit status, wall
#   time, processor time, share of the asked processor time that the run obtained).
# - Blocking; returns athena's exit status. No Slurm: the processors are not scheduled,
#   so the limit of six cores per session (decision 0019, CLAUDE.md) is the caller's to
#   keep.
#
# Environment:
#   ATHENA_EXE  executable (default build_omp/src/athena)
#   THREADS     number of threads (default: OMP_NUM_THREADS if set, else 6)
#   PLACES      auto (default): the THREADS least busy cores of one NUMA node, chosen by
#               scripts/omp_places.py when the run starts, with OMP_PROC_BIND=true;
#               none: no binding (OMP_PROC_BIND=false); anything else: an OMP_PLACES
#               value, used with OMP_PROC_BIND=${BIND:-close}
# Do not use OMP_PLACES=cores with spread or close on this machine: every job is then
# bound to the same cores (scripts/README.md, "Threaded processor runs").
set -euo pipefail

if [[ $# -lt 2 ]]; then
  awk 'NR>1 && /^#/ {sub(/^# ?/, ""); print; next} NR>1 {exit}' "$0"
  exit 1
fi

SCRIPTS=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO=$(dirname "$SCRIPTS")
EXE=${ATHENA_EXE:-$REPO/build_omp/src/athena}
THREADS=${THREADS:-${OMP_NUM_THREADS:-6}}
PLACES=${PLACES:-auto}

mkdir -p "$1"
rundir=$(cd "$1" && pwd)
input=$(cd "$(dirname "$2")" && pwd)/$(basename "$2")
shift 2
[[ -f $input ]] || { echo "ERROR: no such file: $input" >&2; exit 1; }
[[ -x $EXE ]]   || { echo "ERROR: executable not found: $EXE (scripts/build_cpu_omp.sh, or set ATHENA_EXE)" >&2; exit 1; }
EXE=$(cd "$(dirname "$EXE")" && pwd)/$(basename "$EXE")

ts=$(date +%Y%m%d-%H%M%S)
if [[ $input == *.rst ]]; then
  inflag=-r
else
  inflag=-i
  if [[ $(dirname "$input") != "$rundir" ]]; then
    cp "$input" "$rundir/$(basename "$input")"
  fi
fi
log=$rundir/athena.$ts.log
ln -sfn "athena.$ts.log" "$rundir/athena.log"

export OMP_NUM_THREADS=$THREADS
case $PLACES in
  auto) OMP_PLACES=$(python3 "$SCRIPTS/omp_places.py" "$THREADS"); export OMP_PLACES
        export OMP_PROC_BIND=true ;;
  none) unset OMP_PLACES; export OMP_PROC_BIND=false ;;
  *)    export OMP_PLACES=$PLACES; export OMP_PROC_BIND=${BIND:-close} ;;
esac

cd "$rundir"
{
  echo "# host=$(hostname) threads=$OMP_NUM_THREADS proc_bind=$OMP_PROC_BIND" \
       "places=${OMP_PLACES:-unset} load=$(cut -d' ' -f1-3 /proc/loadavg) start=$(date -Is)"
  echo "# cwd=$PWD"
  echo "# cmd: $EXE $inflag $input -d $rundir $*"
} > "$log"

apid=
forward() { [[ -n $apid ]] && kill -TERM "$apid" 2>/dev/null; }
trap forward TERM INT
t0=$(date +%s.%N)
"$EXE" "$inflag" "$input" -d "$rundir" "$@" >> "$log" 2>&1 &
apid=$!
while :; do
  wait "$apid"; rc=$?
  if (( rc > 128 )) && kill -0 "$apid" 2>/dev/null; then continue; fi
  break
done
t1=$(date +%s.%N)
# processor time of the children of this shell (athena): user + system, in seconds
cpu=$(awk '{print ($16 + $17)/100}' /proc/$$/stat)   # cutime + cstime, 100 ticks per second
awk -v t0="$t0" -v t1="$t1" -v cpu="$cpu" -v n="$THREADS" -v rc="$rc" -v end="$(date -Is)" \
    -v load="$(cut -d' ' -f1-3 /proc/loadavg)" 'BEGIN {
      w = t1 - t0;
      printf "# exit=%d end=%s wall_s=%.1f cpu_s=%.1f cpu_share=%.2f load=%s\n",
             rc, end, w, cpu, (w > 0 ? cpu/(w*n) : 0), load }' >> "$log"
exit $rc
