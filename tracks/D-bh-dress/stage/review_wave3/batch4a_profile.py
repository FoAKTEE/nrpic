#!/usr/bin/env python3
"""Lead's batch-4a check Y5 (JOURNAL.md): the dust profile of Q16 at its last snapshot against
the fresh verifier's seedless self-similar solution. No helper code: snapshot reader and r_ta
estimator of stage/review_wave2/infall_check.py (wave-2 lead); reference m(lambda) from
verifier_g1 run D-20261121-031711-0d79cb3 (v2_selfsimilar.npz), rho/rho_b = (9 pi^2/16) dm/dlambda^3.
Writes batch4a_profile.json and batch4a_profile.png/.pdf into --out.
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "review_wave2")))
import infall_check as ic  # noqa: E402
from infall_check import fs  # noqa: E402

SCR = "/data/haiyangw/nrpic/scratch/D-bh-dress"
Q16 = os.path.join(SCR, "D-20261121-085652-7e189a2")
SS = os.path.join(SCR, "D-20261121-031711-0d79cb3", "v2_selfsimilar.npz")
EDGES = 10 ** np.arange(np.log10(0.075), np.log10(0.3) + 1e-9, 0.1)


def ss_binned(lam, m, edges):
    mi = np.interp(edges, lam, m)
    return (9 * np.pi ** 2 / 16) * np.diff(mi) / np.diff(edges ** 3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    p = json.load(open(os.path.join(Q16, "setup.json")))
    fn = sorted(glob.glob(os.path.join(Q16, "infall.part.*.bin")))[-1]
    t, rec, tag = ic.snap(fn)
    a = ((p["t_i"] + t) / p["t_i"]) ** (2.0 / 3.0)
    d0, d1 = p["tag_dust"]
    dust = (tag >= d0) & (tag < d1)
    x = rec[dust, :3] - np.asarray(p["shift"], float)
    u = rec[dust, 3:6]
    m = rec[dust, 6]
    r = np.sqrt((x ** 2).sum(1))
    vr = (x * u).sum(1) / r
    mclump = rec[(tag >= p["tag_clump"][0]) & (tag < p["tag_clump"][1]), 6].sum()
    rta, mrta = ic.r_ta_mass(r, vr, m, mclump)
    rho_b = p["rho_i"] * a ** -3
    z = np.load(SS)
    ref = ss_binned(z["lam"], z["m"], EDGES)
    res = {"file": os.path.basename(fn), "a": a, "r_ta": rta, "M_in_rta": mrta,
           "edges": EDGES.tolist(), "ref": ref.tolist()}
    for lab, fac in (("r_ta", 1.0), ("r_ta*0.97", 0.97), ("r_ta*1.03", 1.03)):
        rr = rta * fac
        w, _ = np.histogram(r / rr, EDGES, weights=m)
        rho = w / ((4 * np.pi / 3) * rr ** 3 * np.diff(EDGES ** 3)) / rho_b
        ratio = rho / ref
        res[lab] = dict(rho=rho.tolist(), ratio=ratio.tolist(),
                        maxdev=float(np.max(np.abs(ratio - 1))),
                        rms=float(np.sqrt(np.mean((ratio - 1) ** 2))))
    with open(os.path.join(args.out, "batch4a_profile.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(res, indent=1))
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(8, 3.2))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.16, top=0.9, wspace=0.3)
    c = np.sqrt(EDGES[:-1] * EDGES[1:])
    axs[0].loglog(c, ref, "-", color=fs.PAL["blue"], label="self-similar (verifier, seedless)")
    for lab, col in (("r_ta", fs.PAL["red"]), ("r_ta*0.97", fs.PAL["yellow"]), ("r_ta*1.03", fs.PAL["green"])):
        axs[0].loglog(c, res[lab]["rho"], "o", color=col, ms=4, label="Q16, " + lab)
        axs[1].semilogx(c, res[lab]["ratio"], "o-", color=col, ms=4, label=lab)
    axs[1].axhspan(0.75, 1.25, color="0.9")
    axs[1].axhline(1, color="0.5", lw=0.8)
    axs[0].set_xlabel(r"$\lambda=r/r_{\rm ta}$")
    axs[0].set_ylabel(r"$\rho_{\rm dust}/\rho_b(t)$")
    axs[0].legend(frameon=False, fontsize=7)
    axs[0].set_title(f"(a) Q16 at $a/a_i$ = {a:.2f}, $r_{{ta}}$ = {rta:.1f} M", fontsize=9)
    axs[1].set_xlabel(r"$\lambda$")
    axs[1].set_ylabel("run / self-similar")
    axs[1].set_ylim(0.5, 1.5)
    axs[1].legend(frameon=False, fontsize=7)
    axs[1].set_title("(b) ratio; band: Y5 bound 25 %", fontsize=9)
    fs.save(fig, os.path.join(args.out, "batch4a_profile"))


if __name__ == "__main__":
    main()
