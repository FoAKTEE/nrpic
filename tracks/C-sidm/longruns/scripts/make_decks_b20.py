#!/usr/bin/env python3
"""Decks of the convergence legs of the N = 1e6 bracket (batch 20; ruling 0039 item 3: twenty
card-hours for the mesh leg and the gauge leg; predictions: tracks/C-sidm/JOURNAL.md, entry
2026-11-25 "batch 20: mesh and gauge legs of the bracket, predictions before submission").

  A16N_<y0>_N1e6_s1_kin   mesh leg: the bracket deck A8N_<y0>_N1e6_s1_kin (N6b344, N6b324) with
                          a fourth refined region, cells of M/16 inside |x|_inf < 1.95 M, the
                          geometry of the collisional mesh member D2M16 (make_decks_b11.py).
                          The step on the finest level halves (M/64 at cfl_number 0.25), so the
                          cycle cadences of the history, the constraint statistics, the
                          trajectories and ndiag are doubled to keep their cadence in M.
  A8N_<y0>_N1e6_s1_kin_eta1  gauge leg: the bracket deck with <z4c> shift_eta = 1.0 instead of
                          2.0, the variant of D2eta1 (make_decks_b17.py), so the track's gauge
                          leg is one change of the shift damping for both the collisional and
                          the collisionless series.
Everything else is the bracket deck: same particle files (runs C-20261125-115759-77a6999 for
0.344, C-20261125-120426-f261c3e for 0.324), same executable (core-v0.6 card build, as
qitem.sh runs it), cfl_number 0.25 (below the bound 0.47 of the 1+log lapse,
coord/INTERFACES/step_limit.md), no `dt_gauge`, no horizon finder (as the controls).

    python3 make_decks_b20.py [--check]
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
INP = os.path.normpath(os.path.join(HERE, "..", "inputs"))
MODELS = ("y0p34400", "y0p32400")

REGION3 = """<refined_region3>
level = 8          # batch 20: cells of M/16 inside |x|_inf < 1.95 M (mesh leg of the bracket; geometry of D2M16)
x1min = -1.95
x1max = 1.95
x2min = -1.95
x2max = 1.95
x3min = -1.95
x3max = 1.95

<time>"""


def sub1(text, old, new):
    n = text.count(old)
    if n != 1:
        sys.exit(f"make_decks_b20: '{old[:60]}' occurs {n} times, expected once")
    return text.replace(old, new)


def base(y0):
    name = f"A8N_{y0}_N1e6_s1_kin"
    return name, open(os.path.join(INP, name + ".athinput")).read()


def mesh16(y0):
    src_name, t = base(y0)
    name = f"A16N_{y0}_N1e6_s1_kin"
    t = sub1(t, f"problem          = King cluster {src_name}\n", f"problem          = King cluster {name}\n")
    t = sub1(t, "\n<time>", "\n" + REGION3)
    t = sub1(t, "ndiag            = 1600", "ndiag            = 3200")
    t = sub1(t, "hist_dcycle      = 8   # every 0.25 M at dt = M/32", "hist_dcycle      = 16   # every 0.25 M at dt = M/64")
    t = sub1(t, "cstat_dcycle     = 32", "cstat_dcycle     = 64")
    t = sub1(t, "traj_dcycle      = 800   # every 25 M at dt = M/32", "traj_dcycle      = 1600   # every 25 M at dt = M/64")
    head = (f"# longruns {name} (batch 20, make_decks_b20.py): the bracket deck {src_name} with cells of\n"
            f"# M/16 inside |x|_inf < 1.95 M (mesh leg; ruling 0039 item 3) and the cycle cadences doubled.\n")
    return name, head + t


def eta1(y0):
    src_name, t = base(y0)
    name = f"A8N_{y0}_N1e6_s1_kin_eta1"
    t = sub1(t, f"problem          = King cluster {src_name}\n", f"problem          = King cluster {name}\n")
    t = sub1(t, "shift_eta       = 2.0", "shift_eta       = 1.0     # batch 20: gauge leg (the bracket deck has 2.0)")
    head = (f"# longruns {name} (batch 20, make_decks_b20.py): the bracket deck {src_name} with <z4c>\n"
            f"# shift_eta 1.0 instead of 2.0 (gauge leg; ruling 0039 item 3; the variant of D2eta1).\n")
    return name, head + t


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="build in memory and print the names only")
    a = ap.parse_args()
    decks = [mesh16(y) for y in MODELS] + [eta1(y) for y in MODELS]
    for name, text in decks:
        for ln in text.splitlines():
            key = ln.split("#", 1)[0].strip()
            if key.startswith("particle_file") or key.startswith("comp0_file"):
                p = key.split("=", 1)[1].strip()
                if not os.path.exists(p):
                    sys.exit(f"make_decks_b20: {name}: missing {p}")
        path = os.path.join(INP, name + ".athinput")
        if a.check:
            print(name, len(text.splitlines()), "lines")
            continue
        with open(path, "w") as f:
            f.write(text)
        print("wrote", path)


if __name__ == "__main__":
    main()
