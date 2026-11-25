"""Readers of the verifier of item C18 (Track A, G2), written from docs/FORMATS.md and
coord/INTERFACES/diagnostics.md only (not from the packages' scripts).

- horizon summary `<base>.horizon_summary_N.txt`: columns 1 iter, 2 time, 3 mass,
  4-6 S_i, 7 S, 8 area, 9 hrms, 10 hmean, 11 meanradius, 12 minradius; a failed search
  writes nan. Restarted chains append: the last record of each time is kept.
- trajectories `<base>.traj.bin` (8 float64: time, tag, x^i, u_i) and `<base>.trajmet.bin`
  (17 float64: time, tag, alpha, beta^i, gamma_ij (xx xy xz yy yz zz), proper time,
  E, S_i). Restarts append: the last record of each (time, tag) is kept.
- AthenaK `tab` line outputs: '# Athena++ data at time=...' and a column header line.
"""
import re
import numpy as np


def _last_unique(keys):
    """Indices of the last occurrence of each key (keys: 1-d array or list of tuples)."""
    seen = {}
    for i, k in enumerate(keys):
        seen[k] = i
    idx = np.array(sorted(seen.values(), key=lambda j: keys[j]))
    return idx


def read_status(path):
    """`<base>.horizon_status_N.txt` (docs/FORMATS.md; coord/INTERFACES/cosmo_amr.md 2.3):
    one line per search, column 2 time, column 3 found (0/1), column 4 reason. Restarted
    chains append: the last record of each time is kept. Returns {time: (found, reason)}."""
    out = {}
    with open(path) as f:
        for line in f:
            s = line.split("#")[0].strip()
            if not s:
                continue
            v = s.split()
            out[round(float(v[1]), 9)] = (int(float(v[2])), int(float(v[3])))
    return out


def read_summary(path, status_path=None):
    """Summary of the finder. After a failed search the summary repeats the values of the
    last success (or NaN) (coord/INTERFACES/cosmo_amr.md 2.3): with a status file, 'found'
    is taken from it; without one, a record bitwise equal in mass, area and mean radius to
    the previous record is counted as a repeat, not as a find ('stale')."""
    rows = []
    with open(path) as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            v = s.split()
            if len(v) < 12:
                continue
            rows.append([float(x) for x in v[:12]])
    a = np.array(rows, float)
    # keep the last record of each time (restart appends); time printed with %g
    keys = [round(t, 9) for t in a[:, 1]]
    seen = {}
    for i, k in enumerate(keys):
        seen[k] = i
    order = sorted(seen.items())
    a = a[[i for _, i in order]]
    out = {"iter": a[:, 0], "time": a[:, 1], "mass": a[:, 2], "S": a[:, 6],
           "area": a[:, 7], "meanradius": a[:, 10], "minradius": a[:, 11]}
    finite = np.isfinite(a[:, 2]) & np.isfinite(a[:, 7]) & (a[:, 7] > 0)
    same = np.zeros(a.shape[0], bool)
    same[1:] = ((a[1:, 2] == a[:-1, 2]) & (a[1:, 7] == a[:-1, 7]) & (a[1:, 10] == a[:-1, 10]))
    out["stale_by_repeat"] = finite & same
    if status_path is not None:
        st = read_status(status_path)
        keys = [round(t, 9) for t in a[:, 1]]
        sf = np.array([st.get(k, (0, -1))[0] == 1 for k in keys])
        out["status_reason"] = np.array([st.get(k, (0, -1))[1] for k in keys])
        out["found"] = finite & sf
        out["found_source"] = "status"
    else:
        out["found"] = finite & ~same
        out["found_source"] = "summary, repeats removed"
    with np.errstate(invalid="ignore"):
        out["mirr"] = np.sqrt(a[:, 7] / (16 * np.pi))
    return out


def read_records(path, ncol):
    a = np.fromfile(path, dtype="<f8")
    if a.size % ncol:
        raise ValueError("%s: %d values are not a multiple of %d" % (path, a.size, ncol))
    a = a.reshape(-1, ncol)
    # last record of each (time, tag): sort stably by (time, tag) keeping the later one
    n = a.shape[0]
    order = np.lexsort((np.arange(n), a[:, 1], a[:, 0]))
    b = a[order]
    keep = np.ones(n, bool)
    same = (b[1:, 0] == b[:-1, 0]) & (b[1:, 1] == b[:-1, 1])
    keep[:-1] = ~same          # drop an entry followed by one with the same key
    return b[keep]


class Tracks:
    """Tracked particles on a common time grid: x[t, p], tau[t, p], gamma[t, p, 6]."""

    def __init__(self, traj_path, met_path):
        tr = read_records(traj_path, 8)
        me = read_records(met_path, 17)
        if tr.shape[0] != me.shape[0] or np.any(tr[:, :2] != me[:, :2]):
            raise ValueError("traj and trajmet records do not match")
        times = np.unique(tr[:, 0])
        tags = np.unique(tr[:, 1])
        it = np.searchsorted(times, tr[:, 0])
        ip = np.searchsorted(tags, tr[:, 1])
        nt, npart = times.size, tags.size
        self.t = times
        self.tag = tags
        self.x = np.full((nt, npart, 3), np.nan)
        self.tau = np.full((nt, npart), np.nan)
        self.alpha = np.full((nt, npart), np.nan)
        self.g = np.full((nt, npart, 6), np.nan)
        self.x[it, ip] = tr[:, 2:5]
        self.tau[it, ip] = me[:, 12]
        self.alpha[it, ip] = me[:, 2]
        self.g[it, ip] = me[:, 6:12]
        self.r = np.sqrt((self.x ** 2).sum(-1))

    def at(self, t, q):
        """Linear interpolation in time of q[t, p] (nan where a particle has no record)."""
        i = np.searchsorted(self.t, t) - 1
        i = int(np.clip(i, 0, self.t.size - 2))
        w = (t - self.t[i]) / (self.t[i + 1] - self.t[i])
        return (1 - w) * q[i] + w * q[i + 1]

    def areal_radius(self):
        """Areal radius at every record: r sqrt(gamma_T), gamma_T the mean of the metric
        in the two directions normal to the radial one (spherical symmetry)."""
        n = self.x / self.r[..., None]
        gxx, gxy, gxz, gyy, gyz, gzz = [self.g[..., k] for k in range(6)]
        tr = gxx + gyy + gzz
        nn = (gxx * n[..., 0] ** 2 + gyy * n[..., 1] ** 2 + gzz * n[..., 2] ** 2
              + 2 * (gxy * n[..., 0] * n[..., 1] + gxz * n[..., 0] * n[..., 2]
                     + gyz * n[..., 1] * n[..., 2]))
        gT = 0.5 * (tr - nn)
        return self.r * np.sqrt(gT)


_TIME = re.compile(r"time\s*=\s*([-+0-9.eE]+)")


def read_tab(path):
    """One AthenaK tab line: (time, dict of columns), rows sorted by x1v, duplicate x
    removed (the last one kept)."""
    t = None
    names = None
    rows = []
    with open(path) as f:
        for line in f:
            if line.startswith("#"):
                m = _TIME.search(line)
                if m and t is None:
                    t = float(m.group(1))
                elif "x1v" in line:
                    names = line[1:].split()
                continue
            v = line.split()
            if v:
                rows.append([float(x) for x in v])
    a = np.array(rows, float)
    cols = {n: a[:, k] for k, n in enumerate(names)}
    order = np.argsort(cols["x1v"], kind="stable")
    x = cols["x1v"][order]
    keep = np.ones(x.size, bool)
    keep[:-1] = x[1:] != x[:-1]
    return t, {n: c[order][keep] for n, c in cols.items()}
