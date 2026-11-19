#!/usr/bin/env python3
"""Analysis of the isobaric-mode runs (T7, T8) of the heat package.

    an_mode.py T7  OUTDIR RUNDIR [RUNDIR ...]     conductivity per (theta, eps, k lambda)
    an_mode.py T8  OUTDIR RUNDIR [RUNDIR ...]     parameter variants at one k lambda
    an_mode.py CL  OUTDIR RUNDIR [RUNDIR ...]     collisionless check (k lambda >= 50)

RUNDIR holds case directories (case.json, reduced.npz) written by run_mode.py. Per case:
  A_N = 2 sum M cos(k x)/sum M, A_K = 2 sum M K cos/sum M K (K = W - 1),
  A_S = (A_K - A_N) (<W> - 1)/theta - A_N (entropy combination, A_S(0) = eps c_p),
  theta from the mean kinetic energy of the snapshot.
Fit A = A0 exp(-G t) by least squares over the window [10 t_coll, 2/Gamma_1] of TESTS.md
(Gamma_1 the first Chapman-Enskog rate kappa_1 k^2/(n c_p)), on A_S (primary) and A_N.
Statistics per (theta, eps, k lambda):
  literal  kappa/kappa_1 = G n c_p(theta)/k^2 / kappa_1(theta) (TESTS.md T7);
  f        G / G_ref, G_ref the same fit applied to the nonlinear isobaric reference with
           kappa = kappa_1(T) (isobaric.py) at the same eps, theta, k and window: the
           conductivity in units of kappa_1 with the finite-amplitude bias removed (D3).
Seeds give the mean and its standard error. kappa/kappa_1 is extrapolated linearly in
(k lambda)^2 to zero (weighted least squares). Writes T7_<...>.json and figures.
"""
import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import heatlib as hl          # noqa: E402
import isobaric as iso        # noqa: E402
import conduction as cd       # noqa: E402
import mj                     # noqa: E402
import snap                   # noqa: E402

import matplotlib             # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt   # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

_REF = {}


def load_case(d):
    P = json.load(open(os.path.join(d, "case.json")))
    R = dict(np.load(os.path.join(d, "reduced.npz")))
    t = R["time"]
    AN = 2 * R["c1_M"] / R["sM"]
    AK = 2 * R["c1_MK"] / R["sMK"]
    AE = 2 * R["c1_MW"] / R["sMW"]
    Kbar = R["sMK"] / R["sM"]
    th = np.array([float(mj.theta_from_kinetic(k)) for k in Kbar])
    G = (np.array([float(mj.mean_W(x)) for x in th]) - 1.0) / th
    AS = (AK - AN) * G - AN
    out = dict(P=P, t=t, AN=AN, AK=AK, AE=AE, AS=AS, theta=th,
               SN=2 * R["s1_M"] / R["sM"], n=int(R["n"][0]),
               frac_moved=R.get("frac_moved"), dir=d)
    sp = os.path.join(d, "summary.json")
    out["summary"] = json.load(open(sp)) if os.path.exists(sp) else None
    return out


def reference(theta, eps, kl, t_end, win):
    key = (theta, eps, kl)
    if key not in _REF:
        k = kl
        G1 = cd.mode_rate(cd.kappa_ce_nr(theta, 1.0), 1.0, theta, k)
        t = np.linspace(0, t_end, 401)
        r = iso.mode_reference(k, 1.0, theta, eps, 1.0, t, nm=512)
        GS = iso.fit_exp(r["t"], r["AS"], *win)[0]
        GN = iso.fit_exp(r["t"], r["AN"], *win)[0]
        _REF[key] = dict(G1=G1, GS=GS, GN=GN, t=r["t"], AS=r["AS"], AN=r["AN"])
    return _REF[key]


def fit_case(c):
    P = c["P"]
    G1 = P["Gamma1"]
    win = (10 * P["t_coll"], 2.0 / G1)
    ref = reference(P["theta"], P["eps"], P["k_lambda"], P["t_end"], win)
    GS, A0S, nS = iso.fit_exp(c["t"], c["AS"], *win)
    GN, A0N, nN = iso.fit_exp(c["t"], c["AN"], *win)
    th = float(np.mean(c["theta"]))
    cp = float(mj.c_p(th))
    k = P["k"]
    kap1 = float(cd.kappa_ce_nr(th, P["sigma"]))
    lit = GS * 1.0 * cp / k ** 2 / kap1
    litN = GN * 1.0 * cp / k ** 2 / kap1
    return dict(name=P["name"], seed=P["seed"], theta_gas=th, G_S=GS, G_N=GN, A0_S=A0S,
                n_fit=nS, G1=G1, G_ref_S=ref["GS"], G_ref_N=ref["GN"],
                literal_kappa_over_kappa1=lit, literal_N=litN, f_S=GS / ref["GS"],
                f_N=GN / ref["GN"], window=list(win))


def group(cases, keys):
    g = {}
    for c in cases:
        P = c["P"]
        g.setdefault(tuple(P[k] for k in keys), []).append(c)
    return g


def mean_se(x):
    x = np.asarray(x, float)
    if len(x) < 2:
        return float(x.mean()), float("nan")
    return float(x.mean()), float(x.std(ddof=1) / np.sqrt(len(x)))


def extrapolate(kl, f, se):
    """Weighted least squares f = f0 + b (k lambda)^2; returns f0, se(f0), b, se(b)."""
    x = np.asarray(kl) ** 2
    w = 1.0 / np.asarray(se) ** 2
    A = np.vstack([np.ones_like(x), x]).T
    C = np.linalg.inv(A.T @ (A * w[:, None]))
    p = C @ (A.T @ (w * np.asarray(f)))
    chi2 = float(np.sum(w * (np.asarray(f) - A @ p) ** 2))
    return float(p[0]), float(np.sqrt(C[0, 0])), float(p[1]), float(np.sqrt(C[1, 1])), chi2


def cmd_T7(outdir, rundirs):
    cases = [load_case(os.path.dirname(p)) for r in rundirs
             for p in glob.glob(os.path.join(r, "*", "reduced.npz"))]
    cases = [c for c in cases if not c["P"].get("collisionless_check")
             and not c["P"]["name"].startswith("T8")]     # T8 variants: cmd_T8
    res = dict(rundirs=rundirs, groups={})
    fs.use_style()
    for (th, eps), cs in sorted(group(cases, ("theta", "eps")).items()):
        rows = []
        fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.4))
        ax1 = fig.add_axes([0.08, 0.15, 0.40, 0.75])
        ax2 = fig.add_axes([0.58, 0.15, 0.40, 0.75])
        cols = dict(zip((0.4, 0.2, 0.1), (fs.PAL["red"], fs.PAL["yellow"], fs.PAL["green"])))
        for kl, ck in sorted(group(cs, ("k_lambda",)).items()):
            kl = kl[0]
            fits = [fit_case(c) for c in sorted(ck, key=lambda c: c["P"]["seed"])]
            fS = mean_se([f["f_S"] for f in fits])
            fN = mean_se([f["f_N"] for f in fits])
            lit = mean_se([f["literal_kappa_over_kappa1"] for f in fits])
            P = ck[0]["P"]
            # fit of the seed-mean A_S
            tm = ck[0]["t"]
            Am = np.mean([c["AS"] for c in ck], axis=0)
            Gm = iso.fit_exp(tm, Am, *fits[0]["window"])[0]
            ref = reference(th, eps, kl, P["t_end"], tuple(fits[0]["window"]))
            colls = [c["summary"]["coll"] for c in ck if c["summary"] and "coll" in c["summary"]]
            rows.append(dict(k_lambda=kl, n_seeds=len(fits), n_per_seed=ck[0]["n"],
                             f_S=fS, f_N=fN, literal=lit, f_seedmean_fit=Gm / ref["GS"],
                             fits=fits, nx=P["nx"], dt=P["dt"], t_coll=P["t_coll"],
                             Gamma1=P["Gamma1"],
                             n_trunc=sum(cc["n_trunc"] for cc in colls),
                             max_P=max([cc["max_P"] for cc in colls], default=None),
                             mean_nsub=float(np.mean([cc["mean_nsub"] for cc in colls]))
                             if colls else None,
                             min_N=min([cc["min_N"] for cc in colls], default=None),
                             max_dx_mfp=max([cc["max_dx_mfp"] for cc in colls], default=None),
                             n_noroot=sum(cc["n_noroot"] for cc in colls),
                             n_balance=sum(cc["n_balance"] for cc in colls)))
            G1 = P["Gamma1"]
            c = cols.get(kl, "k")
            for cc in ck:
                ax1.semilogy(G1 * cc["t"], np.abs(cc["AS"]) / (eps * float(mj.c_p(th))),
                             "o", ms=2, color=c, alpha=0.35)
            ax1.semilogy(G1 * ref["t"], np.abs(ref["AS"]) / (eps * float(mj.c_p(th))),
                         **fs.GUIDE)
            ax1.semilogy(G1 * tm, np.abs(Am) / (eps * float(mj.c_p(th))), "-", color=c,
                         lw=1.5, label=rf"$k\lambda={kl}$")
            fs.average_window(ax1, G1 * fits[0]["window"][0], G1 * fits[0]["window"][1], c)
        ax1.set_xlabel(r"$\Gamma_1 t$")
        ax1.set_ylabel(r"$|A_S|/(\epsilon c_p)$")
        ax1.set_title(rf"$\theta={th}$, $\epsilon={eps}$: entropy mode", fontsize=10)
        ax1.set_xlim(0, 2.3)
        ax1.set_ylim(0.05, 1.5)
        ax1.legend(loc="lower left", fontsize=8)
        kl = np.array([r["k_lambda"] for r in rows])
        fS = np.array([r["f_S"][0] for r in rows])
        se = np.array([r["f_S"][1] for r in rows])
        lit = np.array([r["literal"][0] for r in rows])
        grp = dict(theta=th, eps=eps, rows=rows)
        if len(rows) >= 2 and np.all(np.isfinite(se)) and np.all(se > 0):
            f0, sf0, b, sb, chi2 = extrapolate(kl, fS, se)
            grp.update(f0=f0, f0_se=sf0, slope_b=b, slope_b_se=sb, chi2=chi2,
                       dof=len(rows) - 2)
            xx = np.linspace(0, kl.max() ** 2 * 1.1, 50)
            ax2.plot(xx, f0 + b * xx, **fs.REF_LINE, label=rf"$f_0={f0:.3f}\pm{sf0:.3f}$")
            fs.band(ax2, [0.0, 0.004], [f0 - sf0] * 2, [f0 + sf0] * 2, fs.PAL["red"])
            if th == 0.003:
                grp["pass_T7"] = bool(0.99 <= f0 <= 1.06)
        ax2.errorbar(kl ** 2, fS, yerr=se, fmt="o", color=fs.PAL["red"], ms=4,
                     label=r"$f$ (vs nonlinear ref.)")
        ax2.plot(kl ** 2, lit, "s", mfc="none", color=fs.PAL["blue"], ms=4,
                 label=r"literal $\Gamma n c_p/(k^2\kappa_1)$")
        ax2.axhspan(0.99, 1.06, color="grey", alpha=0.12, lw=0)
        ax2.axhline(1.025, **fs.GUIDE)
        ax2.axhline(1.0, **fs.MASK_LINE)
        ax2.set_xlabel(r"$(k\lambda)^2$")
        ax2.set_ylabel(r"$\kappa/\kappa_1$")
        ax2.set_title("conductivity, extrapolation", fontsize=10)
        ax2.legend(loc="best", fontsize=8)
        name = f"T7_th{th:g}_e{eps:g}"
        fs.save(fig, os.path.join(outdir, name))
        plt.close(fig)
        res["groups"][name] = grp
    with open(os.path.join(outdir, "T7.json"), "w") as fh:
        json.dump(res, fh, indent=1, default=float)
    short = {k: dict(f0=v.get("f0"), f0_se=v.get("f0_se"), b=v.get("slope_b"),
                     chi2=v.get("chi2"), pass_T7=v.get("pass_T7"),
                     rows=[(r["k_lambda"], r["n_seeds"], r["f_S"], r["f_N"], r["literal"],
                            r["f_seedmean_fit"], r["n_trunc"], r["mean_nsub"])
                           for r in v["rows"]])
             for k, v in res["groups"].items()}
    print(json.dumps(short, indent=1, default=float))


def cmd_T8(outdir, rundirs):
    cases = [load_case(os.path.dirname(p)) for r in rundirs
             for p in glob.glob(os.path.join(r, "T8*", "reduced.npz"))]
    rows = []
    for c in cases:
        f = fit_case(c)
        P = c["P"]
        cs = c["summary"]["coll"] if c["summary"] and "coll" in c["summary"] else {}
        rows.append(dict(dt_frac=P["dt_frac"], pmax=P["pmax"], dx_frac=P["dx_frac"],
                         seed=P["seed"], f_S=f["f_S"], f_N=f["f_N"],
                         literal=f["literal_kappa_over_kappa1"], n=c["n"],
                         mean_nsub=cs.get("mean_nsub"), max_P=cs.get("max_P"),
                         n_trunc=cs.get("n_trunc"), min_N=cs.get("min_N"),
                         max_dx_mfp=cs.get("max_dx_mfp"), name=P["name"]))
    base = dict(dt_frac=0.1, pmax=0.1, dx_frac=0.25)
    out = dict(rundirs=rundirs, rows=rows, series={})
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.0))
    for i, (par, lab) in enumerate((("dt_frac", r"$\Delta t/t_{\rm coll}$"),
                                    ("pmax", r"$P_{\max}$"),
                                    ("dx_frac", r"$\Delta x/\lambda$"))):
        sel = [r for r in rows if all(r[q] == base[q] for q in base if q != par)]
        vals = sorted({r[par] for r in sel})
        pts = []
        for v in vals:
            fsv = [r["f_S"] for r in sel if r[par] == v]
            m, s = mean_se(fsv)
            pts.append((v, m, s, len(fsv)))
        out["series"][par] = pts
        if len(pts) >= 2:
            (v1, m1, s1, _), (v2, m2, s2, _) = pts[0], pts[1]
            out["series"][par + "_finest_change"] = (m1 - m2) / m2
        ax = fig.add_axes([0.07 + 0.32 * i, 0.17, 0.25, 0.73])
        ax.errorbar([p[0] for p in pts], [p[1] for p in pts],
                    yerr=[p[2] if np.isfinite(p[2]) else 0 for p in pts], fmt="o-",
                    color=fs.PAL["red"], ms=4)
        ax.set_xscale("log")
        ax.set_xlabel(lab)
        if i == 0:
            ax.set_ylabel(r"$f=\kappa/\kappa_1$ at $k\lambda=0.2$")
        ax.axhline(1.025, **fs.GUIDE)
    fs.save(fig, os.path.join(outdir, "T8_convergence"))
    with open(os.path.join(outdir, "T8.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=float)
    print(json.dumps(out["series"], indent=1, default=float))


def cmd_CL(outdir, rundirs):
    cases = [load_case(os.path.dirname(p)) for r in rundirs
             for p in glob.glob(os.path.join(r, "*", "reduced.npz"))]
    cases = [c for c in cases if c["P"].get("collisionless_check")]
    out = {}
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.0))
    for i, c in enumerate(sorted(cases, key=lambda c: c["P"]["theta"])):
        P = c["P"]
        th = P["theta"]
        ref = cd.mode_collisionless(c["t"], P["k"], th, "number")
        A0 = c["AN"][0]
        sn = np.sqrt(2.0 / c["n"])
        z = (c["AN"] - A0 * ref) / sn
        # free streaming of the same sample (deterministic): separates the sample's own
        # noise (free - ensemble) from the effect of the collisions (code - free)
        ini = snap.read_nrp(P["particle_file"])
        vx = ini["u"][:, 0] / hl.W_flat(ini["u"])
        x0 = ini["x"][:, 0] - hl.X0
        free = np.array([2 * np.mean(np.cos(P["k"] * (x0 + vx * tt))) for tt in c["t"]])
        zf = (free - A0 * ref) / sn
        zc = (c["AN"] - free) / sn
        out[P["name"]] = dict(theta=th, max_abs_z=float(np.max(np.abs(z[1:]))),
                              rms_z=float(np.sqrt(np.mean(z[1:] ** 2))),
                              pass_=bool(np.max(np.abs(z[1:])) < 4),
                              rms_z_sample_vs_ensemble=float(np.sqrt(np.mean(zf[1:] ** 2))),
                              rms_z_code_vs_sample=float(np.sqrt(np.mean(zc[1:] ** 2))),
                              max_abs_z_code_vs_sample=float(np.max(np.abs(zc[1:]))),
                              code_minus_sample_end=float(c["AN"][-1] - free[-1]),
                              frac_moved_end=float(c["frac_moved"][-1])
                              if c["frac_moved"] is not None else None)
        ax = fig.add_axes([0.07 + 0.32 * i, 0.17, 0.25, 0.73])
        ax.plot(c["t"], A0 * ref, color=fs.PAL["blue"], label="free streaming, ensemble")
        fs.band(ax, c["t"], A0 * ref - 2 * sn, A0 * ref + 2 * sn, fs.PAL["blue"])
        ax.plot(c["t"], free, **fs.GUIDE, label="free streaming, this sample")
        ax.plot(c["t"], c["AN"], "o", ms=3, color=fs.PAL["red"], label="AthenaK")
        ax.set_xlabel(r"$t$")
        ax.set_title(rf"$\theta={th}$, $k\lambda={P['k_lambda']:g}$", fontsize=10)
        if i == 0:
            ax.set_ylabel(r"$A_N$")
            ax.legend(loc="lower right", fontsize=8)
    fs.save(fig, os.path.join(outdir, "T7_collisionless"))
    with open(os.path.join(outdir, "T7_collisionless.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps(out, indent=1))


def main():
    cmd, outdir, rundirs = sys.argv[1], sys.argv[2], sys.argv[3:]
    if outdir == "-":                  # the registered run's own output directory
        outdir = hl.outdir("analysis")
    rundirs = [r if os.path.isabs(r) else os.path.join(hl.MAIN, "scratch", "C-sidm", r)
               for r in rundirs]
    os.makedirs(outdir, exist_ok=True)
    dict(T7=cmd_T7, T8=cmd_T8, CL=cmd_CL)[cmd](outdir, rundirs)


if __name__ == "__main__":
    main()
