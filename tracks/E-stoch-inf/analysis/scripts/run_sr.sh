#!/bin/bash
# Slow-roll scouting runs with the release executable from a homogeneous slice
# (make_sr_case.py), then the analysis (analyse_sr.py).
#   run_sr.sh EXE OUTDIR N [control]
# With "control", a second run with the sign of the Pi kick flipped (noise_pi_sign = -1,
# the negative control P-f of spec/SPEC.md 7.1) is made and analysed alongside.
set -u
EXE=$1; OUT=$2; N=$3; CTL=${4:-}
S=tracks/E-stoch-inf/analysis/scripts
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 $S/make_sr_case.py --N "$N" --out "$OUT/sr$N" > "$OUT/sr$N.case.log" || exit 1
( cd "$OUT/sr$N" && "$EXE" -i sr.athinput > athena.log 2>&1 ) || exit 2
ctl=()
if [[ $CTL == control ]]; then
  python3 $S/make_sr_case.py --N "$N" --pi-sign -1 --out "$OUT/sr${N}ctl" > "$OUT/sr${N}ctl.case.log" || exit 3
  ( cd "$OUT/sr${N}ctl" && "$EXE" -i sr.athinput > athena.log 2>&1 ) || exit 4
  ctl=(--control "$OUT/sr${N}ctl")
fi
python3 $S/analyse_sr.py --run "$OUT/sr$N" --out "$OUT/ana$N" "${ctl[@]}"
