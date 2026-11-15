#!/usr/bin/env bash
# Lead's rerun of three verifier analyses (R10 of ../JOURNAL.md) into the run directory,
# then a leaf-by-leaf comparison of the JSON with the verifier's registered outputs.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
V="$here/../../G0/verifier/scripts"
S=/data/haiyangw/nrpic/scratch/B-emd-gw
out=${1:-$NRPIC_RUN_DIR}
mkdir -p "$out/v2" "$out/v3" "$out/v6"
python3 "$V/v2_crossed.py" "$out/v2" > "$out/v2/stdout.txt"
python3 "$V/v3_junk.py" "$out/v3" > "$out/v3/stdout.txt"
python3 "$V/v6_za_scaling.py" "$out/v6" > "$out/v6/stdout.txt"
python3 "$here/compare_json.py" \
    "$S/B-20261115-165119-efd5ee7/v2_crossed.json" "$out/v2/v2_crossed.json" \
    "$S/B-20261115-165123-9cb1745/v3_junk.json" "$out/v3/v3_junk.json" \
    "$S/B-20261115-170518-c1b61a3/v6_za_scaling.json" "$out/v6/v6_za_scaling.json" \
    | tee "$out/compare.txt"
