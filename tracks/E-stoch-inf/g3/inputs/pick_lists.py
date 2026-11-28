#!/usr/bin/env python3
"""Write the batch lists of the G3 members still missing after the preemptions of 2026-11-27 (jobs 5537, 5541,
5546, 5552, 5558; queue audit of decision 0048 item 9; g3/JOURNAL.md entry 19). Every run line is COPIED UNCHANGED,
by its label, from the list that held it before (base07, base10, base11, l2_01); nothing is generated anew, so
seed, sign, deck, overrides and executable stay those of SCOPE 4d. l2_00.list (level-2 pairs 0-4 with k000, k001)
is queued as it stands and is not rewritten here. Run from the worktree root:
    python3 tracks/E-stoch-inf/g3/inputs/pick_lists.py
then python3 tracks/E-stoch-inf/g3/check_lists.py on every list it wrote."""
import os

D = "tracks/E-stoch-inf/g3/inputs"


def lines_of(name):
    out = {}
    for ln in open(os.path.join(D, name)):
        if ln.startswith("#") or not ln.strip():
            continue
        out[ln.split()[0]] = ln if ln.endswith("\n") else ln + "\n"
    return out


SRC = {}
for n in ("base07.list", "base10.list", "base11.list", "l2_01.list"):
    for lab, ln in lines_of(n).items():
        assert lab not in SRC, lab
        SRC[lab] = ln


def pairs(rng, pre=""):
    out = []
    for i in rng:
        out += [f"{pre}p{i:03d}", f"{pre}m{i:03d}"]
    return out


HEAD = ("# {what}. Lines copied unchanged by label from base07/base10/base11/l2_01 (pick_lists.py) after the\n"
        "# preemptions of 2026-11-27 (g3/JOURNAL.md entry 19); release card build core-v0.7 as SCOPE 4d fixes.\n"
        "# Predictions: g3/JOURNAL.md entries 2, 4, 6, 14 and 19.\n")

lists = {
    "base12.list": ("Baseline job 12: m077 (lost in job 5537), mirrored pairs 78-81 and 105, 11 runs",
                    ["m077"] + pairs(range(78, 82)) + pairs(range(105, 106))),
    "base13.list": ("Baseline job 13: mirrored pairs 106-111, 12 runs", pairs(range(106, 112))),
    "base14.list": ("Baseline job 14: mirrored pairs 112-114 and 117-119, 12 runs",
                    pairs(range(112, 115)) + pairs(range(117, 120))),
    "base15.list": ("Baseline job 15: mirrored pairs 120-125, 12 runs", pairs(range(120, 126))),
    "l2_04.list": ("Level 2 job 4: lm005 (lp005 finished in job 5558) and level-2 mirrored pairs 6-10, 11 runs",
                   ["lm005"] + pairs(range(6, 11), "l")),
}
for name, (what, labels) in lists.items():
    p = os.path.join(D, name)
    with open(p, "w") as f:
        f.write(HEAD.format(what=what) + "".join(SRC[lab] for lab in labels))
    print(p, len(labels), labels[0], "...", labels[-1])
