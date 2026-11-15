#!/bin/bash
# Lead's wave-2 re-check of the note package (JOURNAL.md, prediction W10).
# In $NRPIC_RUN_DIR: (1) compile a clean copy of tracks/D-bh-dress/note (tracked files only)
# with latexmk and count the pages; (2) rerun note/scripts/ledger.py into a fresh tables/
# directory next to a copy of the committed figures/*_numbers.json and compare with the
# committed tables byte for byte; (3) print three ledger numbers next to the run outputs
# they cite (drift, wall radius, spike peak).
set -euo pipefail
OUT="${NRPIC_RUN_DIR:?}"
WT=/data/haiyangw/nrpic/wt/D-bh-dress
NOTE=$WT/tracks/D-bh-dress/note
SCR=/data/haiyangw/nrpic/scratch/D-bh-dress
mkdir -p "$OUT/note" "$OUT/ledger/figures" "$OUT/ledger/tables"
cd "$WT"
git ls-files tracks/D-bh-dress/note | while read -r f; do
  rel="${f#tracks/D-bh-dress/note/}"
  mkdir -p "$OUT/note/$(dirname "$rel")"
  cp "$f" "$OUT/note/$rel"
done
cp "$WT/tracks/D-bh-dress/WRITING_GUIDE.md" "$WT/tracks/D-bh-dress/NOTATION.md" "$OUT/"
rm -f "$OUT/note/main.pdf"
(cd "$OUT/note" && latexmk -pdf -interaction=nonstopmode main.tex > "$OUT/latexmk.log" 2>&1) || echo "latexmk exit $?"
echo "pages: $(pdfinfo "$OUT/note/main.pdf" | awk '/^Pages/ {print $2}')"
echo "undefined refs/citations: $(grep -c -i 'undefined' "$OUT/note/main.log" || true)"
echo "overfull boxes: $(grep -c 'Overfull' "$OUT/note/main.log" || true)"
cp "$NOTE"/figures/fig_*_numbers.json "$OUT/ledger/figures/"
"$WT/.venv/bin/python" "$NOTE/scripts/ledger.py" --out "$OUT/ledger/tables" > "$OUT/ledger.log" 2>&1
for t in ledger.tex parameters.tex claims.md claims.json; do
  if cmp -s "$OUT/ledger/tables/$t" "$NOTE/tables/$t"; then echo "$t: identical"; else echo "$t: DIFFERS"; diff "$OUT/ledger/tables/$t" "$NOTE/tables/$t" | head -20; fi
done
echo "--- ledger: drift, wall, spike peak"
grep -n "drift of the \$20M\$ mean\|wall radius at\|constant \$f\$: peak density" "$NOTE/tables/ledger.tex" | cut -c1-160
echo "--- run outputs"
python3 -I -c "
import json
d=json.load(open('$SCR/D-bh-dress-20261115-145546-5259f48/lead_drift_recheck.json')); print('drift recheck:', json.dumps(d)[:600])
p=json.load(open('$SCR/D-bh-dress-20261115-145950-23fa1c7/first_run_plan.json')); print('first_run_plan keys:', list(p)[:30])
r=json.load(open('$SCR/D-bh-dress-20261115-145636-5259f48/reference.json')); print('spike reference:', json.dumps(r)[:600])
"
