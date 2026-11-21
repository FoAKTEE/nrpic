#!/bin/bash
# Test T5 of tracks/core/JOURNAL-scalar2.md: Track E's validations (noise/README.md of
# track/E-stoch-inf) on the outputs of an existing run of analysis/lead/u_runs.py.
#   t5_validate.sh RUNDIR TREE OUTDIR [CARD_U9_DIR]
# RUNDIR  directory with U1 ... U8 (each with its u.athinput)
# TREE    root of a copy of track/E-stoch-inf (tracks/E-stoch-inf/noise/...), with links
#         python -> <worktree>/python and athenak -> <worktree>/athenak; the copy
#         Etree_patched forms the window increment in noise/ref/noise_ref.py without
#         cancellation (window_increment), as the code does
# CARD_U9_DIR  optional: U2 on a card, compared with U2 of RUNDIR (test A14)
set -u
R=$1; T=$2; O=$3; C=${4:-}
V=$T/tracks/E-stoch-inf/noise/validate/validate_noise.py
PY=${PYTHON:-python3}
mkdir -p "$O"
st=0
card=()
[[ -n $C ]] && card=(--card "$C")
$PY $V --input $R/U1/u.athinput --run $R/U1 --blocks8 $R/U2 --blocks64 $R/U3 \
  --restart $R/U4 --res-lo $R/U5a --res-hi $R/U5b --res-lo-input $R/U5a/u.athinput \
  --res-hi-input $R/U5b/u.athinput --seed2 $R/U8 --seed2-input $R/U8/u.athinput \
  "${card[@]}" --tag frozen --out $O/val_frozen > $O/val_frozen.log 2>&1 || st=1
$PY $V --input $R/U6/u.athinput --run $R/U6 --tag markov_tanh --out $O/val_markov_tanh \
  > $O/val_markov_tanh.log 2>&1 || st=1
$PY $V --input $R/U7/u.athinput --run $R/U7 --tag markov_heaviside \
  --out $O/val_markov_heaviside > $O/val_markov_heaviside.log 2>&1 || st=1
for k in frozen markov_tanh markov_heaviside; do
  echo "== $k"; cat $O/val_$k/summary.txt 2>/dev/null || tail -5 $O/val_$k.log
done
exit $st
