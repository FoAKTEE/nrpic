"""Own readers and reference of the G2 verifier (E-stoch-inf, stage/G2/verifier).

Written from the interface texts, not from the analysis scripts of the track:
- dump layout NRSFDMP2: coord/INTERFACES/scalar_field_2.md section 4;
- constraint record columns: header line of <basename>.sf.con.hst, scalar_field_3.md 6;
- noise field convention (hemisphere, cell centres, L^-3/2 R alpha): scalar_field.md 7.1, 7.3;
- R^NR extraction: TH appendix.tex:515-521 and P1 PRD_v2.tex:524-526
  (Phi_k = (1/2)(X_k/<X> - 1) + (1/4) k_i k_j/k^2 (gt_ij - delta_ij)_k,
   R = Phi - <K>/(3 <alpha> <Pi>) (phi - <phi>));
- background and Mukhanov-Sasaki equation of the code (scalar_field.md 7.3), integrated
  here with DOP853 from (phi0, pi0) of the deck and the mode file at N*.
Only one variable of a dump is read at a time (sequential read of its block).
"""
import os
import struct
import sys

import numpy as np
import scipy.fft as sfft
from scipy.integrate import solve_ivp

L_BOX = 2.0 * np.pi
HERE = os.path.dirname(os.path.abspath(__file__))
TRACK = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))   # tracks/E-stoch-inf
WORKERS = int(os.environ.get("VERIFIER_FFT_WORKERS", "2"))

# ----------------------------------------------------------------------------- dumps

def dump_header(path):
    with open(path, "rb") as f:
        magic = f.read(8)
        if magic != b"NRSFDMP2":
            raise ValueError(f"{path}: not NRSFDMP2 ({magic!r})")
        nmb, nx1, nx2, nx3, nvar, cycle, nnoise = struct.unpack("<7q", f.read(56))
        (time,) = struct.unpack("<d", f.read(8))
        names = [f.read(16).rstrip(b"\0").decode() for _ in range(nvar)]
        start = f.tell()
    if nmb != 1:
        raise ValueError("this reader handles one MeshBlock (all G2 runs have one)")
    ncell = nx1 * nx2 * nx3
    return dict(path=path, nmb=nmb, nx=(nx1, nx2, nx3), nvar=nvar, cycle=cycle,
                time=time, names=names, data0=start + 32 + 48, ncell=ncell)


def read_var(path_or_hdr, name):
    h = dump_header(path_or_hdr) if isinstance(path_or_hdr, str) else path_or_hdr
    i = h["names"].index(name)
    nx1, nx2, nx3 = h["nx"]
    with open(h["path"], "rb") as f:
        f.seek(h["data0"] + i * h["ncell"] * 8)
        a = np.fromfile(f, dtype="<f8", count=h["ncell"])
    if a.size != h["ncell"]:
        raise IOError(f"{h['path']}: short read of {name}")
    return a.reshape(nx3, nx2, nx1)          # [z, y, x], x fastest


def write_dump(path, fields, time=0.0, cycle=0, box=(0.0, L_BOX)):
    """Write a synthetic NRSFDMP2 file (one MeshBlock) for the reader test."""
    names = list(fields)
    nz, ny, nx = fields[names[0]].shape
    with open(path, "wb") as f:
        f.write(b"NRSFDMP2")
        f.write(struct.pack("<7q", 1, nx, ny, nz, len(names), cycle, 0))
        f.write(struct.pack("<d", time))
        for nm in names:
            f.write(nm.encode().ljust(16, b"\0"))
        f.write(struct.pack("<4q", 0, 0, 0, 0))
        f.write(struct.pack("<6d", box[0], box[1], box[0], box[1], box[0], box[1]))
        for nm in names:
            np.ascontiguousarray(fields[nm], dtype="<f8").tofile(f)


def read_con(path):
    """Constraint record; rows deduplicated by cycle (last occurrence kept: restarts)."""
    a = np.loadtxt(path, comments="#")
    cyc = a[:, 1].astype(np.int64)
    last = {}
    for i, c in enumerate(cyc):
        last[c] = i
    idx = np.array([last[c] for c in sorted(last)])
    return a[idx], int(len(a) - len(idx))

# ----------------------------------------------------------------------------- modes

def hemisphere(nmax2):
    """Integer wave vectors (nx, ny, nz) of the hemisphere of scalar_field.md 7.1."""
    m = int(np.floor(np.sqrt(nmax2)))
    r = np.arange(-m, m + 1)
    nz, ny, nx = np.meshgrid(r, r, r, indexing="ij")
    nx, ny, nz = nx.ravel(), ny.ravel(), nz.ravel()
    n2 = nx * nx + ny * ny + nz * nz
    keep = (n2 > 0) & (n2 <= nmax2) & ((nx > 0) | ((nx == 0) & (ny > 0)) |
                                       ((nx == 0) & (ny == 0) & (nz > 0)))
    n = np.stack([nx[keep], ny[keep], nz[keep]], axis=1)
    order = np.lexsort((n[:, 2], n[:, 1], n[:, 0], (n ** 2).sum(1)))
    return n[order]


def rfft(field):
    return sfft.rfftn(field, workers=WORKERS)


def coeffs_from_rfft(F, n, N):
    """c_n of f = sum_H 2 Re[c_n exp(i k_n (x - x0))] on cell centres, from rfftn of f."""
    nx, ny, nz = n[:, 0], n[:, 1], n[:, 2]
    val = F[nz % N, ny % N, nx]
    phase = np.exp(-1j * np.pi * (nx + ny + nz) / N)
    return val * phase / float(N) ** 3


def synth(n, c, N):
    """Field sum_H 2 Re[c_n exp(i 2 pi n (g + 1/2)/N)] on an N^3 lattice ([z, y, x])."""
    g = (np.arange(N) + 0.5) / N
    out = np.zeros((N, N, N))
    for (nx, ny, nz), cc in zip(n, c):
        ex = np.exp(2j * np.pi * nx * g)
        ey = np.exp(2j * np.pi * ny * g)
        ez = np.exp(2j * np.pi * nz * g)
        out += 2.0 * np.real(cc * ez[:, None, None] * ey[None, :, None] * ex[None, None, :])
    return out


GT = [("gxx", 0, 0), ("gyy", 1, 1), ("gzz", 2, 2), ("gxy", 0, 1), ("gxz", 0, 2), ("gyz", 1, 2)]


def rnr_from_dump(path, n, want_full=False, want_parts=False):
    """R^NR coefficients on the modes n from one dump (TH appendix.tex:515-521)."""
    h = dump_header(path)
    N = h["nx"][0]
    out = dict(time=h["time"], cycle=h["cycle"], N=N)
    means = {}
    for nm in ("K", "alpha", "Pi"):
        means[nm] = float(read_var(h, nm).mean())
    out["means"] = means
    hop = -means["K"] / (3.0 * means["alpha"] * means["Pi"])      # H/Pi_b of the dump
    out["H_over_Pi"] = hop
    kn = n.astype(np.float64)
    kn /= np.sqrt((kn ** 2).sum(1))[:, None]
    full = None
    if want_full:
        mz = np.fft.fftfreq(N, 1.0 / N)
        mx = np.fft.rfftfreq(N, 1.0 / N)
        KZ, KY, KX = np.meshgrid(mz, mz, mx, indexing="ij")
        K2 = KX ** 2 + KY ** 2 + KZ ** 2
        K2[0, 0, 0] = 1.0
        kk = (KX, KY, KZ)
        full = np.zeros((N, N, N // 2 + 1), dtype=np.complex128)
    # phi
    a = read_var(h, "phi")
    out["mean_phi"] = float(a.mean())
    F = rfft(a)
    del a
    c_phi = coeffs_from_rfft(F, n, N)
    if want_full:
        full += hop * F
    del F
    # chi
    a = read_var(h, "chi")
    mchi = float(a.mean())
    out["mean_chi"] = mchi
    F = rfft(a)
    del a
    c_chi = 0.5 * coeffs_from_rfft(F, n, N) / mchi
    if want_full:
        full += 0.5 * F / mchi
    del F
    c_gt = np.zeros(len(n), dtype=np.complex128)
    for nm, i, j in GT:
        a = read_var(h, nm)
        F = rfft(a)
        del a
        w = (1.0 if i == j else 2.0) * 0.25
        c_gt += w * kn[:, i] * kn[:, j] * coeffs_from_rfft(F, n, N)
        if want_full:
            full += w * kk[i] * kk[j] / K2 * F
        del F
    out["c"] = hop * c_phi + c_chi + c_gt
    if want_parts:
        out["c_phi"] = hop * c_phi
        out["c_chi"] = c_chi
        out["c_gt"] = c_gt
    if want_full:
        full[0, 0, 0] = 0.0
        w = np.full(N // 2 + 1, 2.0)
        w[0] = 1.0
        if N % 2 == 0:
            w[-1] = 1.0
        var = float((np.abs(full) ** 2 * w[None, None, :]).sum()) / float(N) ** 6
        out["rms_full"] = np.sqrt(var)
        # skewness/kurtosis/extremes of the full field
        f = sfft.irfftn(full, s=(N, N, N), workers=WORKERS)
        out["max_abs_full"] = float(np.abs(f).max())
        sd = f.std()
        out["skew_full"] = float(((f / sd) ** 3).mean())
        out["exkurt_full"] = float(((f / sd) ** 4).mean() - 3.0)
        del f, full
    out["rms_band"] = float(np.sqrt(2.0 * (np.abs(out["c"]) ** 2).sum()))
    return out

# ----------------------------------------------------------------------------- reference

def potential(lam, vev):
    """V and V' of the inflection potential in code units (derivation in JOURNAL entry 2):
    V = lam vev^4 phi^2 (3 phi^2 + 2 sqrt2 phi vev + 6 vev^2) / (3 (3 phi^2 + 2 vev^2)^2)."""
    import sympy as sp
    p, l, v = sp.symbols("p l v", real=True)
    V = l * v ** 4 * p ** 2 * (3 * p ** 2 + 2 * sp.sqrt(2) * p * v + 6 * v ** 2) / \
        (3 * (3 * p ** 2 + 2 * v ** 2) ** 2)
    dV = sp.simplify(sp.diff(V, p))
    fV = sp.lambdify((p, l, v), V, "numpy")
    fdV = sp.lambdify((p, l, v), dV, "numpy")
    return (lambda x: fV(x, lam, vev)), (lambda x: fdV(x, lam, vev))


def read_deck(path):
    out, sec = {}, None
    for line in open(path):
        line = line.split("#")[0].strip()
        if not line:
            continue
        if line.startswith("<"):
            sec = line.strip("<>")
            continue
        if "=" in line:
            k, v = [s.strip() for s in line.split("=", 1)]
            out[f"{sec}/{k}"] = v
    return out


def read_mode_file(path):
    rows = np.loadtxt(path, comments="#")
    q2 = rows[:, 0].astype(np.int64)
    R0 = rows[:, 1] + 1j * rows[:, 2]
    dR0 = rows[:, 3] + 1j * rows[:, 4]
    return q2, R0, dR0


class Reference:
    """Friedmann + Klein-Gordon background and continuum MS modes from t = 0 (N*)."""

    def __init__(self, deck, mode_file, t_end, rtol=1e-12, nshell=None):
        d = read_deck(deck)
        self.lam = float(d["scalar_field/lambda"])
        self.vev = float(d["scalar_field/vev"])
        self.phi0 = float(d["problem/phi0"])
        self.pi0 = float(d["problem/pi0"])
        self.V, self.dV = potential(self.lam, self.vev)
        q2, R0, dR0 = read_mode_file(mode_file)
        if nshell is not None:
            q2, R0, dR0 = q2[:nshell], R0[:nshell], dR0[:nshell]
        self.q2, self.R0, self.dR0 = q2, R0, dR0
        self.k2 = q2.astype(np.float64) * (2.0 * np.pi / L_BOX) ** 2
        ns = len(q2)
        y0 = np.concatenate([[self.phi0, self.pi0, 0.0], R0.real, R0.imag,
                             dR0.real, dR0.imag])
        self.ns = ns
        sc = np.concatenate([[1.0, 1.0, 1.0], np.abs(R0) + 1e-30, np.abs(R0) + 1e-30,
                             np.abs(dR0) + 1e-30, np.abs(dR0) + 1e-30])
        self.sol = solve_ivp(self._rhs, (0.0, t_end), y0, method="DOP853", rtol=rtol,
                             atol=sc * rtol * 1e-3, dense_output=True)
        if not self.sol.success:
            raise RuntimeError(self.sol.message)

    def hubble(self, phi, pi):
        return np.sqrt(8.0 * np.pi / 3.0 * (0.5 * pi * pi + self.V(phi)))

    def _rhs(self, t, y):
        phi, pi, N = y[0], y[1], y[2]
        H = self.hubble(phi, pi)
        dV = self.dV(phi)
        eps1 = 4.0 * np.pi * pi * pi / (H * H)
        eps2 = 6.0 + 2.0 * dV / (H * pi) - 2.0 * eps1
        ns = self.ns
        Rr, Ri = y[3:3 + ns], y[3 + ns:3 + 2 * ns]
        Dr, Di = y[3 + 2 * ns:3 + 3 * ns], y[3 + 3 * ns:3 + 4 * ns]
        fr = (3.0 - eps2) * H
        w2 = self.k2 * np.exp(-2.0 * N)
        return np.concatenate([[pi, -3.0 * H * pi - dV, H], Dr, Di,
                               -fr * Dr - w2 * Rr, -fr * Di - w2 * Ri])

    def background(self, t):
        y = self.sol.sol(t)
        phi, pi, N = y[0], y[1], y[2]
        H = self.hubble(phi, pi)
        eps1 = 4.0 * np.pi * pi * pi / (H * H)
        eps2 = 6.0 + 2.0 * self.dV(phi) / (H * pi) - 2.0 * eps1
        return dict(phi=phi, Pi=pi, N=N, H=H, K=-3.0 * H, eps1=eps1, eps2=eps2)

    def modes(self, t):
        y = self.sol.sol(t)
        ns = self.ns
        R = y[3:3 + ns] + 1j * y[3 + ns:3 + 2 * ns]
        dR = y[3 + 2 * ns:3 + 3 * ns] + 1j * y[3 + 3 * ns:3 + 4 * ns]
        return R, dR

    def window(self, t, k, s=5.0, sigma=1.0):
        b = self.background(t)
        aH = np.exp(b["N"]) * b["H"]
        return 0.5 * (1.0 + np.tanh(s * np.log(sigma * aH / k)))


def shell_lookup(q2_ref, n):
    """Index into the reference shells for every mode n."""
    n2 = (n ** 2).sum(1)
    pos = {int(q): i for i, q in enumerate(q2_ref)}
    return np.array([pos[int(q)] for q in n2])


def full_multiplicity(nmax2):
    m = int(np.floor(np.sqrt(nmax2)))
    r = np.arange(-m, m + 1)
    nz, ny, nx = np.meshgrid(r, r, r, indexing="ij")
    n2 = (nx * nx + ny * ny + nz * nz).ravel()
    return np.bincount(n2[n2 <= nmax2], minlength=nmax2 + 1)

# ----------------------------------------------------------------------------- alpha

def alpha_modes(seed, n):
    """alpha_n from the track's own Philox re-implementation (noise/ref/philox_ref.py)."""
    sys.path.insert(0, os.path.join(TRACK, "noise", "ref"))
    import philox_ref
    return philox_ref.mode_alpha(int(seed), 0, 0, n)


def alpha_modes_core_twin(seed, n):
    """The same from core's twin python/nrpic/rng.py (cross-check only)."""
    root = os.path.abspath(os.path.join(TRACK, "..", ".."))
    sys.path.insert(0, os.path.join(root, "python"))
    from nrpic import rng
    ent = rng.mode_entity(n[:, 0], n[:, 1], n[:, 2])
    st = rng.stochastic_mode_stream(0)
    z1, z2 = rng.normal2(int(seed), st, ent, 0, 0)
    return (np.asarray(z1) + 1j * np.asarray(z2)) / np.sqrt(2.0)

# ----------------------------------------------------------------------------- parts

def floor2(o_s, o_h):
    """f^2 = max(0, (4 o_{s/2}^2 - o_s^2)/3) of SCOPE 4c."""
    return max(0.0, (4.0 * o_h ** 2 - o_s ** 2) / 3.0)

# ----------------------------------------------------------------------------- runs

SCRATCH = "/data/haiyangw/nrpic/scratch/E-stoch-inf"
DECK = os.path.join(TRACK, "g2prod", "inputs", "usr_prod.athinput")
MODEFILE = os.path.join(TRACK, "usr", "inputs", "modes_usr_n4096.txt")
SEED = {"A": 20261115, "B": 20261116}
RUNS = {   # label: (run id, s, seed, N); g2prod/queue.txt, runs/*/manifest.json
    "U256ap": ("E-20261121-211214-0377aab", +1.0, "A", 256),
    "U256am": ("E-20261121-214629-da64fb7", -1.0, "A", 256),
    "U320ap": ("E-20261122-023427-0ac3f0b", +1.0, "A", 320),
    "U320am": ("E-20261122-110042-ffcb4b3", -1.0, "A", 320),
    "U256bp": ("E-20261122-033244-564627b", +1.0, "B", 256),
    "U256bm": ("E-20261122-071038-d9f933b", -1.0, "B", 256),
    "U256hp": ("E-20261122-113320-9bbb52b", +0.5, "A", 256),
    "U256hm": ("E-20261122-152116-0542096", -0.5, "A", 256),
    "U256nc": ("E-20261122-190341-0419be6", +1.0, "A", 256),
    "U256qp": ("E-20261123-230004-861aea7", +0.25, "A", 256),
    "U256qm": ("E-20261123-230507-a6246b1", -0.25, "A", 256),
}


def run_dir(label):
    return os.path.join(SCRATCH, RUNS[label][0])


def dump_path(label, k):
    return os.path.join(run_dir(label), f"usr.sf.{k:05d}.dump")


def dumps_of(label):
    d = run_dir(label)
    return sorted(int(f.split(".")[2]) for f in os.listdir(d) if f.endswith(".dump"))
