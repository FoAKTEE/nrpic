#!/usr/bin/env python3
"""Test 3 of tracks/core/JOURNAL-mp.md at t = 0: Hamiltonian residual of the
three-black-hole data on the mesh for no correction, the closed-form corrections with
the background factor, and their plain sum. Reads the registered runs t0_triple_*,
prints norms formed as the Z4c history forms them (outputs/history.cpp: sum of
H^2 sqrt(gamma) dV over the cells with psi^4 <= 16, divided by the sum of sqrt(gamma) dV
over the same cells, square root), for the code and for the closed form on the same
cells, in total and by region, writes triple_static.json and figs/triple_static.
"""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mp_common as mc  # noqa: E402
from mp_common import by, figstyle  # noqa: E402

CASES = {"none": ("t0_triple_none", "no correction", figstyle.PAL["blue"]),
         "approx": ("t0_triple_approx", "closed form, background factor",
                    figstyle.PAL["red"]),
         "plain": ("t0_triple_plain", "closed form, plain sum", figstyle.PAL["yellow"])}


def main():
    figstyle.use_style()
    res, prof = {}, {}
    for key, (label, _, _) in CASES.items():
        man = mc.run_by_label(label)
        d = man["output_directory"]
        _, par, x, y, z, dx, con = mc.read_bin(os.path.join(d, "bin", "by3.con.00000.bin"))
        _, _, _, _, _, _, adm = mc.read_bin(os.path.join(d, "bin", "by3.adm_psi4.00000.bin"))
        hst = mc.read_hst(os.path.join(d, "by3.z4c.user.hst"))
        pts = np.stack([x, y, z], axis=-1)
        puncs = mc.punctures(par, d)
        _, _, han = mc.closed_forms(pts, puncs)
        dv = dx**3 * adm["adm_psi4"]**1.5            # proper volume, sqrt(gamma) = psi^6
        hist = adm["adm_psi4"] <= 16.0
        vol = float(np.sum(dv[hist]))
        rb = np.sqrt((x + 88.0)**2 + y**2 + z**2)      # from the centre of the binary
        rh = np.sqrt((x - 8.0)**2 + y**2 + z**2)       # from the heavy black hole
        regions = {"all": hist, "binary (r < 30)": hist & (rb < 30.0),
                   "heavy (r < 60)": hist & (rh < 60.0),
                   "rest": hist & (rb >= 30.0) & (rh >= 60.0)}
        norm = lambda a, sel: float(np.sqrt(np.sum(a[sel]**2 * dv[sel]) / vol))  # noqa: E731
        e = {"run_id": man["run_id"], "blocks": int(len(x) // 4096),
             "lam": [p.get("lam", 1.0) for p in puncs],
             "volume": vol, "hst_volume": float(hst["Volume"][0]),
             "hst_H": float(np.sqrt(hst["H-norm2"][0] / hst["Volume"][0])),
             "hst_M": float(np.sqrt(hst["M-norm2"][0] / hst["Volume"][0]))}
        for name, sel in regions.items():
            e[name] = {"code": norm(con["con_H"], sel), "closed": norm(han, sel),
                       "diff": norm(con["con_H"] - han, sel)}
        res[key] = e
        # cells nearest the line through the two light holes (x = -88, z = 0) and
        # nearest the x axis through the heavy one
        zl = np.abs(z) <= 0.5 * dx + 1e-9
        la = zl & (np.abs(x + 88.0) <= 0.5 * dx + 1e-9) & (z > 0) & (x > -88.0)
        lb = zl & (np.abs(y) <= 0.5 * dx + 1e-9) & (z > 0) & (y > 0) & (np.abs(x - 8) < 60)
        oa, ob = np.argsort(y[la]), np.argsort(x[lb])
        prof[key] = {"ya": y[la][oa], "Ha": con["con_H"][la][oa], "Hca": han[la][oa],
                     "xb": x[lb][ob], "Hb": con["con_H"][lb][ob], "Hcb": han[lb][ob]}

    for key, e in res.items():
        print(f"{key:7s} {e['run_id']}  blocks {e['blocks']}  Lambda {np.round(e['lam'], 4)}"
              f"  history: H {e['hst_H']:.3e}  M {e['hst_M']:.3e}  volume"
              f" {e['hst_volume']:.6e} (cells: {e['volume']:.6e})")
        for name in ("all", "binary (r < 30)", "heavy (r < 60)", "rest"):
            r = e[name]
            print(f"   {name:16s} code {r['code']:.3e}  closed form {r['closed']:.3e}"
                  f"  difference {r['diff']:.3e}")
    with open(os.path.join(mc.HERE, "triple_static.json"), "w") as f:
        json.dump(res, f, indent=1)

    fig, ax = plt.subplots(1, 2, figsize=(figstyle.FULL_WIDTH, 3.0), sharey=True)
    fig.subplots_adjust(left=0.085, right=0.985, bottom=0.16, top=0.92, wspace=0.05)
    for key, (_, name, col) in CASES.items():
        p = prof[key]
        ax[0].semilogy(p["ya"], np.abs(p["Ha"]), color=col, label=name)
        ax[0].semilogy(p["ya"], np.abs(p["Hca"]), color="k", lw=0.8, ls="--")
        ax[1].semilogy(p["xb"], np.abs(p["Hb"]), color=col)
        ax[1].semilogy(p["xb"], np.abs(p["Hcb"]), color="k", lw=0.8, ls="--")
    ax[0].set_xlim(-12, 12)
    ax[0].set_ylim(1e-10, 1e1)
    ax[0].set_xlabel(r"$y$ along the line through the light black holes")
    ax[0].set_ylabel(r"$|H|$ at $t=0$")
    ax[0].set_title("binary, masses 0.5 + 0.5", fontsize=10)
    ax[0].legend(fontsize=8, loc="lower center")
    ax[1].set_xlim(-50, 66)
    ax[1].set_xlabel(r"$x$ along the axis through the heavy black hole")
    ax[1].set_title("black hole of mass 10 with spin", fontsize=10)
    print("figure:", mc.savefig(fig, "triple_static"))


if __name__ == "__main__":
    main()
