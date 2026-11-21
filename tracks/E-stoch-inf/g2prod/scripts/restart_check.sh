#!/usr/bin/env bash
# Restart check of the production deck (package g2prod, prediction R0 of JOURNAL entry 1):
# the USR deck g2prod/inputs/usr_prod.athinput at 32^3 (nmax2 = 16) on the release processor
# build, run A straight to N_f, run B restarted from the restart file of A nearest the middle
# of the run; the final scalar-field dump, its mode file and the last history lines of A and B
# must be byte-identical.
#   restart_check.sh <outdir> <athena executable>
set -euo pipefail
out=$1; exe=$2
wt=/data/haiyangw/nrpic/wt/E-stoch-inf
deck=$wt/tracks/E-stoch-inf/g2prod/inputs/usr_prod.athinput
modes=$wt/tracks/E-stoch-inf/usr/inputs/modes_usr_n16.txt
args=(mesh/nx1=32 mesh/nx2=32 mesh/nx3=32 meshblock/nx1=32 meshblock/nx2=32 meshblock/nx3=32
      scalar_field/noise_nmax2=16 scalar_field/noise_mode_file=$modes)
mkdir -p "$out/A" "$out/B"
(cd "$out/A" && "$exe" -i "$deck" "${args[@]}" > athena.log 2>&1)
mapfile -t rst < <(ls "$out/A"/rst/*.rst 2>/dev/null || ls "$out/A"/*.rst)
echo "restart files of A: ${#rst[@]}"; printf '  %s\n' "${rst[@]}"
mid=${rst[$(( (${#rst[@]} - 1) / 2 ))]}
echo "B restarts from $mid"
(cd "$out/B" && "$exe" -r "$mid" "${args[@]}" > athena.log 2>&1)
status=0
last=$(ls "$out/A"/usr.sf.*.dump | tail -1); last=$(basename "$last")
for f in "$last" "${last%.dump}.modes"; do
  if cmp -s "$out/A/$f" "$out/B/$f"; then echo "IDENTICAL $f"; else echo "DIFFERENT $f"; status=1; fi
done
for h in usr.sf.hst usr.sf.con.hst; do
  if [[ -f $out/A/$h && -f $out/B/$h ]]; then
    if [[ $(tail -1 "$out/A/$h") == "$(tail -1 "$out/B/$h")" ]]; then echo "IDENTICAL last line of $h"
    else echo "DIFFERENT last line of $h"; status=1; fi
  fi
done
echo "verdict: $([[ $status == 0 ]] && echo 'R0 holds' || echo 'R0 REFUTED')"
exit $status
