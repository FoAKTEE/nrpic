"""Readers of AthenaK NRPIC output and of the format-2 table, written by the verifier from
the source (athenak/src/particles/nrpic_io.cpp at the run commit) and from
coord/INTERFACES/spherical_id_format2.md. No code of the track is imported."""
import numpy as np

TRAJ_N = 8      # nrpic_io.cpp:802, 919-922: time, tag, x^i, u_i
TRAJMET_N = 17  # nrpic_io.cpp:811-814, 924-926: time, tag, alpha, beta^i, gamma_ij (6), tau, E, S_i


def read_traj(path):
    a = np.fromfile(path, dtype="<f8")
    assert a.size % TRAJ_N == 0, (path, a.size)
    return a.reshape(-1, TRAJ_N)


def read_trajmet(path):
    a = np.fromfile(path, dtype="<f8")
    assert a.size % TRAJMET_N == 0, (path, a.size)
    return a.reshape(-1, TRAJMET_N)


def read_snapshot(path):
    """<basename>.part.NNNNN.bin (nrpic_io.cpp:940-978): 'NRPSNAP1', double time,
    int64 N, int64 ncycle, N x 7 doubles (x^i, u_i, m), N int32 tags, N int32 species,
    N doubles (proper time)."""
    with open(path, "rb") as f:
        magic = f.read(8)
        assert magic == b"NRPSNAP1", magic
        t = np.frombuffer(f.read(8), "<f8")[0]
        n = int(np.frombuffer(f.read(8), "<i8")[0])
        nc = int(np.frombuffer(f.read(8), "<i8")[0])
        rec = np.frombuffer(f.read(56 * n), "<f8").reshape(n, 7)
        tag = np.frombuffer(f.read(4 * n), "<i4")
        sp = np.frombuffer(f.read(4 * n), "<i4")
        tau = np.frombuffer(f.read(8 * n), "<f8")
        rest = f.read()
    assert len(rest) == 0, (path, len(rest))
    return dict(t=t, n=n, ncycle=nc, x=rec[:, :3], u=rec[:, 3:6], m=rec[:, 6], tag=tag,
                sp=sp, tau=tau)


def read_particle_file(path):
    """Initial particle file (nrpic_io.cpp:983-1024): 'NRPIC001', int64 N, N x 7 doubles,
    N int32 species; the tag is the position in the file."""
    with open(path, "rb") as f:
        assert f.read(8) == b"NRPIC001"
        n = int(np.frombuffer(f.read(8), "<i8")[0])
        rec = np.frombuffer(f.read(56 * n), "<f8").reshape(n, 7)
        sp = np.frombuffer(f.read(4 * n), "<i4")
        assert len(f.read()) == 0
    return dict(n=n, x=rec[:, :3], u=rec[:, 3:6], m=rec[:, 6], sp=sp,
                tag=np.arange(n, dtype=np.int32))


def read_horizon_summary(path):
    """horizon_summary_0.txt; columns named in its first line."""
    with open(path) as f:
        head = f.readline()
    names = [w.split(":")[1] for w in head.lstrip("#").split()]
    a = np.loadtxt(path, comments="#")
    return {k: a[:, i] for i, k in enumerate(names)}


def read_hst(path):
    with open(path) as f:
        lines = [l for l in f if l.startswith("#")]
    names = None
    for l in lines:
        if "[1]=" in l:
            names = [w.split("=")[1] for w in l.lstrip("#").split()]
    a = np.loadtxt(path, comments="#")
    if a.ndim == 1:
        a = a[None, :]
    return {k: a[:, i] for i, k in enumerate(names)}


class Table2:
    """Format-2 table (rbar u KL KT alpha betar), four-point Lagrange through rows
    i-1..i+2 shifted to stay inside the table (no breaks in the tables used here)."""

    def __init__(self, path):
        hdr = {}
        rows = []
        with open(path) as f:
            for l in f:
                if l.startswith("#"):
                    if "=" in l:
                        k, v = l[1:].split("=", 1)
                        hdr[k.strip()] = v.strip()
                elif l.strip():
                    rows.append([float(x) for x in l.split()])
        self.hdr = hdr
        self.a = np.array(rows)
        assert hdr.get("format") == "2"
        assert "breaks" not in hdr or hdr["breaks"].strip() == "", "breaks not handled"
        self.dr = self.a[1, 0] - self.a[0, 0]
        assert np.allclose(np.diff(self.a[:, 0]), self.dr)
        self.N = len(self.a)

    def _lag(self, col, r, der=0):
        r = np.atleast_1d(np.asarray(r, float))
        i = np.floor(r / self.dr).astype(int)
        i0 = np.clip(i - 1, 0, self.N - 4)
        out = np.zeros_like(r)
        x = r / self.dr
        for j in range(4):
            k = i0 + j
            # Lagrange basis l_j on the integer nodes i0..i0+3 (in units of drbar)
            lj = np.ones_like(r)
            dlj = np.zeros_like(r)
            for q in range(4):
                if q == j:
                    continue
                kq = i0 + q
                fac = (x - kq) / (k - kq)
                # derivative by product rule
                dlj = dlj * fac + lj / (k - kq)
                lj = lj * fac
            val = self.a[k, col]
            out += val * (dlj / self.dr if der else lj)
        return out

    def eval(self, name, r, der=0):
        col = {"u": 1, "KL": 2, "KT": 3, "alpha": 4, "betar": 5}[name]
        r = np.atleast_1d(np.asarray(r, float))
        inside = r < self.a[-1, 0]
        out = self._lag(col, np.where(inside, r, self.a[-2, 0]), der)
        if not np.all(inside):
            rN, vN = self.a[-1, 0], self.a[-1, col]
            ro = r[~inside]
            if name == "u":
                out[~inside] = vN * rN / ro if not der else -vN * rN / ro ** 2
            elif name in ("KL", "KT") and self.hdr.get("exterior") == "pg":
                out[~inside] = vN * (ro / rN) ** -1.5 if not der else -1.5 * vN * (ro / rN) ** -1.5 / ro
            else:
                raise ValueError("outside table: " + name)
        return out


def sphere_of_table(tab, m_p, rbar):
    """Areal radius R, dR/dl, KT and Misner-Sharp mass at isotropic radius rbar for the
    table plus a puncture of bare mass m_p (psi = 1 + u + m_p/(2 rbar))."""
    u = tab.eval("u", rbar)
    du = tab.eval("u", rbar, der=1)
    psi = 1.0 + u + m_p / (2 * rbar)
    dpsi = du - m_p / (2 * rbar ** 2)
    R = psi ** 2 * rbar
    dR_drbar = 2 * psi * dpsi * rbar + psi ** 2
    W = dR_drbar / psi ** 2
    KT = tab.eval("KT", rbar)
    m = 0.5 * R * (1 - W ** 2 + R ** 2 * KT ** 2)
    return dict(R=R, W=W, KT=KT, m=m, psi=psi)
