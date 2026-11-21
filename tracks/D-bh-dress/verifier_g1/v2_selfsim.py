"""Verifier's own self-similar solution of collisionless secondary infall onto a point
seed in an Einstein-de Sitter background (Bertschinger type), written from the equations
in JOURNAL entry 2, without the track's selfsimilar.py.

A shell that turns around at t* with radius r* = r_ta(t*) moves as r = r* Lambda(tau),
tau = t/t*. With r_ta ~ t^(8/9), M_ta ~ t^(2/3) and the mean density inside r_ta equal
to (9 pi^2/16) rho_b at turnaround:

    Lambda'' = -(pi^2/8) tau^(2/3) m(lambda) / Lambda^2,  lambda = Lambda tau^(-8/9),
    Lambda(1) = 1, Lambda'(1) = 0,

    m(lambda) = int_0^1 H(lambda - lambda_shell(x)) dx,  x = tau^(-2/3)   (mass in units M_ta),
    rho/rho_b = (9 pi^2/16) dm/d(lambda^3).

The radial orbit passes through the centre (signed X = Lambda), the centre softened by s
in Lambda. Fixed-point iteration on m, damped. Pure Python scalar leapfrog with an adaptive
step (eta times the smaller of the dynamical time and R/|V|). The measure of each step is
dx = (2/3) tau^(-5/3) dtau, so m is an exact quadrature along the recorded orbit; shells
with tau > tau_max are put at the centre.
"""
import math

import numpy as np

C = math.pi ** 2 / 8.0


def orbit(mgrid, u0, du, tau_max, eta, soft, x_rest):
    """one orbit Lambda(tau) in the profile m (on a log-lambda grid u0 + k du)."""
    n = len(mgrid)
    mg = list(mgrid)
    X, V, tau = 1.0, 0.0, 1.0
    s2 = soft * soft

    def acc(X, tau):
        R2 = X * X + s2
        lam = abs(X) * tau ** (-8.0 / 9.0)
        if lam <= 0.0:
            m = mg[0]
        else:
            q = (math.log(lam) - u0) / du
            if q <= 0:
                m = mg[0]
            elif q >= n - 1:
                m = mg[-1]
            else:
                k = int(q)
                f = q - k
                m = mg[k] * (1 - f) + mg[k + 1] * f
        return -C * tau ** (2.0 / 3.0) * m * X / (R2 * math.sqrt(R2)), m

    a, m = acc(X, tau)
    T, L, W = [], [], []
    while tau < tau_max:
        R = math.sqrt(X * X + s2)
        tdyn = math.sqrt(R ** 3 / (C * tau ** (2.0 / 3.0) * max(m, 1e-12)))
        h = eta * min(tdyn, R / (abs(V) + 1e-30))
        h = min(h, tau_max - tau) if tau_max - tau > 1e-12 else h
        V += 0.5 * h * a
        Xm = X + 0.5 * h * V
        X += h * V
        tm = tau + 0.5 * h
        tau += h
        a, m = acc(X, tau)
        V += 0.5 * h * a
        T.append(tm)
        L.append(abs(Xm))
        W.append((2.0 / 3.0) * tm ** (-5.0 / 3.0) * h)
    return np.array(T), np.array(L), np.array(W)


def solve(tau_max=60.0, eta=0.01, soft=1e-4, n_iter=40, tol=2e-4, damp=0.5, ngrid=3000,
          lam_min=1e-6, verbose=False):
    u = np.linspace(math.log(lam_min), 0.0, ngrid)
    du = u[1] - u[0]
    lam_g = np.exp(u)
    m_g = np.minimum(lam_g ** 0.75, 1.0)
    x_rest = tau_max ** (-2.0 / 3.0)
    hist = []
    for it in range(n_iter):
        T, L, W = orbit(m_g, u[0], du, tau_max, eta, soft, x_rest)
        lam = L * T ** (-8.0 / 9.0)
        o = np.argsort(lam)
        cum = x_rest + np.cumsum(W[o])
        m_new = np.interp(lam_g, lam[o], cum, left=x_rest, right=cum[-1])
        diff = float(np.max(np.abs(m_new - m_g)))
        hist.append(diff)
        if verbose:
            print("iter", it, "steps", len(T), "max change", diff, "m(1)", cum[-1], flush=True)
        m_g = (1 - damp) * m_g + damp * m_new
        if diff < tol and it >= 6:
            break
    # final orbit in the converged profile, for the caustic
    T, L, W = orbit(m_g, u[0], du, tau_max, eta, soft, x_rest)
    lam = L * T ** (-8.0 / 9.0)
    # first passage: first minimum of L; the outermost caustic is the largest lambda after it
    i0 = int(np.argmax(np.diff(np.sign(np.diff(L))) > 0)) + 1
    lam1 = float(lam[i0:].max())
    tau1 = float(T[i0:][np.argmax(lam[i0:])])
    return dict(lam=lam_g, m=m_g, hist=hist, T=T, L=L, lam_orbit=lam, lam_caustic1=lam1,
                tau_caustic1=tau1, tau_first_passage=float(T[i0]))


def binned_rho(lam_g, m_g, edges):
    mm = np.interp(edges, lam_g, m_g)
    return (9 * math.pi ** 2 / 16) * np.diff(mm) / np.diff(np.asarray(edges) ** 3)


if __name__ == "__main__":
    import sys
    import time
    t0 = time.time()
    r = solve(tau_max=float(sys.argv[1]) if len(sys.argv) > 1 else 60.0,
              eta=float(sys.argv[2]) if len(sys.argv) > 2 else 0.01, verbose=True)
    print("time", time.time() - t0)
    print("caustic", r["lam_caustic1"], "at tau", r["tau_caustic1"], "first passage", r["tau_first_passage"])
    for l in (1e-3, 1e-2, 0.05, 0.1, 0.2, 0.3, 0.364, 0.5, 1.0):
        print(l, float(np.interp(l, r["lam"], r["m"])))
    e = np.logspace(-1, math.log10(0.3), 9)
    print("rho/rho_b on [0.1,0.3]", np.round(binned_rho(r["lam"], r["m"], e), 3))
