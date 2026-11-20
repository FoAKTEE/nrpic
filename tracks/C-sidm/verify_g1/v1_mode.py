"""V1b: decay rate of the isobaric (entropy) mode from the T7 runs, own analysis.

Inputs per case directory: case.json (set-up), reduced.npz (Fourier sums of every
snapshot, written by the run driver), the first and the last snapshot (checked against
reduced.npz with my own sums). Separation of sound and entropy mode (JOURNAL entry 1):
A_n = c1_M/sM, A_p = c1_MK/sMK, A_s = A_n - (c_v/c_p) A_p (adiabatic sound has
delta s = c_v dp/p - c_p dn/n = 0, so A_s carries the entropy mode only).

Two estimates per case:
 (1) the definition of TESTS.md T7: A = A0 exp(-Gamma t) on [10 t_coll, 2/Gamma],
     kappa = Gamma n c_p/k^2, ratio to kappa_1 = (75 sqrt(pi)/64) sqrt(theta)/sigma;
 (2) the nonlinear isobaric reference (heat_ref.py) with kappa = f kappa_1(T):
     A_s(t) = a A_ref(f t), f = kappa/kappa_1 with the eps = 0.2 nonlinearity removed.
Seed scatter gives the error; extrapolation linear in (k lambda)^2 to zero.
"""
import argparse
import glob
import json
import os
import sys

import numpy as np
from scipy.optimize import curve_fit, least_squares

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, "/data/haiyangw/nrpic/wt/C-sidm/python")
import lib  # noqa: E402
import heat_ref  # noqa: E402

K1C = 75*np.sqrt(np.pi)/64
RUNS = ["C-20261119-144545-c606492", "C-20261119-155434-8563453"]
SCR = "/data/haiyangw/nrpic/scratch/C-sidm"


def own_sums(snap, k, x0):
    x = snap["x"][:, 0] - x0
    M = snap["m"]
    u = snap["u"]
    W = np.sqrt(1 + np.einsum("ij,ij->i", u, u))
    K = W - 1
    c = np.cos(k*x)
    return dict(sM=M.sum(), sMK=(M*K).sum(), c1_M=(M*c).sum(), c1_MK=(M*K*c).sum(),
                s1_M=(M*np.sin(k*x)).sum())


def profile(snap, k, x0, nb=32):
    """binned density and temperature (2/3 <K>, non-relativistic) over one wavelength"""
    x = np.mod(snap["x"][:, 0] - x0, 2*np.pi/k)
    u = snap["u"]
    W = np.sqrt(1 + np.einsum("ij,ij->i", u, u))
    b = np.floor(x/(2*np.pi/k)*nb).astype(int)
    cnt = np.bincount(b, minlength=nb)
    kin = np.bincount(b, weights=W - 1, minlength=nb)
    xc = (np.arange(nb) + 0.5)/nb*2*np.pi/k
    return xc, cnt/cnt.mean(), (kin/cnt)/(kin.sum()/cnt.sum())


def fit_exp(t, A, t0, t1):
    s = (t >= t0) & (t <= t1)
    p, cov = curve_fit(lambda tt, a, g: a*np.exp(-g*tt), t[s], A[s],
                       p0=[A[s][0]*np.exp(1e-3*t[s][0]), 1e-3])
    return p, np.sqrt(np.diag(cov)), s


def window_fit(t, A, tcoll, g0):
    g = g0
    for _ in range(5):
        p, e, s = fit_exp(t, A, 10*tcoll, 2.0/g)
        g = p[1]
    return p, e, s


class Ref:
    """nonlinear isobaric reference for one (k, eps, theta0) at f = 1"""

    def __init__(self, k, eps, theta0, cp, tmax, adiabatic=False, N=512):
        T, dm, P, Mtot = heat_ref.mode_initial(eps, theta0, 1.0, k, N, adiabatic)
        self.t = np.linspace(0, tmax, 3001)
        Tt = heat_ref.evolve(T, dm, P, 1.0, cp, self.t)
        self.A, self.L = heat_ref.mode_amplitude(Tt, dm, P, k)
        self.Lexact = 2*np.pi/k

    def __call__(self, tt):
        return np.interp(tt, self.t, self.A)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = a.out or lib.run_dir(SCR + "/tmp/verify_g1/v1_mode")
    os.makedirs(out, exist_ok=True)
    cases = sorted(c for r in RUNS for c in glob.glob(f"{SCR}/{r}/T7_*"))
    theta0 = 0.003
    cv = lib.c_v(theta0)
    cp = cv + 1
    refs = {}
    rows = []
    store = {}
    for cdir in cases:
        cs = json.load(open(os.path.join(cdir, "case.json")))
        d = np.load(os.path.join(cdir, "reduced.npz"))
        k = cs["k"]
        lam = cs["lam"]
        sig = cs["sigma"]
        eps = cs["eps"]
        x0 = 10.0
        # 1. reduced.npz against my own sums of the two snapshots that remain
        chk = []
        for idx, fn in [(0, "heat.part.00000.bin"), (-1, sorted(glob.glob(cdir + "/heat.part.*.bin"))[-1])]:
            sn = lib.read_snap(os.path.join(cdir, fn) if not fn.startswith("/") else fn)
            o = own_sums(sn, k, x0)
            assert abs(sn["time"] - d["time"][idx]) < 1e-9*max(1, sn["time"])
            chk.append(max(abs(o["c1_M"] - d["c1_M"][idx])/abs(d["sM"][idx]),
                           abs(o["c1_MK"] - d["c1_MK"][idx])/abs(d["sMK"][idx]),
                           abs(o["sM"] - d["sM"][idx])/abs(d["sM"][idx])))
            if idx == 0:
                xc, nprof, tprof = profile(sn, k, x0)
                # amplitude fits of the initial profiles
                cc = np.cos(k*xc)
                an = -2*np.mean((nprof - 1)*cc)
                at = 2*np.mean((tprof/np.mean(tprof) - 1)*cc)
        t = d["time"]
        An = d["c1_M"]/d["sM"]
        Ap = d["c1_MK"]/d["sMK"]
        As = An - (cv/cp)*Ap
        tcoll = cs["t_coll"]
        g1 = K1C*np.sqrt(theta0)*lam*k**2/cp          # kappa_1 k^2/(n c_p), n = 1
        pS, eS, sS = window_fit(t, As, tcoll, g1)
        pN, eN, sN = window_fit(t, An, tcoll, g1)
        # 2. nonlinear reference fit
        key = (k, eps)
        if key not in refs:
            refs[key] = Ref(k, eps, theta0, cp, 1.6*t[-1]*K1C*np.sqrt(theta0)*lam*k**2/cp/g1)
            refs[(k, eps, "ad")] = Ref(k, eps, theta0, cp,
                                      1.6*t[-1]*K1C*np.sqrt(theta0)*lam*k**2/cp/g1,
                                      adiabatic=True)
        R = refs[key]
        Rad = refs[(k, eps, "ad")]
        tw0, tw1 = 10*tcoll, 2.0/pS[1]
        sw = (t >= tw0) & (t <= tw1)

        def resid(p, RR):
            return p[0]*RR(p[1]*t[sw]) - As[sw]
        lsq = least_squares(resid, [1.0, 1.0], args=(R,))
        lsq_ad = least_squares(resid, [1.0, 1.0], args=(Rad,))
        J = lsq.jac
        s2 = np.sum(lsq.fun**2)/max(1, sw.sum() - 2)
        cov = np.linalg.inv(J.T @ J)*s2
        # nonlinearity factor of the T7 estimator: exponential fit of the reference itself
        # on the same sample times and window (f = 1)
        pR, _, _ = fit_exp(t, R(t), tw0, tw1)
        row = dict(case=os.path.basename(cdir), run=os.path.basename(os.path.dirname(cdir)),
                   k_lambda=cs["k_lambda"], seed=cs["seed"], eps=eps, k=k,
                   n_points_fit=int(sS.sum()), window=[tw0, tw1],
                   reduced_check_max_rel=max(chk), init_n_amp=an, init_T_amp=at,
                   Gamma_s=pS[1], Gamma_s_err=eS[1], Gamma_n=pN[1], Gamma_n_err=eN[1],
                   Gamma_kappa1=g1,
                   ratio_T7_s=pS[1]/g1, ratio_T7_n=pN[1]/g1,
                   f_nonlinear=lsq.x[1], f_nonlinear_err=np.sqrt(cov[1, 1]),
                   f_nonlinear_adiabatic=lsq_ad.x[1], amp_nonlinear=lsq.x[0],
                   ref_nl_factor=pR[1]/g1,
                   resid_rms_s=float(np.std(As[sS] - pS[0]*np.exp(-pS[1]*t[sS]))),
                   resid_rms_n=float(np.std(An[sN] - pN[0]*np.exp(-pN[1]*t[sN]))),
                   ref_volume_drift=float(np.max(np.abs(R.L/R.Lexact - 1))))
        rows.append(row)
        store[row["case"]] = dict(t=t, An=An, Ap=Ap, As=As, pS=pS, pN=pN, g1=g1,
                                  f=lsq.x, R=R, tcoll=tcoll)
        print(json.dumps({kk: (round(v, 6) if isinstance(v, float) else v)
                          for kk, v in row.items() if kk not in ("window",)}))
    # seed statistics and extrapolation
    summ = {}
    for est in ["ratio_T7_s", "ratio_T7_n", "f_nonlinear", "f_nonlinear_adiabatic"]:
        kl = sorted(set(r["k_lambda"] for r in rows))
        per = []
        for q in kl:
            v = np.array([r[est] for r in rows if r["k_lambda"] == q])
            per.append(dict(k_lambda=q, n=len(v), mean=v.mean(), std=v.std(ddof=1),
                            se=v.std(ddof=1)/np.sqrt(len(v))))
        x = np.array([p["k_lambda"]**2 for p in per])
        y = np.array([p["mean"] for p in per])
        w = 1/np.array([p["se"] for p in per])**2
        A = np.vstack([np.ones_like(x), x]).T
        C = np.linalg.inv(A.T @ (A*w[:, None]))
        beta = C @ (A.T @ (w*y))
        chi2 = float(np.sum(w*(y - A @ beta)**2))
        summ[est] = dict(per_k=per, intercept=beta[0], intercept_se=np.sqrt(C[0, 0]),
                         slope=beta[1], slope_se=np.sqrt(C[1, 1]), chi2=chi2,
                         dof=len(x) - 2)
        print(est, json.dumps(summ[est], default=float))
    lib.save_json(os.path.join(out, "v1_mode.json"), dict(rows=rows, summary=summ,
                  theta0=theta0, c_v=cv, c_p=cp, kappa1_coeff=K1C))
    figures(out, rows, store, summ)


def figures(out, rows, store, summ):
    from nrpic import figstyle
    import matplotlib.pyplot as plt
    figstyle.use_style()
    P = figstyle.PAL
    # Figure 1: one case of each k lambda: amplitudes and residuals
    fig, ax = plt.subplots(2, 3, figsize=(8, 5), sharex="col")
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.1, top=0.93, wspace=0.32,
                        hspace=0.06)
    for j, q in enumerate([0.1, 0.2, 0.4]):
        name = [r["case"] for r in rows if r["k_lambda"] == q and r["seed"] == 1][0]
        s = store[name]
        t = s["t"]
        ax[0, j].plot(t, -s["An"], "o", ms=3, color=P["red"], label=r"$-A_n$")
        ax[0, j].plot(t, -s["As"], "s", ms=3, mfc="none", color=P["blue"],
                      label=r"$-A_s$ (entropy)")
        ax[0, j].plot(t, -s["Ap"], "^", ms=3, color=P["green"], label=r"$-A_p$ (pressure)")
        tt = np.linspace(0, t[-1], 300)
        ax[0, j].plot(tt, -s["pS"][0]*np.exp(-s["pS"][1]*tt), "k-", lw=1,
                      label="exp fit to $A_s$")
        ax[0, j].plot(tt, -s["f"][0]*s["R"](s["f"][1]*tt), "k--", lw=1,
                      label="nonlinear ref. fit")
        ax[0, j].axvspan(10*s["tcoll"], 2/s["pS"][1], color="grey", alpha=0.1)
        ax[0, j].set_title(r"$k\lambda=%g$, seed 1" % q)
        ax[1, j].plot(t, s["As"] - s["pS"][0]*np.exp(-s["pS"][1]*t), "s", ms=3,
                      mfc="none", color=P["blue"], label=r"$A_s$ - exp fit")
        ax[1, j].plot(t, s["An"] - s["pN"][0]*np.exp(-s["pN"][1]*t), "o", ms=3,
                      color=P["red"], label=r"$A_n$ - its exp fit")
        ax[1, j].axhline(0, color="k", lw=0.8)
        ax[1, j].set_xlabel("t")
    ax[0, 0].set_ylabel("mode amplitude (cos kx)")
    ax[1, 0].set_ylabel("residual")
    ax[0, 0].legend(loc="upper right", fontsize=7)
    ax[1, 0].legend(loc="lower right", fontsize=7)
    fig.savefig(os.path.join(out, "v1b_mode_amplitudes.png"))
    plt.close(fig)
    # Figure 2: kappa/kappa_1 against (k lambda)^2
    fig, axs = plt.subplots(1, 2, figsize=(8, 3.6), gridspec_kw=dict(width_ratios=[2, 1]))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.14, top=0.95, wspace=0.3)
    ax = axs[1]
    sm = summ["ratio_T7_n"]
    ax.plot([r["k_lambda"]**2 for r in rows], [r["ratio_T7_n"] for r in rows], ".",
            color=P["yellow"], alpha=0.5)
    ax.errorbar([p["k_lambda"]**2 for p in sm["per_k"]], [p["mean"] for p in sm["per_k"]],
                yerr=[p["se"] for p in sm["per_k"]], fmt="o", color=P["yellow"],
                label="T7 estimator on $A_n$\n(sound not removed)")
    ax.axhspan(0.99, 1.06, color="grey", alpha=0.15)
    ax.set_xlabel(r"$(k\lambda)^2$")
    ax.legend(loc="upper left", fontsize=7)
    ax = axs[0]
    for est, col, lab, off in [("ratio_T7_s", P["red"], "T7 estimator on $A_s$", -0.002),
                               ("f_nonlinear", P["blue"], "nonlinear reference fit", 0.002)]:
        xs = [r["k_lambda"]**2 + off for r in rows]
        ax.plot(xs, [r[est] for r in rows], ".", color=col, alpha=0.5)
        sm = summ[est]
        ax.errorbar([p["k_lambda"]**2 + off for p in sm["per_k"]],
                    [p["mean"] for p in sm["per_k"]], yerr=[p["se"] for p in sm["per_k"]],
                    fmt="o", color=col, label=lab)
        xx = np.linspace(0, 0.17, 10)
        ax.plot(xx, sm["intercept"] + sm["slope"]*xx, "-", color=col, lw=1)
        ax.errorbar([0], [sm["intercept"]], yerr=[sm["intercept_se"]], fmt="D",
                    color=col, ms=5)
    ax.axhspan(0.99, 1.06, color="grey", alpha=0.15, label="T7 pass interval")
    ax.axhline(1.0296, color="k", ls="--", lw=1, label="CE (rel., order 4) at 0.003")
    ax.set_xlabel(r"$(k\lambda)^2$")
    ax.set_ylabel(r"$\kappa/\kappa_1$")
    ax.set_ylim(0.95, 1.10)
    ax.legend(loc="upper left", fontsize=7, ncol=2)
    fig.savefig(os.path.join(out, "v1b_kappa_ratio.png"))
    plt.close(fig)


if __name__ == "__main__":
    main()
