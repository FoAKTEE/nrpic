"""Misner-Sharp mass profile and apparent horizon of the slices in AthenaK restart dumps.

    python3 slicemass.py <rundir> [--base NAME] [--out NAME] [--center x,y,z] [--no-fig]

For every restart dump <rundir>/rst/<base>.NNNNN.rst (base found automatically when
the directory holds one) the Z4c state is read and, on every cell,

  R   = r <(gamma_ij t^i t^j)^(1/2)>  over two unit coordinate vectors t orthogonal to
        x - center (areal radius of a spherically symmetric slice),
  K_T = tangential eigenvalue of K^i_j, (t^i K_ij t^j)/(t^i gamma_ij t^j), mean of the two,
  m   = (R/2)(1 - gamma^ij d_i R d_j R + R^2 K_T^2)   (Misner-Sharp mass),

with d_i R by 4th-order centred differences inside each MeshBlock (the stencil of the
two cells next to a block face reaches into the ghost cells stored in the dump). m is
purely geometric; matter only enters through the metric it has produced. For a vacuum
puncture m is the black-hole mass at every R; with matter m(R) rises through the matter
and is flat outside it. An apparent horizon of a spherical slice is a sphere with
2m/R = 1; the outermost one is the outermost crossing of 2m/R = 1 from below (outside)
to above (inside).

Shells are logarithmic in the coordinate radius r = |x - center| (cells are assigned by
the position of their centre): a core shell r < 2 dx_finest, then up to the last complete
sphere (4 root cells inside the mesh boundary). Where a shell is thinner than 2 cells
the statistics are taken over a window of 2 cells centred on it (a thin shell holds
cells at a few lattice radii only; the table shows the window). Per shell: medians of R
and of m, the spread of m about a straight line in R across the window (16-84
percentile half-width s68, min and max; the line removes the radial change of m across
the window, so the spread measures non-sphericity and noise), and 2m/R of the medians.
Printed table: 4 shells per factor of 2.

Trapped region: maximum over the shells (16 per factor 2) of 2m/R (also over the same
shells without widening: windows lower a narrow maximum such as the throat of the
initial puncture slice). Horizon: outermost pair of shells (16 per factor 2) with
2m/R >= 1 inside and < 1 outside; m linear in R between them and R_H = 2 m(R_H) solved,
M_H = R_H/2. Uncertainty of M_H printed as two parts: "shells" = half the largest change
of R_H with 8 or 32 shells per factor 2 or with unwidened shells; "spread of m" = s68 of
m in the two shells / |1 - 2 dm/dR| (how far M_H moves if m moves by its spread, i.e.
the angular variation).

Asymptotic mass: from the outermost shell (4 per factor 2) inward as long as each shell
median stays within 1e-3 m of the median of the shells already taken; median of m over
the cells of those shells. If they span less than a factor 2 in r the profile is
reported NOT FLAT and the median over the outermost factor 2 is given.

Stencil check: |m - shell median| for the cells within 2 cells of a MeshBlock face
(their derivatives use the ghost cells stored in the dump) against the other cells; a
difference would show stale or unfilled ghost cells, e.g. after a regrid.

If <base>.horizon_summary_0.txt exists, the finder row nearest in time to each dump is
printed (mass, mean coordinate radius from column 11, rms expansion) together with R, m
and 2m/R of the slice at that coordinate radius: on an apparent horizon of a spherical
slice R = 2 M_finder and 2m/R = 1.

Figure <out>.pdf/.png in figs/: top, m against R for each dump (medians of 8 shells per
factor of 2, colour = time; band: the spread); for runs where m varies by less than 20 %
the m axis is zoomed on the region outside the horizon and curves may leave it. Bottom,
2m/R with the line 2m/R = 1 (grey) and the finder horizons at their areal radius
2 M_finder on that line (open circles, dump colour); inset: the crossing region, 16 shells
per factor 2. The core shell and shells inside a minimum of R (the second sheet of the
initial puncture slice) are not drawn.

Importable (no work at import): rst_open, rst_params, rst_geometry, slice_fields,
dump_cells, wide, shell, near, sort_cells, shell_edges, profile, crossing, read_finder,
analyse, report, figure, main.

Limits: Z4c restart files only (variables written in front of Z4c in the per-block
record are skipped), Real = double, three-dimensional meshes, one file for all ranks (not
`single_file_per_rank`), no data after the MeshBlock records (the zoom extension); the
slice is assumed spherically symmetric about --center and the coordinates spherically
symmetric too (R is read from the tangential metric); the spread of m measures how far
that holds. Inside the horizon and within a few cells of a puncture m is not
meaningful (finite differences across the puncture).
"""
import glob
import os
import struct
import sys

import numpy as np

NZ4C = 22   # chi, gt_ij(6), Khat, At_ij(6), Gam^i(3), Theta, alpha, beta^i(3)

# fixed part of the binary header after "<par_end>\n" (outputs/restart.cpp, step 1):
# nmb_total, root_level (int), RegionSize (9 Real), RegionIndcs of the mesh and of a
# MeshBlock (19 int each), time, dt (Real), ncycle (int)
_HEAD_FMT = "<ii9d19i19iddi"
_HEAD_LEN = struct.calcsize(_HEAD_FMT)          # 252 bytes with Real = double


# ---------------------------------------------------------------------------------------
# restart reader
# ---------------------------------------------------------------------------------------
def rst_params(path):
    """{(block, key): value string} from the parameter dump at the top of a restart
    file (everything before "<par_end>")."""
    with open(path, "rb") as f:
        head = f.read(1 << 20)
    i = head.find(b"<par_end>")
    txt = head[:i if i >= 0 else len(head)].decode("latin-1")
    par, blk = {}, None
    for line in txt.splitlines():
        line = line.split("#")[0].strip()
        if line.startswith("<"):
            blk = line.strip("<>")
        elif "=" in line and blk is not None:
            k, v = [s.strip() for s in line.split("=", 1)]
            par[(blk, k)] = v
    return par


def rst_open(path, strict=False):
    """Header and memory map of the Z4c variables of an AthenaK restart file.

    Everything is read from the file itself: mesh extent and cell numbers, MeshBlock
    size and ghost cells, time, cycle, the logical location and level of every
    MeshBlock (outputs/restart.cpp steps 1-2) and the size of one MeshBlock's data
    record (the uint64 written in front of the data). The record holds, per MeshBlock,
    hydro, MHD (+ face fields), radiation, forcing and Z4c in this order; the Z4c
    variables are its last NZ4C * cells doubles, so other physics in front is skipped.
    The data start is located by searching the variable-length step 3 (Z4c output time,
    puncture-tracker positions, turbulence RNG state) for a record size whose records
    end exactly at the end of the file.

    Returns a dict (time, dt, ncycle, nmb, root, ng, nx = (nx1, nx2, nx3) active cells
    per MeshBlock, n = with ghosts, mesh_nx, mesh = RegionSize dict, lloc [nmb, 4] =
    lx1, lx2, lx3, level, cost, mm [nmb, NZ4C, n3, n2, n1] memory map, data_size, path),
    or None (ValueError with the reason when strict) if the file cannot be read so."""
    def fail(msg):
        if strict:
            raise ValueError(f"{os.path.basename(path)}: {msg}")
        return None

    with open(path, "rb") as f:
        head = f.read(1 << 20)
        i = head.find(b"<par_end>")
        if i < 0:
            return fail("no <par_end> in the first MB (not an AthenaK restart file)")
        off = i + 10                                      # "<par_end>\n"
        f.seek(off)
        fixed = f.read(_HEAD_LEN)
        if len(fixed) < _HEAD_LEN:
            return fail("file ends inside the header")
        v = struct.unpack(_HEAD_FMT, fixed)
        nmb, root = v[0], v[1]
        ms = dict(zip(("x1min", "x2min", "x3min", "x1max", "x2max", "x3max", "dx1", "dx2",
                       "dx3"), v[2:11]))
        mesh_ind, mb_ind = v[11:30], v[30:49]
        time, dt, ncycle = v[49], v[50], v[51]
        off += _HEAD_LEN
        f.seek(off)
        lloc = np.frombuffer(f.read(16 * nmb), dtype="<i4").reshape(nmb, 4)
        cost = np.frombuffer(f.read(4 * nmb), dtype="<f4")
        off += 20 * nmb
        f.seek(off)
        step3 = f.read(4096)
    par = rst_params(path)
    # the parameter dump must agree with the binary header (checks the struct layout
    # and Real = double)
    try:
        for k in ("x1min", "x1max", "x2min", "x2max", "x3min", "x3max"):
            if abs(float(par[("mesh", k)]) - ms[k]) > 1e-9 * (1 + abs(ms[k])):
                return fail(f"header mesh {k} = {ms[k]!r} differs from the parameter "
                            f"dump ({par[('mesh', k)]}): layout not understood (single "
                            "precision build?)")
        if int(par[("mesh", "nx1")]) != mesh_ind[1] or int(par[("meshblock", "nx1")]) \
                != mb_ind[1]:
            return fail("header cell numbers differ from the parameter dump")
    except KeyError as e:
        return fail(f"parameter dump lacks {e}")
    if not any(b == "z4c" for b, _ in par):
        return fail("no <z4c> block: not a Z4c restart file")
    ng, nx = mb_ind[0], tuple(mb_ind[1:4])
    if min(nx) <= 1:
        return fail(f"MeshBlock {nx}: only three-dimensional meshes are handled")
    n = tuple(k + 2 * ng for k in nx)
    cells = n[0] * n[1] * n[2]
    zbytes = NZ4C * cells * 8
    fsize = os.path.getsize(path)
    cand = []
    for o in range(0, len(step3) - 7):
        ds, = struct.unpack_from("<Q", step3, o)
        if ds >= zbytes and ds % 8 == 0 and off + o + 8 + nmb * ds == fsize:
            cand.append((o, ds))
    if not cand:
        return fail("no MeshBlock record size found that ends at the end of the file "
                    "(data after the MeshBlock records, e.g. zoom, or not one file "
                    "for all ranks)")
    o, ds = cand[0]
    start = off + o + 8
    raw = np.memmap(path, dtype=np.float64, mode="r", offset=start, shape=(nmb, ds // 8))
    mm = raw[:, (ds - zbytes) // 8:].reshape(nmb, NZ4C, n[2], n[1], n[0])
    return dict(time=time, dt=dt, ncycle=ncycle, nmb=nmb, root=root, ng=ng, nx=nx, n=n,
                mesh_nx=tuple(mesh_ind[1:4]), mesh=ms, lloc=lloc, cost=cost, mm=mm,
                data_size=ds, step3=o, path=path)


def _left_edge(i, n, xmin, xmax):
    """LeftEdgeX of coordinates/cell_locations.hpp (same rounding)."""
    x = float(i) / float(n)
    return (x * xmax - x * xmin) - (0.5 * xmax - 0.5 * xmin) + (0.5 * xmin + 0.5 * xmax)


def rst_geometry(h):
    """[(xmin[3], width[3], dx[3])] of every MeshBlock, computed as in
    mesh/meshblock.cpp from the logical location, the level and the mesh of the
    header."""
    ms, out = h["mesh"], []
    lo = [ms["x1min"], ms["x2min"], ms["x3min"]]
    hi = [ms["x1max"], ms["x2max"], ms["x3max"]]
    nx = np.array(h["nx"], dtype=float)
    for lx1, lx2, lx3, L in h["lloc"]:
        a, b = np.empty(3), np.empty(3)
        for d, l in enumerate((lx1, lx2, lx3)):
            nmbx = (h["mesh_nx"][d] // h["nx"][d]) << int(L - h["root"])
            a[d] = lo[d] if l == 0 else _left_edge(l, nmbx, lo[d], hi[d])
            b[d] = hi[d] if l == nmbx - 1 else _left_edge(l + 1, nmbx, lo[d], hi[d])
        w = b - a
        out.append((a, w, w / nx))
    return out


# ---------------------------------------------------------------------------------------
# Misner-Sharp mass on one MeshBlock
# ---------------------------------------------------------------------------------------
def slice_fields(xmin, dx, u, ng, center=(0.0, 0.0, 0.0), M=1.0):
    """Misner-Sharp mass etc. on the active cells of one MeshBlock.

    u = Z4c variables [NZ4C, n3, n2, n1] with ng ghost cells, xmin the MeshBlock corner,
    dx the cell size (scalar or per direction). Returns flattened arrays over the active
    cells: R (areal radius), m (Misner-Sharp mass), dtR = d_t R at fixed x
    (-alpha R K_T + beta^i d_i R), cK = ((alpha^2 - beta_i beta^i)/(1 - 2M/R))^(1/2) (the
    Killing normalisation of d_t for Schwarzschild of mass M), r = |x - center| and the
    cell-centre coordinates x, y, z."""
    if ng < 2:
        raise ValueError("4th-order differences need nghost >= 2")
    dx = np.broadcast_to(np.asarray(dx, dtype=float), (3,))
    n3, n2, n1 = u.shape[-3:]
    cx = (np.arange(n1) - ng + 0.5) * dx[0]
    cy = (np.arange(n2) - ng + 0.5) * dx[1]
    cz = (np.arange(n3) - ng + 0.5) * dx[2]
    z, y, x = np.meshgrid(xmin[2] + cz, xmin[1] + cy, xmin[0] + cx, indexing="ij")
    X, Y, Z = x - center[0], y - center[1], z - center[2]
    chi, gt, Kh, At, Th, alp, beta = u[0], u[1:7], u[7], u[8:14], u[17], u[18], u[19:22]
    g = gt / chi
    K = At / chi + (Kh + 2 * Th) / 3 * g

    def full(s):
        xx, xy, xz, yy, yz, zz = s
        return np.array([[xx, xy, xz], [xy, yy, yz], [xz, yz, zz]])
    G, KK = full(g), full(K)
    r = np.sqrt(X * X + Y * Y + Z * Z)
    nn = np.stack([X, Y, Z]) / r
    ez = np.abs(nn[2]) < 0.9
    ref = np.stack([np.where(ez, 0.0, 1.0), 0 * r, np.where(ez, 1.0, 0.0)])
    t1 = np.cross(ref, nn, axis=0)
    t1 /= np.sqrt((t1 ** 2).sum(0))
    t2 = np.cross(nn, t1, axis=0)
    quad = lambda T, a: np.einsum("i...,ij...,j...->...", a, T, a)
    g1, g2 = quad(G, t1), quad(G, t2)
    R = r * 0.5 * (np.sqrt(g1) + np.sqrt(g2))
    KT = 0.5 * (quad(KK, t1) / g1 + quad(KK, t2) / g2)

    def dd(f, ax):
        h = dx[2 - ax]                        # array axes (z, y, x)
        return (-np.roll(f, -2, ax) + 8 * np.roll(f, -1, ax) - 8 * np.roll(f, 1, ax)
                + np.roll(f, 2, ax)) / (12 * h)
    dR = np.stack([dd(R, 2), dd(R, 1), dd(R, 0)])
    Gi = np.moveaxis(np.linalg.inv(np.moveaxis(G, (0, 1), (-2, -1))), (-2, -1), (0, 1))
    m = R / 2 * (1 - np.einsum("i...,ij...,j...->...", dR, Gi, dR) + (R * KT) ** 2)
    dtR = -alp * R * KT + (beta * dR).sum(0)
    b2 = (beta * np.einsum("ij...,j...->i...", G, beta)).sum(0)
    cK = np.sqrt(np.abs(alp ** 2 - b2) / np.abs(1 - 2 * M / R))
    s = (slice(ng, n3 - ng), slice(ng, n2 - ng), slice(ng, n1 - ng))
    return {k: v[s].ravel() for k, v in dict(R=R, m=m, dtR=dtR, cK=cK, r=r, x=x, y=y,
                                              z=z).items()}


def dump_cells(h, geo=None, center=(0.0, 0.0, 0.0), rmax=np.inf, keys=("R", "m", "r")):
    """slice_fields over the MeshBlocks of a dump that reach within rmax of center,
    concatenated. Adds per cell: dx (largest cell size of its MeshBlock), level and
    face (True if the cell is within 2 cells of a MeshBlock face, i.e. its derivative
    stencil uses ghost cells)."""
    geo = rst_geometry(h) if geo is None else geo
    c = np.asarray(center, dtype=float)
    acc = {}
    nx = h["nx"]
    ei = [np.minimum(np.arange(k), np.arange(k)[::-1]) for k in nx]
    edge = np.minimum.reduce(np.meshgrid(ei[2], ei[1], ei[0], indexing="ij")).ravel()
    face = edge < 2
    for b, (xmin, w, dx) in enumerate(geo):
        lo = xmin - c
        dmin = np.sqrt((np.maximum(0, np.maximum(lo, -(lo + w))) ** 2).sum())
        if dmin > rmax:
            continue
        f = slice_fields(xmin, dx, np.asarray(h["mm"][b]), h["ng"], center=c)
        for k in keys:
            acc.setdefault(k, []).append(f[k])
        acc.setdefault("dx", []).append(np.full(f["r"].size, dx.max()))
        acc.setdefault("level", []).append(np.full(f["r"].size, h["lloc"][b, 3], np.int16))
        acc.setdefault("face", []).append(face)
    return {k: np.concatenate(v) for k, v in acc.items()}


# ---------------------------------------------------------------------------------------
# summaries over cells (h: dict of per-cell arrays R, m, r, ...)
# ---------------------------------------------------------------------------------------
def shell(h, key, R, half=0.1):
    """Median and range over |R' - R| < half, cells with coordinate r < 1 left out."""
    s = (np.abs(h["R"] - R) < half) & (h["r"] > 1.0)
    v = h[key][s]
    return np.median(v), v.min(), v.max()


def wide(h, key, lo, hi):
    """Median and range over lo < R < hi; cells with coordinate r < 1 are left out
    (on the t = 0 slice R grows again towards the puncture, the second sheet)."""
    s = (h["R"] > lo) & (h["R"] < hi) & (h["r"] > 1.0)
    v = h[key][s]
    return np.median(v), v.min(), v.max()


def near(h, key, X, rad=0.5):
    """Median over the cells within rad of the point X."""
    s = (h["x"] - X[0]) ** 2 + (h["y"] - X[1]) ** 2 + (h["z"] - X[2]) ** 2 < rad ** 2
    return np.median(h[key][s]) if s.any() else np.nan


def shell_edges(r_in, r_out, nper2):
    """[0, r_in, ..., r_out]: a core shell, then nper2 logarithmic shells per factor 2."""
    k = max(1, int(np.ceil(np.log2(r_out / r_in) * nper2)))
    return np.concatenate([[0.0], r_in * (r_out / r_in) ** (np.arange(k + 1) / k)])


PROFILE_KEYS = ("n", "r", "R", "m", "m16", "m84", "mmin", "mmax", "q", "q16", "q84",
                "dxmin", "dxmax", "lo", "hi")


def sort_cells(c):
    """Cells with finite R and m, sorted by r (input of profile)."""
    ok = np.isfinite(c["m"]) & np.isfinite(c["R"])
    o = np.nonzero(ok)[0]
    o = o[np.argsort(c["r"][o], kind="stable")]
    return {k: v[o] for k, v in c.items()}


def _spread(R, v):
    """Residuals of v about its least-squares straight line in R (removes the radial
    variation across a shell, leaves the angular part and the noise)."""
    dR = R - R.mean()
    var = (dR * dR).mean()
    b = (dR * (v - v.mean())).mean() / var if var > 0 else 0.0
    return v - b * dR - np.median(v - b * dR)


WIN_CELLS = 1.0    # statistics windows are at least 2 x 1.0 = 2 cells wide in r


def profile(cs, edges, nmin=8, wcells=WIN_CELLS):
    """Per shell [edges[i], edges[i+1]) of the r-sorted cells cs (edges[0] = 0: core),
    statistics over a window in r: the shell itself, or, where the shell is thinner
    than 2 wcells times the largest cell size in it, a window of that width centred on
    the shell, cut at edges[1] and edges[-1] (a thin shell holds cells at a few
    lattice radii only, and its median then depends on which). Returned per shell: the
    window (lo, hi), number of cells, medians of r, R and m, q = 2 m/R of the medians,
    the 16/84 percentiles and the range of m and the 16/84 percentiles of the per-cell
    2m/R, both about a straight line in R across the window (the spread, added to the
    median), smallest and largest cell size. Windows with fewer than nmin cells are
    NaN."""
    ns = len(edges) - 1
    r = cs["r"]
    P = {k: np.full(ns, np.nan) for k in PROFILE_KEYS}
    P["lo"], P["hi"] = edges[:-1].copy(), edges[1:].copy()
    nb = np.searchsorted(r, edges, side="left")
    for i in range(1, ns):
        lo, hi = edges[i], edges[i + 1]
        k0, k1 = nb[i], nb[i + 1]
        if k1 > k0:
            dxs = cs["dx"][k0:k1].max()
        else:
            dxs = cs["dx"][min(k0, len(r) - 1)]
        half = wcells * dxs
        if hi - lo < 2 * half:
            c = 0.5 * (lo + hi)
            P["lo"][i], P["hi"][i] = max(c - half, edges[1]), min(c + half, edges[-1])
    for i in range(ns):
        k0, k1 = np.searchsorted(r, [P["lo"][i], P["hi"][i]], side="left")
        P["n"][i] = k1 - k0
        if k1 - k0 < nmin:
            continue
        s = slice(k0, k1)
        R, m = cs["R"][s], cs["m"][s]
        P["r"][i], P["R"][i], P["m"][i] = np.median(r[s]), np.median(R), np.median(m)
        P["q"][i] = 2 * P["m"][i] / P["R"][i]
        e = _spread(R, m)
        p16, p84 = np.percentile(e, [16, 84])
        P["m16"][i], P["m84"][i] = P["m"][i] + p16, P["m"][i] + p84
        P["mmin"][i], P["mmax"][i] = P["m"][i] + e.min(), P["m"][i] + e.max()
        p16, p84 = np.percentile(_spread(R, 2 * m / R), [16, 84])
        P["q16"][i], P["q84"][i] = P["q"][i] + p16, P["q"][i] + p84
        P["dxmin"][i], P["dxmax"][i] = cs["dx"][s].min(), cs["dx"][s].max()
    return P


def crossing(P):
    """Outermost crossing of 2m/R = 1 (shell medians: 2m/R >= 1 inside, < 1 outside).
    Between the two shells m is taken linear in R and R = 2 m(R) solved (exact when m
    is flat). Returns None if 2m/R < 1 in every shell, else a dict: RH (NaN if
    2m/R >= 1 up to the outermost shell), shell indices i (inside), j (outside), their
    median r, dR = R_j - R_i, dm/dR, the cell size, ms68 = mean 16-84 half-width of m
    in the two shells, and dRH_spread = 2 ms68 / |1 - 2 dm/dR| (the change of R_H if m
    moves by ms68)."""
    s = np.nonzero(np.isfinite(P["q"]))[0]
    above = np.nonzero(P["q"][s] >= 1)[0]
    if not len(above):
        return None
    k = above[-1]
    if k == len(s) - 1:
        return dict(RH=np.nan, i=s[k], j=None)
    i, j = s[k], s[k + 1]
    Ri, Rj, mi, mj = P["R"][i], P["R"][j], P["m"][i], P["m"][j]
    dm = (mj - mi) / (Rj - Ri)
    RH = 2 * (mi - dm * Ri) / (1 - 2 * dm)
    ms = 0.25 * ((P["m84"][i] - P["m16"][i]) + (P["m84"][j] - P["m16"][j]))
    return dict(RH=RH, i=i, j=j, ri=P["r"][i], rj=P["r"][j], dR=Rj - Ri, dmdR=dm,
                dx=max(P["dxmax"][i], P["dxmax"][j]), ms68=ms,
                dRH_spread=2 * ms / abs(1 - 2 * dm))


def outer_sheet(P):
    """Indices of the valid shells from the outermost inward as long as the median R
    does not increase (drops the second sheet inside a minimum of R)."""
    s = np.nonzero(np.isfinite(P["R"]))[0]
    if not len(s):
        return s
    k = len(s) - 1
    while k > 0 and P["R"][s[k - 1]] <= P["R"][s[k]]:
        k -= 1
    return s[k:]


def read_finder(path):
    """Horizon-finder summary (<base>.horizon_summary_0.txt) as rows of time, mass,
    mean coordinate radius (column 11), area, rms expansion; rows where the finder
    found nothing have NaN mass. Restarts append: the last row of each time is kept."""
    rows = []
    if not os.path.exists(path):
        return np.zeros((0, 5))
    for line in open(path):
        if line.startswith("#"):
            continue
        x = line.split()
        if len(x) >= 11:
            rows.append([float(x[1]), float(x[2]), float(x[10]), float(x[7]),
                         float(x[8])])
    if not rows:
        return np.zeros((0, 5))
    a = np.array(rows)
    _, idx = np.unique(a[::-1, 0], return_index=True)
    return a[::-1][idx]


def _interp_r(P, rq, key):
    """Shell medians of key interpolated linearly in the median r."""
    s = np.nonzero(np.isfinite(P["r"]) & np.isfinite(P[key]))[0]
    if not len(s) or rq < P["r"][s[0]] or rq > P["r"][s[-1]]:
        return np.nan
    return float(np.interp(rq, P["r"][s], P[key][s]))


# ---------------------------------------------------------------------------------------
# one dump
# ---------------------------------------------------------------------------------------
NPER2_PRINT, NPER2_FIG, NPER2_H = 4, 8, 16
FLAT_TOL = 1e-3


def analyse(h, center=(0.0, 0.0, 0.0), finder=None):
    """Everything the command line prints and plots for one opened dump."""
    geo = rst_geometry(h)
    c = np.asarray(center, dtype=float)
    ms = h["mesh"]
    lo = np.array([ms["x1min"], ms["x2min"], ms["x3min"]]) - c
    hi = np.array([ms["x1max"], ms["x2max"], ms["x3max"]]) - c
    root_dx = max(ms["dx1"], ms["dx2"], ms["dx3"])
    r_out = min(np.min(-lo), np.min(hi)) - 4 * root_dx      # last complete sphere
    cs = sort_cells(dump_cells(h, geo, c, rmax=r_out))
    cut = np.searchsorted(cs["r"], r_out)
    cs = {k: v[:cut] for k, v in cs.items()}
    dx_min = min(g[2].min() for g in geo)
    r_in = 2 * dx_min
    lev = h["lloc"][:, 3]
    A = dict(time=h["time"], ncycle=h["ncycle"], nmb=h["nmb"], levels=np.unique(lev),
             nlev={int(L): int((lev == L).sum()) for L in np.unique(lev)},
             dx_min=dx_min, dx_max=max(g[2].max() for g in geo), r_in=r_in, r_out=r_out,
             ncells=cut, nx=h["nx"],
             tile=sum(np.prod(g[1]) for g in geo) / np.prod(hi - lo) - 1)
    A["P"] = {k: profile(cs, shell_edges(r_in, r_out, k))
              for k in (NPER2_PRINT, NPER2_FIG, NPER2_H, 2 * NPER2_H)}
    A["P"]["thin"] = profile(cs, shell_edges(r_in, r_out, NPER2_H), wcells=0.0)
    # asymptotic mass: from the outermost shell inward while each shell median stays
    # within FLAT_TOL of the median of the shells already taken
    P = A["P"][NPER2_PRINT]
    s = np.nonzero(np.isfinite(P["m"]))[0]
    inc = [s[-1]]
    for k in s[-2::-1]:
        ref = np.median(P["m"][inc])
        if abs(P["m"][k] - ref) > FLAT_TOL * abs(ref):
            A["flat_break"] = k
            break
        inc.append(k)
    else:
        A["flat_break"] = None
    r_a = P["lo"][inc[-1]]
    A["flat"] = r_out / r_a >= 2.0 - 1e-9
    if not A["flat"]:                         # outermost factor 2 instead
        r_a = r_out / 2
    i0, i1 = np.searchsorted(cs["r"], [r_a, r_out])
    A["m_inf"] = np.median(cs["m"][i0:i1])
    A["flat_r"] = (r_a, r_out)
    A["flat_R"] = (np.median(cs["R"][i0:min(i0 + 1000, i1)]), np.median(cs["R"][max(i1 - 1000, i0):i1]))
    sel = [k for k in inc if P["lo"][k] >= r_a - 1e-12]
    A["flat_dev"] = np.max(np.abs(P["m"][sel] - A["m_inf"]))
    # trapped region and horizon
    PH = A["P"][NPER2_H]
    A["qmax"] = np.nanmax(PH["q"])
    A["qmax_r"] = PH["r"][np.nanargmax(PH["q"])]
    A["qmax_core"] = bool(np.nanargmax(PH["q"]) == 0)
    PT = A["P"]["thin"]
    A["qmax_thin"] = np.nanmax(PT["q"])
    A["qmax_thin_r"] = PT["r"][np.nanargmax(PT["q"])]
    A["X"] = {k: crossing(A["P"][k]) for k in (NPER2_FIG, NPER2_H, 2 * NPER2_H, "thin")}
    X = A["X"][NPER2_H]
    if X is not None and np.isfinite(X["RH"]):
        alt = [A["X"][k]["RH"] if A["X"][k] is not None else np.nan
               for k in (NPER2_FIG, 2 * NPER2_H, "thin")]
        A["RH_alt"] = alt
        A["dMH_shell"] = 0.5 * np.nanmax(np.abs(np.array(alt) - X["RH"]))
        A["dMH_spread"] = 0.5 * X["dRH_spread"]
    # stencil check: cells next to MeshBlock faces (derivatives use the dump's ghost
    # cells) against interior cells, deviation from their shell median, outside the core
    e = shell_edges(r_in, r_out, NPER2_FIG)
    idx = np.clip(np.searchsorted(e, cs["r"], side="right") - 1, 0, len(e) - 2)
    dev = np.abs(cs["m"] - A["P"][NPER2_FIG]["m"][idx]) / abs(A["m_inf"])
    good = np.isfinite(dev) & (cs["r"] >= r_in) & (cs["r"] < r_out)
    f, g = good & cs["face"], good & ~cs["face"]
    A["face_dev"] = (np.median(dev[f]), dev[f].max(), np.median(dev[g]), dev[g].max(),
                     int(f.sum()), int(g.sum()))
    # second sheet (minimum of R)
    P8 = A["P"][NPER2_FIG]
    sh = outer_sheet(P8)
    A["sheet"] = sh
    valid = np.nonzero(np.isfinite(P8["R"]))[0]
    A["second_sheet"] = bool(len(sh) and sh[0] > valid[0])
    # finder
    A["finder"] = None
    if finder is not None and len(finder):
        j = int(np.argmin(np.abs(finder[:, 0] - h["time"])))
        t, Mf, rf, area, hrms = finder[j]
        F = dict(t=t, M=Mf, r=rf, area=area, hrms=hrms)
        if np.isfinite(Mf):
            for k in ("R", "q", "m"):
                F[k] = _interp_r(PH, rf, k)
        A["finder"] = F
    return A


def _row(P, i):
    if not np.isfinite(P["m"][i]):
        return f"    {P['lo'][i]:8.4g}-{P['hi'][i]:<8.4g}{int(P['n'][i]):9d}   (too few cells)"
    dxs = (f"{P['dxmin'][i]:.4g}" if P["dxmin"][i] == P["dxmax"][i]
           else f"{P['dxmin'][i]:.4g}-{P['dxmax'][i]:.4g}")
    return (f"    {P['lo'][i]:8.4g}-{P['hi'][i]:<8.4g}{int(P['n'][i]):9d} {P['R'][i]:10.5f} "
            f"{P['m'][i]:10.6f} {0.5 * (P['m84'][i] - P['m16'][i]):9.2e} "
            f"{P['mmin'][i] - P['m'][i]:+9.2e} {P['mmax'][i] - P['m'][i]:+9.2e} "
            f"{P['q'][i]:9.5f}  {dxs}")


_HEAD = ("      r window          cells     R          m         s68     min-med   "
         "max-med     2m/R    dx")


def report(A, pr=print):
    """Print the summary of one dump."""
    lv = ", ".join(f"{L}: {n}" for L, n in A["nlev"].items())
    pr(f"t = {A['time']:.4f} (cycle {A['ncycle']}): {A['nmb']} MeshBlocks of "
       f"{'x'.join(str(k) for k in A['nx'])} cells on levels {A['levels'].min()}.."
       f"{A['levels'].max()} (per level {lv}), dx = {A['dx_min']:.5g} .. "
       f"{A['dx_max']:.5g}; block volumes sum to the mesh volume x (1 {A['tile']:+.0e}); "
       f"{A['ncells']} cells within r = {A['r_out']:.4g}")
    P = A["P"][NPER2_PRINT]
    pr(f"  shells in r, {NPER2_PRINT} per factor 2 (core r < {A['r_in']:.4g}; windows widened "
       f"to {2 * WIN_CELLS:g} cells where thinner): medians of R and m, spread of m about a "
       "straight line in R across the window (s68 = 16-84 half-width, min and max minus "
       "median), 2m/R of the medians, cell sizes")
    pr(_HEAD)
    for i in range(len(P["n"])):
        pr(_row(P, i))
    fr, fR = A["flat_r"], A["flat_R"]
    if A["flat"]:
        pr(f"  asymptotic mass m = {A['m_inf']:.6f} (m - 1 = {A['m_inf'] - 1:+.2e}): median "
           f"over r = {fr[0]:.4g}..{fr[1]:.4g} (R = {fR[0]:.4g}..{fR[1]:.4g}), where the "
           f"shell medians agree to {A['flat_dev']:.1e} (tolerance {FLAT_TOL:g} m)"
           + ("" if A["flat_break"] is None else
              f"; the next shell inward (r = {P['lo'][A['flat_break']]:.4g}..) has m = "
              f"{P['m'][A['flat_break']]:.6f}"))
    else:
        pr(f"  NOT FLAT: the outermost shells differ by more than {FLAT_TOL:g} m within a "
           f"factor 2 in r; median over r = {fr[0]:.4g}..{fr[1]:.4g}: m = {A['m_inf']:.6f} "
           f"(shell medians differ from it by up to {A['flat_dev']:.1e})")
    if A["second_sheet"]:
        P8 = A["P"][NPER2_FIG]
        k = A["sheet"][0]
        pr(f"  R has a minimum at r = {P8['r'][k]:.3g} (R = {P8['R'][k]:.5f}); shells "
           "inside it lie on the second sheet")
    fd = A["face_dev"]
    pr(f"  stencil check, |m - shell median|/m for r = {A['r_in']:.3g}..{A['r_out']:.4g}: "
       f"median {fd[0]:.1e} (max {fd[1]:.1e}) over the {fd[4]} cells within 2 cells of a "
       f"MeshBlock face, {fd[2]:.1e} (max {fd[3]:.1e}) over the {fd[5]} others")
    X = A["X"][NPER2_H]
    pr(f"  max 2m/R over shells ({NPER2_H} per factor 2) = {A['qmax']:.5f} at r = "
       f"{A['qmax_r']:.3g}" + (" (core shell)" if A["qmax_core"] else "")
       + f"; over the same shells not widened {A['qmax_thin']:.5f} at r = "
       f"{A['qmax_thin_r']:.3g}")
    if X is None:
        pr("  trapped region: none (2m/R < 1 in every shell)")
    elif not np.isfinite(X["RH"]):
        pr("  trapped region: 2m/R >= 1 up to the outermost shell (no crossing)")
    else:
        alt = A["RH_alt"]
        pr(f"  trapped region: yes; outermost 2m/R = 1 at R_H = {X['RH']:.5f} (between "
           f"shells at r = {X['ri']:.4g} and {X['rj']:.4g}), M_H = R_H/2 = "
           f"{X['RH'] / 2:.6f} +- {A['dMH_shell']:.1e} (shells) +- {A['dMH_spread']:.1e} "
           "(spread of m)")
        pr(f"    shells {NPER2_H} per factor 2: dR = {X['dR']:.4f}, dm/dR = {X['dmdR']:+.2e}, "
           f"cell size {X['dx']:.4g}, s68 of m {X['ms68']:.1e}; R_H with {NPER2_FIG} and "
           f"{2 * NPER2_H} shells per factor 2: {alt[0]:.5f}, {alt[1]:.5f}, with {NPER2_H} not "
           f"widened: {alt[2]:.5f}")
        PH = A["P"][NPER2_H]
        pr("    shells around the crossing:")
        pr("  " + _HEAD)
        for i in range(max(X["i"] - 2, 0), min(X["j"] + 3, len(PH["n"]))):
            pr("  " + _row(PH, i))
    F = A["finder"]
    if F is not None:
        if not np.isfinite(F["M"]):
            pr(f"  finder: nearest row (t = {F['t']:.4f}) has no horizon")
        else:
            pr(f"  finder at t = {F['t']:.4f} (dt = {F['t'] - A['time']:+.3g}): M = "
               f"{F['M']:.6f} (R = 2M = {2 * F['M']:.5f}), mean coordinate radius "
               f"{F['r']:.4f}, rms expansion {F['hrms']:.1e}; slice at that r: R = "
               f"{F['R']:.5f}, m = {F['m']:.6f}, 2m/R = {F['q']:.5f}")


# ---------------------------------------------------------------------------------------
# figure
# ---------------------------------------------------------------------------------------
def figure(res, path):
    """Top: m(R) per dump; bottom: 2m/R with the finder horizons; inset: zoom on the
    crossing. Returns the files written."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import common  # noqa: F401  (puts python/ on sys.path)
    from nrpic import figstyle as fs

    fs.use_style()
    W, H = fs.FULL_WIDTH, 5.8
    fig = plt.figure(figsize=(W, H))
    left, right, bot, top, gap = 0.86, 0.10, 0.52, 0.08, 0.06
    hh = (H - bot - top - gap) / 2
    aq = fs.inch_axes(fig, left, bot, W - left - right, hh)
    am = fs.inch_axes(fig, left, bot + hh + gap, W - left - right, hh)
    cols = fs.series_colors(len(res), cmap="viridis")
    allm, Rlo, Rhi, qtop = [], np.inf, 0.0, 1.25
    curves = []
    for A, col in zip(res, cols):
        P = A["P"][NPER2_FIG]
        s = A["sheet"]
        s = s[P["lo"][s] >= A["r_in"]]              # core shell left out
        if not len(s):
            continue
        R = P["R"][s]
        am.plot(R, P["m"][s], color=col, lw=1.2, label=f"$t={A['time']:.3g}$")
        fs.band(am, R, P["m16"][s], P["m84"][s], col)
        aq.plot(R, P["q"][s], color=col, lw=1.2)
        fs.band(aq, R, P["q16"][s], P["q84"][s], col)
        curves.append((A, col, s))
        allm.append(P["m"][s])
        Rlo, Rhi = min(Rlo, R.min()), max(Rhi, R.max())
        qtop = max(qtop, np.nanmax(P["q"][s]) * 1.05)
    allm = np.concatenate(allm)
    lo, hi = np.nanpercentile(allm, 1), np.nanpercentile(allm, 99)
    mref = max(abs(A["m_inf"]) for A in res)
    if hi - lo < 0.2 * mref:
        # vacuum-like: zoom on the part outside the horizon (10-90 percentiles of the
        # shell medians there); curves leaving the range are clipped
        v = []
        for A, _, s in curves:
            X = A["X"][NPER2_H]
            Rc = 1.05 * X["RH"] if X is not None and np.isfinite(X["RH"]) else 0.0
            P = A["P"][NPER2_FIG]
            v.append(P["m"][s][P["R"][s] > Rc])
        v = np.concatenate(v)
        lo, hi = np.nanpercentile(v, 10), np.nanpercentile(v, 90)
        pad = max(0.3 * (hi - lo), 3e-4 * mref)
        am.set_ylim(lo - pad, hi + 2.5 * pad)
    else:
        am.set_ylim(min(0.0, lo) - 0.04 * mref, hi + 0.3 * mref)
        # inset: m where it is within 5 % of the asymptotic mass, zoomed
        v, Rmin = [], np.inf
        for A, _, s in curves:
            P = A["P"][NPER2_FIG]
            k = s[np.abs(P["m"][s] / A["m_inf"] - 1) < 0.05]
            if len(k):
                v.append(P["m"][k])
                Rmin = min(Rmin, P["R"][k].min())
        if v:
            v = np.concatenate(v)
            zlo, zhi = np.nanpercentile(v, 2), np.nanpercentile(v, 98)
            pad = max(0.15 * (zhi - zlo), 1e-3 * mref)
            az = am.inset_axes([0.5, 0.2, 0.47, 0.45])
            for A, col, s in curves:
                P = A["P"][NPER2_FIG]
                az.plot(P["R"][s], P["m"][s], color=col, lw=1.2)
                fs.band(az, P["R"][s], P["m16"][s], P["m84"][s], col)
            az.set_xscale("log")
            az.set_xlim(Rmin / 1.05, Rhi * 1.08)
            az.set_ylim(zlo - pad, zhi + pad)
            az.xaxis.set_major_locator(matplotlib.ticker.LogLocator(10, subs=(1.0, 2.0, 5.0)))
            az.xaxis.set_minor_locator(matplotlib.ticker.LogLocator(10, subs="auto"))
            az.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
            az.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, _: f"{x:g}"))
            az.tick_params(labelsize="small")
            az.ticklabel_format(axis="y", useOffset=False)
            az.set_xlabel("$R$", fontsize="small", labelpad=1)
            az.set_ylabel("$m$", fontsize="small", labelpad=1)
    for ax in (am, aq):
        ax.set_xscale("log")
        ax.set_xlim(Rlo / 1.08, Rhi * 1.08)
        ax.xaxis.set_major_locator(matplotlib.ticker.LogLocator(10, subs=(1.0, 2.0, 5.0)))
        ax.xaxis.set_minor_locator(matplotlib.ticker.LogLocator(10, subs="auto"))
        ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    aq.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}"))
    aq.axhline(1.0, **fs.MASK_LINE)
    aq.set_ylim(0.0, min(qtop, 2.0))
    am.xaxis.set_major_formatter(matplotlib.ticker.NullFormatter())
    am.ticklabel_format(axis="y", useOffset=False)
    am.set_ylabel(r"Misner-Sharp mass $m$")
    aq.set_ylabel(r"$2m/R$")
    aq.set_xlabel(r"areal radius $R$", labelpad=1)
    for ax in (am, aq):
        ax.yaxis.set_label_coords(-0.085, 0.5)
    am.legend(loc="upper left", ncol=min(len(res), 6), fontsize="small", handlelength=1.4,
              columnspacing=1.0, borderaxespad=0.3)
    have_f = [(A, col) for A, col, _ in curves
              if A["finder"] is not None and np.isfinite(A["finder"]["M"])]
    have_x = [A["X"][NPER2_H]["RH"] for A, _, _ in curves
              if A["X"][NPER2_H] is not None and np.isfinite(A["X"][NPER2_H]["RH"])]
    mk = dict(ls="none", marker="o", ms=6, mfc="none", mew=1.2, zorder=6, clip_on=False)
    for A, col in have_f:
        aq.plot(2 * A["finder"]["M"], 1.0, mec=col, **mk)
    # inset: the crossing region, linear axes
    if have_x or have_f:
        xs = have_x + [2 * A["finder"]["M"] for A, _ in have_f]
        xc = np.median(have_x) if have_x else np.median(xs)
        half = max(0.06 * xc, 1.3 * max(abs(x - xc) for x in xs))
        ai = aq.inset_axes([0.54, 0.34, 0.33, 0.54])
        for A, col, s in curves:
            P = A["P"][NPER2_H]
            k = outer_sheet(P)
            k = k[(P["lo"][k] >= A["r_in"]) & (np.abs(P["R"][k] - xc) < 2 * half)]
            ai.plot(P["R"][k], P["q"][k], color=col, lw=1.2)
        for A, col in have_f:
            ai.plot(2 * A["finder"]["M"], 1.0, mec=col, **{**mk, "clip_on": True})
        ai.axhline(1.0, **fs.MASK_LINE)
        ai.set_xlim(xc - half, xc + half)
        ai.set_ylim(1 - 0.5 * half / xc * 1.2, 1 + 0.5 * half / xc * 1.2)
        ai.tick_params(labelsize="small")
        ai.set_xlabel("$R$", fontsize="small", labelpad=1)
        ai.set_ylabel("$2m/R$", fontsize="small", labelpad=1)
        aq.indicate_inset_zoom(ai, edgecolor="grey", alpha=0.6)
    if have_f:
        hd = [matplotlib.lines.Line2D([], [], **{**mk, "mec": "k"},
                                      label=r"finder: $R=2M_{\rm finder}$")]
        aq.legend(handles=hd, loc="upper right", fontsize="small", handletextpad=0.3,
                  borderaxespad=0.3)
    return fs.save(fig, path)


# ---------------------------------------------------------------------------------------
# command line
# ---------------------------------------------------------------------------------------
def find_bases(d):
    from common import run_path
    pat = run_path(d, "rst", "*.[0-9][0-9][0-9][0-9][0-9].rst")
    return sorted({os.path.basename(p).rsplit(".", 2)[0] for p in glob.glob(pat)})


def main(argv):
    from common import FIGS, parse_cli, run_path
    runs, opts = parse_cli(argv, options=("base", "out", "center"))
    if not runs:
        sys.exit(__doc__)
    label, d = runs[0]
    bases = find_bases(d)
    base = opts.get("base") or (bases[0] if len(bases) == 1 else None)
    if base is None:
        sys.exit(f"{d}/rst holds dumps of the basenames {bases}: give --base")
    out = opts.get("out", f"slicemass_{label}")
    center = tuple(float(v) for v in str(opts.get("center", "0,0,0")).split(","))
    files = sorted(glob.glob(run_path(d, "rst", f"{base}.[0-9][0-9][0-9][0-9][0-9].rst")))
    finder = read_finder(run_path(d, f"{base}.horizon_summary_0.txt"))
    print(f"run {d}: {len(files)} restart dumps rst/{base}.NNNNN.rst, centre {center}; "
          f"finder summary {base}.horizon_summary_0.txt: "
          + (f"{len(finder)} rows, {int(np.isfinite(finder[:, 1]).sum())} with a horizon"
             if len(finder) else "absent"))
    res = []
    for p in files:
        try:
            h = rst_open(p, strict=True)
        except ValueError as e:
            print(f"\n{e}; skipped")
            continue
        nvar = h["data_size"] / (8 * np.prod(h["n"]))
        print(f"\n{os.path.basename(p)}: {h['data_size']} bytes per MeshBlock ({nvar:g} x "
              f"{'x'.join(str(k) for k in h['n'])} doubles), Z4c = the last {NZ4C}")
        A = analyse(h, center, finder)
        report(A)
        res.append(A)
    if not res:
        sys.exit("no readable dumps")
    print("\nsummary: t, MeshBlocks, asymptotic m, max 2m/R, M_H = R_H/2 +- shells +- "
          "spread of m, finder mass at the nearest row")
    for A in res:
        X = A["X"][NPER2_H]
        F = A["finder"]
        mh = (f"{X['RH'] / 2:.5f} +- {A['dMH_shell']:.0e} +- {A['dMH_spread']:.0e}"
              if X is not None and np.isfinite(X["RH"]) else "no crossing")
        fm = ("-" if F is None else f"none at t = {F['t']:.4g}" if not np.isfinite(F["M"])
              else f"{F['M']:.5f} at t = {F['t']:.4g}")
        print(f"  t = {A['time']:8.3f}: {A['nmb']:4d} MB, m_inf = {A['m_inf']:.6f}"
              + ("" if A["flat"] else " (NOT FLAT)") + f", max 2m/R = {A['qmax']:.4f} "
              f"({A['qmax_thin']:.4f} unwidened), "
              f"M_H = {mh}; finder {fm}")
    if "no-fig" not in opts:
        print("\n".join(figure(res, out if os.path.isabs(out) else os.path.join(FIGS, out))))
    return res


if __name__ == "__main__":
    main(sys.argv[1:])
