"""Reference algorithms for the stochastic sources of the scalar field in AthenaK
(design review E-pre-2, tracks/E-stoch-inf/codebase/DESIGN_REVIEW.md).

Nothing here is a simulation code: these are the exact reference operations that the
implementation in athenak/src (core) is checked against.

- band-limited real fields on a periodic box from their Fourier coefficients, by
  separable one-dimensional sums evaluated MeshBlock by MeshBlock (no Fourier library);
- the symbols of the centred first and second derivatives of athenak/src/utils/
  finite_diff.hpp (nghost 2, 3, 4);
- the window function of arXiv:2512.14649 and its analytic time derivatives;
- the stage times and effective weights of the integrators of athenak/src/driver/
  driver.cpp.

Conventions: box [x0, x0 + L)^3, N cells per side, cell centres x_i = x0 + (i + 1/2) h,
h = L/N; integer wave vectors n, k = 2 pi n / L; arrays indexed [i, j, k] = (x, y, z).
"""
import functools

import numpy as np


# ---------------------------------------------------------------------------------------
# Fourier coefficients on a ball of integer wave vectors
# ---------------------------------------------------------------------------------------
@functools.lru_cache(maxsize=8)
def ball_modes(nmax, include_zero=False):
    """All integer wave vectors n with |n| <= nmax (n = 0 only if include_zero), as an
    (M, 3) int array, sorted lexicographically."""
    r = np.arange(-nmax, nmax + 1)
    nx, ny, nz = np.meshgrid(r, r, r, indexing="ij")
    n = np.stack([nx.ravel(), ny.ravel(), nz.ravel()], axis=1)
    n2 = (n**2).sum(axis=1)
    keep = n2 <= nmax*nmax
    if not include_zero:
        keep &= n2 > 0
    out = n[keep]
    out.setflags(write=False)
    return out


def half_space(n):
    """True for the representative of each pair (n, -n): nx > 0, or nx = 0 and ny > 0,
    or nx = ny = 0 and nz > 0."""
    return (n[:, 0] > 0) | ((n[:, 0] == 0) & (n[:, 1] > 0)) | \
           ((n[:, 0] == 0) & (n[:, 1] == 0) & (n[:, 2] > 0))


def hermitian_gaussian(n, rng):
    """Complex Gaussian coefficients alpha_n with <|alpha_n|^2> = 1 and
    alpha_{-n} = conj(alpha_n) (the statistics of eq. alphas of arXiv:2512.14649 on the
    lattice). n must contain both members of each pair."""
    key = {tuple(v): i for i, v in enumerate(n)}
    a = np.zeros(len(n), dtype=complex)
    hs = half_space(n)
    idx = np.nonzero(hs)[0]
    z = (rng.standard_normal(len(idx)) + 1j*rng.standard_normal(len(idx)))/np.sqrt(2.0)
    a[idx] = z
    for i, zi in zip(idx, z):
        a[key[tuple(-n[i])]] = np.conj(zi)
    return a


# ---------------------------------------------------------------------------------------
# synthesis
# ---------------------------------------------------------------------------------------
def synth_fft(n, c, N, L, x0=0.0):
    """Reference: f at the cell centres from numpy.fft.ifftn (needs |n| < N/2)."""
    h = L/N
    A = np.zeros((N, N, N), dtype=complex)
    # phase of the cell-centre offset x0 + h/2 in each direction
    ph = np.exp(2j*np.pi*(n @ np.array([1.0, 1.0, 1.0]))*(x0 + 0.5*h)/L)
    np.add.at(A, (n[:, 0] % N, n[:, 1] % N, n[:, 2] % N), c*ph*N**3)
    return np.fft.ifftn(A)


def synth_block(n, c, N, L, i0, j0, k0, b, x0=0.0):
    """f on the b^3 cells of one MeshBlock whose first cell has global indices
    (i0, j0, k0), by three one-dimensional sums: over nz (for every (nx, ny) present),
    over ny (for every nx), over nx. Uses only the block's own cell coordinates.
    Returns the complex array [i, j, k] of shape (b, b, b) and the count of complex
    multiply-adds."""
    h = L/N
    xs = x0 + (np.arange(i0, i0 + b) + 0.5)*h
    ys = x0 + (np.arange(j0, j0 + b) + 0.5)*h
    zs = x0 + (np.arange(k0, k0 + b) + 0.5)*h
    w = 2.0*np.pi/L
    ops = 0
    # stage z: G1[(nx, ny), k]
    pairs, inv = np.unique(n[:, :2], axis=0, return_inverse=True)
    inv = inv.ravel()
    Ez = np.exp(1j*w*np.outer(n[:, 2], zs))            # (M, b)
    G1 = np.zeros((len(pairs), b), dtype=complex)
    np.add.at(G1, inv, c[:, None]*Ez)
    ops += len(n)*b
    # stage y: G2[nx, j, k]
    nxs, invx = np.unique(pairs[:, 0], return_inverse=True)
    invx = invx.ravel()
    Ey = np.exp(1j*w*np.outer(pairs[:, 1], ys))        # (P, b)
    G2 = np.zeros((len(nxs), b, b), dtype=complex)
    np.add.at(G2, invx, Ey[:, :, None]*G1[:, None, :])
    ops += len(pairs)*b*b
    # stage x
    Ex = np.exp(1j*w*np.outer(nxs, xs))                # (X, b)
    f = np.einsum("xi,xjk->ijk", Ex, G2)
    ops += len(nxs)*b**3
    return f, ops


def synth_mesh(n, c, N, L, b, x0=0.0):
    """f on the whole mesh assembled from MeshBlocks of b^3 cells (N divisible by b)."""
    f = np.zeros((N, N, N), dtype=complex)
    ops = 0
    for i0 in range(0, N, b):
        for j0 in range(0, N, b):
            for k0 in range(0, N, b):
                fb, o = synth_block(n, c, N, L, i0, j0, k0, b, x0)
                f[i0:i0+b, j0:j0+b, k0:k0+b] = fb
                ops += o
    return f, ops


def synth_ops(N, nmax, b, hermitian=False):
    """Complex multiply-adds of one synthesis over the whole mesh (formula of synth_block):
    (N/b)^3 [M b + P b^2 + X b^3], M modes in the ball, P distinct (nx, ny), X distinct nx.
    With hermitian=True the half space only (real part doubled)."""
    n = ball_modes(nmax)
    if hermitian:
        n = n[half_space(n)]
    M = len(n)
    P = len(np.unique(n[:, :2], axis=0))
    X = len(np.unique(n[:, 0]))
    nb = (N//b)**3
    return nb*(M*b + P*b*b + X*b**3)


# ---------------------------------------------------------------------------------------
# finite-difference symbols of athenak/src/utils/finite_diff.hpp
# ---------------------------------------------------------------------------------------
D1_COEF = {2: [1/2], 3: [2/3, -1/12], 4: [3/4, -3/20, 1/60]}


def keff(kh, nghost=4):
    """Symbol of the centred first derivative: D1 exp(i k x) = i keff exp(i k x);
    returns keff*h for k*h."""
    return sum(2.0*a*np.sin((m + 1)*kh) for m, a in enumerate(D1_COEF[nghost]))


def d1_periodic(f, axis, h, nghost=4):
    """Centred first derivative of a periodic array, the stencil of Dx<NGHOST>."""
    out = np.zeros_like(f)
    for m, a in enumerate(D1_COEF[nghost]):
        s = m + 1
        out += a*(np.roll(f, -s, axis=axis) - np.roll(f, s, axis=axis))
    return out/h


# ---------------------------------------------------------------------------------------
# window function of arXiv:2512.14649 (eq. ourWindow) and its time derivatives
# ---------------------------------------------------------------------------------------
def window(k, ksig, s=5.0):
    return 0.5*(1.0 + np.tanh(s*np.log(ksig/k)))


def window_dt(k, ksig, dlnks, d2lnks, s=5.0):
    """dW/dt and d2W/dt2 for ln k_sigma(t) with first and second time derivatives
    dlnks, d2lnks. In slow roll with Launay's signs (eps_{i+1} = -dln eps_i/dN):
    dlnks = H (1 - eps1), d2lnks = H^2 eps1 (eps2 - 1 + eps1)."""
    u = s*np.log(ksig/k)
    sech2 = 1.0/np.cosh(u)**2
    w1 = 0.5*s*sech2*dlnks
    w2 = 0.5*sech2*(s*d2lnks - 2.0*s*s*np.tanh(u)*dlnks**2)
    return w1, w2


# ---------------------------------------------------------------------------------------
# integrators of athenak/src/driver/driver.cpp
# ---------------------------------------------------------------------------------------
RK4_2S = dict(
    gam0=[0.0, 0.121098479554482, -3.843833699660025, 0.546370891121863],
    gam1=[1.0, 0.721781678111411, 2.121209265338722, 0.198653035682705],
    beta=[1.193743905974738, 0.099279895495783, 1.131678018054042, 0.310665766509336],
    delta=[1.0, 0.217683334308543, 1.065841341361089, 0.0])


def lowstorage_tableau(sch=RK4_2S):
    """Stage times c_s (the time at which stage s evaluates its right-hand side) and the
    effective weights b_s of the update u0 <- gam0 u0 + gam1 u1 + beta dt F(u0), with
    u1 <- u0 (stage 1) or u1 <- u1 + delta[s-1] u0 (stages 2..4) before F is evaluated,
    as in Z4c::CopyU and Z4c::ExpRKUpdate. Each register is held as coefficients on
    (u_n, dt F_1, ..., dt F_S); for u' = 1 the u0 coefficients sum to the stage time."""
    S = len(sch["beta"])
    e = lambda j: np.eye(S + 1)[j]
    u0 = e(0).copy()
    u1 = np.zeros(S + 1)
    c = []
    for s in range(S):
        if s == 0:
            u1 = u0.copy()
        else:
            u1 = u1 + sch["delta"][s]*u0
        c.append(u0[1:].sum())        # time of this stage, for u' = 1 and t_n = 0
        u0 = sch["gam0"][s]*u0 + sch["gam1"][s]*u1 + sch["beta"][s]*e(s + 1)
    # final u0 = a u_n + sum_s b_s dt F_s
    return np.array(c), u0[1:], u0[0]
