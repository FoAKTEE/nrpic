#!/bin/bash
# Validations of the noise unit test at the base size (journal 17:05, P1-P5) once the card
# job (U1-U3, U5a, U5b, U6-U8; its U2 is U9) and the processor run (U2, U4) exist.
#   val_base.sh CARD_RUNDIR PROC_RUNDIR OUTDIR [CARD_U4_RUNDIR]
# PROC_RUNDIR "-" skips the processor part (A12, A14); CARD_U4_RUNDIR (U2 of the card job
# restarted on a card at cycle 150) adds A12 on the card.
# frozen: A0-A11, A13, A15 on the card; U6 with the reference as it is and cancellation-free;
# U7; A12 (processor U4 against processor U2) and A14 (card U2 = U9 against processor U2).
set -u
C=$1; P=$2; O=$3
V=tracks/E-stoch-inf/noise/validate/validate_noise.py
S=tracks/E-stoch-inf/analysis/scripts
I=tracks/E-stoch-inf/analysis/inputs/u64
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
mkdir -p "$O"
st=0
python3 $V --input $I/U1.athinput --run $C/U1 --blocks8 $C/U2 --blocks64 $C/U3 \
  --res-lo $C/U5a --res-hi $C/U5b --res-lo-input $I/U5a.athinput --res-hi-input $I/U5b.athinput \
  --seed2 $C/U8 --seed2-input $I/U8.athinput --tag card_frozen --out $O/val_card_frozen \
  > $O/val_card_frozen.log 2>&1 || st=1
python3 $V --input $I/U6.athinput --run $C/U6 --tag card_markov_tanh --out $O/val_card_u6_std \
  > $O/val_card_u6_std.log 2>&1   # A1 expected to fail (reference cancellation, P3)
python3 $S/val_cf.py --input $I/U6.athinput --run $C/U6 --tag card_markov_tanh_cf \
  --out $O/val_card_u6_cf > $O/val_card_u6_cf.log 2>&1 || st=1
python3 $V --input $I/U7.athinput --run $C/U7 --tag card_markov_heaviside --out $O/val_card_u7 \
  > $O/val_card_u7.log 2>&1 || st=1
K=(val_card_frozen val_card_u6_std val_card_u6_cf val_card_u7)
if [[ $P != - ]]; then
  if compgen -G "$P/U4/*.sf.*.dump" > /dev/null; then RST=(--restart $P/U4); else RST=(); fi
  python3 $V --input $I/U2.athinput --run $P/U2 "${RST[@]}" --card $C/U2 --tag proc_u2 \
    --out $O/val_a12_a14 > $O/val_a12_a14.log 2>&1 || st=1
  K+=(val_a12_a14)
fi
if [[ -n ${4:-} ]]; then
  python3 $V --input $I/U2.athinput --run $C/U2 --restart $4 --tag card_u2_restart \
    --out $O/val_card_a12 > $O/val_card_a12.log 2>&1 || st=1
  K+=(val_card_a12)
fi
for k in "${K[@]}"; do
  echo "== $k"; cat $O/$k/summary.txt 2>/dev/null || tail -5 $O/$k.log
done
exit $st
