#!/usr/bin/env python3
"""Test 1 of the work package "id": Hamiltonian and momentum residuals of the expanding
ball at the start, by region, against resolution and particle number.

Reads the field dump of the start (`ball.field.00000.bin`) of the registered runs with
tag t1-*, writes `test1_numbers.json` and the figures `figs/t1_*.png|pdf`.

Regions (r the coordinate radius of a cell centre, dx the cell size, R_in and R_out the
inner and outer radius of the edge of the matter; R_in = R_out = R_b for a sharp
surface):
    interior   r < R_in - 4 dx          surface   R_in - 4 dx <= r <= R_out + 4 dx
    exterior   R_out + 4 dx < r < 30    fixed regions r < 4 and 16 < r < 30 for the
                                        comparison between resolutions
Norms: largest absolute value, mean absolute value, root mean square; for the surface
also the integral of the absolute value over the mesh (sum |.| dx^3).
|M| = sqrt(gamma^ij M_i M_j) with gamma^ij = chi delta^ij (conformally flat start).
"""
import json
import math
import os

import numpy as np

import idlib
from nrpic import figstyle as fs
import matplotlib.pyplot as plt

HALF = 32.0
RB = 10.0


def norms(a, mask, dv):
    v = np.abs(a[mask])
    if v.size == 0:
        return dict(max=float("nan"), mean=float("nan"), rms=float("nan"), integral=0.0, cells=0)
    return dict(max=float(v.max()), mean=float(v.mean()), rms=float(np.sqrt(np.mean(v * v))),
                integral=float(v.sum() * dv), cells=int(v.size))


def analyse(man):
    meta = idlib.run_meta(man)
    fld = idlib.read_field(os.path.join(man["output_directory"], "ball.field.00000.bin"))
    n = fld["n"][0]
    dx = 2.0 * HALF / n
    r = idlib.cell_radius(fld["n"], HALF)
    edge = meta["edge"]
    rin, rout = RB - edge, RB + edge
    mabs = np.sqrt(fld["chi"] * (fld["Mx"] ** 2 + fld["My"] ** 2 + fld["Mz"] ** 2))
    reg = dict(interior=r < rin - 4.0 * dx,
               surface=(r >= rin - 4.0 * dx) & (r <= rout + 4.0 * dx),
               exterior=(r > rout + 4.0 * dx) & (r < 30.0),
               interior_fixed=r < 4.0,
               exterior_fixed=(r > 16.0) & (r < 30.0))
    out = dict(tag=man["tag"], run_id=man["run_id"], cells=n, dx=dx, h=meta["lattice_h"],
               q=dx / meta["lattice_h"], edge=edge, N=meta["particles"]["N_ball"],
               rho0=meta["rho0"], H0=meta["H"],
               sum_m_over_rest_mass=meta["particles"]["sum_m_over_rest_mass"])
    for name, mask in reg.items():
        out[name] = dict(H=norms(fld["H"], mask, dx ** 3), M=norms(mabs, mask, dx ** 3))
    # radial profile: shells of width dx
    edges = np.arange(0.0, 30.0 + dx, dx)
    idx = np.digitize(r.ravel(), edges) - 1
    ok = (idx >= 0) & (idx < len(edges) - 1)
    cnt = np.bincount(idx[ok], minlength=len(edges) - 1)
    h2 = np.bincount(idx[ok], weights=(fld["H"].ravel()[ok]) ** 2, minlength=len(edges) - 1)
    m2 = np.bincount(idx[ok], weights=(mabs.ravel()[ok]) ** 2, minlength=len(edges) - 1)
    prof = dict(r=0.5 * (edges[1:] + edges[:-1]), H=np.sqrt(h2 / np.maximum(cnt, 1)),
                M=np.sqrt(m2 / np.maximum(cnt, 1)))
    return out, prof


def main():
    mans = idlib.manifests("t1-")
    res, prof = {}, {}
    for tag, man in sorted(mans.items()):
        res[tag[3:]], prof[tag[3:]] = analyse(man)
    os.makedirs(idlib.FIGS, exist_ok=True)
    with open(os.path.join(idlib.HERE, "test1_numbers.json"), "w") as f:
        json.dump(res, f, indent=1)
        f.write("\n")

    rho0 = next(iter(res.values()))["rho0"]
    h0 = next(iter(res.values()))["H0"]
    href = 16.0 * math.pi * rho0
    print(f"16 pi rho_0 = {href:.6e}, H = {h0:.6e}, 3H/(2 dx) is the jump of KL over a cell")
    hdr = ("case", "cells", "q", "N", "int Hmax", "int Hrms", "int Mmax", "srf Hmax",
           "srf H int", "srf Mmax", "srf M int", "ext Hmax", "ext Mmax", "ext Mrms")
    print(("%-22s %5s %5s %8s" + " %9s" * 10) % hdr)
    for k, v in res.items():
        print(("%-22s %5d %5.2f %8d" + " %9.2e" * 10) % (
            k, v["cells"], v["q"], v["N"], v["interior"]["H"]["max"], v["interior"]["H"]["rms"],
            v["interior"]["M"]["max"], v["surface"]["H"]["max"], v["surface"]["H"]["integral"],
            v["surface"]["M"]["max"], v["surface"]["M"]["integral"], v["exterior"]["H"]["max"],
            v["exterior_fixed"]["M"]["max"], v["exterior_fixed"]["M"]["rms"]))

    fs.use_style()
    seq = [k for k in ("sharp-n064-q1", "sharp-n096-q1", "sharp-n128-q1", "sharp-n192-q1",
                       "sharp-n256-q1") if k in res]

    # ---- figure 1: vacuum exterior against resolution
    if len(seq) >= 2:
        dx = np.array([res[k]["dx"] for k in seq])
        fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2))
        fig.subplots_adjust(left=0.09, right=0.98, bottom=0.15, top=0.95, wspace=0.28)
        mrms = np.array([res[k]["exterior_fixed"]["M"]["rms"] for k in seq])
        mmax = np.array([res[k]["exterior_fixed"]["M"]["max"] for k in seq])
        ax[0].loglog(dx, mmax, "o-", color=fs.PAL["red"], label="largest value")
        ax[0].loglog(dx, mrms, "s-", color=fs.PAL["yellow"], label="root mean square")
        ax[0].loglog(dx, mmax[0] * (dx / dx[0]) ** 6, **fs.GUIDE, label=r"$\propto \Delta x^6$")
        ax[0].set_xlabel(r"cell size $\Delta x/M$", labelpad=-2)
        ax[0].set_ylabel(r"momentum residual $|M_i|$, $16<r/M<30$")
        ax[0].legend()
        hmax = np.array([res[k]["exterior"]["H"]["max"] for k in seq])
        himax = np.array([res[k]["interior"]["H"]["max"] for k in seq])
        mimax = np.array([res[k]["interior"]["M"]["max"] for k in seq])
        ax[1].loglog(dx, np.maximum(hmax, 1e-20) / href, "o-", color=fs.PAL["red"],
                     label=r"exterior $|H|/16\pi\rho_0$")
        ax[1].loglog(dx, np.maximum(himax, 1e-20) / href, "s-", color=fs.PAL["blue"],
                     label=r"interior $|H|/16\pi\rho_0$")
        ax[1].loglog(dx, np.maximum(mimax, 1e-20) / (h0 / RB), "^-", color=fs.PAL["green"],
                     label=r"interior $|M_i| R_b/H$")
        ax[1].set_xlabel(r"cell size $\Delta x/M$", labelpad=-2)
        ax[1].set_ylabel("largest residual away from the surface")
        ax[1].legend()
        fs.save(fig, os.path.join(idlib.FIGS, "t1_exterior"))
        plt.close(fig)
        slopes = np.log(mmax[:-1] / mmax[1:]) / np.log(dx[:-1] / dx[1:])
        print("order of the exterior momentum residual between successive meshes:",
              " ".join(f"{s:.2f}" for s in slopes))

    # ---- figure 2: radial profiles, sharp surface and smooth edge
    fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.4), sharex=True)
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.09, top=0.96, wspace=0.26, hspace=0.06)
    for col, fam in enumerate(("sharp", "edge2")):
        keys = [k for k in (f"{fam}-n064-q1", f"{fam}-n128-q1", f"{fam}-n256-q1") if k in res]
        for k, c in zip(keys, fs.series_colors(max(len(keys), 1))):
            p = prof[k]
            lab = r"$\Delta x=%g\,M$" % res[k]["dx"]
            ax[0, col].semilogy(p["r"], np.maximum(p["H"], 1e-22) / href, color=c, label=lab)
            ax[1, col].semilogy(p["r"], np.maximum(p["M"], 1e-22) / (h0 / RB), color=c, label=lab)
        for a in ax[:, col]:
            edge = 0.0 if fam == "sharp" else 2.0
            a.axvline(RB - edge, **fs.MASK_LINE)
            a.axvline(RB + edge, **fs.MASK_LINE)
            a.set_ylim(1e-17, 30.0)
        ax[0, col].legend(title="sharp surface" if fam == "sharp" else "smooth edge, $w=2\\,M$")
        ax[1, col].set_xlabel(r"coordinate radius $r/M$", labelpad=-2)
    ax[0, 0].set_ylabel(r"rms of $|H|/16\pi\rho_0$ in shells")
    ax[1, 0].set_ylabel(r"rms of $|M_i|\,R_b/H$ in shells")
    fs.save(fig, os.path.join(idlib.FIGS, "t1_profiles"))
    plt.close(fig)

    # ---- figure 3: surface layer against resolution
    fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.4), sharex=True)
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.09, top=0.96, wspace=0.26, hspace=0.06)
    fams = (("sharp", "sharp surface", fs.PAL["red"]), ("edge1", "edge $w=1\\,M$", fs.PAL["yellow"]),
            ("edge2", "edge $w=2\\,M$", fs.PAL["blue"]))
    for fam, lab, c in fams:
        keys = sorted([k for k in res if k.startswith(fam + "-n") and k.endswith("-q1")],
                      key=lambda k: -res[k]["dx"])
        if not keys:
            continue
        dx = np.array([res[k]["dx"] for k in keys])
        for i, (fld, scale) in enumerate((("H", href), ("M", h0 / RB))):
            ax[0, i].loglog(dx, [res[k]["surface"][fld]["max"] / scale for k in keys], "o-",
                            color=c, label=lab)
            ax[1, i].loglog(dx, [res[k]["surface"][fld]["integral"] / scale for k in keys], "o-",
                            color=c, label=lab)
    dxg = np.array([0.25, 1.0])
    ax[0, 1].loglog(dxg, 40.0 / dxg, **fs.GUIDE, label=r"$\propto 1/\Delta x$")
    ax[1, 0].loglog(dxg, 2.0e3 * dxg, **fs.GUIDE, label=r"$\propto \Delta x$")
    ax[1, 1].loglog(dxg, 30.0 * dxg ** 2, color="k", ls=":", label=r"$\propto \Delta x^2$")
    ax[0, 0].set_ylabel("largest value in the surface layer")
    ax[1, 0].set_ylabel(r"$\int |\cdot|\,dV$ over the surface layer [$M^3$]")
    ax[1, 0].set_xlabel(r"cell size $\Delta x/M$", labelpad=-2)
    ax[1, 1].set_xlabel(r"cell size $\Delta x/M$", labelpad=-2)
    ax[0, 0].set_title(r"$|H|/16\pi\rho_0$")
    ax[0, 1].set_title(r"$|M_i|\,R_b/H$")
    for a in ax.ravel():
        a.legend()
    fs.save(fig, os.path.join(idlib.FIGS, "t1_surface"))
    plt.close(fig)

    # ---- figure 4: interior against the lattice
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.15, top=0.95, wspace=0.28)
    k128 = sorted([k for k in res if k.startswith("sharp-n128-q") and "-s0" not in k],
                  key=lambda k: res[k]["q"])
    for nf, c, lab in ((1, fs.PAL["red"], "one binomial pass"), (0, fs.PAL["yellow"], "no pass")):
        ks = [k for k in k128 if k.endswith("-nf0") == (nf == 0)]
        if not ks:
            continue
        q = np.array([res[k]["q"] for k in ks])
        v = np.array([res[k]["interior"]["H"]["rms"] for k in ks]) / href
        ax[0].semilogy(q, np.maximum(v, 1e-18), "o", color=c, label=lab)
    qq = np.linspace(1.0, 4.2, 400)
    model = 2.0 * np.sin(math.pi * qq) ** 2 / (math.pi * qq) ** 2 * math.sqrt(1.5)
    ax[0].semilogy(qq, np.maximum(model, 1e-18), color="k", ls=":", lw=1.0,
                   label="cloud-in-cell estimate, no pass")
    resp = np.cos(math.pi * (qq - np.round(qq))) ** 2
    ax[0].semilogy(qq, np.maximum(model * resp, 1e-18), **fs.GUIDE,
                   label="estimate with the pass")
    ax[0].set_ylim(1e-17, 1.0)
    ax[0].set_xlabel(r"lattice sites per cell and direction $q=\Delta x/h$", labelpad=-2)
    ax[0].set_ylabel(r"interior rms of $|H|/16\pi\rho_0$")
    ax[0].legend(loc="center right", fontsize=8)
    kq = sorted([k for k in res if k.endswith("-q1p25")], key=lambda k: -res[k]["dx"])
    if kq:
        dx = [res[k]["dx"] for k in kq]
        ax[1].loglog(dx, [res[k]["interior"]["H"]["rms"] / href for k in kq], "o-",
                     color=fs.PAL["red"], label="rms, $q=1.25$")
        ax[1].loglog(dx, [res[k]["interior"]["H"]["max"] / href for k in kq], "s-",
                     color=fs.PAL["yellow"], label="largest, $q=1.25$")
        ax[1].set_ylim(1e-3, 1.0)
    ax[1].set_xlabel(r"cell size $\Delta x/M$", labelpad=-2)
    ax[1].set_ylabel(r"interior $|H|/16\pi\rho_0$")
    ax[1].legend()
    fs.save(fig, os.path.join(idlib.FIGS, "t1_interior"))
    plt.close(fig)


if __name__ == "__main__":
    main()
