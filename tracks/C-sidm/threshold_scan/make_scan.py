#!/usr/bin/env python3
"""Inputs of the longer threshold scan (prepared in wave 2, not run): SCAN.md says what each
block is for and what it costs.

  ic     particle files: the five King b = 1 models of the equilibria package
         (y0 = 0.314, 0.324, 0.334032, 0.344, 0.354; 2009.08163 l.1146 and the computed
         y_max) at N = 10^5, stratified, seed 1, each unperturbed and with a coherent radial
         kick of one percent of the particle's own speed, inward (`kin`) and outward
         (`kout`): q -> q -+ 0.01 |q| rhat in the orthonormal frame of the static observer,
         u = psi^2 q, net momentum removed again (the first paper's `--vpert` of
         python/nrpic/sampling.sample_st, applied with each particle's speed because the
         King model is not monoenergetic). The table is the unperturbed equilibrium's: the
         kick changes the energy density at second order in the kick only (the first-order
         term averages out over isotropic directions); the momentum constraint is violated
         at first order, as in the first paper's kicked runs.
  decks  inputs/scan/: block A (collisionless threshold location, 10 runs of 1000 M) and
         block C (collisional pilot at the threshold model, Kn = 3 and 0.3, 1000 M); the
         continuation of the wave-2 runs CC1 to 1000 M restarts from their files at 300 M.

    python3 make_scan.py ic [--out DIR]          (registered: writes particle files)
    python3 make_scan.py decks --ic-dir DIR      (writes inputs/scan/*.athinput, lists)
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
import make_decks as D  # noqa: E402

KING = ("king_y0p31400", "king_y0p32400", "king_y0p33403", "king_y0p34400", "king_y0p35400")
VPERT = {"kin": 0.01, "kout": -0.01}
TLIM_A = 1000.0
RST_DT = 200.0
SCAN_DIR = os.path.join(C.HERE, "inputs", "scan")


def kick(x, u, psi, vpert):
    """Coherent radial kick: orthonormal q = u/psi^2 -> q - vpert |q| rhat; net momentum
    (sum m u_i over equal masses) removed afterwards."""
    r = np.linalg.norm(x, axis=1)
    rhat = x / r[:, None]
    q = u / psi[:, None] ** 2
    qm = np.linalg.norm(q, axis=1)
    q2 = q - (vpert * qm)[:, None] * rhat
    u2 = psi[:, None] ** 2 * q2
    return u2 - u2.mean(axis=0)


def make_ic(out):
    make = os.path.join(C.HERE, "..", "equilibria", "make_equilibria.py")
    cmd = [sys.executable, os.path.normpath(make), "--out", out, "--N", "100000", "--seed", "1",
           "--sampler", "stratified", "--only", *KING]
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)
    index = {}
    for tag in KING:
        md = C.load_model(tag, out)
        r = np.linalg.norm(md["x"], axis=1)
        psi, alp = C.psi_alpha(md, r)
        E0 = md["meta"]["E0"]
        W0 = np.sqrt(1.0 + np.sum(md["u"] ** 2, axis=1) / psi ** 4)
        for name, vp in VPERT.items():
            u2 = kick(md["x"], md["u"], psi, vp)
            path = os.path.join(out, f"{C.stem(tag)}_{name}.nrp")
            C.nio.write_nrp(path, md["x"], u2, md["m"])
            W = np.sqrt(1.0 + np.sum(u2 ** 2, axis=1) / psi ** 4)
            EK = alp * W
            vr = np.sum((u2 / psi[:, None] ** 2) * md["x"], axis=1) / r / W
            index[f"{tag}_{name}"] = dict(
                file=os.path.basename(path), vpert=vp, mean_radial_velocity=float(np.mean(vr)),
                sum_mW_rel_change=float(np.sum(W) / np.sum(W0) - 1.0),
                frac_EK_above_E0=float(np.mean(EK > E0)), max_EK_over_E0=float(EK.max() / E0),
                net_momentum=[float(v) for v in (md["m"][:, None] * u2).sum(0)])
            print(tag, name, json.dumps(index[f"{tag}_{name}"]), flush=True)
    with open(os.path.join(out, "kicks.json"), "w") as f:
        json.dump(index, f, indent=1)


def write_deck(name, text):
    os.makedirs(SCAN_DIR, exist_ok=True)
    with open(os.path.join(SCAN_DIR, name + ".athinput"), "w") as f:
        f.write(text)


def make_decks(ic_dir):
    names = []
    # block A: collisionless, kicked in and out, 1000 M, restart every 200 M for chains
    for tag in KING:
        mk = "a_" + tag.split("_")[1]
        for kname in VPERT:
            C.MODELS[mk] = dict(tag=tag, label=f"scan A, {tag}, kick {kname}")
            _, text = D.deck(mk, None, TLIM_A, ic_dir)
            text = D.set_key(text, "particles", "particle_file",
                             os.path.join(ic_dir, f"{C.stem(tag)}_{kname}.nrp"))
            text = D.set_key(text, "output2", "dt", f"{RST_DT:g}")
            name = f"scanA_{tag.split('_')[1]}_{kname}"
            text = text.replace(f"King cluster {mk}_kninf", f"King cluster scanA {tag} {kname}")
            text = text.replace(f"# threshold_scan {mk}_kninf:", f"# threshold_scan {name}:")
            write_deck(name, text)
            names.append(name)
            del C.MODELS[mk]
    # block C: collisional pilot on the threshold model, Kn = 3 and 0.3, unperturbed
    for kn in (3.0, 0.3):
        _, text = D.deck("cc1", kn, TLIM_A, ic_dir)
        text = D.set_key(text, "output2", "dt", f"{RST_DT:g}")
        name = f"scanC_cc1_kn{kn:g}".replace(".", "p")
        write_deck(name, text)
        names.append(name)
    # block C on the first paper's adaptive mesh (down to M/16, apparent-horizon finder):
    # the static M/4 mesh of wave 2 cannot hold the black hole after a collapse (JOURNAL
    # entry 6), so the collapsed mass needs these decks
    amr = os.path.join(C.WT, "problems", "st", "st_cluster_amr.athinput")
    for kn in (10.0, 3.0, 1.0, 0.3):
        _, text = D.deck("cc1", kn, 300.0, ic_dir, template=amr)
        text = D.set_key(text, "output2", "dt", "50")
        text = D.set_key(text, "particles", "snap_dt", "5.0")
        name = f"scanC_amr_cc1_kn{kn:g}".replace(".", "p")
        write_deck(name, text)
        names.append(name)
    with open(os.path.join(SCAN_DIR, "decks.list"), "w") as f:
        f.write("# decks of the prepared threshold scan; each runs as one chain (SCAN.md)\n")
        for n in names:
            f.write(f"{n} {os.path.relpath(os.path.join(SCAN_DIR, n + '.athinput'), C.WT)}\n")
    print("\n".join(names))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("what", choices=["ic", "decks"])
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--ic-dir")
    a = ap.parse_args()
    if a.what == "ic":
        if not a.out:
            sys.exit("give --out or run through nrpic-run")
        make_ic(a.out)
    else:
        if not a.ic_dir:
            sys.exit("give --ic-dir (the run directory of `make_scan.py ic`)")
        make_decks(a.ic_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
