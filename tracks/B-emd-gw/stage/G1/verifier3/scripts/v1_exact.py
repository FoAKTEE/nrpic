#!/usr/bin/env python3
"""V1 of verifier3: exact linear solutions of tests F and X, checked symbolically and
numerically (JOURNAL entry 1, predictions P1.1-P1.7).

Run through nrpic-run; writes $NRPIC_RUN_DIR/v1.json, v1_T.png/pdf.
"""
import json
import os
import sys
import time

import numpy as np
import sympy as sp
from scipy.integrate import solve_ivp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import exact  # noqa: E402
import figstyle as fs  # noqa: E402

OUT = os.environ.get("NRPIC_RUN_DIR", os.path.join(HERE, "..", "results", "tmp_v1"))
os.makedirs(OUT, exist_ok=True)
res = {}
t0 = time.time()

# ------------------------------------------------------------------ P1.1 polarization
A, B = exact.generator_tensors(1.0, 1.0, 1.0)
ep, ex, n, u, v = exact.pol_tensors([1.0, 1.0, 1.0])
p11 = {
    "max|A - e+|": float(np.max(np.abs(A - ep))),
    "max|B - ex|": float(np.max(np.abs(B - ex))),
    "max|A.n|": float(np.max(np.abs(A @ n))), "max|B.n|": float(np.max(np.abs(B @ n))),
    "trA": float(np.trace(A)), "trB": float(np.trace(B)),
    "A:A": float(np.sum(A * A)), "B:B": float(np.sum(B * B)), "A:B": float(np.sum(A * B)),
}
# also random directions (transversality of the corrected generator for any k)
rng = np.random.default_rng(1)
worst = 0.0
worst_basis = 0.0
for _ in range(200):
    kk = rng.normal(size=3)
    Ag, Bg = exact.generator_tensors(*kk)
    epr, exr, nr, _, _ = exact.pol_tensors(kk)
    worst = max(worst, np.max(np.abs(Ag @ nr)), np.max(np.abs(Bg @ nr)),
                abs(np.trace(Ag)), abs(np.trace(Bg)))
    # generator basis vs mine: same up to a rotation about n?  record the difference
    worst_basis = max(worst_basis, np.max(np.abs(Ag - epr)), np.max(np.abs(Bg - exr)))
p11["random k: max transversality/trace defect"] = float(worst)
p11["random k: max |gen - mine|"] = float(worst_basis)
res["P1.1"] = p11

# ------------------------------------------------------------------ P1.2 linear ADM, flat
x, y, z, t = sp.symbols("x y z t", real=True)
eps, Ap, Ax, phx = sp.symbols("epsilon A_p A_x phi_x", real=True)
X = (x, y, z)
s3, s6, s2 = sp.sqrt(3), sp.sqrt(6), sp.sqrt(2)
nS = sp.Matrix([1, 1, 1]) / s3
uS = sp.Matrix([1, 1, -2]) / s6
vS = sp.Matrix([-1, 1, 0]) / s2
epS = uS * uS.T - vS * vS.T
exS = uS * vS.T + vS * uS.T
# check the symbolic basis is the numeric one
res["P1.1"]["sympy basis = numeric basis"] = float(
    max(np.max(np.abs(np.array(epS, float) - ep)), np.max(np.abs(np.array(exS, float) - ex))))
Kc = 2 * sp.pi * sp.Matrix([1, 1, 1])
w = sp.sqrt((Kc.T * Kc)[0])
P = (Kc.T * sp.Matrix(X))[0] - w * t
h = Ap * epS * sp.sin(P) + Ax * exS * sp.sin(P + phx)
Kdd = -sp.Rational(1, 2) * h.diff(t)
At_gen = sp.pi * sp.sqrt(3) * (Ap * epS * sp.cos(P) + Ax * exS * sp.cos(P + phx))


def ricci_lin(hm):
    """first-order Ricci of delta + h (standard formula)."""
    R = sp.zeros(3, 3)
    for i in range(3):
        for j in range(3):
            r = 0
            for k in range(3):
                r += (sp.diff(hm[k, j], X[i], X[k]) + sp.diff(hm[k, i], X[j], X[k])
                      - sp.diff(hm[i, j], X[k], X[k]))
            r -= sp.diff(sum(hm[k, k] for k in range(3)), X[i], X[j])
            R[i, j] = r / 2
    return R


Rl = ricci_lin(h)
res["P1.2"] = {
    "At(generator) - K_ij(linear)": str(sp.simplify(At_gen - Kdd)),
    "d_t K_ij - R_ij (linear ADM, alpha=1)": str(sp.simplify(Kdd.diff(t) - Rl)),
    "d_t^2 h - lap h": str(sp.simplify(h.diff(t, 2) - sum((h.diff(c, 2) for c in X), sp.zeros(3, 3)))),
}

# ------------------------------------------------------------------ 3+1 Weyl parts
def weyl_31(gam, Kd, order_eps):
    """E_ij = TF[R + K K - K.K], B_ij = sym(eps_i^kl D_k K_lj) for a metric linear in eps;
    returns the coefficient of eps^order_eps after expansion (inverse metric to O(eps))."""
    g0 = gam.subs(eps, 0)
    g1 = gam.diff(eps).subs(eps, 0)
    g0i = g0.inv()
    gi = g0i - eps * g0i * g1 * g0i
    Gam = [[[0] * 3 for _ in range(3)] for _ in range(3)]
    for k in range(3):
        for i in range(3):
            for j in range(3):
                Gam[k][i][j] = sum(gi[k, l] * (sp.diff(gam[l, j], X[i]) + sp.diff(gam[l, i], X[j])
                                               - sp.diff(gam[i, j], X[l])) for l in range(3)) / 2
    R = sp.zeros(3, 3)
    for i in range(3):
        for j in range(3):
            r = 0
            for k in range(3):
                r += sp.diff(Gam[k][i][j], X[k]) - sp.diff(Gam[k][i][k], X[j])
                for l in range(3):
                    r += Gam[k][k][l] * Gam[l][i][j] - Gam[k][j][l] * Gam[l][i][k]
            R[i, j] = r
    Kud = gi * Kd
    trK = sum(Kud[i, i] for i in range(3))
    M = R + trK * Kd - Kd * gi * Kd
    trM = sum((gi * M)[i, i] for i in range(3))
    E = M - gam * trM / 3
    # B
    detg = g0.det() * (1 + eps * (g0i * g1).trace())
    sq = sp.sqrt(g0.det()) * (1 + eps * (g0i * g1).trace() / 2)
    DK = [[[0] * 3 for _ in range(3)] for _ in range(3)]  # D_k K_lj
    for k in range(3):
        for l in range(3):
            for j in range(3):
                DK[k][l][j] = (sp.diff(Kd[l, j], X[k])
                               - sum(Gam[m][k][l] * Kd[m, j] + Gam[m][k][j] * Kd[l, m]
                                     for m in range(3)))
    Bm = sp.zeros(3, 3)
    for i in range(3):
        for j in range(3):
            b = 0
            for m in range(3):
                for k in range(3):
                    for l in range(3):
                        lc = sp.LeviCivita(m, k, l)
                        if lc != 0:
                            b += gam[i, m] * lc / sq * DK[k][l][j]
            Bm[i, j] = b
    Bs = (Bm + Bm.T) / 2
    out = []
    for Q in (E, Bs):
        Qe = Q.applyfunc(lambda q: sp.diff(q, eps, order_eps).subs(eps, 0) / sp.factorial(order_eps))
        out.append(Qe)
    return out[0], out[1], trK, M


gamF = sp.eye(3) + eps * h
KF = -sp.Rational(1, 2) * gamF.diff(t)
E1, B1, _, _ = weyl_31(gamF, KF, 1)
E0, B0, _, _ = weyl_31(gamF, KF, 0)
wv = 2 * sp.pi * sp.sqrt(3)
E_pred = (wv ** 2 / 2) * h
hd = h.diff(t)
B_pred = sp.zeros(3, 3)
for i in range(3):
    for j in range(3):
        bb = 0
        for k in range(3):
            for l in range(3):
                bb += sp.LeviCivita(i, k, l) * sp.diff(hd[l, j], X[k])
        B_pred[i, j] = -bb / 2
B_pred = (B_pred + B_pred.T) / 2
mb = (uS - sp.I * vS) / s2
mbr = (uS + sp.I * vS) / s2  # reversed direction: n -> -n, u -> u, v -> -v
psi4f = -sum((E_pred - sp.I * B_pred)[i, j] * mb[i] * mb[j] for i in range(3) for j in range(3))
psi4r = -sum((E_pred - sp.I * B_pred)[i, j] * mbr[i] * mbr[j] for i in range(3) for j in range(3))
hp = Ap * sp.sin(P)
hxs = Ax * sp.sin(P + phx)
res["P1.3"] = {
    "E^(0), B^(0) (background)": [str(sp.simplify(E0)), str(sp.simplify(B0))],
    "E^(1) - (w^2/2) h": str(sp.simplify(E1 - E_pred)),
    "B^(1) - B_pred": str(sp.simplify(B1 - B_pred)),
    "Psi4(+n) - (hdd_+ - i hdd_x)": str(sp.simplify(sp.expand_trig(psi4f - (hp.diff(t, 2) - sp.I * hxs.diff(t, 2))))),
    "Psi4(-n)": str(sp.simplify(sp.expand_trig(psi4r))),
}
print("F done", time.time() - t0, flush=True)

# ------------------------------------------------------------------ X: background, P1.6
a_f = sp.Function("a", positive=True)(t)
T_f = sp.Function("T")(t)
aE = (1 + t / 2) ** 2
rho0 = 3 / (8 * sp.pi)
res["P1.6"] = {
    "lapse: d_t a - (-(1/3) a^2 K), K = -3 a'/a^2": str(sp.simplify(sp.diff(aE, t) - (-(sp.Rational(1, 3)) * aE ** 2 * (-3 * sp.diff(aE, t) / aE ** 2)))),
    "Friedmann: (a'/a^2)^2 - (8 pi/3) rho0 a^-3": str(sp.simplify((sp.diff(aE, t) / aE ** 2) ** 2 - sp.Rational(8, 3) * sp.pi * rho0 / aE ** 3)),
}

# ------------------------------------------------------------------ X: ADM + Weyl, P1.7
kS = sp.pi / 2 * sp.Matrix([1, 1, 0])
kn = sp.pi / s2
uX = sp.Matrix([0, 0, -1])
vX = sp.Matrix([-1, 1, 0]) / s2
epX = uX * uX.T - vX * vX.T
exX = uX * vX.T + vX * uX.T
phX = (kS.T * sp.Matrix(X))[0]
ep_, ex_ = sp.symbols("e_p e_x", real=True)
hX = T_f * (ep_ * epX * sp.cos(phX) + ex_ * exX * sp.cos(phX + phx))
gamX = a_f ** 2 * (sp.eye(3) + eps * hX)
alp = a_f
KX = -gamX.diff(t) / (2 * alp)
E1X, B1X, trKX, MX = weyl_31(gamX, KX, 1)
hXd = hX.diff(t)
calH = sp.diff(a_f, t) / a_f
E_predX = (kn ** 2 / 2) * hX + (calH / 2) * hXd
B_predX = sp.zeros(3, 3)
for i in range(3):
    for j in range(3):
        bb = 0
        for k in range(3):
            for l in range(3):
                bb += sp.LeviCivita(i, k, l) * sp.diff(hXd[l, j], X[k])
        B_predX[i, j] = -bb / 2
B_predX = (B_predX + B_predX.T) / 2
# ADM evolution with dust at rest: d_t K_ij = alpha (R_ij - 2 K_ik K^k_j + K K_ij) - 4 pi alpha rho gamma_ij
g0i = gamX.subs(eps, 0).inv()
gi = g0i - eps * g0i * gamX.diff(eps).subs(eps, 0) * g0i
# R_ij from weyl_31's M: M = R + K K - K.K  -> R = M - K K + K.K
Rx = MX - trKX * KX + KX * gi * KX
rho = rho0 / a_f ** 3
evo = KX.diff(t) - alp * (Rx - 2 * KX * gi * KX + trKX * KX) + 4 * sp.pi * alp * rho * gamX
evo0 = evo.applyfunc(lambda q: q.subs(eps, 0))
evo1 = evo.applyfunc(lambda q: sp.diff(q, eps).subs(eps, 0))
subsE = {a_f: aE}
mode_eq = sp.diff(T_f, t, 2) + 2 * calH * sp.diff(T_f, t) + kn ** 2 * T_f
evo0s = sp.simplify(evo0.subs(a_f, aE).doit())
# order eps: substitute T'' from the mode equation and check the remainder vanishes
T2 = sp.solve(sp.Eq(mode_eq, 0), sp.diff(T_f, t, 2))[0]
evo1s = sp.simplify(evo1.subs(sp.Derivative(T_f, (t, 2)), T2).subs(a_f, aE).doit())
# E with the mode equation: -(1/2)(h'' + calH h')
E_alt = -(hX.diff(t, 2) + calH * hXd) / 2
res["P1.7"] = {
    "E^(1) - [(k^2/2) h + (a'/2a) h']": str(sp.simplify(E1X - E_predX)),
    "B^(1) - [-(1/2) sym eps d h']": str(sp.simplify((B1X - B_predX).subs(sp.sqrt(a_f ** 6), a_f ** 3))),
    "E_pred - (-(1/2)(h'' + calH h')) using the mode eq": str(sp.simplify((E_predX - E_alt).subs(sp.Derivative(T_f, (t, 2)), T2))),
    "ADM d_t K_ij residual, order eps^0 (Friedmann acceleration)": str(evo0s),
    "ADM d_t K_ij residual, order eps^1 with T'' from h''+2(a'/a)h'+k^2 h=0": str(evo1s),
}
print("X symbolic done", time.time() - t0, flush=True)

# ------------------------------------------------------------------ P1.5 closed form T
xw = exact.ExpandingWave()
md = xw.mode
tt = np.linspace(0.0, 10.0, 2001)
sol = solve_ivp(lambda s, yv: [yv[1], -(4.0 / (s + 2.0)) * yv[1] - md.kn ** 2 * yv[0]],
                (0.0, 10.0), [0.0, 1.0], t_eval=tt, rtol=1e-13, atol=1e-16, method="DOP853")
Tc = md.T(tt)
dTc = md.dT(tt)
err = np.max(np.abs(Tc - sol.y[0])) / np.max(np.abs(Tc))
errd = np.max(np.abs(dTc - sol.y[1])) / np.max(np.abs(dTc))
# residual of the ODE by central differences of the closed form
hh = 1e-3
ts = tt[1:-1]
Tpp = (md.T(ts + hh) - 2 * md.T(ts) + md.T(ts - hh)) / hh ** 2
Tp = (md.T(ts + hh) - md.T(ts - hh)) / (2 * hh)
resid = Tpp + (4.0 / (ts + 2.0)) * Tp + md.kn ** 2 * md.T(ts)
# sympy: j1(x)/x solves the mode equation
xs = sp.symbols("x", positive=True)
f1 = sp.jn(1, xs) / xs
f2 = sp.yn(1, xs) / xs
ode_x = lambda f: sp.simplify(sp.expand_func(sp.diff(f, xs, 2) + 4 / xs * sp.diff(f, xs) + f))
res["P1.5"] = {
    "kn": md.kn, "c1": md.c[0], "c2": md.c[1],
    "T(0)": float(md.T(0.0)), "T'(0)": float(md.dT(0.0)),
    "max rel |T_closed - T_ode|": float(err), "max rel |T'_closed - T'_ode|": float(errd),
    "max |FD residual| / (k^2 max|T|)": float(np.max(np.abs(resid)) / (md.kn ** 2 * np.max(np.abs(Tc)))),
    "sympy residual j1(x)/x": str(ode_x(f1)), "sympy residual y1(x)/x": str(ode_x(f2)),
    "T(10)": float(md.T(10.0)), "T'(10)": float(md.dT(10.0)),
    "zeros of T in (0,10]": [float(v) for v in tt[2:][np.diff(np.sign(Tc[1:])) != 0]],
}
res["wall_s"] = time.time() - t0
with open(os.path.join(OUT, "v1.json"), "w") as f:
    json.dump(res, f, indent=1, default=str)
print(json.dumps(res, indent=1, default=str))

# ------------------------------------------------------------------ figure
fs.use_style()
import matplotlib.pyplot as plt  # noqa: E402

fig, axs = plt.subplots(2, 1, figsize=(fs.COLUMN_WIDTH * 1.4, 4.6), sharex=True)
fig.subplots_adjust(left=0.16, right=0.97, bottom=0.11, top=0.97, hspace=0.06)
ax = axs[0]
ax.plot(tt, sol.y[0], color=fs.PAL["blue"], label="ODE (DOP853)")
ax.plot(tt, Tc, **fs.GUIDE, label=r"$c_1 j_1(x)/x + c_2 y_1(x)/x$")
ax.axhline(0.0, color="grey", lw=0.8)
ax.set_ylabel(r"$T(t)$")
ax.legend(loc="upper right")
ax2 = axs[1]
ax2.semilogy(tt, np.abs(Tc - sol.y[0]) + 1e-20, color=fs.PAL["red"], label=r"$|T_{\rm closed}-T_{\rm ODE}|$")
ax2.semilogy(ts, np.abs(resid) + 1e-20, color=fs.PAL["yellow"], label="FD residual of the ODE")
ax2.set_xlabel(r"conformal time $t$")
ax2.set_ylabel("difference")
ax2.legend(loc="lower right")
fs.save(fig, os.path.join(OUT, "v1_T"))
print("done", time.time() - t0)
