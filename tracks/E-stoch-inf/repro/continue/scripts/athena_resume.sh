#!/usr/bin/env bash
# Executable wrapper for a chain (scripts/submit_chain.sh, through harness/bin/nrpic-run
# --launcher chain --exe <this file>) that CONTINUES an earlier run in a new run directory
# from that run's restart file (package repro/continue of Track E, batch R2, 2026-11-24;
# after tracks/F-hills/binary_conv/scripts/athena_resume_bc.sh on branch track/F-hills).
#
# Two arguments of the chain's command line are consumed here and never reach AthenaK:
#   nrpic_exe=<path>     the real card executable to exec (a byte copy of the original
#                        run's executable under a name without "athena", so that a kill by
#                        name from another project, `pkill -x athena`, does not hit it)
#   nrpic_resume=<path>  the original run's restart file (<name>.NNNNN.rst; the scalar
#                        field reads <path>.sf beside it)
# Rule: while the run directory (the working directory of the job, set by
# scripts/_athena_job.sh) holds no restart file of its own (rst/*.rst), the `-i <deck>`
# that the chain passes to its first segment is replaced by `-r <nrpic_resume>`. Once the
# continuation has written a restart file of its own, the chain passes `-r <own newest>`
# and the arguments go through unchanged. Every other argument (the parameter overrides of
# the original run, `-d`, `-t`) is passed as given.
#
# Reason: nrpic-run's chain launcher starts a new run directory from a deck; it cannot
# start from another run's restart file (decision 0026 item 7 asks for that option).
set -euo pipefail
real=""
resume=""
args=()
for a in "$@"; do
  case $a in
    nrpic_exe=*)    real=${a#nrpic_exe=} ;;
    nrpic_resume=*) resume=${a#nrpic_resume=} ;;
    *)              args+=("$a") ;;
  esac
done
[[ -n $real && -x $real ]] || { echo "athena_resume: nrpic_exe='$real' is not executable" >&2; exit 2; }
shopt -s nullglob
own=( rst/*.rst )
if [[ -n $resume ]] && (( ${#own[@]} == 0 )); then
  [[ -r $resume ]] || { echo "athena_resume: $resume not readable" >&2; exit 2; }
  [[ -r $resume.sf ]] || { echo "athena_resume: $resume.sf not readable" >&2; exit 2; }
  out=()
  skip=0
  for a in "${args[@]}"; do
    if (( skip )); then skip=0; continue; fi
    if [[ $a == -i ]]; then out+=(-r "$resume"); skip=1; continue; fi
    out+=("$a")
  done
  args=("${out[@]}")
  echo "athena_resume: first segment resumes from $resume" >&2
else
  echo "athena_resume: own restart file present (${#own[@]}), arguments unchanged" >&2
fi
echo "athena_resume: exec $real ${args[*]}" >&2
exec "$real" "${args[@]}"
