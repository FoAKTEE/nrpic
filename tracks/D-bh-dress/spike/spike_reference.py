"""P1: the relativistic spike of SFW (arXiv:1305.2619) recomputed by its own method and
compared with the numbers and curves printed in SFW and in the Kerr sequel FdRW
(arXiv:1707.06302).

usage: python3 spike_reference.py --out <scratch run dir> [--kb <kb-data/raw/arxiv>]
Writes reference.json, reference_table.txt, figures (PDF, PNG) into --out and copies the
PNGs to figs/ next to this script.
"""
import argparse
import json
import shutil
import subprocess
import sys
import time
import warnings
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "python"))
from spike_lib import (MSUN_PC3_TO_GEV_CM3, KMS, RG_SUN_PC, SpikeModel, HernquistInverse,  # noqa
                       rho_constf_rel, rho_constf_gs, Emin_root, Emin_bruteforce,
                       bh_action_period, newton_action, hernquist_orbit_from_La,
                       hernquist_xc, hernquist_delta_direct)
from nrpic import figstyle  # noqa

warnings.simplefilter("ignore", RuntimeWarning)
GEV = MSUN_PC3_TO_GEV_CM3


def peak(x, y):
    i = int(np.nanargmax(y))
    if 0 < i < len(y) - 1:          # parabola through the three points around the maximum
        c = np.polyfit(x[i - 1:i + 2], y[i - 1:i + 2], 2)
        xp = -c[1] / (2 * c[0])
        return float(xp), float(np.polyval(c, xp))
    return float(x[i]), float(y[i])


def interp_curve(xq, x, y):
    x = np.asarray(x); y = np.asarray(y)
    o = np.argsort(x)
    return np.interp(xq, x[o], y[o], left=np.nan, right=np.nan)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--kb", default="/data/haiyangw/nrpic/kb-data/raw/arxiv")
    args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    res = {}

    # ---- digitized curves (untrusted sources, parsed under python3 -I) ----------------
    subprocess.run([sys.executable, "-I", str(HERE / "paper_curves.py"), args.kb, str(out)],
                   check=True)
    pc = json.loads((out / "paper_curves.json").read_text())

    # ---- checks of the building blocks --------------------------------------------------
    chk = {}
    rr = [4.05, 4.2, 4.5, 5.0, 5.5, 6.0, 8.0, 20.0, 100.0]
    chk["Emin_sfw_vs_bruteforce"] = [[r, Emin_root(r), float(Emin_bruteforce(r))] for r in rr]
    tab = HernquistInverse()
    rng = np.random.default_rng(7)
    errs = []
    for _ in range(400):
        # the domain the spike calculations use: L~ in 1e-10..1e-3, apocentres to 1e6 x_c
        L = 10 ** rng.uniform(-10, -3)
        xa = hernquist_xc(np.array([L]))[0] * (1 + 10 ** rng.uniform(-4, 6))
        d, _, _, I = hernquist_orbit_from_La(np.array([L]), np.array([xa]))
        errs.append(abs(tab.delta(np.array([L]), I)[0] / d[0] - 1))
    errs = np.array(errs)
    chk["table_delta_relerr_median_max_nnan"] = [float(np.nanmedian(errs)),
                                                 float(np.nanmax(errs)),
                                                 int(np.sum(~np.isfinite(errs)))]
    I, T, _ = bh_action_period(np.array([1 - 1e-6]), np.array([300.0**2]))
    chk["kepler_limit_E=1-1e-6_L=300"] = {"I_rel": float(I[0]),
                                          "I_kepler": float(newton_action(1e-6, 300.0)),
                                          "T_rel": float(T[0]),
                                          "T_kepler": float(2 * np.pi / (2e-6) ** 1.5)}
    res["checks"] = chk

    # ---- constant f (SFW Sec. III.C, Fig. 1) ---------------------------------------------
    sigma = 100.0 * KMS
    f0 = 0.3 / (2 * np.pi * sigma**2) ** 1.5             # GeV/cm^3 per (velocity/c)^3
    r1 = np.concatenate([np.linspace(4.0005, 12, 400), np.linspace(12.02, 100, 300)])
    rel = rho_constf_rel(r1, f0) / 1e8
    gs8 = rho_constf_gs(r1, f0, 8.0) / 1e8
    gs4 = rho_constf_gs(r1, f0, 4.0) / 1e8
    pr, pg, p4 = peak(r1, rel), peak(r1, gs8), peak(r1, gs4)
    dig_r = pc["sfw_fig1_relativistic"]; dig_g = pc["sfw_fig1_gs"]
    pdr = peak(np.array(dig_r["x"]), np.array(dig_r["y"]))
    pdg = peak(np.array(dig_g["x"]), np.array(dig_g["y"]))
    fd = [c for c in pc["fig_rho_a"]["curves"] if c["dash"].startswith("{9.6")][0]
    pfd = peak(np.array(fd["x"]), np.array(fd["y"]))
    xs = np.linspace(8.5, 95, 200)
    dev_r = rho_constf_rel(xs, f0) / 1e8 / interp_curve(xs, dig_r["x"], dig_r["y"]) - 1
    dev_g = rho_constf_gs(xs, f0, 8.0) / 1e8 / interp_curve(xs, dig_g["x"], dig_g["y"]) - 1
    xs2 = np.linspace(5.0, 39.0, 200)
    dev_f = rho_constf_rel(xs2, f0) / 1e8 / interp_curve(xs2, fd["x"], fd["y"]) - 1
    res["constf"] = {
        "f0_GeV_cm3": f0,
        "zero_rel_Gm": 4.0, "zero_gs_Gm": 8.0,
        "peak_rel": pr, "peak_gs8": pg, "peak_gs4": p4,
        "peak_rel_digitized_sfw_fig1": pdr, "peak_gs_digitized_sfw_fig1": pdg,
        "peak_rel_digitized_fdrw_fig_rho_a": pfd,
        "ratio_peak_rel_over_gs8": pr[1] / pg[1],
        "excess_peak_gs4_over_rel": p4[1] / pr[1] - 1,
        "dev_vs_sfw_fig1_rel_8.5-95Gm_maxabs": float(np.nanmax(np.abs(dev_r))),
        "dev_vs_sfw_fig1_gs_8.5-95Gm_maxabs": float(np.nanmax(np.abs(dev_g))),
        "dev_vs_fdrw_rho_a_5-39Gm_maxabs": float(np.nanmax(np.abs(dev_f))),
    }

    # ---- Hernquist (SFW Sec. IV) ------------------------------------------------------------
    hern = {}
    curves = {}
    for m in (4.0e6, 1.0e6):
        sm = SpikeModel(M_sun=1e12, a_pc=2.0e4, m_sun=m, table=tab)
        rg = np.concatenate([4.0 + np.logspace(-3, np.log10(6.0), 90),
                             np.logspace(1.0, 8.3, 150)])
        rc = sm.rho_rel(rg, "canonical") * GEV
        rs = sm.rho_rel(rg, "sfw") * GEV
        rn = sm.rho_newton_gs(rg) * GEV
        rh = sm.rho_hernquist(rg) * GEV
        key = f"m{m:.0e}"
        curves[key] = dict(r=rg, can=rc, sfw=rs, gs=rn, hern=rh, sm=sm)
        d = {"rg_pc": sm.rg_pc, "R_S_pc": 2 * sm.rg_pc, "kappa": sm.kappa,
             "nan_fraction": [float(np.mean(~np.isfinite(v))) for v in (rc, rs, rn)],
             "peak_canonical": peak(rg[rg < 30], rc[rg < 30]),
             "peak_sfw": peak(rg[rg < 30], rs[rg < 30]),
             "peak_gs": peak(rg[rg < 60], rn[rg < 60])}
        for rq in (6.0, 7.6, 10.0, 20.0, 50.0, 100.0, 200.0, 1e3, 1e4, 1e5):
            i = int(np.argmin(abs(rg - rq)))
            d[f"at_r={rg[i]:.4g}Gm"] = {"canonical": rc[i], "sfw": rs[i], "gs": rn[i],
                                         "sfw_over_can": rs[i] / rc[i] - 1,
                                         "can_over_gs": rc[i] / rn[i] if rn[i] > 0 else None}
        big = rg > 200.0
        d["max_|can/gs-1|_beyond_100R_S"] = float(np.max(np.abs(rc[big] / rn[big] - 1)))
        # radius where the spike falls to the initial Hernquist density
        diff = np.log(rc) - np.log(rh)
        k = np.where((diff[:-1] > 0) & (diff[1:] <= 0) & (rg[:-1] > 100))[0]
        if len(k):
            k = k[0]
            lr = np.interp(0.0, [diff[k + 1], diff[k]], [np.log(rg[k + 1]), np.log(rg[k])])
            d["spike_meets_hernquist_pc"] = float(np.exp(lr) * sm.rg_pc)
        hern[key] = d
    res["hernquist"] = hern

    # comparisons with the digitized curves
    fh = [c for c in pc["fig_rho_hern"]["curves"] if c["dash"].startswith("{9.6")][0]
    c4 = curves["m4e+06"]
    xq = np.linspace(5.0, 39.0, 120)
    for nm in ("can", "sfw"):
        ours = np.interp(xq, c4["r"], c4[nm]) / 1e18
        dv = ours / interp_curve(xq, fh["x"], fh["y"]) - 1
        hern["m4e+06"][f"dev_{nm}_vs_fdrw_fig_rho_hern_5-39Gm"] = {
            "maxabs": float(np.nanmax(np.abs(dv))), "median": float(np.nanmedian(dv))}
    hern["m4e+06"]["peak_fdrw_digitized"] = peak(np.array(fh["x"]), np.array(fh["y"]))
    c1 = curves["m1e+06"]
    lx = np.linspace(0.45, 4.0, 150)
    rq = 2 * 10**lx                              # r / Gm
    dr = pc["sfw_fig3_curve0"]; dn = pc["sfw_fig3_curve1"]
    for nm, dig in (("sfw", dr), ("can", dr), ("gs", dn)):
        ours = np.log10(np.interp(rq, c1["r"], c1[nm]))
        dv = ours - interp_curve(lx, dig["x"], dig["y"])
        sel = lx >= (0.75 if nm == "gs" else 0.45)
        hern["m1e+06"][f"dex_{nm}_vs_sfw_fig3"] = {
            "maxabs": float(np.nanmax(np.abs(dv[sel]))), "median": float(np.nanmedian(dv[sel]))}
    hern["sfw_fig3_peaks_digitized"] = {
        "rel": peak(np.array(dr["x"]), np.array(dr["y"])),
        "gs": peak(np.array(dn["x"]), np.array(dn["y"]))}
    for key in ("m4e+06", "m1e+06"):
        c = curves[key]
        sel = c["r"] < 60
        pk = hern[key]
        pk["peak_ratio_can_over_gs"] = pk["peak_canonical"][1] / pk["peak_gs"][1]
        pk["peak_ratio_sfw_over_gs"] = pk["peak_sfw"][1] / pk["peak_gs"][1]

    res["wall_s"] = time.time() - t0
    (out / "reference.json").write_text(json.dumps(res, indent=1, default=float))
    np.savez(out / "reference_curves.npz",
             r1=r1, rel=rel, gs8=gs8, gs4=gs4,
             **{f"{k}_{n}": v for k, c in curves.items() for n, v in c.items() if n != "sm"})

    # ---- figures ------------------------------------------------------------------------
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    figstyle.use_style()
    P = figstyle.PAL
    figdir = HERE / "figs"; figdir.mkdir(exist_ok=True)

    # Fig A: constant f
    fig, axs = plt.subplots(2, 1, figsize=(4.0, 4.6), sharex=True,
                            gridspec_kw=dict(height_ratios=[3, 1.3]))
    fig.subplots_adjust(left=0.15, right=0.97, top=0.97, bottom=0.11, hspace=0.0)
    a = axs[0]
    a.plot(dig_r["x"], dig_r["y"], color=P["blue"], lw=3.0, alpha=0.45,
           label="SFW Fig. 1, relativistic (digitized)")
    a.plot(dig_g["x"], dig_g["y"], color=P["blue"], lw=3.0, alpha=0.45, ls="--",
           label="SFW Fig. 1, GS (digitized)")
    a.plot(r1, rel, color=P["red"], label="this work, relativistic")
    a.plot(r1, gs8, color=P["red"], ls="--", label="this work, GS eq. (3.22)")
    a.plot(r1, gs4, color=P["yellow"], ls=":", label="GS with 8 -> 4 Gm")
    for v in (4, 8):
        a.axvline(v, **figstyle.MASK_LINE)
    a.set_xlim(0, 60); a.set_ylim(-0.02, 1.05)
    a.set_ylabel(r"$\rho$ [$10^8$ GeV cm$^{-3}$]")
    a.legend(loc="upper right", fontsize=7)
    b = axs[1]
    b.plot(xs, dev_r * 100, color=P["red"], label="relativistic")
    b.plot(xs, dev_g * 100, color=P["red"], ls="--", label="GS")
    b.plot(xs2, dev_f * 100, color=P["green"], ls="-.", label="vs FdRW fig_rho_a")
    b.axhline(0, **figstyle.THIN)
    b.set_ylim(-4, 4); b.set_xlabel(r"$r/Gm$"); b.set_ylabel("ours/digitized - 1 [%]")
    b.legend(loc="lower right", fontsize=7, ncol=3)
    for ext in ("pdf", "png"):
        fig.savefig(out / f"ref_constf.{ext}")
    plt.close(fig)

    # Fig B: Hernquist, m = 4e6 against FdRW and m = 1e6 against SFW Fig. 3
    fig, axs = plt.subplots(2, 2, figsize=(8.0, 5.6), gridspec_kw=dict(height_ratios=[3, 1.3]))
    fig.subplots_adjust(left=0.08, right=0.98, top=0.95, bottom=0.09, hspace=0.0, wspace=0.25)
    a = axs[0, 0]
    a.plot(fh["x"], fh["y"], color=P["blue"], lw=3.0, alpha=0.45,
           label="FdRW Schwarzschild (digitized)")
    a.plot(c4["r"], c4["can"] / 1e18, color=P["red"], label="canonical action")
    a.plot(c4["r"], c4["sfw"] / 1e18, color=P["yellow"], ls="--", label="SFW action (3.19)")
    a.plot(c4["r"], c4["gs"] / 1e18, color=P["green"], ls=":", label="Newtonian, GS capture")
    a.set_xlim(0, 40); a.set_ylim(-0.05, 3.0); a.tick_params(labelbottom=False)
    a.set_title(r"$m = 4\times10^6\,M_\odot$", fontsize=10)
    a.set_ylabel(r"$\rho$ [$10^{18}$ GeV cm$^{-3}$]")
    a.legend(loc="upper right", fontsize=7)
    b = axs[1, 0]
    for nm, col, ls in (("can", P["red"], "-"), ("sfw", P["yellow"], "--")):
        ours = np.interp(xq, c4["r"], c4[nm]) / 1e18
        b.plot(xq, (ours / interp_curve(xq, fh["x"], fh["y"]) - 1) * 100, color=col, ls=ls)
    b.axhline(0, **figstyle.THIN)
    b.set_xlim(0, 40); b.set_ylim(-8, 8)
    b.set_xlabel(r"$r/Gm$"); b.set_ylabel("ours/FdRW - 1 [%]")
    a = axs[0, 1]
    a.plot(dr["x"], dr["y"], color=P["blue"], lw=3.0, alpha=0.45, label="SFW Fig. 3 relativistic")
    a.plot(dn["x"], dn["y"], color=P["blue"], lw=3.0, alpha=0.45, ls="--",
           label="SFW Fig. 3 non-relativistic")
    lr1 = np.log10(c1["r"] / 2)
    a.plot(lr1, np.log10(c1["sfw"]), color=P["red"], label="SFW action, $m=10^6$")
    a.plot(lr1, np.log10(c1["can"]), color=P["yellow"], ls="-.", label="canonical, $m=10^6$")
    a.plot(lr1, np.log10(c1["gs"]), color=P["red"], ls="--", label="Newtonian GS, $m=10^6$")
    a.plot(np.log10(c4["r"] / 2), np.log10(c4["can"]), color=P["green"], ls=":",
           label=r"canonical, $m=4\times10^6$")
    a.plot(lr1, np.log10(c1["hern"]), **figstyle.GUIDE, label="initial Hernquist, $m=10^6$")
    a.set_xlim(0, 7); a.set_ylim(8.3, 19.9); a.tick_params(labelbottom=False)
    a.set_title("against SFW Fig. 3", fontsize=10)
    a.set_ylabel(r"$\log_{10}\rho$ [GeV cm$^{-3}$]")
    a.legend(loc="upper right", fontsize=7)
    b = axs[1, 1]
    for nm, dig, col, ls in (("sfw", dr, P["red"], "-"), ("can", dr, P["yellow"], "-."),
                             ("gs", dn, P["red"], "--")):
        ours = np.log10(np.interp(rq, c1["r"], c1[nm]))
        b.plot(lx, ours - interp_curve(lx, dig["x"], dig["y"]), color=col, ls=ls)
    b.axhline(0, **figstyle.THIN)
    b.set_xlim(0, 7); b.set_ylim(-0.3, 0.3)
    b.set_xlabel(r"$\log_{10}(r/R_{\rm S})$"); b.set_ylabel("ours - SFW [dex]")
    for ext in ("pdf", "png"):
        fig.savefig(out / f"ref_hernquist.{ext}")
    plt.close(fig)
    for f in ("ref_constf.png", "ref_hernquist.png"):
        shutil.copy(out / f, figdir / f)

    # table
    lines = [f"wall {res['wall_s']:.1f} s"]
    lines.append(json.dumps(res["checks"], default=float))
    lines.append(json.dumps(res["constf"], default=float))
    for k, v in hern.items():
        lines.append(k + " " + json.dumps(v, default=float))
    (out / "reference_table.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
