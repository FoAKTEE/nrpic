#!/usr/bin/env python3
"""Offline constraint check of data set 3 (prep_bh.py): finite-difference Hamiltonian and
momentum residuals of the exact slice (expball/mesh.py `residuals`, conformally flat
form, divided by 6 H^2) on octant meshes of increasing resolution, away from the
non-smooth radii (the top-hat jumps at R1 and R2 and the taper) and over all cells, with
the measured orders; the same check as the G1 test of A-pre-1 (expball/README.md) for the
new data.

    constraints_ds3.py --prep <prep_bh output> --out <dir> [--Ns 32,64,128,256]
"""
import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C            # noqa: E402
from expball import mesh as XMESH   # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prep", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--Ns", default="32,64,128,256")
    ap.add_argument("--band", type=float, default=0.1, help="excluded band / R_b around non-smooth radii")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    ex = C.load_json(os.path.join(a.prep, "exact.json"))
    ball = C.ball_from_spec(ex["spec"])
    Ns = [int(s) for s in a.Ns.split(",")]
    L = 1.25 * ball.R_out
    ed = ball.rbar_edges()
    band = a.band * ball.Rb
    regs = {"all": lambda r: np.ones_like(r, dtype=bool),
            "smooth": lambda r: np.min(np.abs(r[..., None] - ed), axis=-1) > band}
    src = XMESH.radial_source(ball)
    res = dict(nonsmooth_rbar=ed.tolist(), band=band, L=L, N=Ns, h=[L / n for n in Ns], norms={})
    for n in Ns:
        r = XMESH.residuals(src, n, L, (2, 4), regs, norm=6 * ball.H ** 2)
        res["norms"][n] = r
        print(f"N = {n}: " + "  ".join(f"p{q}: H {r[q]['smooth']['H_L2']:.3e} M {r[q]['smooth']['M_L2']:.3e} "
                                       f"(all: H {r[q]['all']['H_L2']:.3e} M {r[q]['all']['M_L2']:.3e})"
                                       for q in (2, 4)), flush=True)
    od = {}
    hs = np.array(res["h"])
    for q in (2, 4):
        for reg in ("smooth", "all"):
            for key in ("H_L2", "M_L2", "H_Linf", "M_Linf"):
                es = np.array([res["norms"][n][q][reg][key] for n in Ns])
                with np.errstate(divide="ignore", invalid="ignore"):
                    od[f"p{q}/{reg}/{key}"] = (np.log(es[:-1] / es[1:]) / np.log(hs[:-1] / hs[1:])).tolist()
    res["orders"] = od
    for k in ("p2/smooth/H_L2", "p2/smooth/M_L2", "p4/smooth/H_L2", "p4/smooth/M_L2", "p2/all/H_L2", "p2/all/M_L2"):
        print(k, np.round(od[k], 3).tolist())
    C.write_json(os.path.join(a.out, "constraints_ds3.json"), res)
    from nrpic import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(8.0, 3.3))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.15, top=0.90, wspace=0.30)
    for j, reg in enumerate(("smooth", "all")):
        ax = fig.add_subplot(1, 2, 1 + j)
        for q, ls in ((2, "-"), (4, "--")):
            ax.loglog(hs, [res["norms"][n][q][reg]["H_L2"] for n in Ns], "o" + ls, color=fs.PAL["red"],
                      label=f"$H$, order-{q} differences")
            ax.loglog(hs, [res["norms"][n][q][reg]["M_L2"] for n in Ns], "s" + ls, color=fs.PAL["blue"],
                      label=f"$|M|$, order-{q} differences")
        h0 = hs[0]
        e0 = res["norms"][Ns[0]][2][reg]["H_L2"]
        ax.loglog(hs, e0 * (hs / h0) ** 2, **fs.GUIDE, label="slope 2")
        ax.set_xlabel(r"cell size $h\,/M$")
        ax.set_ylabel(r"L2 residual $/6H^2$")
        ax.legend(fontsize=6)
        ax.set_title("away from the jumps" if reg == "smooth" else "all cells", fontsize=10)
    fs.save(fig, os.path.join(a.out, "fig_constraints_ds3"))


if __name__ == "__main__":
    main()
