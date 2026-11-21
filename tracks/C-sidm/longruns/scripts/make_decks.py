#!/usr/bin/env python3
"""Decks of the batch-5 card runs of C-sidm (predictions: tracks/C-sidm/JOURNAL.md, entry
2026-11-21T20:25Z). All on the M/8 mesh of the drift package (level-7 region, cells of M/8,
inside |x|_inf < 3.9 M; drift/scripts/make_decks.py REGION7), outputs as drift run (i):
history every 0.25 M, trajectories of all particles every 25 M, restart files every 100 M.

  block A  A8_<y0>_s<seed>_<ctrl|kin|kout>: collisionless, 600 M; the threshold model
           y0 = 0.334032 with particle seeds 1, 2, 3, the models 0.324 and 0.344 with seed 1;
           each unkicked (control) and kicked one percent inward and outward.
  D2       D2_cc2_kn10_f<f>_s<s>: CC2 (y0 = 0.314, seed-1 particle file of wave 2), Kn = 10,
           coll_energy = particle, coll_cell_factor f = 1, 2, 4, collision seed s; and the
           collisionless control D2_cc2_kninf; 300 M.
  timing   inputs/timing.list: short segments of A8_y0p33403_s1_ctrl (20 M) and of the
           three D2 collisional decks (10 M).

    python3 make_decks.py --seed-ic DIR     (DIR: the run of make_ic_seeds.py)
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.normpath(os.path.join(HERE, ".."))
TRACK = os.path.normpath(os.path.join(PKG, ".."))
WT = os.path.normpath(os.path.join(TRACK, "..", ".."))
sys.path.insert(0, os.path.join(TRACK, "threshold_scan"))
import importlib.util  # noqa: E402


def _load(modname, path):
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[modname] = mod
    spec.loader.exec_module(mod)
    return mod


# threshold_scan's make_decks (set_key) under its own name; drift's module imports it as
# `make_decks`, so that name must point to the threshold_scan file before drift's is loaded
D = _load("make_decks", os.path.join(TRACK, "threshold_scan", "make_decks.py"))
DR = _load("drift_make_decks", os.path.join(TRACK, "drift", "scripts", "make_decks.py"))

SCRATCH = "/data/haiyangw/nrpic/scratch/C-sidm"
SCAN_IC = os.path.join(SCRATCH, "C-20261115-174556-3544e2c")   # seed 1, all five models, kicks
INP = os.path.join(PKG, "inputs")
TLIM_A, TLIM_D2, RST_DT = 600.0, 300.0, 100.0
MODELS_A = [("y0p33403", 1), ("y0p33403", 2), ("y0p33403", 3), ("y0p32400", 1), ("y0p34400", 1)]


def m8(text, src, title, head_lines):
    head = "".join(f"# {ln}\n" for ln in head_lines)
    head += (f"# Written by tracks/C-sidm/longruns/scripts/make_decks.py from {os.path.relpath(src, WT)};"
             " do not edit by hand.\n")
    body = text.split("<comment>", 1)[1]
    text = head + "\n<comment>" + body
    assert "<refined_region2>" not in text
    text = text.replace("<time>", DR.REGION7 + "<time>", 1)
    text = D.set_key(text, "comment", "problem", title)
    text = D.set_key(text, "time", "ndiag", "1600")
    text = D.set_key(text, "particles", "hist_dcycle", "8", "every 0.25 M at dt = M/32")
    text = D.set_key(text, "particles", "cstat_dcycle", "32")
    text = D.set_key(text, "particles", "traj_dcycle", "800", "every 25 M at dt = M/32")
    text = D.set_key(text, "output2", "dt", f"{RST_DT:g}")
    return text


def write(name, text):
    os.makedirs(INP, exist_ok=True)
    p = os.path.join(INP, name + ".athinput")
    with open(p, "w") as f:
        f.write(text)
    return os.path.relpath(p, WT)


def block_a(seed_ic):
    out = []
    for y, s in MODELS_A:
        tag = f"king_{y}"
        src = os.path.join(TRACK, "threshold_scan", "inputs", "scan", f"scanA_{y}_kin.athinput")
        ic = SCAN_IC if s == 1 else os.path.join(seed_ic, f"s{s}")
        stem = f"{tag}_stratified_N100000_s{s}"
        for k in ("ctrl", "kin", "kout"):
            name = f"A8_{y}_s{s}_{k}"
            pf = os.path.join(ic, stem + ("" if k == "ctrl" else f"_{k}") + ".nrp")
            assert os.path.exists(pf), pf
            text = m8(open(src).read(), src, f"King cluster {name}",
                      [f"longruns {name}: block A on the M/8 mesh, King b = 1 {tag}, particle seed {s},",
                       f"{'unkicked control' if k == 'ctrl' else 'coherent one-percent radial kick ' + k},"
                       f" N = 1e5, collisionless, {TLIM_A:g} M."])
            text = D.set_key(text, "time", "tlim", f"{TLIM_A:g}")
            text = D.set_key(text, "particles", "particle_file", pf)
            text = D.set_key(text, "problem", "comp0_file", os.path.join(ic, stem + ".tab"))
            out.append((name, write(name, text)))
    return out


def d2():
    out = []
    for f, s in ((1, 1), (2, 1), (4, 1), (2, 2)):
        src = os.path.join(TRACK, "decisive", "inputs", f"cc2_kn10_part_s{s}.athinput")
        name = f"D2_cc2_kn10_f{f}_s{s}"
        text = m8(open(src).read(), src, f"King cluster {name}",
                  [f"longruns {name}: decisive D2, CC2 (y0 = 0.314) at Kn = 10, coll_energy = particle,",
                   f"on the M/8 mesh with coll_cell_factor = {f}, collision seed {s}, {TLIM_D2:g} M."])
        text = D.set_key(text, "time", "tlim", f"{TLIM_D2:g}")
        text = D.set_key(text, "particles", "coll_cell_factor", str(f))
        out.append((name, write(name, text)))
    src = os.path.join(TRACK, "threshold_scan", "inputs", "cc2_kninf.athinput")
    name = "D2_cc2_kninf"
    text = m8(open(src).read(), src, f"King cluster {name}",
              [f"longruns {name}: collisionless control of D2 (same particle file, mesh and executable),",
               f"{TLIM_D2:g} M."])
    text = D.set_key(text, "time", "tlim", f"{TLIM_D2:g}")
    out.append((name, write(name, text)))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed-ic", required=True)
    a = ap.parse_args()
    A = block_a(a.seed_ic)
    B = d2()
    with open(os.path.join(INP, "timing.list"), "w") as f:
        f.write("# longruns timing job (core-v0.6): <name> <athinput> [athena args]\n")
        f.write(f"T_A8_ctrl {dict(A)['A8_y0p33403_s1_ctrl']} time/tlim=20\n")
        for n, p in B[:3]:
            f.write(f"T_{n} {p} time/tlim=10\n")
    for n, p in A + B:
        print(n, p)


if __name__ == "__main__":
    main()
