"""Reference calculation for the coloured noise of the stochastic sources (E-pre-4).

Implements NOISE_SPEC.md: the mode set, the keys, the amplitudes, the transfer functions
of the unit test (section 8), the synthesis of the mesh field from the modes, the
analysis of a mesh field into modes, and the expected statistics with their variances.

Conventions (NOISE_SPEC.md, section 2): periodic box [x0, x0 + L)^3, N^3 cells,
h = L/N, cell centres x_j = x0 + (j + 1/2) h, arrays indexed [i, j, k] = (x, y, z);
xi(x) = sum_n xi_n exp(i k_n.(x - x0)), k_n = (2 pi / L) n;
xi_n = (1/N^3) sum_x xi(x) exp(-i k_n.(x - x0)); <|xi_n|^2> = P(k_n) / L^3.
"""
import numpy as np

try:
    from philox_ref import mode_alpha
except ImportError:                         # imported as a package
    from .philox_ref import mode_alpha

# component -> degree of freedom of the unit test (NOISE_SPEC.md, section 8)
TEST_DOF = {0: 0, 1: 0, 2: 1, 3: 0}


class Lattice:
    """Modes of one hemisphere with 0 < n.n <= nmax2 on an N^3 mesh of side L.

    Hemisphere H (the half space of E-pre-2, codebase/ref/synth.py:half_space):
    n_x > 0, or n_x = 0 and n_y > 0, or n_x = n_y = 0 and n_z > 0.
    Order: n_z slowest, n_x fastest (consecutive entities along rows)."""

    def __init__(self, N, L, nmax2):
        self.N, self.L, self.nmax2 = int(N), float(L), int(nmax2)
        nmax = int(np.floor(np.sqrt(self.nmax2) + 1e-12))
        if 2 * nmax >= self.N:
            raise ValueError("the cut reaches the Nyquist plane: need 2 n_max < N")
        r = np.arange(-nmax, nmax + 1)
        nz, ny, nx = np.meshgrid(r, r, r, indexing="ij")
        n = np.stack([nx.ravel(), ny.ravel(), nz.ravel()], axis=1).astype(np.int64)
        n2 = (n * n).sum(axis=1)
        hemi = (n[:, 0] > 0) | ((n[:, 0] == 0) & (n[:, 1] > 0)) | \
               ((n[:, 0] == 0) & (n[:, 1] == 0) & (n[:, 2] > 0))
        keep = hemi & (n2 >= 1) & (n2 <= self.nmax2)
        self.n = n[keep]
        self.n2 = n2[keep]
        self.M = self.n.shape[0]
        self.kf = 2.0 * np.pi / self.L
        self.q = np.sqrt(self.n2.astype(np.float64))          # |k| / k_f
        self.kmag = self.kf * self.q
        self.mu2 = self.n[:, 2].astype(np.float64)**2 / self.n2   # (k_z / k)^2
        self.idx = self.n % self.N
        self.idx_m = (-self.n) % self.N
        self.phase = np.exp(1j * np.pi * self.n.sum(axis=1) / self.N)  # cell-centre shift

    def in_set_mask(self):
        """Boolean N^3 array: True on the modes of the set and their mirrors."""
        m = np.zeros((self.N,) * 3, dtype=bool)
        m[tuple(self.idx.T)] = True
        m[tuple(self.idx_m.T)] = True
        return m


# --------------------------------------------------------------------- amplitudes
def amplitudes(lat, seed, dof, epoch, scheme="hemisphere", log="agm"):
    """Random amplitudes of the modes of `lat`.
    hemisphere: alpha_n (one complex unit Gaussian per mode of H); returns (alpha, None).
    pair: independent beta_n and beta_{-n} (n in H); returns (beta_plus, beta_minus)."""
    a = mode_alpha(seed, dof, epoch, lat.n, log)
    if scheme == "hemisphere":
        return a, None
    if scheme == "pair":
        return a, mode_alpha(seed, dof, epoch, -lat.n, log)
    raise ValueError(f"unknown amplitude scheme {scheme!r}")


def coefficients(G, amp_pair, scheme="hemisphere"):
    """xi_n for n in H from the transfer G_n and the amplitudes (NOISE_SPEC eq. 4.2)."""
    a, b = amp_pair
    if scheme == "hemisphere":
        return G * a
    # pair: G_{-n} = G_n for every transfer of the specification (even in n)
    return (G * a + np.conj(G) * np.conj(b)) / np.sqrt(2.0)


# ---------------------------------------------------------------------- transforms
def synthesise(lat, c, positions="centre"):
    """Real mesh field [i, j, k] from the coefficients c_n (n in H). Returns the field
    and the largest imaginary part (a check of the Hermitian completion).
    positions='centre': x - x0 = (j + 1/2) h (the specification); 'corner': j h (a
    deliberate error used as a negative control)."""
    N = lat.N
    ph = lat.phase if positions == "centre" else np.ones(lat.M)
    F = np.zeros((N, N, N), dtype=complex)
    F[tuple(lat.idx.T)] = c * ph
    F[tuple(lat.idx_m.T)] = np.conj(c * ph)
    f = np.fft.ifftn(F) * N**3
    return f.real.copy(), float(np.abs(f.imag).max())


def analyse(lat, field):
    """Coefficients xi_n (n in H) of a mesh field, the full normalised transform (for the
    band-limit test), in the convention of the module docstring."""
    N = lat.N
    Fh = np.fft.fftn(field) / N**3
    c = Fh[tuple(lat.idx.T)] * np.conj(lat.phase)
    return c, Fh


# ------------------------------------------------------- unit-test transfer (sec. 8)
def window(lat, t, p):
    """W_k(t) of the unit test: k_sigma(t) = ksigma0 k_f exp(hubble t)."""
    ks_over_kf = p["ksigma0"] * np.exp(p["hubble"] * t)
    if p["window"] == "tanh":
        return 0.5 * (1.0 + np.tanh(p["sharpness"] * np.log(ks_over_kf / lat.q)))
    if p["window"] == "heaviside":
        return (lat.q <= ks_over_kf).astype(np.float64)
    raise ValueError(f"unknown window {p['window']!r}")


def window_rate(lat, t, p):
    """dW_k/dt of the tanh window: (s/2) sech^2(s ln(k_sigma/k)) hubble."""
    if p["window"] != "tanh":
        raise ValueError("the rate form needs the tanh window")
    x = p["sharpness"] * np.log(p["ksigma0"] * np.exp(p["hubble"] * t) / lat.q)
    return 0.5 * p["sharpness"] * p["hubble"] / np.cosh(x)**2


def base_amplitude(lat, p):
    """amp q^{-3/2} L^{-3/2}: scale-invariant colouring (Delta flat)."""
    return p["amp"] * lat.q**-1.5 * lat.L**-1.5


def component_factor(lat, comp, p):
    """Factor of component c relative to component 0 (NOISE_SPEC.md, section 8)."""
    if comp in (0, 2):
        return np.ones(lat.M, dtype=complex)
    if comp == 1:
        return np.full(lat.M, np.exp(1j * p["phase1"]))
    if comp == 3:
        return (lat.mu2 - 1.0 / 3.0).astype(complex)
    raise ValueError(f"no component {comp}")


def out_time(cycle, p):
    return p.get("t0", 0.0) + cycle * p["dt"]


def transfer(lat, comp, cycle, p):
    """G^c_n of the field written at `cycle`.
    frozen: the rate at the output time, amp q^-3/2 L^-3/2 dW/dt (t_cycle);
    markov: the increment of the step ending at the output time,
            amp q^-3/2 L^-3/2 sqrt(W(t_cycle) - W(t_cycle - dt))."""
    t = out_time(cycle, p)
    if p["scheme"] == "frozen":
        g = base_amplitude(lat, p) * window_rate(lat, t, p)
    else:
        dW = window(lat, t, p) - window(lat, t - p["dt"], p)
        g = base_amplitude(lat, p) * np.sqrt(np.where(dW > 0.0, dW, 0.0))
    return g * component_factor(lat, comp, p)


def acc_transfer(lat, cycle, p):
    """Frozen scheme: G of the integrated field a(t) = int_0^t c0 dt' (telescoped,
    amp q^-3/2 L^-3/2 [W(t) - W(t0)]); the code's integrator reproduces it to its
    truncation error. Markov: the standard deviation of the summed increments."""
    dW = window(lat, out_time(cycle, p), p) - window(lat, p.get("t0", 0.0), p)
    dW = np.where(dW > 0.0, dW, 0.0)
    if p["scheme"] == "frozen":
        return (base_amplitude(lat, p) * dW).astype(complex)
    return (base_amplitude(lat, p) * np.sqrt(dW)).astype(complex)


def epoch_of(cycle, p):
    """Step word of the amplitudes of the field written at `cycle`: 0 in the frozen
    scheme, `cycle` (the step from cycle - 1 to cycle) in the Markov scheme."""
    return 0 if p["scheme"] == "frozen" else int(cycle)


def reference_outputs(lat, p, cycles, comps=(0, 1, 2, 3), log="agm", with_acc=True):
    """Coefficients (n in H) of every component at every output cycle, and of the
    integrated field of component 0, as the code must produce them."""
    out = {}
    cache = {}

    def amps(dof, ep):
        if (dof, ep) not in cache:
            cache[(dof, ep)] = amplitudes(lat, p["seed"], dof, ep, p["amplitudes"], log)
        return cache[(dof, ep)]

    for cyc in cycles:
        for c in comps:
            out[(f"stoch_c{c}", cyc)] = coefficients(
                transfer(lat, c, cyc, p), amps(TEST_DOF[c], epoch_of(cyc, p)),
                p["amplitudes"])
    if with_acc:
        if p["scheme"] == "frozen":
            for cyc in cycles:
                out[("stoch_acc0", cyc)] = coefficients(acc_transfer(lat, cyc, p),
                                                        amps(0, 0), p["amplitudes"])
        else:
            acc = np.zeros(lat.M, dtype=complex)
            for m in range(1, max(cycles) + 1):
                G = transfer(lat, 0, m, p)
                if np.any(G != 0):
                    acc = acc + coefficients(G, amps(0, m), p["amplitudes"])
                if m not in cycles:
                    cache.pop((0, m), None)          # keep memory bounded
                else:
                    out[("stoch_acc0", m)] = acc.copy()
    return out


# ------------------------------------------------------------- expected statistics
def expected_corr(lat, G, lags):
    """C(r) = sum_H 2 |G|^2 cos(k.r) and the variance of the one-realisation estimator
    sum_H 2 |xi_n|^2 cos(k.r) (|alpha|^2 ~ Exp(1)): sum_H 4 |G|^4 cos^2(k.r).
    lags: (m, 3) integer cell offsets."""
    h = lat.L / lat.N
    kr = (lat.kf * lat.n.astype(np.float64)) @ (np.asarray(lags, float).T * h)
    cos = np.cos(kr)
    g2 = np.abs(G)**2
    return (2.0 * g2[:, None] * cos).sum(axis=0), (4.0 * g2[:, None]**2 * cos**2).sum(axis=0)


def measured_corr(field, lags):
    """(1/N^3) sum_x xi(x) xi(x + r) for integer cell offsets r (periodic)."""
    out = np.empty(len(lags))
    for i, r in enumerate(lags):
        out[i] = np.mean(field * np.roll(field, shift=tuple(-np.asarray(r)), axis=(0, 1, 2)))
    return out


def standard_lags(N):
    """Lags along x, y, z and the (1,1,1) diagonal, 0 to N/2 cells."""
    lags = [(0, 0, 0)]
    for d in range(1, N // 2 + 1):
        lags += [(d, 0, 0), (0, d, 0), (0, 0, d), (d, d, d)]
    return np.array(lags, dtype=np.int64)


def default_params(**kw):
    """Parameters of the unit test of NOISE_SPEC.md, section 8 (base case)."""
    p = dict(seed=20261115, scheme="frozen", amplitudes="hemisphere", N=64, L=2.5,
             x0=-1.25, nmax2=256, window="tanh", sharpness=5.0, ksigma0=0.9, hubble=1.0,
             amp=1.0, phase1=np.pi / 3.0, dt=0.01, t0=0.0, nsteps=400,
             cycles=(100, 101, 200, 300))
    p.update(kw)
    return p
