#!/usr/bin/env python3
"""Test 1a of tracks/core/JOURNAL-mp.md: Bowen-York data on the mesh at t = 0 against
the closed forms. Reads the registered runs of run_static.sh, prints one row per run,
writes static_check.json and two figures (figs/static_convergence, figs/static_profile).

Quantities (cells with psi^4 <= 16 are the cells the Z4c history sums over; "far"
means at least 0.75 from every puncture):
  dK     max |K_ij(code) - psi^-2 Abar_ij| / max |K_ij| over cells >= 0.5 from punctures
  Hrms   root mean square of the Hamiltonian residual of the code over the history cells
  Han    the same of the closed form -8 psi^-5 lap(u) - psi^-12 Abar^2
  dH     rms(H code - H closed form) / rms(H closed form, no correction) over far cells
  Mrms   root mean square of the momentum residual sqrt(M_i M^i) over the history cells
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

LABELS = (
    [f"s_p0.0_none_n{n}" for n in (32, 64, 128)]
    + [f"s_p0.3_{c}_n{n}" for c in ("none", "approx", "table") for n in (32, 64, 128)]
    + ["s_p0.3_tablelin_n128"]
    + [f"s_p{p}_{c}_n128" for p in ("0.1", "0.2", "0.4") for c in ("none", "approx")]
    + [f"s_{k}_{c}_n{n}" for k in ("spin", "ps", "two") for c in ("none", "approx")
       for n in (64, 128)])


def analyse(label):
    man = mc.run_by_label(label)
    d = man["output_directory"]
    _, par, x, y, z, dx, con = mc.read_bin(os.path.join(d, "bin", "bys.con.00000.bin"))
    _, _, xa, ya, za, _, adm = mc.read_bin(os.path.join(d, "bin", "bys.adm.00000.bin"))
    assert np.array_equal(x, xa) and np.array_equal(z, za)
    pts = np.stack([x, y, z], axis=-1)
    puncs = mc.punctures(par, d)
    psi, kan, han = mc.closed_forms(pts, puncs)
    # the same closed form without any correction, as the scale of the residual
    bare = [dict(p, corr="none") for p in puncs]
    _, _, hbare = mc.closed_forms(pts, bare)
    rmin = np.min([by._disp(pts, p["pos"])[1] for p in puncs], axis=0)
    hist = adm["adm_psi4"] <= 16.0
    far = rmin >= 0.75
    kcode = np.stack([adm["adm_Kxx"], adm["adm_Kxy"], adm["adm_Kxz"], adm["adm_Kyy"],
                      adm["adm_Kyz"], adm["adm_Kzz"]], axis=-1)
    kref = np.stack([kan[:, 0, 0], kan[:, 0, 1], kan[:, 0, 2], kan[:, 1, 1],
                     kan[:, 1, 2], kan[:, 2, 2]], axis=-1)
    sel = rmin >= 0.5
    kscale = np.max(np.abs(kref[sel])) if np.any(kref[sel] != 0.0) else 1.0
    rms = lambda a: float(np.sqrt(np.mean(a**2)))  # noqa: E731
    out = {"label": label, "run_id": man["run_id"], "n": int(par["mesh"]["nx1"]),
           "dx": float(dx[0]),
           "dK": float(np.max(np.abs(kcode[sel] - kref[sel])) / kscale),
           "dpsi": float(np.max(np.abs(adm["adm_psi4"][sel]**0.25 / psi[sel] - 1.0))),
           "Hrms": rms(con["con_H"][hist]), "Han": rms(han[hist]),
           "Hbare": rms(hbare[hist]),
           "dH": rms((con["con_H"] - han)[far]) / max(rms(hbare[far]), 1e-300),
           "Hfar": rms(con["con_H"][far]), "Hbare_far": rms(hbare[far]),
           "Han_far": rms(han[far]),
           "Mrms": float(np.sqrt(np.mean(con["con_M"][hist]))),
           "Kscale": float(kscale)}
    # line of cells nearest the x axis, for the profile figure
    line = (np.abs(y - 0.5 * dx) < 1e-9) & (np.abs(z - 0.5 * dx) < 1e-9)
    o = np.argsort(x[line])
    prof = {"x": x[line][o], "Hcode": con["con_H"][line][o], "Han": han[line][o],
            "Hbare": hbare[line][o]}
    return out, prof, (pts, con["con_H"], far, hist)


def main():
    figstyle.use_style()
    res, profs, raw = {}, {}, {}
    for lab in LABELS:
        res[lab], profs[lab], raw[lab] = analyse(lab)
    # the Hamiltonian residual minus the residual of the same mesh without curvature is
    # algebraic (K^2 - K_ij K^ij): no truncation error
    for n in (32, 64, 128):
        pts, h0, far, hist = raw[f"s_p0.0_none_n{n}"]
        _, h1, _, _ = raw[f"s_p0.3_none_n{n}"]
        puncs = [{"pos": np.zeros(3), "m": 1.0, "P": np.array([0.3, 0, 0]),
                  "S": np.zeros(3), "corr": "none"}]
        _, _, han = mc.closed_forms(pts, puncs)
        res[f"s_p0.3_none_n{n}"]["dH_algebraic"] = float(
            np.max(np.abs((h1 - h0 - han)[hist])) / np.max(np.abs(han[hist])))

    print(f"{'label':24s} {'run id':30s} {'dx':>7s} {'dK':>9s} {'dpsi':>9s} {'Hrms':>10s}"
          f" {'Han':>10s} {'Hbare':>10s} {'dH':>9s} {'Mrms':>10s}")
    for lab in LABELS:
        r = res[lab]
        print(f"{lab:24s} {r['run_id']:30s} {r['dx']:7.4f} {r['dK']:9.2e} {r['dpsi']:9.2e}"
              f" {r['Hrms']:10.3e} {r['Han']:10.3e} {r['Hbare']:10.3e} {r['dH']:9.2e}"
              f" {r['Mrms']:10.3e}")
    for n in (32, 64, 128):
        print(f"n = {n}: max |H(P=0.3) - H(P=0) - closed form| / max |closed form| = "
              f"{res[f's_p0.3_none_n{n}']['dH_algebraic']:.2e}")
    with open(os.path.join(mc.HERE, "static_check.json"), "w") as f:
        json.dump(res, f, indent=1)

    # ---- figure 1: convergence and scaling with the momentum
    fig, ax = plt.subplots(1, 3, figsize=(figstyle.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.085, right=0.985, bottom=0.17, top=0.93, wspace=0.42)
    dxs = np.array([res[f"s_p0.3_none_n{n}"]["dx"] for n in (32, 64, 128)])
    cols = {"none": figstyle.PAL["blue"], "approx": figstyle.PAL["red"],
            "table": figstyle.PAL["green"]}
    names = {"none": "no correction", "approx": "closed form", "table": "table"}
    for c in ("none", "approx", "table"):
        v = [res[f"s_p0.3_{c}_n{n}"]["dH"] for n in (32, 64, 128)]
        ax[0].loglog(dxs, v, "o-", color=cols[c], label=names[c])
    ax[0].loglog(dxs, res["s_p0.3_none_n128"]["dH"] * (dxs / dxs[-1])**6, **figstyle.GUIDE)
    ax[0].text(0.11, 2.0e-1, r"$\Delta x^6$", fontsize=9)
    ax[0].set_xlabel(r"cell size $\Delta x/m$")
    ax[0].set_ylabel(r"rms$(H-H_{\rm closed})$ / rms$(H_{\rm BL})$, $r\geq0.75m$")
    ax[0].legend(fontsize=8, loc="lower right")
    for c in ("none", "approx", "table"):
        v = [res[f"s_p0.3_{c}_n{n}"]["Mrms"] for n in (32, 64, 128)]
        ax[1].loglog(dxs, v, "o-", color=cols[c], label=names[c])
    ax[1].loglog(dxs, res["s_p0.3_none_n128"]["Mrms"] * (dxs / dxs[-1])**6, **figstyle.GUIDE)
    ax[1].set_xlabel(r"cell size $\Delta x/m$")
    ax[1].set_ylabel(r"rms momentum residual, $\psi\leq2$")
    ps = np.array([0.1, 0.2, 0.3, 0.4])
    for c in ("none", "approx"):
        v = [res[f"s_p{p}_{c}_n128"]["Hrms"] for p in ("0.1", "0.2", "0.3", "0.4")]
        ax[2].loglog(ps, v, "o-", color=cols[c], label=names[c])
        va = [res[f"s_p{p}_{c}_n128"]["Han"] for p in ("0.1", "0.2", "0.3", "0.4")]
        ax[2].loglog(ps, va, "x", color="k", ms=5)
    ax[2].axhline(res["s_p0.0_none_n128"]["Hrms"], **figstyle.MASK_LINE)
    ax[2].text(0.105, res["s_p0.0_none_n128"]["Hrms"] * 1.25, "P = 0 (truncation)",
               fontsize=8)
    h3 = res["s_p0.3_none_n128"]["Han"]
    ax[2].loglog(ps, h3 * (ps / 0.3)**2, **figstyle.GUIDE)
    h3a = res["s_p0.3_approx_n128"]["Han"]
    ax[2].loglog(ps, h3a * (ps / 0.3)**4, **figstyle.GUIDE)
    ax[2].text(0.22, h3 * 0.25, r"$P^2$", fontsize=9)
    ax[2].text(0.22, h3a * 0.12, r"$P^4$", fontsize=9)
    ax[2].set_xlabel(r"momentum $P/m$")
    ax[2].set_ylabel(r"rms $H$, $\psi\leq2$, $\Delta x=m/16$")
    ax[2].legend(fontsize=8, loc="lower right")
    print("figure:", mc.savefig(fig, "static_convergence"))

    # ---- figure 2: residual along the line of cells nearest the x axis, dx = 1/16
    fig, ax = plt.subplots(1, 2, figsize=(figstyle.FULL_WIDTH, 3.0), sharey=True)
    fig.subplots_adjust(left=0.085, right=0.985, bottom=0.16, top=0.93, wspace=0.05)
    for a, (case, title) in zip(ax, (("p0.3", r"one puncture, $P=0.3m$ along $x$"),
                                     ("two", "two punctures with momenta and a spin"))):
        for c in ("none", "approx") + (("table",) if case == "p0.3" else ()):
            p = profs[f"s_{case}_{c}_n128"]
            a.semilogy(p["x"], np.abs(p["Hcode"]), color=cols[c], label=names[c])
            a.semilogy(p["x"], np.abs(p["Han"]), color="k", lw=0.8, ls="--")
        if case == "p0.3":
            p = profs["s_p0.0_none_n128"]
            a.semilogy(p["x"], np.abs(p["Hcode"]), color="grey", alpha=0.6, lw=1.0,
                       label="P = 0 (truncation)")
        a.set_xlabel(r"$x/m$")
        a.set_title(title, fontsize=10)
        a.set_ylim(1e-11, 3e0)
        a.set_xlim(-4, 4)
    ax[0].set_ylabel(r"$|H|$ on the cells nearest the $x$ axis")
    ax[0].legend(fontsize=8, loc="upper right")
    print("figure:", mc.savefig(fig, "static_profile"))


if __name__ == "__main__":
    main()
