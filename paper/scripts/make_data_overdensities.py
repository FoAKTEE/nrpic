"""Reduce the cluster with two collapsing overdensities to the arrays of
fig_overdensities.py.

This is the only script of the overdensity figure that reads the simulation outputs and
the analysis modules of the repository; the figure script reads
paper/data/overdensities.npz alone. Monoenergetic envelope (0.76 of the total mass M,
6000 macroparticles, species 0) with two Gaussian overdensities (0.12 M each, 2000
macroparticles each, species 1 at x = -3 M and species 2 at x = +3 M) on a circular
orbit in the x-y plane; they collapse to black holes A and B, which orbit inside the
envelope and accrete.

Two meshes, each one physical evolution stored in several directories because it was
restarted with changed settings:
- finest cells M/64: runs/jeans/n1e4_v7 (0 to 10.0 M), diag_v14b (10.0 to 13.0 M),
  n1e4_v17 (13.0 M onward, a restart chain);
- finest cells M/128: runs/jeans/n1e4_v11 (0 to 6.31 M), n1e4_v18 (6.31 M onward).
Each directory is cut where the next one starts (first record of the next directory in
the same file, at the latest its restart time), so no time appears twice; within a
directory records rewritten by a later job segment are dropped (as make_tables.py does).
Runs still writing are read as far as they are complete: an unfinished last line and a
snapshot file shorter than its header says are skipped, so the script can be rerun at any
time. A restart from an earlier dump rewrites the tracker files and leaves the snapshots
of the superseded job segment on disk until they are overwritten; snapshots later than
the last current history record of their directory are therefore skipped. The tracker
files of n1e4_v11 begin at 12.30 M (rewritten by a restart), so the M/128 trackers
begin at 6.31 M.

Kept, for each mesh:
- particle history (every step): particle number, removed particles, smallest lapse,
  MeshBlock count;
- tracker of each black hole (every step): time, x, y, z;
- apparent-horizon searches of A, B and the common horizon: time, mass, spin vector and
  magnitude, area, mean and smallest coordinate radius (nan: no horizon found; a row
  identical in every column to the previous found row is the finder re-writing its last
  result after a failed search, flagged as stale and set to nan);
- from every complete snapshot (every 0.5 M): number and rest mass of the macroparticles
  of each species;
- for the M/64 mesh, from the horizon shape files where they exist: the offset of the
  centre of each found horizon from the point about which the finder expands it (the
  tracker), as a check that the tracker stays inside its black hole.
For the M/64 mesh also four particle snapshots (x, y and species of every particle) at
t = 0, 12 M, 50 M and the last complete snapshot; while the run has not passed 60 M the
third panel takes the snapshot half-way between 12 M and the last one. With each
snapshot: the tracker positions and the mean coordinate radius of the horizons found
within 0.25 M of it.

    python3 paper/scripts/make_data_overdensities.py
"""
import os
import re
import sys
from math import factorial
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.dont_write_bytecode = True        # leave the analysis folders untouched
sys.path.insert(0, str(REPO / "analysis" / "diag"))
from common import H, read_snapshot, snapshot_files, snapshot_times  # noqa: E402

RUNS = REPO / "runs" / "jeans"
BASE = "jeans"
# (directory, time from which it is used: its restart time)
MESHES = {
    "64": [("n1e4_v7", 0.0), ("diag_v14b", 10.0), ("n1e4_v17", 13.0)],
    "128": [("n1e4_v11", 0.0), ("n1e4_v18", 6.31)],
}
DX = {"64": 1.0 / 64.0, "128": 1.0 / 128.0}
TOL = 0.01                            # slack on the restart times, in M
T_END = 100.0                         # end time of both runs
LMAX = 8                              # degree of the horizon shape expansion
T_WIN = 0.25                          # largest distance in time of a horizon to a snapshot
T_LIST = np.arange(10.0, T_END + 1e-9, 10.0)   # times of the tabulated numbers
# values of the original paper (from its text)
ORIG = dict(
    t_first=np.array([8.475, 8.525]),               # first apparent horizons
    t_M=np.array([10.0, 10.0, 60.0, 60.0]),         # individual horizon masses ...
    M=np.array([0.0880, 0.0877, 0.1742, 0.1761]),   # ... of A, B at 10 M and at 60 M
    t_common=64.16, M_common=0.3833, chi_common=0.5036,
    t_final=100.0, M_final=0.6474, chi_final=0.1713,
    chi_individual=1e-5)
OUT = HERE.parent / "data" / "overdensities.npz"


# ---- readers that tolerate files still being written -------------------------------
def current(t_raw):
    """Mask of the records of an appended time series that no later record supersedes:
    a job segment restarted from an earlier dump rewrites every time from its start on,
    so a record is kept only if all later records have larger times (as make_tables.py)."""
    t_raw = np.asarray(t_raw, dtype=float)
    later = np.r_[np.minimum.accumulate(t_raw[::-1])[::-1][1:], np.inf]
    return t_raw < later


def read_table(path, ncols, tcol, pad_to=None):
    """Numeric rows of a text file with a column count in ``ncols`` (comments and an
    unfinished last line skipped), without superseded records; rows shorter than
    ``pad_to`` are padded with nan."""
    width = pad_to or max(ncols)
    if not os.path.exists(path):
        return np.zeros((0, width))
    with open(path) as f:
        txt = f.read()
    lines = txt.split("\n")
    if not txt.endswith("\n"):
        lines = lines[:-1]            # the run is writing this line
    rows = []
    for line in lines:
        if not line.strip() or line.startswith("#"):
            continue
        x = line.split()
        if len(x) not in ncols:
            continue
        try:
            rows.append([float(v) for v in x] + [np.nan] * (width - len(x)))
        except ValueError:
            continue
    if not rows:
        return np.zeros((0, width))
    a = np.array(rows)
    return a[current(a[:, tcol])]


def read_hst(d):
    return read_table(d / f"{BASE}.nrpic.hst", (23, 27), 0, pad_to=27)


def read_co(d, i):
    """Tracker i: iteration, time, x, y, z, vx, vy, vz."""
    return read_table(d / f"{BASE}.co_{i}.txt", (8,), 1)


def read_ah(d, i):
    """Horizon searches: iter, time, mass, Sx, Sy, Sz, S, area, hrms, hmean, mean radius,
    smallest radius (nan where no horizon was found)."""
    return read_table(d / f"{BASE}.horizon_summary_{i}.txt", (12,), 1)


def complete_snapshots(d):
    """(times, files) of the snapshots whose size matches their particle number."""
    files = []
    for p in snapshot_files(str(d), BASE):
        try:
            with open(p, "rb") as f:
                head = f.read(32)
            n = int(np.frombuffer(head[16:24], dtype="<i8")[0])
            if len(head) == 32 and os.path.getsize(p) == 32 + 64 * n:
                files.append(p)
        except (OSError, IndexError, ValueError):
            continue
    return snapshot_times(files), files


def stitch(parts, starts, tcol):
    """Concatenate the pieces of one evolution: piece k ends before the first record of
    piece k+1 (at the latest at its restart time), piece k+1 begins at its restart time.
    Returns the rows and the index of the piece each row comes from."""
    out, seg = [], []
    for k, a in enumerate(parts):
        t = a[:, tcol]
        keep = np.ones(len(a), dtype=bool)
        if k + 1 < len(parts):
            nxt = parts[k + 1]
            if len(nxt):
                keep &= t < nxt[0, tcol]
            keep &= t <= starts[k + 1] + TOL
        if k > 0:
            keep &= t >= starts[k] - TOL
        out.append(a[keep])
        seg.append(np.full(keep.sum(), k, dtype=np.int8))
    return np.concatenate(out), np.concatenate(seg)


# ---- apparent-horizon shape (as make_data_prolate.py) ------------------------------
def ylm(l, m, theta, phi):
    """Complex spherical harmonic in the Wigner-d form of the horizon finder
    (real and imaginary part)."""
    w = np.zeros_like(theta, dtype=float)
    c, s = np.cos(theta / 2.0), np.sin(theta / 2.0)
    for k in range(max(0, m), min(l + m, l) + 1):
        w += ((-1.0) ** k * c ** (2 * l + m - 2 * k) * s ** (2 * k - m)
              / (factorial(l + m - k) * factorial(l - k) * factorial(k) * factorial(k - m)))
    w *= np.sqrt((2 * l + 1) / (4 * np.pi)) * factorial(l) * np.sqrt(
        factorial(l + m) * factorial(l - m))
    return w * np.cos(m * phi), w * np.sin(m * phi)


def horizon_radius(coef, theta, phi):
    """Coordinate radius r(theta, phi) about the expansion centre from the coefficients
    of the shape file (per l: a_l0, then a_lm^c, a_lm^s for m = 1 .. l)."""
    r, i = np.zeros_like(theta, dtype=float), 0
    for l in range(LMAX + 1):
        re_, _ = ylm(l, 0, theta, phi)
        r += coef[i] * re_
        i += 1
        for m in range(1, l + 1):
            re_, im_ = ylm(l, m, theta, phi)
            r += np.sqrt(2.0) * (coef[i] * re_ + coef[i + 1] * im_)
            i += 2
    return r


def read_shapes(path):
    """{time: coefficient array} from the shape file (complete lines only), without the
    blocks that a later job segment rewrote."""
    if not os.path.exists(path):
        return {}
    ncoef = (LMAX + 1) ** 2
    ts, cs, t = [], [], None
    for line in open(path):
        if line.startswith("#"):
            m = re.search(r"Time\s*=\s*([-+0-9.eE]+)", line)
            t = float(m.group(1)) if m else None
        elif line.strip() and t is not None:
            x = line.split()
            if len(x) == ncoef:
                ts.append(t)
                cs.append(np.array(x, dtype=float))
            t = None
    keep = current(ts) if ts else []
    return {a: c for a, c, k in zip(ts, cs, keep) if k}


def centre_offset(coef):
    """Offset (dx, dy, dz) of the centre of the horizon surface from its expansion
    centre: half the difference of the radii in opposite directions."""
    th = np.array([np.pi / 2, np.pi / 2, np.pi / 2, np.pi / 2, 0.0, np.pi])
    ph = np.array([0.0, np.pi, np.pi / 2, 3 * np.pi / 2, 0.0, 0.0])
    r = horizon_radius(coef, th, ph)
    return np.array([r[0] - r[1], r[2] - r[3], r[4] - r[5]]) / 2.0


# ---- one mesh ------------------------------------------------------------------------
def reduce_mesh(key):
    dirs = [RUNS / name for name, _ in MESHES[key]]
    starts = [t for _, t in MESHES[key]]
    h, h_seg = stitch([read_hst(d) for d in dirs], starts, 0)
    co, co_seg = zip(*[stitch([read_co(d, i) for d in dirs], starts, 1) for i in (0, 1)])
    ah, ah_seg = zip(*[stitch([read_ah(d, i) for d in dirs], starts, 1) for i in (0, 1, 2)])
    # snapshots: the same cut on the snapshot times; a snapshot later than the last
    # history record of its directory was written by a job segment that a restart from
    # an earlier dump superseded (it is overwritten when the run gets there again)
    snaps = [complete_snapshots(d) for d in dirs]
    st, sf = [], []
    for k, (t, f) in enumerate(snaps):
        hk = h[h_seg == k, 0]
        keep = t <= (hk[-1] + TOL if len(hk) else -np.inf)
        if k + 1 < len(snaps):
            if len(snaps[k + 1][0]):
                keep &= t < snaps[k + 1][0][0]
            keep &= t <= starts[k + 1] + TOL
        if k > 0:
            keep &= t >= starts[k] - TOL
        st.extend(t[keep])
        sf.extend(np.array(f)[keep])
    st = np.array(st)
    sn = np.zeros((len(sf), 3))
    sm = np.zeros((len(sf), 3))
    for k, p in enumerate(sf):
        _, q, _, sp = read_snapshot(p)
        for s in range(3):
            sel = sp == s
            sn[k, s] = sel.sum()
            sm[k, s] = q[sel, 6].sum()
    # trackers on common times
    tA, tB = np.round(co[0][:, 1], 9), np.round(co[1][:, 1], 9)
    tc, ia, ib = np.intersect1d(tA, tB, return_indices=True)
    xa, xb = co[0][ia, 2:5], co[1][ib, 2:5]
    d = {"h_t": h[:, H["time"]], "h_np": h[:, H["np"]], "h_nexc": h[:, H["n_excised"]],
         "h_alpha_min": h[:, H["alpha_min"]], "h_nmb": h[:, H["nmb"]],
         "h_sum_m": h[:, H["sum_m"]], "h_seg": h_seg,
         "co_t": tc, "co_A": xa, "co_B": xb, "co_seg": co_seg[0][ia],
         "snap_t": st, "snap_n": sn, "snap_m": sm,
         "restart_t": np.array(starts[1:]), "dx": DX[key],
         "dirs": np.array([p.name for p in dirs])}
    for i, lab in enumerate("ABC"):
        a = ah[i].copy()
        # a search that fails after a success can re-write the previous result: every
        # column equal to the last found row to the last digit; counted as not found
        fi = np.where(np.isfinite(a[:, 2]))[0]
        rep = fi[1:][np.all(a[fi[1:], 2:12] == a[fi[:-1], 2:12], axis=1)]
        a[rep, 2:12] = np.nan
        d[f"ah{lab}_stale"] = np.isin(np.arange(len(a)), rep)
        d.update({f"ah{lab}_t": a[:, 1], f"ah{lab}_M": a[:, 2], f"ah{lab}_S": a[:, 6],
                  f"ah{lab}_Svec": a[:, 3:6], f"ah{lab}_area": a[:, 7],
                  f"ah{lab}_rmean": a[:, 10], f"ah{lab}_rmin": a[:, 11],
                  f"ah{lab}_seg": ah_seg[i]})
    # offset of each found horizon from the tracker (shape files, where written)
    for i, lab in enumerate("AB"):
        shp = {}
        for p in dirs:
            shp.update(read_shapes(p / f"{BASE}.horizon_shape_{i}.txt"))
        ts = np.array(sorted(shp))
        off = np.array([centre_offset(shp[t]) for t in ts]) if len(ts) else np.zeros((0, 3))
        d[f"off{lab}_t"], d[f"off{lab}"] = ts, off
    return d, sf


def nearest_found(d, lab, t, win=T_WIN):
    """Mean radius of the found horizon nearest in time to t (nan if none within win)."""
    tt, M, r = d[f"ah{lab}_t"], d[f"ah{lab}_M"], d[f"ah{lab}_rmean"]
    ok = np.isfinite(M) & (np.abs(tt - t) <= win)
    if not ok.any():
        return np.nan, np.nan
    k = np.where(ok)[0][np.argmin(np.abs(tt[ok] - t))]
    return tt[k], r[k]


def panel_times(st):
    t_last = st[-1]
    mid = 50.0 if t_last >= 60.0 else 0.5 * (12.0 + t_last)
    return (0.0, 12.0, mid, t_last)


def main():
    data = {f"orig_{k}": v for k, v in ORIG.items()}
    data.update(t_end=T_END, t_list=T_LIST)
    files64 = None
    for key in MESHES:
        d, files = reduce_mesh(key)
        data.update({f"m{key}_{k}": v for k, v in d.items()})
        if key == "64":
            files64, d64 = files, d
        print(f"M/{key}: " + ", ".join(MESHES[key][k][0] for k in range(len(MESHES[key])))
              + f"; history t = {d['h_t'][0]:g} .. {d['h_t'][-1]:g} ({len(d['h_t'])}); "
              f"trackers to {d['co_t'][-1]:g}; {len(d['snap_t'])} snapshots to "
              f"{d['snap_t'][-1]:g}; horizons found A {np.isfinite(d['ahA_M']).sum()}, "
              f"B {np.isfinite(d['ahB_M']).sum()}, common {np.isfinite(d['ahC_M']).sum()}")
    # particle panels (M/64)
    st = data["m64_snap_t"]
    for j, tw in enumerate(panel_times(st)):
        k = int(np.argmin(np.abs(st - tw)))
        tk, q, _, sp = read_snapshot(files64[k])
        data[f"p{j}_t"] = tk
        data[f"p{j}_x"] = q[:, 0].astype(np.float32)
        data[f"p{j}_y"] = q[:, 1].astype(np.float32)
        data[f"p{j}_sp"] = sp.astype(np.int8)
        c = int(np.argmin(np.abs(d64["co_t"] - tk)))
        hz = []
        for lab, pos in (("A", d64["co_A"][c]), ("B", d64["co_B"][c]),
                         ("C", 0.5 * (d64["co_A"][c] + d64["co_B"][c]))):
            t_ah, r = nearest_found(d64, lab, tk)
            hz.append([pos[0], pos[1], r, t_ah])
        data[f"p{j}_hz"] = np.array(hz)          # rows A, B, common: x, y, radius, time
    OUT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT, **data)
    print(f"{OUT}  {OUT.stat().st_size / 1e6:.3f} MB")
    summary(data)


# ---- numbers for the text and the table ----------------------------------------------
def separation(D, m):
    dx = D[f"m{m}_co_B"] - D[f"m{m}_co_A"]
    return np.sqrt((dx ** 2).sum(1)), np.unwrap(np.arctan2(dx[:, 1], dx[:, 0]))


def value_at(t, y, t0, win):
    if len(t) == 0:
        return np.nan, np.nan
    k = int(np.argmin(np.abs(t - t0)))
    return (t[k], y[k]) if abs(t[k] - t0) <= win else (np.nan, np.nan)


def found(D, m, lab):
    M = D[f"m{m}_ah{lab}_M"]
    ok = np.isfinite(M)
    return D[f"m{m}_ah{lab}_t"][ok], M[ok], D[f"m{m}_ah{lab}_S"][ok]


def gaps(t_search, M, longer=0.5):
    """Stretches without a found horizon between the first and last found search."""
    ok = np.isfinite(M)
    if ok.sum() < 2:
        return []
    tf = t_search[ok]
    dt = np.diff(tf)
    return [(tf[k], tf[k + 1]) for k in np.where(dt > longer)[0]]


def summary(D):
    print("summary:")
    print("  particle panels at " + ", ".join(f"{D[f'p{j}_t']:g} M" for j in range(4)))
    for m in ("64", "128"):
        print(f"  --- M/{m} ({', '.join(D[f'm{m}_dirs'])}); history to "
              f"{D[f'm{m}_h_t'][-1]:.4f} M, trackers to {D[f'm{m}_co_t'][-1]:.4f} M, "
              f"snapshots to {D[f'm{m}_snap_t'][-1]:g} M")
        tc = D[f"m{m}_co_t"]
        sep, phi = separation(D, m)
        if len(tc):
            print(f"      trackers from t = {tc[0]:.4f} M; separation {sep[0]:.4f} M there")
        for lab in "AB":
            tf, M, S = found(D, m, lab)
            if len(tf):
                print(f"      {lab}: first found t = {tf[0]:.4f} M, mass {M[0]:.5f}, "
                      f"S/M^2 {S[0] / M[0] ** 2:.2e}; {len(tf)} of "
                      f"{len(D[f'm{m}_ah{lab}_t'])} searches found "
                      f"({len(tf)} of {(D[f'm{m}_ah{lab}_t'] >= tf[0]).sum()} from the first); "
                      f"last {M[-1]:.5f} at "
                      f"{tf[-1]:.4f} M (S {S[-1]:.2e}, S/M^2 {S[-1] / M[-1] ** 2:.2e})")
                print(f"         {D[f'm{m}_ah{lab}_stale'].sum()} stale rows (previous result "
                      f"re-written) at " + ", ".join(
                          f"{x:.4f}" for x in D[f"m{m}_ah{lab}_t"][D[f"m{m}_ah{lab}_stale"]]))
                g = gaps(D[f"m{m}_ah{lab}_t"], D[f"m{m}_ah{lab}_M"])
                if g:
                    print(f"         stretches > 0.5 M without a found {lab}: "
                          + ", ".join(f"{a:.3f}-{b:.3f}" for a, b in g))
            else:
                print(f"      {lab}: no horizon found in {len(D[f'm{m}_ah{lab}_t'])} searches")
        tf, M, S = found(D, m, "C")
        if len(tf):
            print(f"      common horizon first found t = {tf[0]:.4f} M, mass {M[0]:.5f}, "
                  f"S/M^2 {S[0] / M[0] ** 2:.4f}; last {M[-1]:.5f}, "
                  f"S/M^2 {S[-1] / M[-1] ** 2:.4f} at {tf[-1]:.4f} M")
        else:
            print(f"      common horizon: none found ({len(D[f'm{m}_ahC_t'])} searches)")
        if len(tc):
            orbits = phi[-1] / (2 * np.pi)
            below = np.where(sep < 1.0)[0]
            print(f"      orbital angle {np.degrees(phi[-1]):.1f} deg "
                  f"({orbits:.3f} orbits, {int(np.floor(abs(orbits)))} completed) by "
                  f"{tc[-1]:.3f} M; separation below 1 M: "
                  + (f"from t = {tc[below[0]]:.4f} M" if len(below) else "not yet")
                  + f"; smallest separation {sep.min():.4f} M at {tc[np.argmin(sep)]:.4f} M")
        n0 = D[f"m{m}_snap_n"][0]
        print("      t      sep   phi/deg   M_A      M_B      M_C     N_env N_A  N_B "
              "  (fractions)")
        for t0 in np.r_[[D["orig_t_first"][0]], D["t_list"]]:
            if t0 > D[f"m{m}_h_t"][-1] + 1e-9:
                break
            _, s = value_at(tc, sep, t0, 0.01)
            _, p = value_at(tc, np.degrees(phi), t0, 0.01)
            ms = []
            for lab in "ABC":
                tf, M, _ = found(D, m, lab)
                ta, mv = value_at(tf, M, t0, T_WIN)
                ms.append(f"{mv:.5f}" if np.isfinite(mv) else "   --  ")
            ts, n = value_at(D[f"m{m}_snap_t"], D[f"m{m}_snap_n"], t0, 0.01)
            ns = (" ".join(f"{int(v):4d}" for v in n) + "  (" +
                  " ".join(f"{v / w:.3f}" for v, w in zip(n, n0)) + ")"
                  if np.ndim(n) else "")
            print(f"      {t0:5.1f} {s:6.3f} {p:7.2f}  " + " ".join(ms) + "  " + ns)
        # mesh and particles
        nmb, ht = D[f"m{m}_h_nmb"], D[f"m{m}_h_t"]
        k = int(np.argmax(nmb))
        print(f"      largest MeshBlock count {nmb[k]:.0f} at t = {ht[k]:.4f} M; now "
              f"{nmb[-1]:.0f}; particles now {D[f'm{m}_h_np'][-1]:.0f}, removed "
              f"{D[f'm{m}_h_nexc'][-1]:.0f}; smallest lapse now {D[f'm{m}_h_alpha_min'][-1]:.4f}")
        ne = D[f"m{m}_h_nexc"]
        k0 = int(np.argmax(ne > 0))
        print(f"      first removal at t = {ht[k0]:.4f} M ({ne[k0]:.0f} particles)")
        # restarts: last record of one directory against the first of the next
        hs, cs = D[f"m{m}_h_seg"], D[f"m{m}_co_seg"]
        for k, tr in enumerate(D[f"m{m}_restart_t"]):
            line = f"      restart {tr:g}:"
            i0, i1 = np.where(hs == k)[0], np.where(hs == k + 1)[0]
            if len(i0) and len(i1):
                a, b = i0[-1], i1[0]
                line += (f" history t {ht[a]:.4f}/{ht[b]:.4f} np {D[f'm{m}_h_np'][a]:.0f}/"
                         f"{D[f'm{m}_h_np'][b]:.0f} lapse {D[f'm{m}_h_alpha_min'][a]:.4f}/"
                         f"{D[f'm{m}_h_alpha_min'][b]:.4f} nmb {nmb[a]:.0f}/{nmb[b]:.0f}")
            j0, j1 = np.where(cs == k)[0], np.where(cs == k + 1)[0]
            if len(j0) and len(j1):
                line += (f"; separation {sep[j0[-1]]:.4f}/{sep[j1[0]]:.4f} at "
                         f"{tc[j0[-1]]:.4f}/{tc[j1[0]]:.4f}")
            for lab in "AB":
                a_s = D[f"m{m}_ah{lab}_seg"]
                ok = np.isfinite(D[f"m{m}_ah{lab}_M"])
                f0, f1 = np.where(ok & (a_s == k))[0], np.where(ok & (a_s == k + 1))[0]
                if len(f0) and len(f1):
                    tt, M = D[f"m{m}_ah{lab}_t"], D[f"m{m}_ah{lab}_M"]
                    line += (f"; M_{lab} {M[f0[-1]]:.5f}/{M[f1[0]]:.5f} at "
                             f"{tt[f0[-1]]:.4f}/{tt[f1[0]]:.4f}")
            print(line)
        # tracker steps and offsets of the horizons from the trackers
        if len(tc) > 1:
            for lab in "AB":
                x = D[f"m{m}_co_{lab}"]
                step = np.sqrt((np.diff(x, axis=0) ** 2).sum(1))
                k = int(np.argmax(step))
                print(f"      tracker {lab}: largest step {step[k]:.4f} M between "
                      f"{tc[k]:.4f} and {tc[k + 1]:.4f} M")
        for lab in "AB":
            ts, off = D[f"m{m}_off{lab}_t"], D[f"m{m}_off{lab}"]
            if len(ts):
                o = np.sqrt((off ** 2).sum(1))
                tf, _, _ = found(D, m, lab)
                r = np.interp(ts, D[f"m{m}_ah{lab}_t"][np.isfinite(D[f"m{m}_ah{lab}_M"])],
                              D[f"m{m}_ah{lab}_rmean"][np.isfinite(D[f"m{m}_ah{lab}_M"])])
                k = int(np.argmax(o / r))
                print(f"      horizon {lab} centre from its tracker: median {np.median(o):.4f} M, "
                      f"largest {o[k]:.4f} M ({o[k] / r[k]:.2f} of the mean radius) at "
                      f"{ts[k]:.4f} M ({len(ts)} shapes)")


if __name__ == "__main__":
    main()
