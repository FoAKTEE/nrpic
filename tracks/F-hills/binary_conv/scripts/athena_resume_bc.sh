#!/usr/bin/env bash
# Executable wrapper for a chain that CONTINUES an earlier binary_conv run in a new run
# directory (lead, batch 5: R16n extension). Same as athena_keep_trackers_bc.sh (tracker
# files kept in trk_keep/ before each start; real executable = byte copy bc-ak05-gpu of
# release core-v0.5's card build), plus one rule:
#
#   an argument `nrpic_resume=<path to .rst>` is removed from the command line; if the run
#   directory (the working directory of the job) holds no restart file of its own yet
#   (rst/*.rst), the `-i <deck>` of the chain's first segment is replaced by `-r <path>`.
#   Later segments find their own restart files and pass through unchanged.
#
# Reason: nrpic-run's chain launcher starts a new run directory from a deck; it cannot
# start from another run's restart file, and it passes no variable of the caller.
set -euo pipefail
REAL=${NRPIC_REAL_ATHENA:-/data/haiyangw/nrpic/scratch/F-hills/tmp/binary_conv/exe/bc-ak05-gpu}
if [[ ! -x $REAL ]]; then
  echo "athena_resume_bc: $REAL missing, using the release path" >&2
  REAL=/data/haiyangw/nrpic/.work/build_gpu_v05/src/athena
fi
resume=""
args=()
for a in "$@"; do
  case $a in
    nrpic_resume=*) resume=${a#nrpic_resume=} ;;
    *) args+=("$a") ;;
  esac
done
shopt -s nullglob
own=( rst/*.rst )
if [[ -n $resume ]] && (( ${#own[@]} == 0 )); then
  [[ -r $resume ]] || { echo "athena_resume_bc: $resume not readable" >&2; exit 2; }
  out=()
  skip=0
  for a in "${args[@]}"; do
    if (( skip )); then skip=0; continue; fi
    if [[ $a == -i ]]; then out+=(-r "$resume"); skip=1; continue; fi
    out+=("$a")
  done
  args=("${out[@]}")
  echo "athena_resume_bc: first segment resumes from $resume" >&2
fi
files=( *.co_*.txt )
if (( ${#files[@]} > 0 )); then
  dest="trk_keep/$(date -u +%Y%m%dT%H%M%S.%N)"
  mkdir -p "$dest"
  cp -p "${files[@]}" "$dest/"
  echo "athena_resume_bc: kept ${#files[@]} tracker file(s) in $dest" >&2
fi
exec "$REAL" "${args[@]}"
