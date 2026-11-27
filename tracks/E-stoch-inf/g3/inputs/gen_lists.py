#!/usr/bin/env python3
"""Write the batch lists of the G3 baseline and level-2 pairs that remain after the preemptions of
2026-11-26 18:04 PST (job 5419, G3B06: m071, pairs 72-73 lost) and 18:07 PST (job 5420, G3L00: nothing ran).
The run line is the one of base06.list (baseline) and l2_00.list (level 2) with the seed and sign changed;
nothing else differs (g3/JOURNAL.md entry 14). Run from the worktree root:
    python3 tracks/E-stoch-inf/g3/inputs/gen_lists.py
then python3 tracks/E-stoch-inf/g3/check_lists.py on every list it wrote."""
import os

D = "tracks/E-stoch-inf/g3/inputs"
DECK = "tracks/E-stoch-inf/g2prod/inputs/usr_prod.athinput"
MODES = "/data/haiyangw/nrpic/wt/E-stoch-inf/tracks/E-stoch-inf/usr/inputs/modes_usr_n1024.txt"
COMMON = ("mesh/nx1=128 mesh/nx2=128 mesh/nx3=128 meshblock/nx1=128 meshblock/nx2=128 meshblock/nx3=128 "
          "scalar_field/noise_nmax2=1024 scalar_field/noise_mode_file=" + MODES)
TAIL = "scalar_field/dump_dt=10.437508874065651 output1/dt=100.0 scalar_field/dump_constraints=false"


def line(label, i, sign, level2=False):
    s = "1.0" if sign > 0 else "-1.0"
    extra = " scalar_field/noise_level=2" if level2 else ""
    return (f"{label} {DECK} {COMMON} scalar_field/noise_mode_scale={s} job/rng_seed={20262000 + i} "
            f"{TAIL}{extra}\n")


def base_pairs(pairs):
    out = []
    for i in pairs:
        out += [line(f"p{i:03d}", i, +1), line(f"m{i:03d}", i, -1)]
    return out


def l2_pairs(pairs):
    out = []
    for i in pairs:
        out += [line(f"lp{i:03d}", i, +1, True), line(f"lm{i:03d}", i, -1, True)]
    return out


HEAD_B = ("# Baseline of SCOPE 4d.9 A5, {what}; 128^3, nmax2 = 1024, dumps at t = 0 and tlim without constraint\n"
          "# fields, release card build core-v0.7 as SCOPE 4d (common set-up) fixes. Written by gen_lists.py after the\n"
          "# preemption of job 5419 (G3B06). Predictions: g3/JOURNAL.md entries 2 (G3P-2), 4 (V, T), 6 (C6-1, C6-3), 14.\n")
HEAD_L = ("# Level 2 of SCOPE 4d.7 with 4d.9 A11, {what}; noise_level = 2 (mesh mode by default), the same seeds and\n"
          "# modes as the baseline pairs. Written by gen_lists.py after the preemption of job 5420 (G3L00).\n"
          "# Predictions: g3/JOURNAL.md entries 2 (G3-L2), 6 (C6-2, C6-4), 14.\n")

lists = {
    "base07.list": (HEAD_B.format(what="job 7: m071 (lost in job 5419) and mirrored pairs 72-81, 21 runs"),
                    [line("m071", 71, -1)] + base_pairs(range(72, 82))),
    "base08.list": (HEAD_B.format(what="job 8: mirrored pairs 82-92, 22 runs"), base_pairs(range(82, 93))),
    "base09.list": (HEAD_B.format(what="job 9: mirrored pairs 93-103, 22 runs"), base_pairs(range(93, 104))),
    "base10.list": (HEAD_B.format(what="job 10: mirrored pairs 104-114, 22 runs"), base_pairs(range(104, 115))),
    "base11.list": (HEAD_B.format(what="job 11: mirrored pairs 115-125, 22 runs"), base_pairs(range(115, 126))),
    "l2_01.list": (HEAD_L.format(what="job 1: mirrored pairs 5-10, 12 runs"), l2_pairs(range(5, 11))),
    "l2_02.list": (HEAD_L.format(what="job 2: mirrored pairs 11-15 (10 runs) with the baseline pairs 126-127"),
                   l2_pairs(range(11, 16)) + base_pairs(range(126, 128))),
}
for name, (head, body) in lists.items():
    p = os.path.join(D, name)
    with open(p, "w") as f:
        f.write(head + "".join(body))
    print(p, len(body))
