"""Tracers around an evolved Schwarzschild puncture compared with exact Schwarzschild
geodesics in gauge-invariant variables: proper time tau, areal radius R and the
azimuth in the orbital plane. Reads <base>.traj.bin, <base>.trajmet.bin and, if
present, the restart dumps rst/<base>.NNNNN.rst (Z4c state on the mesh).

    python3 tracers_exact.py <rundir> [--base punc] [--out NAME] [--window 100] [--no-rst]

Written for runs/puncture/single_v3 (tracers_single.athinput): tags 0-2 circular
equatorial orbits, tag 3 an inclined circular orbit, tag 4 a plunge from rest in R,
tag 5 a radial infall from rest; M = 1.

Definitions (all from the recorded state x^i, u_i and the metric alpha, beta^i,
gamma_ij reconstructed at the particle):
  W = (1 + gamma^ij u_i u_j)^(1/2),  dtau/dt = alpha / W  (u^t = W / alpha; the shift does
      not enter), tau by the trapezoidal rule (Simpson printed for comparison);
  R = r <(gamma_ij t^i t^j)^(1/2)> over two unit coordinate vectors t orthogonal to x
      (areal radius of a spherically symmetric slice, as in tracers.py);
  L = |x cross u| (conserved total angular momentum); orbital plane normal = L(0).
Exact references: tag 5 the cycloid R = R0 (1 + cos eta)/2,
tau = (R0^3/8M)^(1/2) (eta + sin eta); tag 4 d^2R/dtau^2 = -M/R^2 + L^2/R^3 - 3 M L^2/R^4,
dphi/dtau = L/R^2 with R(0) = r0 psi^2 and E, L from the initial data (E = alpha_K W,
alpha_K = (1 - M/2r)/(1 + M/2r)); tags 0-3 R = const, dphi/dt = (M/R^3)^(1/2) in
Killing time, dphi/dtau = (M/R^3)^(1/2) (1 - 3M/R)^(-1/2).

Restart dumps (skipped with --no-rst or when absent) give metric-only diagnostics:
the Misner-Sharp mass m = (R/2)(1 - gamma^ij d_i R d_j R + R^2 K_T^2) of the evolved
slice (K_T = tangential eigenvalue of K^i_j, 4th-order differences inside each
MeshBlock), the coordinate drift d_t R|_x = -alpha R K_T + beta^i d_i R, the
Killing normalisation c_K = ((alpha^2 - beta_i beta^i)/(1 - 2M/R))^(1/2) of d_t, and an
estimate of the error of reading R at the particle (Catmull-Rom, as in the code,
against 4- and 6-point Lagrange interpolation of the same cell data). From each dump
at t = 50 the tracers are also compared with geodesics of mass m(t) (dump medians,
linear in t between dumps) started from their own state, which separates what the
tracer does in the evolved spacetime from the mass of that spacetime.

Figure. Left, top: R(tau) of tags 5 and 4 with the exact geodesics (blue dashed).
Left, middle: |R/R_exact - 1| (solid); dotted: against the geodesic of the dump mass
started at t = 50; open circles: R-reading error estimate at the nearest dump; short
ticks at the top: changes of refinement level at the particle. Left, bottom:
phi(R) - phi_exact(R) of tag 4. Right, top: R/R0 - 1 of the circular orbits. Right,
middle: effective mass that makes each circular tracer's radial acceleration
geodesic, M_eff = (L^2/R^3 - d^2R/dtau^2)/(1/R^2 + 3L^2/R^4) (20 M Savitzky-Golay),
with the Misner-Sharp mass of the dumps (black: median over 6 < R < 12, bar: range).
Right, bottom: running dphi/dtau / exact - 1 (solid) and dphi/dt / Kepler - 1 (dashed);
shaded: the window of the frequency fits.
"""
import glob
import os
import struct
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.integrate import cumulative_simpson, cumulative_trapezoid, solve_ivp
from scipy.interpolate import CubicSpline
from scipy.signal import savgol_filter

from common import FIGS, inv_sym3, parse_cli, read_horizon, read_traj_tagged, run_path
from nrpic import figstyle as fs

M = 1.0
RCUT = 2.2            # "outside the horizon" part of the falls: R_exact > RCUT
SG_WIN = 20.0         # Savitzky-Golay window for d^2R/dtau^2 and running frequencies [M]
CIRC, PLUNGE, INFALL = (0, 1, 2, 3), 4, 5

runs, opts = parse_cli(sys.argv[1:], options=("base", "out", "window"))
if not runs:
    sys.exit(__doc__)
label, d = runs[0]
base = opts.get("base", "punc")
out = opts.get("out", f"tracers_exact_{label}")
WIN = float(opts.get("window", 100.0))

tr = read_traj_tagged(run_path(d, f"{base}.traj.bin"), 8)
tm = read_traj_tagged(run_path(d, f"{base}.trajmet.bin"), 12)
if not tr or not tm:
    sys.exit(f"need {base}.traj.bin and {base}.trajmet.bin in {d}")
missing = [k for k in CIRC + (PLUNGE, INFALL) if k not in tr or k not in tm]
if missing:
    sys.exit(f"tags {missing} missing: this script expects the six tracers of "
             "tracers_single.athinput")


# ---------------------------------------------------------------------------------------
# per-tracer derived quantities
# ---------------------------------------------------------------------------------------
def level_dx(x):
    """Cell size at the particle for the static mesh of tracers_single.athinput
    (level 5 dx = 1/8 for max|x^i| < 4, then doubling at 8, 16, 32, 64)."""
    m = np.max(np.abs(x), axis=1)
    return np.select([m < 4, m < 8, m < 16, m < 32, m < 64], [0.125, 0.25, 0.5, 1.0, 2.0],
                     4.0)


def tangent_basis(x):
    r = np.sqrt((x ** 2).sum(1))
    n = x / r[:, None]
    ref = np.where(np.abs(n[:, 2:3]) < 0.9, [[0.0, 0.0, 1.0]], [[1.0, 0.0, 0.0]])
    t1 = np.cross(ref, n)
    t1 /= np.sqrt((t1 ** 2).sum(1))[:, None]
    return r, n, t1, np.cross(n, t1)


def areal_radius(x, g6):
    """R = r <(gamma_ij t^i t^j)^1/2> for points x [N,3] and gamma_ij [6,N]."""
    r, _, t1, t2 = tangent_basis(x)
    gxx, gxy, gxz, gyy, gyz, gzz = g6
    G = np.stack([np.stack([gxx, gxy, gxz], -1), np.stack([gxy, gyy, gyz], -1),
                  np.stack([gxz, gyz, gzz], -1)], -2)
    q1 = np.sqrt(np.einsum("ni,nij,nj->n", t1, G, t1))
    q2 = np.sqrt(np.einsum("ni,nij,nj->n", t2, G, t2))
    return r * 0.5 * (q1 + q2), G


def derive(a, m):
    t, ia, im = np.intersect1d(a[:, 0], m[:, 0], return_indices=True)
    a, m = a[ia], m[im]
    x, u = a[:, 2:5], a[:, 5:8]
    alp, beta, g6 = m[:, 2], m[:, 3:6], m[:, 6:12].T
    (uxx, uxy, uxz, uyy, uyz, uzz), _ = inv_sym3(*g6)
    ux, uy, uz = u.T
    W = np.sqrt(1.0 + uxx * ux * ux + uyy * uy * uy + uzz * uz * uz
                + 2 * (uxy * ux * uy + uxz * ux * uz + uyz * uy * uz))
    R, G = areal_radius(x, g6)
    b_low = np.einsum("nij,nj->ni", G, beta)
    Lv = np.cross(x, u)
    dtau = alp / W
    tau = cumulative_trapezoid(dtau, t, initial=0.0)
    tau_s = cumulative_simpson(dtau, x=t, initial=0.0)
    cK = np.sqrt(np.abs(alp ** 2 - (b_low * beta).sum(1)) / np.abs(1 - 2 * M / R))
    return dict(t=t, x=x, u=u, alp=alp, beta=beta, W=W, R=R, r=np.sqrt((x ** 2).sum(1)),
                Lv=Lv, L=np.sqrt((Lv ** 2).sum(1)), tau=tau, tau_s=tau_s, cK=cK,
                dx=level_dx(x))


Q = {k: derive(tr[k], tm[k]) for k in CIRC + (PLUNGE, INFALL)}


def plane_angle(q):
    """Unwrapped azimuth in the plane orthogonal to L(0), measured from x(0)."""
    if q["L"][0] < 1e-10:                       # radial orbit: no plane
        return np.zeros(len(q["t"])), np.zeros(len(q["t"]))
    nhat = q["Lv"][0] / q["L"][0]
    e1 = q["x"][0] - nhat * (q["x"][0] @ nhat)
    e1 /= np.sqrt(e1 @ e1)
    e2 = np.cross(nhat, e1)
    phi = np.unwrap(np.arctan2(q["x"] @ e2, q["x"] @ e1))
    tilt = np.degrees(np.arccos(np.clip(q["Lv"] @ nhat / q["L"], -1, 1)))
    return phi, tilt


for q in Q.values():
    q["phi"], q["tilt"] = plane_angle(q)


# ---------------------------------------------------------------------------------------
# exact initial data of each tracer (isotropic time-symmetric slice, Killing lapse)
# ---------------------------------------------------------------------------------------
def exact_constants(x0, u0):
    r0 = np.sqrt(x0 @ x0)
    psi = 1 + M / (2 * r0)
    aK = (1 - M / (2 * r0)) / (1 + M / (2 * r0))
    W0 = np.sqrt(1 + (u0 @ u0) / psi ** 4)
    R0 = r0 * psi ** 2
    # dR/dtau = u^r dR/dr, u^r = u_r / psi^4, dR/dr = psi (psi - M/r)
    v0 = (x0 @ u0) / r0 / psi ** 4 * psi * (psi - M / r0)
    return dict(R0=R0, E=aK * W0, L=np.sqrt(np.cross(x0, u0) @ np.cross(x0, u0)), v0=v0,
                r0=r0)


EX = {k: exact_constants(tr[k][0, 2:5], tr[k][0, 5:8]) for k in Q}


def geodesic(tau_eval, R0, v0, L, Mfun=lambda tau: M, tau0=0.0, R_stop=0.3):
    """Radial geodesic equation in proper time with phi; returns R, phi at tau_eval
    (nan beyond R_stop)."""
    def rhs(tau, y):
        R, v, _ = y
        Mt = Mfun(tau)
        return [v, -Mt / R ** 2 + L ** 2 / R ** 3 - 3 * Mt * L ** 2 / R ** 4, L / R ** 2]

    def stop(tau, y):
        return y[0] - R_stop
    stop.terminal = True
    s = solve_ivp(rhs, [tau0, tau_eval[-1]], [R0, v0, 0.0], method="DOP853", rtol=1e-12,
                  atol=1e-13, dense_output=True, events=stop, max_step=0.5)
    Y = np.full((3, len(tau_eval)), np.nan)
    ok = tau_eval <= s.t[-1]
    Y[:, ok] = s.sol(tau_eval[ok])
    return Y[0], Y[2]


def cycloid(tau, R0):
    A = np.sqrt(R0 ** 3 / (8 * M))
    eta = np.linspace(0, np.pi, 200001)
    return np.interp(tau, A * (eta + np.sin(eta)), R0 * (1 + np.cos(eta)) / 2)


def local_state(q, t0, half=2.0):
    """R and dR/dtau of the tracer at t0 from a cubic fit over |t - t0| <= half."""
    j = int(np.argmin(np.abs(q["t"] - t0)))
    s = np.abs(q["t"] - q["t"][j]) <= half
    c = np.polyfit(q["tau"][s] - q["tau"][j], q["R"][s], 3)
    return j, c[-1], c[-2]


def first_cross(tau, y, level):
    i = np.nonzero(y < level)[0]
    return tau[i[0]] if len(i) else np.nan


# ---------------------------------------------------------------------------------------
# restart dumps: Misner-Sharp mass, drift, Killing normalisation, R-reading check
# ---------------------------------------------------------------------------------------
NZ4C = 22   # chi, gt_ij(6), Khat, At_ij(6), Gam^i(3), Theta, alpha, beta^i(3)


def rst_open(path):
    """Header and memory map of an AthenaK restart file holding only Z4c data."""
    with open(path, "rb") as f:
        head = f.read(65536)
    i = head.find(b"<par_end>")
    if i < 0:
        return None
    off = head.find(b"\n", i) + 1
    nmb, root = struct.unpack_from("ii", head, off)
    off += 8 + 72 + 76                          # RegionSize, mesh RegionIndcs
    bind = struct.unpack_from("19i", head, off)
    off += 76
    time, _ = struct.unpack_from("dd", head, off)
    off += 20                                   # time, dt, ncycle
    lloc = np.frombuffer(head, dtype=np.int32, count=4 * nmb, offset=off).reshape(nmb, 4)
    ng, nx = bind[0], bind[1]
    n = nx + 2 * ng
    size = NZ4C * n ** 3 * 8
    start = os.path.getsize(path) - nmb * size
    with open(path, "rb") as f:
        f.seek(start - 8)
        if struct.unpack("Q", f.read(8))[0] != size:
            return None
    mm = np.memmap(path, dtype=np.float64, mode="r", offset=start, shape=(nmb, NZ4C, n, n, n))
    return dict(time=time, nmb=nmb, root=root, ng=ng, nx=nx, n=n, lloc=lloc, mm=mm,
                path=path)


def rst_geometry(h, mesh_min=-128.0, root_width=64.0):
    out = []
    for b in range(h["nmb"]):
        lx1, lx2, lx3, L = h["lloc"][b]
        w = root_width / 2 ** (L - h["root"])
        out.append((np.array([mesh_min + lx1 * w, mesh_min + lx2 * w, mesh_min + lx3 * w]),
                    w, w / h["nx"]))
    return out


def mesh_extent(path):
    """x1min and root MeshBlock width from the parameter dump of the restart file."""
    txt = open(path, "rb").read(65536).decode("latin-1")
    par, blk = {}, None
    for line in txt.splitlines():
        line = line.split("#")[0].strip()
        if line.startswith("<"):
            blk = line.strip("<>")
        elif "=" in line and blk in ("mesh", "meshblock"):
            k, v = [s.strip() for s in line.split("=", 1)]
            par[(blk, k)] = v
    x1min = float(par[("mesh", "x1min")])
    x1max = float(par[("mesh", "x1max")])
    nroot = int(par[("mesh", "nx1")]) // int(par[("meshblock", "nx1")])
    return x1min, (x1max - x1min) / nroot


def slice_fields(xmin, dx, u, ng):
    """Misner-Sharp mass etc. on the active cells of one MeshBlock."""
    n = u.shape[-1]
    c = (np.arange(n) - ng + 0.5) * dx
    z, y, x = np.meshgrid(xmin[2] + c, xmin[1] + c, xmin[0] + c, indexing="ij")
    chi, gt, Kh, At, Th, alp, beta = u[0], u[1:7], u[7], u[8:14], u[17], u[18], u[19:22]
    g = gt / chi
    K = At / chi + (Kh + 2 * Th) / 3 * g

    def full(s):
        xx, xy, xz, yy, yz, zz = s
        return np.array([[xx, xy, xz], [xy, yy, yz], [xz, yz, zz]])
    G, KK = full(g), full(K)
    r = np.sqrt(x * x + y * y + z * z)
    nn = np.stack([x, y, z]) / r
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
        return (-np.roll(f, -2, ax) + 8 * np.roll(f, -1, ax) - 8 * np.roll(f, 1, ax)
                + np.roll(f, 2, ax)) / (12 * dx)
    dR = np.stack([dd(R, 2), dd(R, 1), dd(R, 0)])
    Gi = np.moveaxis(np.linalg.inv(np.moveaxis(G, (0, 1), (-2, -1))), (-2, -1), (0, 1))
    m = R / 2 * (1 - np.einsum("i...,ij...,j...->...", dR, Gi, dR) + (R * KT) ** 2)
    dtR = -alp * R * KT + (beta * dR).sum(0)
    b2 = (beta * np.einsum("ij...,j...->i...", G, beta)).sum(0)
    cK = np.sqrt(np.abs(alp ** 2 - b2) / np.abs(1 - 2 * M / R))
    s = (slice(ng, n - ng),) * 3
    return {k: v[s].ravel() for k, v in dict(R=R, m=m, dtR=dtR, cK=cK, r=r, x=x, y=y,
                                              z=z).items()}


def lagrange_w(s, npt):
    nodes = np.arange(-(npt // 2 - 1), npt // 2 + 1)
    w = np.ones(npt)
    for a in range(npt):
        for b in range(npt):
            if a != b:
                w[a] *= (s - nodes[b]) / (nodes[a] - nodes[b])
    return w, nodes[0]


def catmull_rom_w(s):
    return np.array([0.5 * (-s + 2 * s * s - s ** 3), 0.5 * (2 - 5 * s * s + 3 * s ** 3),
                     0.5 * (s + 4 * s * s - 3 * s ** 3), 0.5 * (-s * s + s ** 3)]), -1


def R_at(h, geo, X, scheme):
    """Areal radius at X interpolated from the cell-centred ADM gamma_ij of a dump."""
    for b, (xmin, w, dx) in enumerate(geo):
        if np.all(X >= xmin) and np.all(X < xmin + w):
            break
    else:
        return np.nan
    xi = (X - xmin) / dx - 0.5
    i0 = np.floor(xi).astype(int)
    W = [scheme(xi[k] - i0[k]) for k in range(3)]
    sl = [slice(h["ng"] + i0[k] + W[k][1], h["ng"] + i0[k] + W[k][1] + len(W[k][0]))
          for k in range(3)]
    u = np.asarray(h["mm"][b][:, sl[2], sl[1], sl[0]])
    g = np.einsum("vkji,k,j,i->v", u[1:7] / u[0], W[2][0], W[1][0], W[0][0])
    return areal_radius(X[None, :], g[:, None])[0][0]


dumps = []
rfiles = [] if "no-rst" in opts else sorted(glob.glob(run_path(d, "rst", f"{base}.*.rst")))
for p in rfiles:
    h = rst_open(p)
    if h is None:
        print(f"{os.path.basename(p)}: not a Z4c-only restart file, skipped")
        continue
    x1min, wroot = mesh_extent(p)
    geo = rst_geometry(h, x1min, wroot)
    acc = {}
    for b, (xmin, w, dx) in enumerate(geo):
        # MeshBlocks whose nearest point lies within r = 17 (covers 2.5 < R < 16)
        dmin = np.sqrt((np.maximum(0, np.maximum(xmin, -(xmin + w))) ** 2).sum())
        if dmin > 17.0:
            continue
        f = slice_fields(xmin, dx, np.asarray(h["mm"][b]), h["ng"])
        for k, v in f.items():
            acc.setdefault(k, []).append(v)
    h.update({k: np.concatenate(v) for k, v in acc.items()})
    h["geo"] = geo
    dumps.append(h)


def shell(h, key, R, half=0.1):
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


TD = np.array([h["time"] for h in dumps])
MD = np.array([wide(h, "m", 2.5, 16.0)[0] for h in dumps]) if dumps else np.zeros(0)
mass_hist = (lambda t: float(np.interp(t, TD, MD))) if dumps else None


# ---------------------------------------------------------------------------------------
# numbers
# ---------------------------------------------------------------------------------------
def pr(s=""):
    print(s)


pr(f"run {d}: t_end = {max(q['t'][-1] for q in Q.values()):.3f} M, "
   f"records every {np.diff(Q[0]['t']).min():.4f} M")
pr("proper time: max |tau_trapezoid - tau_Simpson| = "
   + ", ".join(f"tag {k} {np.abs(q['tau'] - q['tau_s']).max():.1e}" for k, q in Q.items()))
for k, q in Q.items():
    pr(f"tag {k}: R(0) = {q['R'][0]:.7f} (exact {EX[k]['R0']:.7f}, rel {q['R'][0] / EX[k]['R0'] - 1:+.1e}), "
       f"E = {EX[k]['E']:.9f}, L = {EX[k]['L']:.9f}, dR/dtau(0) = {EX[k]['v0']:+.1e}, "
       f"max|L/L0-1| = {np.abs(q['L'] / q['L'][0] - 1).max() if q['L'][0] > 0 else np.abs(q['L']).max():.1e}"
       f", t_end = {q['t'][-1]:.3f}, tau_end = {q['tau'][-1]:.4f}")

# reading-error estimate at the particle on the dumps
read_est = {}
if dumps:
    pr("\nR reading at the particle on the dumps (Catmull-Rom = trajmet check; "
       "estimate = max |Lagrange4,6 - Catmull-Rom| / R):")
    for k, q in Q.items():
        rows = []
        for h in dumps:
            j = np.nonzero(np.abs(q["t"] - h["time"]) < 1e-9)[0]
            if not len(j):
                continue
            X = q["x"][j[0]]
            Rc = R_at(h, h["geo"], X, catmull_rom_w)
            est = max(abs(R_at(h, h["geo"], X, lambda s: lagrange_w(s, n)) / Rc - 1)
                      for n in (4, 6))
            rows.append((h["time"], Rc / q["R"][j[0]] - 1, est))
        read_est[k] = rows
        pr(f"  tag {k}: " + "; ".join(f"t={a:.0f} chk {b:+.0e} est {c:.1e}" for a, b, c in rows))
    # along the last 30 M of the falls, on the nearest dump
    for k in (INFALL, PLUNGE):
        q = Q[k]
        js = np.nonzero(q["t"] >= q["t"][-1] - 30)[0][::4]
        est = []
        for j in js:
            h = dumps[int(np.argmin(np.abs(TD - q["t"][j])))]
            X = q["x"][j]
            Rc = R_at(h, h["geo"], X, catmull_rom_w)
            est.append(max(abs(R_at(h, h["geo"], X, lambda s: lagrange_w(s, n)) / Rc - 1)
                           for n in (4, 6)))
        Q[k]["read_tau"], Q[k]["read_est"] = q["tau"][js], np.array(est)

# R jumps where the particle changes refinement level (a reading error appears as a jump,
# an error of the worldline does not): third difference of R around each change
pr("\nR at changes of refinement level: max |d^3 R|/R within 2 records of a change "
   "(median over the whole track in brackets):")
for k, q in Q.items():
    d3 = np.abs(np.diff(q["R"], 3)) / q["R"][3:]
    ch = np.nonzero(np.diff(q["dx"]))[0]
    if not len(ch):
        pr(f"  tag {k}: no level change (dx = {q['dx'][0]:g}) [{np.median(d3):.0e}]")
        continue
    jumps = [d3[max(j - 2, 0):min(j + 2, len(d3))].max() for j in ch]
    pr(f"  tag {k}: {len(ch)} changes, max {max(jumps):.1e} [{np.median(d3):.0e}]; "
       + ", ".join(f"t={q['t'][j + 1]:.1f} dx {q['dx'][j]:g}->{q['dx'][j + 1]:g}" for j in ch[:6])
       + (" ..." if len(ch) > 6 else ""))

# --- tag 5: radial infall
q, ex = Q[INFALL], EX[INFALL]
q["Rex"] = cycloid(q["tau"], ex["R0"])
q["res"] = q["R"] / q["Rex"] - 1
out_ = q["Rex"] > RCUT
i5 = int(np.argmax(np.abs(q["res"][out_])))
iall = int(np.argmax(np.abs(q["res"])))
pr(f"\ntag 5 radial infall, R0 = {ex['R0']:.6f}, E = {ex['E']:.9f} (exact cycloid):")
pr(f"  max|R/R_ex - 1| for R_ex > {RCUT}: {np.abs(q['res'][out_]).max():.2e} "
   f"(at tau = {q['tau'][out_][i5]:.2f}, R = {q['Rex'][out_][i5]:.3f}, sign {np.sign(q['res'][out_][i5]):+.0f})")
pr(f"  down to removal: {np.abs(q['res']).max():.2e} (at tau = {q['tau'][iall]:.3f}, "
   f"R = {q['R'][iall]:.3f}, r = {q['r'][iall]:.3f}); removal at t = {q['t'][-1]:.3f}, "
   f"tau = {q['tau'][-1]:.4f}, R = {q['R'][-1]:.4f} (exact {q['Rex'][-1]:.4f}), alpha = {q['alp'][-1]:.4f}")
pr(f"  R_num increases between records {int((np.diff(q['R']) > 0).sum())} times "
   f"(last at R = {q['R'][1:][np.diff(q['R']) > 0].min() if (np.diff(q['R']) > 0).any() else np.nan:.3f})")
for tt in (10, 20, 30, 35):
    j = int(np.argmin(np.abs(q["tau"] - tt)))
    pr(f"  tau = {tt}: t = {q['t'][j]:.1f}, R = {q['Rex'][j]:.3f}, R/R_ex - 1 = {q['res'][j]:+.2e}")

# --- tag 4: plunge
q, ex = Q[PLUNGE], EX[PLUNGE]
taug = np.concatenate([q["tau"], q["tau"][-1] + np.linspace(1e-3, 3.0, 300)])
Rg, phg = geodesic(taug, ex["R0"], ex["v0"], ex["L"])
q["Rex"], q["phex"] = Rg[:len(q["tau"])], phg[:len(q["tau"])]
q["res"] = q["R"] / q["Rex"] - 1
ok = np.isfinite(Rg)
# phi(R): exact phi as a function of R (monotonic after the apocentre)
Rmono, phmono = Rg[ok][1:][::-1], phg[ok][1:][::-1]
q["dphiR"] = q["phi"] - np.interp(q["R"], Rmono, phmono)
q["dphitau"] = q["phi"] - q["phex"]
out_ = q["Rex"] > RCUT
sel_phi = out_ & (q["R"] < ex["R0"] - 0.5)
i4 = int(np.argmax(np.abs(q["res"][out_])))
pr(f"\ntag 4 plunge, R0 = {ex['R0']:.6f}, E = {ex['E']:.9f}, L = {ex['L']:.9f}, "
   f"u_r(0) = {(tr[4][0, 2:5] @ tr[4][0, 5:8]):+.1e} (starts at the apocentre, moves in):")
pr(f"  max|R/R_ex - 1| for R_ex > {RCUT}: {np.abs(q['res'][out_]).max():.2e} "
   f"(at tau = {q['tau'][out_][i4]:.2f}, sign {np.sign(q['res'][out_][i4]):+.0f}); "
   f"down to removal: {np.abs(q['res']).max():.2e}")
pr(f"  removal at t = {q['t'][-1]:.3f}, tau = {q['tau'][-1]:.3f}, R = {q['R'][-1]:.4f} "
   f"(exact at that tau {q['Rex'][-1]:.4f}); tau at R_ex = {RCUT}: "
   f"{first_cross(q['tau'], q['Rex'], RCUT):.3f}, at R_num = {RCUT}: {first_cross(q['tau'], q['R'], RCUT):.3f}")
pr(f"  phi(R) - phi_ex(R) for R < R0 - 0.5 and R_ex > {RCUT}: max {np.abs(q['dphiR'][sel_phi]).max():.2e} rad, "
   f"at R_num = {RCUT}: {np.interp(-RCUT, -q['R'], q['dphiR']):+.3e}; down to removal: "
   f"max {np.abs(q['dphiR'][q['R'] < ex['R0'] - 0.5]).max():.2e}; "
   f"phi(tau) - phi_ex(tau) at R_ex = {RCUT}: {np.interp(-RCUT, -q['Rex'], q['dphitau']):+.3e} rad")
for tt in (20, 40, 60, 80, 90):
    j = int(np.argmin(np.abs(q["tau"] - tt)))
    pr(f"  tau = {tt}: t = {q['t'][j]:.1f}, R_ex = {q['Rex'][j]:.3f}, R/R_ex - 1 = {q['res'][j]:+.2e}, "
       f"dx = {q['dx'][j]:.3f}")

# --- separation with the dump mass: geodesics of mass m(t) from the tracer state at t = 50
sep = {}
if dumps and np.any(TD >= 50):
    t0 = 50.0
    pr(f"\nMisner-Sharp mass of the dumps, median (range) over 2.5 < R < 16 and 6 < R < 12:")
    for h in dumps:
        a, b = wide(h, "m", 2.5, 16), wide(h, "m", 6, 12)
        c, e = wide(h, "dtR", 6, 12), wide(h, "cK", 6, 12)
        pr(f"  t = {h['time']:5.1f}: m - 1 = {a[0] - 1:+.2e} ({a[1] - 1:+.1e} .. {a[2] - 1:+.1e}); "
           f"{b[0] - 1:+.2e} ({b[1] - 1:+.1e} .. {b[2] - 1:+.1e}); d_t R|_x = {c[0]:+.2e}; "
           f"c_K - 1 = {e[0] - 1:+.2e} ({e[1] - 1:+.1e} .. {e[2] - 1:+.1e})")
    ah = read_horizon(run_path(d, f"{base}.horizon_summary_0.txt"))
    pr("Misner-Sharp mass at the horizon, 1.9 < R < 2.1 (r > 0.75), against the "
       "apparent-horizon mass of the horizon finder:")
    for h in dumps:
        s = (np.abs(h["R"] - 2.0) < 0.1) & (h["r"] > 0.75)
        mh = np.median(h["m"][s]) - 1 if s.any() else np.nan
        mah = (ah[np.argmin(np.abs(ah[:, 0] - h["time"])), 1] - 1) if len(ah) else np.nan
        pr(f"  t = {h['time']:5.1f}: m - 1 = {mh:+.2e}; M_AH - 1 = {mah:+.2e}")
    pr(f"geodesics from the tracer state at t = {t0:g} (R, dR/dtau from a cubic fit over "
       f"+-2 M, L = |x cross u|), M = 1 against M = m(t) of the dumps:")
    for k in CIRC + (PLUNGE,):
        q = Q[k]
        if q["t"][-1] <= t0:
            continue
        j0, R0, v0 = local_state(q, t0)
        tt = CubicSpline(q["tau"], q["t"])
        tau = q["tau"][j0:]
        res = {}
        for name, Mf in (("M=1", lambda s: M),
                         ("m(t)", lambda s: mass_hist(float(tt(min(s, q["tau"][-1])))))):
            Re, phe = geodesic(tau, R0, v0, q["L"][j0], Mf, tau0=tau[0])
            rr = q["R"][j0:] / Re - 1
            o = Re > RCUT
            res[name] = (np.nanmax(np.abs(rr[o])), np.nanmax(np.abs(rr)), rr)
            if k == PLUNGE:     # orbit shape phi(R) from t0 on
                okk = np.isfinite(Re)
                dph = (q["phi"][j0:] - q["phi"][j0]) - np.interp(
                    q["R"][j0:], Re[okk][::-1], phe[okk][::-1])
                sel = (q["R"][j0:] > RCUT)
                pr(f"  tag 4 phi(R) - phi_geo(R) from t = {t0:g}, {name}: max over R > {RCUT} "
                   f"{np.abs(dph[sel]).max():.2e} rad")
        sep[k] = dict(tau=tau, j0=j0, **{n: v[2] for n, v in res.items()},
                      M1=res["M=1"][0], Md=res["m(t)"][0])
        pr(f"  tag {k}: max|R/R_geo - 1| (R_geo > {RCUT}) M=1 {res['M=1'][0]:.2e}, "
           f"m(t) {res['m(t)'][0]:.2e}; down to removal/end M=1 {res['M=1'][1]:.2e}, "
           f"m(t) {res['m(t)'][1]:.2e}")

# --- circular orbits
pr(f"\ncircular orbits, window t = [{Q[0]['t'][-1] - WIN:g}, {Q[0]['t'][-1]:g}]:")
circ_rows = {}
for k in CIRC:
    q, ex = Q[k], EX[k]
    R0 = ex["R0"]
    OmK = np.sqrt(M / R0 ** 3)
    Omtau = OmK / np.sqrt(1 - 3 * M / R0)
    w = q["t"] >= q["t"][-1] - WIN
    Om_t = np.polyfit(q["t"][w], q["phi"][w], 1)[0]
    Om_tau = np.polyfit(q["tau"][w], q["phi"][w], 1)[0]
    dadt = np.polyfit(q["t"][w], q["alp"][w], 1)[0]
    dRdt = np.polyfit(q["t"][w], q["R"][w], 1)[0]
    rel = q["R"] / R0 - 1
    # effective mass from the radial acceleration
    tu = np.arange(0.0, q["tau"][-1], 0.1)
    Ru = CubicSpline(q["tau"], q["R"])(tu)
    Lu = CubicSpline(q["tau"], q["L"])(tu)
    nwin = int(SG_WIN / 0.1) | 1
    acc = savgol_filter(Ru, nwin, 3, deriv=2, delta=0.1)
    Meff = (Lu ** 2 / Ru ** 3 - acc) / (1 / Ru ** 2 + 3 * Lu ** 2 / Ru ** 4)
    edge = (tu > SG_WIN / 2) & (tu < tu[-1] - SG_WIN / 2)
    q["Meff_t"] = CubicSpline(q["tau"], q["t"])(tu)[edge]
    q["Meff"] = Meff[edge]
    phu = CubicSpline(q["tau"], q["phi"])(tu)
    q["om_tau_run"] = savgol_filter(phu, nwin, 3, deriv=1, delta=0.1)[edge] / Omtau - 1
    ttu = np.arange(0.0, q["t"][-1], 0.125)
    phiu_t = np.interp(ttu, q["t"], q["phi"])
    edge_t = (ttu > SG_WIN / 2) & (ttu < ttu[-1] - SG_WIN / 2)
    q["om_t_run"] = savgol_filter(phiu_t, int(SG_WIN / 0.125) | 1, 3, deriv=1,
                                  delta=0.125)[edge_t] / OmK - 1
    q["om_t_t"] = ttu[edge_t]
    # dphi/dtau = L/R^2 of a geodesic with the exact L and the measured R, fitted the same way
    phi_R = cumulative_trapezoid(ex["L"] / q["R"] ** 2, q["tau"], initial=0.0)
    expl = np.polyfit(q["tau"][w], phi_R[w], 1)[0] / Omtau - 1
    row = dict(R0=R0, Rmin=rel.min(), Rend=rel[-1], Rwin=rel[w].mean(),
               Om_t=Om_t / OmK - 1, Om_tau=Om_tau / Omtau - 1, expl=expl, dadt=dadt,
               dRdt=dRdt, cK=q["cK"][w].mean() - 1, tilt=q["tilt"].max(),
               Lerr=np.abs(q["L"] / q["L"][0] - 1).max())
    if dumps:
        mt = []
        for h in dumps:
            j = np.nonzero(np.abs(q["t"] - h["time"]) < 1e-9)[0]
            if h["time"] >= 50 and len(j) and q["Meff_t"][0] <= h["time"] <= q["Meff_t"][-1]:
                X = q["x"][j[0]]
                mt.append((h["time"], float(np.interp(h["time"], q["Meff_t"], q["Meff"])),
                           near(h, "m", X), near(h, "dtR", X), near(h, "cK", X)))
        row["dumpcmp"] = mt
        row["MeffVsDump"] = max(abs(a - b) for _, a, b, _, _ in mt)
        h = dumps[-1]
        X = q["x"][np.argmin(np.abs(q["t"] - h["time"]))]
        row["dtR_dump"] = near(h, "dtR", X)
        row["cK_dump"] = near(h, "cK", X) - 1
        row["read"] = max(c for _, _, c in read_est.get(k, [(0, 0, 0)]))
    circ_rows[k] = row
    pr(f"  tag {k} (R0 = {R0:.5f}): R/R0-1 min {row['Rmin']:+.2e}, end {row['Rend']:+.2e}, "
       f"window mean {row['Rwin']:+.2e}; |L/L0-1| max {row['Lerr']:.1e}, plane tilt max "
       f"{row['tilt']:.1e} deg")
    pr(f"      Om_t/Kepler - 1 = {row['Om_t']:+.3e}; dalpha/dt = {dadt:+.2e}, dR/dt = {dRdt:+.2e}, "
       f"<c_K> - 1 = {row['cK']:+.2e}")
    pr(f"      Om_tau/exact - 1 = {row['Om_tau']:+.3e}; geodesic L/R^2 with measured R: "
       f"{row['expl']:+.3e} (difference {row['Om_tau'] - row['expl']:+.1e})")
    if dumps:
        pr(f"      M_eff - m_dump at the particle (t >= 50) max {row['MeffVsDump']:.1e}; at t = "
           f"{dumps[-1]['time']:g}: d_t R|_x = {row['dtR_dump']:+.2e}, c_K - 1 = "
           f"{row['cK_dump']:+.2e}; reading est. max {row['read']:.1e}")
        for a, b, c, e, f in row["dumpcmp"]:
            pr(f"        t = {a:5.1f}: M_eff - 1 = {b - 1:+.2e}, m_dump - 1 = {c - 1:+.2e}, "
               f"d_t R|_x = {e:+.2e}, c_K - 1 = {f - 1:+.2e}")

# ---------------------------------------------------------------------------------------
# figure
# ---------------------------------------------------------------------------------------
fs.use_style()
FIG_H = 7.3
fig = plt.figure(figsize=(fs.FULL_WIDTH, FIG_H))
xl, xr, wcol, b0, top = 0.74, 4.80, 3.0, 0.45, 0.08
hphi, gphi, hres = 1.5, 0.55, 2.6
hRt = FIG_H - top - b0 - hphi - gphi - hres - 0.06
aPhi = fs.inch_axes(fig, xl, b0, wcol, hphi)
aRes = fs.inch_axes(fig, xl, b0 + hphi + gphi, wcol, hres)
aRt = fs.inch_axes(fig, xl, b0 + hphi + gphi + hres + 0.06, wcol, hRt)
hr = (FIG_H - b0 - top - 2 * 0.06) / 3
aOm = fs.inch_axes(fig, xr, b0, wcol, hr)
aM = fs.inch_axes(fig, xr, b0 + hr + 0.06, wcol, hr)
aRc = fs.inch_axes(fig, xr, b0 + 2 * (hr + 0.06), wcol, hr)
COL = {0: fs.PAL["red"], 1: fs.PAL["yellow"], 2: fs.PAL["green"], 3: fs.PAL["orange"],
       4: "#7B3FA0", 5: "#8C564B"}
NAME = {4: "tag 4, plunge", 5: "tag 5, radial infall"}
BLUE = fs.PAL["blue"]
SMALL = dict(fontsize="small", handlelength=1.6, handletextpad=0.5, borderaxespad=0.3)

# left top: R(tau)
for k in (INFALL, PLUNGE):
    q = Q[k]
    aRt.plot(q["tau"], q["R"], color=COL[k], label=NAME[k])
    aRt.plot(q["tau"][-1], q["R"][-1], marker="o", ms=3.5, color=COL[k], zorder=6)
for k in (INFALL, PLUNGE):
    q = Q[k]
    aRt.plot(q["tau"], q["Rex"], color=BLUE, ls="--", lw=1.2,
             label="exact geodesic, $M=1$" if k == INFALL else None)
aRt.axhline(2 * M, **{**fs.MASK_LINE, "lw": 1.0})
aRt.text(62, 2 * M + 0.25, "$R=2M$", color="grey", fontsize="small", va="bottom")
aRt.set_ylabel(r"$R\,[M]$")
aRt.set_ylim(0, 14.5)
aRt.set_yticks([2, 6, 10, 14])
aRt.legend(loc="lower left", **SMALL)
aRt.xaxis.set_major_formatter(matplotlib.ticker.NullFormatter())

# left middle: residuals
FLOOR = 1e-8
for k in (INFALL, PLUNGE):
    q = Q[k]
    aRes.plot(q["tau"], np.maximum(np.abs(q["res"]), FLOOR), color=COL[k], lw=1.2)
    if k in sep:
        s = sep[k]
        aRes.plot(s["tau"], np.maximum(np.abs(s["m(t)"]), FLOOR), color=COL[k], lw=1.2,
                  ls=":")
    if "read_est" in q:
        sel = np.interp(q["read_tau"], q["tau"], q["R"]) < 4.0
        aRes.plot(q["read_tau"][sel], np.maximum(q["read_est"][sel], FLOOR), ls="none",
                  marker="o", ms=3.0, mfc="white", mec=COL[k], mew=0.8)
    for j in np.nonzero(np.diff(q["dx"]))[0]:
        aRes.plot([q["tau"][j + 1]] * 2, [1.5e-8, 6e-8], color=COL[k], lw=1.0)
    aRes.axvline(first_cross(q["tau"], q["Rex"], RCUT), **{**fs.MASK_LINE, "lw": 1.0})
aRes.set_yscale("log")
aRes.set_ylim(FLOOR, 1.0)
aRes.set_xlim(aRt.get_xlim())
aRes.set_ylabel(r"$|R/R_{\rm exact}-1|$")
aRes.set_xlabel(r"proper time $\tau\,[M]$", labelpad=-2)
fs.no_minor_labels(aRes)
hd = [matplotlib.lines.Line2D([], [], color="k", lw=1.2, label="vs. $M=1$"),
      matplotlib.lines.Line2D([], [], color="k", lw=1.2, ls=":",
                              label="vs. dump $m(t)$"),
      matplotlib.lines.Line2D([], [], color="k", ls="none", marker="o", ms=3.0, mfc="white",
                              mew=0.8, label="reading error")]
if dumps:
    aRes.legend(handles=hd, loc="upper left", **SMALL)

# left bottom: phi(R) of the plunge
q = Q[PLUNGE]
m = q["R"] < EX[PLUNGE]["R0"] - 0.5
aPhi.plot(q["R"][m], 100 * q["dphiR"][m], color=COL[PLUNGE])
aPhi.axhline(0.0, color=BLUE, lw=1.2, zorder=1)
aPhi.axvline(RCUT, **{**fs.MASK_LINE, "lw": 1.0})
aPhi.set_xlim(EX[PLUNGE]["R0"], 1.0)
aPhi.set_xlabel(r"$R\,[M]$ of tag 4", labelpad=-2)
aPhi.set_ylabel(r"$\Delta\phi(R)\ [10^{-2}]$")

# right: circular orbits
for k in CIRC:
    q = Q[k]
    aRc.plot(q["t"], 100 * (q["R"] / EX[k]["R0"] - 1), color=COL[k], lw=1.2,
             label=rf"tag {k}, $R_0={EX[k]['R0']:.3f}$" + (", incl." if k == 3 else ""))
    aM.plot(q["Meff_t"], 1e3 * (q["Meff"] - 1), color=COL[k], lw=1.2)
    aOm.plot(q["Meff_t"], 100 * q["om_tau_run"], color=COL[k], lw=1.2)
    aOm.plot(q["om_t_t"], 100 * q["om_t_run"], color=COL[k], lw=1.0, ls="--")
for ax in (aRc, aM, aOm):
    ax.axhline(0.0, color=BLUE, lw=1.2, zorder=1)
if dumps:
    mm = np.array([wide(h, "m", 6, 12) for h in dumps])
    aM.errorbar(TD, 1e3 * (mm[:, 0] - 1), yerr=1e3 * np.abs(mm[:, 1:].T - mm[:, 0]),
                fmt="s", ms=3.5, color="k", capsize=2, lw=1.0, zorder=6, clip_on=False,
                label=r"Misner-Sharp $m$ of the dumps")
    aM.legend(loc="lower right", **SMALL)
tend = Q[0]["t"][-1]
fs.average_window(aOm, tend - WIN, tend, color="grey")
aRc.set_ylim(-2.75, 0.25)
aRc.set_ylabel(r"$R/R_0-1\ [10^{-2}]$")
aM.set_ylabel(r"$M_{\rm eff}-1\ [10^{-3}]$")
aOm.set_ylabel(r"$\Omega/\Omega_{\rm exact}-1\ [10^{-2}]$")
aRc.legend(loc="lower left", **{**SMALL, "handlelength": 1.2})
hd = [matplotlib.lines.Line2D([], [], color="k", lw=1.2, label=r"$d\phi/d\tau$"),
      matplotlib.lines.Line2D([], [], color="k", lw=1.0, ls="--", label=r"$d\phi/dt$")]
aOm.set_ylim(-2.0, 6.2)
aOm.legend(handles=hd, loc="upper left", bbox_to_anchor=(0.12, 1.0), ncol=2, **SMALL)
for ax in (aRc, aM, aOm):
    ax.set_xlim(0, tend)
    ax.yaxis.set_label_coords(-0.13, 0.5)
for ax in (aRc, aM):
    ax.xaxis.set_major_formatter(matplotlib.ticker.NullFormatter())
aOm.set_xlabel(r"coordinate time $t\,[M]$", labelpad=-2)
for ax in (aRt, aRes, aPhi):
    ax.yaxis.set_label_coords(-0.15, 0.5)
print("\n".join(fs.save(fig, out if os.path.isabs(out) else os.path.join(FIGS, out))))
