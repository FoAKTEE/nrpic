#!/bin/bash
# Validations of noise/README.md on the outputs of an existing L-U run (u_runs.py), with
# each run's own input file (U5a/U5b have their own nmax2).
#   lu_validate.sh RUNDIR OUTDIR
set -u
R=$1; O=$2
V=tracks/E-stoch-inf/noise/validate/validate_noise.py
mkdir -p "$O"
st=0
python3 $V --input $R/U1/u.athinput --run $R/U1 --blocks8 $R/U2 --blocks64 $R/U3 \
  --restart $R/U4 --res-lo $R/U5a --res-hi $R/U5b --res-lo-input $R/U5a/u.athinput \
  --res-hi-input $R/U5b/u.athinput --seed2 $R/U8 --seed2-input $R/U8/u.athinput \
  --out $O/val_frozen > $O/val_frozen.log 2>&1 || st=1
python3 $V --input $R/U6/u.athinput --run $R/U6 --tag markov_tanh --out $O/val_markov_tanh > $O/val_markov_tanh.log 2>&1 || st=1
python3 $V --input $R/U7/u.athinput --run $R/U7 --tag markov_heaviside --out $O/val_markov_heaviside > $O/val_markov_heaviside.log 2>&1 || st=1
for k in frozen markov_tanh markov_heaviside; do echo "== $k"; cat $O/val_$k/summary.txt; done
exit $st
