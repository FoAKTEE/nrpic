#!/usr/bin/env bash
# Continue a cut row-4 chain IN PLACE from its own newest restart file, through the shared
# card queue (decision 0033; harness/RULES.md, section "Shared card queue"). Core lead,
# batch 12 (2026-11-24): level 3 of the M/8 bisection, run core-20261124-130310-597d9ca.
#
#   tracks/core/verify/row4/continue_chain.sh <run_id> [max_segments]
#
# Given to `harness/bin/nrpic-queue add --label L --cmd '...'`. The dispatcher runs the line
# with bash in the worktree root, with its marker (NRPIC_QUEUE_DISPATCH) and the submit lock
# held. It submits AT MOST ONE job: it repeats the chain's start command on the run's own
# directory,
#     scripts/submit_chain.sh <rundir> <deck> <the run's overrides>
# which resumes from the newest rst/*.rst there, with the settings the chain was started with
# (chain/config.sh: the executable EXE_SRC it copies again, JOB_NAME = the run id, so the
# queue knows the chain's jobs by name; PROC_NAME, ATHENA_WALL, SLURM_TIME, CPUS, PARTITION,
# MAX_OUTSIDE_KILLS, SLURM_EXTRA, CHECK_CMD) and MAX_SEGMENTS = max_segments (default: the
# cap the run was registered with, resources.segments_max of its manifest). The segment
# counter chain/segment goes on, so the card-hours stay inside what the run asked for.
#
# Checks, each fatal before anything is submitted: the manifest exists, is unfinished
# (status submitted) and its launcher is chain; its command is submit_chain.sh on this run
# directory; the chain is not DONE, has no job in squeue, and has a restart file of its own
# with its .prt (without one there is nothing to continue: register a new run); the deck's
# sha256 is the manifest's; EXE_SRC has the sha256 the manifest recorded for the executable;
# JOB_NAME and the overrides of config.sh are those of the manifest; a segment is left.
#
# Outside a dispatch (`harness/bin/nrpic-queue check-dispatch` fails) it refuses (exit 3);
# DRY=1 prints what it would run and submits nothing (with or without the marker). The continuation is recorded in
# <rundir>/chain/continuations.log (time, queue entry, wrapper sha256, restart, segments);
# submit_chain.sh writes "start/resume" and "submitted job N" into chain/events.log, from
# which `nrpic-run finish <run_id>` collects every job id and the card-hours.
set -euo pipefail

die() { echo "continue_chain: $1" >&2; exit "${2:-1}"; }
[[ $# -ge 1 && $# -le 2 ]] || die "usage: continue_chain.sh <run_id> [max_segments]"
run=$1
[[ $run =~ ^core-[0-9]{8}-[0-9]{6}-[0-9a-f]{7}$ ]] || die "not a run id of core: $run"
WT=$(cd "$(dirname "${BASH_SOURCE[0]}")" && git rev-parse --show-toplevel)
cd "$WT"
man=tracks/core/runs/$run/manifest.json
[[ -f $man ]] || die "no manifest $man"

# manifest fields, one per line (python3 -I: standard library only)
mapfile -t f < <(python3 -I - "$man" <<'EOF'
import json, sys
m = json.load(open(sys.argv[1]))
cmd = m.get("command") or []
exe = (m.get("code") or {}).get("exe_sha256") or ""
print(m.get("status", ""))
print(m.get("launcher", ""))
print((m.get("input") or {}).get("sha256", ""))
print(exe)
print((m.get("resources") or {}).get("segments_max") or "")
print(cmd[0] if len(cmd) > 0 else "")
print(cmd[1] if len(cmd) > 1 else "")
print(cmd[2] if len(cmd) > 2 else "")
print("\x1f".join(cmd[3:]))
EOF
)
status=${f[0]}; launcher=${f[1]}; deck_sha=${f[2]}; exe_sha=${f[3]}; segmax=${f[4]}
c0=${f[5]}; rundir=${f[6]}; deck=${f[7]}
IFS=$'\x1f' read -r -a over <<< "${f[8]}"
[[ $status == submitted ]] || die "$run: manifest status is '$status', not submitted (a finished run is not continued)"
[[ $launcher == chain ]] || die "$run: launcher '$launcher', not chain"
[[ $c0 == scripts/submit_chain.sh ]] || die "$run: manifest command does not start with scripts/submit_chain.sh"
[[ $rundir == /data/haiyangw/nrpic/scratch/core/$run ]] || die "$run: run directory '$rundir' is not scratch/core/$run"
C=$rundir/chain
[[ -f $C/config.sh ]] || die "$run: no $C/config.sh"
max=${2:-$segmax}
[[ $max =~ ^[1-9][0-9]*$ ]] || die "$run: max_segments '$max' is not a positive integer"

[[ $(cat "$C/STATUS" 2>/dev/null) != DONE ]] || die "$run: chain is DONE"
# every job of the account (squeue -j of a job Slurm has forgotten exits non-zero)
sq=$(squeue -h -u "$(id -un)" -o '%i %j %T') || die "$run: squeue did not answer"
jid=$(cat "$C/jobid" 2>/dev/null || true)
q=$(awk -v j="$jid" -v n="$run" '$1 == j || $2 == n' <<< "$sq")
[[ -z $q ]] || die "$run: a job of it is still in squeue: $q"
rst=$(find "$rundir/rst" -maxdepth 1 -name '*.rst' -printf '%T@ %p\n' 2>/dev/null |
      sort -k1,1gr -k2,2r | head -1 | cut -d' ' -f2-)
[[ -n $rst ]] || die "$run: no restart file of its own in $rundir/rst: register a new run instead"
[[ -r $rst.prt ]] || die "$run: $rst has no $rst.prt (particles)"

got=$(sha256sum "$deck" | cut -d' ' -f1)
[[ $got == "$deck_sha" ]] || die "$run: deck $deck has sha256 $got, manifest $deck_sha"

# the chain's own settings (sourced in this shell only; nothing is exported)
# shellcheck source=/dev/null
source "$C/config.sh"
[[ ${JOB_NAME:-} == "$run" ]] || die "$run: chain JOB_NAME '${JOB_NAME:-}' is not the run id"
[[ "${EXTRA_ARGS[*]}" == "${over[*]}" ]] || die "$run: overrides of config.sh differ from the manifest's command"
got=$(sha256sum "$EXE_SRC" | cut -d' ' -f1)
[[ $got == "$exe_sha" ]] || die "$run: executable $EXE_SRC has sha256 $got, manifest $exe_sha"
seg=$(cat "$C/segment" 2>/dev/null || echo 0)
(( seg < max )) || die "$run: $seg segments used, MAX_SEGMENTS $max: none left"

cmd=(env "ATHENA_EXE=$EXE_SRC" "JOB_NAME=$run" "MAX_SEGMENTS=$max" "PROC_NAME=$PROC_NAME"
     "ATHENA_WALL=$ATHENA_WALL" "SLURM_TIME=$SLURM_TIME" "CPUS=$CPUS" "PARTITION=$PARTITION"
     "MAX_OUTSIDE_KILLS=${MAX_OUTSIDE_KILLS:-2}" "SLURM_EXTRA=$SLURM_EXTRA" "CHECK_CMD=$CHECK_CMD"
     scripts/submit_chain.sh "$rundir" "$deck" "${EXTRA_ARGS[@]}")
echo "continue_chain: $run resumes in place from $rst ($seg of $max segments used, $((max - seg)) left)"
if [[ ${DRY:-0} == 1 ]]; then
  printf 'continue_chain: DRY, would run:'; printf ' %q' "${cmd[@]}"; echo
  exit 0
fi
# the marker alone proves nothing (harness/RULES.md, nrpic-run section): the queue checks it
# (entry being dispatched with that token, this worktree, submit lock held). scripts/
# removes the marker from the environment of every job it submits (decision 0037 item 4).
"$WT/harness/bin/nrpic-queue" check-dispatch >&2 ||
  die "refused: not inside a dispatch of the shared queue (decision 0033); DRY=1 shows the command" 3

wsha=$(sha256sum "${BASH_SOURCE[0]}" | cut -d' ' -f1)
printf '%s queue-entry=%s wrapper=%s sha256=%s restart=%s segments_used=%s max_segments=%s\n' \
  "$(date -u +%FT%TZ)" "${NRPIC_QUEUE_DISPATCH%%:*}" "tracks/core/verify/row4/continue_chain.sh" \
  "$wsha" "$rst" "$seg" "$max" >> "$C/continuations.log"
exec "${cmd[@]}"
