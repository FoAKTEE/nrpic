"""Classical background and linear flat-gauge modes, used for the noise of the phase-space
Langevin equation and for linear-theory reference variances (M_Pl = 1, time N).

Background: phi' = varpi / H, varpi' = -3 varpi - V'/H, 3 H^2 = varpi^2 / 2 + V, ln a = N - N*.
Slow-roll parameters with the sign convention of 2512.14649 v2 PRD_v2.tex line 171:
eps1 = -d ln H / dN = varpi^2 / (2 H^2), eps2 = -d ln eps1 / dN.

Linear modes (Q = flat-gauge delta phi, P = delta varpi), 2405.10692 v2 draft_JCAP.tex
lines 325-328:
    Q' = P/H + varpi^2/(2 H^2) Q,
    P' = -3 P - k^2/(a^2 H) Q - (V'' + V' varpi/H + 3 varpi^2/2) Q / H - varpi^2/(2 H^2) P.
Bunch-Davies start: u = e^{-i k tau}(1 - i/(k tau)) / sqrt(2k), Q = u/a, tau = -1/((1-eps1) a H)
[BACKGROUND]. Comoving curvature |R| = H |Q| / |varpi|. Dimensionless spectra
P_XY = k^3/(2 pi^2) X Y*; noise covariance per e-fold = Re P_XY(k_sigma) d ln k_sigma / dN
with k_sigma = sigma a H (2512.14649 line 503) [BACKGROUND, 2405.10692 lines 335-347].
"""
import numpy as np
from scipy.integrate import solve_ivp


class ClassicalBackground:
    def __init__(self, model, phi0, dphidN0, N0=0.0, Nstar=None, N_extra=80.0, rtol=1e-12):
        self.model = model
        V = model.V
        H0 = np.sqrt(V(phi0) / (3.0 - 0.5 * dphidN0 ** 2))
        w0 = H0 * dphidN0
        self.N0, self.phi0, self.w0, self.H0 = N0, phi0, w0, H0

        def rhs(N, y):
            phi, w = y
            H = np.sqrt((0.5 * w * w + V(phi)) / 3.0)
            return [w / H, -3.0 * w - model.dV(phi) / H]

        def end(N, y):
            phi, w = y
            H2 = (0.5 * w * w + V(phi)) / 3.0
            return 0.5 * w * w / H2 - 1.0
        end.terminal = True
        end.direction = 1
        sol = solve_ivp(rhs, (N0, N0 + N_extra), [phi0, w0], method="DOP853", rtol=rtol,
                        atol=1e-30, dense_output=True, events=end)
        self.sol = sol
        self.N_end = sol.t_events[0][0] if len(sol.t_events[0]) else np.nan
        self.phi_end = sol.y_events[0][0][0] if len(sol.t_events[0]) else np.nan
        self.Nstar = N0 if Nstar is None else Nstar

    def state(self, N):
        y = self.sol.sol(N)
        return y[0], y[1]

    def H(self, N):
        phi, w = self.state(N)
        return np.sqrt((0.5 * w * w + self.model.V(phi)) / 3.0)

    def eps1(self, N):
        phi, w = self.state(N)
        H = self.H(N)
        return 0.5 * w * w / H ** 2

    def eps2(self, N, h=1e-5):
        return -(np.log(self.eps1(N + h)) - np.log(self.eps1(N - h))) / (2 * h)

    def a(self, N):
        return np.exp(N - self.Nstar)

    def aH(self, N):
        return self.a(N) * self.H(N)

    def N_of_aH(self, target, lo=None, hi=None):
        """N at which a H = target (a H is monotonic during inflation)."""
        from scipy.optimize import brentq
        lo = self.N0 if lo is None else lo
        hi = self.N_end if hi is None else hi
        return brentq(lambda N: np.log(self.aH(N)) - np.log(target), lo, hi, xtol=1e-13)


def mode(bg, k, N_out, K_init=200.0, rtol=1e-10):
    """Integrate one flat-gauge mode from N_i (k = K_init a H, or bg.N0 if later) to the
    times N_out (sorted). Returns complex Q(N_out), P(N_out)."""
    model = bg.model
    N_out = np.atleast_1d(N_out)
    try:
        Ni = bg.N_of_aH(k / K_init)
    except ValueError:
        Ni = bg.N0
    Ni = max(Ni, bg.N0)
    a, H = bg.a(Ni), bg.H(Ni)
    e1 = bg.eps1(Ni)
    phi, w = bg.state(Ni)
    tau = -1.0 / ((1.0 - e1) * a * H)
    u = np.exp(-1j * k * tau) * (1 - 1j / (k * tau)) / np.sqrt(2 * k)
    dudtau = np.exp(-1j * k * tau) * (-1j * k * (1 - 1j / (k * tau)) + 1j / (k * tau ** 2)) / np.sqrt(2 * k)
    Q = u / a
    dQdN = dudtau / (a * a * H) - Q
    P = H * (dQdN - w * w / (2 * H * H) * Q)

    def rhs(N, y):
        Q = y[0] + 1j * y[1]
        P = y[2] + 1j * y[3]
        phi, w = bg.state(N)
        H = np.sqrt((0.5 * w * w + model.V(phi)) / 3.0)
        a = bg.a(N)
        dQ = P / H + w * w / (2 * H * H) * Q
        dP = (-3 * P - k * k / (a * a * H) * Q
              - (model.d2V(phi) + model.dV(phi) * w / H + 1.5 * w * w) * Q / H
              - w * w / (2 * H * H) * P)
        return [dQ.real, dQ.imag, dP.real, dP.imag]

    # the solution is evaluated at N_out >= Ni only
    sol = solve_ivp(rhs, (Ni, max(N_out.max(), Ni + 1e-9)), [Q.real, Q.imag, P.real, P.imag],
                    method="DOP853", rtol=rtol, atol=1e-40, t_eval=np.clip(N_out, Ni, None))
    return sol.y[0] + 1j * sol.y[1], sol.y[2] + 1j * sol.y[3]


def spectra_at(bg, k, N):
    Q, P = mode(bg, k, [N])
    Q, P = Q[0], P[0]
    c = k ** 3 / (2 * np.pi ** 2)
    phi, w = bg.state(N)
    H = bg.H(N)
    return dict(Pff=c * abs(Q) ** 2, Pfp=c * (Q * np.conj(P)).real, Ppp=c * abs(P) ** 2,
                PR=c * abs(Q) ** 2 * H ** 2 / w ** 2)


def PR_late(bg, ks, N_late):
    """Power spectrum of R at N_late for each k."""
    out = []
    for k in ks:
        Q, P = mode(bg, k, [N_late])
        phi, w = bg.state(N_late)
        out.append(k ** 3 / (2 * np.pi ** 2) * abs(Q[0]) ** 2 * bg.H(N_late) ** 2 / w ** 2)
    return np.array(out)


class NoiseTable:
    """Noise covariance per unit N for the coarse-graining scale k_sigma = sigma a H.

    Tabulated at N_grid; between nodes the 2x2 covariance is interpolated linearly and
    factorised (symmetric square root of the clipped eigen decomposition).
    kind = 'modes' (flat-gauge mode functions) or 'desitter' ((H/2pi)^2 in phi only).
    """

    def __init__(self, bg, sigma, N_grid, kind="modes", K_init=200.0):
        self.N = np.asarray(N_grid, dtype=float)
        C = np.zeros((len(self.N), 2, 2))
        for i, N in enumerate(self.N):
            e1 = bg.eps1(N)
            dlnk = 1.0 - e1
            if kind == "desitter":
                C[i, 0, 0] = (bg.H(N) / (2 * np.pi)) ** 2 * dlnk
            else:
                k = sigma * bg.aH(N)
                Q, P = mode(bg, k, [N], K_init=K_init)
                c = k ** 3 / (2 * np.pi ** 2) * dlnk
                C[i, 0, 0] = c * abs(Q[0]) ** 2
                C[i, 0, 1] = C[i, 1, 0] = c * (Q[0] * np.conj(P[0])).real
                C[i, 1, 1] = c * abs(P[0]) ** 2
        self.C = C

    def cov(self, N):
        i = int(np.clip(np.searchsorted(self.N, N) - 1, 0, len(self.N) - 2))
        t = (N - self.N[i]) / (self.N[i + 1] - self.N[i])
        t = min(max(t, 0.0), 1.0)
        return (1 - t) * self.C[i] + t * self.C[i + 1]

    def __call__(self, N):
        C = self.cov(N)
        lam, U = np.linalg.eigh(C)
        lam = np.clip(lam, 0.0, None)
        return U @ np.diag(np.sqrt(lam)) @ U.T


def lattice_shell_counts(nmax):
    """Integer vectors n != 0 with |n| <= nmax: returns sorted unique |n| and multiplicity."""
    r = np.arange(-nmax, nmax + 1)
    X, Y, Z = np.meshgrid(r, r, r, indexing="ij")
    n2 = (X * X + Y * Y + Z * Z).ravel()
    n2 = n2[(n2 > 0) & (n2 <= nmax * nmax)]
    u, c = np.unique(n2, return_counts=True)
    return np.sqrt(u), c
