#!/usr/bin/env bash
# Register and submit the continuation of one or more cut runs of the reproduction
# (package repro/continue, Track E). For each LABEL of scripts/runs.json:
#   harness/bin/nrpic-run submit --launcher chain --gpu-hours ${GPU_HOURS:-1} (one segment)
#     --exe scripts/athena_resume.sh  (wrapper: first segment -r <original newest restart>)
#     --input <byte copy of the original executable> --input <restart> --input <restart>.sf
#     --parent <original run> -- <original deck> <original overrides>
#     nrpic_exe=<byte copy> nrpic_resume=<restart>
# RST=<file name> picks another restart of the original than the one in runs.json, and
# FROM=<run id> continues from that run's directory instead of the original's (a second
# continuation after a preemption: FROM=<first continuation>, RST=<its newest restart>).
# DRY=1 passes --dry-run (prints the manifest, registers and starts nothing).
#
#   tracks/E-stoch-inf/repro/continue/scripts/submit_continue.sh LABEL [LABEL...]
set -euo pipefail
WT=/data/haiyangw/nrpic/wt/E-stoch-inf
PKG=tracks/E-stoch-inf/repro/continue
SCR=/data/haiyangw/nrpic/scratch/E-stoch-inf
cd "$WT"
for lab in "$@"; do
  mapfile -t f < <(python3 -I - "$PKG/scripts/runs.json" "$lab" <<'EOF'
import json, sys
r = json.load(open(sys.argv[1]))[sys.argv[2]]
for k in ("orig", "rst", "deck", "exe_copy", "exe_sha256", "purpose", "package"):
    print(r[k])
print("\x1f".join(r["args"]))
EOF
)
  orig=${f[0]}; rst=${RST:-${f[1]}}; deck=${f[2]}; exe=${f[3]}; sha=${f[4]}; what=${f[5]}; pkg=${f[6]}
  IFS=$'\x1f' read -r -a extra <<< "${f[7]}"
  src=${FROM:-$orig}
  rstp=$SCR/$src/rst/$rst
  [[ -r $rstp && -r $rstp.sf ]] || { echo "missing $rstp or its .sf" >&2; exit 1; }
  got=$(sha256sum "$exe" | cut -d' ' -f1)
  [[ $got == "$sha" ]] || { echo "$exe: sha256 $got, expected $sha" >&2; exit 1; }
  parents=(--parent "$orig")
  [[ $src != "$orig" ]] && parents+=(--parent "$src")
  dry=(); [[ ${DRY:-0} == 1 ]] && dry=(--dry-run)
  harness/bin/nrpic-run submit "${dry[@]}" --kind production --gate G2 --launcher chain \
    --gpu-hours "${GPU_HOURS:-1}" --package "$PKG" \
    --exe "$PKG/scripts/athena_resume.sh" \
    --input "$exe" --input "$rstp" --input "$rstp.sf" "${parents[@]}" \
    --preregistered "$PKG/JOURNAL.md#entry-1" \
    --notes "continuation of $src from rst/$rst (wrapper scripts/athena_resume.sh: first segment -r that file); read with $orig as one run (repro/continue/HANDOFF.md)" \
    --purpose "repro/continue $lab: $orig ($pkg) continued from its restart $rst to tlim; $what; same executable (byte copy $(basename "$exe"), sha256 ${sha:0:8}), deck and overrides; predictions repro/continue/JOURNAL.md entry 1 and those of the original" \
    -- "$deck" "${extra[@]}" "nrpic_exe=$exe" "nrpic_resume=$rstp"
done
