#!/usr/bin/env bash
# Self-test of join_check.py on a synthetic split of a COMPLETED run (package repro/continue).
# The completed run AL0S (E-20261123-153347-18e7c21, 1386 cycles, restart sr256_l0m.00003.rst
# at cycle 978) is cut into a fake "original" (records up to cycle 1015 of its last segment,
# dumps 00000-00012, the restart file) and a fake "continuation" (records from cycle 979, no
# header; dumps 00012-00017; the segment log lines from cycle 980; launch.json naming the
# restart), all by symbolic links or copies of text lines. Since both halves are the same
# run, join_check.py must report J1-J4 true, the overlap 979-1015 identical, the junction
# ratio below 3 and joined records equal to the completed run's own record (checked here).
#
#   join_selftest.sh OUTDIR
set -euo pipefail
OUT=$1
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
S=/data/haiyangw/nrpic/scratch/E-stoch-inf/E-20261123-153347-18e7c21
B=sr256_l0m
T=$OUT/jtest
mkdir -p "$T/ORIG/rst" "$T/CONT/chain" "$T/CONT/.nrpic" "$T/out"
for k in sf.hst sf.con.hst; do
  # original: everything up to the first line of cycle 1016 in the last block
  awk '/^#/ {print; next} {c=$2+0; if (seen && c==1016) exit; if (c<prev) seen=1; prev=c; print}' \
      "$S/$B.$k" > "$T/ORIG/$B.$k"
  # continuation: the last block from cycle 979 on, no header
  awk '/^#/ {next} {c=$2+0; if (c<prev) blk++; prev=c; if (blk>=1 && c>=979) print}' \
      "$S/$B.$k" > "$T/CONT/$B.$k"
done
for n in 00000 00001 00002 00003 00004 00005 00006 00007 00008 00009 00010 00011 00012; do
  ln -sf "$S/$B.sf.$n.dump" "$T/ORIG/$B.sf.$n.dump"
  [[ -e $S/$B.sf.$n.modes ]] && ln -sf "$S/$B.sf.$n.modes" "$T/ORIG/$B.sf.$n.modes"
done
for n in 00012 00013 00014 00015 00016 00017; do
  ln -sf "$S/$B.sf.$n.dump" "$T/CONT/$B.sf.$n.dump"
  [[ -e $S/$B.sf.$n.modes ]] && ln -sf "$S/$B.sf.$n.modes" "$T/CONT/$B.sf.$n.modes"
done
ln -sf "$S/rst/$B.00003.rst" "$T/ORIG/rst/$B.00003.rst"
ln -sf "$S/rst/$B.00003.rst.sf" "$T/ORIG/rst/$B.00003.rst.sf"
awk '/^#/ {print; next} /^elapsed=/ {split($2,a,"="); if (a[2]+0 >= 980) print; next} {print}' \
    "$S/chain/seg002.job5011.a1.log" > "$T/CONT/chain/seg001.job0.a1.log"
printf '{"argv": ["scripts/submit_chain.sh", "x", "deck", "nrpic_resume=%s"]}\n' \
    "$T/ORIG/rst/$B.00003.rst" > "$T/CONT/.nrpic/launch.json"
printf '{"TEST": {"orig": "ORIG", "base": "%s"}}\n' "$B" > "$T/runs.json"
printf '{"TEST": ["CONT"]}\n' > "$T/conts.json"
python3 "$HERE/join_check.py" --scratch "$T" --runs "$T/runs.json" --conts "$T/conts.json" --out "$T/out"
# the joined records must equal the completed run's own record after the same rule
for k in sf.hst sf.con.hst; do
  python3 - "$S/$B.$k" "$T/out/TEST.$k" <<'EOF'
import sys
def latest(p):
    d, head = {}, []
    for l in open(p):
        if l.startswith('#'):
            head.append(l); continue
        d[int(l.split()[1])] = l
    return head, d
h0, a = latest(sys.argv[1]); h1, b = latest(sys.argv[2])
ok = a == b and h0 == h1
print(sys.argv[2], "equal to the completed run's record:", ok, len(a), len(b))
sys.exit(0 if ok else 1)
EOF
done
python3 - "$T/out/join_check.json" <<'EOF'
import json, sys
e = json.load(open(sys.argv[1]))["TEST"]
ok = e["J1_pass"] and e["J2_pass"] and e["J3_pass"] and e["J4_pass"]
print("self-test J1-J4:", e["J1_pass"], e["J2_pass"], e["J3_pass"], e["J4_pass"], "->", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
EOF
cp "$T/out/fig_join.png" "$T/out/fig_join.pdf" "$OUT/"
