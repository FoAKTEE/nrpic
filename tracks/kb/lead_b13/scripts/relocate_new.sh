#!/bin/bash
# Second step of apply_g3.sh (run kb-20261124-233445-89478ae failed only on these three: relocate needs --by).
cd /data/haiyangw/nrpic/wt/kb || exit 2
KB="python3 -I kb/bin/kb"; BY=kb-lead-b13; fail=0
$KB claim relocate 862 --by $BY --locator '1305.2619v1:SFWpaper.tex:L443' || fail=1
$KB claim relocate 863 --by $BY --locator '2611.12831v1:main.tex:L867; 2611.12831v1:main.tex:L877; 2611.12831v1:main.tex:L1142' || fail=1
$KB claim relocate 864 --by $BY --locator '2602.06961v1:apssamp.tex:L77-85; 2610.20594v1:apssamp.tex:L79-88; 2610.20594v1:apssamp.tex:L1469' || fail=1
for c in 682 781 714 809 804 409 447 449 450 452 862 863 864; do $KB claim show "$c" | python3 -I -c 'import json,sys; d=json.load(sys.stdin); print(d["claim_id"], d["label"], d["status"], sum(1 for l in d.get("locators",[]) if l.get("resolved")), len(d.get("locators",[])), sep="\t")'; done > "${NRPIC_RUN_DIR:-.}/after.tsv"
cat "${NRPIC_RUN_DIR:-.}/after.tsv"
$KB claim stats > "${NRPIC_RUN_DIR:-.}/stats.txt" 2>&1
exit $fail
