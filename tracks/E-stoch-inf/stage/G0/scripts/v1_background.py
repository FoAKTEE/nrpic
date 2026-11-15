#!/usr/bin/env python3
"""V1 of the G0 verifier: background of the SR and USR cases from the printed parameters.

Recomputes the 'Derived' row of SCOPE.md section 2 with the cosmic-time integrator of
common.py (not the track's e-fold integrator) and tries to break it with the other reading
of the H0-fixing velocity. Writes v1.json and fig_v1_background.png into --out.
"""
import argparse
import os

import numpy as np

import common
from common import Background, inflection, quadratic, save_json


def usr_interval(bg, Nstar, thr=3.0):
    g = bg.grid(20000)
    cN = g["N"] - Nstar
    above = g["eps2"] > thr
    idx = np.where(np.diff(above.astype(int)) != 0)[0]
    out = []
    for i in idx:                              # linear interpolation of the crossing
        x0, x1 = cN[i], cN[i + 1]
        y0, y1 = g["eps2"][i] - thr, g["eps2"][i + 1] - thr
        out.append(x0 - y0 * (x1 - x0) / (y1 - y0))
    return out, g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = {}
    grids = {}
    alt = inflection("dt")
    H_alt = alt["H0"]
    res["USR_dt"] = dict(phidot0=alt["phidot0"], H0=H_alt,
                         eps1_0=0.5 * (alt["phidot0"] / H_alt) ** 2,
                         note="dphi/dt = -V'/V in Mpl = 1 units: kinetic domination, eps1 near 3, "
                              "no inflation; this reading is not viable")
    print("USR_dt", res["USR_dt"])
    for mdl in (quadratic(), inflection("dN")):
        bg = Background(mdl)
        Ns = mdl["dNstar"]
        s0 = bg.at_N(0.0)
        ss = bg.at_N(Ns)
        sf = bg.at_N(Ns + mdl["dNsim"])
        r = dict(phi0=mdl["phi0"], dphidN0=mdl["phidot0"] / mdl["H0"], H0=mdl["H0"],
                 m=mdl.get("m"), H_star=ss["H"], eps1_star=ss["eps1"], eps2_star=ss["eps2"],
                 V_star_Mpl100=ss["V"] * 1e8, V_f_Mpl100=sf["V"] * 1e8,
                 eps1_f=sf["eps1"], eps2_f=sf["eps2"], phi_f=sf["phi"],
                 tH_star_span=(sf["tau"] - ss["tau"]) * mdl["H0"] / 1.0)
        # cosmic-time span in units of 1/H*: int dN/H * H*
        r["t_span_Hstar"] = (sf["tau"] - ss["tau"]) / mdl["H0"] * ss["H"]
        iv, g = usr_interval(bg, Ns)
        r["eps2_gt3_crossings_cN"] = iv
        cN = g["N"] - Ns
        sel = (cN > 0) & (cN < mdl["dNsim"])
        r["eps1_min"] = float(g["eps1"][sel].min())
        r["cN_eps1_min"] = float(cN[sel][np.argmin(g["eps1"][sel])])
        r["eps2_max"] = float(g["eps2"][sel].max())
        r["eps1_max"] = float(g["eps1"][sel].max())
        r["cN_eps1_max"] = float(cN[sel][np.argmax(g["eps1"][sel])])
        res[mdl["name"]] = r
        grids[mdl["name"]] = (cN, g)
        print(mdl["name"], {k: v for k, v in r.items()})

    # claims of SCOPE.md section 2 / SPEC.md section 6
    claims = {
        "SR": dict(phi0=-14.0950, m=1.73494e-6, H_star=9.48692e-6, eps1_star=1.1107e-2,
                   eps2_star=-2.213e-2, V_star_Mpl100=2.690e-2, eps1_f=1.350e-2),
        "USR": dict(dphidN0=0.102682, H0=9.5902e-6, H_star=9.36232e-6, eps1_star=1.3164e-2,
                    eps2_star=-0.4307, V_star_Mpl100=2.618e-2, eps1_f=1.008e-12,
                    eps1_min=9.7e-13),
    }
    comp = {}
    for case, cl in claims.items():
        comp[case] = {k: dict(claim=v, mine=res[case][k],
                              rel=abs(res[case][k] / v - 1)) for k, v in cl.items()}
    comp["USR"]["interval"] = dict(claim=[2.53, 6.55], mine=res["USR"]["eps2_gt3_crossings_cN"])
    res["comparison"] = comp
    save_json(os.path.join(a.out, "v1.json"), res)

    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(2, 2, figsize=(8.0, 4.6), sharex="col")
    fig.subplots_adjust(left=0.13, right=0.98, bottom=0.11, top=0.93, wspace=0.3, hspace=0.08)
    cols = dict(SR=fs.PAL["blue"], USR=fs.PAL["red"], USR_dt=fs.PAL["yellow"])
    for j, case in enumerate(["SR", "USR"]):
        cN, g = grids[case]
        sel = (cN > -0.2) & (cN < (8.2 if case == "SR" else 10.2))
        ax[0, j].semilogy(cN[sel], g["eps1"][sel], color=cols[case])
        ax[1, j].plot(cN[sel], g["eps2"][sel], color=cols[case])
        ax[0, j].set_title({"SR": "quadratic (SR)", "USR": "inflection (USR)"}[case])
        ax[1, j].axhline(3.0, **fs.GUIDE)
        ax[1, j].set_xlabel(r"$N-N^\ast$", labelpad=-2)
    ax[0, 0].set_ylabel(r"$\varepsilon_1$")
    ax[1, 0].set_ylabel(r"$\varepsilon_2=-d\ln\varepsilon_1/dN$")
    for x in res["USR"]["eps2_gt3_crossings_cN"]:
        ax[1, 1].axvline(x, **fs.MASK_LINE)
    for x in (2.53, 6.55):
        ax[1, 1].axvline(x, color="k", lw=1.0, ls=":")
    fig.savefig(os.path.join(a.out, "fig_v1_background.png"))
    print("comparison:")
    for case in comp:
        for k, v in comp[case].items():
            print(case, k, v)


if __name__ == "__main__":
    main()
