"""Truncated Maxwell-Boltzmann (F21) / relativistic King cluster, written from scratch.

Not derived from tmb.py, king_sequence.py or evstatic.py of the track. The steady state is
f = A [exp(-E/T_inf) - exp(-E_c/T_inf)] for E <= E_c (E the Killing energy per unit mass).
At radius r the local cut-off Lorentz factor is W_c(r) = E_c e^{-Phi(r)} and the local
temperature T(r) = T_inf e^{-Phi} = b W_c(r) with b = T_inf/E_c, so

    f = A' [exp((W_c - W)/(b W_c)) - 1],  1 <= W <= W_c,

one function of W_c per radius. With A' = 1 and the momentum per unit mass q
(d^3q = 4 pi q W dW), G = c = 1 and lengths in F21's zeta, these are F21's hatted units
(rho^ = 4 sqrt2 pi I_rho of main.tex:122-139 follows by the substitution W - 1 = b x/(1-bw)).
Moments by Gauss-Legendre in s = (W - 1)^{1/2}. F21's w0 = eps_c(0)/kT(0) maps to
W_c(0) = 1/(1 - b w0); the King ansatz of 2009.08163 (paper.tex:635) is b = 1 with
y0 = ln W_c(0).

TOV in areal r: dM/dr = 4 pi r^2 rho, d ln W_c/dr = -(M + 4 pi r^3 p)/(r (r - 2M)),
surface where W_c = 1. e^{Phi} = E_c/W_c with E_c = (1 - 2M/R)^{1/2}.
"""
import numpy as np
from scipy.integrate import solve_ivp

XG, WG = np.polynomial.legendre.leggauss(96)
XG, WG = 0.5 * (XG + 1.0), 0.5 * WG          # on [0, 1]
FOURPI = 4.0 * np.pi


def moments(Wc, b):
    """n, rho, p, u (thermal), <v> numerator at local cut-off Wc (scalar)."""
    if Wc <= 1.0:
        return 0.0, 0.0, 0.0, 0.0, 0.0
    sc = np.sqrt(Wc - 1.0)
    s = sc * XG
    w = sc * WG * 2.0 * s                     # dW = 2 s ds
    W = 1.0 + s * s
    q = s * np.sqrt(2.0 + s * s)
    g = np.expm1((Wc - W) / (b * Wc))
    n = FOURPI * np.sum(g * q * W * w)
    rho = FOURPI * np.sum(g * q * W * W * w)
    p = FOURPI / 3.0 * np.sum(g * q ** 3 * w)
    u = FOURPI * np.sum(g * q * W * s * s * w)   # rho - n without cancellation
    vnum = FOURPI * np.sum(g * q * q * w)        # int (q/W) f d^3q
    return n, rho, p, u, vnum


def _rhs(r, y, b):
    M, lnW = y[0], y[1]
    Wc = np.exp(lnW)
    n, rho, p, u, _ = moments(Wc, b)
    g = 1.0 - 2.0 * M / r
    eL = g ** -0.5
    e2L = 1.0 / g
    gam = 1.0 + p / u if u > 1e-300 else 5.0 / 3.0
    w3 = Wc ** -3.0                            # e^{3 Phi} / E_c^3
    r2 = r * r
    return [FOURPI * r2 * rho,
            -(M + FOURPI * r ** 3 * p) / (r2 * g),
            FOURPI * r2 * n * eL,                                   # E_rest
            w3 * eL * p * r2,                                       # I0
            w3 * eL * gam * p * r2,                                 # I_gamma
            w3 * eL * (16 * p + (e2L - 1) * (rho + p)) * (e2L - 1) * r2,
            w3 * eL ** 3 * (8 * p + (e2L + 1) * (rho + p)) * p * r2 * r2,
            w3 * eL ** 5 * (rho + p) * p * p * r2 ** 3]


def solve(b, w0=None, y0=None, dense=False, rtol=1e-11):
    if y0 is not None:
        Wc0 = np.exp(y0)
        w0 = (1.0 - 1.0 / Wc0) / b
    else:
        Wc0 = 1.0 / (1.0 - b * w0)
    n0, rho0, p0, u0, vn0 = moments(Wc0, b)
    r0 = 1e-6
    lnW = np.log(Wc0) - 2 * np.pi * (rho0 / 3 + p0) * r0 ** 2
    y_init = [FOURPI / 3 * rho0 * r0 ** 3, lnW, FOURPI / 3 * n0 * r0 ** 3, 0, 0, 0, 0, 0]

    def surf(r, y, b):
        return y[1]
    surf.terminal, surf.direction = True, -1
    sol = solve_ivp(_rhs, [r0, 1e4], y_init, args=(b,), events=surf, method="DOP853",
                    rtol=rtol, atol=1e-16, dense_output=dense)
    R = sol.t_events[0][0]
    ye = sol.y_events[0][0]
    M, Er, I0, Ig, I1, I2, I3 = ye[0], ye[2], ye[3], ye[4], ye[5], ye[6], ye[7]
    Ec = np.sqrt(1 - 2 * M / R)
    out = dict(b=b, w0=w0, y0=np.log(Wc0), Wc0=Wc0, M=M, R=R, Erest=Er, B=Er - M,
               eps=(Er - M) / Er, C=M / R, Z0=Wc0 / Ec - 1.0, epsc0=Wc0 - 1.0,
               rho_c=rho0, p_c=p0, n_c=n0, u_c=u0, v0=np.sqrt(3 * p0 / rho0),
               gamma_avg=Ig / I0,
               gamma_cr=4 / 3 + I1 / (36 * I0) + 4 * np.pi / 9 * I2 / I0
               + 16 * np.pi ** 2 / 9 * I3 / I0,
               vmean_c=vn0 / n0)
    # ADM units (M = 1)
    out["rho0c_M2"] = n0 * M * M
    out["Hc_scope"] = np.sqrt(p0 / (FOURPI * rho0 ** 2)) / M      # SCOPE.md 4: rho = energy
    out["Hc_conv"] = np.sqrt(p0 / (FOURPI * n0 ** 2)) / M         # CONVERSION.md: rho0
    out["R_over_M"] = R / M
    out["M0_over_M"] = Er / M
    out["v1_energy"] = np.sqrt(p0 / rho0)
    out["v1_rest"] = np.sqrt(p0 / n0)
    if dense:
        out["sol"] = sol
    return out


def profile(model, r):
    """rho, p, n, u, gamma, e^{Phi}, e^{Lambda}, dp/dr at areal radii r (hatted units)."""
    sol, b = model["sol"], model["b"]
    Ec = np.sqrt(1 - 2 * model["M"] / model["R"])
    Y = sol.sol(r)
    M, lnW = Y[0], Y[1]
    res = np.array([moments(np.exp(l), b)[:4] for l in lnW])
    n, rho, p, u = res.T
    gam = np.where(u > 1e-300, 1 + p / np.maximum(u, 1e-300), 5 / 3)
    eL = (1 - 2 * M / r) ** -0.5
    ePhi = Ec / np.exp(lnW)
    dPhi = (M + FOURPI * r ** 3 * p) / (r * r * (1 - 2 * M / r))
    dp = -(rho + p) * dPhi
    return dict(r=r, M=M, rho=rho, p=p, n=n, u=u, gamma=gam, ePhi=ePhi, eL=eL, dp=dp,
                dPhi=dPhi)


def vmol_avg(Wc, b, nq=64, nmu=96):
    """Average Moller speed over pairs of the local isotropic distribution (3D quadrature)."""
    sc = np.sqrt(Wc - 1.0)
    x, wx = np.polynomial.legendre.leggauss(nq)
    x, wx = 0.5 * (x + 1), 0.5 * wx
    s = sc * x
    w = sc * wx * 2 * s
    W = 1 + s * s
    q = s * np.sqrt(2 + s * s)
    f = np.expm1((Wc - W) / (b * Wc))
    wt = f * q * W * w                    # weight of d^3q per particle (times 4 pi)
    mu, wmu = np.polynomial.legendre.leggauss(nmu)
    W1, W2, MU = np.meshgrid(W, W, mu, indexing="ij")
    Q1, Q2, _ = np.meshgrid(q, q, mu, indexing="ij")
    gr = W1 * W2 - Q1 * Q2 * MU
    v = np.sqrt(np.maximum(gr * gr - 1, 0)) / (W1 * W2)
    vmu = 0.5 * np.einsum("ijk,k->ij", v, wmu)
    return float(wt @ vmu @ wt / wt.sum() ** 2)
