"""verifier_c18: own readers, TT projection, mode amplitudes, junk reference, spatial-gauge piece.

Written for this package from the file formats (docs/FORMATS.md section "Mesh binary output",
athenak/src/outputs/restart.cpp lines 205-300) and the note's definitions (note/main.tex
Eqs. (2)-(9)); nothing is imported from the track's analysis code.

Conventions
- Uniform periodic mesh of n^3 cells, side L, cell centres x = xmin + (i + 1/2) dx; arrays are
  indexed [k, j, i] (z, y, x), as written by AthenaK (first index fastest).
- Mode amplitude of a real field f = c cos(K.x) + s sin(K.x): amp(f, m) = c - i s, computed as
  (2 / Ncell) sum_x f(x) exp(-i K.x) with the actual cell-centre coordinates.
- Polarizations at K1 = (k, k, 0): e+ = u u - z z, ex = u z + z u, u = (1, -1, 0)/sqrt2; at
  K2 = (k, -k, 0): u = (1, 1, 0)/sqrt2; h_+ = (1/2) e+_ij h_ij (note Sec. II B).
"""
import os
import re

import numpy as np

Z4C = ["chi", "gxx", "gxy", "gxz", "gyy", "gyz", "gzz", "Khat", "Axx", "Axy", "Axz", "Ayy",
       "Ayz", "Azz", "Gamx", "Gamy", "Gamz", "Theta", "alpha", "betax", "betay", "betaz"]
SYM = [(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)]


# ----------------------------------------------------------------------------- readers
def read_bin(path, want=None):
    """Mesh bin dump (single or double precision). Returns dict with 'time', 'cycle', 'n',
    'xmin', 'L', 'dx' and one [k, j, i] float64 array per variable (prefix z4c_ stripped)."""
    with open(path, "rb") as f:
        raw = f.read()
    head_end = raw.index(b"header offset=")
    line_end = raw.index(b"\n", head_end)
    text = raw[:line_end].decode()
    hoff = int(re.search(r"header offset=(\d+)", text).group(1))
    t = float(re.search(r"time=([-+0-9.eE]+)", text).group(1))
    cyc = int(re.search(r"cycle=(\d+)", text).group(1))
    vsize = int(re.search(r"size of variable=(\d+)", text).group(1))
    lsize = int(re.search(r"size of location=(\d+)", text).group(1))
    names = re.search(r"variables:(.*)", text).group(1).split()
    names = [v[4:] if v.startswith("z4c_") else v for v in names]
    pos = line_end + 1 + hoff
    dt = np.float64 if vsize == 8 else np.float32
    blocks = []
    while pos < len(raw):
        ii = np.frombuffer(raw, np.int32, 10, pos)
        pos += 40
        xb = np.frombuffer(raw, np.float64 if lsize == 8 else np.float32, 6, pos)
        pos += 6 * lsize
        nx1, nx2, nx3 = ii[1] - ii[0] + 1, ii[3] - ii[2] + 1, ii[5] - ii[4] + 1
        nc = nx1 * nx2 * nx3
        data = np.frombuffer(raw, dt, nc * len(names), pos).reshape(len(names), nx3, nx2, nx1)
        pos += nc * len(names) * vsize
        blocks.append((xb.copy(), data))
    return _assemble(blocks, names, t, cyc, want, vsize)


def _assemble(blocks, names, t, cyc, want, vsize, ng=0):
    x1min = min(b[0][0] for b in blocks); x1max = max(b[0][1] for b in blocks)
    x2min = min(b[0][2] for b in blocks); x2max = max(b[0][3] for b in blocks)
    x3min = min(b[0][4] for b in blocks); x3max = max(b[0][5] for b in blocks)
    nb3, nb2, nb1 = blocks[0][1].shape[1:]
    nb3 -= 2 * ng; nb2 -= 2 * ng; nb1 -= 2 * ng
    dx = (blocks[0][0][1] - blocks[0][0][0]) / nb1
    n1 = int(round((x1max - x1min) / dx)); n2 = int(round((x2max - x2min) / dx))
    n3 = int(round((x3max - x3min) / dx))
    out = {"time": t, "cycle": cyc, "n": (n1, n2, n3), "xmin": np.array([x1min, x2min, x3min]),
           "L": np.array([x1max - x1min, x2max - x2min, x3max - x3min]), "dx": dx, "vsize": vsize}
    sel = [i for i, v in enumerate(names) if want is None or v in want]
    for i in sel:
        out[names[i]] = np.empty((n3, n2, n1))
    filled = np.zeros((n3, n2, n1), int)
    for xb, data in blocks:
        i0 = int(round((xb[0] - x1min) / dx)); j0 = int(round((xb[2] - x2min) / dx))
        k0 = int(round((xb[4] - x3min) / dx))
        sl = (slice(k0, k0 + nb3), slice(j0, j0 + nb2), slice(i0, i0 + nb1))
        inner = (slice(ng, ng + nb3), slice(ng, ng + nb2), slice(ng, ng + nb1))
        for i in sel:
            out[names[i]][sl] = data[i][inner]
        filled[sl] += 1
    assert filled.min() == 1 and filled.max() == 1, "blocks do not tile the mesh"
    return out


def read_rst(path, want=None, nz4c=22):
    """z4c part of an AthenaK restart file (no hydro, no MHD; data are the file's tail).
    Layout (restart.cpp): input text, int nmb, int root_level, RegionSize (9 double), two
    RegionIndcs (19 int each: ng, nx1..3, is..ke, cnx1..3, cis..cke), double time, double dt, int ncycle, nmb x LogicalLocation
    (4 int32), nmb x float cost, double z4c last_output_time, uint64 data size, then per
    MeshBlock nz4c arrays (nx3+2ng)(nx2+2ng)(nx1+2ng) with ghost cells."""
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        raw = f.read()
    # find the layout from the back: the (nmb, nx, ng) whose header fields are consistent
    start_guess = None
    for nmb in (1, 2, 4, 8, 16, 32, 64, 128, 256, 512):
        tail_hdr = 4 + 4 + 72 + 76 + 76 + 8 + 8 + 4 + 16 * nmb + 4 * nmb + 8 + 8
        for nx in (8, 16, 24, 32, 48, 64, 128):
            for ng in (2, 3, 4):
                nout = nx + 2 * ng
                dsz = nmb * nz4c * nout ** 3 * 8
                ds = size - dsz
                hs = ds - tail_hdr
                if hs <= 0:
                    continue
                if int(np.frombuffer(raw, np.int32, 1, hs)[0]) != nmb:
                    continue
                if int(np.frombuffer(raw, np.uint64, 1, ds - 8)[0]) not in (dsz, dsz // nmb):  # total or per MeshBlock
                    continue
                mbi = np.frombuffer(raw, np.int32, 19, hs + 4 + 4 + 72 + 76)
                if mbi[0] != ng or mbi[1] != nx:
                    continue
                start_guess = (hs, ds, nx, ng)
                break
            if start_guess:
                break
        if start_guess:
            break
    if not start_guess:
        raise ValueError("restart layout not recognized: " + path)
    hs, ds, nx, ng = start_guess
    p = hs + 8
    msz = np.frombuffer(raw, np.float64, 9, p); p += 72 + 76
    mbi = np.frombuffer(raw, np.int32, 19, p); p += 76
    t = float(np.frombuffer(raw, np.float64, 1, p)[0]); p += 16
    cyc = int(np.frombuffer(raw, np.int32, 1, p)[0]); p += 4
    lloc = np.frombuffer(raw, np.int32, 4 * nmb, p).reshape(nmb, 4)
    nb1, nb2, nb3 = mbi[1], mbi[2], mbi[3]
    nout = (nb3 + 2 * ng, nb2 + 2 * ng, nb1 + 2 * ng)
    ncell = nout[0] * nout[1] * nout[2]
    blocks = []
    dx = msz[6]
    for m in range(nmb):
        data = np.frombuffer(raw, np.float64, nz4c * ncell, ds + m * nz4c * ncell * 8)
        data = data.reshape(nz4c, *nout)
        lx1, lx2, lx3, lev = lloc[m]
        x1 = msz[0] + lx1 * nb1 * dx; x2 = msz[1] + lx2 * nb2 * msz[7]; x3 = msz[2] + lx3 * nb3 * msz[8]
        xb = np.array([x1, x1 + nb1 * dx, x2, x2 + nb2 * msz[7], x3, x3 + nb3 * msz[8]])
        blocks.append((xb, data))
    return _assemble(blocks, Z4C, t, cyc, want, 8, ng=ng)


def tensor(d, base):
    """3x3 symmetric tensor field [a, b, k, j, i] from components base+xx, ..."""
    nm = {(0, 0): "xx", (0, 1): "xy", (0, 2): "xz", (1, 1): "yy", (1, 2): "yz", (2, 2): "zz"}
    T = np.empty((3, 3) + d[base + "xx"].shape)
    for (a, b), s in nm.items():
        T[a, b] = d[base + s]
        T[b, a] = d[base + s]
    return T


# ----------------------------------------------------------------------------- Fourier tools
class Grid:
    def __init__(self, d):
        self.n = d["n"]; self.L = d["L"]; self.xmin = d["xmin"]; self.dx = d["dx"]
        n1, n2, n3 = self.n
        self.ncell = n1 * n2 * n3
        m1 = np.fft.fftfreq(n1, 1.0 / n1); m2 = np.fft.fftfreq(n2, 1.0 / n2); m3 = np.fft.fftfreq(n3, 1.0 / n3)
        M3, M2, M1 = np.meshgrid(m3, m2, m1, indexing="ij")
        self.m = np.array([M1, M2, M3])                      # integer wave numbers, [a, k, j, i]
        self.k = np.array([2 * np.pi * self.m[a] / self.L[a] for a in range(3)])
        self.k2 = (self.k ** 2).sum(axis=0)
        nyq = (np.abs(M1) == n1 // 2) | (np.abs(M2) == n2 // 2) | (np.abs(M3) == n3 // 2)
        self.keep = (~nyq) & (self.k2 > 0)                   # modes that are projected
        x = [self.xmin[a] + (np.arange(self.n[a]) + 0.5) * self.dx for a in range(3)]
        self.x = x

    def fft_t(self, T):
        """Full complex FFT of a [3, 3, k, j, i] tensor (symmetric)."""
        return np.fft.fftn(T, axes=(-3, -2, -1))

    def ifft_t(self, F):
        return np.fft.ifftn(F, axes=(-3, -2, -1)).real

    def tt(self, F):
        """TT projection Lambda_ij,kl F_kl in Fourier space, k = 0 and Nyquist planes zeroed."""
        with np.errstate(invalid="ignore", divide="ignore"):
            kh = np.where(self.k2 > 0, self.k / np.sqrt(np.where(self.k2 > 0, self.k2, 1.0)), 0.0)
        P = np.eye(3)[:, :, None, None, None] - kh[:, None] * kh[None, :]
        PF = np.einsum("ikxyz,klxyz->ilxyz", P, F)
        PFP = np.einsum("ilxyz,ljxyz->ijxyz", PF, P)
        trPF = np.einsum("klxyz,lkxyz->xyz", P, F)
        T = PFP - 0.5 * P * trPF
        T[:, :, ~self.keep] = 0.0
        return T

    def power(self, F):
        """Volume mean of f_ij f_ij per Fourier mode (Parseval), [k, j, i]."""
        return (np.abs(F) ** 2).sum(axis=(0, 1)) / self.ncell ** 2

    def phase(self, m):
        K = np.array([2 * np.pi * m[a] / self.L[a] for a in range(3)])
        x0 = np.array([self.xmin[a] + 0.5 * self.dx for a in range(3)])
        return K, np.exp(-1j * float(K @ x0))

    def amp_from_fft(self, F, m):
        """c - i s of the mode m (integers) from full-FFT coefficients F[..., k, j, i]."""
        _, ph = self.phase(m)
        return 2.0 * F[..., m[2] % self.n[2], m[1] % self.n[1], m[0] % self.n[0]] * ph / self.ncell

    def amp_direct(self, f, m):
        """c - i s by the direct sum over cell centres (independent of the FFT)."""
        K = np.array([2 * np.pi * m[a] / self.L[a] for a in range(3)])
        ex = np.exp(-1j * K[0] * self.x[0]); ey = np.exp(-1j * K[1] * self.x[1]); ez = np.exp(-1j * K[2] * self.x[2])
        return 2.0 * np.einsum("...kji,k,j,i->...", f, ez, ey, ex) / self.ncell


S2 = 1.0 / np.sqrt(2.0)
_Z = np.array([0.0, 0.0, 1.0])
BASIS = {}
for _name, _m, _u in (("K1", (1, 1, 0), np.array([S2, -S2, 0.0])), ("K2", (1, -1, 0), np.array([S2, S2, 0.0]))):
    BASIS[_name] = (_m, np.outer(_u, _u) - np.outer(_Z, _Z), np.outer(_u, _Z) + np.outer(_Z, _u))


def pol(A):
    """(h_+, h_x) from a 3x3 complex mode amplitude A at K1 or K2: dict name -> pair."""
    return {nm: (0.5 * np.einsum("ab,ab->", ep, A[nm]), 0.5 * np.einsum("ab,ab->", ex, A[nm]))
            for nm, (_, ep, ex) in BASIS.items()}


def traceless(T):
    tr = np.einsum("aa...->...", T)
    return T - np.eye(3)[:, :, None, None, None] * tr / 3.0


# ----------------------------------------------------------------------------- reference
H0 = 1.0
LBOX = 4.0
KBOX = 2 * np.pi / LBOX


def a_of_tau(tau):
    """EdS scale factor in conformal time with a(0) = 1, H(0) = 1: a = (1 + tau/2)^2."""
    return (1.0 + 0.5 * np.asarray(tau, float)) ** 2


def s_static(delta, eps):
    """s = -(5/6) phi_x phi_y, phi_i = -(3/2)(H/k)^2 delta r_i, r = (1, eps, 0)."""
    px = -1.5 * (H0 / KBOX) ** 2 * delta
    return -(5.0 / 6.0) * px * (eps * px)


def g_closed(tau):
    """Junk solution g'' + 2 Hc g' + K^2 (g - 1) = 0, g(0) = g'(0) = 0, Hc = 2/(tau + 2),
    K^2 = 2 k^2: u = g - 1 solves u'' + 4/(tau+2) u' + K^2 u = 0, u = [c1 j1(x) + c2 y1(x)]/x,
    x = K (tau + 2), with u(0) = -1, u'(0) = 0."""
    from scipy.special import spherical_jn, spherical_yn
    K = np.sqrt(2.0) * KBOX
    tau = np.asarray(tau, float)

    def basis(x):
        j, y = spherical_jn(1, x), spherical_yn(1, x)
        dj, dy = spherical_jn(1, x, derivative=True), spherical_yn(1, x, derivative=True)
        return j / x, y / x, (dj * x - j) / x ** 2, (dy * x - y) / x ** 2
    x0 = 2 * K
    f1, f2, d1, d2 = basis(x0)
    # u = c1 f1 + c2 f2, du/dtau = K (c1 d1 + c2 d2)
    M = np.array([[f1, f2], [K * d1, K * d2]])
    c1, c2 = np.linalg.solve(M, [-1.0, 0.0])
    x = K * (tau + 2.0)
    F1, F2, _, _ = basis(x)
    return 1.0 + c1 * F1 + c2 * F2


def g_ode(tau):
    from scipy.integrate import solve_ivp
    K2 = 2 * KBOX ** 2
    tau = np.asarray(tau, float)
    sol = solve_ivp(lambda t, y: [y[1], -4.0 / (t + 2.0) * y[1] - K2 * (y[0] - 1.0)], (0, float(tau.max()) + 1e-9),
                    [0.0, 0.0], method="DOP853", rtol=1e-12, atol=1e-14, dense_output=True)
    return sol.sol(tau)[0]


# ----------------------------------------------------------------------------- per-dump measure
def measure(d, energies=True, spectrum=False, gauge=False):
    """Diagnostics of one z4c dump (dict from read_bin/read_rst)."""
    g = Grid(d)
    gt = tensor(d, "g")
    h = traceless(gt - np.eye(3)[:, :, None, None, None])
    Fh = g.fft_t(h)
    Th = g.tt(Fh)
    r = {"time": d["time"], "a_chi": float(np.mean(d["chi"]) ** -0.5), "vsize": d["vsize"]}
    # direct-sum amplitudes at the box modes (TT at a single K: e+ and ex are TT already)
    A = {nm: g.amp_direct(h, m) for nm, (m, _, _) in BASIS.items()}
    for nm, (hp, hx) in pol(A).items():
        r[f"{nm}_plus"] = [hp.real, hp.imag]
        r[f"{nm}_cross"] = [hx.real, hx.imag]
    P = g.power(Th)
    ms_tt = float(P.sum())
    ms_tf = float(g.power(Fh)[g.k2 > 0].sum())
    r["rms_TT"] = np.sqrt(ms_tt)
    r["rms_nonTT"] = np.sqrt(max(ms_tf - ms_tt, 0.0))
    nrm = np.sqrt((np.abs(Th) ** 2).sum(axis=(0, 1))) * 2.0 / g.ncell
    r["max_TT_mode"] = float(nrm.max())
    box = np.zeros(g.n[::-1], bool)
    for m in ((1, 1, 0), (-1, -1, 0), (1, -1, 0), (-1, 1, 0)):
        box[m[2] % g.n[2], m[1] % g.n[1], m[0] % g.n[0]] = True
    r["box_share"] = float(P[box].sum() / ms_tt) if ms_tt > 0 else None
    if energies:
        At = traceless(tensor(d, "A"))
        TA = g.tt(g.fft_t(At))
        chib = float(np.mean(d["chi"]))
        r["kin"] = 4.0 * float(g.power(TA).sum())
        r["grad"] = chib * float((g.k2 * P).sum())
    if spectrum:
        mag = np.sqrt((g.m ** 2).sum(axis=0))
        r["frac_ge16_round"] = float(P[np.rint(mag) >= 16].sum() / ms_tt)
        r["frac_ge16_floor"] = float(P[np.floor(mag) >= 16].sum() / ms_tt)
        r["frac_ge15p5"] = float(P[mag >= 15.5].sum() / ms_tt)
    if gauge:
        Gq, Gt = gauge_piece(h, Fh, Th, g)
        for key, GG in (("Gq", Gq), ("Gtot", Gt)):
            AG = {nm: g.amp_from_fft(GG, m) for nm, (m, _, _) in BASIS.items()}
            for nm, (hp, hx) in pol(AG).items():
                r[f"{key}_{nm}_plus"] = [hp.real, hp.imag]
    return r


def gauge_piece(h, Fh, Th, g):
    """Spatial-gauge piece of the flat TT projection at second order (note Eq. (9)):
    G_tot = TT[ D^T D - (2/3)(div xi)(D + D^T) + D^T hR + hR D - (2/3)(div xi) hR + (xi.grad) hR ],
    D_ki = d_i xi_k, xi from the traceless non-TT part hL = d_i xi_j + d_j xi_i - (2/3) delta div xi,
    hR = TT part + homogeneous traceless part. Returns (TT of the quadratic piece alone, G_tot),
    both as full-FFT coefficients."""
    FL = Fh - Th
    FL[:, :, g.k2 == 0] = 0.0
    k = g.k
    k2 = np.where(g.k2 > 0, g.k2, 1.0)
    v = np.einsum("ijxyz,jxyz->ixyz", FL, k)                # hL_ij k_j
    kv = np.einsum("ixyz,ixyz->xyz", k, v)
    # hL = i (k_i xi_j + k_j xi_i) - (2/3) i delta (k.xi):  xi = -i v/k^2 + i k (k.v)/(4 k^4)
    Fxi = -1j * v / k2 + 1j * k * kv / (4.0 * k2 ** 2)
    Fxi[:, g.k2 == 0] = 0.0
    xi = np.fft.ifftn(Fxi, axes=(-3, -2, -1)).real
    D = np.fft.ifftn(1j * k[None, :] * Fxi[:, None], axes=(-3, -2, -1)).real   # D[k, i] = d_i xi_k
    div = np.einsum("aa...->...", D)
    hR = np.fft.ifftn(Th, axes=(-3, -2, -1)).real + h.mean(axis=(-3, -2, -1))[:, :, None, None, None]
    DtD = np.einsum("kixyz,kjxyz->ijxyz", D, D)
    quad = DtD - (2.0 / 3.0) * div * (D + np.swapaxes(D, 0, 1))
    cross = (np.einsum("kixyz,kjxyz->ijxyz", D, hR) + np.einsum("ikxyz,kjxyz->ijxyz", hR, D)
             - (2.0 / 3.0) * div * hR)
    FhR = np.fft.fftn(hR, axes=(-3, -2, -1))
    grad_hR = np.fft.ifftn(1j * k[None, None] * FhR[:, :, None], axes=(-3, -2, -1)).real  # [i, j, l]
    adv = np.einsum("lxyz,ijlxyz->ijxyz", xi, grad_hR)
    Gq = g.tt(g.fft_t(quad))
    Gt = g.tt(g.fft_t(quad + cross + adv))
    return Gq, Gt
