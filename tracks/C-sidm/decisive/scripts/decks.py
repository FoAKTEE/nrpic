#!/usr/bin/env python3
"""Decks and batch lists of the decisive runs D1 and D3 (stage/REVIEW-wave2.md section 7).

D1 (defect of the release operator, seed scatter): the wave-2 decks
threshold_scan/inputs/cc{1,2}_kn10.athinput unchanged (same particle files, mesh, options,
300 M) except for <job> rng_seed and <particles> coll_energy (and the header). coll_budget =
true is already in those decks. Runs:
    cc2_kn10_part_s1, cc2_kn10_part_s2, cc1_kn10_part_s1, cc1_kn10_part_s2  (coll_energy = particle)
    cc2_kn10_cell_s2                                                        (coll_energy = cell)
The wave-2 runs cc1_kninf, cc2_kninf (C-20261115-171058-c26cfad, C-20261115-171059-4b70228)
stay the controls; cc2_kn10 of C-20261115-171059-35441e3 is cell mode, seed 1.

D3 (stable King model): decks written from the CC2 decks with the model's particle and table
files and sigma~ = K/Kn of the model (equilibria/knudsen.py via threshold_scan/common.py):
    d3_kninf, d3_kn10_part_s1, d3_kn1_part_s1

    python3 decks.py d1
    python3 decks.py d3 --ic-dir DIR --tag king_y0p26000

Writes inputs/<run>.athinput and inputs/<job>.list (paths from the worktree root). Every list
starts with a smoke run of the first deck to t = 0.5 M (8 steps), as the collisions-2 READY
advises for card jobs.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.normpath(os.path.join(HERE, ".."))
TS = os.path.normpath(os.path.join(PKG, "..", "threshold_scan"))
sys.path.insert(0, TS)
import common as C  # noqa: E402
from make_decks import set_key  # noqa: E402

INP = os.path.join(PKG, "inputs")
REL = os.path.relpath(INP, C.WT)

D1 = [  # name, model key, energy mode, seed
    ("cc2_kn10_part_s1", "cc2", "particle", 1),
    ("cc2_kn10_part_s2", "cc2", "particle", 2),
    ("cc1_kn10_part_s1", "cc1", "particle", 1),
    ("cc1_kn10_part_s2", "cc1", "particle", 2),
    ("cc2_kn10_cell_s2", "cc2", "cell", 2),
]
# jobs of two runs each (300 M at 3.42-3.46 s per M is about 17-18 min per run); the CC2
# pair first (the review's question is whether CC2's collapse is an artefact)
D1_JOBS = [("d1_job1", ("cc2_kn10_part_s1", "cc2_kn10_part_s2")),
           ("d1_job2", ("cc1_kn10_part_s1", "cc1_kn10_part_s2"))]


def header(name, lines):
    return "".join(f"# decisive {name}: {ln}\n" for ln in lines)


def replace_header(text, new_head):
    body = "<comment>" + text.split("<comment>", 1)[1]
    return new_head + "# Written by tracks/C-sidm/decisive/scripts/decks.py; do not edit by hand.\n\n" + body


def d1_deck(name, mk, mode, seed):
    src = os.path.join(TS, "inputs", f"{mk}_kn10.athinput")
    text = open(src).read()
    old = [ln[2:] for ln in text.split("<comment>", 1)[0].splitlines() if ln.startswith("# ")
           and "Written by" not in ln]
    head = header(name, [f"D1 ({'energy defect' if mode == 'particle' else 'seed scatter of the release operator'}), "
                         f"from {os.path.relpath(src, C.WT)},"] + old[:2] +
                  [f"changed: <job> rng_seed = {seed}, <particles> coll_energy = {mode}."])
    text = replace_header(text, head)
    text = set_key(text, "comment", "problem", f"King cluster {name}")
    text = set_key(text, "job", "rng_seed", str(seed))
    text = set_key(text, "particles", "coll_energy", mode,
                   "pair conserves sum u_i and sum (alpha W - beta.u) at each particle's metric"
                   if mode == "particle" else "release operator (pair energy at the cell centre)")
    text = set_key(text, "particles", "coll_budget", "true")
    return text


def d3_deck(name, ic_dir, tag, kn, mode, seed):
    """From the CC2 deck of the same Kn class; model files and sigma~ of the D3 model."""
    src = os.path.join(TS, "inputs", "cc2_kninf.athinput" if kn is None else "cc2_kn10.athinput")
    text = open(src).read()
    s = C.stem(tag)
    meta = json.load(open(os.path.join(ic_dir, s + ".json")))
    nrp, tab = os.path.join(ic_dir, s + ".nrp"), os.path.join(ic_dir, s + ".tab")
    K = C.kn_constant(meta)[0]
    head = header(name, [f"D3, King b = 1 of 2009.08163 at y0 = {meta.get('y0', tag)}, N = "
                         f"{meta['particles']['N']} (IC run {os.path.basename(ic_dir)}),",
                         f"Kn = lambda_c/H_c = {'infinity (operator absent)' if kn is None else f'{kn:g}'}; "
                         f"from {os.path.relpath(src, C.WT)} with this model's files"
                         + ("" if kn is None else f", sigma~ = K/Kn (K = {K:.6g}), rng_seed = {seed}, "
                            f"coll_energy = {mode}") + "."])
    text = replace_header(text, head)
    text = set_key(text, "comment", "problem", f"King cluster {name}")
    text = set_key(text, "particles", "particle_file", nrp)
    text = set_key(text, "problem", "comp0_file", tab)
    if kn is not None:
        text = set_key(text, "job", "rng_seed", str(seed))
        text = set_key(text, "particles", "coll_sigma", repr(float(K / kn)),
                       f"sigma~ = K/Kn, K = 1/(rho0_c H_c) = {K:.6g}")
        text = set_key(text, "particles", "coll_energy", mode,
                       "pair conserves sum u_i and sum (alpha W - beta.u) at each particle's metric")
        text = set_key(text, "particles", "coll_budget", "true")
    return text, K


def write_list(job, names, comment):
    with open(os.path.join(INP, job + ".list"), "w") as f:
        f.write(f"# decisive card job {job}: {comment}\n")
        f.write("# <name> <athinput> [athena args]; paths from the worktree root; smoke run first\n")
        f.write(f"smoke_{names[0]} {REL}/{names[0]}.athinput time/tlim=0.5\n")
        for n in names:
            f.write(f"{n} {REL}/{n}.athinput\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("what", choices=("d1", "d3"))
    ap.add_argument("--ic-dir")
    ap.add_argument("--tag")
    a = ap.parse_args()
    os.makedirs(INP, exist_ok=True)
    if a.what == "d1":
        for name, mk, mode, seed in D1:
            with open(os.path.join(INP, name + ".athinput"), "w") as f:
                f.write(d1_deck(name, mk, mode, seed))
            print("wrote", name)
        for job, names in D1_JOBS:
            write_list(job, names, "D1, " + ", ".join(names))
        return 0
    if not (a.ic_dir and a.tag):
        sys.exit("d3 needs --ic-dir and --tag")
    runs = [("d3_kninf", None, None, None), ("d3_kn10_part_s1", 10.0, "particle", 1),
            ("d3_kn1_part_s1", 1.0, "particle", 1)]
    for name, kn, mode, seed in runs:
        text, K = d3_deck(name, a.ic_dir, a.tag, kn, mode, seed)
        with open(os.path.join(INP, name + ".athinput"), "w") as f:
            f.write(text)
        print("wrote", name, "K =", K, "sigma~ =", None if kn is None else K / kn)
    # the D3 control with the Kn = 1 run first (the strongest signal of the hypothesis in
    # 300 M), then Kn = 10 with the cell-mode seed-2 run of D1
    write_list("d3_job3", ("d3_kninf", "d3_kn1_part_s1"), "D3, d3_kninf, d3_kn1_part_s1")
    write_list("d3_job4", ("d3_kn10_part_s1", "cc2_kn10_cell_s2"), "D3 and D1, d3_kn10_part_s1, cc2_kn10_cell_s2")
    return 0


if __name__ == "__main__":
    sys.exit(main())
