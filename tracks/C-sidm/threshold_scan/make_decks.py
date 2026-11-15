#!/usr/bin/env python3
"""Write the AthenaK input decks of the first collisional cluster runs (CC1, CC2 at
Kn = infinity, 10, 1) and the batch lists for harness/bin/nrpic-run, from the first
paper's static dx = M/4 deck `problems/st/st_migration.athinput` (domain 512 M, level-6
region |x|_inf < 7.9 M, Z4c with 1+log and Gamma driver, four compensated binomial
passes; Table "setups", row "Unperturbed unstable", of paper/sections/tables/tab_setups.tex).

    python3 make_decks.py [--tlim 300] [--ic-dir DIR]

Writes inputs/<run>.athinput (particle and table files by absolute path into the IC run
directory) and inputs/batch_<k>.list. Changes against the template, all in this file:
basename, seed, tlim, outputs (history every 4 cycles, snapshots every 10 M, trajectories
with the metric of all particles every 400 cycles, constraint statistics every 16 cycles,
restart files at 0 and tlim), the model files, and the <particles> collision block
(absent for Kn = infinity: the collisionless control runs the first paper's code path).
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

TEMPLATE = os.path.join(C.WT, "problems", "st", "st_migration.athinput")
OUTDIR = os.path.join(C.HERE, "inputs")


def set_key(text, block, key, value, comment=None):
    """Set `key = value` in <block>; append the line at the end of the block if absent."""
    lines = text.split("\n")
    out, inblk, done = [], False, False
    val = f"{key:<16} = {value}" + (f"   # {comment}" if comment else "")
    for i, ln in enumerate(lines):
        m = re.match(r"^<([^>]+)>", ln)
        if m:
            if inblk and not done:
                while out and out[-1].strip() == "":
                    out.pop()
                out.append(val)
                out.append("")
                done = True
            inblk = (m.group(1) == block)
        elif inblk and re.match(rf"^\s*{re.escape(key)}\s*=", ln):
            out.append(val)
            done = True
            continue
        out.append(ln)
    if inblk and not done:
        out.append(val)
        done = True
    if not done:
        raise KeyError(f"block <{block}> not found")
    return "\n".join(out)


def deck(model_key, kn, tlim, ic_dir, template=TEMPLATE):
    md = C.load_model(C.MODELS[model_key]["tag"], ic_dir)
    meta = md["meta"]
    N = int(meta["particles"]["N"])
    text = open(template).read()
    name = C.run_name(model_key, kn)
    head = (f"# threshold_scan {name}: {C.MODELS[model_key]['label']}, King b = 1 of 2009.08163,\n"
            f"# N = {N} (IC run {os.path.basename(ic_dir)}), Kn = lambda_c/H_c = "
            f"{'infinity (operator absent)' if kn is None else f'{kn:g}'}.\n"
            f"# Written by tracks/C-sidm/threshold_scan/make_decks.py from "
            f"{os.path.relpath(template, C.WT)}; do not edit by hand.\n\n")
    text = head + "<comment>" + text.split("<comment>", 1)[1]   # template's own header dropped
    text = set_key(text, "comment", "problem", f"King cluster {name}")
    text = set_key(text, "job", "basename", "cc")
    text = set_key(text, "job", "rng_seed", "1")
    text = set_key(text, "time", "tlim", f"{tlim:g}")
    text = set_key(text, "time", "ndiag", "800")
    text = set_key(text, "particles", "hist_dcycle", "4")
    text = set_key(text, "particles", "snap_dt", "10.0")
    text = set_key(text, "particles", "cstat_dcycle", "16")
    text = set_key(text, "particles", "traj_dcycle", "400", "every 25 M at dt = M/16")
    text = set_key(text, "particles", "traj_ntrack", str(N), "all particles")
    text = set_key(text, "particles", "particle_file", md["nrp"])
    text = set_key(text, "problem", "comp0_file", md["tab"])
    text = set_key(text, "output2", "dt", f"{tlim:g}")
    if kn is not None:
        sig = C.sigma_of(meta, kn)
        text = set_key(text, "particles", "collisions", "true")
        text = set_key(text, "particles", "coll_sigma", repr(float(sig)),
                       f"sigma~ = K/Kn, K = 1/(rho0_c H_c) = {C.kn_constant(meta)[0]:.6g}")
        text = set_key(text, "particles", "coll_sigma_model", "constant")
        text = set_key(text, "particles", "coll_pmax", "0.1")
        text = set_key(text, "particles", "coll_subcycle", "measured")
        text = set_key(text, "particles", "coll_nsub_max", "1000")
        text = set_key(text, "particles", "coll_cell_factor", "1")
        text = set_key(text, "particles", "coll_weights", "equal")
        text = set_key(text, "particles", "coll_hist_dcycle", "1", "records hold one cycle only")
        text = set_key(text, "particles", "coll_dump_cycle", "-1")
        text = set_key(text, "particles", "coll_budget", "true")
    return name, text


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tlim", type=float, default=300.0)
    ap.add_argument("--ic-dir", default=C.IC_DIR)
    a = ap.parse_args()
    os.makedirs(OUTDIR, exist_ok=True)
    names = []
    for mk in C.MODELS:
        for kn in C.KN_LIST:
            name, text = deck(mk, kn, a.tlim, a.ic_dir)
            with open(os.path.join(OUTDIR, name + ".athinput"), "w") as f:
                f.write(text)
            names.append(name)
            print("wrote", name)
    # two runs per card job (about 18 min each at 3.3-3.7 s per M): the most informative
    # pair first
    jobs = [("cc1_kninf", "cc1_kn1"), ("cc1_kn10", "cc2_kninf"), ("cc2_kn10", "cc2_kn1")]
    rel = os.path.relpath(OUTDIR, C.WT)
    for k, job in enumerate(jobs, 1):
        with open(os.path.join(OUTDIR, f"batch_{k}.list"), "w") as f:
            f.write(f"# threshold_scan card job {k}: <name> <athinput>, paths from the worktree root\n")
            for n in job:
                assert n in names
                f.write(f"{n} {rel}/{n}.athinput\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
