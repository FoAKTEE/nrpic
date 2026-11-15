#!/usr/bin/env python3
"""Analysis of the Minkowski-box tests of TESTS.md from AthenaK snapshots and histories.

    an_box.py relax   RUNDIR BASE META.json OUTDIR   T3, T4, T5 (twotemp; also unequal: T9)
    an_box.py mode    RUNDIR BASE META.json OUTDIR   T7 (isobaric mode, conductivity)
    an_box.py rate    RUNDIR BASE META.json OUTDIR   T2, T11 (needs <base>.coll.hst)
    an_box.py conserve RUNDIR BASE OUTDIR             T1 (nrpic.hst and coll.hst)
    an_box.py repro   SNAP_A SNAP_B [...]            T10 (bitwise equality)

Each writes OUTDIR/<test>_<BASE>.json (numbers and the pass/fail of the criteria of
TESTS.md, as written before the runs) and a figure OUTDIR/<test>_<BASE>.png. Units and
conventions as in make_box.py (m = 1; Minkowski box, so u_i = u^i). Populations are told
apart by tag (tags are the positions in the particle file): population 1 = tags below
META["n_pop1"] (twotemp) or META["n_classA"] (unequal).

The names of the collision-history columns are those proposed in SPEC.md 4.7; pass
--col NAME=HEADERNAME to map them to core's names once collisions.md exists.
"""
import argparse
import json
import os
import sys

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "REFERENCES"))
sys.path.insert(0, HERE)
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))

import matplotlib                       # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt         # noqa: E402
from nrpic import figstyle as fs        # noqa: E402

import snap                             # noqa: E402
import mj                               # noqa: E402
import rate                             # noqa: E402
import relax as rx                      # noqa: E402
import entropy as en                    # noqa: E402
import conduction as cd                 # noqa: E402

COLS = dict(sum_P="sum_P", n_collisions="n_collisions", n_truncated="n_truncated",
            max_P="max_P", dE_rel="dE_rel", dP_rel="dP_rel", n_pairs="n_pairs_tested")


def theta_of(u, w=None):
    k = snap.kinetic_flat(u)
    kb = float(np.average(k, weights=w))
    # standard error of the mean kinetic energy, propagated through dk/dtheta = c_v
    se_k = float(np.sqrt(np.average((k - kb) ** 2, weights=w) / len(k)))
    th = mj.theta_from_kinetic(kb)
    return th, se_k / float(mj.c_v(th))


def save(fig, out, name):
    os.makedirs(out, exist_ok=True)
    fs.save(fig, os.path.join(out, name))
    plt.close(fig)


# ------------------------------------------------------------------------- relax
def cmd_relax(a):
    meta = json.load(open(a.meta))
    files = snap.snapshots(a.rundir, a.base)
    unequal = meta["kind"] == "unequal"
    n1 = meta["n_classA"] if unequal else meta["n_pop1"]
    V = float(np.prod(meta["box"]))
    s0 = snap.read_snapshot(files[0])
    M = s0["m"]
    pop1 = s0["tag"] < n1
    # rest-frame number densities (m = 1): rest mass per volume of each population
    rho1, rho2 = M[pop1].sum() / V, M[~pop1].sum() / V
    th1_0, _ = theta_of(s0["u"][pop1]); th2_0, _ = theta_of(s0["u"][~pop1])
    # exact initial rate and equilibrium from the sample's own initial temperatures
    d1, d2 = rx.dtheta_dt(rho1, rho2, meta["sigma"], th1_0, th2_0)
    th_eq = rx.theta_eq(rho1, rho2, th1_0, th2_0)
    tau = (th1_0 - th2_0) / abs(d1 - d2)
    t, T1, T2, E1, E2, S, Se = [], [], [], [], [], [], []
    for f in files:
        s = snap.read_snapshot(f)
        p1 = s["tag"] < n1
        a1, e1 = theta_of(s["u"][p1]); a2, e2 = theta_of(s["u"][~p1])
        r = en.s_estimate(s["u"], (rho1 + rho2), th_eq)
        t.append(s["time"]); T1.append(a1); T2.append(a2); E1.append(e1); E2.append(e2)
        S.append(r["s_mm"]); Se.append(r["stderr"])
    t, T1, T2, E1, E2, S, Se = map(np.array, (t, T1, T2, E1, E2, S, Se))
    res = dict(test="relax", run=a.rundir, rho1=rho1, rho2=rho2, theta1_0=th1_0,
               theta2_0=th2_0, theta_eq=th_eq, tau_rel=tau,
               slope_exact=float(d1 - d2), slope_nr=float(rx.dT_rate_nr(
                   rho1, rho2, meta["sigma"], th1_0, th2_0)))
    # T4: quadratic fit of theta1 - theta2 over [0, 0.15 tau], linear coefficient
    w = t <= 0.15 * tau * (1 + 1e-9)
    if w.sum() >= 4:
        D = T1[w] - T2[w]
        sd = np.sqrt(E1[w] ** 2 + E2[w] ** 2)
        A = np.vstack([np.ones(w.sum()), t[w], t[w] ** 2]).T
        # ordinary least squares; standard error from the residuals (the noise of a run
        # is correlated between snapshots, so per-snapshot errors would overstate it)
        coef, rss, _, _ = np.linalg.lstsq(A, D, rcond=None)
        dof = max(w.sum() - 3, 1)
        s2 = float(np.sum((D - A @ coef) ** 2)) / dof
        cov = s2 * np.linalg.inv(A.T @ A)
        slope, se = float(coef[1]), float(np.sqrt(cov[1, 1]))
        ex = float(d1 - d2)
        res.update(T4_slope=slope, T4_slope_se=se, T4_ratio=slope / ex,
                   T4_pass=bool(abs(slope - ex) <= 4 * se + 0.01 * abs(ex) and
                                abs(slope - ex) <= 0.05 * abs(ex)))
    # T3: end state
    se_ = snap.read_snapshot(files[-1])
    absu = np.sqrt(np.sum(se_["u"] ** 2, 1))
    smp = mj.Sampler(th_eq)
    ks = stats.kstest(absu, smp.cdf_u).pvalue
    W = snap.W_flat(se_["u"])
    q = se_["u"] ** 2 / W[:, None]
    ident = float(np.sum(q, 1).mean() / 3)
    ident_se = float(np.sum(q, 1).std() / 3 / np.sqrt(len(W)))
    res.update(t_end_over_tau=float(t[-1] / tau), T3_ks_p=float(ks),
               T3_u2W_over3=ident, T3_u2W_se=ident_se,
               T3_theta1_end=float(T1[-1]), T3_theta2_end=float(T2[-1]),
               T3_pass=bool(ks > 1e-3 and abs(ident - th_eq) < 4 * ident_se and
                            abs(T1[-1] - th_eq) < 4 * E1[-1] + 0 and
                            abs(T2[-1] - th_eq) < 4 * E2[-1]))
    # T5: entropy
    s_mix = en.s_mixture(rho1, th1_0, rho2, th2_0)
    s_eq = float(en.s_mj(rho1 + rho2, th_eq))
    mono = True
    for i in range(len(t)):
        for j in range(i + 1, len(t)):
            if t[j] - t[i] >= 0.25 * tau and S[j] - S[i] < -4 * np.sqrt(2) * max(Se[i], Se[j]):
                mono = False
    res.update(T5_s0=float(S[0]), T5_s_mix=float(s_mix), T5_s_end=float(S[-1]),
               T5_s_eq=s_eq, T5_se=float(Se.max()),
               T5_pass=bool(abs(S[0] - s_mix) < 4 * Se[0] and mono and
                            abs(S[-1] - s_eq) < 4 * Se[-1]))
    if unequal:
        res["T9_same_theta"] = bool(abs(T1[-1] - T2[-1]) < 4 * np.hypot(E1[-1], E2[-1]))
    # figure
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.3))
    ax = fig.add_axes([0.07, 0.15, 0.24, 0.78])
    ax.plot(t / tau, T1 / th_eq, "o", ms=2.5, color=fs.PAL["red"], label="population 1")
    ax.plot(t / tau, T2 / th_eq, "s", ms=2.5, color=fs.PAL["red"], mfc="none",
            label="population 2")
    tm, ym = rx.two_mj_model(rho1, rho2, meta["sigma"], th1_0, th2_0,
                             max(t[-1], 1e-30), 200)
    ax.plot(tm / tau, ym[0] / th_eq, color=fs.PAL["blue"], lw=1.0, label="two-MJ guide")
    ax.plot(tm / tau, ym[1] / th_eq, color=fs.PAL["blue"], lw=1.0)
    xx = np.linspace(0, 0.3, 10)
    ax.plot(xx, (th1_0 + d1 * xx * tau) / th_eq, **fs.GUIDE, label="exact initial slope")
    ax.plot(xx, (th2_0 + d2 * xx * tau) / th_eq, **fs.GUIDE)
    ax.axhline(1, **fs.MASK_LINE)
    ax.set_xlabel(r"$t/\tau_{\rm rel}$"); ax.set_ylabel(r"$\theta_i/\theta_{\rm eq}$")
    ax.legend(loc="upper right", fontsize=8)
    ax = fig.add_axes([0.42, 0.15, 0.24, 0.78])
    ax.errorbar(t / tau, S - s_eq, yerr=Se, fmt="o", ms=2.5, color=fs.PAL["red"])
    ax.axhline(s_mix - s_eq, **fs.GUIDE)
    ax.axhline(0, **fs.MASK_LINE)
    ax.set_xlabel(r"$t/\tau_{\rm rel}$"); ax.set_ylabel(r"$s - s_{\rm MJ}(\theta_{\rm eq})$")
    ax = fig.add_axes([0.75, 0.15, 0.23, 0.78])
    h, e = np.histogram(absu, bins=80, density=True)
    c = 0.5 * (e[1:] + e[:-1])
    ax.plot(c, h, drawstyle="steps-mid", color=fs.PAL["red"], label="end state")
    uu = np.linspace(0, e[-1], 300)
    ax.plot(uu, mj.speed_pdf(uu, th_eq), color=fs.PAL["blue"], label=r"MJ($\theta_{\rm eq}$)")
    ax.set_xlabel(r"$|u|$"); ax.set_ylabel("density")
    ax.legend(loc="upper right", fontsize=8)
    save(fig, a.outdir, f"relax_{a.base}")
    json.dump(res, open(os.path.join(a.outdir, f"relax_{a.base}.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))


# ------------------------------------------------------------------------- mode
def cmd_mode(a):
    meta = json.load(open(a.meta))
    k = meta["k"]
    x0 = meta["x0"]
    files = snap.snapshots(a.rundir, a.base)
    t, AN, AK, SN = [], [], [], []
    for f in files:
        s = snap.read_snapshot(f)
        c = np.cos(k * (s["x"][:, 0] - x0))
        M = s["m"]
        K = snap.kinetic_flat(s["u"])
        t.append(s["time"])
        AN.append(float((M * c).sum() / M.sum() * 2))
        AK.append(float((M * K * c).sum() / (M * K).sum() * 2))
        SN.append(float(np.sqrt(2.0 / len(M))))          # noise of a cosine mode
    t, AN, AK, SN = map(np.array, (t, AN, AK, SN))
    th = meta["theta"]
    n = meta["rho0"]
    sig = meta["sigma"]
    tcoll = 1.0 / (n * sig * float(rate.vmol_mean(th)))
    kap1 = cd.kappa_ce_nr(th, sig)
    G1 = cd.mode_rate(kap1, n, th, k)
    w = (t >= 10 * tcoll) & (t <= 2.0 / G1) & (AN > 3 * SN)
    res = dict(test="mode", run=a.rundir, k=k, k_lambda=k / (n * sig), theta=th,
               t_coll=tcoll, kappa1=kap1, Gamma_kappa1=G1, n_fit=int(w.sum()))
    if w.sum() >= 4:
        sl, ic = np.polyfit(t[w], np.log(np.abs(AN[w])), 1, w=np.abs(AN[w]) / SN[w])
        Gk = -sl
        kap = Gk * n * float(mj.c_p(th)) / k ** 2
        res.update(Gamma_k=float(Gk), kappa=float(kap), kappa_over_kappa1=float(kap / kap1))
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH / 2, 3.3))
    ax = fig.add_axes([0.16, 0.15, 0.8, 0.78])
    ax.semilogy(t / tcoll, np.abs(AN), "o", ms=2.5, color=fs.PAL["red"], label="number mode")
    ax.semilogy(t / tcoll, np.abs(AK), "s", ms=2.5, mfc="none", color=fs.PAL["yellow"],
                label="kinetic-energy mode")
    ax.semilogy(t / tcoll, AN[0] * np.exp(-G1 * t), **fs.GUIDE, label=r"$\kappa_1$")
    ax.semilogy(t / tcoll, AN[0] * np.exp(-G1 / np.sqrt(6 / np.pi) * t), color="k", lw=1,
                ls=":", label=r"Balberg et al. $b$")
    ax.semilogy(t / tcoll, 3 * SN, **fs.MASK_LINE)
    ax.set_xlabel(r"$t/t_{\rm coll}$"); ax.set_ylabel("mode amplitude")
    ax.legend(loc="lower left", fontsize=8)
    save(fig, a.outdir, f"mode_{a.base}")
    json.dump(res, open(os.path.join(a.outdir, f"mode_{a.base}.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))


# ------------------------------------------------------------------------- rate
def cmd_rate(a):
    meta = json.load(open(a.meta))
    cols = dict(COLS)
    for kv in a.col or []:
        k, v = kv.split("="); cols[k] = v
    head, h = snap.read_history(os.path.join(a.rundir, f"{a.base}.coll.hst"))
    ci = snap.history_columns(head)
    tm = h[:, ci.get("time", 0)]
    sumP = h[:, ci[cols["sum_P"]]]
    ncol = h[:, ci[cols["n_collisions"]]]
    ntr = h[:, ci[cols["n_truncated"]]]
    dt = np.diff(tm).mean() if len(tm) > 1 else float("nan")
    N = meta["n"]
    th = meta["theta"]
    beta = meta.get("beta", 0.0)
    gb = 1.0 / np.sqrt(1 - beta ** 2)
    expect = 0.5 * N * meta["rho0"] * meta["sigma"] * float(rate.vmol_mean(th)) * dt
    if meta["kind"] == "boosted":
        # rho0 of make_box is the lab rest-mass density; rest-frame density rho0/gamma_b,
        # collisions per particle per lab time Gamma_rest/gamma_b
        expect = 0.5 * N * (meta["rho0"] / gb) * meta["sigma"] * \
            float(rate.vmol_mean(th)) * dt / gb
    res = dict(test="rate", run=a.rundir, steps=len(tm), dt=float(dt),
               collisions=float(ncol.sum()), sum_P=float(sumP.sum()),
               n_truncated=float(ntr.sum()), expected_per_step=float(expect),
               sumP_per_step=float(sumP.mean()),
               sumP_per_step_se=float(sumP.std(ddof=1) / np.sqrt(len(sumP))))
    res["a_pass"] = bool(abs(ncol.sum() - sumP.sum()) < 4 * np.sqrt(sumP.sum()))
    res["b_pass"] = bool(abs(sumP.mean() - expect) < 4 * res["sumP_per_step_se"] and
                         abs(sumP.mean() / expect - 1) < 0.005)
    json.dump(res, open(os.path.join(a.outdir, f"rate_{a.base}.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))


# ------------------------------------------------------------------------- conserve
def cmd_conserve(a):
    head, h = snap.read_history(os.path.join(a.rundir, f"{a.base}.nrpic.hst"))
    ci = snap.history_columns(head)
    smw = h[:, ci["sum_mW"]]
    valid = smw != 0
    drift = float(np.max(np.abs(smw[valid] / smw[valid][0] - 1))) if valid.any() else None
    res = dict(test="conserve", run=a.rundir, sum_mW_max_rel_drift=drift)
    for c in ("sum_mux", "sum_muy", "sum_muz"):
        res[c + "_max_abs_change"] = float(np.max(np.abs(h[:, ci[c]] - h[0, ci[c]])))
    res["pass_drift"] = bool(drift is not None and drift < 1e-11)
    json.dump(res, open(os.path.join(a.outdir, f"conserve_{a.base}.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))


# ------------------------------------------------------------------------- repro
def cmd_repro(a):
    ref = snap.read_snapshot(a.snaps[0])
    out = dict(test="repro", reference=a.snaps[0], same={})
    for p in a.snaps[1:]:
        s = snap.read_snapshot(p)
        same = (s["cycle"] == ref["cycle"] and np.array_equal(s["tag"], ref["tag"]) and
                np.array_equal(s["x"], ref["x"]) and np.array_equal(s["u"], ref["u"]) and
                np.array_equal(s["m"], ref["m"]))
        out["same"][p] = bool(same)
        if not same and np.array_equal(s["tag"], ref["tag"]):
            out.setdefault("max_du", {})[p] = float(np.abs(s["u"] - ref["u"]).max())
    out["pass"] = all(out["same"].values())
    print(json.dumps(out, indent=1))
    return 0 if out["pass"] else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("relax", "mode", "rate"):
        p = sub.add_parser(name)
        p.add_argument("rundir"); p.add_argument("base"); p.add_argument("meta")
        p.add_argument("outdir")
        p.add_argument("--col", action="append")
    p = sub.add_parser("conserve")
    p.add_argument("rundir"); p.add_argument("base"); p.add_argument("outdir")
    p = sub.add_parser("repro")
    p.add_argument("snaps", nargs="+")
    a = ap.parse_args()
    if a.cmd != "repro":
        os.makedirs(a.outdir, exist_ok=True)
    return dict(relax=cmd_relax, mode=cmd_mode, rate=cmd_rate, conserve=cmd_conserve,
                repro=cmd_repro)[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main() or 0)
