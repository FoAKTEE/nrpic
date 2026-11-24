#!/usr/bin/env python3
"""Decks of the batch-11 follow-up card runs of C-sidm (predictions: tracks/C-sidm/JOURNAL.md,
entry 2026-11-24 "follow-up runs, predictions before submission").

  N-series  A8N_y0p33403_N<1e4|1e6>_s1_ctrl: the unkicked control of the threshold model
            (King b = 1, y0 = 0.334032) on the M/8 mesh of block A, collisionless, 600 M,
            with the stratified seed-1 sample at N = 1e4 or 1e6 instead of 1e5 (the block A
            control A8_y0p33403_s1_ctrl collapsed on its own at 534.8 M). Everything else is
            the block A deck; trajectories of the first 1e5 (1e6) or all 1e4 particles.
  M/16      D2M16_cc2_kn10_f4_s1: decisive D2 (CC2, y0 = 0.314, Kn = 10, coll_energy =
            particle, collision seed 1) with a level-8 region (cells of M/16) inside
            |x|_inf < 1.95 M added inside the level-7 region of M/8; coll_cell_factor 4, so
            that the collision cells are M/4 as on the M/4 mesh (f = 1) and on M/8 (f = 2);
            220 M; output cadences doubled in cycles so that they stay the same in time.
All new decks write a restart every 10 M (preemption by the priority partition, JOURNAL
2026-11-24T12:59Z).

    python3 make_decks_b11.py --n1e6 DIR --n1e4 DIR    (DIR: runs of make_ic_seeds.py, seed 1)
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_decks as MD  # noqa: E402

D = MD.D
TAG = "king_y0p33403"
REGION8 = """<refined_region3>
level = 8          # batch 11: cells of M/16 inside |x|_inf < 1.95 M (mesh leg of D2)
x1min = -1.95
x1max = 1.95
x2min = -1.95
x2max = 1.95
x3min = -1.95
x3max = 1.95

"""


def head(text, lines):
    body = text.split("<comment>", 1)[1]
    h = "".join(f"# {ln}\n" for ln in lines)
    h += "# Written by tracks/C-sidm/longruns/scripts/make_decks_b11.py; do not edit by hand.\n"
    return h + "\n<comment>" + body


def nseries(ic_dir, n, label):
    src = os.path.join(MD.INP, "A8_y0p33403_s1_ctrl.athinput")
    text = open(src).read()
    name = f"A8N_y0p33403_N{label}_s1_ctrl"
    stem = f"{TAG}_stratified_N{n}_s1"
    pf = os.path.join(ic_dir, "s1", stem + ".nrp")
    tab = os.path.join(ic_dir, "s1", stem + ".tab")
    assert os.path.exists(pf) and os.path.exists(tab), (pf, tab)
    text = head(text, [f"longruns {name}: N-series of the M/8 control drift (batch 11), King b = 1 {TAG},",
                       f"stratified sample seed 1 at N = {n}, unkicked control, collisionless, 600 M;",
                       "otherwise the block A deck A8_y0p33403_s1_ctrl (N = 1e5)."])
    text = D.set_key(text, "comment", "problem", f"King cluster {name}")
    text = D.set_key(text, "particles", "particle_file", pf)
    text = D.set_key(text, "problem", "comp0_file", tab)
    text = D.set_key(text, "particles", "traj_ntrack", str(min(n, 100000)),
                     "all particles" if n <= 100000 else "the first 1e5 particles")
    text = D.set_key(text, "output2", "dt", "10")
    return name, MD.write(name, text)


def d2m16():
    src = os.path.join(MD.INP, "D2_cc2_kn10_f2_s1.athinput")
    text = open(src).read()
    name = "D2M16_cc2_kn10_f4_s1"
    text = head(text, [f"longruns {name}: decisive D2 on the M/16 mesh (batch 11): CC2 (y0 = 0.314) at",
                       "Kn = 10, coll_energy = particle, collision seed 1, coll_cell_factor 4 (collision cells",
                       "of M/4 as in the M/4 and M/8 members), 220 M; otherwise D2_cc2_kn10_f2_s1."])
    assert "<refined_region3>" not in text
    text = text.replace("<time>", REGION8 + "<time>", 1)
    text = D.set_key(text, "comment", "problem", f"King cluster {name}")
    text = D.set_key(text, "time", "tlim", "220")
    text = D.set_key(text, "time", "ndiag", "3200")
    text = D.set_key(text, "particles", "hist_dcycle", "16", "every 0.25 M at dt = M/64")
    text = D.set_key(text, "particles", "cstat_dcycle", "64")
    text = D.set_key(text, "particles", "traj_dcycle", "1600", "every 25 M at dt = M/64")
    text = D.set_key(text, "particles", "coll_cell_factor", "4")
    text = D.set_key(text, "output2", "dt", "10")
    return name, MD.write(name, text)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n1e6", required=True)
    ap.add_argument("--n1e4", required=True)
    a = ap.parse_args()
    for n, p in (nseries(a.n1e6, 1000000, "1e6"), nseries(a.n1e4, 10000, "1e4"), d2m16()):
        print(n, p)


if __name__ == "__main__":
    main()
