"""Constraint-satisfying initial data for particles on a three-torus with a rectangular
box of n1 x n2 x n3 cells (the solver of `cosmo/ic/cosmo_id.py`, which is restricted to a
cube, written for any box; for a cube the two agree to rounding).

Slice: gamma_ij = psi^4 delta_ij, K_ij = psi^-2 Ahat_ij + (1/3) psi^4 delta_ij K, with K
given, Ahat_ij = d_i W_j + d_j W_i - (2/3) delta_ij d_k W_k. The particles (positions x,
covariant momenta per unit rest mass u_i, rest masses m) are held fixed; their deposited
sums Ehat = psi^6 E and Shat_i = psi^6 S_i do not depend on psi except through the
Lorentz factors. The constraints

    lap psi  = (1/12) K^2 psi^5 - (1/8) psi^-7 Ahat_ij Ahat_ij - 2 pi psi^5 E,
    d_j Ahat_ij = (2/3) psi^6 d_i K + 8 pi psi^6 S_i,

are solved with Fourier transforms on the mesh of the run, with E and S_i formed as the
code forms them: deposit with the cloud of the run to cell centres, optional
compensation of the cloud, division by sqrt(gamma) = psi^6 of the cell, then the binomial
filter passes. The linearized Hamiltonian operator is lap - sigma with
sigma = (5/12) K^2 + 2 pi E > 0, so the fixed-point iteration contracts.

Arrays on the mesh have shape (n1, n2, n3) and are indexed [i, j, k] = (x, y, z); cell
centres are at (i + 1/2) h_x and so on; the box is [0, L1) x [0, L2) x [0, L3).
Units G = c = 1. Options of the deposit (as `<particles>` of the code) are passed as a
`Deposit` object instead of module variables.

Derivatives. By default (`Torus(n, L)`) they are spectral, as in `cosmo/ic/cosmo_id.py`:
the data then satisfy the constraints of the code up to the truncation error of its
finite differences, which is negligible for smooth data and of order one for the part of
the sources near the mesh frequency (a particle lattice displaced at random). With
`Torus(n, L, fd_order=6)` (4 and 2 for `nghost` = 3 and 2) the derivatives are the centred
differences of the code: the Hamiltonian residual is the one the code evaluates
(`Z4c::ADMConstraints`: Ricci scalar of gamma_ij = psi^4 delta_ij from first and second
differences of psi^4), to rounding, and the vector equation is solved with the first
difference applied twice. The momentum constraint of the code then holds up to the
product-rule error of the differences (noise of the sources times the relative change of
psi over a cell). The eight modes whose first differences all vanish (zero or the mesh
frequency in every direction) cannot be solved for; their part of the momentum source is
dropped and reported (`rdrop`).
"""
from dataclasses import dataclass

import numpy as np
from scipy import ndimage

__all__ = ["Deposit", "Torus", "deposit", "interp", "compensate_density", "binomial",
           "a_squared", "sources", "hamiltonian", "residuals", "solve"]


@dataclass
class Deposit:
    """Options of the deposit of the run."""
    shape: str = "cic"          # deposit_shape: cic, tsc, pcs
    comp_c: float = -1.0        # filter_comp_c (compensation pass of the binomial filter)
    dep_comp_c: float = 0.0     # deposit_comp_c (compensation of the cloud)
    dep_comp_limit: float = 0.0  # deposit_comp_limit
    dep_comp_c2: float = 0.0    # deposit_comp_c2
    nfilter: int = 0            # nfilter
    compensate: bool = False    # filter_compensate


def _three(v):
    return (v,)*3 if np.isscalar(v) else tuple(v)


def _cloud(xi, shape):
    """First cell index and the weights of the cloud along one direction."""
    if shape == "tsc":
        i0 = np.floor(xi + 0.5).astype(np.int64)
        d = xi - i0
        return i0 - 1, [0.5*(0.5 - d)**2, 0.75 - d*d, 0.5*(0.5 + d)**2]
    if shape == "pcs":
        i0 = np.floor(xi).astype(np.int64)
        s = xi - i0
        return i0 - 1, [(1.0 - s)**3/6.0, (3.0*s**3 - 6.0*s**2 + 4.0)/6.0,
                        (-3.0*s**3 + 3.0*s**2 + 3.0*s + 1.0)/6.0, s**3/6.0]
    if shape != "cic":
        raise ValueError(f"unknown cloud shape {shape}")
    i0 = np.floor(xi).astype(np.int64)
    s = xi - i0
    return i0, [1.0 - s, s]


def deposit(x, w, n, L, shape="cic"):
    """Sum of the weights w spread with the cloud of the code, per coordinate volume: a
    B-spline of degree one ("cic"), two ("tsc") or three ("pcs") per direction."""
    n, L = _three(n), _three(L)
    h = [L[d]/n[d] for d in range(3)]
    i0, wts = [], []
    for d in range(3):
        a, b = _cloud(x[:, d]/h[d] - 0.5, shape)
        i0.append(a)
        wts.append(b)
    ntot = n[0]*n[1]*n[2]
    out = np.zeros(ntot)
    for cx, wx in enumerate(wts[0]):
        ix = (i0[0] + cx) % n[0]
        for cy, wy in enumerate(wts[1]):
            iy = (i0[1] + cy) % n[1]
            for cz, wz in enumerate(wts[2]):
                iz = (i0[2] + cz) % n[2]
                out += np.bincount((ix*n[1] + iy)*n[2] + iz, weights=w*wx*wy*wz,
                                   minlength=ntot)
    return out.reshape(n)/(h[0]*h[1]*h[2])


def interp(f, x, L, order=3):
    """Value of the cell-centred periodic field f at the positions x."""
    L = _three(L)
    c = np.stack([x[:, d]/(L[d]/f.shape[d]) - 0.5 for d in range(3)])
    return ndimage.map_coordinates(f, c, order=order, mode="grid-wrap")


def binomial(f, npass, compensate=False, comp_c=-1.0):
    """The source filter of the code: npass passes of (1/4, 1/2, 1/4) per direction and,
    with compensate, one pass (-c, 1 + 2c, -c) per direction, c = npass/4 by default."""
    g = f
    passes = [(0.5, 0.25)]*npass
    if compensate and (npass > 0 or comp_c > 0.0):
        c = comp_c if comp_c >= 0.0 else 0.25*npass
        passes = passes + [(1.0 + 2.0*c, -c)]
    for w0, w1 in passes:
        for ax in range(3):
            g = w0*g + w1*(np.roll(g, 1, ax) + np.roll(g, -1, ax))
    return g


def compensate_density(fields, c, lim=0.0, c2=0.0):
    """The compensation pass of the deposit as in the code (NrpicCompensateLimited):
    fields[0] is the energy density, the others follow it. Per direction
    u - (F_{i+1/2} - F_{i-1/2}), F_{i+1/2} = c (u_{i+1} - u_i)
    - (c2/16) (u_{i+2} - 3 u_{i+1} + 3 u_i - u_{i-1}); with lim > 0 each face flux is
    scaled by min(1, lim min(E_i, E_{i+1}) / |flux of E|); the directions in turn."""
    if lim <= 0.0 and c2 == 0.0:
        return [binomial(f, 0, True, c) for f in fields]
    q = c2/16.0

    def flux(u, ax):
        up, um, upp = np.roll(u, -1, ax), np.roll(u, 1, ax), np.roll(u, -2, ax)
        return c*(up - u) - q*(upp - 3.0*up + 3.0*u - um)

    out = [np.array(f, dtype=float) for f in fields]
    for ax in range(3):
        th = 1.0
        if lim > 0.0:
            e = out[0]
            fe = flux(e, ax)
            cap = lim*np.maximum(np.minimum(e, np.roll(e, -1, ax)), 0.0)
            with np.errstate(divide="ignore", invalid="ignore"):
                th = np.where(np.abs(fe) > cap, cap/np.abs(fe), 1.0)
        new = []
        for u in out:
            f = th*flux(u, ax)                         # flux through the upper face
            new.append(u - f + np.roll(f, 1, ax))
        out = new
    return out


# centred differences of athenak/src/utils/finite_diff.hpp: first derivative (offsets
# 1, 2, ...) and second derivative (offsets 0, 1, 2, ...), by order of accuracy
FD1 = {2: [0.5], 4: [2.0/3.0, -1.0/12.0], 6: [0.75, -0.15, 1.0/60.0]}
FD2 = {2: [-2.0, 1.0], 4: [-2.5, 4.0/3.0, -1.0/12.0],
       6: [-49.0/18.0, 1.5, -0.15, 1.0/90.0]}


class Torus:
    """Derivative operators on the box of n = (n1, n2, n3) cells and lengths L, applied
    in Fourier space: spectral (fd_order = None) or the centred differences of the code
    of order fd_order (2, 4 or 6; 2 (nghost - 1) for the code)."""

    def __init__(self, n, L, fd_order=None):
        self.n, self.L = _three(n), _three(L)
        self.h = tuple(self.L[d]/self.n[d] for d in range(3))
        self.fd_order = fd_order
        k1 = 2.0*np.pi*np.fft.fftfreq(self.n[0], d=self.h[0])
        k2 = 2.0*np.pi*np.fft.fftfreq(self.n[1], d=self.h[1])
        k3 = 2.0*np.pi*np.fft.rfftfreq(self.n[2], d=self.h[2])
        self.k = np.meshgrid(k1, k2, k3, indexing="ij")
        if fd_order is None:
            self.k2 = self.k[0]**2 + self.k[1]**2 + self.k[2]**2
            # first derivatives: the Nyquist mode of an even grid has no derivative
            self.kd = [np.array(kk) for kk in self.k]
            if self.n[0] % 2 == 0:
                self.kd[0][self.n[0]//2, :, :] = 0.0
            if self.n[1] % 2 == 0:
                self.kd[1][:, self.n[1]//2, :] = 0.0
            if self.n[2] % 2 == 0:
                self.kd[2][:, :, self.n[2]//2] = 0.0
            # operator of the vector equation, as in cosmo/ic/cosmo_id.py
            self.k2v = self.k2
        else:
            c1, c2 = FD1[fd_order], FD2[fd_order]
            self.kd, self.k2 = [], 0.0
            for d in range(3):
                th = self.k[d]*self.h[d]
                self.kd.append(2.0*sum(c*np.sin((m + 1)*th) for m, c in enumerate(c1))
                               / self.h[d])
                self.k2 = self.k2 - (c2[0] + 2.0*sum(c*np.cos((m + 1)*th)
                                                     for m, c in enumerate(c2[1:])))/self.h[d]**2
            # the vector equation contains the first difference applied twice
            self.k2v = self.kd[0]**2 + self.kd[1]**2 + self.kd[2]**2
        self.rdrop = 0.0

    def fft(self, f):
        return np.fft.rfftn(f)

    def ifft(self, F):
        return np.fft.irfftn(F, s=self.n)

    def grad(self, f):
        F = self.fft(f)
        return [self.ifft(1j*kd*F) for kd in self.kd]

    def lap(self, f):
        return self.ifft(-self.k2*self.fft(f))

    def solve_helmholtz(self, rhs, sigma):
        """f with (lap - sigma) f = rhs, sigma > 0 constant."""
        return self.ifft(-self.fft(rhs)/(self.k2 + sigma))

    def solve_vector(self, R):
        """W_i with lap W_i + (1/3) d_i d_k W_k = R_i (mean of R removed), and the
        traceless Ahat_ij = d_i W_j + d_j W_i - (2/3) delta_ij d_k W_k as six arrays
        (xx, xy, xz, yy, yz, zz)."""
        Rk = [self.fft(r) for r in R]
        k, k2 = self.kd, self.k2v.copy()
        # modes without a solution: the mean, and with differences the modes whose
        # first differences all vanish
        null = k2 <= 1e-12*np.abs(self.k2v).max()
        null[0, 0, 0] = True
        k2[null] = 1.0
        kR = k[0]*Rk[0] + k[1]*Rk[1] + k[2]*Rk[2]
        Wk = [-(Rk[i] - 0.25*k[i]*kR/k2)/k2 for i in range(3)]
        ntot = self.n[0]*self.n[1]*self.n[2]
        self.rdrop = float(max(np.abs(r[null]).max() for r in Rk)/ntot)
        for w in Wk:
            w[null] = 0.0
        divW = 1j*(k[0]*Wk[0] + k[1]*Wk[1] + k[2]*Wk[2])
        A = []
        for a in range(3):
            for b in range(a, 3):
                Ak = 1j*(k[a]*Wk[b] + k[b]*Wk[a])
                if a == b:
                    Ak = Ak - (2.0/3.0)*divW
                A.append(self.ifft(Ak))
        return [self.ifft(w) for w in Wk], A


def a_squared(A):
    """Ahat_ij Ahat_ij from the six stored components."""
    xx, xy, xz, yy, yz, zz = A
    return xx*xx + yy*yy + zz*zz + 2.0*(xy*xy + xz*xz + yz*yz)


def sources(tor, x, u, m, psi, dep):
    """E and S_i on the mesh as the code forms them, and the Lorentz factors."""
    psip = interp(psi, x, tor.L)
    W = np.sqrt(1.0 + (u*u).sum(axis=1)/psip**4)
    isg = 1.0/psi**6
    dens = [deposit(x, m*W, tor.n, tor.L, dep.shape)] \
        + [deposit(x, m*u[:, i], tor.n, tor.L, dep.shape) for i in range(3)]
    if dep.dep_comp_c > 0.0:
        dens = compensate_density(dens, dep.dep_comp_c, dep.dep_comp_limit, dep.dep_comp_c2)
    E = binomial(dens[0]*isg, dep.nfilter, dep.compensate, dep.comp_c)
    S = [binomial(dens[1 + i]*isg, dep.nfilter, dep.compensate, dep.comp_c)
         for i in range(3)]
    return E, S, W


def hamiltonian(tor, psi, K, A, E):
    """Hamiltonian residual: the first constraint above with all terms on the left. With
    differences (tor.fd_order) it is -(psi^5/8) times the constraint as the code
    evaluates it: Ricci scalar of gamma_ij = f delta_ij, f = psi^4, from differences of
    f, R = -2 sum_i D_ii f / f^2 + (3/2) sum_i (D_i f)^2 / f^3."""
    if tor.fd_order is None:
        return (tor.lap(psi) - K*K*psi**5/12.0 + a_squared(A)/(8.0*psi**7)
                + 2.0*np.pi*psi**5*E)
    f = psi**4
    F = tor.fft(f)
    lapf = tor.ifft(-tor.k2*F)
    grad2 = sum(tor.ifft(1j*kd*F)**2 for kd in tor.kd)
    ricci = -2.0*lapf/f**2 + 1.5*grad2/f**3
    hc = ricci + (2.0/3.0)*K*K - a_squared(A)/psi**12 - 16.0*np.pi*E
    return -(psi**5/8.0)*hc


def residuals(tor, psi, K, A, E, S):
    """Hamiltonian residual (see `hamiltonian`) and the three momentum residuals."""
    ham = hamiltonian(tor, psi, K, A, E)
    dK = tor.grad(K)
    Ak = [tor.fft(a) for a in A]
    idx = {(0, 0): 0, (0, 1): 1, (0, 2): 2, (1, 1): 3, (1, 2): 4, (2, 2): 5}
    mom = []
    for i in range(3):
        div = 0.0
        for j in range(3):
            div = div + 1j*tor.kd[j]*Ak[idx[(min(i, j), max(i, j))]]
        mom.append(tor.ifft(div) - (2.0/3.0)*psi**6*dK[i] - 8.0*np.pi*psi**6*S[i])
    return ham, mom


def solve(tor, x, u, m, K, dep=None, psi0=None, tol=1e-12, maxit=200, verbose=False):
    """Conformal factor psi and Ahat_ij for the given particles and K.
    Returns a dict with psi, A (six arrays), E, S, W (Lorentz factors), the history of
    the largest Hamiltonian residual, and the mean of the momentum source that was
    removed (it must be small: the torus has no solution otherwise)."""
    dep = Deposit() if dep is None else dep
    psi = np.ones(tor.n) if psi0 is None else np.array(psi0, dtype=float)
    dK = tor.grad(K)
    hist = []
    for it in range(maxit):
        E, S, W = sources(tor, x, u, m, psi, dep)
        R = [(2.0/3.0)*psi**6*dK[i] + 8.0*np.pi*psi**6*S[i] for i in range(3)]
        rmean = [float(r.mean()) for r in R]
        _, A = tor.solve_vector([r - r.mean() for r in R])
        ham = hamiltonian(tor, psi, K, A, E)
        err = float(np.abs(ham).max())
        hist.append(err)
        if verbose:
            print(f"  it {it:3d}  max |H| = {err:.3e}")
        if err < tol:
            break
        sigma = float((5.0*K*K*psi**4/12.0 + 2.0*np.pi*psi**4*E).mean())
        psi = psi + tor.solve_helmholtz(-ham, sigma)
    return {"psi": psi, "A": A, "E": E, "S": S, "W": W, "hist": hist, "rmean": rmean,
            "rdrop": tor.rdrop}
