#!/usr/bin/env python3
"""G1 test of A-pre-1: finite-difference constraint residuals of the expanding-ball data on
meshes of increasing resolution, with the measured order, and the interpolation error of
the format-2 table against its spacing. Registers one run; figures go to the run directory
and to expball/figures/.

    run_convergence.py [--Ns 32,64,128,256] [--orders 2,4]
"""

import argparse
import json
import math
import os
import shutil
import sys
import time

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")
_PKG = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, _PKG)

import numpy as np  # noqa: E402

from expball import mesh, model as M, runlog, table  # noqa: E402

REPO = os.path.normpath(os.path.join(_PKG, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))
from nrpic import figstyle as fs  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HRB, RB = 0.5, 8.0
CORE = dict(delta_c=1.0, R1=0.3 * RB, R2=0.75 * RB)


def models():
    return {
        "flat": (M.Ball.from_HRb(HRB), "nonsmooth: R_b"),
        "flat_taper": (M.Ball.from_HRb(HRB, edge_width=0.1 * RB), "C^4 taper, |R - R_b| < 0.1 R_b"),
        "tophat": (M.Ball.from_HRb(HRB, profile=M.TopHat(**CORE)), "nonsmooth: R1, R2, R_b"),
        "smooth_tophat": (M.Ball.from_HRb(HRB, profile=M.SmoothTopHat(**CORE)), "nonsmooth: R_b"),
    }


def nonsmooth(name, b):
    if name == "flat" or name == "smooth_tophat":
        R = [b.Rb]
    elif name == "tophat":
        R = [b.prof.R1, b.prof.R2, b.Rb]
    else:
        R = []
    return b.rbar_of_R(np.array(R)) if R else np.array([])


def orders_of(hs, es):
    hs, es = np.asarray(hs), np.asarray(es)
    with np.errstate(divide="ignore", invalid="ignore"):
        return list(np.log(es[:-1] / es[1:]) / np.log(hs[:-1] / hs[1:]))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--Ns", default="32,64,128,256")
    p.add_argument("--orders", default="2,4")
    p.add_argument("--band", type=float, default=0.1, help="excluded band around non-smooth radii / R_b")
    p.add_argument("--Lfac", type=float, default=1.25, help="octant size / R_b")
    p.add_argument("--models", default="flat,flat_taper,tophat,smooth_tophat")
    p.add_argument("--no-table", action="store_true", help="skip the table-interpolation part")
    p.add_argument("--slab", type=int, default=8)
    p.add_argument("--tag", default="", help="suffix of the figure names")
    a = p.parse_args(argv)
    Ns = [int(s) for s in a.Ns.split(",")]
    ords = tuple(int(s) for s in a.orders.split(","))
    with runlog.Run("G1 of A-pre-1: FD constraint residuals vs resolution (orders "
                    f"{ords}, N = {Ns}) and table interpolation error vs spacing",
                    kind="production", cores=4) as run:
        res = {}
        L = a.Lfac * RB
        band = a.band * RB
        planes = {}
        sel_models = a.models.split(",")
        for name, (b, note) in models().items():
            if name not in sel_models:
                continue
            src = mesh.radial_source(b)
            ed = nonsmooth(name, b)
            regs = {"all": lambda r: np.ones_like(r, dtype=bool),
                    "smooth": (lambda r, ed=ed: np.ones_like(r, dtype=bool) if len(ed) == 0 else
                               np.min(np.abs(r[..., None] - ed), axis=-1) > band)}
            res[name] = dict(note=note, nonsmooth_rbar=list(ed), N=Ns, h=[L / N for N in Ns],
                             norms={})
            for N in Ns:
                t0 = time.time()
                want_plane = (N == 128)
                r = mesh.residuals(src, N, L, ords, regs, norm=6 * b.H ** 2, plane=want_plane,
                                   slab=a.slab)
                if want_plane:
                    r, pl = r
                    planes[name] = pl
                res[name]["norms"][N] = r
                print(f"{name:14s} N={N:4d} {time.time() - t0:6.1f}s " + "  ".join(
                    f"p{q}: H {r[q]['smooth']['H_L2']:.3e} M {r[q]['smooth']['M_L2']:.3e}" for q in ords),
                    flush=True)
            # measured orders
            od = {}
            for q in ords:
                for reg in ("smooth", "all"):
                    for key in ("H_L1", "H_L2", "H_Linf", "M_L1", "M_L2", "M_Linf"):
                        es = [res[name]["norms"][N][q][reg][key] for N in Ns]
                        od[f"p{q}/{reg}/{key}"] = orders_of(res[name]["h"], es)
            res[name]["orders"] = od
        # table interpolation error against its spacing
        tabres = {}
        for name in (() if a.no_table else ("smooth_tophat", "flat", "tophat")):
            b = models()[name][0]
            rm = b.matter_rbar()
            ed = b.rbar_edges()
            x = np.random.default_rng(7).uniform(0.0, 1.45 * rm, 4000)
            ex = b.fields(x, ("u", "KL", "KT", "betar"))
            tabres[name] = {}
            for npts in (500, 1000, 2000, 4000, 8000):
                dr = rm / npts
                rows = np.arange(int(np.ceil(1.5 * rm / dr)) + 1) * dr
                f = b.fields(rows, ("u", "KL", "KT", "betar"))
                cols = dict(rbar=rows, u=f["u"], KL=f["KL"], KT=f["KT"], alpha=np.ones_like(rows),
                            betar=f["betar"])
                T = table.Format2Table(cols, dict(format="2", exterior="pg"))
                tv = T(x)
                far = np.min(np.abs(x[:, None] - ed[None, :]), axis=1) > 2.5 * dr
                if name == "smooth_tophat":   # data C-infinity at R1, R2: only R_b is a jump
                    far = np.abs(x - b.Rb) > 2.5 * dr
                tabres[name][npts] = {k: float(np.max(np.abs(tv[k] - ex[k])[far])) for k in ("u", "KL", "KT", "betar")}
            tabres[name]["orders"] = {k: orders_of([rm / n for n in (500, 1000, 2000, 4000, 8000)],
                                                   [tabres[name][n][k] for n in (500, 1000, 2000, 4000, 8000)])
                                      for k in ("u", "KL", "KT", "betar")}
        # residual of the table actually written (rm/4000) against the exact fields, N = 128
        b = models()["smooth_tophat"][0]
        if a.no_table:
            b = None
        if b is not None:
            rm = b.matter_rbar()
            dr = rm / 4000
            rows = np.arange(int(np.ceil(1.5 * rm / dr)) + 1) * dr
            f = b.fields(rows, ("u", "KL", "KT", "betar"))
            T = table.Format2Table(dict(rbar=rows, u=f["u"], KL=f["KL"], KT=f["KT"],
                                        alpha=np.ones_like(rows), betar=f["betar"]),
                                   dict(format="2", exterior="pg"))
            ed = nonsmooth("smooth_tophat", b)
            regs = {"smooth": lambda r: np.min(np.abs(r[..., None] - ed), axis=-1) > band}
            rt = mesh.residuals(mesh.radial_source(b, T), 128, L, (4,), regs, norm=6 * b.H ** 2)
            tabres["residual_table_vs_exact_N128_p4"] = dict(
                table=rt[4]["smooth"],
                exact=res.get("smooth_tophat", {}).get("norms", {}).get(128, {}).get(4, {}).get("smooth"))
        out = dict(run_id=run.run_id, L=L, band=band, models=res, table=tabres)
        with open(os.path.join(run.out, "convergence.json"), "w") as fh:
            json.dump(out, fh, indent=1, default=float)
        if planes:
            np.savez_compressed(os.path.join(run.out, "planes_N128.npz"),
                                **{f"{n}_p{q}_{k}": planes[n][q][i] for n in planes
                                   for q in planes[n] for i, k in enumerate(("H", "M"))})
        figs = make_figures(out, planes, run.out, L, a.tag)
        for fpath in figs:
            shutil.copy(fpath, os.path.join(_PKG, "figures", os.path.basename(fpath)))
        run.results = dict(orders={n: {k: v for k, v in res[n]["orders"].items()
                                       if "/smooth/" in k and k.endswith("_L2")} for n in res},
                           table_orders={n: tabres[n]["orders"] for n in tabres if "orders" in tabres[n]},
                           figures=[os.path.basename(f) for f in figs])
        print(json.dumps(run.results, indent=1, default=float))
    return 0


def make_figures(out, planes, d, L, tag=""):
    fs.use_style()
    files = []
    names = list(out["models"].keys())
    fig, axes = plt.subplots(2, len(names), figsize=(8.0, 4.8), sharex=True, squeeze=False)
    fig.subplots_adjust(left=0.09, right=0.99, bottom=0.1, top=0.86, wspace=0.36, hspace=0.08)
    cols = {2: fs.PAL["blue"], 4: fs.PAL["red"]}
    for j, name in enumerate(names):
        r = out["models"][name]
        h = np.array(r["h"]) / RB
        for i, key in enumerate(("H", "M")):
            ax = axes[i, j]
            for q in (2, 4):
                if q not in r["norms"][r["N"][0]]:
                    continue
                es = np.array([r["norms"][N][q]["smooth"][key + "_L2"] for N in r["N"]])
                ea = np.array([r["norms"][N][q]["all"][key + "_L2"] for N in r["N"]])
                ax.loglog(h, es, "o-", color=cols[q], ms=3,
                          label=f"order {q}, smooth region" if (i, j) == (0, 0) else None)
                ax.loglog(h, ea, "s--", color=cols[q], ms=3, lw=1.0,
                          label=f"order {q}, all cells" if (i, j) == (0, 0) else None)
                if es[-1] > 1e-9:
                    ax.loglog(h, es[-1] * (h / h[-1]) ** q, color="k", lw=0.8, ls=":",
                              label=r"$\propto h^p$" if (i, j, q) == (0, 0, 4) else None)
            if key == "H" and name.startswith("flat"):
                ax.text(0.05, 0.5, "round-off only:\norder 4 stencil sums\nto -7e-17, / $h^2$",
                        transform=ax.transAxes, fontsize=7)
            if i == 0:
                ax.set_title(name.replace("_", " "), fontsize=10)
            if j == 0:
                ax.set_ylabel(("Hamiltonian" if key == "H" else "momentum") + r" $L_2/6H^2$")
            if i == 1:
                ax.set_xlabel(r"$h/R_b$", labelpad=-2)
            ax.set_xticks([0.005, 0.01, 0.02, 0.04])
            ax.set_xticklabels(["0.005", "0.01", "0.02", "0.04"])
            ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    fig.legend(loc="upper center", ncol=5, fontsize=8, bbox_to_anchor=(0.54, 0.995))
    files += fs.save(fig, os.path.join(d, "fig_constraint_convergence" + tag))
    plt.close(fig)
    # residual maps in the plane z = h/2 (N = 128, order 4)
    sel = [n for n in ("tophat", "smooth_tophat", "flat") if n in planes]
    if sel:
        fig, axes = plt.subplots(2, len(sel), figsize=(8.0, 5.3), squeeze=False)
        fig.subplots_adjust(left=0.08, right=0.88, bottom=0.08, top=0.95, wspace=0.08, hspace=0.12)
        ext = [0, L / RB, 0, L / RB]
        for j, name in enumerate(sel):
            for i, arr in enumerate((planes[name][4][0], planes[name][4][1])):
                ax = axes[i, j]
                v = np.log10(np.abs(arr).T + 1e-18)
                im = ax.imshow(v, origin="lower", extent=ext, cmap=fs.CMAP["dens"], vmin=-10, vmax=0,
                               interpolation="none", rasterized=True)
                ax.set_aspect("equal")
                if i == 0:
                    ax.set_title(name.replace("_", " "), fontsize=10)
                    ax.xaxis.set_major_formatter(matplotlib.ticker.NullFormatter())
                else:
                    ax.set_xlabel(r"$x/R_b$", labelpad=-2)
                if j == 0:
                    ax.set_ylabel(r"$y/R_b$")
                else:
                    ax.yaxis.set_major_formatter(matplotlib.ticker.NullFormatter())
        for i, lab in enumerate(("H", "M")):
            pos = axes[i, -1].get_position()
            cax = fig.add_axes([0.9, pos.y0, 0.015, pos.height])
            fig.colorbar(im, cax=cax, label=r"$\log_{10}|" + lab + r"|/6H^2$ (order 4, $N=128$)")
        files += fs.save(fig, os.path.join(d, "fig_residual_maps_N128" + tag))
        plt.close(fig)
    if not out["table"] or "smooth_tophat" not in out["table"]:
        return [f for f in files if f.endswith((".png", ".pdf"))]
    # table interpolation error
    fig, ax = plt.subplots(1, 1, figsize=(4.0, 3.2))
    fig.subplots_adjust(left=0.18, right=0.97, bottom=0.15, top=0.95)
    tr = out["table"]
    npts = [500, 1000, 2000, 4000, 8000]
    for name, c in (("smooth_tophat", fs.PAL["red"]), ("tophat", fs.PAL["yellow"]), ("flat", fs.PAL["blue"])):
        for k, ls in (("u", "-"), ("KL", "--"), ("KT", ":")):
            e = np.array([tr[name][n][k] for n in npts])
            if np.all(e > 0):
                ax.loglog(1.0 / np.array(npts), e, ls, color=c, label=f"{name.replace('_', ' ')}, {k}")
    x = 1.0 / np.array(npts)
    ax.loglog(x, 1e-12 * (x / x[-1]) ** 4, **fs.GUIDE, label=r"$\propto \Delta\bar r^4$")
    ax.set_xlabel(r"$\Delta\bar r/\bar r_{\rm matter}$")
    ax.set_ylabel("max |table - exact| (smooth part)")
    ax.legend(fontsize=6, ncol=2)
    files += fs.save(fig, os.path.join(d, "fig_table_interpolation" + tag))
    plt.close(fig)
    return [f for f in files if f.endswith((".png", ".pdf"))]


if __name__ == "__main__":
    sys.exit(main())
