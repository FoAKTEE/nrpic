"""V4: own static spherically symmetric Einstein-Vlasov equilibria and their thresholds.

Family (JOURNAL entry 9): f = (exp((E0 - E)/T_inf) - 1)_+, E = eps e^mu, T_inf = b E0;
b = 1 is the King model of arXiv:2009.08163 (paper.tex line 635), b = 0.1 the truncated
Maxwell-Boltzmann core of arXiv:2108.11967 (F21, main.tex lines 113-144).
Variables y = ln E0 - mu (eps_c = e^y, T = b e^y), m(r), N(r); Schwarzschild coordinates,
G = c = m = 1; with coefficient 1 the moments equal F21's hat quantities (unit zeta).

Radial pulsation (Chandrasekhar's equation, F21 lines 202-204) in variational form, Rayleigh-Ritz
with xi_k = r e^Phi (r/R)^(2k); K = 1 is F21's trial function. Adiabatic index: F21's
1 + p/u or the Maxwell-Juttner Gamma_1(T) = 1 + 1/c_v(T) of the local temperature.
"""
import argparse
import json
import os
import sys

import numpy as np
from scipy import integrate, linalg, optimize, special

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "python"))
import lib  # noqa: E402

GS, GW = special.roots_legendre(48)
GS = 0.5*(GS + 1)          # s in [0, 1]
GW = 0.5*GW


def moments(y, b):
    """n, rho, p at local cutoff e^y (eps = 1 + k s^2, k = e^y - 1)."""
    if y <= 0:
        return 0.0, 0.0, 0.0
    k = np.expm1(y)
    eps = 1 + k*GS**2
    if isinstance(b, str):          # "poly<k>": polytropic ansatz f = (1 - E/E0)^k_+ (2009.08163 l. 631)
        f = (1 - eps*np.exp(-y))**float(b[4:])
    else:
        T = b*np.exp(y)
        f = np.expm1(k*(1 - GS**2)/T)
    sq = GS*np.sqrt(k*(2 + k*GS**2))           # sqrt(eps^2 - 1)
    jac = 2*k*GS                               # d eps / ds
    n = 4*np.pi*np.sum(GW*f*eps*sq*jac)
    rho = 4*np.pi*np.sum(GW*f*eps**2*sq*jac)
    p = 4*np.pi/3*np.sum(GW*f*sq**3*jac)
    return n, rho, p


def solve(y0, b, dense=False):
    n0, rho0, p0 = moments(y0, b)
    r0 = 1e-6/np.sqrt(rho0)
    m_init = 4*np.pi/3*rho0*r0**3
    y_init = y0 - 2*np.pi/3*(rho0 + 3*p0)*r0**2
    N_init = 4*np.pi/3*n0*r0**3

    def rhs(r, s):
        m, y, N = s
        n, rho, p = moments(y, b)
        dy = -(m + 4*np.pi*r**3*p)/(r*(r - 2*m))
        return [4*np.pi*r*r*rho, dy, 4*np.pi*r*r*n/np.sqrt(1 - 2*m/r)]

    def surf(r, s):
        return s[1]
    surf.terminal = True
    surf.direction = -1
    sol = integrate.solve_ivp(rhs, [r0, 1e4], [m_init, y_init, N_init], method="DOP853",
                              rtol=1e-12, atol=1e-16, events=surf, dense_output=dense)
    R = sol.t_events[0][0]
    M, _, N = sol.y_events[0][0]
    C = M/R
    Z0 = np.exp(y0)/np.sqrt(1 - 2*C) - 1
    out = dict(y0=y0, b=b, w0=(-np.expm1(-y0)/b if not isinstance(b, str) else None), M=M, R=R, N=N, C=C, Eb=(N - M)/N, B=N - M,
               Z0=Z0, eps_c0=np.expm1(y0), rho0=rho0, p0=p0, v0=np.sqrt(3*p0/rho0))
    return out, (sol if dense else None)


def gamma1_mj(T):
    return 1 + 1/lib.c_v(T)


def background(eq, sol, b, J):
    """Background on the Gauss points of J elements uniform in u = sqrt(r/R)."""
    R = eq["R"]
    tq, wq = special.roots_legendre(6)
    tq = 0.5*(tq + 1)
    wq = 0.5*wq
    h = 1.0/J
    ue = np.arange(J)*h
    u = (ue[:, None] + h*tq[None, :]).ravel()
    wu = np.tile(wq*h, J)
    r = R*u*u
    wr = wu*2*R*u
    S = sol.sol(r)
    m, y = S[0], S[1]
    mom = np.array([moments(yy, b) for yy in y])
    n, rho, p = mom[:, 0], mom[:, 1], mom[:, 2]
    T = b*np.exp(y)
    e2L = 1/(1 - 2*m/r)
    eL = np.sqrt(e2L)
    Phi = 0.5*np.log(1 - 2*eq["M"]/R) - y
    dp = -(rho + p)*(m + 4*np.pi*r**3*p)/(r*(r - 2*m))
    Q = 4*dp/r + 8*np.pi*e2L*p*(rho + p) - dp**2/(rho + p)
    return dict(J=J, h=h, tq=tq, u=u, wu=wu, r=r, wr=wr, n=n, rho=rho, p=p, T=T, e2L=e2L, eL=eL,
                Phi=Phi, Q=Q, R=R)


def fem_lowest(bg, g):
    """Lowest omega^2 with xi = r e^Phi eta, eta piecewise linear in u (J elements):
    A = int e^{3Phi+Lam} g p/r^2 zeta'^2 + e^{Phi+Lam} r^2 Q xi^2, zeta = r^3 eta;
    B = int e^{3Lam-Phi} (rho+p) r^2 xi^2. Diagonal scaling before eigh."""
    J, h, R = bg["J"], bg["h"], bg["R"]
    r, wr, u = bg["r"], bg["wr"], bg["u"]
    t = np.tile(bg["tq"], J)
    el = np.repeat(np.arange(J), len(bg["tq"]))
    phiL, phiR = 1 - t, t
    dL = -1/h/(2*R*u)
    dR = 1/h/(2*R*u)
    wA1 = wr*np.exp(3*bg["Phi"])*bg["eL"]*g*bg["p"]/r**2
    xs2 = (r*np.exp(bg["Phi"]))**2
    wA2 = wr*np.exp(bg["Phi"])*bg["eL"]*r**2*bg["Q"]*xs2
    wB = wr*bg["eL"]**3*np.exp(-bg["Phi"])*(bg["rho"] + bg["p"])*r**2*xs2
    zL = 3*r**2*phiL + r**3*dL
    zR = 3*r**2*phiR + r**3*dR
    A = np.zeros((J + 1, J + 1))
    B = np.zeros((J + 1, J + 1))
    for (ia, za, fa) in [(0, zL, phiL), (1, zR, phiR)]:
        for (ib, zb, fb) in [(0, zL, phiL), (1, zR, phiR)]:
            va = wA1*za*zb + wA2*fa*fb
            vb = wB*fa*fb
            np.add.at(A, (el + ia, el + ib), va)
            np.add.at(B, (el + ia, el + ib), vb)
    sc = 1/np.sqrt(np.diag(B))
    As = A*sc[:, None]*sc[None, :]
    Bs = B*sc[:, None]*sc[None, :]
    lam, vec = linalg.eigh(As, Bs, subset_by_index=[0, 0])
    eta = vec[:, 0]*sc
    # constant eta (F21 trial function) Rayleigh quotient from the same matrices
    one = np.ones(J + 1)
    rq1 = one @ A @ one/(one @ B @ one)
    return float(lam[0]), float(rq1), eta


def pulsation(y0, b, J=200, Js=()):
    """Lowest omega^2 (FEM, J elements; also Js for convergence) for gamma = 1 + p/u and
    Gamma_1(T); F21's <gamma> and closed-form gamma_cr (main.tex lines 455-461)."""
    eq, sol = solve(y0, b, dense=True)
    res = dict(eq)
    bg = background(eq, sol, b, J)
    r, wr, p, rho, n, e2L, eL, Phi = (bg[k] for k in ["r", "wr", "p", "rho", "n", "e2L", "eL", "Phi"])
    g_f21 = 1 + p/(rho - n)
    g_mj = np.array([gamma1_mj(t) for t in bg["T"]])
    g_mjpu = np.array([1 + t/(lib.mean_w(t) - 1) for t in bg["T"]])   # 1 + p/u of a full MJ gas
    e3 = np.exp(3*Phi)*eL
    den = np.sum(wr*e3*p*r**2)
    t1 = np.sum(wr*e3*(16*p + (e2L - 1)*(rho + p))*(e2L - 1)*r**2)/den/36
    t2 = 4*np.pi/9*np.sum(wr*np.exp(3*Phi)*eL**3*(8*p + (e2L + 1)*(rho + p))*p*r**4)/den
    t3 = 16*np.pi**2/9*np.sum(wr*np.exp(3*Phi)*eL**5*(rho + p)*p**2*r**6)/den
    res["gamma_cr"] = 4/3 + t1 + t2 + t3
    res["gavg_f21"] = np.sum(wr*e3*g_f21*p*r**2)/den
    res["gavg_mj"] = np.sum(wr*e3*g_mj*p*r**2)/den
    n0, rho0, p0 = moments(y0, b)
    res["gamma_c"] = 1 + p0/(rho0 - n0)
    res["T_c"] = b*np.exp(y0)
    res["Gamma1_c"] = gamma1_mj(res["T_c"])
    B00 = np.sum(wr*eL**3*np.exp(-Phi)*(rho + p)*r**2*(r*np.exp(Phi))**2)
    res["gavg_mjpu"] = np.sum(wr*e3*g_mjpu*p*r**2)/den
    for lab, g in [("f21", g_f21), ("mj", g_mj), ("mjpu", g_mjpu)]:
        lam, rq1, eta = fem_lowest(bg, g)
        res["omega2_" + lab] = lam
        res["omega2K1_" + lab] = rq1
        res["eta_" + lab] = eta
    res["check_f21_closed_vs_rq"] = res["omega2K1_f21"]*B00/(9*den) - (res["gavg_f21"] - res["gamma_cr"])
    for JJ in Js:
        bgj = background(eq, sol, b, JJ)
        gj_f = 1 + bgj["p"]/(bgj["rho"] - bgj["n"])
        gj_m = np.array([gamma1_mj(t) for t in bgj["T"]])
        res[f"omega2_f21_J{JJ}"] = fem_lowest(bgj, gj_f)[0]
        res[f"omega2_mj_J{JJ}"] = fem_lowest(bgj, gj_m)[0]
    return res


def argmax(fun, lo, hi):
    r = optimize.minimize_scalar(lambda t: -fun(t), bounds=(lo, hi), method="bounded",
                                 options=dict(xatol=1e-8))
    return float(r.x)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = a.out or lib.run_dir("/data/haiyangw/nrpic/scratch/C-sidm/tmp/verify_g1/v4")
    os.makedirs(out, exist_ok=True)
    res = {}
    # ---------- check against F21 Table 1 (b = 0.1), main.tex lines 490-503
    f21_rows = [  # w0, M, Erest, eps, R, Z0, rho0, p0, v0, <gamma>, gamma_cr
        (0.6, 3.47240e-2, 3.51790e-2, 1.29311e-2, 1.63800, 8.71214e-2, 5.82063e-2, 9.86165e-4, 2.25450e-1, 1.65936, 1.37799),
        (1.9, 2.72897e-2, 2.81385e-2, 3.01659e-2, 5.81001e-1, 2.96903e-1, 2.33058, 1.21454e-1, 3.95398e-1, 1.64377, 1.47651),
        (3.2, 1.84498e-2, 1.91224e-2, 3.51754e-2, 3.78001e-1, 5.47883e-1, 2.22039e1, 1.89599, 5.06132e-1, 1.62919, 1.57054),
        (4.05150, 1.42556e-2, 1.47424e-2, 3.30243e-2, 3.68001e-1, 7.50107e-1, 8.17923e1, 8.74006, 5.66189e-1, 1.62117, 1.62117),
        (4.5, 1.27271e-2, 1.31271e-2, 3.04753e-2, 4.13001e-1, 8.76941e-1, 1.60208e2, 1.89661e1, 5.95948e-1, 1.61808, 1.63933),
    ]
    chk = []
    for row in f21_rows:
        w0 = row[0]
        y0 = -np.log(1 - 0.1*w0)
        pr = pulsation(y0, 0.1)
        mine = (pr["M"], pr["N"], pr["Eb"], pr["R"], pr["Z0"], pr["rho0"], pr["p0"], pr["v0"],
                pr["gavg_f21"], pr["gamma_cr"])
        names = ["M", "Erest", "eps", "R", "Z0", "rho0", "p0", "v0", "gavg", "gamma_cr"]
        d = dict(w0=w0, y0=y0, check_closed=pr["check_f21_closed_vs_rq"],
                 omega2K1_f21=pr["omega2K1_f21"], omega2_f21=pr["omega2_f21"],
                 omega2K1_mj=pr["omega2K1_mj"], omega2_mj=pr["omega2_mj"])
        for nm, mv, pv in zip(names, mine, row[1:]):
            d[nm] = [mv, pv, mv/pv - 1]
        chk.append(d)
        print("F21 check", json.dumps(d, default=float))
    res["f21_table_check"] = chk
    # ---------- (a) King b = 1: E_b maximum and zero
    king = lambda t: solve(t, 1.0)[0]["Eb"]
    ymax = argmax(king, 0.25, 0.45)
    yzero = optimize.brentq(king, 0.6, 0.95, xtol=1e-10)
    res["king"] = dict(y_Ebmax=ymax, Eb_max=king(ymax), y_Ebzero=yzero,
                       eq_at_max=solve(ymax, 1.0)[0])
    print("King", res["king"])
    # ---------- (c) F21 b = 0.1 turning points
    fb = 0.1
    ylim = -np.log(1 - fb*6.0)
    yE = argmax(lambda t: solve(t, fb)[0]["M"], 0.01, 0.3)
    yB = argmax(lambda t: solve(t, fb)[0]["B"], 0.1, 0.4)
    yeps = argmax(lambda t: solve(t, fb)[0]["Eb"], 0.25, 0.5)
    res["f21_turning"] = {k: solve(v, fb)[0] for k, v in [("E", yE), ("B", yB), ("eps", yeps)]}
    print("F21 turning", json.dumps(res["f21_turning"], default=float))

    # ---------- onsets: F21 trial function (K1) and finite elements (J = 200; J = 400 check)
    keys = ["y0", "w0", "Z0", "v0", "C", "M", "R", "N", "Eb", "gavg_f21", "gavg_mj", "gamma_cr",
            "gamma_c", "Gamma1_c", "T_c", "omega2K1_f21", "omega2_f21", "omega2K1_mj", "omega2_mj",
            "gavg_mjpu", "omega2K1_mjpu", "omega2_mjpu"]

    def val(pr, lab, kind):
        return pr[("omega2K1_" if kind == "K1" else "omega2_") + lab]

    def onset(b, lab, kind, lo, hi, J=200):
        fn = lambda t: val(pulsation(t, b, J=J), lab, kind)
        return optimize.brentq(fn, lo, hi, xtol=1e-10)

    ons = {}
    scans = {}
    for fam, b, lo, hi in [("king", 1.0, 0.002, 0.7), ("f21", 0.1, 0.02, ylim)]:
        ys = np.linspace(lo, hi, 70)
        scan = [pulsation(t, b) for t in ys]
        scans[fam] = [{k: s[k] for k in keys} for s in scan]
        for lab in ["f21", "mj", "mjpu"]:
            for kind in ["K1", "FEM"]:
                vals = np.array([val(s, lab, kind) for s in scan])
                idx = np.where((vals[:-1] > 0) & (vals[1:] <= 0))[0]
                name = f"{fam}_{lab}_{kind}"
                if len(idx) == 0:
                    ons[name] = dict(none=True, first=float(vals[0]), last=float(vals[-1]))
                    print("onset", name, "none in scan", vals[0], vals[-1])
                    continue
                y_on = onset(b, lab, kind, ys[idx[0]], ys[idx[0] + 1])
                pr = pulsation(y_on, b, Js=(100, 400))
                d = {k: pr[k] for k in keys}
                d.update({k: pr[k] for k in pr if k.startswith("omega2_") and "_J" in k})
                if kind == "FEM":
                    d["y0_J400"] = onset(b, lab, kind, ys[idx[0]], ys[idx[0] + 1], J=400)
                    d["eta"] = [float(v) for v in pr["eta_" + lab]]
                d["n_crossings_in_scan"] = int(len(idx))
                ons[name] = d
                print("onset", name, json.dumps({k: d[k] for k in keys + (["y0_J400"] if kind == "FEM" else [])}, default=float))
    res["onsets"] = ons
    res["scans"] = scans
    lib.save_json(os.path.join(out, "v4_ev.json"), res)
    figures(out, res)


def figures(out, res):
    from nrpic import figstyle
    import matplotlib.pyplot as plt
    figstyle.use_style()
    P = figstyle.PAL
    fig, ax = plt.subplots(2, 2, figsize=(8, 6.4))
    fig.subplots_adjust(left=0.1, right=0.91, bottom=0.08, top=0.95, wspace=0.42, hspace=0.33)
    # King E_b
    ys = np.linspace(0.02, 0.9, 120)
    eb = [solve(t, 1.0)[0]["Eb"] for t in ys]
    ax[0, 0].plot(ys, eb, color=P["blue"])
    k = res["king"]
    ax[0, 0].axvline(k["y_Ebmax"], **figstyle.GUIDE)
    ax[0, 0].axvline(0.334, color=P["red"], lw=1, ls=":")
    ax[0, 0].axhline(0, color="k", lw=0.8)
    ax[0, 0].set_xlabel(r"$y_0$ (King, $b$ = 1)")
    ax[0, 0].set_ylabel(r"$E_b = (N - M)/N$")
    ax[0, 0].set_title(r"max at $y_0$ = %.5f (dashed); paper 0.334 (dotted)" % k["y_Ebmax"], fontsize=8)
    # King omega^2
    sc = res["scans"]["king"]
    y = [s["y0"] for s in sc]
    for lab, col, nm in [("f21", P["green"], r"$\gamma = 1 + p/u$"), ("mj", P["red"], r"$\Gamma_1(T)$ Juttner")]:
        ax[0, 1].plot(y, [s["omega2_" + lab] for s in sc], color=col, label=nm + ", exact (FEM)")
        ax[0, 1].plot(y, [s["omega2K1_" + lab] for s in sc], color=col, ls="--", lw=1, label=nm + r", $\xi = r e^\Phi$")
    ax[0, 1].axhline(0, color="k", lw=0.8)
    ax[0, 1].axvline(k["y_Ebmax"], **figstyle.MASK_LINE)
    ax[0, 1].set_xlabel(r"$y_0$ (King, $b$ = 1)")
    ax[0, 1].set_ylabel(r"$\omega_0^2$ (Rayleigh-Ritz)")
    ax[0, 1].set_yscale("symlog", linthresh=1e-3)
    ax[0, 1].legend(fontsize=6)
    # F21 b = 0.1
    sc = res["scans"]["f21"]
    Z = [s["Z0"] for s in sc]
    for lab, col, nm in [("f21", P["green"], r"$\gamma = 1 + p/u$"), ("mj", P["red"], r"$\Gamma_1(T)$ Juttner")]:
        ax[1, 0].plot(Z, [s["omega2_" + lab] for s in sc], color=col, label=nm + ", exact (FEM)")
        ax[1, 0].plot(Z, [s["omega2K1_" + lab] for s in sc], color=col, ls="--", lw=1, label=nm + r", $\xi = r e^\Phi$")
    ax[1, 0].axhline(0, color="k", lw=0.8)
    ax[1, 0].axvline(0.750, color=P["green"], lw=1, ls=":")
    ax[1, 0].set_xlabel(r"$Z(0)$ (F21, $b$ = 0.1)")
    ax[1, 0].set_ylabel(r"$\omega_0^2$")
    ax[1, 0].set_yscale("symlog", linthresh=1e-1)
    ax[1, 0].legend(fontsize=6)
    ax[1, 1].plot(Z, [s["Eb"] for s in sc], color=P["blue"], label=r"$\varepsilon$")
    ax2 = ax[1, 1].twinx()
    ax2.plot(Z, [s["gavg_f21"] for s in sc], color=P["green"], lw=1, label=r"$\langle 1 + p/u\rangle$")
    ax2.plot(Z, [s["gavg_mj"] for s in sc], color=P["red"], lw=1, label=r"$\langle\Gamma_1\rangle$")
    ax2.plot(Z, [s["gamma_cr"] for s in sc], color="k", lw=1, ls="--", label=r"$\gamma_{cr}$")
    ax2.legend(fontsize=6, loc="lower left")
    t = res["f21_turning"]
    for kk, col in [("E", P["orange"]), ("B", P["yellow"]), ("eps", P["blue"])]:
        ax[1, 1].axvline(t[kk]["Z0"], color=col, lw=1, ls=":")
    ax[1, 1].set_xlabel(r"$Z(0)$ (F21, $b$ = 0.1)")
    ax[1, 1].set_ylabel(r"fractional binding energy $\varepsilon$")
    ax2.set_ylabel("adiabatic indices")
    fig.savefig(os.path.join(out, "v4_ev.png"))
    plt.close(fig)


if __name__ == "__main__":
    main()
