#!/usr/bin/env bash
# V6 and V7 of the G0 verifier: runs of the release processor executable (core-v0.3) on
# core's own deck problems/scalar/noise_ms.athinput (Mukhanov-Sasaki model with kicks of
# Pi, Khat and At and the field coupled to Z4c), with command-line overrides only.
#   V6  N = 32, nmax2 = 64 (k_max = N/4 as in production), dump every 13 cycles:
#       B32 one MeshBlock 32^3; B16 eight 16^3; B3216 four 32x16x16; RST restart of B16 from
#       its restart file of cycle 13; NEG B16 with noise_pi_sign = -1 (negative control);
#       CONT B16 with the continuum projector.
#   V7  timing, 12 cycles: T0 noise none; T64 MS nmax2 = 64 one MeshBlock; T225 MS nmax2 = 225
#       one MeshBlock; T225b8 MS nmax2 = 225 with 64 MeshBlocks of 8^3; T0b8 noise none, 8^3.
# Usage: v6_athenak.sh <athena executable> <output directory>
set -euo pipefail
EXE=$1
OUT=$2
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../../../.." && pwd)
DECK=$ROOT/problems/scalar/noise_ms.athinput
PY=$ROOT/.venv/bin/python
export OMP_NUM_THREADS=1
mkdir -p "$OUT"
"$PY" "$HERE/v6_modefile.py" "$OUT/modes.txt"
# core's deck with one added key (AthenaK refuses command-line keys the deck lacks)
sed 's/^dump_dt *= *2.0/dump_dt         = -1.0\ndump_dcycle     = 13/' "$DECK" > "$OUT/noise_ms_v6.athinput"
grep -q '^dump_dcycle' "$OUT/noise_ms_v6.athinput"
DECK=$OUT/noise_ms_v6.athinput
COMMON=(mesh/nx1=32 mesh/nx2=32 mesh/nx3=32 scalar_field/noise_mode_file="$OUT/modes.txt"
        time/tlim=4.0 output1/dcycle=13)
run() {   # name, extra overrides...
  local name=$1; shift
  mkdir -p "$OUT/$name"
  ( cd "$OUT/$name" && "$EXE" -i "$DECK" "${COMMON[@]}" "$@" > athena.log 2>&1 )
  echo "$name done: $(grep -h 'zone-cycles/cpu_second' "$OUT/$name/athena.log" || true)"
}
run B32 meshblock/nx1=32 meshblock/nx2=32 meshblock/nx3=32 scalar_field/noise_nmax2=64 &
run B16 meshblock/nx1=16 meshblock/nx2=16 meshblock/nx3=16 scalar_field/noise_nmax2=64 &
run B3216 meshblock/nx1=32 meshblock/nx2=16 meshblock/nx3=16 scalar_field/noise_nmax2=64 &
run NEG meshblock/nx1=16 meshblock/nx2=16 meshblock/nx3=16 scalar_field/noise_nmax2=64 \
    scalar_field/noise_pi_sign=-1.0 &
run CONT meshblock/nx1=16 meshblock/nx2=16 meshblock/nx3=16 scalar_field/noise_nmax2=64 \
    scalar_field/noise_projector=continuum &
wait
# restart of B16 from the restart file of cycle 13
RSTF=$(ls "$OUT"/B16/rst/*.00001.rst)
mkdir -p "$OUT/RST"
( cd "$OUT/RST" && "$EXE" -r "$RSTF" scalar_field/noise_mode_file="$OUT/modes.txt" > athena.log 2>&1 )
echo "RST done: $(grep -h 'zone-cycles/cpu_second' "$OUT/RST/athena.log" || true)"
# V7 timing (12 cycles)
T=(time/nlim=12 time/tlim=100 output1/dcycle=1000 scalar_field/dump_dcycle=0)
run T0 meshblock/nx1=32 meshblock/nx2=32 meshblock/nx3=32 scalar_field/noise=none \
    scalar_field/noise_nmax2=64 "${T[@]}" &
run T64 meshblock/nx1=32 meshblock/nx2=32 meshblock/nx3=32 scalar_field/noise_nmax2=64 "${T[@]}" &
run T225 meshblock/nx1=32 meshblock/nx2=32 meshblock/nx3=32 scalar_field/noise_nmax2=225 "${T[@]}" &
run T225b8 meshblock/nx1=8 meshblock/nx2=8 meshblock/nx3=8 scalar_field/noise_nmax2=225 "${T[@]}" &
run T0b8 meshblock/nx1=8 meshblock/nx2=8 meshblock/nx3=8 scalar_field/noise=none \
    scalar_field/noise_nmax2=225 "${T[@]}" &
wait
"$PY" "$HERE/v6_compare.py" "$OUT"
