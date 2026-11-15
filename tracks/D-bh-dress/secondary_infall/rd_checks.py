#!/usr/bin/env python3
"""Test 1 of secondary_infall: what 1901.08528 and 2106.07480 print about the turnaround
of dark matter around a hole in the radiation era, and the radial-orbit factor of
1901.08528 appendix A.

Reduced variables of both papers: y = r/(2M), tau = t/(2M) (G = c = 1);
    y'' = -1/(2 y^2) - y/(4 tau^2)            (2106.07480 appendix.tex:22-25,
                                               1901.08528 PBH-UCMH-ArXiv-v2.tex:480-483)
started in the Hubble flow, y'(tau0) = y0/(2 tau0). Turnaround at y' = 0.

Usage: python3 rd_checks.py --out <dir>
"""
import argparse
import json
import math
import os

import numpy as np
from scipy.integrate import solve_ivp, quad
from scipy.special import beta as Beta

from common import load_figstyle

# printed values, 2106.07480 sections/appendix.tex:90-96 (Table 1)
TABLE1 = [  # y0, lambda, tau_ta, tau_ta/lam^1.5, y_ta, y_ta/lam, y_ta^3/tau_ta^2
    (0.095, 0.8145, 22.98, 31.26, 8.305, 10.197, 1.08519),
    (0.100, 1.0000, 31.00, 31.00, 10.142, 10.142, 1.08557),
    (0.105, 1.2155, 41.25, 30.78, 12.27, 10.096, 1.08588),
    (0.110, 1.4641, 54.21, 30.60, 14.72, 10.057, 1.08614),
]
ETA_2106 = 1.086          # sections/appendix.tex:127, sections/cosmo_setup.tex:66
RATIOS_1901 = (0.964, 0.999)   # PBH-UCMH-ArXiv-v2.tex:497 (analytic, numerical)
BOOST_1901 = 1.53         # PBH-UCMH-ArXiv-v2.tex:468 ("53% denser")


def rhs(tau, s):
    y, v = s
    return [v, -0.5 / y**2 - y / (4.0 * tau**2)]


def turnaround(y0, tau0, dense=False, method="DOP853", rtol=1e-12):
    def ev(tau, s):
        return s[1]
    ev.terminal = True
    ev.direction = -1
    # turnaround happens by tau ~ (y0^3/tau0^1.5)^2 scale; integrate generously
    t_end = tau0 + 1e3 * max(1.0, (y0**3 / tau0**1.5) ** 2) + 1e3
    sol = solve_ivp(rhs, (tau0, t_end), [y0, y0 / (2.0 * tau0)], method=method,
                    rtol=rtol, atol=1e-14 * y0, events=ev, dense_output=dense)
    tau_ta = float(sol.t_events[0][0])
    y_ta = float(sol.y_events[0][0][0])
    out = dict(y0=y0, tau0=tau0, S=y0**3 / (2 * tau0**2), tau_ta=tau_ta, y_ta=y_ta,
               eta=y_ta**3 / tau_ta**2)
    # where along the path the two accelerations are equal (1/(2y^2) = y/(4 tau^2))
    tt = np.geomspace(tau0, tau_ta, 20001) if dense else None
    if dense:
        yy = sol.sol(tt)[0]
        f = 0.5 / yy**2 - yy / (4.0 * tt**2)
        k = np.argmax(f > 0)
        # linear interpolation of the sign change
        w = f[k - 1] / (f[k - 1] - f[k])
        t_eq = tt[k - 1] + w * (tt[k] - tt[k - 1])
        y_eq = yy[k - 1] + w * (yy[k] - yy[k - 1])
        out.update(tau_eq=float(t_eq), y_eq=float(y_eq), path=(tt, yy))
    return out


def boost_closed(n):
    return 2.0 / math.pi * Beta(0.5, n - 1.5)


def boost_quad(n, xmax=np.inf):
    # (2/pi) int_1^xmax x^(1/2-n) (1-1/x)^(-1/2) dx = (2/pi) int_1^xmax x^(1-n) (x-1)^(-1/2)
    # substitute x = 1 + w^2 to remove the end-point singularity
    f = lambda w: 2.0 * (1.0 + w * w) ** (1.0 - n)
    wmax = np.inf if not np.isfinite(xmax) else math.sqrt(xmax - 1.0)
    val, err = quad(f, 0.0, wmax, epsabs=1e-13, epsrel=1e-12, limit=400)
    return 2.0 / math.pi * val


def boost_mc(n, xmax=1e3, npart=4_000_000, seed=20261115):
    """Radial Kepler orbits with apocentres drawn from the frozen-in profile r^(-n) on
    [1, xmax], each at a uniformly random time of its orbit; density over r^(-n)."""
    rng = np.random.default_rng(seed)
    q = 3.0 - n
    u = rng.random(npart)
    r_ap = (1.0 + u * (xmax**q - 1.0)) ** (1.0 / q)
    # radial Kepler orbit r = r_ap (1 - cos e)/2, time ~ e - sin e, uniform on [0, pi]
    target = math.pi * rng.random(npart)
    e = np.full(npart, 0.5 * math.pi)
    for _ in range(60):                                  # Newton on e - sin e = target
        e -= (e - np.sin(e) - target) / np.maximum(1.0 - np.cos(e), 1e-300)
        e = np.clip(e, 0.0, math.pi)
    r = r_ap * 0.5 * (1.0 - np.cos(e))
    mtot = (xmax**q - 1.0) / q                           # int_1^xmax r^2 r^(-n) dr (A = 1/4pi)
    edges = np.geomspace(1.5, 60.0, 25)
    h, _ = np.histogram(r, bins=edges)
    vol = (edges[1:] ** 3 - edges[:-1] ** 3) / 3.0
    rc = np.sqrt(edges[1:] * edges[:-1])
    rho = h * (mtot / npart) / vol                       # in units of A (rho_fi = r^-n)
    # exact expectation for the truncated apocentre range, per bin centre
    # bin average of the exact expectation (rho ~ r^-n varies across a bin: comparing
    # with the value at the bin centre biases the ratio by ~1 %; run
    # D-bh-dress-20261115-121936-5c715b5)
    expect = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        x = np.geomspace(lo, hi, 9)
        f = np.array([boost_quad(n, xmax / xx) for xx in x]) * x ** (2.0 - n)
        num = np.trapz(f, x)
        expect.append(num / ((hi**3 - lo**3) / 3.0))
    expect = np.array(expect) * rc**n               # same normalisation as ratio
    err = np.sqrt(np.maximum(h, 1)) * (mtot / npart) / vol
    return dict(rc=rc, ratio=rho * rc**n, expect=expect, err=err * rc**n, counts=h)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = {"table1": [], "scan": [], "boost": {}}

    # 1a: the four trajectories of Table 1
    rows = []
    for (y0, lam, tta, tl, yta, yl, eta) in TABLE1:
        r = turnaround(y0, 1e-3, dense=True)
        rows.append(r)
        res["table1"].append(dict(
            y0=y0, tau_ta=r["tau_ta"], y_ta=r["y_ta"], eta=r["eta"],
            paper_tau_ta=tta, paper_y_ta=yta, paper_eta=eta,
            d_tau=r["tau_ta"] - tta, d_y=r["y_ta"] - yta, d_eta=r["eta"] - eta,
            y_eq_over_y_ta=r["y_eq"] / r["y_ta"],
            analytic_at_eq_over_y_ta=(2 * r["tau_eq"] ** 2) ** (1 / 3) / r["y_ta"]))

    # 1a, second integrator (implicit Radau) for the same four rows
    res["table1_radau"] = []
    for (y0, *_rest) in TABLE1:
        r = turnaround(y0, 1e-3, method="Radau", rtol=1e-11)
        res["table1_radau"].append(dict(y0=y0, tau_ta=r["tau_ta"], y_ta=r["y_ta"], eta=r["eta"]))

    # 1b, 1c: dependence on how deep in the expansion-dominated regime the start is
    S = np.geomspace(10.0, 1e8, 29)
    tau0 = 1e-3
    for s_ in S:
        y0 = (2.0 * s_ * tau0**2) ** (1.0 / 3.0)
        r = turnaround(y0, tau0, dense=True)
        res["scan"].append(dict(
            S=float(s_), y0=y0, tau0=tau0, tau_ta=r["tau_ta"], y_ta=r["y_ta"], eta=r["eta"],
            num_ratio=(r["tau_ta"] ** 2) ** (1 / 3) / r["y_ta"],         # (2GMt^2)^(1/3)/r_ta
            ana_ratio=(2 * r["tau_ta"] ** 2) ** (1 / 3) / r["y_ta"],     # (4GMt^2)^(1/3)/r_ta
            y_eq_over_y_ta=r["y_eq"] / r["y_ta"],
            ana_at_eq_over_y_ta=(2 * r["tau_eq"] ** 2) ** (1 / 3) / r["y_ta"]))
    eta_inf = res["scan"][-1]["eta"]
    res["eta_inf"] = eta_inf
    res["eta_from_1901_numerical"] = RATIOS_1901[1] ** -3
    res["eta_from_1901_analytic"] = 2.0 * RATIOS_1901[0] ** -3

    # 1d: radial-orbit factor
    ns = np.linspace(1.6, 3.4, 37)
    res["boost"]["n"] = ns.tolist()
    res["boost"]["closed"] = [boost_closed(n) for n in ns]
    res["boost"]["quad"] = [boost_quad(n) for n in ns]
    res["boost"]["n94_closed"] = boost_closed(2.25)
    res["boost"]["n94_quad"] = boost_quad(2.25)
    mc = boost_mc(2.25)
    res["boost"]["mc_rc"] = mc["rc"].tolist()
    res["boost"]["mc_ratio"] = mc["ratio"].tolist()
    res["boost"]["mc_expect"] = mc["expect"].tolist()
    res["boost"]["mc_err"] = mc["err"].tolist()
    sel = mc["rc"] < 15.0       # bins where the truncation of the apocentres is < 1e-2
    res["boost"]["mc_max_rel_dev_from_truncated"] = float(np.max(np.abs(
        mc["ratio"][sel] / mc["expect"][sel] - 1.0)))
    res["boost"]["mc_max_rel_stat"] = float(np.max(mc["err"][sel] / mc["ratio"][sel]))
    w = 1.0 / mc["err"][sel] ** 2
    res["boost"]["mc_weighted_ratio_to_expect"] = float(
        np.sum(w * mc["ratio"][sel] / mc["expect"][sel]) / np.sum(w))

    with open(os.path.join(a.out, "rd_checks.json"), "w") as f:
        json.dump(res, f, indent=1)

    # ------------------------------------------------------------------ figure
    fs = load_figstyle()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.075, right=0.985, bottom=0.17, top=0.96, wspace=0.38)
    ax = axs[0]
    cols = fs.series_colors(4)
    for r, row, c in zip(rows, TABLE1, cols):
        tt, yy = r["path"]
        ax.plot(tt, yy, color=c, lw=1.0)
        ax.plot(r["tau_ta"], r["y_ta"], "o", color=c, ms=4)
        ax.plot(row[2], row[4], "s", mfc="none", color="k", ms=7, mew=0.8)
    tt = np.geomspace(1e-3, 100, 50)
    ax.plot(tt, 0.1 * np.sqrt(tt / 1e-3), **fs.GUIDE)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(1e-3, 100)
    ax.set_ylim(0.08, 40)
    ax.set_xlabel(r"$\tau = t/2M$")
    ax.set_ylabel(r"$y = r/2M$")
    ax.text(0.04, 0.90, "dots: this work\nsquares: 2106.07480 Tab. 1\n"
            "dashed: Hubble flow", transform=ax.transAxes, fontsize=7, va="top")
    ax = axs[1]
    sc = res["scan"]
    ax.plot([d["S"] for d in sc], [d["eta"] for d in sc], color=fs.PAL["red"],
            label=r"$y_{\rm ta}^3/\tau_{\rm ta}^2$, this work")
    ax.plot([r["S"] for r in rows], [row[6] for row in TABLE1], "s", mfc="none",
            color="k", ms=6, mew=0.8, label="2106.07480 Tab. 1")
    ax.axhline(ETA_2106, color=fs.PAL["blue"], ls="--", lw=1.0,
               label=r"$\eta_{\rm ta}=1.086$ (2106.07480)")
    ax.axhline(res["eta_from_1901_numerical"], color=fs.PAL["green"], ls=":", lw=1.2,
               label=r"$0.999^{-3}$ (1901.08528)")
    ax.set_xscale("log")
    ax.set_xlim(8, 1.5e8)
    ax.set_ylim(0.99, 1.11)
    ax.set_xlabel(r"start $S = y_0^3/(2\tau_0^2)$")
    ax.set_ylabel(r"$\eta = y_{\rm ta}^3/\tau_{\rm ta}^2$")
    ax.legend(loc="lower right", fontsize=7)
    ax = axs[2]
    ax.plot(ns, res["boost"]["closed"], color=fs.PAL["blue"],
            label=r"$(2/\pi)\,B(1/2,\, n-3/2)$")
    ax.plot(ns[::4], np.array(res["boost"]["quad"])[::4], "o", color=fs.PAL["red"], ms=3.5,
            label="quadrature")
    ax.errorbar([2.25], [res["boost"]["mc_weighted_ratio_to_expect"] *
                         res["boost"]["n94_closed"]],
                yerr=[res["boost"]["mc_max_rel_stat"] * res["boost"]["n94_closed"]],
                fmt="D", color=fs.PAL["yellow"], ms=4, label="Monte Carlo orbits")
    ax.plot([2.25], [BOOST_1901], "s", mfc="none", color="k", ms=8, mew=0.8,
            label="1901.08528: +53 %")
    ax.set_yscale("log")
    ax.set_xlim(1.55, 3.45)
    ax.set_ylim(0.9, 10)
    ax.set_xlabel(r"frozen-in slope $n$")
    ax.set_ylabel(r"$\rho_{\rm orbits}/\rho_{\rm frozen}$")
    ax.legend(loc="upper right", fontsize=7)
    fs.save(fig, os.path.join(a.out, "rd_checks"))

    # MC per-bin figure
    fig, ax = plt.subplots(figsize=(fs.COLUMN_WIDTH, 2.8))
    fig.subplots_adjust(left=0.17, right=0.97, bottom=0.17, top=0.96)
    ax.errorbar(mc["rc"], mc["ratio"], yerr=mc["err"], fmt="o", ms=3, color=fs.PAL["red"],
                label="Monte Carlo (bins), apocentres on [1, 1000]")
    ax.plot(mc["rc"], mc["expect"], color=fs.PAL["blue"], label="quadrature, same range, bin average")
    ax.axhline(boost_closed(2.25), **fs.GUIDE)
    ax.set_xscale("log")
    ax.set_xlabel(r"$r$ (units of the smallest apocentre)")
    ax.set_ylabel(r"$\rho\, r^{9/4}$ (frozen-in = 1)")
    ax.legend(loc="lower left", fontsize=7)
    fs.save(fig, os.path.join(a.out, "rd_boost_mc"))

    # table
    with open(os.path.join(a.out, "rd_checks.txt"), "w") as f:
        f.write("# Table 1 of 2106.07480 (tau0 = 1e-3): mine vs printed\n")
        for d in res["table1"]:
            f.write(" ".join(f"{k}={v:.6g}" for k, v in d.items()) + "\n")
        f.write("# same rows, Radau rtol 1e-11\n")
        for d in res["table1_radau"]:
            f.write(" ".join(f"{k}={v:.7g}" for k, v in d.items()) + "\n")
        f.write("# scan of the start parameter S\n")
        for d in res["scan"]:
            f.write(" ".join(f"{k}={v:.7g}" for k, v in d.items()) + "\n")
        f.write(f"eta_inf={eta_inf:.7f} eta_from_1901_num={res['eta_from_1901_numerical']:.5f}"
                f" eta_from_1901_ana={res['eta_from_1901_analytic']:.5f}\n")
        b = res["boost"]
        f.write(f"boost n=9/4 closed={b['n94_closed']:.6f} quad={b['n94_quad']:.6f} "
                f"mc/expect={b['mc_weighted_ratio_to_expect']:.5f} "
                f"mc max dev={b['mc_max_rel_dev_from_truncated']:.4f} "
                f"max stat={b['mc_max_rel_stat']:.4f}\n")
    print(open(os.path.join(a.out, "rd_checks.txt")).read())


if __name__ == "__main__":
    main()
