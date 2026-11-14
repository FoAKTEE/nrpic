"""Constraint-satisfying initial data on the three-torus for particles (cosmo/PLAN.md, P1).

Slice: gamma_ij = psi^4 delta_ij, K_ij = psi^-2 Ahat_ij + (1/3) psi^4 delta_ij K, with K
given, Ahat_ij = d_i W_j + d_j W_i - (2/3) delta_ij d_k W_k. The particles (positions x,
covariant momenta per unit rest mass u_i, rest masses m) are held fixed; their deposited
sums Ehat = psi^6 E and Shat_i = psi^6 S_i do not depend on psi except through the
Lorentz factors. The constraints

    lap psi  = (1/12) K^2 psi^5 - (1/8) psi^-7 Ahat_ij Ahat_ij - 2 pi psi^5 E,
    d_j Ahat_ij = (2/3) psi^6 d_i K + 8 pi psi^6 S_i,

are solved with Fourier transforms on the mesh of the run, with E and S_i formed exactly
as the code forms them: cloud-in-cell deposit to cell centres, division by sqrt(gamma) =
psi^6 of the cell, then the binomial filter passes. The linearized Hamiltonian operator
is lap - sigma with sigma = (5/12) K^2 + 2 pi E > 0, so the fixed-point iteration below
contracts.

Arrays on the mesh have shape (n, n, n) and are indexed [i, j, k] = (x, y, z); cell
centres are at (i + 1/2) h. Units G = c = 1.
"""
import numpy as np
from scipy import ndimage


# ---------------------------------------------------------------------------------------
# particle-mesh operations of the code
# ---------------------------------------------------------------------------------------
SHAPE = "cic"    # cloud shape of the deposit, as <particles> deposit_shape of the code


def cic_deposit(x, w, n, L, shape=None):
    """Sum of weights w spread with the cloud shape of the code, per coordinate volume:
    a B-spline of degree one ("cic", two cells per direction), two ("tsc", three cells)
    or three ("pcs", four cells). The default is the module variable SHAPE."""
    shape = SHAPE if shape is None else shape
    h = L/n
    xi = x/h - 0.5
    if shape == "tsc":
        i0 = np.floor(xi + 0.5).astype(np.int64)
        d = xi - i0
        wts = [0.5*(0.5 - d)**2, 0.75 - d*d, 0.5*(0.5 + d)**2]
        i0 = i0 - 1
    elif shape == "pcs":
        i0 = np.floor(xi).astype(np.int64)
        s = xi - i0
        wts = [(1.0 - s)**3/6.0, (3.0*s**3 - 6.0*s**2 + 4.0)/6.0,
               (-3.0*s**3 + 3.0*s**2 + 3.0*s + 1.0)/6.0, s**3/6.0]
        i0 = i0 - 1
    else:
        i0 = np.floor(xi).astype(np.int64)
        s = xi - i0
        wts = [1.0 - s, s]
    out = np.zeros(n*n*n)
    for cx, wx in enumerate(wts):
        ix = (i0[:, 0] + cx) % n
        for cy, wy in enumerate(wts):
            iy = (i0[:, 1] + cy) % n
            for cz, wz in enumerate(wts):
                iz = (i0[:, 2] + cz) % n
                out += np.bincount((ix*n + iy)*n + iz,
                                   weights=w*wx[:, 0]*wy[:, 1]*wz[:, 2],
                                   minlength=n*n*n)
    return out.reshape(n, n, n)/h**3


def interp(f, x, L, order=3):
    """Value of the cell-centred periodic field f at the positions x."""
    n = f.shape[0]
    c = (x/(L/n) - 0.5).T
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


# ---------------------------------------------------------------------------------------
# spectral operators on the torus
# ---------------------------------------------------------------------------------------
class Torus:
    def __init__(self, n, L):
        self.n, self.L, self.h = n, L, L/n
        k1 = 2.0*np.pi*np.fft.fftfreq(n, d=L/n)
        kr = 2.0*np.pi*np.fft.rfftfreq(n, d=L/n)
        self.k = np.meshgrid(k1, k1, kr, indexing="ij")
        self.k2 = self.k[0]**2 + self.k[1]**2 + self.k[2]**2
        # first derivatives: the Nyquist mode of an even grid has no derivative
        self.kd = [np.array(kk) for kk in self.k]
        if n % 2 == 0:
            self.kd[0][n//2, :, :] = 0.0
            self.kd[1][:, n//2, :] = 0.0
            self.kd[2][:, :, n//2] = 0.0

    def fft(self, f):
        return np.fft.rfftn(f)

    def ifft(self, F):
        return np.fft.irfftn(F, s=(self.n,)*3)

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
        k, k2 = self.kd, self.k2.copy()
        k2[0, 0, 0] = 1.0
        kR = k[0]*Rk[0] + k[1]*Rk[1] + k[2]*Rk[2]
        Wk = [-(Rk[i] - 0.25*k[i]*kR/k2)/k2 for i in range(3)]
        for w in Wk:
            w[0, 0, 0] = 0.0
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


# ---------------------------------------------------------------------------------------
# constraint solve
# ---------------------------------------------------------------------------------------
def sources(tor, x, u, m, psi, nfilter=0, compensate=False):
    """E and S_i on the mesh as the code forms them, and the Lorentz factors."""
    psip = interp(psi, x, tor.L)
    W = np.sqrt(1.0 + (u*u).sum(axis=1)/psip**4)
    isg = 1.0/psi**6
    E = binomial(cic_deposit(x, m*W, tor.n, tor.L)*isg, nfilter, compensate)
    S = [binomial(cic_deposit(x, m*u[:, i], tor.n, tor.L)*isg, nfilter, compensate)
         for i in range(3)]
    return E, S, W


def residuals(tor, psi, K, A, E, S):
    """Hamiltonian residual (the first constraint above, all terms on the left) and the
    three momentum residuals."""
    ham = tor.lap(psi) - K*K*psi**5/12.0 + a_squared(A)/(8.0*psi**7) + 2.0*np.pi*psi**5*E
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


def solve(tor, x, u, m, K, psi0=None, nfilter=0, compensate=False, tol=1e-12,
          maxit=200, verbose=False):
    """Conformal factor psi and Ahat_ij for the given particles and K.
    Returns a dict with psi, A (six arrays), E, S, W (Lorentz factors), the history of
    the largest Hamiltonian residual, and the mean of the momentum source that was
    removed (it must be small: the torus has no solution otherwise)."""
    psi = np.ones((tor.n,)*3) if psi0 is None else np.array(psi0, dtype=float)
    dK = tor.grad(K)
    hist = []
    for it in range(maxit):
        E, S, W = sources(tor, x, u, m, psi, nfilter, compensate)
        R = [(2.0/3.0)*psi**6*dK[i] + 8.0*np.pi*psi**6*S[i] for i in range(3)]
        rmean = [float(r.mean()) for r in R]
        _, A = tor.solve_vector([r - r.mean() for r in R])
        ham = (tor.lap(psi) - K*K*psi**5/12.0 + a_squared(A)/(8.0*psi**7)
               + 2.0*np.pi*psi**5*E)
        err = float(np.abs(ham).max())
        hist.append(err)
        if verbose:
            print(f"  it {it:3d}  max |H| = {err:.3e}")
        if err < tol:
            break
        sigma = float((5.0*K*K*psi**4/12.0 + 2.0*np.pi*psi**4*E).mean())
        psi = psi + tor.solve_helmholtz(-ham, sigma)
    return {"psi": psi, "A": A, "E": E, "S": S, "W": W, "hist": hist, "rmean": rmean}
