"""V3: the verifier's own Kerr spike in the equatorial plane (constant f and adiabatic
growth from a Hernquist halo), written from Ferrer, da Rosa and Will, arXiv:1707.06302
(kb-data/raw/arxiv/1707.06302/v2/src/kerrdm.tex: current eq. final_current :396-407,
density eq. :412-416, capture criterion :462-473, adiabatic invariants :523-553,
Hernquist DF :860-881, radial invariant :897-920, f0 :763-764), without the track's
kerr_lib.py / spike_lib.py. Own digitiser of the paper's pgf figures (fig_rho_a.pgf,
fig_rho_hern.pgf; untrusted data, parsed as text only).

Units G = c = m_BH = 1. Carter constant C of the paper = Q + Lz^2 (Q the usual one).
At theta = pi/2 the C integral is done with C = Lz^2 + (Cmax - Lz^2)(1 - cos psi)/2, so
dC/(sqrt(V) sqrt(U)) = r^2/sqrt(Delta) dpsi and
    J_t = -(2/sqrt(Delta)) int dE dLz dpsi E f,   J_phi = (2/sqrt(Delta)) int dE dLz dpsi Lz f.
A (E, C, Lz) orbit counts if E < 1, V(r) >= 0 and it is not captured: the radial quartic
has four real roots r1 >= r2 > r3 >= r4 with r2 <= r <= r1 and r3 >= r_+ (a barrier between
r and the horizon). The condition r3 >= r_+ was missing in my first version; for a != 0 and
Q = 0 it let plunging equatorial orbits count (JOURNAL entry 3).
"""
import argparse
import json
import math
import os
import re

import numpy as np

# ------------------------------------------------------------------ Kerr pieces
def quartic_coeffs(E, Q, Lz, a):
    """R(r) = (E^2-1) r^4 + 2 r^3 + [a^2(E^2-1) - Lz^2 - Q] r^2 + 2[(Lz-aE)^2+Q] r - a^2 Q"""
    E, Q, Lz = np.broadcast_arrays(E, Q, Lz)
    return np.stack([E ** 2 - 1, 2.0 + 0 * E, a * a * (E ** 2 - 1) - Lz ** 2 - Q,
                     2 * ((Lz - a * E) ** 2 + Q), -a * a * Q + 0 * E], axis=-1)


def V_paper(r, E, C, Lz, a):
    """eq. (potential) of 1707.06302, kerrdm.tex:366-369."""
    D = r * r + a * a - 2 * r
    return ((1 + a * a / r ** 2 + 2 * a * a / r ** 3) * E ** 2 - D / r ** 2 * (1 + C / r ** 2)
            + a * a * Lz ** 2 / r ** 4 - 4 * a * E * Lz / r ** 3)


def roots4(E, Q, Lz, a):
    """sorted real parts (descending) and a flag that all four roots are real."""
    c = quartic_coeffs(E, Q, Lz, a)
    lead = c[..., 0:1]
    mon = c[..., 1:] / lead
    n = mon.shape[:-1]
    M = np.zeros(n + (4, 4))
    M[..., 0, :] = -mon
    M[..., 1, 0] = 1
    M[..., 2, 1] = 1
    M[..., 3, 2] = 1
    ev = np.linalg.eigvals(M.reshape(-1, 4, 4)).reshape(n + (4,))
    scale = np.maximum(np.abs(ev).max(-1), 1.0)
    real = np.all(np.abs(ev.imag) <= 1e-7 * scale[..., None], axis=-1)
    rr = -np.sort(-ev.real, axis=-1)
    return rr, real


def valid_orbit(r, E, Q, Lz, a, tol=1e-9):
    rr, real = roots4(E, Q, Lz, a)
    r1, r2, r3 = rr[..., 0], rr[..., 1], rr[..., 2]
    # the barrier (r3, r2) must lie outside the horizon: with Q = 0 a root sits at r = 0 and
    # r2, r3 can both be inside r_+ (then the orbit plunges although r2 > r3)
    rplus = 1 + math.sqrt(max(1 - a * a, 0.0))
    return (real & (r2 > r3 + 1e-6 * r2) & (r3 >= rplus * (1 - 1e-9)) & (r <= r1 * (1 + tol) + tol)
            & (r >= r2 * (1 - tol) - tol) & (E < 1))


def Cmax_eq(r, E, Lz, a):
    """largest C with V(r) >= 0 (V is linear in C)."""
    D = r * r + a * a - 2 * r
    V0 = V_paper(r, E, 0.0, Lz, a)
    return V0 * r ** 4 / D


def I_theta(E, Q, Lz, a, n=24):
    x, w = np.polynomial.legendre.leggauss(n)
    phi = (x + 1) * (np.pi / 4)
    w = w * (np.pi / 4)
    beta = 1 - E ** 2
    S = Q + Lz ** 2 + a * a * beta
    disc = np.sqrt(np.maximum(S * S - 4 * a * a * beta * Q, 0))
    zm = np.where(Q > 0, 2 * Q / (S + disc), 0.0)
    zm = np.minimum(zm, 1.0)
    s2 = np.sin(phi) ** 2
    zmq = np.where(zm > 0, zm, 1.0)
    term = np.sqrt(np.maximum(Q[..., None] / zmq[..., None] - a * a * beta[..., None] * zmq[..., None] * s2, 0))
    integ = zm[..., None] * np.cos(phi) ** 2 * term / (1 - zm[..., None] * s2)
    return 4 * np.sum(integ * w, axis=-1) * (Q > 0)


def I_r_kerr(E, Q, Lz, a, n=48):
    rr, real = roots4(E, Q, Lz, a)
    r1, r2, r3, r4 = (rr[..., k] for k in range(4))
    k = np.arange(1, n + 1)
    y = np.cos(k * np.pi / (n + 1))
    w = np.pi / (n + 1) * np.sin(k * np.pi / (n + 1)) ** 2   # int sqrt(1-y^2) g dy
    c = 0.5 * (r1 + r2)
    h = 0.5 * (r1 - r2)
    rn = c[..., None] + h[..., None] * y
    D = rn ** 2 + a * a - 2 * rn
    g = np.sqrt(np.maximum((1 - E[..., None] ** 2) * (rn - r3[..., None]) * (rn - r4[..., None]), 0)) / D
    return 2 * h ** 2 * np.sum(g * w, axis=-1)


# ------------------------------------------------------------------ Hernquist halo
def hern_Ir(delta, Lt, n=48):
    """radial action (closed orbit, both legs) in units sqrt(G M r_s) for the Hernquist
    potential, relative binding delta = 1 - eps~, L~ = L / sqrt(G M r_s). Scaled radius
    s = x/delta; turning points from the cubic -(2-2d)s^3 + 2s^2 - l d s - l, l = L~^2/d^3.
    Returns nan where no orbit exists (delta below the circular value)."""
    d = delta
    l = Lt ** 2 / d ** 3
    A = 2 - 2 * d
    mon = np.stack([-2 / A, l * d / A, l / A], axis=-1)
    n0 = mon.shape[:-1]
    M = np.zeros(n0 + (3, 3))
    M[..., 0, :] = -mon
    M[..., 1, 0] = 1
    M[..., 2, 1] = 1
    ev = np.linalg.eigvals(M.reshape(-1, 3, 3)).reshape(n0 + (3,))
    real = np.all(np.abs(ev.imag) <= 1e-9 * np.maximum(np.abs(ev).max(-1), 1)[..., None], axis=-1)
    rr = -np.sort(-ev.real, axis=-1)
    sp, sm, s3 = rr[..., 0], rr[..., 1], rr[..., 2]
    # polish the two positive roots with Newton steps on the cubic
    def cub(s):
        return -A * s ** 3 + 2 * s ** 2 - l * d * s - l

    def dcub(s):
        return -3 * A * s ** 2 + 4 * s - l * d
    for _ in range(3):
        sp = sp - cub(sp) / np.where(dcub(sp) != 0, dcub(sp), 1)
        sm = sm - cub(sm) / np.where(dcub(sm) != 0, dcub(sm), 1)
    ok = real & (sm > 0) & (sp > sm)
    k = np.arange(1, n + 1)
    y = np.cos(k * np.pi / (n + 1))
    w = np.pi / (n + 1) * np.sin(k * np.pi / (n + 1)) ** 2
    c = 0.5 * (sp + sm)
    h = 0.5 * (sp - sm)
    s = c[..., None] + h[..., None] * y
    g = np.sqrt(np.maximum(A[..., None] * (s - s3[..., None]) / (s ** 2 * (1 + d[..., None] * s)), 0))
    I = 2 * d ** 1.5 * h ** 2 * np.sum(g * w, axis=-1)
    return np.where(ok, I, np.nan)


def hern_delta(T, Lt, iters=60):
    """delta with hern_Ir(delta, Lt) = T (vectorised bisection in log delta)."""
    lo = np.full(T.shape, math.log(1e-14))
    hi = np.zeros(T.shape)
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        I = hern_Ir(np.exp(mid), Lt)
        big = np.isfinite(I) & (I > T)
        hi = np.where(big, mid, hi)
        lo = np.where(big, lo, mid)
    d = np.exp(0.5 * (lo + hi))
    unbound = hi >= -1e-12   # never found I > T below delta = 1
    return d, unbound


def ftilde_hern(delta):
    """dimensionless Hernquist DF of kerrdm.tex:869-872 with eps~ = 1 - delta."""
    e = 1 - delta
    br = (2 * delta - 1) * (3 - 14 * delta + 8 * delta ** 2) + 3 * np.arccos(np.sqrt(delta)) / np.sqrt(e * delta)
    return np.sqrt(e) / delta ** 2 * br


# ------------------------------------------------------------------ the density
class Spike:
    def __init__(self, a, kind, M_sun=1e12, rs_pc=2.0e4, m_sun=4e6, nE=48, nL=48, npsi=20,
                 variant="paper"):
        self.a, self.kind, self.variant = a, kind, variant
        self.nE, self.nL, self.npsi = nE, nL, npsi
        Gc2_sun_m = 1476.625     # G M_sun / c^2 in m
        pc_m = 3.0856775814913673e16
        self.kappa = m_sun * Gc2_sun_m / (rs_pc * pc_m)     # G m / (c^2 r_s)
        self.eps_m = m_sun / M_sun
        self.act = math.sqrt(self.eps_m * self.kappa)       # Kerr action -> units sqrt(G M r_s)
        # density units (GeV/cm^3) per unit of the dimensionless integral
        c = 299792458.0
        G = 6.67430e-11
        Msun = 1.98840987e30
        GeV_kg = 1.78266192e-27
        if kind == "constf":
            v = 1e5  # 100 km/s
            self.unit = 0.3 * c ** 3 / (2 * math.pi * v * v) ** 1.5    # GeV/cm^3 (f0 c^3)
        else:
            M = M_sun * Msun
            rs = rs_pc * pc_m
            vH = math.sqrt(G * M / rs)
            f_unit = M / (math.sqrt(2) * (2 * math.pi) ** 3 * vH ** 3 * rs ** 3)   # kg m^-3 (m/s)^-3
            self.unit = f_unit * c ** 3 / GeV_kg / 1e6                            # GeV/cm^3

    def f(self, E, C, Lz):
        if self.kind == "constf":
            return np.ones_like(E)
        a = self.a
        Q = C - Lz ** 2
        if self.variant == "L_sqrtC":          # test variant: L^2 = C instead of the polar action
            L = np.sqrt(C)
        else:
            Ith = I_theta(E, Q, Lz, a)
            L = np.abs(Lz) + Ith / (2 * np.pi)
        Ir = I_r_kerr(E, Q, Lz, a)
        d, unb = hern_delta(Ir * self.act, L * self.act)
        return np.where(unb, 0.0, ftilde_hern(d))

    def lz_edges(self, r, E):
        """Lz where Cmax(Lz) = Lz^2 (the quadratic in Lz), for each E."""
        a = self.a
        D = r * r + a * a - 2 * r
        # Cmax - Lz^2 = (r^4/D) V0(Lz) - Lz^2 = A2 Lz^2 + A1 Lz + A0
        A2 = a * a / D - 1
        A1 = -4 * a * E * r / D
        A0 = (r ** 4 / D) * ((1 + a * a / r ** 2 + 2 * a * a / r ** 3) * E ** 2 - D / r ** 2)
        disc = A1 ** 2 - 4 * A2 * A0
        sq = np.sqrt(np.maximum(disc, 0))
        l1 = (-A1 + sq) / (2 * A2)
        l2 = (-A1 - sq) / (2 * A2)
        return np.minimum(l1, l2), np.maximum(l1, l2), disc >= 0

    def valid_at_cmax(self, r, E, Lz):
        Cm = Cmax_eq(r, E, Lz, self.a)
        return valid_orbit(r, E, Cm - Lz ** 2, Lz, self.a) & (Cm >= Lz ** 2)

    def lz_interval(self, r, E, nscan=400):
        lo, hi, ok = self.lz_edges(r, np.array([E]))
        if not ok[0]:
            return None
        lo, hi = float(lo[0]), float(hi[0])
        Lg = np.linspace(lo, hi, nscan)
        v = self.valid_at_cmax(r, np.full(nscan, E), Lg)
        if not v.any():
            return None
        idx = np.where(v)[0]
        runs = np.split(idx, np.where(np.diff(idx) > 1)[0] + 1)
        out = []
        for run in runs:
            i0, i1 = run[0], run[-1]
            a_, b_ = Lg[i0], Lg[i1]
            # refine the edges by bisection where they are interior to [lo, hi]
            if i0 > 0:
                x0, x1 = Lg[i0 - 1], Lg[i0]
                for _ in range(40):
                    xm = 0.5 * (x0 + x1)
                    if self.valid_at_cmax(r, np.array([E]), np.array([xm]))[0]:
                        x1 = xm
                    else:
                        x0 = xm
                a_ = x1
            if i1 < nscan - 1:
                x0, x1 = Lg[i1], Lg[i1 + 1]
                for _ in range(40):
                    xm = 0.5 * (x0 + x1)
                    if self.valid_at_cmax(r, np.array([E]), np.array([xm]))[0]:
                        x0 = xm
                    else:
                        x1 = xm
                b_ = x0
            out.append((a_, b_))
        return out

    def emin(self, r):
        lo, hi = 0.5, 1.0 - 1e-12
        for _ in range(50):
            m = 0.5 * (lo + hi)
            if self.lz_interval(r, m, nscan=200):
                hi = m
            else:
                lo = m
        return hi

    def density(self, r):
        a = self.a
        D = r * r + a * a - 2 * r
        Emin = self.emin(r)
        xe, we = np.polynomial.legendre.leggauss(self.nE)
        # E nodes clustered toward Emin (the Hernquist DF weights deep orbits): E = Emin + (1-Emin) u^2
        u = 0.5 * (xe + 1)
        wu = 0.5 * we
        En = Emin + (1 - Emin) * u ** 2
        wE = (1 - Emin) * 2 * u * wu
        xl, wl = np.polynomial.legendre.leggauss(self.nL)
        xp, wp = np.polynomial.legendre.leggauss(self.npsi)
        nodes_E, nodes_L, nodes_w = [], [], []
        nruns_max = 0
        for E, w in zip(En, wE):
            iv = self.lz_interval(r, E)
            if not iv:
                continue
            nruns_max = max(nruns_max, len(iv))
            for (l0, l1) in iv:
                Ln = 0.5 * (l1 + l0) + 0.5 * (l1 - l0) * xl
                nodes_E.append(np.full(self.nL, E))
                nodes_L.append(Ln)
                nodes_w.append(w * 0.5 * (l1 - l0) * wl)
        E = np.concatenate(nodes_E)
        Lz = np.concatenate(nodes_L)
        W = np.concatenate(nodes_w)
        Cm = Cmax_eq(r, E, Lz, a)
        L2 = Lz ** 2
        # lowest non-captured C by bisection (valid at Cm by construction)
        v_lo = valid_orbit(r, E, np.zeros_like(E), Lz, a)
        c0, c1 = L2.copy(), Cm.copy()
        for _ in range(50):
            cm = 0.5 * (c0 + c1)
            v = valid_orbit(r, E, cm - L2, Lz, a)
            c1 = np.where(v, cm, c1)
            c0 = np.where(v, c0, cm)
        Clo = np.where(v_lo, L2, c1)
        cosp = np.clip(1 - 2 * (Clo - L2) / np.maximum(Cm - L2, 1e-300), -1, 1)
        plo = np.arccos(cosp)
        # psi nodes on [plo, pi]
        psi = 0.5 * (np.pi + plo)[:, None] + 0.5 * (np.pi - plo)[:, None] * xp
        wpsi = 0.5 * (np.pi - plo)[:, None] * wp
        C = L2[:, None] + (Cm - L2)[:, None] * (1 - np.cos(psi)) / 2
        EE = np.broadcast_to(E[:, None], C.shape)
        LL = np.broadcast_to(Lz[:, None], C.shape)
        fv = self.f(EE.ravel(), C.ravel(), LL.ravel()).reshape(C.shape)
        Jt = -(2 / math.sqrt(D)) * np.sum(W[:, None] * wpsi * EE * fv)
        Jp = (2 / math.sqrt(D)) * np.sum(W[:, None] * wpsi * LL * fv)
        self.last = (Jt, Jp)
        Om = Jp / Jt
        gtt = -(1 - 2 / r)
        gtp = -2 * a / r
        gpp = r * r + a * a + 2 * a * a / r
        rho = abs(Jt) * math.sqrt((gpp - 2 * gtp * Om + gtt * Om * Om) / D)
        return dict(r=r, rho=rho * self.unit, rho_dimless=rho, Emin=Emin, Omega=Om, nodes=int(C.size),
                    n_lz_runs_max=nruns_max)


# ------------------------------------------------------------------ digitiser
COL = {"blue": (0.203922, 0.541176, 0.741176), "purple": (0.478431, 0.407843, 0.650980),
       "red": (0.811765, 0.266667, 0.341176)}


def digitise(path):
    """paths of the three coloured curves of a pgf figure, mapped to data coordinates by the
    tick labels (x labels centred on the tick; y labels: baseline + offset of the
    gridline, measured on the grey gridlines)."""
    txt = open(path).read().splitlines()
    xt, yt = [], []
    for l in txt:
        m = re.search(r"\\pgftext\[x=([\d.]+)in,y=([\d.]+)in,([^\]]*)\].*displaystyle ([-\d.]+)\\\)\}%$", l)
        if m:
            x, y, anc, val = float(m.group(1)), float(m.group(2)), m.group(3), float(m.group(4))
            if "top" in anc:
                xt.append((x, val))
            elif "left,base" in anc:
                yt.append((y, val))
    paths, cur, col, grey_h = [], None, None, []
    for l in txt:
        m = re.search(r"definecolor\{currentstroke\}\{rgb\}\{([\d.]+),([\d.]+),([\d.]+)\}", l)
        if m:
            col = tuple(float(v) for v in m.groups())
        m = re.search(r"\\pgfpath(moveto|lineto)\{\\pgfqpoint\{([-\d.]+)in\}\{([-\d.]+)in\}\}", l)
        if m:
            if m.group(1) == "moveto":
                cur = [(float(m.group(2)), float(m.group(3)))]
            elif cur is not None:
                cur.append((float(m.group(2)), float(m.group(3))))
        if "pgfusepath{stroke}" in l and cur:
            paths.append((col, np.array(cur)))
            if col and abs(col[0] - 0.690196) < 1e-4 and len(cur) == 2 and abs(cur[0][1] - cur[1][1]) < 1e-6:
                grey_h.append(cur[0][1])
            cur = None
    xt = np.array(xt)
    yt = np.array(yt)
    px = np.polyfit(xt[:, 0], xt[:, 1], 1)
    # gridline offset: nearest grey horizontal line above each y label
    offs = []
    for y, _ in yt:
        g = [h - y for h in grey_h if 0 < h - y < 0.1]
        if g:
            offs.append(min(g))
    off = float(np.median(offs))
    py = np.polyfit(yt[:, 0] + off, yt[:, 1], 1)
    out = {}
    for name, c in COL.items():
        best = None
        for cc, p in paths:
            if cc and max(abs(cc[i] - c[i]) for i in range(3)) < 1e-4:
                if best is None or len(p) > len(best):
                    best = p
        if best is not None:
            out[name] = np.stack([np.polyval(px, best[:, 0]), np.polyval(py, best[:, 1])], axis=1)
    return out, dict(x_fit=px.tolist(), y_fit=py.tolist(), y_label_offset_in=off, n_grey_h=len(grey_h))


def peak_of(curve):
    i = int(np.argmax(curve[:, 1]))
    # parabola through the three points around the maximum
    if 0 < i < len(curve) - 1:
        x, y = curve[i - 1:i + 2, 0], curve[i - 1:i + 2, 1]
        p = np.polyfit(x, y, 2)
        if p[0] < 0:
            xv = -p[1] / (2 * p[0])
            return float(xv), float(np.polyval(p, xv))
    return float(curve[i, 0]), float(curve[i, 1])


# ------------------------------------------------------------------ main
def selfchecks():
    out = {}
    rng = np.random.default_rng(1)
    a = 0.8
    r, E, C, Lz = 7.3, 0.95, 18.0, 2.1
    Q = C - Lz ** 2
    co = quartic_coeffs(np.array(E), np.array(Q), np.array(Lz), a)
    Rv = np.polyval(co, r)
    out["V_paper_vs_R_over_r4"] = [float(V_paper(r, E, C, Lz, a)), float(Rv / r ** 4)]
    # a = 0 polar action = 2 pi (L - |Lz|)
    Eq = rng.uniform(0.9, 0.99, 5)
    Qq = rng.uniform(1, 30, 5)
    Lq = rng.uniform(-5, 5, 5)
    out["Itheta_a0_vs_2pi(L-|Lz|)"] = [I_theta(Eq, Qq, Lq, 0.0).tolist(),
                                       (2 * np.pi * (np.sqrt(Qq + Lq ** 2) - np.abs(Lq))).tolist()]
    # Kerr radial action at a = 0 and large r against the Kepler value 2 pi (1/sqrt(2 eps) - L)
    E0, L0 = 0.999, 10.0
    Ir = I_r_kerr(np.array([E0]), np.array([L0 ** 2]), np.array([0.0]), 0.0)[0]
    epsN = (1 - E0 ** 2) / 2
    out["Ir_a0_vs_kepler"] = [float(Ir), float(2 * np.pi * (1 / math.sqrt(2 * epsN) - L0))]
    # Hernquist radial action: small delta, against the linear-potential limit check by direct quadrature
    d = np.array([1e-5]); Lt = np.array([1e-8])
    I1 = hern_Ir(d, Lt)[0]
    x = np.linspace(1e-12, 3e-5, 2000001)
    p2 = 2 * d[0] - 2 * x / (1 + x) - Lt[0] ** 2 / x ** 2
    I2 = 2 * np.trapz(np.sqrt(np.maximum(p2, 0)), x)
    out["hern_Ir_vs_trapz"] = [float(I1), float(I2)]
    dd, _ = hern_delta(np.array([I1]), Lt)
    out["hern_delta_inverse"] = [float(dd[0]), 1e-5]
    return out


def zamo_constf(r, a, n=160):
    """independent check of the measure and of the projection for constant f: quadrature over
    the local momentum p in the frame of the zero-angular-momentum observer at the equator,
    N^(0) = int d^3p, N^(phi) = int p^phi/p^0 d^3p over the valid momenta, rho = |N|."""
    D = r * r + a * a - 2 * r
    A = (r * r + a * a) ** 2 - a * a * D
    al = math.sqrt(D * r * r / A)
    gpp = A / (r * r)
    om = 2 * a * r / A
    ps = np.linspace(0, 2, 200001)
    pmax = ps[(al * np.sqrt(1 + ps ** 2) - om * math.sqrt(gpp) * ps) < 1].max() * 1.001
    x, w = np.polynomial.legendre.leggauss(n)
    p = 0.5 * pmax * (x + 1)
    wp = 0.5 * pmax * w
    mu, wmu = x, w
    nb = 2 * n
    be = (np.arange(nb) + 0.5) * 2 * np.pi / nb
    wb = np.full(nb, 2 * np.pi / nb)
    N0 = Nphi = 0.0
    for i in range(n):
        P = p[i]
        g = math.sqrt(1 + P * P)
        pphi = P * mu[:, None] * np.ones(nb)[None, :]
        pt = P * np.sqrt(1 - mu[:, None] ** 2)
        pth = pt * np.sin(be)[None, :]
        Lz = math.sqrt(gpp) * pphi
        E = al * g + om * Lz
        Q = (r * pth) ** 2
        v = valid_orbit(r, E.ravel(), Q.ravel(), Lz.ravel(), a).reshape(E.shape)
        wt = wp[i] * P * P * wmu[:, None] * wb[None, :] * v
        N0 += np.sum(wt)
        Nphi += np.sum(wt * pphi / g)
    return math.sqrt(N0 ** 2 - Nphi ** 2)


FIGS = {"constf": ("fig_rho_a.pgf", 1e8), "hern": ("fig_rho_hern.pgf", 1e18)}


def run_case(args):
    kind, a, colname, src, quick = args
    import os as _os
    _os.environ["OMP_NUM_THREADS"] = "1"
    pgf = src + "/" + FIGS[kind][0]
    dig, meta = digitise(pgf)
    cur = dig[colname]
    unit = FIGS[kind][1]
    sp = Spike(a, kind)
    r_in = {0.0: 4.0, 0.5: 3.0, 0.8: 2.2}[a]
    rg = np.concatenate([np.linspace(r_in + 0.1, 12, 34), np.linspace(13, 38, 11)])
    if quick:
        rg = np.array([5.0, 7.0, 12.0])
    rows = [sp.density(float(r)) for r in rg]
    rr = np.array([x["rho"] for x in rows]) / unit
    xs = cur[:, 0]
    o = np.argsort(xs)
    inr = (rg >= xs.min()) & (rg <= xs.max())
    dig_at = np.interp(rg[inr], xs[o], cur[o, 1])
    rel = rr[inr] / dig_at - 1
    pk_me = peak_of(np.stack([rg, rr], axis=1))
    pk_fd = peak_of(cur[o])
    ipk = int(np.argmax(rr))
    sp2 = Spike(a, kind, nE=96, nL=96, npsi=32)
    dd2 = sp2.density(float(rg[ipk]))
    out = dict(r=rg.tolist(), rho=rr.tolist(), unit_GeV_cm3=unit, Emin=[x["Emin"] for x in rows],
               n_lz_runs_max=max(x["n_lz_runs_max"] for x in rows),
               dig_range=[float(xs.min()), float(xs.max())], dig_curve=cur[o].tolist(),
               rel_dev_at_nodes=rel.tolist(), r_nodes_in_range=rg[inr].tolist(),
               maxabs_rel_dev=float(np.max(np.abs(rel))),
               maxabs_rel_dev_r_ge_5=float(np.max(np.abs(rel[rg[inr] >= 5.0]))),
               median_rel_dev=float(np.median(rel)),
               peak_mine=pk_me, peak_fdrw_digitised=pk_fd, peak_ratio=pk_me[1] / pk_fd[1],
               peak_node_doubled=dict(r=float(rg[ipk]), rho=dd2["rho"] / unit, rho_base=float(rr[ipk]),
                                      rel=float(dd2["rho"] / unit / rr[ipk] - 1)),
               digitiser=meta)
    if kind == "hern" and a > 0:
        spv = Spike(a, kind, variant="L_sqrtC")
        out["peak_node_variant_L_sqrtC"] = spv.density(float(rg[ipk]))["rho"] / unit
    if kind == "constf":
        out["zamo_check"] = {str(rv): [zamo_constf(rv, a) * sp.unit / unit, sp.density(rv)["rho"] / unit]
                             for rv in (float(rg[ipk]), 12.0)}
    return ("%s_a%.1f" % (kind, a), out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    ap.add_argument("--src", default="/data/haiyangw/nrpic/kb-data/raw/arxiv/1707.06302/v2/src")
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--procs", type=int, default=4)
    args = ap.parse_args()
    out = args.out
    import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    res = {"selfchecks": selfchecks()}
    print(json.dumps(res["selfchecks"], indent=1), flush=True)
    sp = Spike(0.0, "constf", nE=32, nL=32, npsi=12)
    d = sp.density(2000.0)
    res["constf_a0_r2000_over_newton"] = d["rho_dimless"] / ((4 * np.pi / 3) * (2 / 2000.0) ** 1.5)
    res["zamo_vs_invariants_constf_a0.8_r300"] = [zamo_constf(300.0, 0.8), Spike(0.8, "constf").density(300.0)["rho_dimless"]]
    print("Newton-limit ratio", res["constf_a0_r2000_over_newton"], res["zamo_vs_invariants_constf_a0.8_r300"], flush=True)
    cases = [("hern", 0.8, "red"), ("hern", 0.0, "blue"), ("hern", 0.5, "purple"),
             ("constf", 0.5, "purple"), ("constf", 0.8, "red")]
    import multiprocessing as mp
    with mp.get_context("fork").Pool(args.procs) as pool:
        got = pool.map(run_case, [(k, a, c, args.src, args.quick) for k, a, c in cases])
    res["cases"] = dict(got)
    for key, c in res["cases"].items():
        print(key, json.dumps({k: v for k, v in c.items() if k not in ("r", "rho", "rel_dev_at_nodes", "r_nodes_in_range", "dig_curve", "Emin")}), flush=True)
        cur = np.array(c["dig_curve"])
        rg = np.array(c["r"])
        rr = np.array(c["rho"])
        fig, axs = plt.subplots(2, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 5.0), sharex=True,
                                gridspec_kw=dict(height_ratios=[2, 1]))
        fig.subplots_adjust(left=0.14, right=0.97, bottom=0.10, top=0.97, hspace=0.06)
        axs[0].plot(cur[:, 0], cur[:, 1], color=fs.PAL["blue"], label="FdRW figure (my digitiser)")
        axs[0].plot(rg, rr, "o", ms=3, color=fs.PAL["red"], label="my computation")
        axs[0].set_ylabel(r"$\rho$ [%g GeV cm$^{-3}$]" % c["unit_GeV_cm3"])
        axs[0].legend(loc="upper right", fontsize=8, title=key + ", equator")
        axs[1].plot(c["r_nodes_in_range"], c["rel_dev_at_nodes"], "o-", ms=3, color=fs.PAL["red"])
        axs[1].axhline(0, **fs.GUIDE)
        axs[1].set_ylim(-0.1, 0.1)
        axs[1].set_ylabel("mine / FdRW - 1")
        axs[1].set_xlabel(r"$r/Gm$")
        fs.save(fig, out + "/v3_%s" % key)
    with open(out + "/v3_results.json", "w") as f:
        json.dump(res, f, indent=1)


if __name__ == "__main__":
    main()
