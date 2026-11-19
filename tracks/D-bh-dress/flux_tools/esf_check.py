#!/usr/bin/env python3
"""Checks of the ES-F data and of its predicted growth law (journal entry 4).

    esf_check.py [--out DIR]

1. Offline constraints of the format-2 table, evaluated with the problem generator's rule
   (es_model.Tab2: four-point Lagrange) at points between the rows, for drbar = 0.04,
   0.02, 0.01: Hamiltonian residual 4 KL KT + 2 KT^2 - 16 pi rho (R_3 = 0 exactly, psi =
   1 + M/(2 rbar) is harmonic) and momentum residual dKT/dR - (KL - KT)/R (S_i = 0),
   with dKT/dR from the interpolant; maximum over 0.6 <= rbar <= 330 M and the order.
2. The exact LTB growth law M_AH(tau) = m(R0) at tau = tau_H(R0) against the Newtonian
   secondary-infall reference of wave 2 (secondary_infall/shells.py, absorbing mode,
   capture at r = 2M), run here with eps = H M of ES-1, the vacuum core and ball edge
   matched in mass to the smooth edges of ES-F.
Writes esf_check.json and esf_check.png.
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "secondary_infall"))
import esf_data  # noqa: E402
import compare as cmp  # noqa: E402


def residuals(fb, drbar, rb):
    tab = fb.table(drbar, 345.0)
    ev = tab.evaluate(rb)
    h = 1e-4 * drbar
    KTp = tab.evaluate(rb + h)["KT"]
    KTm = tab.evaluate(rb - h)["KT"]
    R = fb.areal(rb)
    psi = fb.psi(rb)
    dRdr = psi * (1.0 - fb.M / (2.0 * rb))
    dKTdR = (KTp - KTm) / (2 * h) / dRdr
    H = 4.0 * ev["KL"] * ev["KT"] + 2.0 * ev["KT"] ** 2 - 16.0 * math.pi * fb.density(R)
    Mo = dKTdR - (ev["KL"] - ev["KT"]) / R
    return H, Mo, R


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    fb = esf_data.FilledBubble()
    rng = np.random.default_rng(7)
    rb = np.sort(rng.uniform(0.6, 330.0, 20000))
    res = {"constraints": {}}
    curves = {}
    for d in (0.04, 0.02, 0.01):
        H, Mo, R = residuals(fb, d, rb)
        curves[d] = (H, Mo)
        res["constraints"][str(d)] = dict(H_max=float(np.abs(H).max()),
                                          H_max_rel=float(np.abs(H).max() / (16 * math.pi * fb.rho0)),
                                          M_max=float(np.abs(Mo).max()))
    c = res["constraints"]
    res["order_H"] = [math.log2(c["0.04"]["H_max"] / c["0.02"]["H_max"]),
                      math.log2(c["0.02"]["H_max"] / c["0.01"]["H_max"])]
    res["order_M"] = [math.log2(c["0.04"]["M_max"] / c["0.02"]["M_max"]),
                      math.log2(c["0.02"]["M_max"] / c["0.01"]["M_max"])]
    # growth law: exact LTB against the absorbing shells of wave 2
    import shells
    Rg = np.geomspace(fb.Rin * 1.0001, fb.Rout, 4000)
    sg = fb.shell_times(Rg)
    k43 = 4.0 * math.pi * fb.rho0 / 3.0
    Rc3 = 125.0 - float(fb.D(np.array([5.0]))[0]) / k43        # mass-matched sharp core
    Rb3 = Rc3 + fb.Dtot / k43                                   # mass-matched sharp edge
    eps = fb.H * fb.M
    t_i = 2.0 / (3.0 * eps)
    a_end = ((t_i + 700.0) / t_i) ** (2.0 / 3.0)
    cfg = dict(eps=eps, mode="absorb", soft=0.0, r_abs=2.0, mu_core=eps ** 2 * Rc3 / 2.0,
               mu_max=eps ** 2 * Rb3 / 2.0, n=3000, a_end=a_end, sigma=0.0, nj=1, vac_core=True)
    sres = shells.run(cfg, [], eta=0.02, log_every=20)
    ser = sres["series"]
    tau_s, M_s = ser[:, 0] - t_i, ser[:, 1]
    M_ltb = np.interp(tau_s, sg["tauH"], sg["m"])
    sel = tau_s <= 600.0
    res["shells_cfg"] = dict(cfg, R_core=Rc3 ** (1 / 3), R_edge=Rb3 ** (1 / 3), t_i=t_i)
    res["growth_ltb_minus_shells"] = dict(max=float((M_ltb - M_s)[sel].max()),
                                          min=float((M_ltb - M_s)[sel].min()))
    res["growth_table"] = {f"tau={t:g}": dict(LTB=float(np.interp(t, sg["tauH"], sg["m"])),
                                               shells=float(np.interp(t, tau_s, M_s)))
                           for t in (25, 50, 100, 150, 200, 250, 300, 400, 600)}
    res["shells_wall_s"] = sres["wall"]
    figure(a.out, fb, rb, curves, sg, tau_s, M_s, M_ltb)
    with open(os.path.join(a.out, "esf_check.json"), "w") as f:
        json.dump(cmp.jsonable(res), f, indent=1)
    print(json.dumps(cmp.jsonable(res), indent=1))


def figure(out, fb, rb, curves, sg, tau_s, M_s, M_ltb):
    sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "python", "nrpic"))
    import figstyle
    import matplotlib.pyplot as plt
    figstyle.use_style()
    fig, ax = plt.subplots(1, 3, figsize=(figstyle.FULL_WIDTH, 2.9))
    for d, c in zip((0.04, 0.02, 0.01), figstyle.SERIES):
        H, Mo = curves[d]
        ax[0].semilogy(rb, np.abs(H) / (16 * math.pi * fb.rho0) + 1e-30, ".", ms=0.6, color=c,
                       label=rf"$\Delta\bar r={d:g}$")
        ax[1].semilogy(rb, np.abs(Mo) + 1e-30, ".", ms=0.6, color=c, label=rf"$\Delta\bar r={d:g}$")
    for a_ in ax[:2]:
        a_.set_xscale("log")
        a_.set_xlabel(r"$\bar r\ [M]$")
        a_.legend(fontsize=6, markerscale=8)
    ax[0].set_ylabel(r"$|\mathcal{H}|/(16\pi\rho_0)$")
    ax[1].set_ylabel(r"$|\mathcal{M}_r|$")
    a = ax[2]
    a.plot(sg["tauH"], sg["m"], color=figstyle.PAL["blue"], label="exact LTB, capture at $R=2m$")
    a.plot(tau_s, M_s, color=figstyle.PAL["red"], ls="--", label="shells (wave 2), capture at $r=2M$")
    a.set_xlim(0, 650)
    a.set_ylim(1, 1.65)
    a.set_xlabel(r"$\tau\ [M]$ (proper time since the initial slice)")
    a.set_ylabel(r"$M_{\rm BH}\ [M]$")
    ins = a.inset_axes([0.55, 0.12, 0.42, 0.35])
    ins.plot(tau_s, (M_ltb - M_s) * 1e3, color="k", lw=0.8)
    ins.set_xlim(0, 650)
    ins.set_ylabel(r"$10^3\Delta M$", fontsize=6)
    ins.tick_params(labelsize=6)
    a.legend(fontsize=6, loc="upper left")
    fig.tight_layout()
    figstyle.save(fig, os.path.join(out, "esf_check"))
    plt.close(fig)


if __name__ == "__main__":
    main()
