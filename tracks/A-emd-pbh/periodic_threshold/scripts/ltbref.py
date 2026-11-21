"""Exact spherical dust (Lemaitre-Tolman-Bondi) references for the periodic peak, and the
background of the relaxed 1+log lapse; shared by ltb_reference.py and compare_ltb.py.

Every shell of spherical dust keeps its Misner-Sharp mass M and its energy E until shell
crossing; along its world line (proper time tau)
    (dR/dtau)^2 = 2M/R + 2E,                                                       (1)
so a shell is fixed by (M, E) and its phase on the initial slice. Bound shells (E < 0):
    R = A (1 - cos eta),  t - t_b = T0 (eta - sin eta),  A = M/(-2E),  T0 = M/(-2E)^(3/2),
turnaround at eta = pi, marginally trapped (R = 2M, invariant in spherical symmetry) at
cos eta = 1 + 4E on the collapsing branch, crunch at eta = 2 pi. Unbound shells (E > 0):
    R = A (cosh eta - 1),  t - t_b = T0 (sinh eta - eta),  A = M/(2E),  T0 = M/(2E)^(3/2).
These are the forms of MDPBH.tex:573, 586, 593-619, 743 (arXiv:2609.14218 v1) with
2E = -ktilde r^2 and M = m r^3/6; ltb2609.Profile2609 codes the paper's profile.

Two references are built from (1):
  A  the paper's profile ln Psi = (mu/2) exp(-k^2 r^2/6) with simultaneous bang time
     (t_b = 0) and a_i = 1 at t_i = 2/(3 H_i) (MDPBH.tex:673-704), H_i = 1, k = eps_i;
  B  the code's own initial slice: M and E of each shell from the fields and particles
     that the run starts from (make_field data on the root mesh, conformally flat,
     gamma_ij = psi^4 delta_ij, K_ij = psi^-2 Ahat_ij + (1/3) psi^4 delta_ij K; field file
     NRCOSMO1 of cosmo/ic/nrp_io.py):
        R = psi^2 r,  dR/dr = psi^2 + 2 r psi d_r psi,  K_T = K^theta_theta
          = psi^-6 Ahat_T + K/3,  Ahat_T = -(1/2) n^i n^j Ahat_ij (traceless),
        M = (R/2) (1 + R^2 K_T^2 - (dR/dr)^2/psi^4)          (n.grad R = -R K_T, code sign)
        U = dR/dtau = -W R K_T + psi^-4 u_r dR/dr,   W = sqrt(1 + psi^-4 u_i u_i),
        E = U^2/2 - M/R,
     evaluated at the initial position of each tracked particle by Fourier interpolation
     (the data are periodic and were solved spectrally). Its tau is the proper time of the
     particle from the initial slice, which is what the code integrates (IPTAU).
"""
import math
import struct

import numpy as np

TWO_PI = 2.0 * math.pi


# ---------------------------------------------------------------------------- cycloids
def _q_ell(eta):
    """eta - sin eta, accurate for small eta."""
    eta = np.asarray(eta, dtype=float)
    out = eta - np.sin(eta)
    sm = np.abs(eta) < 0.3
    x = eta[sm]
    x2 = x * x
    out[sm] = x * x2 / 6.0 * (1 - x2 / 20.0 * (1 - x2 / 42.0 * (1 - x2 / 72.0)))
    return out


def _q_hyp(eta):
    eta = np.asarray(eta, dtype=float)
    out = np.sinh(eta) - eta
    sm = np.abs(eta) < 0.3
    x = eta[sm]
    x2 = x * x
    out[sm] = x * x2 / 6.0 * (1 + x2 / 20.0 * (1 + x2 / 42.0 * (1 + x2 / 72.0)))
    return out


def solve_eta_ell(q):
    """eta in [0, 2 pi] with eta - sin eta = q, q in [0, 2 pi] (bisection-safe Newton)."""
    q = np.clip(np.atleast_1d(np.asarray(q, dtype=float)), 0.0, TWO_PI)
    lo, hi = np.zeros_like(q), np.full_like(q, TWO_PI)
    e = np.clip(np.cbrt(6.0 * q), 0.0, TWO_PI)
    for _ in range(100):
        f = _q_ell(e) - q
        lo = np.where(f < 0, e, lo)
        hi = np.where(f > 0, e, hi)
        d = 1.0 - np.cos(e)
        en = np.where(d > 1e-300, e - f / np.where(d > 1e-300, d, 1.0), 0.5 * (lo + hi))
        bad = (en <= lo) | (en >= hi) | ~np.isfinite(en)
        en = np.where(bad, 0.5 * (lo + hi), en)
        if np.all(np.abs(en - e) <= 1e-15 * np.maximum(e, 1e-300)):
            return en
        e = en
    return e


def solve_eta_hyp(q):
    q = np.maximum(np.atleast_1d(np.asarray(q, dtype=float)), 0.0)
    e = np.cbrt(6.0 * q)
    big = q > 1.0
    e[big] = np.arcsinh(q[big] + 1.0) + 0.5
    for _ in range(100):
        f = _q_hyp(e) - q
        d = np.cosh(e) - 1.0
        en = np.where(d > 1e-300, e - f / np.where(d > 1e-300, d, 1.0), e)
        en = np.maximum(en, 0.5 * e)
        if np.all(np.abs(en - e) <= 1e-15 * np.maximum(e, 1e-300)):
            return en
        e = en
    return e


# ---------------------------------------------------------------------------- shells
class Shells:
    """Independent dust shells with Misner-Sharp mass M, energy E and age (time since the
    bang) age0 on the initial slice; tau is the proper time from that slice."""

    def __init__(self, M, E, age0):
        self.M = np.asarray(M, dtype=float)
        self.E = np.asarray(E, dtype=float)
        self.age0 = np.asarray(age0, dtype=float)

    @classmethod
    def from_state(cls, R0, U0, M):
        """Shells from the areal radius, its proper-time derivative and the mass."""
        R0, U0, M = (np.asarray(v, dtype=float) for v in (R0, U0, M))
        E = 0.5 * U0 ** 2 - M / R0
        age = np.empty_like(R0)
        ell = E < 0
        A = M[ell] / (-2.0 * E[ell])
        T0 = M[ell] / (-2.0 * E[ell]) ** 1.5
        c = np.clip(1.0 - R0[ell] / A, -1.0, 1.0)
        eta = np.arccos(c)                         # expanding branch, eta in [0, pi]
        eta = np.where(U0[ell] < 0, TWO_PI - eta, eta)
        age[ell] = T0 * _q_ell(eta)
        hyp = ~ell
        A = M[hyp] / (2.0 * np.maximum(E[hyp], 1e-300))
        T0 = M[hyp] / (2.0 * np.maximum(E[hyp], 1e-300)) ** 1.5
        eta = np.arccosh(1.0 + R0[hyp] / A)
        age[hyp] = T0 * _q_hyp(eta)
        if np.any(hyp & (U0 < 0)):
            raise ValueError("an unbound shell that contracts on the slice")
        return cls(M, E, age)

    def events(self):
        """Proper times from the initial slice of turnaround, R = 2M (collapsing branch)
        and crunch, and the turnaround radius; NaN for unbound shells."""
        M, E, age = self.M, self.E, self.age0
        out = {k: np.full(M.shape, np.nan) for k in ("tau_ta", "tau_ah", "tau_c", "R_max")}
        ell = E < 0
        T0 = M[ell] / (-2.0 * E[ell]) ** 1.5
        out["tau_ta"][ell] = math.pi * T0 - age[ell]
        out["tau_c"][ell] = TWO_PI * T0 - age[ell]
        c = np.clip(1.0 + 4.0 * E[ell], -1.0, 1.0)
        eta_ah = TWO_PI - np.arccos(c)
        out["tau_ah"][ell] = T0 * _q_ell(eta_ah) - age[ell]
        out["R_max"][ell] = M[ell] / (-E[ell])
        return out

    def R(self, tau):
        """Areal radius at proper times tau (array broadcast against the shells; last axis
        the shell); 0 after the crunch."""
        tau = np.asarray(tau, dtype=float)
        tau, M = np.broadcast_arrays(tau, self.M)
        E = np.broadcast_to(self.E, tau.shape)
        age = np.broadcast_to(self.age0, tau.shape)
        out = np.empty(tau.shape)
        ell = E < 0
        A = M[ell] / (-2.0 * E[ell])
        T0 = M[ell] / (-2.0 * E[ell]) ** 1.5
        q = (age[ell] + tau[ell]) / T0
        eta = solve_eta_ell(q)
        r = A * (1.0 - np.cos(eta))
        r[q >= TWO_PI] = 0.0
        out[ell] = r
        hyp = ~ell
        Eh = np.maximum(E[hyp], 1e-300)
        A = M[hyp] / (2.0 * Eh)
        T0 = M[hyp] / (2.0 * Eh) ** 1.5
        eta = solve_eta_hyp((age[hyp] + tau[hyp]) / T0)
        out[hyp] = A * (np.cosh(eta) - 1.0)
        return out


def first_crossing(sh, order, tau_max, n=40001):
    """First proper time at which two neighbouring shells (sorted by `order`, inner
    first) have R_out <= R_in while both are uncrunched, with the time on the initial
    slice taken as common (the slice is close to a synchronous one; the error is the
    spread of the initial lapse integrated, below 1e-3 of the times here). Returns
    (tau, index of the inner shell) or (nan, -1)."""
    idx = np.argsort(order)
    sub = Shells(sh.M[idx], sh.E[idx], sh.age0[idx])
    ev = sub.events()
    tc = np.where(np.isfinite(ev["tau_c"]), ev["tau_c"], np.inf)
    taus = np.linspace(0.0, tau_max, n)
    for t in taus[1:]:
        R = sub.R(np.full(sub.M.shape, t))
        alive = tc > t
        ok = alive[:-1] & alive[1:]
        bad = ok & (R[1:] <= R[:-1])
        if np.any(bad):
            j = int(np.flatnonzero(bad)[0])
            return float(t), int(idx[j])
    return math.nan, -1


# ---------------------------------------------------------------------------- reference A
def reference_A(mu, k=1.0, t_i=2.0 / 3.0, r=None):
    """Shells of the paper's profile (simultaneous bang, age t_i on the slice a = 1);
    r is the isotropic comoving radius (default 400 shells to 8/k)."""
    import os
    import sys
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.normpath(os.path.join(here, "..", "..", "criteria")))
    import ltb2609 as L                                  # noqa: E402
    P = L.Profile2609(mu, k, t_i)
    if r is None:
        r = np.linspace(0.02, 8.0, 400) / k
    r = np.asarray(r, dtype=float)
    M = P.M(r)
    E = -0.5 * P.ktilde(r) * r * r
    return P, r, Shells(M, E, np.full(r.shape, t_i))


# ---------------------------------------------------------------------------- reference B
def read_fields(path):
    """NRCOSMO1 file: psi, K, alpha, Ahat (xx, xy, xz, yy, yz, zz), arrays [i, j, k]."""
    with open(path, "rb") as f:
        if f.read(8) != b"NRCOSMO1":
            raise ValueError(f"{path}: not an NRCOSMO1 file")
        n1, n2, n3 = struct.unpack("qqq", f.read(24))
        arr = []
        for _ in range(9):
            a = np.fromfile(f, dtype=np.float64, count=n1 * n2 * n3)
            arr.append(a.reshape((n1, n2, n3), order="F"))
    return dict(psi=arr[0], K=arr[1], alpha=arr[2], A=arr[3:9])


def fourier_eval(F, L, pts, x0=-0.5):
    """Values at points pts[P, 3] of the periodic field whose cell-centred samples on
    [x0 L, (x0 + 1) L)^3 have the 3-D FFT F (numpy order); the Nyquist plane is halved
    (symmetric interpolant)."""
    n = F.shape[0]
    h = L / n
    kk = 2.0 * np.pi * np.fft.fftfreq(n, d=h)
    wq = np.ones(n)
    if n % 2 == 0:
        wq[n // 2] = 0.0                         # drop Nyquist (real-valued interpolant)
    xs = pts - (x0 * L + 0.5 * h)                # offset of the first cell centre
    out = np.empty(len(pts))
    for s in range(0, len(pts), 64):
        p = xs[s:s + 64]
        ex = wq[None, :] * np.exp(1j * np.outer(p[:, 0], kk))
        ey = wq[None, :] * np.exp(1j * np.outer(p[:, 1], kk))
        ez = wq[None, :] * np.exp(1j * np.outer(p[:, 2], kk))
        t = np.einsum("pk,ijk->pij", ez, F, optimize=True)
        t = np.einsum("pj,pij->pi", ey, t, optimize=True)
        out[s:s + 64] = np.real(np.einsum("pi,pi->p", ex, t)) / n ** 3
    return out


def reference_B(fields, L, x0, u0):
    """Shells of the code's initial slice at the particle positions x0[P, 3] with
    covariant momenta per unit rest mass u0[P, 3] (module doc). Returns (Shells, dict of
    the slice quantities)."""
    n = fields["psi"].shape[0]
    kk = 2.0 * np.pi * np.fft.fftfreq(n, d=L / n)
    KX, KY, KZ = np.meshgrid(kk, kk, kk, indexing="ij")
    Fp = np.fft.fftn(fields["psi"])
    psi = fourier_eval(Fp, L, x0)
    gp = [fourier_eval(1j * Kd * Fp, L, x0) for Kd in (KX, KY, KZ)]
    K = fourier_eval(np.fft.fftn(fields["K"]), L, x0)
    alpha = fourier_eval(np.fft.fftn(fields["alpha"]), L, x0)
    Ah = [fourier_eval(np.fft.fftn(a), L, x0) for a in fields["A"]]
    r = np.sqrt((x0 ** 2).sum(axis=1))
    nvec = x0 / r[:, None]
    nx, ny, nz = nvec.T
    Ann = (Ah[0] * nx * nx + Ah[3] * ny * ny + Ah[5] * nz * nz
           + 2.0 * (Ah[1] * nx * ny + Ah[2] * nx * nz + Ah[4] * ny * nz))
    AT = -0.5 * Ann
    KT = AT / psi ** 6 + K / 3.0
    R = psi ** 2 * r
    dpsidr = gp[0] * nx + gp[1] * ny + gp[2] * nz
    dRdr = psi ** 2 + 2.0 * r * psi * dpsidr
    M = 0.5 * R * (1.0 + R ** 2 * KT ** 2 - dRdr ** 2 / psi ** 4)
    W = np.sqrt(1.0 + (u0 ** 2).sum(axis=1) / psi ** 4)
    ur = (u0 * nvec).sum(axis=1)
    U = -W * R * KT + ur * dRdr / psi ** 4
    sh = Shells.from_state(R, U, M)
    return sh, dict(r0=r, R0=R, U0=U, M=M, E=sh.E, age0=sh.age0, psi=psi, K=K, KT=KT,
                    alpha=alpha, dRdr=dRdr, W=W, ur=ur)


# ---------------------------------------------------------------------------- background
def leak_background(rate, t_end, dt=1e-3, alpha0=1.0, a0=1.0, H0=1.0, alpha_ref=1.0):
    """Homogeneous dust universe in the relaxed 1+log slicing with zero shift:
        d a/dt = alpha a H(a),  H = H0 (a/a0)^(-3/2),
        d ln alpha/dt = 6 H - rate max(ln(alpha/alpha_ref), 0)     (Khat = K = -3H),
    classical RK4 in coordinate time t from (a0, alpha0). Returns t, a, alpha and the
    proper time tau(t) = int alpha dt."""
    nst = int(math.ceil(t_end / dt))
    T = np.empty(nst + 1)
    Y = np.empty((nst + 1, 3))
    y = np.array([a0, math.log(alpha0), 0.0])

    def rhs(y):
        a, la, _ = y
        H = H0 * (a / a0) ** -1.5
        al = math.exp(la)
        return np.array([al * a * H, 6.0 * H - rate * max(la - math.log(alpha_ref), 0.0), al])
    T[0], Y[0] = 0.0, y
    h = t_end / nst
    for i in range(nst):
        k1 = rhs(y)
        k2 = rhs(y + 0.5 * h * k1)
        k3 = rhs(y + 0.5 * h * k2)
        k4 = rhs(y + h * k3)
        y = y + h * (k1 + 2 * k2 + 2 * k3 + k4) / 6.0
        T[i + 1], Y[i + 1] = (i + 1) * h, y
    return T, Y[:, 0], np.exp(Y[:, 1]), Y[:, 2]


def t_over_tH(tau, eps_i=1.0, t_i=2.0 / 3.0):
    """Background proper time t_i + tau in units of t_H = t_i (6/eps_i^2)^(3/2)."""
    return (t_i + np.asarray(tau, dtype=float)) / (t_i * (6.0 / eps_i ** 2) ** 1.5)
