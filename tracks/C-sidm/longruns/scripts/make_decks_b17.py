#!/usr/bin/env python3
"""Decks of the batch-17 follow-up card runs of C-sidm (predictions: tracks/C-sidm/JOURNAL.md,
entry 2026-11-25 "batch 17: follow-up runs, predictions before submission").

  N6i, N6o  A8N_y0p33403_N1e6_s1_<kin|kout>: the threshold model (King b = 1, y0 = 0.334032)
            on the M/8 mesh at N = 1e6, kicked one percent inward or outward; the particle
            files are those of run C-20261124-130731-e1d24de (make_ic_seeds.py --seeds 1
            --N 1000000: the same stratified seed-1 sample as the control N6c, with the kicks
            of threshold_scan/make_scan.py). Everything else is the deck of N6c
            (A8N_y0p33403_N1e6_s1_ctrl, run C-20261124-221122-928c9eb).
  D2eta1    D2_cc2_kn10_f2_s1_eta1: decisive D2 at f = 2, collision seed 1, on M/8 with
            <z4c> shift_eta = 1.0 instead of 2.0 (gauge leg of the three-way convergence),
            tlim 220 M (the f = 2 run collapsed at 163.41 M). Everything else is
            D2_cc2_kn10_f2_s1 (run C-20261122-141414-399ad97).
The decks stay on the executable of their series (core-v0.6 card build, as qitem.sh runs
it), so they carry no `dt_gauge` (an option of core-v0.7); cfl_number 0.25 is below every
bound of coord/INTERFACES/step_limit.md (0.47 with the 1+log lapse).

    python3 make_decks_b17.py [--check]
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
INP = os.path.normpath(os.path.join(HERE, "..", "inputs"))
IC6 = "/data/haiyangw/nrpic/scratch/C-sidm/C-20261124-130731-e1d24de/s1/king_y0p33403_stratified_N1000000_s1"


def sub1(text, old, new):
    n = text.count(old)
    if n != 1:
        sys.exit(f"make_decks_b17: '{old[:60]}' occurs {n} times, expected once")
    return text.replace(old, new)


def kicked(kind):
    src = open(os.path.join(INP, "A8N_y0p33403_N1e6_s1_ctrl.athinput")).read()
    name = f"A8N_y0p33403_N1e6_s1_{kind}"
    t = sub1(src, "problem          = King cluster A8N_y0p33403_N1e6_s1_ctrl",
             f"problem          = King cluster {name}")
    t = sub1(t, f"particle_file    = {IC6}.nrp", f"particle_file    = {IC6}_{kind}.nrp")
    head = (f"# longruns {name} (batch 17, make_decks_b17.py): the deck of A8N_y0p33403_N1e6_s1_ctrl with the\n"
            f"# coherent one-percent radial kick {kind} (particle file {os.path.basename(IC6)}_{kind}.nrp).\n")
    return name, head + t


def eta1():
    src = open(os.path.join(INP, "D2_cc2_kn10_f2_s1.athinput")).read()
    name = "D2_cc2_kn10_f2_s1_eta1"
    t = sub1(src, "shift_eta       = 2.0", "shift_eta       = 1.0     # batch 17: gauge leg (D2 has 2.0)")
    t = re.sub(r"(?m)^tlim(\s*)=\s*300\b", r"tlim\1= 220", t, count=1)
    if "= 220" not in t:
        sys.exit("make_decks_b17: tlim 300 not found in the D2 deck")
    t = sub1(t, "problem          = King cluster D2_cc2_kn10_f2_s1\n",
             f"problem          = King cluster {name}\n")
    head = (f"# longruns {name} (batch 17, make_decks_b17.py): D2_cc2_kn10_f2_s1 with <z4c> shift_eta 1.0\n"
            f"# instead of 2.0 and tlim 220 M (gauge leg of the three-way convergence).\n")
    return name, head + t


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="build in memory and print the differences only")
    a = ap.parse_args()
    for name, text in (kicked("kin"), kicked("kout"), eta1()):
        path = os.path.join(INP, name + ".athinput")
        if a.check:
            print(name, len(text.splitlines()), "lines")
            continue
        with open(path, "w") as f:
            f.write(text)
        print("wrote", path)
    for kind in ("kin", "kout"):
        p = f"{IC6}_{kind}.nrp"
        if not os.path.exists(p):
            sys.exit(f"make_decks_b17: particle file missing: {p}")


if __name__ == "__main__":
    main()
