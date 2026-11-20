#!/usr/bin/env python3
"""Predictions for the late Newtonian-mode infall run (wave 3) from its matched shell
references (nm_shells.py) and the self-similar solution (selfsimilar.py, test 2). Analysis
of reference calculations only (decision 0010).

For each shell reference (label:law:prefix) and each a/a_i of --at (nearest snapshot):
  M_ta, dress (growth table of the shells, interpolated to the round a/a_i),
  dress/M_ta against the self-similar 0.6245, M_ta/(M a/a_i) against 0.5648,
  rho/rho_b of the shells in the 0.1-dex bins of nm_late.LEDGES_LATE, in units of
  lambda = r/r_ta (r_ta from the shells' M_ta), against the self-similar solution binned in
  the same bins, on [lambda_min, 0.3] with lambda_min = max(4 dx/r_ta, 0.03) (dx of the run,
  the same range for every law), and the local logarithmic slope against the self-similar
  one; the spread between the laws is the modelling uncertainty of the reference.
Writes nm_predict.json, nm_predict.txt and the figures nm_predict_profiles, nm_predict_growth.

Usage: python3 nm_predict.py --setup SETUP.json --dx 8.896 --selfsim selfsimilar_profile.npz
         --ref kernel:PREFIX --ref hybrid:PREFIX [--ref point:PREFIX] --at 8 16 30 --out DIR
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from common import load_figstyle, C_TA      # noqa: E402
import nm_late as NL                          # noqa: E402

SS_DRESS_FRAC = 2.0255 ** (-2.0 / 3.0)


def load_ref(prefix):
    d = dict(np.load(prefix + ".npz"))
    with open(prefix + ".json") as f:
        info = json.load(f)
    g = info["growth"]
    d["g_a"] = np.array([x["a"] for x in g])
    d["g_mta"] = np.array([x["mta"] for x in g])
    d["g_dress"] = np.array([x["dress"] for x in g])
    d["info"] = info
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", ""))
    ap.add_argument("--setup", required=True)
    ap.add_argument("--dx", type=float, required=True)
    ap.add_argument("--selfsim", required=True)
    ap.add_argument("--ref", action="append", required=True, help="LABEL:PREFIX")
    ap.add_argument("--at", type=float, nargs="+", default=[8.0, 16.0, 30.0])
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    with open(a.setup) as f:
        p = json.load(f)
    ss = np.load(a.selfsim)
    t_i, rho_i = p["t_i"], p["rho_i"]
    edges = NL.LEDGES_LATE
    rc = np.sqrt(edges[1:] * edges[:-1])
    refs = {}
    for spec in a.ref:
        lab, pre = spec.split(":", 1)
        refs[lab] = load_ref(pre)
    res = {"setup": a.setup, "dx": a.dx, "refs": {}}
    prof = {}
    for lab, R in refs.items():
        out = {"prefix": R["info"].get("label"), "law": R["info"]["law"], "growth": [], "profiles": []}
        for aa in [4.0] + list(a.at):
            if aa > R["g_a"][-1] + 1e-6:
                continue
            mta = float(np.interp(aa, R["g_a"], R["g_mta"]))
            dr = float(np.interp(aa, R["g_a"], R["g_dress"]))
            out["growth"].append(dict(a=aa, M_ta=mta, dress=dr, dress_over_mta=dr / mta,
                                      mta_over_a=mta / aa, mta_dust_over_a=(mta - 1.0) / aa))
        for aa in a.at:
            k = int(np.argmin(np.abs(R["snap_a"] - aa)))
            ak = float(R["snap_a"][k])
            if abs(ak / aa - 1) > 0.02:
                continue
            tc = t_i + float(R["snap_t"][k])
            rho_b = rho_i * (t_i / tc) ** 2
            rho = NL.binned_density(np.abs(R["snap_r"][k]), R["m0"], edges, rho_b)
            mta = float(np.interp(ak, R["g_a"], R["g_mta"]))
            r_ta = NL.r_ta_of(mta, tc)
            cmp_, ssr, sl, sl_ss = NL.compare(rc, edges, rho, ss, r_ta, a.dx)
            cmp_.update(a=ak, t_code=float(R["snap_t"][k]), M_ta=mta, r_ta=r_ta)
            out["profiles"].append(cmp_)
            prof[(lab, aa)] = dict(rho=rho, ssr=ssr, sl=sl, sl_ss=sl_ss, r_ta=r_ta, a=ak,
                                   lam_min=cmp_["lambda_min"])
        res["refs"][lab] = out
    with open(os.path.join(a.out, "nm_predict.json"), "w") as f:
        json.dump(res, f, indent=1)
    lines = ["# growth (masses in M): law a M_ta dress dress/M_ta M_ta/(M a/a_i)   "
             f"[self-similar {SS_DRESS_FRAC:.4f}, {C_TA:.4f}]"]
    for lab, o in res["refs"].items():
        for g in o["growth"]:
            lines.append(f"{lab:8s} {g['a']:5g} {g['M_ta']:8.4f} {g['dress']:8.4f} "
                         f"{g['dress_over_mta']:7.4f} {g['mta_over_a']:7.4f}")
    lines.append("# profile against self-similar on [lambda_min, 0.3]: law a lambda_min nbins "
                 "max|ratio-1| rms  ratios ; slope: max|s - s_ss| mean(s) mean(s_ss) fit fit_ss")
    for lab, o in res["refs"].items():
        for c in o["profiles"]:
            lines.append(f"{lab:8s} {c['a']:6.2f} {c['lambda_min']:.4f} {c['n_bins']:2d} "
                         f"{c['max_dev'] if c['max_dev'] is not None else float('nan'):.3f} "
                         f"{c['rms_dev'] if c['rms_dev'] is not None else float('nan'):.3f}  "
                         + " ".join(f"{l:.3f}:{r:.3f}" for l, r in zip(c["lam"], c["ratio"])))
            if c["slope_max_absdiff"] is not None:
                lines.append(f"{'':8s}  slope {c['slope_max_absdiff']:.3f} {c['slope_mean']:.3f} "
                             f"{c['slope_ss_mean']:.3f} {c.get('fit_slope', float('nan')):.3f} "
                             f"{c.get('fit_slope_ss', float('nan')):.3f}  "
                             + " ".join(f"{l:.3f}:{s:.2f}/{t:.2f}" for l, s, t in
                                        zip(c["slope_lam"], c["slope"], c["slope_ss"])))
    txt = "\n".join(lines) + "\n"
    with open(os.path.join(a.out, "nm_predict.txt"), "w") as f:
        f.write(txt)
    print(txt)

    fs = load_figstyle()
    import matplotlib.pyplot as plt
    lsty = {"kernel": "-", "hybrid": "--", "point": ":", "plummer": "-."}
    cols = [fs.PAL["red"], fs.PAL["green"], fs.PAL["orange"]]
    fig, axs = plt.subplots(3, len(a.at), figsize=(fs.FULL_WIDTH, 6.6), sharex="col",
                            gridspec_kw=dict(height_ratios=[2, 1, 1]))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.08, top=0.95, hspace=0.05, wspace=0.25)
    axs = np.atleast_2d(axs).reshape(3, len(a.at))
    for j, aa in enumerate(a.at):
        ax, axr, axs_ = axs[0, j], axs[1, j], axs[2, j]
        first = True
        for lab in refs:
            if (lab, aa) not in prof:
                continue
            P = prof[(lab, aa)]
            lam = rc / P["r_ta"]
            ok = P["rho"] > 0
            ls = lsty.get(refs[lab]["info"]["law"], "-")
            if first:
                oks = np.isfinite(P["ssr"])
                ax.plot(lam[oks], P["ssr"][oks], color=fs.PAL["blue"], lw=1.6, label="self-similar, same bins")
                axs_.plot(lam, P["sl_ss"], color=fs.PAL["blue"], lw=1.6)
                ax.axvline(P["lam_min"], **fs.MASK_LINE)
                axr.axvline(P["lam_min"], **fs.MASK_LINE)
                axs_.axvline(P["lam_min"], **fs.MASK_LINE)
                first = False
            ax.plot(lam[ok], P["rho"][ok], color="k", ls=ls, lw=1.0, label=f"shells, {lab}")
            with np.errstate(invalid="ignore", divide="ignore"):
                axr.plot(lam, P["rho"] / P["ssr"], color="k", ls=ls, lw=1.0)
            axs_.plot(lam, P["sl"], color="k", ls=ls, lw=1.0)
        for x in (0.3,):
            for axx in (ax, axr, axs_):
                axx.axvline(x, color="grey", lw=0.6, ls=":")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlim(5e-3, 1.5)
        ax.set_ylim(0.5, 3e4)
        ax.set_title(f"$a/a_i$ = {aa:g}", fontsize=10)
        axr.axhline(1, **fs.GUIDE)
        axr.axhspan(0.9, 1.1, color="grey", alpha=0.15)
        axr.set_ylim(0.3, 1.5)
        axs_.axhline(-2.25, **fs.GUIDE)
        axs_.set_ylim(-3.5, 0.0)
        axs_.set_xlabel(r"$\lambda = r/r_{\rm ta}$", labelpad=-2)
        if j == 0:
            ax.set_ylabel(r"$\rho/\rho_b(t)$")
            axr.set_ylabel("shells / self-similar")
            axs_.set_ylabel(r"$d\ln\rho/d\ln r$")
            ax.legend(fontsize=7, loc="lower left")
    fs.save(fig, os.path.join(a.out, "nm_predict_profiles"))
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(fs.COLUMN_WIDTH * 1.5, 3.8))
    fig.subplots_adjust(left=0.13, right=0.97, bottom=0.13, top=0.97)
    for lab, R in refs.items():
        ls = lsty.get(R["info"]["law"], "-")
        ax.plot(R["g_a"], R["g_mta"] / R["g_a"], color=fs.PAL["red"], ls=ls, lw=1.0,
                label=f"$M_{{\\rm ta}}/(M a/a_i)$, {lab}")
        ax.plot(R["g_a"], R["g_dress"] / R["g_mta"], color=fs.PAL["green"], ls=ls, lw=1.0,
                label=f"dress/$M_{{\\rm ta}}$, {lab}")
    ax.axhline(C_TA, **fs.GUIDE)
    ax.axhline(SS_DRESS_FRAC, **fs.GUIDE)
    ax.text(1.6, C_TA + 0.01, "0.565", fontsize=7)
    ax.text(1.6, SS_DRESS_FRAC + 0.01, "0.625", fontsize=7)
    ax.set_xscale("log")
    ax.set_xlim(1.4, 32)
    ax.set_ylim(0.0, 1.0)
    ax.set_xticks([2, 4, 8, 16, 30])
    ax.set_xticklabels(["2", "4", "8", "16", "30"])
    ax.set_xlabel(r"$a/a_i$")
    ax.legend(fontsize=6.5, loc="lower right", ncol=2)
    fs.save(fig, os.path.join(a.out, "nm_predict_growth"))
    plt.close(fig)


if __name__ == "__main__":
    main()
