#!/bin/bash
# U6 (Markov scheme, tanh window) of the lead's scaled base case (N = 32, 120 steps) with
# the release processor executable, validated twice: with the track's reference as it is
# and with the cancellation-free increment (val_cf.py). Prediction P3 (journal).
#   u6_scaled.sh EXE OUTDIR
set -u
EXE=$1; OUT=$2
S=tracks/E-stoch-inf/analysis/scripts
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
mkdir -p "$OUT/U6s"
python3 - "$OUT/U6s/u.athinput" <<'PY'
import re, sys
s = open("tracks/E-stoch-inf/analysis/lead/inputs/u_base32.athinput").read()
s = re.sub(r"(noise_scheme\s*=\s*)frozen", r"\1markov", s)
open(sys.argv[1], "w").write(s)
PY
( cd "$OUT/U6s" && "$EXE" -i u.athinput > athena.log 2>&1 ) || exit 1
V=tracks/E-stoch-inf/noise/validate/validate_noise.py
python3 $V --input "$OUT/U6s/u.athinput" --run "$OUT/U6s" --tag markov_tanh --out "$OUT/val_std" > "$OUT/val_std.log" 2>&1
python3 $S/val_cf.py --input "$OUT/U6s/u.athinput" --run "$OUT/U6s" --tag markov_tanh_cf --out "$OUT/val_cf" > "$OUT/val_cf.log" 2>&1
st=$?
echo "== reference as it is"; cat "$OUT/val_std/summary.txt"
echo "== cancellation-free reference"; cat "$OUT/val_cf/summary.txt"
exit $st
