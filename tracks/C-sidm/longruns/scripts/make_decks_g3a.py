#!/usr/bin/env python3
"""Decks of G3 step 1a (scope/SCOPE_G3.md section 2a; predictions JOURNAL 2026-11-28, step 1a).

  G3A_tmb01_Z0p<z>_N1e6_s1_<kin|ctrl>: the F21 b = 0.1 thermal core with central redshift Z(0)
  (models/model_set.py tags tmb01_Z0p5200, tmb01_Z0p5404, tmb01_Z0p5600, tmb01_Z0p6000) at
  N = 1e6, seed 1, kicked one percent inward (kin) or unkicked (ctrl, Z(0) = 0.5404 only), on the
  G2 mesh M/8. Everything else is the deck of the G2 bracket member N6b324
  (A8N_y0p32400_N1e6_s1_kin, run C-20261126-020831-fabf2d7) plus the horizon finder of
  core-v0.8 (<fastflow>: shear flow, mass rule 1e-5, 100 polishing iterations, diagnostics),
  searched every 32 cycles (1 M at dt = M/32). The particle and table files come from the runs
  of make_ic_seeds.py --maker models given with --ic TAG=RUNDIR.

    python3 make_decks_g3a.py --ic tmb01_Z0p5200=<rundir> ... [--check]
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
INP = os.path.normpath(os.path.join(HERE, "..", "inputs"))
TEMPLATE = "A8N_y0p32400_N1e6_s1_kin.athinput"
OLD_IC = "/data/haiyangw/nrpic/scratch/C-sidm/C-20261125-120426-f261c3e/s1/king_y0p32400_stratified_N1000000_s1"

FINDER = """
<fastflow>
num_horizons        = 1         # 0 when absent: no finder (z4c/z4c.cpp:286)
find_every          = 32        # every 1 M at dt = M/32
flow                = shear     # z4c/fastflow.cpp:68; finds horizons of any mass from any start radius (decision 0048)
mass_tol_0          = 1.0e-5    # the mass rule (core-v0.8 READY)
flow_iterations_0   = 400
polish_iterations_0 = 100
initial_radius_0    = 1.0
diagnostics         = true      # cc.horizon_status_0.txt: found or not, reason, iterations
"""

# (tag, kind): the four members of step 1a
MEMBERS = [("tmb01_Z0p5200", "kin"), ("tmb01_Z0p5404", "ctrl"),
           ("tmb01_Z0p5600", "kin"), ("tmb01_Z0p6000", "kin")]


def sub1(text, old, new):
    n = text.count(old)
    if n != 1:
        sys.exit(f"make_decks_g3a: '{old[:60]}' occurs {n} times, expected once")
    return text.replace(old, new)


def deck(tag, kind, icdir):
    src = open(os.path.join(INP, TEMPLATE)).read()
    z = tag.split("_Z0p")[1]
    name = f"G3A_tmb01_Z0p{z}_N1e6_s1_{kind}"
    st = os.path.join(icdir, "s1", f"{tag}_stratified_N1000000_s1")
    nrp = st + ("_kin.nrp" if kind == "kin" else ".nrp")
    tab = st + ".tab"
    for p in (nrp, tab):
        if not os.path.exists(p):
            sys.exit(f"make_decks_g3a: missing {p}")
    t = sub1(src, "problem          = King cluster A8N_y0p32400_N1e6_s1_kin",
             f"problem          = F21 b = 0.1 thermal core {name}")
    t = sub1(t, f"particle_file    = {OLD_IC}_kin.nrp", f"particle_file    = {nrp}")
    t = sub1(t, f"comp0_file       = {OLD_IC}.tab", f"comp0_file       = {tab}")
    t = sub1(t, "<output1>", FINDER.lstrip("\n") + "\n<output1>")
    head = (f"# longruns {name} (G3 step 1a, make_decks_g3a.py; scope/SCOPE_G3.md section 2a): the deck of\n"
            f"# A8N_y0p32400_N1e6_s1_kin (G2 member N6b324) with the b = 0.1 model {tag}"
            f" ({'kicked 1 percent inward' if kind == 'kin' else 'unkicked control'}) and the finder of core-v0.8.\n")
    return name, head + t


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ic", nargs="+", required=True, help="TAG=RUNDIR of make_ic_seeds.py --maker models")
    ap.add_argument("--check", action="store_true", help="compare with the committed decks, write nothing")
    a = ap.parse_args()
    ic = dict(x.split("=", 1) for x in a.ic)
    bad = 0
    for tag, kind in MEMBERS:
        name, text = deck(tag, kind, ic[tag])
        path = os.path.join(INP, name + ".athinput")
        if a.check:
            same = os.path.exists(path) and open(path).read() == text
            print(("same " if same else "DIFFERS ") + path)
            bad += not same
        else:
            with open(path, "w") as f:
                f.write(text)
            print("wrote", path)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
