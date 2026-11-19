"""Analysis of the Newtonian-mode runs of the population package.

    python3 analyze.py --case NAME:RUNDIR/CASE [--case ...] [--gw NAME] [--ng 64]

Reads the particle snapshots (newton.part.NNNNN.bin), the history of the mode
(newton.newton.hst) and meta.json of each case and writes, into $NRPIC_RUN_DIR,
analysis.json and the figures pop_*.png (copies into ../results, ../figs).

Units G = c = 1, comoving x, conformal time t, a = (1 + t/2)^2, momentum slot
p = a dx/dt, comoving density rho_c (mean 3/(8 pi)); the code's potential Phi_c solves
lap Phi_c = 4 pi (rho_c - <rho_c>) and the Newtonian potential is Phi_N = Phi_c/a.

1. Halos: friends-of-friends, linking length b = 0.2 of the mean particle spacing,
   periodic (scipy cKDTree with boxsize); groups of >= 100 particles are halos. Mass,
   centre of mass, comoving half-mass radius, velocity dispersion, G M/(a r_half).
2. GW signal of the box in the weak-field, slow-motion limit (the linearized Einstein
   equation with the Newtonian stress, the method of arXiv:2212.00425 main.tex:219-288
   with the gravitational stress of arXiv:2312.12499 main.tex:149, whose TT part is
   4 d_i Phi_N d_j Phi_N):
       h~'' + k^2 h~ = F(k, t) = a S^TT(k, t),   h~ = a h,
       S_ij = 16 pi rho_c v_i v_j / a + 4 d_i Phi_N d_j Phi_N,   v = p/a,
   (a''/a = 1/(2a) << k^2 dropped, as 2212.00425 line 241). With C = int cos(k t) F dt,
   S = int sin(k t) F dt (Filon rule: F linear between snapshots, the oscillatory
   integral exact), the waves the box would hold if the source stopped at t have
   a^4 rho_GW = (1/(64 pi)) sum_k sum_ij (|C_ij|^2 + |S_ij|^2) (fftn/N coefficients,
   rho_GW = <h'_ij h'_ij>/(32 pi a^2) time-averaged, arXiv:2312.12499 line 206).
   The quasi-static near field h~_qs = F/k^2 has the gradient energy
   a^4 rho_qs = (1/(32 pi)) sum |F|^2/k^2. Omega = a^4 rho/(a rho_c).
   Check: at early times S^TT -> (20/3) [d_i Phi d_j Phi]^TT (matter era, growing mode).
3. Quadrupole formula per halo (the most massive halos of the last snapshot, tracked
   back by particle tag): Q_ij = sum m (r_i r_j - r^2 delta_ij/3) with r = a (x - x_cm),
   cosmic time dT = a dt, Q''' from the snapshots (Savitzky-Golay smoothing over seven
   samples), P = (1/5) Q'''_ij Q'''_ij, E = int P dT.
"""
import argparse
import glob
import json
import os
import shutil
import sys

import numpy as np
from scipy.signal import savgol_filter
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
PKG = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(ROOT, "python"))
from nrpic import figstyle as fs                       # noqa: E402
from nrpic.newton import read_snapshot, read_newton_hst   # noqa: E402

RHO_C = 3.0/(8.0*np.pi)
NMIN = 100


def scale(t):
    return (1.0 + 0.5*np.asarray(t))**2


LSCALE = 1.0      # --lscale: the same Newtonian run in a box lambda times larger


def read_scaled(fn):
    """Snapshot with x -> lambda x, p -> lambda p, m -> lambda^3 m: the Newtonian
    problem is invariant under this scaling at fixed t (rho_c and the expansion
    unchanged, Phi -> lambda^2 Phi), so a run of box L stands for the box lambda L;
    only light-speed effects (the GW wave equation) break the invariance."""
    t, cyc, x, p, m, tag = read_snapshot(fn)
    lam = LSCALE
    return t, cyc, x*lam, p*lam, m*lam**3, tag


def snapshots(d):
    return sorted(glob.glob(os.path.join(d, "newton.part.*.bin")))


# ---------------------------------------------------------------------------------------
# halos
# ---------------------------------------------------------------------------------------
def fof(x, L, spacing, b=0.2):
    xw = np.mod(x, L)
    xw[xw >= L] = 0.0
    tree = cKDTree(xw, boxsize=L)
    pairs = tree.query_pairs(b*spacing, output_type="ndarray")
    n = len(x)
    g = coo_matrix((np.ones(len(pairs), dtype=np.int8), (pairs[:, 0], pairs[:, 1])),
                   shape=(n, n))
    _, lab = connected_components(g, directed=False)
    return lab


def unwrap_about(x, ref, L):
    return ref + np.mod(x - ref + 0.5*L, L) - 0.5*L


def halo_catalog(x, p, m, tag, a, L, spacing):
    lab = fof(x, L, spacing)
    cnt = np.bincount(lab)
    ids = np.nonzero(cnt >= NMIN)[0]
    out = []
    for h in ids:
        sel = np.nonzero(lab == h)[0]
        xs = unwrap_about(x[sel], x[sel[0]], L)
        ms = m[sel]
        M = ms.sum()
        xc = (ms[:, None]*xs).sum(0)/M
        r = np.sqrt(((xs - xc)**2).sum(1))
        order = np.argsort(r)
        cm = np.cumsum(ms[order])
        rhalf = float(r[order][np.searchsorted(cm, 0.5*M)])
        v = p[sel]/a
        vc = (ms[:, None]*v).sum(0)/M
        sig = float(np.sqrt((ms*((v - vc)**2).sum(1)).sum()/M))
        out.append({"N": int(len(sel)), "M": float(M), "x": np.mod(xc, L).tolist(),
                    "r_half": rhalf, "sigma_v": sig,
                    "GM_over_r_phys": float(M/(a*max(rhalf, 1e-12))),
                    "tags": tag[sel]})
    out.sort(key=lambda h: -h["M"])
    return out, int((cnt >= 32).sum())


# ---------------------------------------------------------------------------------------
# GW of the box
# ---------------------------------------------------------------------------------------
def cic(x, w, n, L):
    """Cloud-in-cell deposit of weights w (N,) or (N, c) on an n^3 periodic mesh with
    cell centres at (i + 1/2) L/n; returns density per comoving volume."""
    h = L/n
    s = x/h - 0.5
    i0 = np.floor(s).astype(np.int64)
    f = s - i0
    w2 = w if w.ndim == 2 else w[:, None]
    out = np.zeros((w2.shape[1], n*n*n))
    for dx in (0, 1):
        wx = f[:, 0] if dx else 1.0 - f[:, 0]
        ix = (i0[:, 0] + dx) % n
        for dy in (0, 1):
            wy = f[:, 1] if dy else 1.0 - f[:, 1]
            iy = (i0[:, 1] + dy) % n
            for dz in (0, 1):
                wz = f[:, 2] if dz else 1.0 - f[:, 2]
                iz = (i0[:, 2] + dz) % n
                idx = (ix*n + iy)*n + iz
                wt = wx*wy*wz
                for c in range(w2.shape[1]):
                    out[c] += np.bincount(idx, weights=wt*w2[:, c], minlength=n**3)
    out = out.reshape((w2.shape[1], n, n, n))/h**3
    return out if w.ndim == 2 else out[0]


class TTBox:
    """Fourier mesh, TT projector, and the Filon accumulators of C and S."""

    def __init__(self, n, L):
        self.n, self.L = n, L
        k1 = 2*np.pi*np.fft.fftfreq(n, d=L/n)
        kz = 2*np.pi*np.fft.rfftfreq(n, d=L/n)
        self.k = [k1[:, None, None]*np.ones((1, n, n//2 + 1)),
                  k1[None, :, None]*np.ones((n, 1, n//2 + 1)),
                  kz[None, None, :]*np.ones((n, n, 1))]
        k2 = sum(c*c for c in self.k)
        self.k2 = k2
        self.kk = np.sqrt(k2)
        k2s = k2.copy()
        k2s[0, 0, 0] = 1.0
        self.k2s = k2s
        e = [c/np.sqrt(k2s) for c in self.k]
        self.P = [[(1.0 if i == j else 0.0) - e[i]*e[j] for j in range(3)] for i in range(3)]
        w = np.full(n//2 + 1, 2.0)
        w[0] = 1.0
        if n % 2 == 0:
            w[-1] = 1.0
        self.w = np.broadcast_to(w[None, None, :], k2.shape)   # rfft multiplicity
        # keep the modes off the Nyquist planes and k != 0
        nyq = np.zeros(k2.shape, dtype=bool)
        if n % 2 == 0:
            m1 = np.abs(np.fft.fftfreq(n)*n) == n//2
            nyq |= m1[:, None, None] | m1[None, :, None]
            nyq[:, :, -1] = True
        self.ok = (~nyq) & (k2 > 0)
        self.C = None
        self.prev = None

    def tt(self, Sk):
        """TT part of the six rfft components {(i,j): array}; returns 3x3 nested list."""
        def s(i, j):
            return Sk[(min(i, j), max(i, j))]
        trP = sum(self.P[l][m]*s(l, m) for l in range(3) for m in range(3))
        out = {}
        for i in range(3):
            for j in range(i, 3):
                acc = 0.0
                for l in range(3):
                    for m in range(3):
                        acc = acc + self.P[i][l]*self.P[j][m]*s(l, m)
                out[(i, j)] = (acc - 0.5*self.P[i][j]*trP)*self.ok
        return out

    def source(self, x, p, m, a):
        """F = a S^TT on the mesh (rfft, fftn/N normalization), six components."""
        n, L = self.n, self.L
        N = n**3
        v = p/a
        comp = [(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)]
        w = np.stack([m] + [m*v[:, i]*v[:, j] for (i, j) in comp], axis=1)
        dep = cic(np.mod(x, L), w, n, L)
        rho = dep[0]
        rk = np.fft.rfftn(rho - rho.mean())/N
        phik = -4*np.pi*rk/self.k2s                        # Phi_c
        phik[0, 0, 0] = 0.0
        g = [np.fft.irfftn(1j*kc*phik*N, s=(n, n, n), axes=(0, 1, 2)) for kc in self.k]   # d_i Phi_c
        Sk = {}
        for c, (i, j) in enumerate(comp):
            sreal = 16*np.pi*dep[c + 1]/a + 4.0*g[i]*g[j]/a**2
            Sk[(i, j)] = a*np.fft.rfftn(sreal)/N
        return self.tt(Sk)

    def add(self, t, F):
        """Filon step from the previous sample to (t, F): Z+- += int F e^{+-ikt} dt with
        F linear in t between the samples (the oscillatory integral exact)."""
        kk = self.kk
        if self.C is None:
            self.C = True
            self.Zp = {key: np.zeros_like(val) for key, val in F.items()}
            self.Zm = {key: np.zeros_like(val) for key, val in F.items()}
            self.first = (t, F)
            self.second = None
            self.prevprev = None
            self.prev = (t, F)
            return
        t0, F0 = self.prev
        if self.second is None:
            self.second = (t, F)
        self.prevprev = self.prev
        h = t - t0
        th = kk*h
        small = th < 1e-3
        ths = np.where(small, 1.0, th)
        kks = np.where(kk > 0, kk, 1.0)
        e1 = np.exp(1j*th)
        # I0 = int_0^h e^{iks} ds, I1 = (1/h) int_0^h s e^{iks} ds
        I0 = np.where(small, h*(1 + 0.5j*th), (e1 - 1)/(1j*kks))
        I1 = np.where(small, h*(0.5 + 1j*th/3), h*(e1/(1j*ths) + (e1 - 1)/ths**2))
        ph = np.exp(1j*kk*t0)
        for key in F:
            a0, a1 = F0[key], F[key]
            self.Zp[key] += ph*(a0*I0 + (a1 - a0)*I1)
            self.Zm[key] += np.conj(ph)*(a0*np.conj(I0) + (a1 - a0)*np.conj(I1))
        self.prev = (t, F)

    def energies(self, t, F):
        """a^4 rho of: the waves the box would hold if the source stopped at t
        (sw: 'switch-off', the measure of arXiv:2212.00425), the radiated part with both
        boundary terms removed (rad: the source switched on and off adiabatically,
        Z_ad = Z - [F e^{ikt}/(ik)] at t and at the first sample; the first-sample term is
        the start without the quasi-static TT field, the junk of conformally flat data),
        and the quasi-static near field (qs, gradient energy of F/k^2); spectra of rad
        and qs in |k| shells of width k_f."""
        kk = np.where(self.kk > 0, self.kk, 1.0)
        t0, Fi = self.first
        sw = np.zeros(self.k2.shape)
        rad1 = np.zeros(self.k2.shape)
        rad = np.zeros(self.k2.shape)
        qs = np.zeros(self.k2.shape)
        have_d = self.second is not None and self.prevprev is not None
        for key in F:
            mult = 1.0 if key[0] == key[1] else 2.0
            zp, zm = self.Zp[key], self.Zm[key]
            sw += mult*0.5*(np.abs(zp)**2 + np.abs(zm)**2)
            ep, e0p = np.exp(1j*kk*t), np.exp(1j*kk*t0)
            bp = (F[key]*ep - Fi[key]*e0p)/(1j*kk)
            bm = (F[key]*np.conj(ep) - Fi[key]*np.conj(e0p))/(-1j*kk)
            zp1, zm1 = zp - bp, zm - bm
            rad1 += mult*0.5*(np.abs(zp1)**2 + np.abs(zm1)**2)
            if have_d:
                # second boundary order [F' e^{+-ikt}]/k^2, one-sided differences
                tq, Fq = self.prevprev
                dF = (F[key] - Fq[key])/(t - tq)
                ts, Fs = self.second
                dFi = (Fs[key] - Fi[key])/(ts - t0)
                cp = (dF*ep - dFi*e0p)/kk**2
                cm = (dF*np.conj(ep) - dFi*np.conj(e0p))/kk**2
                zp1, zm1 = zp1 - cp, zm1 - cm
            rad += mult*0.5*(np.abs(zp1)**2 + np.abs(zm1)**2)
            qs += mult*np.abs(F[key])**2/self.k2s
        sw *= self.w/(64*np.pi)
        rad1 *= self.w/(64*np.pi)
        rad *= self.w/(64*np.pi)
        qs *= self.w/(32*np.pi)
        kf = 2*np.pi/self.L
        b = np.rint(self.kk/kf).astype(int)
        nb = self.n//2
        spec = np.bincount(b[self.ok], weights=rad[self.ok], minlength=nb + 2)[:nb + 1]
        specq = np.bincount(b[self.ok], weights=qs[self.ok], minlength=nb + 2)[:nb + 1]
        return (float(sw[self.ok].sum()), float(rad1[self.ok].sum()),
                float(rad[self.ok].sum()), float(qs[self.ok].sum()), spec, specq)


# ---------------------------------------------------------------------------------------
def circ_centre(x, L):
    """Periodic centre of a set of points (circular mean per axis)."""
    ang = 2*np.pi*x/L
    c = np.angle(np.exp(1j*ang).mean(axis=0))
    return np.mod(c*L/(2*np.pi), L)


def quadrupole_tracks(files, tag_sets, L, a_max):
    """Comoving traceless second moments Qc_ij(t) = sum m (y_i y_j - y^2 delta_ij/3) of
    each set of particles (tags) about its periodic centre of mass, for the snapshots
    with a <= a_max; returns t, a, a list of (n, 6) arrays, and the centres at the first
    snapshot (Lagrangian centres)."""
    T, A = [], []
    Qs = [[] for _ in tag_sets]
    cen0 = []
    for fn in files:
        t, _, x, p, m, tag = read_scaled(fn)
        a = float(scale(t))
        if a > a_max*1.0001:
            break
        order = np.argsort(tag)
        for k, ts in enumerate(tag_sets):
            sel = order[np.searchsorted(tag[order], np.sort(ts))]
            c = circ_centre(x[sel], L)
            xs = unwrap_about(x[sel], c, L)
            ms = m[sel]
            xc = (ms[:, None]*xs).sum(0)/ms.sum()
            if not T:
                cen0.append(np.mod(xc, L))
            y = xs - xc
            y2 = (y*y).sum(1)
            Qs[k].append([(ms*(y[:, i]*y[:, j] - (y2/3.0 if i == j else 0.0))).sum()
                          for (i, j) in ((0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2))])
        T.append(t)
        A.append(a)
    return np.array(T), np.array(A), [np.array(q) for q in Qs], cen0


def quad_energy(t, Qc, win=7):
    """Quadrupole-formula power of Q = a^2 (Qc(t) - Qc(t_0)) in cosmic time T (dT = a dt).
    The constant anisotropy of the Lagrangian region would give a spurious
    -Qc(t_0) a^(-5/2) (a^2 times a constant in the matter era) and is removed.
    Derivatives in t by Savitzky-Golay (cubic, win samples, uniform t) and the chain rule
    f_TTT = f_ttt/a^3 - 3 a' f_tt/a^4 + (3 a'^2 - a a'') f_t/a^5, a = (1 + t/2)^2.
    Returns P(t) = (1/5) sum_ij (d^3 Q_ij/dT^3)^2 and E(t) = int P a dt."""
    s = 1 + 0.5*t
    a, ad, add = s*s, s, 0.5
    Q = (a[:, None]**2)*(Qc - Qc[0])
    dt = t[1] - t[0]
    q1 = savgol_filter(Q, win, 3, deriv=1, delta=dt, axis=0)
    q2 = savgol_filter(Q, win, 3, deriv=2, delta=dt, axis=0)
    q3 = savgol_filter(Q, win, 3, deriv=3, delta=dt, axis=0)
    A1, A2 = a[:, None], ad[:, None]
    Q3 = q3/A1**3 - 3*A2*q2/A1**4 + (3*A2**2 - A1*add)*q1/A1**5
    wts = np.array([1, 2, 2, 1, 2, 1], dtype=float)
    P = 0.2*(wts*Q3*Q3).sum(1)
    E = np.concatenate([[0.0], np.cumsum(0.5*(P[1:]*a[1:] + P[:-1]*a[:-1])*np.diff(t))])
    return P, E


def analyze_case(name, d, gw, ng, nhalo_q, out, design=None):
    meta = json.load(open(os.path.join(d, "meta.json")))
    L, n, ppc = meta["L"]*LSCALE, meta["n"], meta["ppc"]
    spacing = L/(n*ppc)
    files = snapshots(d)
    res = {"name": name, "dir": d, "meta": meta, "snapshots": len(files)}
    if not (meta["seed"] == 1 and meta["nc"] == 3.2 and meta["sigma1_target"] == 0.0562
            and L == 4.0):
        design = None                      # the maxima of design.json are of this field only
    hst = read_newton_hst(os.path.join(d, "newton.newton.hst"))
    aW = np.abs(hst["a"]*hst["W"])
    res["layzer_irvine"] = {"max_abs_C_change_over_max_aW":
                            float(np.max(np.abs(hst["C"] - hst["C"][0]))/aW.max()),
                            "a_end": float(hst["a"][-1]), "cycles": int(hst["ncycle"][-1])}
    # halo catalogues at chosen scale factors (nearest snapshot)
    times = []
    for fn in files:
        with open(fn, "rb") as f:
            f.read(8)
            times.append(np.frombuffer(f.read(8), "<f8")[0])
    times = np.array(times)
    avals = scale(times)
    targets = [5, 7.5, 10, 12.5, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100]
    cats = []
    for at in targets:
        if at > avals[-1]*1.0001:
            continue
        i = int(np.argmin(np.abs(avals - at)))
        t, _, x, p, m, tag = read_scaled(files[i])
        a = float(scale(t))
        hal, n32 = halo_catalog(x, p, m, tag, a, L, spacing)
        cats.append({"a": a, "t": float(t), "n_halos": len(hal), "n_groups_32": n32,
                     "masses": [h["M"] for h in hal], "N": [h["N"] for h in hal],
                     "r_half": [h["r_half"] for h in hal],
                     "sigma_v": [h["sigma_v"] for h in hal],
                     "GM_over_r": [h["GM_over_r_phys"] for h in hal],
                     "x": [h["x"] for h in hal],
                     "f_mass_in_halos": float(sum(h["M"] for h in hal)/m.sum())})
    res["catalogs"] = cats
    t, _, x, p, m, tag = read_scaled(files[-1])
    last_halos, _ = halo_catalog(x, p, m, tag, float(scale(t)), L, spacing)
    # first halo: scan snapshots from early to late at a coarse cadence
    first = None
    for i in range(0, len(files), max(1, len(files)//60)):
        t, _, x, p, m, tag = read_scaled(files[i])
        a = float(scale(t))
        hal, _ = halo_catalog(x, p, m, tag, a, L, spacing)
        if hal:
            first = {"a": a, "N": hal[0]["N"], "M": hal[0]["M"]}
            break
    res["first_halo"] = first
    if gw:
        box = TTBox(ng, L)
        rows = []
        specs = {}
        for i, fn in enumerate(files):
            t, _, x, p, m, tag = read_scaled(fn)
            a = float(scale(t))
            F = box.source(x, p, m, a)
            box.add(t, F)
            if i == 0:
                F0 = F
            sw, rad1, rad, qs, spec, specq = box.energies(t, F)
            rows.append([t, a, sw, rad1, rad, qs, sw/(a*RHO_C), rad1/(a*RHO_C),
                         rad/(a*RHO_C), qs/(a*RHO_C)])
            for at in (2, 5, 10, 20, 40, 70, 100):
                if abs(a - at)/at < 0.03 and str(at) not in specs:
                    specs[str(at)] = {"a": a, "rad": spec.tolist(), "qs": specq.tolist()}
        res["gw"] = {"columns": ["t", "a", "a4_rho_switchoff", "a4_rho_rad1", "a4_rho_rad",
                                 "a4_rho_qs", "Omega_switchoff", "Omega_rad1",
                                 "Omega_rad", "Omega_qs"],
                     "rows": rows, "spectra": specs, "ng": ng}
        # check against (20/3) [dPhi dPhi]^TT at the first snapshot (design.json:
        # quasi_static.Omega_qs_over_a at a = 1)
        res["gw"]["Omega_qs_first"] = rows[0][9]
        # quadrupole formula during formation: the halos found at a = a_id (nearest
        # snapshot), followed from a = 1 to 1.5 a_id (the Lagrangian regions of the
        # halos of a = 100 span up to half the box and cannot be unwrapped); matched to
        # the maxima of the initial field (design.json) by their Lagrangian centre
        a_id = 20.0
        i_id = int(np.argmin(np.abs(avals - a_id)))
        t, _, x, p, m, tag = read_scaled(files[i_id])
        hal_id, _ = halo_catalog(x, p, m, tag, float(scale(t)), L, spacing)
        sel_h = hal_id[:nhalo_q]
        qrows = []
        if sel_h:
            tq, aq, Qlist, cen0 = quadrupole_tracks(files, [h["tags"] for h in sel_h], L,
                                                    1.5*a_id)
            for h, Qc, c0 in zip(sel_h, Qlist, cen0):
                P, E = quad_energy(tq, Qc)
                # comoving GW energy: int P a (a dt), emitted energy times its a
                aE = float(np.sum(0.5*(P[1:]*aq[1:]**2 + P[:-1]*aq[:-1]**2)*np.diff(tq)))
                qrows.append({"M": h["M"], "N": h["N"], "a_id": float(scale(t)),
                              "lagrangian_centre": [float(v) for v in c0],
                              "E": float(E[-1]), "aE_comoving": aE,
                              "a": aq[::2].tolist(), "P": P[::2].tolist(),
                              "E_cum": E[::2].tolist()})
        res["quadrupole_halos"] = qrows
        res["gw"]["Omega_quad_sum"] = {
            "a": float(1.5*a_id),
            "Omega": float(sum(q["aE_comoving"] for q in qrows)/(1.5*a_id*L**3*RHO_C))}
        if design:
            pk = [(np.array(r["cell"]) + 0.5)*L/64 for r in design["peaks_seed1"]]
            for q in qrows:
                c = np.array(q["lagrangian_centre"])
                dd = [float(np.sqrt((((pp - c + L/2) % L - L/2)**2).sum())) for pp in pk]
                j = int(np.argmin(dd))
                r = design["peaks_seed1"][j]
                q["match"] = {"distance": dd[j], "nu": r["nu"],
                              "E_baseline": r.get("E_code_L4"), "a_x": r.get("a_x")}
    return res


def figures(results, od, gwname):
    fs.use_style()
    import matplotlib.pyplot as plt
    # 1. halo counts and mass fraction against a
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.8))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.17, top=0.92, wspace=0.35)
    cols = fs.series_colors(max(len(results), 2))
    for c, r in zip(cols, results):
        a = [x["a"] for x in r["catalogs"]]
        axs[0].plot(a, [x["n_halos"] for x in r["catalogs"]], "-o", ms=3, color=c,
                    label=r["name"])
        axs[0].plot(a, [x["n_groups_32"] for x in r["catalogs"]], ":", color=c)
        axs[1].plot(a, [x["f_mass_in_halos"] for x in r["catalogs"]], "-o", ms=3, color=c)
        last = r["catalogs"][-1] if r["catalogs"] else {"masses": [], "a": 0.0}
        mm = np.sort(np.array(last["masses"]))[::-1]
        if len(mm):
            axs[2].loglog(mm, np.arange(1, len(mm) + 1), drawstyle="steps-post",
                          color=c, label=f"{r['name']}, a = {last['a']:.0f}")
    axs[0].set_xscale("log")
    axs[0].set_xlabel(r"$a$")
    axs[0].set_ylabel(r"halos ($\geq 100$ part.; dotted $\geq 32$)")
    axs[0].legend(fontsize=7)
    axs[1].set_xscale("log")
    axs[1].set_xlabel(r"$a$")
    axs[1].set_ylabel("mass fraction in halos")
    axs[2].set_xlabel(r"halo mass $M$ (code units)")
    axs[2].set_ylabel(r"$N(>M)$")
    axs[2].legend(fontsize=7)
    fs.save(fig, os.path.join(od, "pop_halos"))
    plt.close(fig)
    # 2. projected density of the GW case at four epochs
    r = next(x for x in results if x["name"] == gwname)
    files = snapshots(r["dir"])
    L = r["meta"]["L"]*LSCALE
    times = []
    for fn in files:
        with open(fn, "rb") as f:
            f.read(8)
            times.append(np.frombuffer(f.read(8), "<f8")[0])
    av = scale(np.array(times))
    fig, axs = plt.subplots(1, 4, figsize=(fs.FULL_WIDTH, 2.25))
    fig.subplots_adjust(left=0.01, right=0.99, bottom=0.02, top=0.88, wspace=0.02)
    for ax, at in zip(axs, (5, 15, 30, av[-1])):
        i = int(np.argmin(np.abs(av - at)))
        t, _, x, p, m, tag = read_scaled(files[i])
        H, _, _ = np.histogram2d(np.mod(x[:, 0], L), np.mod(x[:, 1], L), bins=128,
                                 range=[[0, L], [0, L]], weights=m)
        H = H/H.mean()
        ax.imshow(H.T, origin="lower", extent=[0, L, 0, L], cmap=fs.CMAP["dens"],
                  norm=fs.LogNorm(vmin=0.1, vmax=max(H.max(), 10.0)),
                  interpolation="none", rasterized=True)
        cat = (min(r["catalogs"], key=lambda c: abs(c["a"] - scale(t)))
               if r["catalogs"] else {"x": [], "N": []})
        for xc, nn in zip(cat["x"], cat["N"]):
            ax.add_patch(plt.Circle((xc[0], xc[1]), 0.08 + 0.02*np.log10(nn),
                                    fill=False, color="w", lw=0.6))
        ax.set_title(f"a = {scale(t):.1f}", fontsize=9)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_aspect("equal")
    fs.save(fig, os.path.join(od, "pop_density"))
    plt.close(fig)
    # 3. GW energy against a and spectra
    if "gw" in r:
        rows = np.array(r["gw"]["rows"])
        fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
        fig.subplots_adjust(left=0.09, right=0.98, bottom=0.15, top=0.92, wspace=0.3)
        ax = axs[0]
        ax.loglog(rows[:, 1], rows[:, 8], color=fs.PAL["red"],
                  label="radiated (box, TT stress)")
        ax.loglog(rows[:, 1], rows[:, 7], color=fs.PAL["red"], ls=":", lw=1.0,
                  label="radiated, first order removed only")
        ax.loglog(rows[:, 1], rows[:, 6], color=fs.PAL["orange"], ls="-.",
                  label="switch-off measure (2212.00425)")
        ax.loglog(rows[:, 1], rows[:, 9], color=fs.PAL["blue"], ls="--",
                  label="quasi-static near field")
        if r.get("quadrupole_halos"):
            oq = r["gw"]["Omega_quad_sum"]
            ax.plot([oq["a"]], [oq["Omega"]], "s", color=fs.PAL["green"],
                    label="quadrupole formula, halos of a = 20")
        if r.get("design"):
            dz = r["design"]
            ax.loglog(dz["a"], dz["Omega_rad"], color="k", lw=1.0,
                      label="baseline model A (design)")
        ax.set_ylim(1e-13, 1e-5)
        ax.set_xlim(1.0, 1.1*rows[-1, 1])
        ax.set_xlabel(r"$a$")
        ax.set_ylabel(r"$\rho_{\rm GW}/\bar\rho$")
        ax.legend(fontsize=7)
        ax = axs[1]
        kf = 2*np.pi/L
        cs = fs.series_colors(len(r["gw"]["spectra"]))
        for c, (key, sp) in zip(cs, sorted(r["gw"]["spectra"].items(),
                                          key=lambda kv: float(kv[0]))):
            s = np.array(sp["rad"])/(sp["a"]*RHO_C)
            q = np.array(sp["qs"])/(sp["a"]*RHO_C)
            kb = kf*np.arange(len(s))
            ax.loglog(kb[1:], s[1:], color=c, label=f"a = {sp['a']:.0f}")
            ax.loglog(kb[1:], q[1:], color=c, ls=":")
        ax.set_xlabel(r"$|k|$ (shells of width $k_f$)")
        ax.set_ylabel(r"$\Omega$ per shell (dotted: near field)")
        ax.legend(fontsize=7, ncol=2)
        fs.save(fig, os.path.join(od, "pop_gw"))
        plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", action="append", required=True, help="NAME:DIR")
    ap.add_argument("--gw", default=None, help="case name for the GW analysis")
    ap.add_argument("--ng", type=int, default=64)
    ap.add_argument("--nhalo-q", type=int, default=5)
    ap.add_argument("--design", default=None, help="design.json for the overlay")
    ap.add_argument("--tag", default="")
    ap.add_argument("--lscale", type=float, default=1.0,
                    help="analyse the run as the box lambda L (x, p scaled by lambda)")
    a = ap.parse_args()
    global LSCALE
    LSCALE = a.lscale
    od = os.environ.get("NRPIC_RUN_DIR") or os.path.join(ROOT, "..", "..", "scratch",
                                                         "B-emd-gw", "tmp", "analyze")
    os.makedirs(od, exist_ok=True)
    results = []
    dz = json.load(open(a.design)) if a.design else None
    for c in a.case:
        name, d = c.split(":", 1)
        print("case", name, flush=True)
        results.append(analyze_case(name, d, name == a.gw, a.ng, a.nhalo_q, od, dz))
    if a.design:
        for r in results:
            if r["name"] == a.gw:
                r["design"] = {"a": dz["press_schechter"]["a"],
                               "Omega_rad": dz["Omega_rad_baseline_L4"]}
    figures(results, od, a.gw or results[0]["name"])

    def clean(o):
        if isinstance(o, dict):
            return {k: clean(v) for k, v in o.items() if k != "tags"}
        if isinstance(o, list):
            return [clean(v) for v in o]
        if isinstance(o, (np.floating, np.integer)):
            return o.item()
        return o
    fn = f"analysis{a.tag}.json"
    with open(os.path.join(od, fn), "w") as f:
        json.dump(clean(results), f, indent=1)
    if os.environ.get("NRPIC_RUN_DIR"):          # registered runs only: copies
        shutil.copy(os.path.join(od, fn), os.path.join(PKG, "results", fn))
        for g in ("pop_halos", "pop_density", "pop_gw"):
            if os.path.exists(os.path.join(od, g + ".png")):
                shutil.copy(os.path.join(od, g + ".png"),
                            os.path.join(PKG, "figs", f"{g}{a.tag}.png"))
    for r in results:
        print(r["name"], "first halo", r["first_halo"], "LI", r["layzer_irvine"])
        for c in r["catalogs"]:
            print(f"  a={c['a']:.1f} halos={c['n_halos']} groups32={c['n_groups_32']} "
                  f"fmass={c['f_mass_in_halos']:.3f} Mmax="
                  f"{max(c['masses']) if c['masses'] else 0:.4f}")
        if "gw" in r:
            print("  GW end", r["gw"]["rows"][-1], "quad", r["gw"].get("Omega_quad_sum"))
            for q in r.get("quadrupole_halos", []):
                print("   halo M=%.4f N=%d E=%.3e match=%s" % (q["M"], q["N"], q["E"],
                                                             q.get("match")))


if __name__ == "__main__":
    main()
