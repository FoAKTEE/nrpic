"""Exact and semi-analytic first-passage references for the slow-roll (overdamped) Langevin
equation dx = D(x) dN + S(x) dW (Ito), absorbing wall at x_end, reflecting wall at x_uv.

1. Drift-diffusion with constant coefficients (1308.4754 v2, main .tex lines 285-365, 437-443):
   X = mu N + W, first passage at X = m; <N> = m/mu, var = m/mu^3, third central moment
   3 m/mu^5; Laplace transform <exp(-J N)> = exp(m mu - m sqrt(2J + mu^2)) (line 347).
   The density is the inverse Gaussian m / sqrt(2 pi N^3) exp(-(m - mu N)^2 / (2N))
   [BACKGROUND: the inverse Laplace transform of line 347; checked numerically in V1].
2. Moments of N from the adjoint Fokker-Planck recursion L f_n = -n f_{n-1},
   L = D d/dx + (S^2/2) d^2/dx^2, f_n(x_end) = 0, f_n'(x_uv) = 0 [BACKGROUND; n = 1 is
   2206.11234 v2 method.tex line 118 with B = 0].
3. Survival probability and first-passage density by the spectral solution of the backward
   Kolmogorov equation d_N Surv = L Surv on a grid (method of lines, exact in N).
4. Closed-form characteristic function for quadratic inflation, 2206.11234 v2 appendix.tex
   lines 60-102, evaluated at t = iJ (Laplace transform), with mpmath.
"""
import numpy as np
from scipy.linalg import eigh_tridiagonal

# ---------------------------------------------------------------- 1. drift-diffusion

def ig_pdf(N, m, mu):
    N = np.asarray(N, dtype=float)
    out = np.zeros_like(N)
    ok = N > 0
    out[ok] = m / np.sqrt(2 * np.pi * N[ok] ** 3) * np.exp(-(m - mu * N[ok]) ** 2 / (2 * N[ok]))
    return out


def ig_logsf(N, m, mu):
    """log of P(first-passage time > N) for X = mu N + W hitting m (inverse Gaussian)."""
    from scipy.special import log_ndtr
    N = np.asarray(N, dtype=float)
    a = (mu * N - m) / np.sqrt(N)
    b = -(mu * N + m) / np.sqrt(N)
    # sf = Phi(-a) - exp(2 m mu) Phi(b)
    la = log_ndtr(-a)
    lb = 2 * m * mu + log_ndtr(b)
    return la + np.log1p(-np.exp(np.minimum(lb - la, 0.0)))


def ig_moments(m, mu):
    return dict(mean=m / mu, var=m / mu ** 3, mu3=3 * m / mu ** 5,
                skew=3 * m / mu ** 5 / (m / mu ** 3) ** 1.5)


def ig_laplace(J, m, mu):
    return np.exp(m * mu - m * np.sqrt(2 * J + mu ** 2))


# ---------------------------------------------------------------- grid helpers

class Domain:
    """Uniform grid from x_end (index 0, absorbing) to x_uv (index M, reflecting).

    Works in the coordinate y = s (x - x_end) >= 0 with s = sign(x_uv - x_end), so the
    absorbing wall is always at y = 0.
    """

    def __init__(self, D, S, x_end, x_uv, M):
        self.s = 1.0 if x_uv > x_end else -1.0
        self.x_end, self.x_uv, self.M = float(x_end), float(x_uv), int(M)
        self.Y = abs(x_uv - x_end)
        self.y = np.linspace(0.0, self.Y, self.M + 1)
        self.h = self.y[1] - self.y[0]
        self.x = self.x_end + self.s * self.y
        # drift in y and diffusion
        self.Dy = lambda y: self.s * D(self.x_end + self.s * y)
        self.S2 = lambda y: S(self.x_end + self.s * y) ** 2

    def lnpsi(self, y):
        """ln psi(y) = int_0^y 2 D_y / S^2, by Gauss-Legendre on each cell (exact enough)."""
        g, w = np.polynomial.legendre.leggauss(8)
        y = np.asarray(y, dtype=float)
        edges = np.concatenate([[0.0], y]) if y[0] > 0 else y
        a, b = edges[:-1, None], edges[1:, None]
        t = 0.5 * (b - a) * g[None, :] + 0.5 * (b + a)
        cells = 0.5 * (b[:, 0] - a[:, 0]) * np.sum(w[None, :] * 2 * self.Dy(t) / self.S2(t), axis=1)
        c = np.concatenate([[0.0], np.cumsum(cells)])
        return c[1:] if y[0] > 0 else c


# ---------------------------------------------------------------- 2. moments

def fpt_moments(D, S, x_end, x_uv, x0, nmax=4, M=40000):
    """<N^n>(x0), n = 1..nmax, from the recursion (psi f_n')' = -2 n psi f_{n-1} / S^2.

    Returns raw moments and central ones (var, mu3, mu4) plus skewness and excess kurtosis.
    Second-order accurate in the grid spacing; call with two M to check convergence.
    """
    d = Domain(D, S, x_end, x_uv, M)
    y = d.y
    lp = d.lnpsi(y)                       # ln psi at nodes
    invS2 = 1.0 / d.S2(y)
    f_prev = np.ones_like(y)
    raw = []
    for n in range(1, nmax + 1):
        g = 2 * n * f_prev * invS2         # integrand without psi
        # I(y_i) = int_{y_i}^{Y} g(z) exp(lp(z) - lp(y_i)) dz, backward recursion, trapezoid
        I = np.zeros_like(y)
        for i in range(len(y) - 2, -1, -1):
            e = np.exp(lp[i + 1] - lp[i])
            I[i] = e * I[i + 1] + 0.5 * d.h * (g[i] + g[i + 1] * e)
        fp = I                              # f_n'(y) in the y coordinate
        f = np.concatenate([[0.0], np.cumsum(0.5 * d.h * (fp[1:] + fp[:-1]))])
        raw.append(np.interp(abs(x0 - x_end), y, f))
        f_prev = f
    m1 = raw[0]
    out = dict(raw=raw, mean=m1)
    if nmax >= 2:
        out["var"] = raw[1] - m1 ** 2
    if nmax >= 3:
        out["mu3"] = raw[2] - 3 * m1 * raw[1] + 2 * m1 ** 3
        out["skew"] = out["mu3"] / out["var"] ** 1.5
    if nmax >= 4:
        out["mu4"] = raw[3] - 4 * m1 * raw[2] + 6 * m1 ** 2 * raw[1] - 3 * m1 ** 4
        out["exkurt"] = out["mu4"] / out["var"] ** 2 - 3
    return out


# ---------------------------------------------------------------- 3. spectral survival

class SpectralFPT:
    """Semi-discrete backward Kolmogorov operator L = (1/w)(p f')', p = psi, w = 2 psi / S^2,
    Dirichlet at y = 0, Neumann at y = Y. Finite volumes, symmetrised, all eigenpairs.

    Surv(N) = sum_n c_n exp(-lam_n N), P(N) = sum_n c_n lam_n exp(-lam_n N) at the node of x0.
    """

    def __init__(self, D, S, x_end, x_uv, x0, M=4000):
        d = Domain(D, S, x_end, x_uv, M)
        self.dom = d
        y, h = d.y, d.h
        ymid = 0.5 * (y[1:] + y[:-1])
        lp_nodes = d.lnpsi(y)
        lp_mid = d.lnpsi(ymid)
        ref = lp_nodes.max()
        lp_nodes, lp_mid = lp_nodes - ref, lp_mid - ref
        # unknowns: nodes 1..M (node 0 is the absorbing wall)
        lw = np.log(2.0) + lp_nodes - np.log(d.S2(y))           # ln w at nodes
        vol = np.full(M + 1, h)
        vol[M] = 0.5 * h
        lW = lw + np.log(vol)                                    # ln (w * cell volume)
        # stiffness: K_ii = (p_{i-1/2} + p_{i+1/2})/h, K_{i,i+1} = -p_{i+1/2}/h
        p_mid = lp_mid                                           # ln p at midpoints (index i -> i+1/2)
        idx = np.arange(1, M + 1)
        diag = np.exp(p_mid[idx - 1] - lW[idx]) / h
        diag[:-1] += np.exp(p_mid[idx[:-1]] - lW[idx[:-1]]) / h
        off = -np.exp(p_mid[idx[:-1]] - 0.5 * (lW[idx[:-1]] + lW[idx[:-1] + 1])) / h
        lam, G = eigh_tridiagonal(diag, off)
        self.lam = lam
        # coefficients at x0 (linear interpolation between the two nearest nodes)
        y0 = abs(x0 - x_end)
        j = int(np.clip(np.floor(y0 / h), 0, M - 1))
        t = y0 / h - j
        sqW = np.exp(0.5 * lW[idx])
        proj = G.T @ sqW                                         # <g_n, W^{1/2} 1>
        def f_at(node):
            if node == 0:
                return np.zeros_like(lam)
            return G[node - 1, :] / sqW[node - 1]
        fx0 = (1 - t) * f_at(j) + t * f_at(j + 1)
        self.c = fx0 * proj

    def surv(self, N):
        N = np.atleast_1d(N)
        return np.exp(-np.outer(N, self.lam)) @ self.c

    def pdf(self, N):
        N = np.atleast_1d(N)
        return np.exp(-np.outer(N, self.lam)) @ (self.c * self.lam)

    def laplace(self, J):
        """<exp(-J N)> = sum_n c_n lam_n / (lam_n + J)."""
        J = np.atleast_1d(J)
        return np.array([np.sum(self.c * self.lam / (self.lam + j)) for j in J])

    def moments(self):
        """<N> = sum c/lam, <N^2> = 2 sum c/lam^2, ..."""
        r = [np.sum(self.c / self.lam), 2 * np.sum(self.c / self.lam ** 2),
             6 * np.sum(self.c / self.lam ** 3), 24 * np.sum(self.c / self.lam ** 4)]
        m = r[0]
        var = r[1] - m ** 2
        mu3 = r[2] - 3 * m * r[1] + 2 * m ** 3
        mu4 = r[3] - 4 * m * r[2] + 6 * m ** 2 * r[1] - 3 * m ** 4
        return dict(raw=r, mean=m, var=var, mu3=mu3, skew=mu3 / var ** 1.5,
                    exkurt=mu4 / var ** 2 - 3)


class SurvivalPDE:
    """Backward Kolmogorov equation d_N Surv = L Surv, L = (1/w)(p f')', in the
    unsymmetrised conservative form (Surv is O(1) everywhere, so no loss of relative
    accuracy when psi varies by many decades). Time stepping: one backward-Euler step, then
    BDF2 (L-stable, second order). P(N) = -d_N Surv at x0 (central differences).

    The eigenvalues of SpectralFPT (symmetric, well conditioned) give the tail rates; the
    eigenvectors of SpectralFPT are not used where the weight spans many decades.
    """

    def __init__(self, D, S, x_end, x_uv, x0, M=4000):
        from scipy.sparse import diags
        d = Domain(D, S, x_end, x_uv, M)
        self.dom = d
        y, h = d.y, d.h
        ymid = 0.5 * (y[1:] + y[:-1])
        lp_nodes = d.lnpsi(y)
        lp_mid = d.lnpsi(ymid)
        lw = np.log(2.0) + lp_nodes - np.log(d.S2(y))
        vol = np.full(M + 1, h)
        vol[M] = 0.5 * h
        lW = lw + np.log(vol)
        idx = np.arange(1, M + 1)
        lo = np.exp(lp_mid[idx - 1] - lW[idx]) / h            # coefficient of f_{i-1}
        up = np.zeros(M)
        up[:-1] = np.exp(lp_mid[idx[:-1]] - lW[idx[:-1]]) / h  # coefficient of f_{i+1}
        dg = -(lo + up)
        # matrix on unknowns 1..M (f_0 = 0); lo[0] multiplies f_0 = 0 and drops out
        self.A = diags([lo[1:], dg, up[:-1]], [-1, 0, 1], format="csc")
        self.M = M
        y0 = abs(x0 - x_end)
        j = int(np.clip(np.floor(y0 / h), 0, M - 1))
        self.j, self.t = j, y0 / h - j

    def run(self, N_max, dN):
        from scipy.sparse import identity
        from scipy.sparse.linalg import splu
        I = identity(self.M, format="csc")
        be = splu((I - dN * self.A).tocsc())
        bdf = splu((3 * I - 2 * dN * self.A).tocsc())
        f_prev = np.ones(self.M)
        # one backward-Euler step split into 8 sub-steps (damps the initial discontinuity)
        sub = splu((I - (dN / 8) * self.A).tocsc())
        f = f_prev.copy()
        for _ in range(8):
            f = sub.solve(f)
        nsteps = int(round(N_max / dN))
        surv = np.empty(nsteps + 1)

        def at(v):
            vv = np.concatenate([[0.0], v])
            return (1 - self.t) * vv[self.j] + self.t * vv[self.j + 1]
        surv[0] = at(f_prev)
        surv[1] = at(f)
        for n in range(2, nsteps + 1):
            f_new = bdf.solve(4 * f - f_prev)
            f_prev, f = f, f_new
            surv[n] = at(f)
        N = dN * np.arange(nsteps + 1)
        pdf = -np.gradient(surv, dN)
        self.N, self.surv, self.pdf_v = N, surv, pdf
        return N, surv, pdf

    def laplace(self, J, lam_tail=None):
        """<exp(-J N)> = 1 - J int_0^inf Surv e^{-JN} dN, with an exponential tail beyond N_max."""
        out = []
        for j in np.atleast_1d(J):
            g = self.surv * np.exp(-j * self.N)
            I = np.trapz(g, self.N)
            if lam_tail is not None:
                I += g[-1] / (lam_tail + j)
            out.append(1 - j * I)
        return np.array(out)


# ---------------------------------------------------------------- 4. quadratic closed form

def quadratic_laplace_closed_form(J, phi, m, phi_end, phi_uv, dps=40):
    """<exp(-J N)>(phi) for V = m^2 phi^2 / 2 (M_Pl = 1) from 2206.11234 appendix.tex
    eqs. at lines 63-102: v = v0 phi^2, v0 = m^2 / (48 pi^2) (reduced potential of line 34),
    alpha = sqrt(1 - 4 i t / v0) with t = i J, i.e. alpha = sqrt(1 + 4 J / v0),
    chi = [B f/f_end - A g/g_end] / (B - A), A = f'_UV / g'_UV, B = f_end / g_end.
    """
    import mpmath as mp
    mp.mp.dps = dps
    v0 = mp.mpf(m) ** 2 / (48 * mp.pi ** 2)
    out = []
    for Jv in np.atleast_1d(J):
        al = mp.sqrt(1 + 4 * mp.mpf(Jv) / v0)
        def f(ph):
            v = v0 * ph ** 2
            return v ** ((1 + al) / 4) * mp.hyp1f1((-1 - al) / 4, 1 - al / 2, -1 / v)
        def g(ph):
            v = v0 * ph ** 2
            return v ** ((1 - al) / 4) * mp.hyp1f1((-1 + al) / 4, 1 + al / 2, -1 / v)
        pe, pu, p0 = mp.mpf(phi_end), mp.mpf(phi_uv), mp.mpf(phi)
        A = mp.diff(f, pu) / mp.diff(g, pu)
        B = f(pe) / g(pe)
        chi = (B * f(p0) / f(pe) - A * g(p0) / g(pe)) / (B - A)
        out.append(complex(chi))
    out = np.array(out)
    return out.real if np.all(np.abs(out.imag) <= 1e-12 * np.maximum(1.0, np.abs(out.real))) else out
