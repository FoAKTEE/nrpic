"""Vectorised Langevin first-passage solvers for stochastic delta-N (M_Pl = 1, time N).

Overdamped (slow-roll) Langevin, Ito, 2206.11234 v2 intro.tex lines 26-33 and method.tex
lines 100-107:   dphi = D dN + S dW,  D = -V'/V,  S = H/(2 pi),  H^2 = V/3.

Phase-space Langevin (2405.10692 v2 draft_JCAP.tex lines 320-332, 2512.14649 v2 lines
103-111, 1308.4754 v2 lines 644-649), with varpi = dphi/dt:
    dphi   = varpi / H dN + xi_phi,
    dvarpi = (-3 varpi - V'(phi) / H) dN + xi_pi,     3 H^2 = varpi^2 / 2 + V,
and Gaussian white noise of covariance C(N) dN supplied by the caller.

Euler-Maruyama for the overdamped case (as 2206.11234 eq. at method.tex line 23);
deterministic RK4 plus an additive Ito noise increment per step for the phase-space case
(as 2405.10692 line 388). First passage: linear interpolation inside the crossing step;
optionally the Brownian-bridge test for crossings between two steps [BACKGROUND].
Importance sampling: drift bias B, path weight w = p_target / p_sample (2206.11234
method.tex lines 49-80; the sign of the exponent is derived in JOURNAL entry 3).
"""
import numpy as np


def fpt_overdamped(D, S, x0, x_end, dN, n, rng, x_uv=None, bridge=True, bias=None,
                   N_max=np.inf, return_paths=0):
    """First-passage times of dx = D dN + S dW from x0 to x_end.

    D, S: callables (vectorised). x_uv: reflecting wall or None. bias: callable B(x) added
    to the drift of the sampled process (importance sampling) or None.
    Returns dict(N=fpt (nan if N_max reached), logw=log weights, steps=number of steps).
    """
    s = 1.0 if x0 > x_end else -1.0
    x = np.full(n, float(x0))
    fpt = np.full(n, np.nan)
    logw = np.zeros(n)
    alive = np.arange(n)
    N = 0.0
    sq = np.sqrt(dN)
    step = 0
    paths = []
    while alive.size and N < N_max:
        xa = x[alive]
        d = D(xa)
        sg = S(xa)
        xi = rng.standard_normal(alive.size)
        b = bias(xa) if bias is not None else 0.0
        xn = xa + (d + b) * dN + sg * sq * xi
        if x_uv is not None:
            # reflecting wall; exact image likelihood ratio for the importance weight
            over = s * (xn - x_uv) > 0
            xn = np.where(over, 2 * x_uv - xn, xn)
        if bias is not None:
            if x_uv is None:
                logw[alive] += -(b / sg ** 2) * (0.5 * b * dN + sg * sq * xi)
            else:
                y1 = xn                       # landing point inside the domain
                y2 = 2 * x_uv - xn            # its image beyond the wall
                var = sg ** 2 * dN
                def lg(y, mu):
                    return -(y - xa - mu * dN) ** 2 / (2 * var)
                lt = np.logaddexp(lg(y1, d), lg(y2, d))
                ls = np.logaddexp(lg(y1, d + b), lg(y2, d + b))
                logw[alive] += lt - ls
        d0 = s * (xa - x_end)
        d1 = s * (xn - x_end)
        hit = d1 <= 0
        tc = N + dN * d0 / np.where(hit, d0 - d1, 1.0)
        if bridge:
            nb = ~hit
            pb = np.zeros(alive.size)
            pb[nb] = np.exp(-2 * d0[nb] * d1[nb] / (sg[nb] ** 2 * dN))
            bh = nb & (rng.random(alive.size) < pb)
            tc = np.where(bh, N + dN * d0 / (d0 + d1), tc)
            hit = hit | bh
        fpt[alive[hit]] = tc[hit]
        x[alive] = xn
        if return_paths and step % return_paths == 0:
            paths.append((N, x[: min(n, 50)].copy()))
        alive = alive[~hit]
        N += dN
        step += 1
    out = dict(N=fpt, logw=logw, steps=step)
    if return_paths:
        out["paths"] = paths
    return out


class Background:
    """Classical background in phase space (phi, varpi = dphi/dt), time N, M_Pl = 1."""

    def __init__(self, model):
        self.model = model

    def H(self, phi, w):
        return np.sqrt((0.5 * w ** 2 + self.model.V(phi)) / 3.0)

    def rhs(self, phi, w):
        H = self.H(phi, w)
        return w / H, -3.0 * w - self.model.dV(phi) / H

    def rk4(self, phi, w, h):
        k1p, k1w = self.rhs(phi, w)
        k2p, k2w = self.rhs(phi + 0.5 * h * k1p, w + 0.5 * h * k1w)
        k3p, k3w = self.rhs(phi + 0.5 * h * k2p, w + 0.5 * h * k2w)
        k4p, k4w = self.rhs(phi + h * k3p, w + h * k3w)
        return (phi + h / 6 * (k1p + 2 * k2p + 2 * k3p + k4p),
                w + h / 6 * (k1w + 2 * k2w + 2 * k3w + k4w))


def fpt_phase_space(model, phi0, w0, N0, phi_end, dN, n, rng, noise=None, window=(0.0, 0.0),
                    dN_det=None, N_max=200.0, bias=None, noise_scale=1.0, var_factor=None):
    """First passage of phi through phi_end for the phase-space Langevin system.

    noise(N) -> 2x2 matrix L with covariance per unit N equal to L L^T (rows: phi, varpi).
    The noise acts for N in [window[0], window[1]); outside, the step is deterministic
    with step dN_det (default dN). bias(N) -> c: importance-sampling shift of the first
    standard-normal pair per step along the dominant noise direction (against the roll),
    z -> z + c sqrt(dN) e; log weight -c sqrt(dN) e.z - c^2 dN / 2 (exact for a shifted
    standard normal). noise_scale multiplies the noise amplitude; var_factor(N) multiplies
    the covariance (used for the lattice density of states). Crossings inside deterministic
    steps are located by cubic Hermite interpolation, inside noisy steps linearly.
    phi_end may be an array of surfaces (reached in order; one crossing per step at most).
    Returns dict(N=first-passage e-folds since N0, shape (n,) or (n, n_surfaces), nan if
    N_max is reached; logw; state_after_window; ends).
    """
    bg = Background(model)
    ends = np.atleast_1d(np.asarray(phi_end, dtype=float))
    s = 1.0 if phi0 < ends[0] else -1.0      # +1: phi increases towards phi_end
    ends = ends[np.argsort(s * ends)]          # in the order they are reached
    nsurf = len(ends)
    phi = np.full(n, float(phi0))
    w = np.full(n, float(w0))
    fpt = np.full((n, nsurf), np.nan)
    target = np.zeros(n, dtype=int)            # index of the next surface per realisation
    logw = np.zeros(n)
    alive = np.arange(n)
    N = float(N0)
    dN_det = dN if dN_det is None else dN_det
    sq = np.sqrt(dN)
    state_after = None
    while alive.size and N - N0 < N_max:
        in_win = window[0] <= N < window[1]
        h = dN if in_win else dN_det
        if not in_win and N < window[0] and N + h > window[0]:
            h = window[0] - N
            if h <= 1e-14:
                h = dN
        pa, wa = phi[alive], w[alive]
        pn, wn = bg.rk4(pa, wa, h)
        noisy = in_win and noise is not None
        if noisy:
            L = noise(N) * noise_scale
            if var_factor is not None:
                L = L * np.sqrt(var_factor(N))
            z1 = rng.standard_normal(alive.size)
            z2 = rng.standard_normal(alive.size)
            if bias is not None:
                # shift of the standard-normal pair along the dominant noise direction,
                # oriented against the roll (towards longer first-passage times)
                lam, U = np.linalg.eigh(L @ L.T)
                u = U[:, -1] * (-np.sign(U[0, -1]) * s if U[0, -1] != 0 else 1.0)
                # the pair z maps to noise L z; choose z-direction e with L e parallel to u
                e = np.linalg.lstsq(L, u, rcond=None)[0]
                e = e / np.linalg.norm(e)
                c = bias(N) * sq
                logw[alive] += -c * (e[0] * z1 + e[1] * z2) - 0.5 * c * c
                z1 = z1 + c * e[0]
                z2 = z2 + c * e[1]
            pn = pn + sq * (L[0, 0] * z1 + L[0, 1] * z2)
            wn = wn + sq * (L[1, 0] * z1 + L[1, 1] * z2)
        pe = ends[target[alive]]
        d0 = s * (pe - pa)
        d1 = s * (pe - pn)
        hit = d1 <= 0
        th = d0 / np.where(hit, d0 - d1, 1.0)
        if not noisy and np.any(hit):
            # cubic Hermite crossing inside a deterministic step (Newton from the linear guess)
            i = np.where(hit)[0]
            f0 = wa[i] / bg.H(pa[i], wa[i]) * h
            f1 = wn[i] / bg.H(pn[i], wn[i]) * h
            p0, p1, t = pa[i], pn[i], th[i]
            for _ in range(6):
                t2, t3 = t * t, t * t * t
                val = ((2 * t3 - 3 * t2 + 1) * p0 + (t3 - 2 * t2 + t) * f0
                       + (-2 * t3 + 3 * t2) * p1 + (t3 - t2) * f1 - pe[i])
                der = ((6 * t2 - 6 * t) * p0 + (3 * t2 - 4 * t + 1) * f0
                       + (-6 * t2 + 6 * t) * p1 + (3 * t2 - 2 * t) * f1)
                t = np.clip(t - val / der, 0.0, 1.0)
            th[i] = t
        tc = N + h * th
        ah = alive[hit]
        fpt[ah, target[ah]] = tc[hit] - N0
        target[ah] += 1
        phi[alive], w[alive] = pn, wn
        alive = alive[target[alive] < nsurf]
        N += h
        if state_after is None and N >= window[1]:
            state_after = (phi.copy(), w.copy())
    return dict(N=fpt[:, 0] if nsurf == 1 else fpt, logw=logw, state_after_window=state_after,
                ends=ends)
