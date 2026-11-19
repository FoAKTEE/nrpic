"""Nonlinear isobaric heat conduction in one dimension: the reference for the short-
mean-free-path end of T6 (temperature step, contrast 2) and for the amplitude bias of the
isobaric mode of T7 and T8 (eps = 0.05 and 0.2). Units c = k_B = m = 1, theta = T/m.

Model [JUDGEMENT, own derivation; the linear limit is collide/SPEC.md section 7.3]: a gas
at rest to leading order in the Mach number, with uniform pressure p(t); per particle the
first law with Eckart's heat flux q = -kappa dT/dx (the acceleration term T a vanishes at
leading order) reads, along the flow (Lagrangian time derivative, mass coordinate m with
dm = n dx),

    c_p(T) dT/dt = (T/p) dp/dt - dq/dm,      q = -(n kappa) dT/dm,      n = p/T,

with c_p = c_v + 1 of the Maxwell-Juttner gas (collide/REFERENCES/mj.py). The volume of
the periodic box fixes p: L = int T dm / p, so L dp/dt = int dT/dt dm; this keeps the total
energy int <W>(T) dm constant (checked in `selftest`). Non-relativistically c_p = 5/2 and
p stays constant. Conductivity: kappa = f kappa_1(T), kappa_1 = (75 sqrt(pi)/64)
sqrt(T)/sigma (first Chapman-Enskog approximation, hard spheres; collide/REFERENCES/
conduction.py `kappa_ce_nr`), f a free factor (f = 1: kappa_1; the higher Sonine
approximations would give f ~ 1.025 [BACKGROUND]).

Discretisation: finite volumes in m (uniform), periodic; time integration with scipy's
BDF (stiff), banded Jacobian pattern (the rank-one coupling through dp/dt is left to the
Newton iteration). Eulerian positions follow from x(m) = x(0) + int_0^m T/p dm with x(0)
fixed by the symmetry of the set-ups (the centre of the hot slab, the crest of the mode).
"""
import os
import sys

import numpy as np
from scipy import integrate, optimize, sparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "collide", "REFERENCES"))
import mj               # noqa: E402
import conduction as cd  # noqa: E402

KAPPA1_COEF = 75.0 * np.sqrt(np.pi) / 64.0      # = 1.5 * 25 sqrt(pi)/32 = 2.077


class _Tab:
    """Tabulated Maxwell-Juttner c_p, c_v, <W> on a log grid (fast evaluation)."""

    def __init__(self, tmin, tmax, n=400):
        self.lt = np.linspace(np.log(tmin), np.log(tmax), n)
        th = np.exp(self.lt)
        self.cp = np.array([float(mj.c_p(t)) for t in th])
        self.cv = np.array([float(mj.c_v(t)) for t in th])
        self.W = np.array([float(mj.mean_W(t)) for t in th])

    def __call__(self, name, T):
        return np.interp(np.log(T), self.lt, getattr(self, name))


class Isobaric:
    """Solver on a periodic mass grid: Tm0 the initial temperature of the nm cells (cell
    centres at m_i = (i + 1/2) dm from the symmetry point), M the mass per unit area of the
    box, L its length, sigma the cross-section per unit mass, f the conductivity factor."""

    def __init__(self, Tm0, M, L, sigma, f=1.0):
        self.T0 = np.asarray(Tm0, float)
        self.nm = len(self.T0)
        self.M, self.L, self.sigma, self.f = M, L, sigma, f
        self.dm = M / self.nm
        self.tab = _Tab(0.2 * self.T0.min(), 5 * self.T0.max())
        self.p0 = self.dm * self.T0.sum() / L

    def _rhs(self, t, y):
        T, p = y[:-1], y[-1]
        nk = p * self.f * KAPPA1_COEF / (self.sigma * np.sqrt(T))     # n kappa = (p/T) kappa
        nkf = 0.5 * (nk + np.roll(nk, -1))                            # faces i+1/2
        G = nkf * (np.roll(T, -1) - T) / self.dm                      # n kappa dT/dm at faces
        D = (G - np.roll(G, 1)) / self.dm                             # -dq/dm
        cp = self.tab("cp", T)
        pdot = np.sum(self.dm * D / cp) / (self.L - np.sum(self.dm * T / (p * cp)))
        Tdot = ((T / p) * pdot + D) / cp
        return np.concatenate([Tdot, [pdot]])

    def solve(self, times, rtol=1e-10, atol=1e-14):
        """BDF with rtol 1e-10: at rtol 1e-8 the linear decay rate came out 5e-4 high
        (test of 2026-11-19 against the closed form); at 1e-11 it is within the
        grid error (2 pi/nm)^2/12."""
        n = self.nm
        rows = np.arange(n)
        pat = sparse.lil_matrix((n + 1, n + 1))
        for off in (-1, 0, 1):
            pat[rows, (rows + off) % n] = 1
        pat[:, n] = 1
        pat[n, :] = 1
        y0 = np.concatenate([self.T0, [self.p0]])
        sol = integrate.solve_ivp(self._rhs, (0.0, float(times[-1])), y0, method="BDF",
                                  t_eval=np.asarray(times, float), rtol=rtol,
                                  atol=atol * float(self.T0.mean()), jac_sparsity=pat.tocsc())
        if not sol.success:
            raise RuntimeError(sol.message)
        self.t = sol.t
        self.T = sol.y[:-1].T          # (nt, nm)
        self.p = sol.y[-1]
        return self

    def x_centres(self):
        """Eulerian cell-centre positions relative to the symmetry point m = 0."""
        v = self.dm * self.T / self.p[:, None]       # cell volumes per unit area
        return np.cumsum(v, axis=1) - 0.5 * v

    def energy(self):
        return np.sum(self.dm * self.tab("W", self.T), axis=1)


# ----------------------------------------------------------------- the step of T6
def step_reference(L, n_mean, theta1, theta2, sigma, times, f=1.0, nm=1200):
    """Slab sums of the left slab [0, L/2) (hot slab centred at L/4) per unit area: rest
    mass, energy (rest mass included), kinetic energy, at `times`; and the solver.
    Equal pressure at t = 0: n_i theta_i = p0, (n1 + n2)/2 = n_mean."""
    p0 = 2.0 * n_mean / (1.0 / theta1 + 1.0 / theta2)
    n1, n2 = p0 / theta1, p0 / theta2
    M = n_mean * L
    # mass grid symmetric about the hot centre: cells [0, M/2) by symmetry (half box)
    # solved on the full periodic box, m from -M/2 to M/2 with the hot slab |m| < n1 L/4
    m = (np.arange(nm) + 0.5) * (M / nm) - 0.5 * M
    T0 = np.where(np.abs(m) < n1 * L / 4.0, theta1, theta2)
    s = Isobaric(T0, M, L, sigma, f).solve(times)
    out = []
    W = s.tab("W", s.T)
    for it in range(len(s.t)):
        v = s.dm * s.T[it] / s.p[it]
        # cumulative volume from m = -M/2; the hot centre m = 0 sits at index nm/2
        edges = np.concatenate([[0.0], np.cumsum(v)])
        xc0 = edges[nm // 2]                    # x of m = 0 (face between the halves)
        xr = edges - xc0                        # positions relative to the hot centre
        # slab |x| < L/4: mass between the faces where xr = -L/4 and +L/4
        mf = (np.arange(nm + 1)) * s.dm
        lo = np.interp(-L / 4.0, xr, mf)
        hi = np.interp(L / 4.0, xr, mf)
        cm = np.concatenate([[0.0], np.cumsum(s.dm * W[it])])
        ck = np.concatenate([[0.0], np.cumsum(s.dm * (W[it] - 1.0))])
        out.append([hi - lo, np.interp(hi, mf, cm) - np.interp(lo, mf, cm),
                    np.interp(hi, mf, ck) - np.interp(lo, mf, ck)])
    return np.array(out), s


# ----------------------------------------------------------------- the mode of T7/T8
def mode_reference(k, n0, theta0, eps, sigma, times, f=1.0, nm=512):
    """Mode amplitudes of the isobaric start n = n0 (1 - eps cos kx), T = theta0
    (1 + eps cos kx) in a box of one wavelength: number mode A_N = 2 int n cos / int n,
    kinetic-energy mode A_K = 2 int n e_kin cos / int n e_kin, and the entropy
    combination A_S = (A_K - A_N) (<W> - 1)/theta0 - A_N; returns dict of arrays."""
    L = 2.0 * np.pi / k
    M = n0 * L
    # m(x) = n0 (x - (eps/k) sin kx): invert on the uniform mass grid
    mc = (np.arange(nm) + 0.5) * (M / nm)
    xg = np.linspace(0.0, L, 20001)
    mg = n0 * (xg - (eps / k) * np.sin(k * xg))
    xc = np.interp(mc, mg, xg)
    T0 = theta0 * (1.0 + eps * np.cos(k * xc))
    s = Isobaric(T0, M, L, sigma, f).solve(times)
    v = s.dm * s.T / s.p[:, None]
    x = np.cumsum(v, axis=1) - 0.5 * v              # m = 0 at x = 0 (crest, fixed)
    c = np.cos(k * x)
    ek = s.tab("W", s.T) - 1.0
    AN = 2.0 * np.sum(c, axis=1) / nm
    AK = 2.0 * np.sum(ek * c, axis=1) / np.sum(ek, axis=1)
    g = (float(mj.mean_W(theta0)) - 1.0) / theta0
    AS = (AK - AN) * g - AN
    return dict(t=s.t, AN=AN, AK=AK, AS=AS, p=s.p, E=s.energy(), solver=s)


def fit_exp(t, A, t0, t1):
    """Least-squares fit A = A0 exp(-G t) over t0 <= t <= t1 (uniform weights)."""
    w = (t >= t0) & (t <= t1)
    tt, aa = t[w], A[w]
    G0 = -np.polyfit(tt, np.log(np.abs(aa)), 1)[0]
    p, cov = optimize.curve_fit(lambda x, a, g: a * np.exp(-g * x), tt, aa,
                                p0=(aa[0] * np.exp(G0 * tt[0]), G0))
    return float(p[1]), float(p[0]), int(w.sum())


def chi_kappa1(theta, n, sigma, f=1.0):
    """Thermal diffusivity kappa/(n c_p) with kappa = f kappa_1(theta)."""
    return f * cd.kappa_ce_nr(theta, sigma) / (n * float(mj.c_p(theta)))


def fit_step_linear(t, X, L, X0, Xinf, t0, t1, chi_guess):
    """The literal T6(b) statistic: fit conduction.step_diffusive with chi free to X(t)
    over [t0, t1] (X0, Xinf fixed: the initial and the fully mixed value)."""
    w = (t >= t0) & (t <= t1)
    fun = lambda tt, ch: cd.step_diffusive(tt, L, X0, Xinf, ch)
    p, cov = optimize.curve_fit(fun, t[w], X[w], p0=(chi_guess,))
    return float(p[0]), float(np.sqrt(cov[0, 0])), int(w.sum())


def selftest():
    """Energy conservation, the linear limit of the mode (Gamma = kappa_1 k^2/(n c_p)),
    and grid convergence of the step; returns dict of numbers."""
    out = {}
    th0, k, sig = 0.003, 0.1, 1.0
    G1 = cd.mode_rate(cd.kappa_ce_nr(th0, sig), 1.0, th0, k)
    t = np.linspace(0, 2.0 / G1, 201)
    r = mode_reference(k, 1.0, th0, 1e-4, sig, t)
    G, _, _ = fit_exp(r["t"], r["AS"], 0.0, 2.0 / G1)
    out["mode_linear_G_over_G1"] = G / G1
    out["mode_energy_drift"] = float(np.ptp(r["E"]) / r["E"][0])
    r2 = mode_reference(k, 1.0, th0, 1e-4, sig, t, nm=1024)
    G2, _, _ = fit_exp(r2["t"], r2["AS"], 0.0, 2.0 / G1)
    out["mode_linear_grid_change"] = G2 / G - 1.0
    tt = np.linspace(0, 50.0, 101)
    a, s = step_reference(1.0, 1.0, 0.02, 0.01, 100.0, tt, nm=600)
    b, s2 = step_reference(1.0, 1.0, 0.02, 0.01, 100.0, tt, nm=1200)
    out["step_energy_drift"] = float(np.ptp(s2.energy()) / s2.energy()[0])
    out["step_grid_change_mass"] = float(np.max(np.abs(a[:, 0] - b[:, 0])) /
                                         abs(b[0, 0] - b[-1, 0]))
    out["step_pressure_change"] = float(np.ptp(s2.p) / s2.p[0])
    return out


if __name__ == "__main__":
    import json
    print(json.dumps(selftest(), indent=1))
