"""Analytic reference fields written directly as arrays (layout: grid.py).

1. Linear gravitational waves in Minkowski space, TT gauge, alpha = 1, beta = 0:
   h_ij(t, x) = sum_n Re[(a+_n e+_ij(k_n) + ax_n ex_ij(k_n)) exp(i(k_n.x - |k_n| t + phi_n))],
   gamma_ij = delta_ij + h_ij, K_ij = -(1/2) d_t h_ij. With the basis of tt.pol_basis.
   Linear-theory references: E_ij = -(1/2) d_t^2 h_ij, B_ij = -(1/2) sym(eps_ikl d_k d_t h_lj),
   Psi_4 (direction k) = d_t^2 h_+ - i d_t^2 h_x.
2. Pure gauge: Minkowski space in the coordinates (T, X) with t = T + f(X),
   x^i = X^i + xi^i(X). Exact (all orders): the T = const slice has
   gamma_ij = J^m_i J^m_j - d_i f d_j f (J = 1 + d xi), beta_i = -d_i f,
   alpha^2 = 1 + beta_i beta^i, d_T gamma_ij = 0, so
   K_ij = (1/2 alpha)(D_i beta_j + D_j beta_i); the Weyl tensor vanishes identically.
3. Scalar (longitudinal) perturbation: gamma_ij = (1 + 2 zeta) delta_ij + 2 d_i d_j E,
   K_ij = -(zetadot delta_ij + d_i d_j Edot) (alpha = 1, beta = 0). Linear theory:
   TT parts zero, B_ij = 0, E_ij = -(d_i d_j - delta_ij lap/3) zeta (the Coulomb-type
   tidal field; it does not vanish).
Mode wavevectors lie on the lattice of the box, so every field is periodic.
"""
import numpy as np

from .tt import pol_basis

EPS3 = np.zeros((3, 3, 3))
EPS3[0, 1, 2] = EPS3[1, 2, 0] = EPS3[2, 0, 1] = 1.0
EPS3[0, 2, 1] = EPS3[2, 1, 0] = EPS3[1, 0, 2] = -1.0


def lattice_k(grid, m):
    """Angular wavevector of integer mode numbers m = (mx, my, mz)."""
    return np.array([2 * np.pi * m[a] / grid.L[a] for a in range(3)])


class Wave:
    """One plane wave: integer mode numbers m, complex amplitudes ap, ax in the basis of
    tt.pol_basis(k/|k|), moving along +k."""

    def __init__(self, m, ap, ax):
        self.m = tuple(int(v) for v in m)
        self.ap = complex(ap)
        self.ax = complex(ax)


def wave_fields(waves, grid, t=0.0):
    """h, d_t h, d_t^2 h and the spatial gradient d_k d_t h (shape (3, 3, 3, ...),
    index order k, i, j) of a superposition of plane waves at time t."""
    X, Y, Z = grid.mesh()
    shp = (3, 3) + grid.shape
    h = np.zeros(shp)
    hd = np.zeros(shp)
    hdd = np.zeros(shp)
    dhd = np.zeros((3,) + shp)
    for w in waves:
        k = lattice_k(grid, w.m)
        kn = np.linalg.norm(k)
        ep, ex, _, _ = pol_basis((k / kn).reshape(3, 1, 1, 1))
        c = (w.ap * ep + w.ax * ex)[..., 0, 0, 0]               # (3, 3) complex
        ph = np.exp(1j * (k[0] * X + k[1] * Y + k[2] * Z - kn * t))
        cp = c[:, :, None, None, None] * ph
        h += cp.real
        hd += (-1j * kn * cp).real
        hdd += (-kn ** 2 * cp).real
        for a in range(3):
            dhd[a] += (1j * k[a] * -1j * kn * cp).real
    return h, hd, hdd, dhd


def wave_adm(waves, grid, t=0.0):
    """gamma_ij, K_ij of the linear waves (TT gauge, alpha = 1, beta = 0) and the
    linear-theory references (dict)."""
    h, hd, hdd, dhd = wave_fields(waves, grid, t)
    gamma = np.eye(3)[:, :, None, None, None] + h
    K = -0.5 * hd
    E_lin = -0.5 * hdd
    # B_ij = sym(eps_ikl d_k K_lj) = -(1/2) sym(eps_ikl d_k hd_lj)
    C = -0.5 * np.einsum("ikl,klj...->ij...", EPS3, dhd)
    B_lin = 0.5 * (C + np.einsum("ij...->ji...", C))
    return gamma, K, {"h": h, "hd": hd, "hdd": hdd, "E_lin": E_lin, "B_lin": B_lin}


def random_waves(grid, nmodes, kmin_m=1, kmax_m=4, slope=0.0, amp=1e-6, frac_plus=0.5,
                 seed=1):
    """nmodes plane waves on distinct lattice vectors with no pair k_n = +-k_m, |m| in
    [kmin_m, kmax_m], random directions and phases. The rms strain amplitude of mode n
    is amp (|m_n|/kmin_m)^slope; a fraction frac_plus of the energy of each mode is in
    helicity +2 (circular content), the rest in helicity -2, with a random relative phase.
    Returns the list of Wave."""
    rng = np.random.default_rng(seed)
    cand = []
    r = int(np.ceil(kmax_m))
    for mx in range(-r, r + 1):
        for my in range(-r, r + 1):
            for mz in range(-r, r + 1):
                n = np.sqrt(mx * mx + my * my + mz * mz)
                if kmin_m <= n <= kmax_m:
                    cand.append((mx, my, mz))
    rng.shuffle(cand)
    chosen = []
    used = set()
    for m in cand:
        if m in used or tuple(-v for v in m) in used:
            continue
        chosen.append(m)
        used.add(m)
        if len(chosen) == nmodes:
            break
    waves = []
    for m in chosen:
        n = np.sqrt(sum(v * v for v in m))
        A = amp * (n / kmin_m) ** slope
        # a_(+2) = (ap - i ax)/sqrt2, a_(-2) = (ap + i ax)/sqrt2;  |ap|^2 + |ax|^2 = A^2
        aR = A * np.sqrt(frac_plus) * np.exp(1j * rng.uniform(0, 2 * np.pi))
        aL = A * np.sqrt(1 - frac_plus) * np.exp(1j * rng.uniform(0, 2 * np.pi))
        ap = (aR + aL) / np.sqrt(2)
        ax = 1j * (aR - aL) / np.sqrt(2)
        waves.append(Wave(m, ap, ax))
    return waves


def waves_expected(waves, grid, G=1.0):
    """Exact (linear-theory) energy densities and helicity energies of a superposition of
    distinct waves: rho_kin = rho_grad = sum_n |k_n|^2 (|ap|^2 + |ax|^2)/(64 pi G).
    Returns dict with per-mode |k|, rho_kin, rho_plus, rho_minus and totals."""
    ks, rk, rp, rm = [], [], [], []
    for w in waves:
        kn = np.linalg.norm(lattice_k(grid, w.m))
        ks.append(kn)
        rk.append(kn ** 2 * (abs(w.ap) ** 2 + abs(w.ax) ** 2) / (64 * np.pi * G))
        # energy of the mode 2 rho_kin, split by |a_lam|^2 / (|a_+2|^2 + |a_-2|^2)
        aR2 = abs(w.ap - 1j * w.ax) ** 2 / 2
        aL2 = abs(w.ap + 1j * w.ax) ** 2 / 2
        tot = 2 * rk[-1]
        rp.append(tot * aR2 / (aR2 + aL2))
        rm.append(tot * aL2 / (aR2 + aL2))
    return {"k": np.array(ks), "rho_kin": np.array(rk), "rho_plus": np.array(rp),
            "rho_minus": np.array(rm), "rho_kin_total": float(np.sum(rk)),
            "rho_plus_total": float(np.sum(rp)), "rho_minus_total": float(np.sum(rm))}


# ----------------------------------------------------------------------------------------
# Fourier-sum scalar fields with analytic derivatives

class ModeField:
    """f(x) = eps sum_n c_n sin(k_n.x + phi_n): value, gradient, Hessian, third
    derivatives, all analytic."""

    def __init__(self, grid, ms, coef, phase, eps):
        self.k = [lattice_k(grid, m) for m in ms]
        self.c = list(coef)
        self.p = list(phase)
        self.eps = eps
        self.X = grid.mesh()

    def _arg(self, k, p):
        X, Y, Z = self.X
        return k[0] * X + k[1] * Y + k[2] * Z + p

    def val(self):
        return self.eps * sum(c * np.sin(self._arg(k, p)) for k, c, p in zip(self.k, self.c, self.p))

    def grad(self):
        out = np.zeros((3,) + self.X[0].shape)
        for k, c, p in zip(self.k, self.c, self.p):
            cs = np.cos(self._arg(k, p))
            for a in range(3):
                out[a] += self.eps * c * k[a] * cs
        return out

    def hess(self):
        out = np.zeros((3, 3) + self.X[0].shape)
        for k, c, p in zip(self.k, self.c, self.p):
            s = np.sin(self._arg(k, p))
            for a in range(3):
                for b in range(3):
                    out[a, b] -= self.eps * c * k[a] * k[b] * s
        return out

    def third(self):
        out = np.zeros((3, 3, 3) + self.X[0].shape)
        for k, c, p in zip(self.k, self.c, self.p):
            cs = np.cos(self._arg(k, p))
            for a in range(3):
                for b in range(3):
                    for d in range(3):
                        out[a, b, d] -= self.eps * c * k[a] * k[b] * k[d] * cs
        return out


def random_modefield(grid, eps, nmodes=4, mmax=2, seed=0):
    rng = np.random.default_rng(seed)
    ms = []
    while len(ms) < nmodes:
        m = tuple(int(v) for v in rng.integers(-mmax, mmax + 1, size=3))
        if any(m) and m not in ms:
            ms.append(m)
    coef = rng.normal(size=nmodes)
    coef = coef / np.sqrt(np.sum(coef ** 2))
    return ModeField(grid, ms, coef, rng.uniform(0, 2 * np.pi, nmodes), eps)


def gauge_mode(grid, eps, seed=0, slicing=True, nmodes=3, mmax=2):
    """Exact Minkowski space in random coordinates (see module docstring), amplitude eps
    of xi^i / L and of f / L (as dimensionless gradients ~ eps k L). Returns gamma, K,
    alpha, beta_i (lower index)."""
    L = max(grid.L)
    xis = [random_modefield(grid, eps * L / (2 * np.pi), nmodes, mmax, seed + 10 * a + 1)
           for a in range(3)]
    f = random_modefield(grid, eps * L / (2 * np.pi), nmodes, mmax, seed + 7) if slicing else None
    shp = grid.shape
    J = np.eye(3)[:, :, None, None, None] + np.array([x.grad() for x in xis])   # J[m, i] = d_i x^m
    dJ = np.array([x.hess() for x in xis])                                     # dJ[m, i, k] = d_k d_i x^m
    gamma = np.einsum("mi...,mj...->ij...", J, J)
    dgamma = (np.einsum("mik...,mj...->kij...", dJ, J)
              + np.einsum("mi...,mjk...->kij...", J, dJ))                        # d_k gamma_ij
    if f is None:
        K = np.zeros((3, 3) + shp)
        return gamma, K, np.ones(shp), np.zeros((3,) + shp)
    df = f.grad()
    ddf = f.hess()
    gamma = gamma - df[:, None] * df[None, :]
    dgamma = dgamma - (np.einsum("ik...,j...->kij...", ddf, df)
                       + np.einsum("i...,jk...->kij...", df, ddf))
    beta = -df                                                              # beta_i
    dbeta = -ddf                                                            # d_j beta_i (sym)
    from .tt import inv3
    ginv, _ = inv3(gamma)
    bup = np.einsum("ij...,j...->i...", ginv, beta)
    alpha = np.sqrt(1.0 + np.einsum("i...,i...->...", beta, bup))
    G1 = 0.5 * (np.einsum("ikj...->kij...", dgamma) + np.einsum("jki...->kij...", dgamma)
                - dgamma)                                                   # G_kij
    G2 = np.einsum("km...,mij...->kij...", ginv, G1)
    Dbeta = dbeta - np.einsum("kij...,k...->ij...", G2, beta)               # D_j beta_i
    K = (Dbeta + np.einsum("ij...->ji...", Dbeta)) / (2.0 * alpha)
    return gamma, K, alpha, beta


def scalar_mode(grid, eps, seed=0, nmodes=3, mmax=2):
    """Scalar-type data (see module docstring). zeta and k^2 E have amplitude eps; their
    time derivatives are set to eps times a random rate of order |k|. Returns gamma, K and
    the linear-theory E_ij."""
    zeta = random_modefield(grid, eps, nmodes, mmax, seed + 1)
    L = max(grid.L)
    E = random_modefield(grid, eps * (L / (2 * np.pi)) ** 2, nmodes, mmax, seed + 2)
    zd = random_modefield(grid, eps * 2 * np.pi / L, nmodes, mmax, seed + 3)
    Ed = random_modefield(grid, eps * L / (2 * np.pi), nmodes, mmax, seed + 4)
    d = np.eye(3)[:, :, None, None, None]
    gamma = (1 + 2 * zeta.val()) * d + 2 * E.hess()
    K = -(zd.val() * d + Ed.hess())
    H = zeta.hess()
    lap = np.einsum("ii...->...", H)
    E_lin = -(H - d * lap / 3.0)
    return gamma, K, {"E_lin": E_lin, "zeta": zeta}
