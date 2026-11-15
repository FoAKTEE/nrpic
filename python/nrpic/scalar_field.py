"""Reference solutions and readers for the scalar-field module of AthenaK
(athenak/src/scalar_field/, interface tracks/core/interfaces/scalar_field.md).

Nothing here is a simulation code: readers of the module's output, the ordinary
differential equations of a homogeneous field (Friedmann and Klein-Gordon), the symbols of
the finite differences of athenak/src/utils/finite_diff.hpp, and the twin of the
stochastic sources (mode set, amplitudes, shell factors) built on nrpic.rng.

Conventions as in the code: G = c = 1, K = -3H, Pi = n.d phi (alpha = 1: dot phi),
T_munu = d phi d phi - g (d phi.d phi/2 + V).
"""
import struct

import numpy as np

from . import rng

DUMP_VARS = ["phi", "Pi", "chi", "K", "alpha", "H", "Mx", "My", "Mz", "E"]


# ----------------------------------------------------------------------------- readers
def read_history(fname):
    """Columns of <basename>.sf.hst as a dict of arrays (names of the header line)."""
    names = ["time", "cycle", "phi", "Pi", "K", "chi", "alpha", "rms_phi", "rms_Pi", "E",
             "H_l1", "H_rms", "H_max", "M_rms", "M_max", "Theta_rms", "H_norm",
             "lock_time", "phi_b", "Pi_b", "ln_a"]
    d = np.atleast_2d(np.loadtxt(fname))
    return {n: d[:, i] for i, n in enumerate(names)}


CON_HIST_VARS = ["time", "cycle", "efolds", "H_ratio", "H_ratio_max", "H_ratio_of_means",
                 "M_ratio", "M_ratio_max", "M_ratio_of_means", "H_mag", "M_mag", "H_l1",
                 "M_l1", "H_rms", "M_rms", "M_bssn_adm", "phi", "Pi", "K", "alpha"]


def read_con_history(fname):
    """Columns of <basename>.sf.con.hst (constraints relative to the magnitudes [H], [M]
    of arXiv:2512.14649; scalar_field_diag.cpp) as a dict of arrays."""
    d = np.atleast_2d(np.loadtxt(fname))
    return {n: d[:, i] for i, n in enumerate(CON_HIST_VARS)}


def read_dump(fname):
    """A dump <basename>.sf.NNNNN.dump (layouts NRSFDMP1 and NRSFDMP2).  Returns a dict with time, cycle, the list of
    MeshBlocks (level, lx, extent, data[var][i, j, k]) and, when all MeshBlocks are on
    the root level, the fields assembled on the whole mesh, fields[name][i, j, k] with
    (i, j, k) = (x, y, z); the stochastic fields are named noise0, noise1, ..."""
    with open(fname, "rb") as fp:
        magic = fp.read(8)
        if magic not in (b"NRSFDMP1", b"NRSFDMP2"):
            raise ValueError(f"{fname}: bad magic")
        nmb, nx1, nx2, nx3, nvar, cycle, nnoise = struct.unpack("<7q", fp.read(56))
        (time,) = struct.unpack("<d", fp.read(8))
        if magic == b"NRSFDMP1":
            names = DUMP_VARS + [f"noise{n}" for n in range(nnoise)]
        else:     # extended layout (scalar_field_diag.cpp): the names are in the file
            names = [fp.read(16).rstrip(b"\0").decode() for _ in range(nvar)]
        blocks = []
        for _ in range(nmb):
            lev, lx1, lx2, lx3 = struct.unpack("<4q", fp.read(32))
            ext = struct.unpack("<6d", fp.read(48))
            raw = np.fromfile(fp, dtype="<f8", count=nvar*nx1*nx2*nx3)
            raw = raw.reshape(nvar, nx3, nx2, nx1).transpose(0, 3, 2, 1)   # [v, i, j, k]
            blocks.append(dict(level=lev, lx=(lx1, lx2, lx3), extent=ext,
                               data={n: raw[v] for v, n in enumerate(names)}))
    out = dict(time=time, cycle=cycle, names=names, blocks=blocks, nx=(nx1, nx2, nx3))
    if all(b["level"] == 0 for b in blocks):
        n1 = (max(b["lx"][0] for b in blocks) + 1)*nx1
        n2 = (max(b["lx"][1] for b in blocks) + 1)*nx2
        n3 = (max(b["lx"][2] for b in blocks) + 1)*nx3
        fields = {n: np.empty((n1, n2, n3)) for n in names}
        for b in blocks:
            i0, j0, k0 = b["lx"][0]*nx1, b["lx"][1]*nx2, b["lx"][2]*nx3
            for n in names:
                fields[n][i0:i0+nx1, j0:j0+nx2, k0:k0+nx3] = b["data"][n]
        out["fields"] = fields
    return out


def read_modes(fname):
    """The text record <basename>.sf.NNNNN.modes written next to a dump: (header dict,
    array of rows n2, Re R, Im R, Re dR, Im dR, Re shell, Im shell)."""
    head = {}
    with open(fname) as fp:
        for line in fp:
            if not line.startswith("#"):
                break
            tok = line[1:].split()
            for a, b in zip(tok[:-1], tok[1:]):
                try:
                    head[a] = float(b)
                except ValueError:
                    pass
    return head, np.atleast_2d(np.loadtxt(fname))


# -------------------------------------------------------------------------- potentials
def potential(kind, **p):
    """V(phi) and V'(phi) of the kinds of the code: quadratic (mass), quartic (mass,
    lam), plateau (v0, mu), inflection (lam, vev)."""
    off = p.get("v_offset", 0.0)
    if kind == "quadratic":
        m2 = p["mass"]**2
        return (lambda x: 0.5*m2*x*x + off), (lambda x: m2*x)
    if kind == "quartic":
        m2, lam = p.get("mass", 0.0)**2, p["lam"]
        return (lambda x: 0.5*m2*x*x + 0.25*lam*x**4 + off), (lambda x: m2*x + lam*x**3)
    if kind == "plateau":
        v0, mu = p["v0"], p["mu"]
        return ((lambda x: v0*(1.0 - np.exp(-x/mu))**2 + off),
                (lambda x: 2.0*v0*(1.0 - np.exp(-x/mu))*np.exp(-x/mu)/mu))
    if kind == "inflection":
        lam, vv = p["lam"], p["vev"]
        c, s2 = lam*vv**4/3.0, np.sqrt(2.0)

        def v(x):
            pp = 3.0*x*x + 2.0*s2*x*vv + 6.0*vv*vv
            qq = 3.0*x*x + 2.0*vv*vv
            return c*x*x*pp/qq**2 + off

        def dv(x):
            pp = 3.0*x*x + 2.0*s2*x*vv + 6.0*vv*vv
            qq = 3.0*x*x + 2.0*vv*vv
            return c*((2.0*x*pp + x*x*(6.0*x + 2.0*s2*vv))/qq**2 - 12.0*x**3*pp/qq**3)
        return v, dv
    raise ValueError(kind)


# ------------------------------------------------------------- homogeneous background
def friedmann(v, dv, phi0, pi0, t_eval, gauge="geodesic", rtol=1e-13, atol=1e-15):
    """Homogeneous field and flat universe: d phi/dt = alpha Pi, d Pi/dt = alpha (-3 H Pi
    - V'), d ln a/dt = alpha H, H^2 = (8 pi/3)(Pi^2/2 + V), with alpha = 1 (gauge
    'geodesic') or d alpha/dt = alpha^2 H (gauge 'conformal': the lapse condition
    d_t alpha = -(1/3) alpha^2 K of cosmo/README.md, alpha = a for alpha(0) = a(0) = 1).
    Returns dict of arrays at t_eval: phi, Pi, ln_a, alpha, H, K, chi."""
    from scipy.integrate import solve_ivp

    def hub(phi, pi):
        return np.sqrt((8.0*np.pi/3.0)*(0.5*pi*pi + v(phi)))

    def rhs(t, y):
        phi, pi, lna, alp = y
        h = hub(phi, pi)
        dalp = alp*alp*h if gauge == "conformal" else 0.0
        return [alp*pi, alp*(-3.0*h*pi - dv(phi)), alp*h, dalp]

    t_eval = np.atleast_1d(np.asarray(t_eval, dtype=float))
    sol = solve_ivp(rhs, (0.0, max(t_eval[-1], 1e-300)), [phi0, pi0, 0.0, 1.0],
                    method="DOP853", t_eval=t_eval, rtol=rtol, atol=atol)
    phi, pi, lna, alp = sol.y
    h = hub(phi, pi)
    return dict(time=sol.t, phi=phi, Pi=pi, ln_a=lna, alpha=alp, H=h, K=-3.0*h,
                chi=np.exp(-2.0*lna))


def flat_oscillator(dv, phi0, pi0, t_eval, rtol=1e-13, atol=1e-15):
    """Homogeneous field on flat spacetime: ddot phi = -V'(phi)."""
    from scipy.integrate import solve_ivp
    t_eval = np.atleast_1d(np.asarray(t_eval, dtype=float))
    sol = solve_ivp(lambda t, y: [y[1], -dv(y[0])], (0.0, t_eval[-1]), [phi0, pi0],
                    method="DOP853", t_eval=t_eval, rtol=rtol, atol=atol)
    return sol.y[0], sol.y[1]


# ---------------------------------------------------------- finite-difference symbols
D1_COEF = {2: [1/2], 3: [2/3, -1/12], 4: [3/4, -3/20, 1/60]}
D2_COEF = {2: [-2.0, 1.0], 3: [-5/2, 4/3, -1/12], 4: [-49/18, 3/2, -3/20, 1/90]}


def d1_symbol(kh, nghost=4):
    """q h with D exp(i k x) = i q exp(i k x) for the centred first difference."""
    return sum(2.0*a*np.sin((m + 1)*kh) for m, a in enumerate(D1_COEF[nghost]))


def d2_symbol(kh, nghost=4):
    """kap2 with Dxx exp(i k x) = -(kap2/h^2) exp(i k x) for the centred second
    difference (kap2 -> (k h)^2)."""
    c = D2_COEF[nghost]
    return -(c[0] + sum(2.0*a*np.cos((m + 1)*kh) for m, a in enumerate(c[1:])))


def diss_rate(kh, h, diss, nghost=4):
    """Damping rate of exp(i k x) by the Kreiss-Oliger term of one direction:
    diss 2^(-2 nghost) (2 sin(kh/2))^(2 nghost) / h."""
    return diss*2.0**(-2*nghost)*(2.0*np.sin(0.5*kh))**(2*nghost)/h


# ------------------------------------------------------------------- stochastic twin
STREAM_MODE_FLAG = 1 << 16
OFFSET = 1 << 20


def mode_set(nmax2):
    """Wave vectors of the hemisphere (n_x > 0, or n_x = 0 and n_y > 0, or n_x = n_y = 0
    and n_z > 0) with 0 < |n|^2 <= nmax2, in the order of the code: by n_x, n_y, n_z."""
    nmax = int(np.floor(np.sqrt(nmax2) + 1e-9))
    r = np.arange(-nmax, nmax + 1)
    nx, ny, nz = np.meshgrid(np.arange(0, nmax + 1), r, r, indexing="ij")
    n = np.stack([nx.ravel(), ny.ravel(), nz.ravel()], axis=1).astype(np.int64)
    n2 = (n*n).sum(axis=1)
    hemi = (n[:, 0] > 0) | ((n[:, 0] == 0) & (n[:, 1] > 0)) | \
           ((n[:, 0] == 0) & (n[:, 1] == 0) & (n[:, 2] > 0))
    keep = hemi & (n2 >= 1) & (n2 <= nmax2)
    return n[keep], n2[keep]


def mode_alpha(seed, dof, epoch, n):
    """alpha_n = (z1 + i z2)/sqrt(2) with the keys of the code."""
    ent = rng.cell_entity(n[:, 0] + OFFSET, n[:, 1] + OFFSET, n[:, 2] + OFFSET)
    z1, z2 = rng.normal2(seed=seed, stream=rng.stream(rng.STREAM_STOCHASTIC,
                                                      STREAM_MODE_FLAG | dof),
                         entity=ent, step=epoch, draw=0)
    return (np.asarray(z1) + 1j*np.asarray(z2))/np.sqrt(2.0)


def analyse(field, n):
    """Coefficients xi_n of a mesh field [i, j, k] for the wave vectors n (M, 3), in the
    convention xi(x) = sum_n xi_n exp(i k_n.(x - x0)) at the cell centres
    x - x0 = (j + 1/2) h; also the full transform (for the band limit)."""
    nn = field.shape[0]
    fh = np.fft.fftn(field)/field.size
    ph = np.exp(-1j*np.pi*n.sum(axis=1)/nn)
    c = fh[n[:, 0] % nn, n[:, 1] % nn, n[:, 2] % nn]*ph
    return c, fh


def synthesise(c, n, nn):
    """Mesh field [i, j, k] from the coefficients c_n of the hemisphere (numpy FFT)."""
    f = np.zeros((nn, nn, nn), dtype=complex)
    ph = np.exp(1j*np.pi*n.sum(axis=1)/nn)
    f[n[:, 0] % nn, n[:, 1] % nn, n[:, 2] % nn] = c*ph
    f[(-n[:, 0]) % nn, (-n[:, 1]) % nn, (-n[:, 2]) % nn] = np.conj(c*ph)
    return np.fft.ifftn(f).real*nn**3


def power_shell_factor(n2, t0, t1, length, amp=1.0, tilt=0.0, ksigma0=1.0, hubble=1.0,
                       tref=0.0, sharpness=5.0, window="tanh", scheme="frozen"):
    """Shell factor of the increment of the step from t0 to t1 of the power model."""
    q = np.sqrt(np.asarray(n2, dtype=float))
    ks0 = ksigma0*np.exp(hubble*(t0 - tref))
    ks1 = ksigma0*np.exp(hubble*(t1 - tref))
    if window == "tanh":
        # tanh x1 - tanh x0 = sinh(x1 - x0)/(cosh x1 cosh x0), without cancellation
        x0, x1 = sharpness*np.log(ks0/q), sharpness*np.log(ks1/q)
        dw = 0.5*np.sinh(sharpness*hubble*(t1 - t0))/(np.cosh(x1)*np.cosh(x0))
    else:
        dw = (q <= ks1).astype(float) - (q <= ks0).astype(float)
    dw = np.where(dw > 0.0, dw, 0.0)
    base = amp*q**(0.5*(tilt - 3.0))*length**-1.5
    return base*(dw if scheme == "frozen" else np.sqrt(dw))


def ms_reference(v, dv, phi0, pi0, n2, r0, dr0, length, t_eval, sigma=1.0, sharpness=5.0,
                 rtol=1e-12, atol=1e-30):
    """Level-0 Mukhanov-Sasaki model in geodesic slicing (alpha_b = 1): background and
    mode functions R_q integrated from t = 0 (a = 1) with SciPy, and the shell factor
    S_R L^(-3/2) at the times t_eval.  r0, dr0: complex R and dR/dt of every shell at
    t = 0.  Returns dict with phi, Pi, ln_a, H, eps1, eps2 (per time) and R, dR, shell
    (time, shell), complex."""
    from scipy.integrate import solve_ivp
    n2 = np.asarray(n2, dtype=float)
    ns = n2.size
    k = 2.0*np.pi*np.sqrt(n2)/length

    def bg(phi, pi):
        h = np.sqrt((8.0*np.pi/3.0)*(0.5*pi*pi + v(phi)))
        e1 = 4.0*np.pi*pi*pi/(h*h)
        e2 = 6.0 + 2.0*dv(phi)/(h*pi) - 2.0*e1
        return h, e1, e2

    def rhs(t, y):
        phi, pi, lna = y[:3]
        h, e1, e2 = bg(phi, pi)
        r = y[3:3+2*ns]
        d = y[3+2*ns:]
        k2a2 = np.tile(k*k*np.exp(-2.0*lna), 2)
        return np.concatenate([[pi, -3.0*h*pi - dv(phi), h], d,
                               -(3.0 - e2)*h*d - k2a2*r])

    r0, dr0 = np.asarray(r0, dtype=complex), np.asarray(dr0, dtype=complex)
    y0 = np.concatenate([[phi0, pi0, 0.0], r0.real, r0.imag, dr0.real, dr0.imag])
    t_eval = np.atleast_1d(np.asarray(t_eval, dtype=float))
    sol = solve_ivp(rhs, (0.0, max(t_eval[-1], 1e-300)), y0, method="DOP853",
                    t_eval=t_eval, rtol=rtol, atol=atol)
    phi, pi, lna = sol.y[:3]
    h, e1, e2 = bg(phi, pi)
    r = (sol.y[3:3+ns] + 1j*sol.y[3+ns:3+2*ns]).T
    d = (sol.y[3+2*ns:3+3*ns] + 1j*sol.y[3+3*ns:]).T
    x = sharpness*np.log(sigma*np.exp(lna)[:, None]*h[:, None]/k[None, :])
    sech2 = 1.0/np.cosh(x)**2
    dl = (h*(1.0 - e1))[:, None]
    d2l = (h*h*e1*(e2 - 1.0 + e1))[:, None]
    w1 = 0.5*sharpness*sech2*dl
    w2 = 0.5*sech2*(sharpness*d2l - 2.0*sharpness**2*np.tanh(x)*dl*dl)
    shell = length**-1.5*(r*w2 + (2.0*d + ((3.0 - e2)*h)[:, None]*r)*w1)
    return dict(time=sol.t, phi=phi, Pi=pi, ln_a=lna, H=h, eps1=e1, eps2=e2, R=r, dR=d,
                shell=shell)
