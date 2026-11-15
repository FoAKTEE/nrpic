#!/usr/bin/env python3
"""Field calibration of the Newtonian-mode runs (analysis of AthenaK output only).

For runs of nm_run.py with --onestep: the tracers start at rest, so their momentum after
the one step of length dt is dt times the acceleration at their position. Compares the
radial acceleration with the exact field of the set-up (clump: G M(<r)/r^2 of the uniform
lattice ball of radius r_clump; with dust: plus the dust of the uniform shell
R_w <= r < R_edge), fits a Plummer softening g = M r/(r^2 + s^2)^(3/2) inside 4 cells,
and reports the errors by distance in cells. Writes nm_field.json and figures.

Usage: python3 nm_field.py --out DIR --run LABEL:RUNDIR [--run ...]
"""
import argparse
import glob
import json
import os
import sys

import numpy as np
from scipy.optimize import minimize_scalar

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..", "python")))

from common import load_figstyle  # noqa: E402
from nrpic import newton as nw   # noqa: E402


def exact_menc(r, p):
    m = np.minimum((r / p["r_clump"]) ** 3, 1.0)       # the clump (uniform ball)
    if p.get("n_dust", 0) > 0:
        rho = p["m_dust"] / (4.0 * np.pi / 3.0 * (p["r_edge"]**3 - p["r_w"]**3))
        rr = np.clip(r, p["r_w"], p["r_edge"])
        m = m + 4.0 * np.pi / 3.0 * rho * (rr**3 - p["r_w"]**3)
    return m


def load(rundir):
    with open(os.path.join(rundir, "setup.json")) as f:
        p = json.load(f)
    with open(os.path.join(rundir, "nm_run.json")) as f:
        meta = json.load(f)
    snaps = sorted(glob.glob(os.path.join(rundir, "*.part.*.bin")))
    t, cyc, x, u, m, tag = nw.read_snapshot(snaps[-1])
    t0, _, x0, u0, m0, tag0 = nw.read_snapshot(snaps[0])
    k = (tag >= p["tag_tracer"][0]) & (tag < p["tag_tracer"][1])
    order = np.argsort(tag[k])
    xt, ut = x[k][order], u[k][order]
    acc = ut / (t - t0)
    r = np.sqrt((xt**2).sum(1))
    rhat = xt / r[:, None]
    gr = -(acc * rhat).sum(1)                         # inward positive
    gt = np.sqrt(np.maximum((acc**2).sum(1) - gr**2, 0.0))
    return dict(p=p, meta=meta, r=r, gr=gr, gt=gt, dx=meta["dx"], t=t)


def plummer_fit(d, rmax_cells=4.0):
    r, gr, dx = d["r"], d["gr"], d["dx"]
    k = (r < rmax_cells * dx) & (r > d["p"]["r_clump"])
    menc = 1.0                                        # clump only inside 4 dx (r_w > 4 dx not assumed)
    if d["p"].get("n_dust", 0) > 0:
        k &= r < d["p"]["r_w"]
    y = gr[k] * r[k]**2 / menc

    def cost(s):
        return np.mean((y - r[k]**3 / (r[k]**2 + s * s) ** 1.5) ** 2)
    res = minimize_scalar(cost, bounds=(0.01 * dx, 3.0 * dx), method="bounded")
    return float(res.x), float(np.sqrt(res.fun)), int(k.sum())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", ""))
    ap.add_argument("--run", action="append", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    fs = load_figstyle()
    import matplotlib.pyplot as plt

    runs = []
    for spec in a.run:
        lab, d = spec.split(":", 1)
        dd = load(d)
        dd["label"], dd["dir"] = lab, d
        runs.append(dd)
    summary = {}
    edges = np.array([0.25, 0.5, 1, 2, 4, 8, 16, 32, 64])
    for d in runs:
        p = d["p"]
        g_ex = exact_menc(d["r"], p) / d["r"]**2
        rel = d["gr"] / g_ex - 1.0
        d["rel"] = rel
        rc = d["r"] / d["dx"]
        rows = []
        for lo, hi in zip(edges[:-1], edges[1:]):
            k = (rc >= lo) & (rc < hi) & (d["r"] > p["r_clump"])
            if p.get("n_dust", 0) > 0:
                k &= ~((np.abs(d["r"] - p["r_w"]) < d["dx"]) | (np.abs(d["r"] - p["r_edge"]) < d["dx"]))
            if k.sum() < 3:
                continue
            rows.append(dict(cells=[float(lo), float(hi)], n=int(k.sum()),
                             rms_rel=float(np.sqrt(np.mean(rel[k]**2))),
                             mean_rel=float(np.mean(rel[k])),
                             rms_trans=float(np.sqrt(np.mean((d["gt"][k] / g_ex[k])**2)))))
        out = dict(dx=d["dx"], nx=d["meta"]["nx"], bins=rows, run=d["dir"])
        far4 = (rc > 4) & (d["r"] > p["r_clump"])
        far16 = (rc > 16) & (d["r"] > p["r_clump"])
        if p.get("n_dust", 0) > 0:
            band = (d["r"] > p["r_w"] + 4 * d["dx"]) & (d["r"] < p["r_edge"] - 2 * d["dx"])
            out.update(rms_rel_dust_band=float(np.sqrt(np.mean(rel[band]**2))), n_band=int(band.sum()))
        out.update(rms_rel_gt4=float(np.sqrt(np.mean(rel[far4]**2))),
                   rms_rel_gt16=float(np.sqrt(np.mean(rel[far16]**2))) if far16.any() else None)
        s, rmsfit, nfit = plummer_fit(d)
        d["s_eff"] = s
        out.update(s_eff=s, s_eff_cells=s / d["dx"], plummer_fit_rms=rmsfit, plummer_fit_n=nfit)
        if p.get("n_dust", 0) == 0:
            # the measured kernel f(q) = g_r r^2/M of the clump, q = r/dx: binned median and
            # 16/84 percentiles, for the shell reference with the mesh's own softening
            qe = np.geomspace(0.02, 32.0, 49)
            q = d["r"] / d["dx"]
            f = d["gr"] * d["r"]**2
            rows_k = []
            for lo, hi in zip(qe[:-1], qe[1:]):
                k = (q >= lo) & (q < hi)
                if k.sum() >= 5:
                    rows_k.append((np.sqrt(lo * hi), np.median(f[k]), np.percentile(f[k], 16),
                                   np.percentile(f[k], 84), k.sum()))
            kfile = os.path.join(a.out, "kernel_nx%d.txt" % d["meta"]["nx"])
            np.savetxt(kfile, np.array(rows_k), header="q=r/dx  median(g_r r^2/M)  p16  p84  n"
                       "   (clump-only one-step run %s)" % d["dir"])
            out["kernel_file"] = kfile
        summary[d["label"]] = out
    # the dust's own force: the run with dust minus the run without, same tracers and nx
    for d in runs:
        if d["p"].get("n_dust", 0) == 0:
            continue
        for e in runs:
            if e["p"].get("n_dust", 0) == 0 and e["meta"]["nx"] == d["meta"]["nx"] \
                    and np.allclose(e["r"], d["r"]):
                p = d["p"]
                gdust = d["gr"] - e["gr"]
                mu = exact_menc(d["r"], p) - exact_menc(d["r"], e["p"])
                g_tot = exact_menc(d["r"], p) / d["r"]**2
                err = (gdust - mu / d["r"]**2) / g_tot
                core = (d["r"] > p["r_clump"]) & (d["r"] < p["r_w"] - d["dx"])
                band = (d["r"] > p["r_w"] + d["dx"]) & (d["r"] < p["r_edge"] - d["dx"])
                summary[d["label"]].update(
                    dust_force_vacuum_core_max_rel=float(np.max(np.abs(err[core]))),
                    dust_force_vacuum_core_rms_rel=float(np.sqrt(np.mean(err[core]**2))),
                    dust_force_band_rms_rel=float(np.sqrt(np.mean(err[band]**2))),
                    dust_force_band_max_rel=float(np.max(np.abs(err[band]))),
                    dust_pair=e["dir"])
                d["dust_err"] = err

    # figure: radial field in units of M_enc/r^2, its errors, and the dust's own force
    fig, axs = plt.subplots(3, 1, figsize=(fs.COLUMN_WIDTH * 1.4, 8.0))
    fig.subplots_adjust(left=0.16, right=0.97, bottom=0.065, top=0.98, hspace=0.32)
    cols = [fs.PAL["red"], fs.PAL["yellow"], fs.PAL["green"], fs.PAL["orange"]]
    for i, d in enumerate(runs):
        rc = d["r"] / d["dx"]
        g_ex = exact_menc(d["r"], d["p"]) / d["r"]**2
        c = cols[i % len(cols)]
        axs[0].plot(rc, d["gr"] / g_ex, ".", ms=1.5, color=c, alpha=0.6,
                    label=f"{d['label']}: Plummer fit $s$ = {d['s_eff'] / d['dx']:.2f}" + r"$\Delta x$")
        rr = np.geomspace(d["p"]["r_clump"] / d["dx"], 40, 300) * d["dx"]
        if d["p"].get("n_dust", 0) == 0:
            axs[0].plot(rr / d["dx"], rr**3 / (rr**2 + d["s_eff"]**2) ** 1.5
                        / exact_menc(rr, d["p"]), color=c, lw=1.0)
        axs[1].plot(rc, np.abs(d["rel"]), ".", ms=1.5, color=c, alpha=0.6)
        axs[1].plot(rc, d["gt"] / g_ex, "x", ms=1.5, color=c, alpha=0.3)
        if "dust_err" in d:
            axs[2].plot(d["r"], np.abs(d["dust_err"]), ".", ms=2, color=c,
                        label=f"{d['label']} minus clump alone")
            for rr_ in (d["p"]["r_w"], d["p"]["r_edge"]):
                axs[2].axvline(rr_, **fs.MASK_LINE)
    axs[0].axhline(1.0, **fs.GUIDE)
    axs[0].set_ylabel(r"$g_r\,/\,(G M_{\rm enc}/r^2)$")
    axs[0].set_xscale("log")
    axs[0].set_xlim(0.03, 40)
    axs[0].set_ylim(-0.05, 1.35)
    axs[0].set_xlabel(r"$r/\Delta x$", labelpad=-2)
    axs[0].legend(loc="lower right", markerscale=6, fontsize=8)
    axs[1].set_xscale("log")
    axs[1].set_yscale("log")
    axs[1].set_xlim(0.03, 40)
    axs[1].set_ylim(1e-5, 3)
    axs[1].set_xlabel(r"$r/\Delta x$", labelpad=-2)
    axs[1].set_ylabel(r"$|\delta g_r|/g$ (dots), $g_t/g$ (crosses)")
    xx = np.geomspace(1, 40, 50)
    axs[1].plot(xx, 0.5 * xx**-2, **fs.GUIDE)
    axs[1].text(12, 0.5 * 12**-2 * 2.5, r"$0.5\,(\Delta x/r)^2$", fontsize=9)
    axs[2].set_xscale("log")
    axs[2].set_yscale("log")
    axs[2].set_xlabel(r"$r$ [$GM/c^2$]", labelpad=-2)
    axs[2].set_ylabel(r"$|g_{\rm dust} - G\mu(<r)/r^2|/g$")
    if any("dust_err" in d for d in runs):
        axs[2].legend(loc="upper left", markerscale=4, fontsize=8)
    fs.save(fig, os.path.join(a.out, "nm_field"))
    with open(os.path.join(a.out, "nm_field.json"), "w") as f:
        json.dump(summary, f, indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
