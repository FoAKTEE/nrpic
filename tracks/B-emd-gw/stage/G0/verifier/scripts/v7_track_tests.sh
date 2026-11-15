#!/bin/bash
# Verifier of B-emd-gw: rerun of the tests and scripts the track cites for C1-C3, C7, C8,
# unchanged, into the run directory, then a comparison with the committed results.
#
#   v7_track_tests.sh [OUTDIR]      (default $NRPIC_RUN_DIR)
set -u
OUT=${1:-${NRPIC_RUN_DIR:?no output directory}}
HERE=$(cd "$(dirname "$0")" && pwd)
T=$(cd "$HERE/../../../.." && pwd)            # tracks/B-emd-gw
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
mkdir -p "$OUT/scope" "$OUT/baseline"
echo "== pytest gw_diag, first_source, verify_cosmo" > "$OUT/pytest.txt"
python3 -m pytest -q -p no:cacheprovider "$T/gw_diag/tests" "$T/first_source/tests" \
    "$T/verify_cosmo/scripts/test_zeldovich.py" >> "$OUT/pytest.txt" 2>&1
echo "pytest exit $?" >> "$OUT/pytest.txt"
for s in check_item3 crossed_waves_tt regime_estimates; do
  python3 "$T/scope/scripts/$s.py" "$OUT/scope" > "$OUT/scope/$s.log" 2>&1
  echo "$s exit $?" >> "$OUT/pytest.txt"
done
python3 "$T/baseline/scripts/run_baseline.py" "$OUT/baseline" T1 T2 > "$OUT/baseline/log.txt" 2>&1
echo "run_baseline T1 T2 exit $?" >> "$OUT/pytest.txt"
python3 "$HERE/v7_compare.py" "$T" "$OUT" > "$OUT/compare.txt" 2>&1
echo "compare exit $?" >> "$OUT/pytest.txt"
cat "$OUT/pytest.txt" "$OUT/compare.txt"
