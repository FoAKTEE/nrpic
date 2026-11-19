#!/usr/bin/env python3
"""Analysis of the temperature-step runs (T6) of the heat package.

    an_step2.py a  OUTDIR RUNDIR [RUNDIR ...]    long mean free path (lambda/L = 1000, 100)
    an_step2.py b  OUTDIR RUNDIR [RUNDIR ...]    short mean free path (lambda/L = 0.01)
    an_step2.py c  OUTDIR RUNDIR [RUNDIR ...]    the transition (all lambda/L found)

RUNDIR holds case directories (case.json, reduced.npz, heat.nrp) of run_step.py.
(a) Per case: slab sums per unit area against the exact collisionless curve of the
    sample's slab densities and temperatures (conduction.step_collisionless), in units of
    the sampling noise (64 resamplings of 2e5 particles from the reference distribution,
    scaled to N, as collide/analysis/an_step.py); against the free streaming of the same
    sample (no noise: the collisional deviation); initial slopes of rest mass and energy by
    a quadratic fit over t <= 0.5 L/<|v|>_2, the fit's bias on the exact curve subtracted,
    against -2 (Phi(1) - Phi(2)); the standard deviation of that slope estimator from the
    resamplings. Pass (TESTS.md T6a, at 1000): rms deviation < 1.5 noise units for rest
    mass, energy and kinetic energy; slopes of rest mass and energy within 5 percent.
(b) Slab rest mass against the nonlinear isobaric reference (isobaric.step_reference): f
    fitted (kappa = f kappa_1(T)), and the literal statistic chi_fit/chi(kappa_1, 0.015) of
    step_diffusive, both over [20 t_coll, 2/(chi_1 k_1^2)] (declared D2, JOURNAL.md).
(c) Slab rest mass against t for every lambda/L found, with the collisionless and the
    isobaric curves (reported).
"""
import glob
import json
import os
import sys

import numpy as np
from scipy import optimize

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import heatlib as hl          # noqa: E402
import isobaric as iso        # noqa: E402
import conduction as cd       # noqa: E402
import mj                     # noqa: E402
import rate                   # noqa: E402
import snap                   # noqa: E402

import matplotlib             # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt   # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

X0 = hl.X0


def load(d):
    P = json.load(open(os.path.join(d, "case.json")))
    R = dict(np.load(os.path.join(d, "reduced.npz")))
    area = P["box"][1] * P["box"][2]
    ini = snap.read_nrp(os.path.join(d, hl.BASE + ".nrp"))
    sp = os.path.join(d, "summary.json")
    return dict(P=P, R=R, area=area, ini=ini, dir=d,
                summary=json.load(open(sp)) if os.path.exists(sp) else None)


def sample_state(c):
    L = c["P"]["box"][0]
    ini = c["ini"]
    x = ini["x"][:, 0]
    left = np.mod(x - X0, L) < 0.5 * L
    M = ini["m"]
    rho1 = M[left].sum() / (0.5 * L * c["area"])
    rho2 = M[~left].sum() / (0.5 * L * c["area"])
    K = hl.kin_flat(ini["u"])
    th1 = float(mj.theta_from_kinetic(float(np.mean(K[left]))))
    th2 = float(mj.theta_from_kinetic(float(np.mean(K[~left]))))
    return rho1, rho2, th1, th2, left


def free_stream_sums(c, times):
    L = c["P"]["box"][0]
    ini = c["ini"]
    u = ini["u"]
    W = hl.W_flat(u)
    K = hl.kin_flat(u)
    vx = u[:, 0] / W
    M = ini["m"]
    out = []
    for t in times:
        left = np.mod(ini["x"][:, 0] - X0 + vx * t, L) < 0.5 * L
        out.append([M[left].sum(), (M * W)[left].sum(), (M * K)[left].sum()])
    return np.array(out) / c["area"]


def quad_slope(t, X, tmax):
    w = t <= tmax + 1e-12
    p = np.polyfit(t[w], X[w] - X[w][0], 2)
    return float(p[1])


def resample_noise(c, times, rho1, rho2, th1, th2, nres=64, nsub=200000, tslope=None):
    """Noise of the slab sums per unit area (and of the slope estimator) for N particles,
    from nres resamplings of nsub particles scaled by sqrt(nsub/N)."""
    L = c["P"]["box"][0]
    N = len(c["ini"]["m"])
    Mtot = c["ini"]["m"].sum()
    n1 = int(round(nsub * rho1 / (rho1 + rho2)))
    n2 = nsub - n1
    Mm = Mtot / nsub
    rng = np.random.default_rng(12345)
    s1, s2 = mj.Sampler(th1), mj.Sampler(th2)
    sims, slopes = [], []
    for r in range(nres):
        xa = rng.uniform(0, 0.5 * L, n1)
        xb = 0.5 * L + rng.uniform(0, 0.5 * L, n2)
        us = np.concatenate([mj.sample_u(n1, th1, rng, s1), mj.sample_u(n2, th2, rng, s2)])
        xs = np.concatenate([xa, xb])
        Ws = hl.W_flat(us)
        Ks = hl.kin_flat(us)
        vs = us[:, 0] / Ws
        row = []
        for t in times:
            left = np.mod(xs + vs * t, L) < 0.5 * L
            row.append([Mm * left.sum(), Mm * Ws[left].sum(), Mm * Ks[left].sum()])
        row = np.array(row) / c["area"]
        sims.append(row)
        if tslope is not None:
            slopes.append([quad_slope(times, row[:, k], tslope) for k in range(3)])
    sims = np.array(sims)
    scale = np.sqrt(nsub / N)
    noise = sims.std(0, ddof=1) * scale
    sl_sd = np.array(slopes).std(0, ddof=1) * scale if slopes else None
    return noise, sl_sd


def cmd_a(outdir, rundirs):
    cases = [load(os.path.dirname(p)) for r in rundirs
             for p in glob.glob(os.path.join(r, "*", "reduced.npz"))]
    cases = [c for c in cases if c["P"]["lam_over_L"] >= 50]
    res = {}
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 6.2))
    for c in sorted(cases, key=lambda c: (-c["P"]["lam_over_L"], c["P"]["seed"])):
        P = c["P"]
        L = P["box"][0]
        t = c["R"]["time"]
        code = np.stack([c["R"]["slab_M"], c["R"]["slab_MW"], c["R"]["slab_MK"]], 1) / c["area"]
        rho1, rho2, th1, th2, _ = sample_state(c)
        NL, EL, KL = cd.step_collisionless(t, L, rho1, th1, rho2, th2)
        ens = np.stack([NL, EL, KL], 1)
        free = free_stream_sums(c, t)
        tcross = P["tcross"]
        noise, sl_sd = resample_noise(c, t, rho1, rho2, th1, th2, tslope=0.5 * tcross)
        noise[noise == 0] = np.inf
        dev = (code - ens) / noise
        exact_slopes = [float(-2 * (cd.phi_N(rho1, th1) - cd.phi_N(rho2, th2))),
                        float(-2 * (cd.phi_E(rho1, th1) - cd.phi_E(rho2, th2)))]
        exact_slopes.append(exact_slopes[1] - exact_slopes[0])
        fit_code = [quad_slope(t, code[:, k], 0.5 * tcross) for k in range(3)]
        fit_ens = [quad_slope(t, ens[:, k], 0.5 * tcross) for k in range(3)]
        corr = [fit_code[k] - (fit_ens[k] - exact_slopes[k]) for k in range(3)]
        ratio = [corr[k] / exact_slopes[k] for k in range(3)]
        coll_dev = code - free
        fm = c["R"].get("frac_moved")
        r = dict(lam_over_L=P["lam_over_L"], seed=P["seed"], n=len(c["ini"]["m"]),
                 rho=[rho1, rho2], theta=[th1, th2],
                 rms_dev_noise=[float(np.sqrt(np.mean(dev[1:, k] ** 2))) for k in range(3)],
                 max_dev_noise=[float(np.max(np.abs(dev[1:, k]))) for k in range(3)],
                 slope_exact=exact_slopes, slope_code_fit=fit_code, slope_exact_fit=fit_ens,
                 slope_ratio=ratio, slope_sd_rel=[float(sl_sd[k] / abs(exact_slopes[k]))
                                                  for k in range(3)],
                 coll_dev_rms_noise=[float(np.sqrt(np.mean((coll_dev[1:, k] / noise[1:, k]) ** 2)))
                                     for k in range(3)],
                 coll_dev_abs_end=[float(coll_dev[-1, k]) for k in range(3)],
                 coll_dev_rms_abs=[float(np.sqrt(np.mean(coll_dev[1:, k] ** 2))) for k in range(3)],
                 frac_moved_end=float(fm[-1]) if fm is not None else None,
                 coll=c["summary"]["coll"] if c["summary"] else None)
        if P["lam_over_L"] >= 500:
            r["pass_rms"] = bool(all(x < 1.5 for x in r["rms_dev_noise"]))
            r["pass_slope"] = bool(all(abs(x - 1) < 0.05 for x in ratio[:2]))
        res[f"lam{P['lam_over_L']:g}_s{P['seed']}"] = r
        # figure: 3 rows (M, E, K) x 2 columns (lambda/L), seed 1 only
        if P["seed"] == min(cc["P"]["seed"] for cc in cases):
            col = 0 if P["lam_over_L"] >= 500 else 1
            for k, nm in enumerate(("rest mass", "energy", "kinetic energy")):
                ax = fig.add_axes([0.09 + 0.47 * col, 0.69 - 0.29 * k, 0.40, 0.25])
                ax.plot(t / tcross, ens[:, k], color=fs.PAL["blue"], label="exact, collisionless")
                fs.band(ax, t / tcross, ens[:, k] - 2 * noise[:, k], ens[:, k] + 2 * noise[:, k],
                        fs.PAL["blue"])
                ax.plot(t / tcross, free[:, k], **fs.GUIDE, label="free streaming, sample")
                ax.plot(t / tcross, code[:, k], "o", ms=2.5, color=fs.PAL["red"], label="AthenaK")
                if k == 0:
                    ax.set_title(rf"$\lambda/L={P['lam_over_L']:g}$", fontsize=10)
                if k == 2:
                    ax.set_xlabel(r"$t\,\langle|v|\rangle_2/L$")
                else:
                    ax.set_xticklabels([])
                if col == 0:
                    ax.set_ylabel(nm, fontsize=9)
                if k == 0 and col == 0:
                    ax.legend(loc="lower right", fontsize=8)
    fs.save(fig, os.path.join(outdir, "T6a_step_long"))
    plt.close(fig)
    with open(os.path.join(outdir, "T6a.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(res, indent=1, default=float))


def cmd_b(outdir, rundirs):
    cases = [load(os.path.dirname(p)) for r in rundirs
             for p in glob.glob(os.path.join(r, "*", "reduced.npz"))]
    cases = [c for c in cases if c["P"]["lam_over_L"] <= 0.02]
    res = {}
    P0 = cases[0]["P"]
    L = P0["box"][0]
    th1, th2 = P0["theta1"], P0["theta2"]
    sig = P0["sigma"]
    thm = 0.5 * (th1 + th2)
    tcoll = 1.0 / (sig * float(rate.vmol_mean(thm)))
    chi1 = iso.chi_kappa1(thm, 1.0, sig)
    win = (20 * tcoll, 2.0 / (chi1 * (2 * np.pi / L) ** 2))
    w_env = os.environ.get("HEAT_T6B_WINDOW_TCOLL")       # e.g. "300,1374": other window
    if w_env:
        a_, b_ = (float(v) for v in w_env.split(","))
        win = (a_ * tcoll, b_ * tcoll)
    t = cases[0]["R"]["time"]
    cache = {}

    def ref(f):
        if f not in cache:
            X, s = iso.step_reference(L, 1.0, th1, th2, sig, t, f=f, nm=1200)
            cache[f] = (X, s)
        return cache[f][0]

    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 5.6))
    ax = fig.add_axes([0.09, 0.42, 0.40, 0.52])
    axr = fig.add_axes([0.09, 0.09, 0.40, 0.25])
    axp = fig.add_axes([0.58, 0.42, 0.40, 0.52])
    axk = fig.add_axes([0.58, 0.09, 0.40, 0.25])
    w = (t >= win[0]) & (t <= win[1])
    allX = []
    for c in sorted(cases, key=lambda c: c["P"]["seed"]):
        X = np.stack([c["R"]["slab_M"], c["R"]["slab_MW"], c["R"]["slab_MK"]], 1) / c["area"]
        allX.append(X)
        ssr = lambda f: float(np.sum((X[w, 0] - ref(round(f, 5))[w, 0]) ** 2))
        # golden-section on f in [0.8, 1.3]
        o = optimize.minimize_scalar(ssr, bounds=(0.8, 1.3), method="bounded",
                                     options=dict(xatol=2e-4))
        f_fit = float(o.x)
        Xinf = 0.5 * L * 1.0
        chi_fit, chi_se, nfit = iso.fit_step_linear(t, X[:, 0], L, X[0, 0], Xinf, win[0],
                                                    win[1], chi1)
        R1 = ref(1.0)
        res[f"s{c['P']['seed']}"] = dict(seed=c["P"]["seed"], n=len(c["ini"]["m"]), f=f_fit,
                                         literal_ratio=chi_fit / chi1, n_fit=int(w.sum()),
                                         window=list(win), t_coll=tcoll,
                                         rms_resid_f=float(np.sqrt(ssr(f_fit) / w.sum())),
                                         coll=c["summary"]["coll"] if c["summary"] else None,
                                         pass_f=bool(0.95 <= f_fit <= 1.10),
                                         pass_literal=bool(0.95 <= chi_fit / chi1 <= 1.10))
        col = fs.PAL["red"] if c["P"]["seed"] == 1 else fs.PAL["orange"]
        ax.plot(t / tcoll, X[:, 0], "o", ms=2, color=col, label=f"AthenaK seed {c['P']['seed']}")
        axr.plot(t / tcoll, X[:, 0] - ref(round(f_fit, 5))[:, 0], "o", ms=2, color=col)
    ax.plot(t / tcoll, ref(1.0)[:, 0], color=fs.PAL["blue"], label=r"isobaric, $\kappa_1(T)$")
    ax.plot(t / tcoll, cd.step_diffusive(t, L, ref(1.0)[0, 0], 0.5 * L, chi1), **fs.GUIDE,
            label=r"linear, $\chi(\kappa_1,\bar\theta)$")
    rng_ = (allX[0][0, 0], 0.5 * L)
    for a_ in (ax, axr):
        fs.average_window(a_, win[0] / tcoll, win[1] / tcoll)
        a_.set_xscale("log")
    ax.set_ylabel("left-slab rest mass per area")
    ax.set_xticklabels([])
    ax.legend(loc="upper left", fontsize=8)
    ax.set_title(r"T6(b): $\lambda/L=0.01$", fontsize=10)
    axr.axhline(0, **fs.MASK_LINE)
    axr.set_xlabel(r"$t/t_{\rm coll}$")
    axr.set_ylabel("code - ref.($f$)")
    # temperature profiles at a few times, seed 1, against the reference with f fitted
    c = sorted(cases, key=lambda c: c["P"]["seed"])[0]
    s = cache[1.0][1]
    xr = s.x_centres()
    nb = c["R"]["prof_M"].shape[1]
    xb = (np.arange(nb) + 0.5) / nb * L
    for it_frac, colr in zip((0.02, 0.1, 0.4, 1.0), fs.SERIES):
        it = int(round(it_frac * (len(t) - 1)))
        pm = c["R"]["prof_M"][it]
        pk = c["R"]["prof_MK"][it]
        thp = np.array([float(mj.theta_from_kinetic(k)) if m > 0 else np.nan
                        for k, m in zip(pk / np.maximum(pm, 1e-300), pm)])
        axp.plot(xb, thp, "o", ms=2, color=colr)
        # reference: the mass grid starts at the cold centre; the hot centre (face nm/2)
        # sits at x = L/4 in the code's coordinates
        v = s.dm * s.T[it] / s.p[it]
        x_hot = float(np.sum(v[: s.nm // 2]))
        xx = np.mod(xr[it] - x_hot + 0.25 * L, L)
        o_ = np.argsort(xx)
        axp.plot(xx[o_], s.T[it][o_], color=colr, lw=1.0, label=rf"$t={t[it]:.3g}$")
    axp.set_xlabel(r"$x/L$")
    axp.set_ylabel(r"$\theta$ (kinetic)")
    axp.legend(loc="upper right", fontsize=8)
    axp.set_title(r"profiles: AthenaK (dots), isobaric $\kappa_1$ (lines)", fontsize=10)
    # kinetic energy of the slab
    for X, colr in zip(allX, (fs.PAL["red"], fs.PAL["orange"])):
        axk.plot(t / tcoll, X[:, 2], "o", ms=2, color=colr)
    axk.plot(t / tcoll, ref(1.0)[:, 2], color=fs.PAL["blue"])
    axk.set_xscale("log")
    axk.set_xlabel(r"$t/t_{\rm coll}$")
    axk.set_ylabel("slab kinetic energy")
    tagw = "" if not w_env else "_w" + w_env.replace(",", "-")
    fs.save(fig, os.path.join(outdir, "T6b_step_short" + tagw))
    plt.close(fig)
    fvals = [v["f"] for v in res.values()]
    res["combined"] = dict(f_mean=float(np.mean(fvals)),
                           f_se=float(np.std(fvals, ddof=1) / np.sqrt(len(fvals)))
                           if len(fvals) > 1 else None,
                           ref_literal_ratio_f1=None)
    with open(os.path.join(outdir, "T6b" + tagw + ".json"), "w") as fh:
        json.dump(res, fh, indent=1, default=float)
    print(json.dumps(res, indent=1, default=float))


def cmd_c(outdir, rundirs):
    cases = [load(os.path.dirname(p)) for r in rundirs
             for p in glob.glob(os.path.join(r, "*", "reduced.npz"))]
    cases = [c for c in cases if c["P"]["seed"] == 1 and c["P"]["lam_over_L"] > 0.02]
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH / 2, 3.4))
    ax = fig.add_axes([0.17, 0.15, 0.78, 0.76])
    P0 = cases[0]["P"]
    L, th1, th2, tcross = P0["box"][0], P0["theta1"], P0["theta2"], P0["tcross"]
    t = np.linspace(0, 5 * tcross, 200)
    p0 = 2.0 / (1 / th1 + 1 / th2)
    NL, _, _ = cd.step_collisionless(t, L, p0 / th1, th1, p0 / th2, th2)
    ax.plot(t / tcross, NL, **fs.GUIDE, label="collisionless")
    out = {}
    cs = sorted(cases, key=lambda c: -c["P"]["lam_over_L"])
    colors = fs.series_colors(len(cs))
    for c, colr in zip(cs, colors):
        X = c["R"]["slab_M"] / c["area"]
        tt = c["R"]["time"]
        ax.plot(tt / tcross, X, "-", color=colr, lw=1.2,
                label=rf"$\lambda/L={c['P']['lam_over_L']:g}$")
        out[f"lam{c['P']['lam_over_L']:g}"] = dict(t=tt.tolist(), slab_M=X.tolist(),
                                                   frac_moved=c["R"]["frac_moved"].tolist()
                                                   if "frac_moved" in c["R"] else None)
    ax.set_xlabel(r"$t\,\langle|v|\rangle_2/L$")
    ax.set_ylabel("left-slab rest mass per area")
    ax.legend(loc="lower right", fontsize=8)
    ax.set_title("T6(c): transition", fontsize=10)
    fs.save(fig, os.path.join(outdir, "T6c_transition"))
    with open(os.path.join(outdir, "T6c.json"), "w") as fh:
        json.dump(out, fh)
    print("cases", [c["P"]["name"] for c in cs])


def main():
    cmd, outdir, rundirs = sys.argv[1], sys.argv[2], sys.argv[3:]
    if outdir == "-":                  # the registered run's own output directory
        outdir = hl.outdir("analysis")
    rundirs = [r if os.path.isabs(r) else os.path.join(hl.MAIN, "scratch", "C-sidm", r)
               for r in rundirs]
    os.makedirs(outdir, exist_ok=True)
    dict(a=cmd_a, b=cmd_b, c=cmd_c)[cmd](outdir, rundirs)


if __name__ == "__main__":
    main()
