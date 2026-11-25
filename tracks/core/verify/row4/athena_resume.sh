#!/usr/bin/env bash
# Executable wrapper for a chain that CONTINUES an earlier row-4 run in a new run directory
# (core lead, batch 11, level-3 continuations of the M/8 bisection to 600 M). Modelled on
# Track F's tracks/F-hills/binary_conv/scripts/athena_resume_bc.sh (branch track/F-hills).
#
#   an argument `nrpic_resume=<path to .rst>` is removed from the command line; if the run
#   directory (the job's working directory) holds no restart file of its own yet
#   (rst/*.rst), the `-i <deck>` of the chain's first segment is replaced by `-r <path>`
#   (AthenaK then reads `<path>.prt` for the particles). Later segments find their own
#   restart files and pass through unchanged.
#
# Real executable: the release card build of core-v0.6 (the build that wrote the restart
# files), copied once into chain/ under a name without "athena" so that a kill by name from
# another project (pkill -x athena) does not hit it; the copy is checked against the
# sha256 below before every start.
#
# Reason: nrpic-run's chain launcher starts a new run directory from a deck; it cannot start
# from another run's restart file.
set -euo pipefail
REAL=/data/haiyangw/nrpic/.work/build_gpu_v06/src/athena
SHA=ea473498500f8efc211f5ee9572cd393aad019d035f819f825fe0b79d5114851
here=$(pwd)
copy="$here/chain/nrcr-$(printf %s "$here" | sha256sum | cut -c1-8)"
if [[ ! -x $copy ]]; then
  cp -p "$REAL" "$copy.tmp" && mv "$copy.tmp" "$copy"
fi
got=$(sha256sum "$copy" | cut -d' ' -f1)
if [[ $got != "$SHA" ]]; then
  echo "athena_resume: $copy has sha256 $got, expected $SHA" >&2
  exit 2
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
  [[ -r $resume && -r $resume.prt ]] || { echo "athena_resume: $resume or its .prt not readable" >&2; exit 2; }
  out=()
  skip=0
  for a in "${args[@]}"; do
    if (( skip )); then skip=0; continue; fi
    if [[ $a == -i ]]; then out+=(-r "$resume"); skip=1; continue; fi
    out+=("$a")
  done
  args=("${out[@]}")
  echo "athena_resume: first segment resumes from $resume" >&2
fi
exec "$copy" "${args[@]}"
