"""Gaussian random density fields on the periodic mesh, their power spectra, and the
Zel'dovich displacement.

Mesh conventions as in cosmo_id.py: box [0, L)^3 (L in Mpc/h), n^3 cells, cell centres at
x_i = (i + 1/2) L/n, arrays indexed [i, j, k] = (x, y, z), N = n^3.

Fourier convention (used by every function here):

    delta_k = (1/N) sum_x delta(x) exp(-i k.x),   delta(x) = sum_k delta_k exp(i k.x),

with x the cell-centre positions (not the indices) and k = (2 pi / L)(n_x, n_y, n_z). A
field with power spectrum P(k) has <|delta_k|^2> = P(|k|) / L^3 for every mesh mode
(k != 0), so that sum_k |delta_k|^2 -> int d^3k/(2 pi)^3 P(k) = sigma^2. The coefficients
differ from numpy's fftn(delta)/N by the phase exp(-i k.h/2), h = L/n, which keeps them
the same for the same physical field on meshes of different resolution. On a Nyquist
plane the wavenumber component is taken as -pi/h (numpy fftfreq order).
"""
import numpy as np

try:
    from cosmo_id import Torus
except ImportError:                       # imported as part of a package
    from .cosmo_id import Torus

_SQRT2 = np.sqrt(2.0)


# ---------------------------------------------------------------------------------------
# realisation
# ---------------------------------------------------------------------------------------
def _shell(s):
    """Integer vectors with max(|n_x|, |n_y|, |n_z|) = s, in lexicographic order, so that
    v -> -v maps entry i to entry count - 1 - i. (24 s^2 + 2 vectors for s >= 1.)"""
    if s == 0:
        return np.zeros((1, 3), dtype=np.int64)
    r = np.arange(-s, s + 1)
    inner = np.arange(-s + 1, s)
    m = 2*s + 1
    sq_y, sq_z = np.repeat(r, m), np.tile(r, m)                  # full face, (ny, nz)
    ring_y = np.concatenate([np.full(m, -s), np.repeat(inner, 2), np.full(m, s)])
    ring_z = np.concatenate([r, np.tile([-s, s], 2*s - 1), r])   # boundary of the face
    nr = ring_y.size
    nx = np.concatenate([np.full(m*m, -s), np.repeat(inner, nr), np.full(m*m, s)])
    ny = np.concatenate([sq_y, np.tile(ring_y, 2*s - 1), sq_y])
    nz = np.concatenate([sq_z, np.tile(ring_z, 2*s - 1), sq_z])
    return np.stack([nx, ny, nz], axis=1).astype(np.int64)


def _last_shell(n, L, kcut, cut, zero_nyquist):
    m = n//2
    s_max = m - 1 if (n % 2 == 0 and zero_nyquist) else m
    if kcut is not None:
        kf = 2.0*np.pi/L
        if cut == "sharp":
            s_max = min(s_max, int(np.floor(kcut/kf*(1.0 + 1e-12))))
        elif cut == "gaussian":
            # exp(-k^2/(2 kcut^2)) < 3e-18 beyond 9 kcut; such shells are not generated
            s_max = min(s_max, int(np.ceil(9.0*kcut/kf)))
        else:
            raise ValueError(f"unknown cut {cut!r}")
    return s_max


def _mesh_coefficients(n, L, pk, seed, kcut=None, cut="sharp", zero_nyquist=False,
                       half=True):
    """numpy-normalised coefficients F (delta = ifftn(F), or irfftn(F) for half=True).

    The white noise is drawn shell by shell in max(|n_i|), s = 0, 1, 2, ..., in the
    lexicographic order of _shell(s), from one numpy Generator seeded with seed: the
    numbers given to a wavevector do not depend on n, so meshes of different resolution
    share all modes below the coarser Nyquist frequency. Hermitian symmetry: with W(v)
    the complex unit-variance noise of vector v, U(v) = [W(v) + W*(-v)]/sqrt(2), so
    U(-v) = U*(v) and <|U|^2> = 1. The coefficient of v is
    c(v) = sqrt(P(|k|)/L^3) cut(k) U(v), and the mesh field is the sum of c(v) exp(i k.x)
    sampled at the cell centres. For even n the Nyquist shell s = n/2 holds vectors that
    alias (n_i = +-n/2 are the same mesh mode); their coefficients are divided by
    sqrt(number of aliases) and summed, which makes every mesh mode, including those on the
    Nyquist planes, edges and corners, have <|delta_k|^2> = P/L^3, with the mesh field real.
    """
    N = n**3
    kf = 2.0*np.pi/L
    s_max = _last_shell(n, L, kcut, cut, zero_nyquist)
    # amplitude as a function of the integer |v|^2
    m2 = np.arange(3*s_max*s_max + 1)
    kk = kf*np.sqrt(m2)
    amp = np.zeros(m2.size)
    if m2.size > 1:
        pv = np.asarray(pk(kk[1:]), dtype=float)
        if np.any(pv < 0) or not np.all(np.isfinite(pv)):
            raise ValueError("pk must be finite and non-negative")
        a = np.sqrt(pv/L**3)
        if kcut is not None:
            if cut == "sharp":
                a = np.where(kk[1:] <= kcut, a, 0.0)
            else:
                a = a*np.exp(-0.5*(kk[1:]/kcut)**2)
        amp[1:] = a

    F = np.zeros((n, n, n//2 + 1) if half else (n, n, n), dtype=complex)
    rng = np.random.default_rng(seed)
    nyq = n//2 if n % 2 == 0 else None
    for s in range(s_max + 1):
        v = _shell(s)
        g = rng.standard_normal((len(v), 2))
        if s == 0:
            continue                                   # k = 0: delta_k = 0
        w = (g[:, 0] + 1j*g[:, 1])/_SQRT2
        u = (w + np.conj(w[::-1]))/_SQRT2
        val = N*amp[(v*v).sum(axis=1)]*u*np.exp(1j*np.pi*v.sum(axis=1)/n)
        if s == nyq:
            val = val/np.sqrt(2.0**(np.abs(v) == nyq).sum(axis=1))
            keep = (v[:, 2] >= 0) | (v[:, 2] == -nyq) if half else slice(None)
            idx = v[keep] % n
            np.add.at(F, (idx[:, 0], idx[:, 1], idx[:, 2]), val[keep])
        else:
            keep = v[:, 2] >= 0 if half else slice(None)
            idx = v[keep] % n
            F[idx[:, 0], idx[:, 1], idx[:, 2]] = val[keep]
    return F


def _phase(n, L, half=False):
    """exp(-i k.h/2) on the mesh (full layout, or the rfft layout for half=True)."""
    k1 = 2.0*np.pi*np.fft.fftfreq(n, d=L/n)
    kz = 2.0*np.pi*np.fft.rfftfreq(n, d=L/n) if half else k1
    h2 = 0.5*L/n
    p1 = np.exp(-1j*k1*h2)
    pz = np.exp(-1j*kz*h2)
    return p1[:, None, None]*p1[None, :, None]*pz[None, None, :]


def gaussian_field(n, L, pk, seed, kcut=None, cut="sharp", zero_nyquist=False):
    """Real Gaussian random field delta(x) on the n^3 cell-centred mesh of a periodic box
    of side L (Mpc/h), with <|delta_k|^2> = pk(|k|)/L^3 in the convention of the module
    docstring (delta_k = (1/N) sum delta(x) exp(-i k.x), x the cell centres).

    pk: callable, k in h/Mpc -> P(k) in (Mpc/h)^3 (vectorised; it is called once on the
    distinct |k| of the mesh). seed: int or numpy SeedSequence; the same seed gives the
    same field, and the same modes below the Nyquist frequency at any n (the noise is
    drawn shell by shell in max|n_i|, see _mesh_coefficients). The k = 0 mode is zero.
    kcut (h/Mpc): cut="sharp" removes the modes with |k| > kcut; cut="gaussian"
    multiplies delta_k by exp(-k^2/(2 kcut^2)) (the power by exp(-k^2/kcut^2)). The modes
    that survive a cut are those of the uncut field with the same seed.
    zero_nyquist: set the modes on the Nyquist planes (any |n_i| = n/2, even n) to zero.
    The first derivative of cosmo_id.Torus drops the Nyquist component of k, so the
    Zel'dovich displacement (zeldovich) reproduces these modes only in part; without
    them -div psi = delta exactly.
    """
    F = _mesh_coefficients(n, L, pk, seed, kcut, cut, zero_nyquist, half=True)
    return np.fft.irfftn(F, s=(n, n, n), axes=(0, 1, 2))


def gaussian_modes(n, L, pk, seed, kcut=None, cut="sharp", zero_nyquist=False):
    """The Fourier coefficients delta_k of gaussian_field (same arguments), on the full
    n^3 mesh in numpy fftfreq order, in the convention of the module docstring."""
    F = _mesh_coefficients(n, L, pk, seed, kcut, cut, zero_nyquist, half=False)
    return F/n**3*_phase(n, L)


def fourier_coefficients(delta, L):
    """delta_k = (1/N) sum_x delta(x) exp(-i k.x) of a mesh field (x the cell centres),
    full n^3 array in numpy fftfreq order."""
    n = delta.shape[0]
    return np.fft.fftn(delta)/delta.size*_phase(n, L)


# ---------------------------------------------------------------------------------------
# power spectrum
# ---------------------------------------------------------------------------------------
def _half_k(n, L):
    k1 = 2.0*np.pi*np.fft.fftfreq(n, d=L/n)
    kz = 2.0*np.pi*np.fft.rfftfreq(n, d=L/n)
    return k1, kz


def _half_weights(n):
    """Number of full-mesh modes each rfft entry stands for (1 on kz = 0 and on the
    kz = n/2 plane of an even mesh, 2 otherwise)."""
    w = np.full(n//2 + 1, 2.0)
    w[0] = 1.0
    if n % 2 == 0:
        w[-1] = 1.0
    return w


def bin_edges(n, L, nbins=None):
    """Edges in h/Mpc of the spherical bins of measure_power.
    nbins=None: width k_f = 2 pi/L, centred on k_f, 2 k_f, ..., (n//2) k_f (edges at
    half-integer multiples of k_f, so that no lattice |k| falls on an edge).
    nbins int: that many equal-width bins on [k_f/2, (n//2 + 1/2) k_f].
    nbins array: the edges themselves (h/Mpc, increasing)."""
    kf = 2.0*np.pi/L
    if nbins is None:
        return kf*(np.arange(n//2 + 1) + 0.5)
    if np.ndim(nbins) == 0:
        return np.linspace(0.5*kf, (n//2 + 0.5)*kf, int(nbins) + 1)
    return np.asarray(nbins, dtype=float)


def _binning(n, L, nbins):
    """Selection of the rfft entries that fall in a bin: (mask over the flattened rfft
    array, their |k|, weights, bin indices, number of bins)."""
    k1, kz = _half_k(n, L)
    kmag = np.sqrt(k1[:, None, None]**2 + k1[None, :, None]**2
                   + kz[None, None, :]**2).ravel()
    w = np.broadcast_to(_half_weights(n)[None, None, :], (n, n, n//2 + 1)).ravel()
    edges = bin_edges(n, L, nbins)
    idx = np.searchsorted(edges, kmag, side="right") - 1
    nb = len(edges) - 1
    ok = (idx >= 0) & (idx < nb) & (kmag > 0)
    return ok, kmag[ok], w[ok], idx[ok], nb


def bspline_window(n, L, degree):
    """Squared Fourier window of a B-spline cloud of the given degree (0 NGP, 1 CIC,
    2 TSC, 3 PCS) on the rfft layout: prod_i sinc(k_i h/2)^(2(degree + 1))."""
    k1, kz = _half_k(n, L)
    h = L/n
    s1 = np.sinc(k1*h/(2.0*np.pi))            # np.sinc(x) = sin(pi x)/(pi x)
    sz = np.sinc(kz*h/(2.0*np.pi))
    w = s1[:, None, None]*s1[None, :, None]*sz[None, None, :]
    return w**(2*(degree + 1))


def measure_power(delta, L, nbins=None, deconvolve=None):
    """Spherically averaged power spectrum of a cubic mesh field, convention of the
    module docstring: each mode contributes L^3 |delta_k|^2.

    Returns (k, P, nmodes): the mean |k| of the modes in each bin (h/Mpc), the mean of
    L^3 |delta_k|^2 over them ((Mpc/h)^3), and the number of mesh modes per bin (k and
    -k counted separately, k = 0 excluded). Bins: see bin_edges; empty bins give NaN.
    deconvolve = 1, 2 or 3: divide each mode by the squared window of a B-spline cloud of
    that degree (CIC, TSC, PCS), prod_i sinc(k_i h/2)^(2(p+1)), for fields deposited from
    particles. This does not remove aliasing or shot noise.
    """
    n = delta.shape[0]
    F = np.fft.rfftn(delta)/delta.size
    p = (F.real**2 + F.imag**2)*L**3
    if deconvolve:
        p = p/bspline_window(n, L, int(deconvolve))
    ok, kmag, w, idx, nb = _binning(n, L, nbins)
    pv = p.ravel()[ok]
    cnt = np.bincount(idx, weights=w, minlength=nb)
    ks = np.bincount(idx, weights=w*kmag, minlength=nb)
    ps = np.bincount(idx, weights=w*pv, minlength=nb)
    with np.errstate(invalid="ignore", divide="ignore"):
        return ks/cnt, ps/cnt, np.rint(cnt).astype(np.int64)


def expected_power(n, L, pk, nbins=None):
    """Prediction for measure_power of a Gaussian field with spectrum pk on this mesh and
    binning: returns (k, Pbar, sigma, nmodes) with Pbar the mode-weighted mean of
    pk(|k|) over the modes of each bin and sigma its sample-variance error,
    sigma^2 = 2 sum_modes P^2 / nmodes^2 (k and -k are one independent complex mode;
    self-conjugate modes have one real degree of freedom; both give this formula)."""
    ok, kmag, w, idx, nb = _binning(n, L, nbins)
    pv = np.asarray(pk(kmag), dtype=float)
    cnt = np.bincount(idx, weights=w, minlength=nb)
    ks = np.bincount(idx, weights=w*kmag, minlength=nb)
    ps = np.bincount(idx, weights=w*pv, minlength=nb)
    p2 = np.bincount(idx, weights=w*pv*pv, minlength=nb)
    with np.errstate(invalid="ignore", divide="ignore"):
        return ks/cnt, ps/cnt, np.sqrt(2.0*p2)/cnt, np.rint(cnt).astype(np.int64)


# ---------------------------------------------------------------------------------------
# Zel'dovich displacement
# ---------------------------------------------------------------------------------------
def _inverse_laplacian_modes(delta, L):
    tor = Torus(delta.shape[0], L)
    k2 = tor.k2.copy()
    k2[0, 0, 0] = 1.0
    G = tor.fft(delta)/k2                    # -lap^-1 delta in Fourier space
    G[0, 0, 0] = 0.0
    return tor, G


def zeldovich(delta, L):
    """Zel'dovich displacement psi_i = -d_i lap^-1 delta (Mpc/h for L in Mpc/h), three
    mesh arrays, spectral with the derivatives of cosmo_id.Torus (|k|^2 in lap^-1, and
    the first derivative of a Nyquist component is zero): psi_k = i kd_i delta_k / k^2,
    with kd_i = k_i except kd_i = 0 for n_i = n/2. Particles at q + psi(q) then have the
    linear density contrast -div psi = delta for every mode off the Nyquist planes; a
    mode on them is reproduced only by the fraction (kd^2/k^2) of its non-Nyquist
    components (none for the axis, edge and corner Nyquist modes). Generate the field
    with gaussian_field(..., zero_nyquist=True) to have -div psi = delta exactly.
    """
    tor, G = _inverse_laplacian_modes(delta, L)
    return [tor.ifft(1j*kd*G) for kd in tor.kd]


def displacement_jacobian(delta, L):
    """det(delta_ij + d_j psi_i) on the mesh for the Zel'dovich displacement of delta
    (zeldovich), with d_j psi_i = -d_i d_j lap^-1 delta spectral (Torus derivatives).
    The density of the displaced particles is (1 + delta_ZA) = 1/J at x = q + psi(q);
    for a single plane wave below the Nyquist frequency J = 1 - delta exactly (the
    displacement gradient has rank one)."""
    tor, G = _inverse_laplacian_modes(delta, L)
    kd = tor.kd
    d = {}
    for i in range(3):
        for j in range(i, 3):
            d[i, j] = tor.ifft(-kd[i]*kd[j]*G)
    a11, a22, a33 = 1.0 + d[0, 0], 1.0 + d[1, 1], 1.0 + d[2, 2]
    a12, a13, a23 = d[0, 1], d[0, 2], d[1, 2]
    return (a11*(a22*a33 - a23*a23) - a12*(a12*a33 - a23*a13)
            + a13*(a12*a23 - a22*a13))
