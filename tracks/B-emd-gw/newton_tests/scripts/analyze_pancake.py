#!/usr/bin/env python3
"""Tests P1 and P2 of newton_tests: the plane-wave pancake in AthenaK's Newtonian mode.

    analyze_pancake.py --out DIR [--east N:RUNDIR/CASE ...] [--pm N:DIR ...]
                       [--sin N:RUNDIR/CASE ...]

P1 (--east, --pm): the trajectories of the sheets of one x line (newton.traj.bin, tags
   < n, every two cycles) against the exact solution of verify_cosmo/scripts/zeldovich.py
   (continuum and discrete sheets) and against cosmo/newton/pm.py (newton.npz of run
   B-emd-gw-20261115-115239-69ab1db, same particles, records every two steps); plane
   symmetry from the particle snapshots.
P2 (--sin): the second-moment columns of newton.newton.hst against the exact solution
   x = q + a psi of the equal-mass lattice (coefficients in particles.json).
Writes DIR/pancake.json and the figures DIR/pancake_east.{pdf,png},
DIR/pancake_sin_moments.{pdf,png}.
"""
import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "python"))
sys.path.insert(0, os.path.join(WT, "tracks", "B-emd-gw", "verify_cosmo", "scripts"))

import numpy as np  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from nrpic import figstyle as fs  # noqa: E402
from nrpic import io as nio  # noqa: E402
from nrpic import newton as nw  # noqa: E402
import zeldovich as Z  # noqa: E402

A_CHECK = (2.0, 5.0, 10.0, 15.0, 18.0, 20.0)


def h1_growth(n, L=1.0):
    """Hypothesis H1 (JOURNAL.md): the seven-point Laplacian makes the force on the
    fundamental mode too strong by F = [(kh/2)/sin(kh/2)]^2. Linear theory with that
    force, started in the growing mode of F = 1 (s = s0, ds/da = s0 at a = 1):
    s/s0 = A a^n1 + B a^n2. Returns F and the list [(A, n1), (B, n2)]."""
    kh = 2.0*np.pi/n
    F = ((0.5*kh)/np.sin(0.5*kh))**2
    r = np.sqrt(0.25 + 6.0*F)
    n1, n2 = 0.5*(-0.5 + r), 0.5*(-0.5 - r)
    A = (1.0 - n2)/(n1 - n2)
    return F, [(A, n1), (1.0 - A, n2)]


def h1_D(n, t, k=0):
    """k-th conformal-time derivative of D = s/s0 of h1_growth at the times t
    (a = (1 + t/2)^2, so a^m = u^(2m) with u = 1 + t/2, du/dt = 1/2)."""
    _, terms = h1_growth(n)
    u = 1.0 + 0.5*np.asarray(t, float)
    out = np.zeros_like(u)
    for c, m in terms:
        e = 2.0*m
        f = 1.0
        for j in range(k):
            f *= (e - j)
        out += c*f*u**(e - k)/2.0**k
    return out


def pairs(items):
    """N:DIR or N:DIR:PARTDIR (PARTDIR holds particles.json and particles.nrp when the
    case directory does not, as for the card runs started from a batch list)."""
    out = []
    for s in items or []:
        f = s.split(":")
        out.append((int(f[0]), f[1] if len(f) < 3 else (f[1], f[2])))
    return out


def dirs(case):
    return (case, case) if isinstance(case, str) else case


def read_traj(path, ntrack):
    raw = np.fromfile(path, dtype="<f8")
    rec = raw.reshape(-1, 8)
    t = rec[:, 0]
    tag = rec[:, 1].astype(np.int64)
    times = np.unique(t)
    nt = len(times)
    x = np.full((nt, ntrack, 3), np.nan)
    u = np.full((nt, ntrack, 3), np.nan)
    it = np.searchsorted(times, t)
    x[it, tag] = rec[:, 2:5]
    u[it, tag] = rec[:, 5:8]
    return times, x, u


def unwrap(xx, qq, L):
    return qq + np.mod(xx - qq + 0.5*L, L) - 0.5*L


def at(arr, a_rec, a):
    i = int(np.argmin(np.abs(a_rec - a)))
    return float(arr[i]), float(a_rec[i])


def east_case(n, case):
    case, pdir = dirs(case)
    meta = json.load(open(os.path.join(pdir, "particles.json")))
    L, d, nt = meta["L"], meta["delta"], meta["ntrack"]
    k = 2.0*np.pi/L
    tau, x, u = read_traj(os.path.join(case, "newton.traj.bin"), nt)
    q = np.array(meta["q_line"])
    x0 = np.array(meta["x0_line"])
    v0 = np.array(meta["v0_line"])
    m = np.array(meta["m_line"])
    a = nw.scale_factor(tau)
    xu = unwrap(x[:, :, 0], q[None, :], L)
    v = u[:, :, 0]/a[:, None]
    xs, vs = Z.sheet_solution(x0, v0, m, L, tau)
    xs = unwrap(xs, q[None, :], L)
    xc = np.empty_like(xu)
    for i, ai in enumerate(a):
        xc[i] = Z.continuum(x0, ai, d, L)[0]
    xc = unwrap(xc, q[None, :], L)
    disp = np.where(a > 1.0, (a - 1.0)*d/k, np.nan)
    with np.errstate(invalid="ignore", divide="ignore"):
        ex_cont = np.abs(xu - xc).max(axis=1)/disp
        ex_sheet = np.abs(xu - xs).max(axis=1)/disp
        ev_cont = np.abs(v - np.sqrt(a)[:, None]*(d/k)*np.cos(k*x0)[None, :]).max(axis=1) \
            / (np.sqrt(a)*d/k)
    D = h1_D(n, tau)
    with np.errstate(invalid="ignore", divide="ignore"):
        ex_h1 = np.abs(D - a)/(a - 1.0)
        x0u = unwrap(x0, q, L)
        ratio = (xu - xc)/(xc - x0u[None, :])/((D - a)/(a - 1.0))[:, None]
    big = np.abs(np.cos(2.0*np.pi*x0/L)) > 0.3
    a_cross = Z.first_crossing_a(xu, a)
    a_cross_sheets = Z.first_crossing_a(xs, a)
    return dict(n=n, L=L, d=d, tau=tau, a=a, x=xu, v=v, x0=x0, xs=xs, xc=xc, disp=disp,
                ex_cont=ex_cont, ex_sheet=ex_sheet, ev_cont=ev_cont, a_cross=a_cross,
                ex_h1=ex_h1, ratio_h1=ratio, big=big, pdir=pdir,
                a_cross_sheets=a_cross_sheets, case=case)


def plane_symmetry(case, pdir, a_max):
    """Largest spread of x over the particles of one lattice plane (grouped by their
    initial x), over the snapshots with a < a_max, in units of L."""
    x0, _, _, _ = nio.read_nrp(os.path.join(pdir, "particles.nrp"))
    key = np.round(x0[:, 0], 12)
    _, grp = np.unique(key, return_inverse=True)
    out = []
    for f in sorted(glob.glob(os.path.join(case, "newton.part.*.bin"))):
        t, cyc, x, u, mm, tag = nw.read_snapshot(f)
        a = float(nw.scale_factor(t))
        if a >= a_max:
            continue
        g = grp[tag]
        xx = x[:, 0]
        lo = np.full(grp.max() + 1, np.inf)
        hi = np.full(grp.max() + 1, -np.inf)
        np.minimum.at(lo, g, xx)
        np.maximum.at(hi, g, xx)
        sy = np.ptp(x[:, 1] - x0[tag, 1])
        out.append(dict(a=a, spread_x=float((hi - lo).max()), spread_perp=float(sy)))
    return out


def pm_case(n, d):
    z = np.load(os.path.join(d, "newton.npz"))
    return dict(n=n, tau=z["tau"], a=z["a"], x=z["x"], v=z["v"], q=z["q"])


def east_analysis(east, pm, res):
    rows = {}
    for n, case in east:
        r = east_case(n, case)
        rows[n] = r
        e = {"case": r["case"], "a_cross": r["a_cross"],
             "a_cross_sheets": r["a_cross_sheets"]}
        for ac in A_CHECK:
            e["ex_cont_a%g" % ac], e["a_rec_%g" % ac] = at(r["ex_cont"], r["a"], ac)
            e["ex_sheet_a%g" % ac], _ = at(r["ex_sheet"], r["a"], ac)
            e["ev_cont_a%g" % ac], _ = at(r["ev_cont"], r["a"], ac)
            e["ex_h1_pred_a%g" % ac], _ = at(r["ex_h1"], r["a"], ac)
            i = int(np.argmin(np.abs(r["a"] - ac)))
            rr = r["ratio_h1"][i][r["big"]]
            e["h1a_ratio_min_max_a%g" % ac] = [float(rr.min()), float(rr.max())]
        e["plane_symmetry"] = plane_symmetry(r["case"], r["pdir"], 21.0)
        res["P1_athenak_n%d" % n] = e
    pms = {}
    for n, d in pm:
        p = pm_case(n, d)
        pms[n] = p
        if n in rows:
            r = rows[n]
            m = min(len(r["tau"]), len(p["tau"]))
            dtau = np.abs(r["tau"][:m] - p["tau"][:m]).max()
            diff = np.abs(r["x"][:m] - p["x"][:m]).max(axis=1)/r["disp"][:m]
            # pm.py against the continuum on its own records (verify_cosmo metric)
            xc = r["xc"][:m]
            with np.errstate(invalid="ignore", divide="ignore"):
                pm_ex = np.abs(p["x"][:m] - xc).max(axis=1)/r["disp"][:m]
            r["diff_pm"] = diff
            r["pm_ex"] = pm_ex
            r["pm_a"] = r["a"][:m]
            e = {"max_tau_mismatch": float(dtau),
                 "max_tau_mismatch_but_last": float(np.abs(r["tau"][:m-1]
                                                           - p["tau"][:m-1]).max()),
                 "a_cross_pm": Z.first_crossing_a(p["x"], p["a"])}
            # H1a' (post hoc, JOURNAL.md): AthenaK - pm.py sheet by sheet against the
            # H1 error of each sheet (the lattice error, shared by both, cancels)
            L = r["L"]
            x0u = unwrap(r["x0"], p["q"], L)
            D = h1_D(n, r["tau"][:m])
            pred = ((D - r["a"][:m])/(r["a"][:m] - 1.0))[:, None] \
                * (r["xc"][:m] - x0u[None, :])
            with np.errstate(invalid="ignore", divide="ignore"):
                rat = (r["x"][:m] - p["x"][:m])/pred
            for ac in (2.0, 5.0, 10.0):
                i = int(np.argmin(np.abs(r["a"][:m] - ac)))
                rr = rat[i][r["big"]]
                e["h1a_prime_ratio_min_max_a%g" % ac] = [float(rr.min()), float(rr.max())]
            for ac in A_CHECK + (25.0, 30.0, 42.0):
                e["diff_a%g" % ac], _ = at(diff, r["a"][:m], ac)
                e["pm_ex_cont_a%g" % ac], _ = at(pm_ex, r["a"][:m], ac)
            res["P1_athenak_minus_pm_n%d" % n] = e
    return rows, pms


def east_figure(rows, out):
    fs.use_style()
    fig, axs = plt.subplots(2, 1, figsize=(fs.COLUMN_WIDTH*1.5, 6.0), sharex=True)
    fig.subplots_adjust(left=0.15, right=0.97, bottom=0.09, top=0.97, hspace=0.06)
    cols = {16: fs.PAL["orange"], 32: fs.PAL["red"], 64: fs.PAL["yellow"]}
    for n, r in sorted(rows.items()):
        c = cols.get(n, "k")
        ax = axs[0]
        ax.semilogy(r["a"], r["ex_cont"], color=c, label="AthenaK Newton, n = %d" % n)
        ax.semilogy(r["a"], r["ex_h1"], color="k", ls="--", lw=1.0,
                    label=("H1: seven-point Laplacian, linear" if n == min(rows) else None))
        if "pm_ex" in r:
            ax.semilogy(r["pm_a"], r["pm_ex"], color=c, ls="--", lw=1.0,
                        label="pm.py, n = %d" % n)
        if "diff_pm" in r:
            axs[1].semilogy(r["pm_a"], r["diff_pm"], color=c, label="n = %d" % n)
    for ax in axs:
        ax.axvline(21.0, **fs.GUIDE, alpha=0.5)
    axs[0].set_ylabel(r"max$|x - x_{\rm Zel}|\,/\,[(a-1)\,d/k]$")
    axs[1].set_ylabel(r"max$|x_{\rm AthenaK} - x_{\rm pm}|\,/\,[(a-1)\,d/k]$")
    axs[1].set_xlabel(r"scale factor $a$")
    axs[0].set_ylim(1e-6, 1)
    axs[1].set_ylim(1e-7, 1)
    axs[0].legend(ncol=1, loc="upper left", fontsize=8)
    axs[1].legend(loc="lower right")
    axs[0].text(20.6, 2e-6, "continuum crossing", fontsize=8, ha="right")
    return fs.save(fig, os.path.join(out, "pancake_east"))


def sin_case(n, case):
    case, pdir = dirs(case)
    meta = json.load(open(os.path.join(pdir, "particles.json")))
    h = nw.read_newton_hst(os.path.join(case, "newton.newton.hst"))
    c0, c1, c2 = meta["moment_coeffs"]["00"]
    a = h["a"]
    t3 = h["time_d3I"]
    a3 = nw.scale_factor(t3)
    ex = {"I": c1*a + c2*a*a, "dI": (c1 + 2*c2*a)*np.sqrt(a),
          "d2I": 0.5*c1 + 3.0*c2*a, "d3I": 3.0*c2*np.sqrt(a3)}
    got = {"I": h["I_xx"] - c0, "dI": h["dI_xx"], "d2I": h["d2I_xx"], "d3I": h["d3I_xx"]}
    # I, dI, d2I: error over the largest exact value for a <= 15 (d2I_xx changes sign
    # at a = 1/(1.5 d) = 13.3); d3I (positive): pointwise relative error
    w15 = a <= 15.0
    rel = {k: np.abs(got[k] - ex[k])/np.abs(ex[k][w15]).max() for k in ("I", "dI", "d2I")}
    rel["d3I"] = np.abs(got["d3I"] - ex["d3I"])/np.abs(ex["d3I"])
    D0, D1, D2, D3 = (h1_D(n, t3, k) for k in range(4))
    d3_h1 = c1*D3 + 2.0*c2*(3.0*D1*D2 + D0*D3)
    sgn_meas = (got["d3I"] - ex["d3I"])/ex["d3I"]
    sgn_h1 = (d3_h1 - ex["d3I"])/ex["d3I"]
    # the first record has no difference quotient yet
    rel["d3I"][0] = np.nan
    got["d3I"] = got["d3I"].copy()
    got["d3I"][0] = np.nan
    others = {}
    for c in ("yy", "zz", "xy", "xz", "yz"):
        for p in ("dI", "d2I"):
            others["%s_%s" % (p, c)] = float(np.abs(h["%s_%s" % (p, c)]).max()
                                             / np.abs(h["d2I_xx"]).max())
    for c in ("yy", "zz"):
        c0c = meta["moment_coeffs"]["11" if c == "yy" else "22"][0]
        others["I_%s_rel" % c] = float(np.abs(h["I_%s" % c] - c0c).max()/c0c)
    W = h["W"]
    C = h["C"]
    sgn_meas[0] = np.nan
    return dict(n=n, a=a, a3=a3, rel=rel, ex=ex, got=got, others=others, h=h, case=case,
                d3_rel_meas=sgn_meas, d3_rel_h1=sgn_h1,
                C=C, W=W, a_cross=meta["a_cross"])


def sin_analysis(sins, res):
    rows = {}
    for n, case in sins:
        r = sin_case(n, case)
        rows[n] = r
        e = {"case": r["case"], "others_max_over_max_d2Ixx": r["others"]}
        for k in ("I", "dI", "d2I"):
            win = (r["a"] >= 1.2) & (r["a"] <= 15.0)
            e["%s_maxerr_over_max_1.2_15" % k] = float(r["rel"][k][win].max())
        win3 = (r["a3"] >= 1.2) & (r["a3"] <= 15.0)
        e["d3I_rms_rel_1.2_15"] = float(np.sqrt(np.mean(r["rel"]["d3I"][win3]**2)))
        e["d3I_max_rel_1.2_15"] = float(r["rel"]["d3I"][win3].max())
        for lo, hi in ((1.2, 5.0), (5.0, 10.0), (10.0, 15.0), (15.0, 19.0)):
            w = (r["a3"] >= lo) & (r["a3"] <= hi)
            e["d3I_rms_rel_%g_%g" % (lo, hi)] = float(np.sqrt(np.mean(r["rel"]["d3I"][w]**2)))
        for lo, hi in ((2.0, 5.0), (5.0, 10.0), (10.0, 15.0)):
            w = (r["a3"] >= lo) & (r["a3"] <= hi)
            e["h1c_d3I_relerr_mean_meas_%g_%g" % (lo, hi)] = float(np.mean(r["d3_rel_meas"][w]))
            e["h1c_d3I_relerr_mean_pred_%g_%g" % (lo, hi)] = float(np.mean(r["d3_rel_h1"][w]))
        pre = r["a"] < 20.0
        aW = np.abs(r["a"]*r["W"])[pre].max()
        e["layzer_irvine_dC_over_max_aW"] = float(np.abs(r["C"][pre] - r["C"][0]).max()/aW)
        res["P2_athenak_n%d" % n] = e
    return rows


def sin_figure(rows, out):
    fs.use_style()
    fig, axs = plt.subplots(3, 1, figsize=(fs.COLUMN_WIDTH*1.5, 7.5), sharex=True)
    fig.subplots_adjust(left=0.16, right=0.97, bottom=0.07, top=0.98, hspace=0.06)
    cols = {16: fs.PAL["orange"], 32: fs.PAL["red"], 64: fs.PAL["yellow"]}
    for n, r in sorted(rows.items()):
        c = cols.get(n, "k")
        axs[0].plot(r["a3"], r["got"]["d3I"], color=c, lw=0.8, label="AthenaK, n = %d" % n)
        for k, ls in (("I", "-"), ("dI", "--"), ("d2I", ":")):
            axs[1].semilogy(r["a"], r["rel"][k], color=c, ls=ls, lw=1.0,
                            label=({"I": r"$I_{xx} - c_0$", "dI": r"$\dot I_{xx}$",
                                    "d2I": r"$\ddot I_{xx}$"}[k] + ", n = %d" % n))
        axs[2].semilogy(r["a3"], r["rel"]["d3I"], color=c, lw=0.6, label="n = %d" % n)
        axs[2].semilogy(r["a3"], np.abs(r["d3_rel_h1"]), color=c, ls="--", lw=1.0,
                        label="H1 prediction, n = %d" % n)
    r = rows[min(rows)]
    axs[0].plot(r["a3"], r["ex"]["d3I"], **fs.GUIDE, label=r"exact $3 c_2 a^{1/2}$")
    for ax in axs:
        ax.axvline(r["a_cross"], color="grey", lw=1.0, alpha=0.5)
    axs[0].set_ylabel(r"$\dddot I_{xx}$ (code units)")
    axs[1].set_ylabel(r"error / max$_{a\leq 15}$|exact|")
    axs[2].set_ylabel(r"relative error of $\dddot I_{xx}$")
    axs[2].set_xlabel(r"scale factor $a$")
    axs[0].legend(loc="upper left")
    axs[1].legend(loc="lower right", ncol=2, fontsize=7)
    axs[2].legend(loc="lower right")
    axs[1].set_ylim(1e-8, 1)
    axs[2].set_ylim(1e-5, 10)
    return fs.save(fig, os.path.join(out, "pancake_sin_moments"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--east", action="append")
    ap.add_argument("--pm", action="append")
    ap.add_argument("--sin", action="append")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = {}
    figs = []
    if a.east:
        rows, _ = east_analysis(pairs(a.east), pairs(a.pm), res)
        figs += east_figure(rows, a.out)
    if a.sin:
        rows = sin_analysis(pairs(a.sin), res)
        figs += sin_figure(rows, a.out)
    res["figures"] = figs
    with open(os.path.join(a.out, "pancake.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)
        f.write("\n")
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
