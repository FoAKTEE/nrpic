"""Lead re-check L2: independent derivations of the key claims of the wave-1 packages.

    python3 lead_checks.py OUTDIR

Written by the B-emd-gw lead, not by the helpers that made the claims; it uses none of
their code. Predictions P-L2a..f in tracks/B-emd-gw/JOURNAL.md (entry 2026-11-15T13:05Z).
Writes OUTDIR/lead_checks.json and OUTDIR/lead_checks.{pdf,png}.

a  polarization tensor of athenak/src/pgen/tests/z4c_linear_wave.cpp lines 107-112
b  plane-symmetric dust with x-independent transverse metric: decaying mode only
c  harmonic TT mode of a plane-symmetric slice on the torus and its overlap with K
d  quasi-static TT strain of two crossed sine waves (equation of arXiv:1604.06065)
e  Zel'dovich-ellipsoid GW energy by quadrature against the closed form
f  Zel'dovich sheet modes; second-order lapse drift in a closed box with a TT wave
"""
import json
import os
import sys

import numpy as np
import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "python"))
from nrpic import figstyle as fs  # noqa: E402


def check_a():
    """The generator's tensor, copied from the source, and with axy, ayz flipped."""
    def tensor(k, flip):
        k1, k2, k3 = k
        th = np.arctan2(np.hypot(k1, k2), k3)
        ph = np.arctan2(k1, k2)
        axx = -np.cos(th)**2*np.cos(2*ph) - np.cos(ph)**2*np.sin(th)**2
        axy = -0.25*(3 + np.cos(2*th))*np.sin(2*ph)
        axz = -np.cos(th)*np.sin(th)*np.sin(ph)
        ayy = np.cos(th)**2*np.cos(2*ph) - np.sin(th)**2*np.sin(ph)**2
        ayz = np.cos(th)*np.sin(th)*np.cos(ph)
        azz = np.sin(th)**2
        if flip:
            axy, ayz = -axy, -ayz
        return np.array([[axx, axy, axz], [axy, ayy, ayz], [axz, ayz, azz]])
    rng = np.random.default_rng(20261115)
    ks = rng.normal(size=(400, 3))
    res = {}
    for flip in (False, True):
        ek = np.array([np.linalg.norm(tensor(k, flip) @ k)/np.linalg.norm(k) for k in ks])
        tr = np.array([abs(np.trace(tensor(k, flip))) for k in ks])
        ee = np.array([np.sum(tensor(k, flip)**2) for k in ks])
        cosz = np.abs(ks[:, 2])/np.linalg.norm(ks, axis=1)
        res["flipped" if flip else "code"] = {
            "max_ek": float(ek.max()), "max_trace": float(tr.max()),
            "ee_range": [float(ee.min()), float(ee.max())],
            "ek_111": float(np.linalg.norm(tensor((1., 1., 1.), flip) @ np.ones(3))/np.sqrt(3)),
            "ek_100": float(np.linalg.norm(tensor((1., 0., 0.), flip) @ np.array([1., 0, 0]))),
            "_ek": ek, "_cosz": cosz}
    res["pass"] = bool(res["flipped"]["max_ek"] < 1e-12 and res["code"]["ek_111"] > 0.1
                       and res["code"]["ek_100"] < 1e-12)
    return res


def einstein_mixed(g, coords):
    """G^a_b of a diagonal metric g (sympy Matrix)."""
    n = len(coords)
    gi = g.inv()
    Gam = [[[sp.simplify(sum(gi[a, d]*(sp.diff(g[d, b], coords[c]) + sp.diff(g[d, c], coords[b])
                                         - sp.diff(g[b, c], coords[d])) for d in range(n))/2)
             for c in range(n)] for b in range(n)] for a in range(n)]
    Ric = sp.zeros(n)
    for b in range(n):
        for c in range(n):
            Ric[b, c] = sp.simplify(sum(sp.diff(Gam[a][b][c], coords[a]) for a in range(n))
                                    - sum(sp.diff(Gam[a][b][a], coords[c]) for a in range(n))
                                    + sum(Gam[a][a][d]*Gam[d][b][c] for a in range(n) for d in range(n))
                                    - sum(Gam[a][c][d]*Gam[d][b][a] for a in range(n) for d in range(n)))
    R = sp.simplify(sum(gi[a, b]*Ric[a, b] for a in range(n) for b in range(n)))
    G = sp.simplify(gi*Ric - R/2*sp.eye(n))
    return G


def check_b():
    t, x, y, z = sp.symbols("t x y z", real=True)
    A = sp.Function("A")(t)
    B = sp.Function("B")(t)
    f = sp.Function("f")(x)
    p = sp.symbols("p")
    # background Y = t^(2/3) is forced by G^x_x = 0 at f = 0; check it, then the modes
    Y = t**sp.Rational(2, 3)
    X = A + B*f
    g = sp.diag(-1, X**2, Y**2, Y**2)
    G = einstein_mixed(g, (t, x, y, z))
    Gxx = sp.simplify(G[1, 1])        # dust: zero
    Gyy = sp.simplify(G[2, 2])        # dust: zero
    Gtx = sp.simplify(G[0, 1])        # momentum constraint
    # G^x_x involves only Y: zero for Y = t^(2/3)
    gxx_ok = sp.simplify(Gxx) == 0
    # G^y_y = 0 for all x  <=>  A and B obey the same ODE; insert power laws
    ode = sp.simplify(sp.numer(sp.together(Gyy)))
    eqA = sp.simplify(ode.subs(f, 0).subs(A, t**p).doit())
    expA = sp.solve(sp.simplify(eqA/t**(p - 2)), p)
    # with A = t^(2/3) (the background), B = t^q: exponents of B
    q = sp.symbols("q")
    eqB = sp.simplify(ode.subs(A, Y).subs(B, t**q).doit())
    coef = sp.Poly(sp.expand(sp.simplify(eqB*t**(2 - q - sp.Rational(2, 3)))), f)
    expB = sp.solve(coef.coeffs()[0], q)
    D = [sp.simplify(t**qq/Y) for qq in expB]
    return {"Gxx_zero_for_Y_t23": bool(gxx_ok), "Gtx": str(Gtx),
            "exponents_A": [str(e) for e in expA], "exponents_B": [str(e) for e in expB],
            "D_modes": [str(d) for d in D],
            "pass": bool(gxx_ok and Gtx == 0 and set(D) == {sp.Integer(1), 1/t})}


def check_c():
    t, x = sp.symbols("t x", real=True)
    X = sp.Function("X")(t, x)
    Y = sp.Function("Y")(t, x)
    P = sp.Function("P")(x)
    g = sp.diag(X**2, Y**2, Y**2)
    sqrtg = X*Y**2
    Am = sp.diag(P, -P/2, -P/2)          # mixed A^i_j
    Aup = Am*g.inv()                     # A^ij = A^i_k g^kj
    # divergence of the mixed tensor: D_j A^j_i = (1/sqrtg) d_j (sqrtg A^j_i) - (1/2) d_i g_jk A^jk
    div_x = sp.simplify(sp.diff(sqrtg*Am[0, 0], x)/sqrtg
                        - sp.Rational(1, 2)*sum(sp.diff(g[j, k], x)*Aup[j, k]
                                                for j in range(3) for k in range(3)))
    sol = sp.dsolve(sp.Eq(div_x, 0), P)
    expected = sp.Symbol("C1")/Y**3
    sol_ok = sp.simplify(sol.rhs - expected) == 0 or \
        sp.simplify(sol.rhs*Y**3).free_symbols <= {sp.Symbol("C1")}
    # overlap with K (alpha = 1, zero shift: K^i_j = -(1/2) g^ik d_t g_kj)
    K = -g.inv()*sp.diff(g, t)/2
    c = sp.Symbol("c")
    integrand = sp.simplify(sum((c/Y**3*sp.diag(1, -sp.Rational(1, 2), -sp.Rational(1, 2)))[i, j]
                                * K[j, i] for i in range(3) for j in range(3))*sqrtg)
    target = sp.simplify(-c*sp.diff(X/Y, t))
    return {"solution_P": str(sol.rhs), "P_is_C_over_Y3": bool(sol_ok),
            "overlap_integrand_minus_target": str(sp.simplify(integrand - target)),
            "pass": bool(sol_ok and sp.simplify(integrand - target) == 0)}


def check_d(n=64, L=4.0, phx=-6.079e-3, phy=-5.471e-3):
    """Real-space TT projection of (20/3) d_i Phi d_j Phi / |K|^2 at K = (k, k, 0)."""
    k = 2*np.pi/L
    xs = np.arange(n)*L/n
    Xg, Yg = np.meshgrid(xs, xs, indexing="ij")
    Phi = phx*np.sin(k*Xg) + phy*np.sin(k*Yg)
    dP = [phx*k*np.cos(k*Xg), phy*k*np.cos(k*Yg), np.zeros_like(Xg)]
    ddP = np.zeros((3, 3) + Xg.shape)
    ddP[0, 0] = -phx*k*k*np.sin(k*Xg)
    ddP[1, 1] = -phy*k*k*np.sin(k*Yg)
    # source of 1604.06065 eq. (ij): TT[8 pi a^2 Pi - 2 dPhi dPhi - 4 Phi ddPhi] with the
    # growing-mode velocity: 8 pi a^2 rho v v = (4/3) dPhi dPhi
    S = np.array([[(4/3 - 2)*dP[i]*dP[j] - 4*Phi*ddP[i, j] for j in range(3)] for i in range(3)])
    # project onto cos(K.x) and sin(K.x) at K = (k, k, 0) (real-space overlap, no FFT)
    ph = k*(Xg + Yg)
    Sc = np.array([[2*np.mean(S[i, j]*np.cos(ph)) for j in range(3)] for i in range(3)])
    Ss = np.array([[2*np.mean(S[i, j]*np.sin(ph)) for j in range(3)] for i in range(3)])
    Kh = np.array([1, 1, 0])/np.sqrt(2)
    Pp = np.eye(3) - np.outer(Kh, Kh)

    def lam(M):
        return Pp @ M @ Pp - 0.5*Pp*np.trace(Pp @ M)
    K2 = 2*k*k
    hc, hs = 2*lam(Sc)/K2, 2*lam(Ss)/K2       # (1/2) K^2 h = TT[S]
    u = np.array([1, -1, 0])/np.sqrt(2)
    ez = np.array([0, 0, 1.0])
    ep = np.outer(u, u) - np.outer(ez, ez)
    hplus_cos = float(np.sum(hc*ep)/2)
    hplus_sin = float(np.sum(hs*ep)/2)
    pred_real = 5/6*phx*phy
    return {"phi_x": phx, "phi_y": phy, "hplus_cos_amplitude": hplus_cos,
            "hplus_sin_amplitude": hplus_sin, "predicted_real_amplitude_5_6": pred_real,
            "fourier_coefficient_equivalent": abs(hplus_cos)/2,
            "scope_value_5_12": 5/12*abs(phx*phy),
            "rel_dev": abs(abs(hplus_cos) - abs(pred_real))/abs(pred_real),
            "sign": "h_+ = -(5/6) phi_x phi_y cos(K.x) in the basis e+ = u u - z z, u = (1,-1,0)/sqrt2",
            "pass": bool(abs(abs(hplus_cos) - abs(pred_real)) < 1e-12*abs(pred_real) + 1e-20
                         and abs(hplus_sin) < 1e-15),
            "_x": xs, "_hline": None}


def check_e(lam=(0.11122237, 0.05, 0.02), t1=1.0, t2=None):
    """ZA ellipsoid: R_i = a R_L (1 - a lam_i), a = t^(2/3) (t_k = 1), G = c = 1,
    R_L = 3/2, M = 3/4. Q_ii = (M/15)(3 R_i^2 - sum R^2). Energy by adaptive quadrature
    of (1/5) sum Q'''^2 with Q''' from sympy's differentiation of Q(t) as defined here
    (a finite difference of Q was tried in a smoke test and is limited by rounding of the
    large non-radiating t^2 term: 1.7e-4 at h = 1e-3)."""
    from scipy.integrate import quad
    lam = np.array(lam)
    M, RL = 0.75, 1.5
    if t2 is None:
        t2 = lam.max()**-1.5          # first crossing of the ZA axis
    ts = sp.symbols("t", positive=True)
    a = ts**sp.Rational(2, 3)
    R = [a*sp.Rational(3, 2)*(1 - a*sp.Float(li, 30)) for li in lam]
    Qs = [sp.Rational(3, 4)/15*(3*R[i]**2 - sum(r**2 for r in R)) for i in range(3)]
    Q3 = sp.lambdify(ts, [sp.diff(q, ts, 3) for q in Qs], "numpy")

    def P_of(t):
        return 0.2*np.sum(np.array(Q3(t), dtype=float)**2, axis=0)
    E_quad = float(quad(P_of, t1, t2, epsabs=0, epsrel=1e-12, limit=200)[0])
    t = np.geomspace(t1, t2, 400)
    P = P_of(t)
    S = float((lam**4).sum() - (lam[0]**2*lam[1]**2 + lam[0]**2*lam[2]**2 + lam[1]**2*lam[2]**2))
    E_closed = 8/15*M*S*(t2**(1/3) - t1**(1/3))
    return {"lambda": lam.tolist(), "t1": t1, "t2": float(t2), "S": S, "E_quadrature": E_quad,
            "E_closed": E_closed, "rel_dev": abs(E_quad/E_closed - 1),
            "pass": bool(abs(E_quad/E_closed - 1) < 1e-6), "_t": t, "_P": P}


def check_f():
    tau, A = sp.symbols("tau A", positive=True)
    a = (1 + tau/2)**2
    res = {}
    for name, s in (("a", a), ("a^-3/2", a**sp.Rational(-3, 2))):
        res[name] = str(sp.simplify(sp.diff(a*sp.diff(s, tau), tau) - sp.Rational(3, 2)*s))
    t = sp.symbols("t", positive=True)
    Kmean = sp.pi**2*A**2*t
    # d_t alpha = -(1/3) alpha^2 K  and  -2 alpha K, alpha = 1 + O(A^2): first order in A^2
    conf = sp.integrate(-sp.Rational(1, 3)*Kmean, (t, 0, t))
    onelog = sp.integrate(-2*Kmean, (t, 0, t))
    # mean of K_ij K^ij for K_yy = -K_zz = -pi A cos(2 pi (x - t)): pi^2 A^2
    x = sp.symbols("x")
    kk = sp.integrate(2*(sp.pi*A*sp.cos(2*sp.pi*(x - t)))**2, (x, 0, 1))
    vals = {"conformal_t10_A1e-6": float(conf.subs({A: 1e-6, t: 10})),
            "onelog_t10_A1e-6": float(onelog.subs({A: 1e-6, t: 10}))}
    return {"sheet_modes_residual": res, "mean_KijKij": str(sp.simplify(kk)),
            "alpha_minus_1_conformal": str(conf), "alpha_minus_1_onelog": str(onelog),
            **vals,
            "pass": bool(all(v == "0" for v in res.values()) and sp.simplify(kk - sp.pi**2*A**2) == 0)}


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    R = {"a": check_a(), "b": check_b(), "c": check_c(), "d": check_d(), "e": check_e(),
         "f": check_f()}
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
    ax = axs[0]
    for key, col, lab in (("code", fs.PAL["red"], "as in the source"),
                          ("flipped", fs.PAL["blue"], r"$a_{xy}, a_{yz}$ flipped")):
        ax.semilogy(R["a"][key]["_cosz"], np.maximum(R["a"][key]["_ek"], 1e-17), "o", ms=2.5,
                    color=col, label=lab)
    ax.set_xlabel(r"$|\hat k_z|$ of a random direction")
    ax.set_ylabel(r"$|e\cdot\hat k|$")
    ax.set_ylim(1e-18, 3)
    ax.legend(loc="center right", fontsize=7)
    ax.set_title("(a) z4c_linear_wave polarization", fontsize=8)
    ax = axs[1]
    d = R["d"]
    k = 2*np.pi/4.0
    s = np.linspace(0, 4.0*np.sqrt(2), 200)
    ax.plot(s, d["hplus_cos_amplitude"]*np.cos(k*np.sqrt(2)*s)*1e5, color=fs.PAL["blue"],
            label="projection of the source")
    ax.plot(s[::10], -5/6*d["phi_x"]*d["phi_y"]*np.cos(k*np.sqrt(2)*s[::10])*1e5, "o", ms=3,
            color=fs.PAL["red"], label=r"$-(5/6)\phi_x\phi_y\cos\mathbf{K}\cdot\mathbf{x}$")
    ax.set_xlabel(r"distance along $(1,1,0)/\sqrt{2}$")
    ax.set_ylabel(r"$h_+\ [10^{-5}]$ at $\mathbf{K}=(k,k,0)$")
    ax.legend(loc="lower left", fontsize=7)
    ax.set_title(r"(d) crossed waves, $\delta=0.01$, $L=4$", fontsize=8)
    ax = axs[2]
    e = R["e"]
    ax.loglog(e["_t"], e["_P"], color=fs.PAL["blue"], label="quadrature integrand")
    tt = np.array(e["_t"])
    lam = np.array(e["lambda"])
    Sv = e["S"]
    ax.loglog(tt[::8], (8/45)*0.75*Sv*tt[::8]**(-2/3), "o", ms=3, color=fs.PAL["red"],
              label=r"$\frac{8}{45}MS\,t^{-2/3}$ (closed form)")
    ax.set_xlabel(r"$t/t_k$")
    ax.set_ylabel(r"$P_{\rm GW}/(c^5/G)$")
    ax.legend(loc="upper right", fontsize=7)
    ax.set_title(r"(e) ZA ellipsoid, $E$ to %.0e" % e["rel_dev"], fontsize=8)
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "lead_checks"))
    clean = {k: {kk: vv for kk, vv in v.items() if not kk.startswith("_")} for k, v in R.items()}
    for v in clean.values():
        for kk in ("code", "flipped"):
            if kk in v:
                v[kk] = {a: b for a, b in v[kk].items() if not a.startswith("_")}
    with open(os.path.join(out, "lead_checks.json"), "w") as f:
        json.dump(clean, f, indent=1, default=float)
    for k, v in clean.items():
        print(k, "PASS" if v["pass"] else "FAIL", {kk: vv for kk, vv in v.items()
                                                   if kk not in ("pass", "code", "flipped")})


if __name__ == "__main__":
    main()
