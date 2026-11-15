"""Hybrid relativistic-Newtonian approximation (HRNA) for a binary passing a black hole.

Reference solution (ordinary differential equations) of track F-hills, package F-pre-2.
Model of Manzaneda, Navarrete & Tejeda, arXiv:2404.16270 (source
kb-data/raw/arxiv/2404.16270/v1/src/article.tex), equation (CoordtEqs), lines 246-256:

    xddot^i = -(g^{i lam} - g^{0 lam} xdot^i)
              * [ (1/(m Gamma^2)) d_lam Phi + (d_nu g_{mu lam} - 1/2 d_lam g_{mu nu}) xdot^mu xdot^nu ],
    Gamma   = (-g_{mu nu} xdot^mu xdot^nu)^(-1/2)                 (article.tex:258-261)

with xdot^0 = 1, the Newtonian pair potential Phi = -m1 m2/|x1 - x2| (Euclidean coordinate
distance, article.tex:236-241) and -(1/m) d_i Phi = a_i the usual Newtonian pair acceleration
(article.tex:263-267).  The black hole is fixed at the origin; no back-reaction.

Metrics (closed forms written here, independent of python/nrpic/kerr.py, which the tests use as
the reference):
  coords "sch": Schwarzschild in Cartesian form, x = r (sin th cos ph, sin th sin ph, cos th),
                g_00 = -(1 - 2M/r), g_ij = delta_ij + 2M/(r - 2M) n_i n_j.
  coords "cks": Cartesian Kerr-Schild, g = eta + 2 H l l, H = M r^3/(r^4 + a^2 z^2),
                l = (1, (r x + a y)/(r^2 + a^2), (r y - a x)/(r^2 + a^2), z/r).
law "newton": point mass M at the origin plus the same pair force (the paper's Newtonian runs).

Units G = c = M = 1 throughout (lengths in r_g, times in GM/c^3).
Integrator: embedded Runge-Kutta 8(5,3) of Dormand and Prince (DOP853), with the tableau taken
from scipy (scipy.integrate._ivp.dop853_coefficients) and the step-size control of scipy's DOP853.
"""
from __future__ import annotations

import math

import numba as nb
import numpy as np
from scipy.integrate._ivp import dop853_coefficients as _dc

LAW_NEWTON, LAW_HRNA = 0, 1
COORDS_SCH, COORDS_CKS = 0, 1
PAIR_GRAVITY, PAIR_HOOKE = 0, 1

_NS = _dc.N_STAGES                      # 12
_A = np.ascontiguousarray(_dc.A[:_NS, :_NS], dtype=np.float64)
_B = np.ascontiguousarray(_dc.B, dtype=np.float64)
_C = np.ascontiguousarray(_dc.C[:_NS], dtype=np.float64)
_E3 = np.ascontiguousarray(_dc.E3, dtype=np.float64)
_E5 = np.ascontiguousarray(_dc.E5, dtype=np.float64)


# ------------------------------------------------------------------------------------------
# metrics: fill g[4,4], gi[4,4], dg[3,4,4] (dg[k] = d g / d x^k) at the spatial point x
# ------------------------------------------------------------------------------------------
@nb.njit(cache=True)
def metric_sch(x, M, g, gi, dg):
    r = math.sqrt(x[0] * x[0] + x[1] * x[1] + x[2] * x[2])
    n0, n1, n2 = x[0] / r, x[1] / r, x[2] / r
    n = (n0, n1, n2)
    f = 1.0 - 2.0 * M / r
    h = 2.0 * M / (r - 2.0 * M)
    hp = -2.0 * M / ((r - 2.0 * M) * (r - 2.0 * M))
    for mu in range(4):
        for nu in range(4):
            g[mu, nu] = 0.0
            gi[mu, nu] = 0.0
            for k in range(3):
                dg[k, mu, nu] = 0.0
    g[0, 0] = -f
    gi[0, 0] = -1.0 / f
    for i in range(3):
        for j in range(3):
            d = 1.0 if i == j else 0.0
            g[i + 1, j + 1] = d + h * n[i] * n[j]
            gi[i + 1, j + 1] = d - 2.0 * M / r * n[i] * n[j]
    for k in range(3):
        dg[k, 0, 0] = -2.0 * M / (r * r) * n[k]
        for i in range(3):
            for j in range(3):
                dik = 1.0 if i == k else 0.0
                djk = 1.0 if j == k else 0.0
                dg[k, i + 1, j + 1] = hp * n[k] * n[i] * n[j] + h / r * (
                    dik * n[j] + djk * n[i] - 2.0 * n[i] * n[j] * n[k])


@nb.njit(cache=True)
def cks_r(x, a):
    R2 = x[0] * x[0] + x[1] * x[1] + x[2] * x[2]
    b = R2 - a * a
    return math.sqrt(0.5 * (b + math.sqrt(b * b + 4.0 * a * a * x[2] * x[2])))


@nb.njit(cache=True)
def metric_cks(x, M, a, g, gi, dg):
    X, Y, Z = x[0], x[1], x[2]
    r = cks_r(x, a)
    D = r ** 4 + a * a * Z * Z
    H = M * r ** 3 / D
    s = r * r + a * a
    l = np.empty(4)
    l[0] = 1.0
    l[1] = (r * X + a * Y) / s
    l[2] = (r * Y - a * X) / s
    l[3] = Z / r
    # gradient of r: r_k = r (r^2 x_k + a^2 z delta_kz) / (r^4 + a^2 z^2)
    rk = np.empty(3)
    rk[0] = r * (r * r * X) / D
    rk[1] = r * (r * r * Y) / D
    rk[2] = r * (r * r * Z + a * a * Z) / D
    dH = np.empty(3)
    dl = np.zeros((3, 4))
    for k in range(3):
        dzk = 1.0 if k == 2 else 0.0
        dH[k] = M * (3.0 * r * r * rk[k] * D - r ** 3 * (4.0 * r ** 3 * rk[k] + 2.0 * a * a * Z * dzk)) / (D * D)
        dxk = 1.0 if k == 0 else 0.0
        dyk = 1.0 if k == 1 else 0.0
        dl[k, 1] = ((rk[k] * X + r * dxk + a * dyk) * s - (r * X + a * Y) * 2.0 * r * rk[k]) / (s * s)
        dl[k, 2] = ((rk[k] * Y + r * dyk - a * dxk) * s - (r * Y - a * X) * 2.0 * r * rk[k]) / (s * s)
        dl[k, 3] = (dzk * r - Z * rk[k]) / (r * r)
    # contravariant l^mu = eta^{mu nu} l_nu
    lu0, lu1, lu2, lu3 = -l[0], l[1], l[2], l[3]
    lu = (lu0, lu1, lu2, lu3)
    for mu in range(4):
        for nu in range(4):
            eta = 0.0
            if mu == nu:
                eta = -1.0 if mu == 0 else 1.0
            g[mu, nu] = eta + 2.0 * H * l[mu] * l[nu]
            gi[mu, nu] = eta - 2.0 * H * lu[mu] * lu[nu]
            for k in range(3):
                dg[k, mu, nu] = 2.0 * dH[k] * l[mu] * l[nu] + 2.0 * H * (dl[k, mu] * l[nu] + l[mu] * dl[k, nu])


@nb.njit(cache=True)
def metric(coords, x, M, a, g, gi, dg):
    if coords == COORDS_SCH:
        metric_sch(x, M, g, gi, dg)
    else:
        metric_cks(x, M, a, g, gi, dg)


@nb.njit(cache=True)
def radius(coords, x, a):
    if coords == COORDS_CKS:
        return cks_r(x, a)
    return math.sqrt(x[0] * x[0] + x[1] * x[1] + x[2] * x[2])


# ------------------------------------------------------------------------------------------
# accelerations
# ------------------------------------------------------------------------------------------
@nb.njit(cache=True)
def accel_one(law, coords, M, a, x, v, Ap, out, g, gi, dg, xd, F):
    """Coordinate acceleration of one member: background plus pair acceleration Ap (3,)."""
    if law == LAW_NEWTON:
        r = math.sqrt(x[0] * x[0] + x[1] * x[1] + x[2] * x[2])
        c = -M / (r * r * r)
        for i in range(3):
            out[i] = c * x[i] + Ap[i]
        return
    metric(coords, x, M, a, g, gi, dg)
    xd[0] = 1.0
    xd[1], xd[2], xd[3] = v[0], v[1], v[2]
    s = 0.0
    for mu in range(4):
        for nu in range(4):
            s += g[mu, nu] * xd[mu] * xd[nu]
    inv_gam2 = -s                                    # 1/Gamma^2
    for lam in range(4):
        c = 0.0
        for mu in range(4):
            for j in range(3):
                c += dg[j, mu, lam] * xd[mu] * xd[j + 1]
        if lam >= 1:
            k = lam - 1
            for mu in range(4):
                for nu in range(4):
                    c -= 0.5 * dg[k, mu, nu] * xd[mu] * xd[nu]
            c -= Ap[k] * inv_gam2                   # (1/(m Gamma^2)) d_k Phi = -a_k / Gamma^2
        F[lam] = c
    for i in range(3):
        acc = 0.0
        for lam in range(4):
            acc -= (gi[i + 1, lam] - gi[0, lam] * v[i]) * F[lam]
        out[i] = acc


@nb.njit(cache=True)
def pair_accel(pair, m1, m2, kpair, l0, x1, x2, A1, A2):
    d0, d1, d2 = x1[0] - x2[0], x1[1] - x2[1], x1[2] - x2[2]
    r12 = math.sqrt(d0 * d0 + d1 * d1 + d2 * d2)
    if pair == PAIR_GRAVITY:
        c = 1.0 / (r12 * r12 * r12)
        c1, c2 = -m2 * c, m1 * c
    else:                                            # Hooke: Phi = k/2 (r12 - l0)^2, kpair = k/m
        c = kpair * (r12 - l0) / r12
        c1, c2 = -c, c
    A1[0], A1[1], A1[2] = c1 * d0, c1 * d1, c1 * d2
    A2[0], A2[1], A2[2] = c2 * d0, c2 * d1, c2 * d2


@nb.njit(cache=True)
def rhs(law, coords, pair, M, a, m1, m2, kpair, l0, alive, y, dy, wk):
    """y = (x1, v1, x2, v2) -> dy.  wk: work arrays tuple."""
    g, gi, dg, xd, F, A1, A2, o1, o2 = wk
    x1, v1, x2, v2 = y[0:3], y[3:6], y[6:9], y[9:12]
    if alive[0] and alive[1]:
        pair_accel(pair, m1, m2, kpair, l0, x1, x2, A1, A2)
    else:
        for i in range(3):
            A1[i] = 0.0
            A2[i] = 0.0
    if alive[0]:
        accel_one(law, coords, M, a, x1, v1, A1, o1, g, gi, dg, xd, F)
        for i in range(3):
            dy[i] = v1[i]
            dy[3 + i] = o1[i]
    else:
        for i in range(6):
            dy[i] = 0.0
    if alive[1]:
        accel_one(law, coords, M, a, x2, v2, A2, o2, g, gi, dg, xd, F)
        for i in range(3):
            dy[6 + i] = v2[i]
            dy[9 + i] = o2[i]
    else:
        for i in range(6):
            dy[6 + i] = 0.0


def _work():
    return (np.zeros((4, 4)), np.zeros((4, 4)), np.zeros((3, 4, 4)), np.zeros(4), np.zeros(4),
            np.zeros(3), np.zeros(3), np.zeros(3), np.zeros(3))


# ------------------------------------------------------------------------------------------
# conserved quantities of one member (test-particle values)
# ------------------------------------------------------------------------------------------
@nb.njit(cache=True)
def energy_lz(law, coords, M, a, x, v, g, gi, dg):
    """Return (E, Lz, Gamma): E = -u_t (relativistic) or 1 + v^2/2 - M/r (Newton), Lz = u_phi."""
    if law == LAW_NEWTON:
        r = math.sqrt(x[0] * x[0] + x[1] * x[1] + x[2] * x[2])
        e = 0.5 * (v[0] * v[0] + v[1] * v[1] + v[2] * v[2]) - M / r
        return 1.0 + e, x[0] * v[1] - x[1] * v[0], 1.0
    metric(coords, x, M, a, g, gi, dg)
    xd = np.empty(4)
    xd[0] = 1.0
    xd[1], xd[2], xd[3] = v[0], v[1], v[2]
    s = 0.0
    for mu in range(4):
        for nu in range(4):
            s += g[mu, nu] * xd[mu] * xd[nu]
    gam = 1.0 / math.sqrt(-s)
    ut, ux, uy = 0.0, 0.0, 0.0
    for nu in range(4):
        ut += g[0, nu] * xd[nu]
        ux += g[1, nu] * xd[nu]
        uy += g[2, nu] * xd[nu]
    return -gam * ut, gam * (x[0] * uy - x[1] * ux), gam


# ------------------------------------------------------------------------------------------
# DOP853 integration of one encounter with on-the-fly diagnostics
# ------------------------------------------------------------------------------------------
@nb.njit(cache=True)
def integrate(law, coords, pair, M, a, m1, m2, kpair, l0, y0, h0, rtol, atol,
              r_stop, r_apo_min, r_plunge, t_max, max_steps, a0, rec_cap,
              A, B, C, E3, E5, wk, h_max=1e300):
    """Integrate from t = 0.  Stops when (i) the CM radius exceeds r_stop while receding, or (ii)
    after the CM pericentre the CM turns around at a radius > r_apo_min (bound CM), or (iii)
    t > t_max or max_steps.  Members crossing r < r_plunge inwards are marked dead (captured).

    Returns (status, t_end, y_end, diag, rec_t, rec_y, nrec, nsteps, nrej) with
    diag = [t_peri, r_peri, a_min, alpha_max, t_s, rcm_ts, plunged1, plunged2, alpha_all]
    (alpha_max: a/R while the instantaneous Newtonian E_b < 0; alpha_all: at any time)
    status 0 r_stop, 1 bound-CM apocentre, 2 t_max, 3 max_steps, 4 step underflow.
    """
    n = 12
    mb = m1 + m2
    y = y0.copy()
    K = np.zeros((_NS + 1, n))
    ynew = np.empty(n)
    dy = np.empty(n)
    ytmp = np.empty(n)
    alive = np.ones(2, dtype=np.bool_)
    rhs(law, coords, pair, M, a, m1, m2, kpair, l0, alive, y, dy, wk)
    K[0, :] = dy
    t = 0.0
    h = h0
    rec_t = np.empty(rec_cap)
    rec_y = np.empty((rec_cap, n))
    nrec = 0
    if rec_cap > 0:
        rec_t[0] = t
        rec_y[0, :] = y
        nrec = 1

    def cm_r_rdot(yy):
        xc0 = (m1 * yy[0] + m2 * yy[6]) / mb
        xc1 = (m1 * yy[1] + m2 * yy[7]) / mb
        xc2 = (m1 * yy[2] + m2 * yy[8]) / mb
        vc0 = (m1 * yy[3] + m2 * yy[9]) / mb
        vc1 = (m1 * yy[4] + m2 * yy[10]) / mb
        vc2 = (m1 * yy[5] + m2 * yy[11]) / mb
        rc = math.sqrt(xc0 * xc0 + xc1 * xc1 + xc2 * xc2)
        return rc, (xc0 * vc0 + xc1 * vc1 + xc2 * vc2) / rc

    def sep(yy):
        d0, d1, d2 = yy[0] - yy[6], yy[1] - yy[7], yy[2] - yy[8]
        return math.sqrt(d0 * d0 + d1 * d1 + d2 * d2)

    def ebin(yy):
        d0, d1, d2 = yy[0] - yy[6], yy[1] - yy[7], yy[2] - yy[8]
        w0, w1, w2 = yy[3] - yy[9], yy[4] - yy[10], yy[5] - yy[11]
        return 0.5 * (w0 * w0 + w1 * w1 + w2 * w2) - mb / math.sqrt(d0 * d0 + d1 * d1 + d2 * d2)

    rc_old, rd_old = cm_r_rdot(y)
    s_old = sep(y)
    t_peri = -1.0
    r_peri = 1e300
    a_min = s_old
    alpha_max = 0.0
    t_s = math.nan
    rcm_ts = math.nan
    plunged = np.zeros(2)
    eb_min = 0.0
    passed_peri = False
    status = 3
    nsteps = 0
    nrej = 0
    rejected = False
    exponent = -1.0 / 8.0
    while nsteps < max_steps:
        if t > t_max:
            status = 2
            break
        if h > h_max:
            h = h_max
        # one DOP853 step attempt
        for s_ in range(1, _NS):
            for i in range(n):
                acc = 0.0
                for j in range(s_):
                    acc += A[s_, j] * K[j, i]
                ytmp[i] = y[i] + h * acc
            rhs(law, coords, pair, M, a, m1, m2, kpair, l0, alive, ytmp, dy, wk)
            K[s_, :] = dy
        for i in range(n):
            acc = 0.0
            for j in range(_NS):
                acc += B[j] * K[j, i]
            ynew[i] = y[i] + h * acc
        rhs(law, coords, pair, M, a, m1, m2, kpair, l0, alive, ynew, dy, wk)
        K[_NS, :] = dy
        # error estimate (scipy DOP853), scale per 3-vector block
        e5 = 0.0
        e3 = 0.0
        for blk in range(4):
            nm = 0.0
            nn = 0.0
            for i in range(3):
                nm += y[3 * blk + i] ** 2
                nn += ynew[3 * blk + i] ** 2
            sc = atol + rtol * math.sqrt(max(nm, nn))
            for i in range(3):
                idx = 3 * blk + i
                a5 = 0.0
                a3 = 0.0
                for j in range(_NS + 1):
                    a5 += E5[j] * K[j, idx]
                    a3 += E3[j] * K[j, idx]
                e5 += (a5 / sc) ** 2
                e3 += (a3 / sc) ** 2
        if e5 == 0.0 and e3 == 0.0:
            err = 0.0
        else:
            denom = e5 + 0.01 * e3
            err = abs(h) * e5 / math.sqrt(denom * n)
        if err < 1.0:
            if err == 0.0:
                fac = 10.0
            else:
                fac = min(10.0, 0.9 * err ** exponent)
            if rejected:
                fac = min(1.0, fac)
            rejected = False
            t_new = t + h
            # ---- diagnostics on the accepted step ----
            rc_new, rd_new = cm_r_rdot(ynew)
            s_new = sep(ynew)
            if s_new < a_min:
                a_min = s_new
            if (not passed_peri) and rd_old < 0.0 and rd_new >= 0.0:
                w = rd_old / (rd_old - rd_new)
                t_peri = t + w * h
                r_peri = rc_old + w * (rc_new - rc_old)
                passed_peri = True
            eb = ebin(ynew)
            if alive[0] and alive[1]:
                al = s_new / rc_new ** 1.5 * math.sqrt(M)
                if al > eb_min:
                    eb_min = al                       # alpha without the bound condition
                if eb < 0.0 and al > alpha_max:
                    alpha_max = al
            if s_old < 2.0 * a0 and s_new >= 2.0 * a0:
                w = (2.0 * a0 - s_old) / (s_new - s_old)
                t_s = t + w * h
                rcm_ts = rc_old + w * (rc_new - rc_old)
            # plunge check
            for k in range(2):
                if alive[k]:
                    xx = ynew[6 * k:6 * k + 3]
                    vv = ynew[6 * k + 3:6 * k + 6]
                    rk_ = radius(coords, xx, a)
                    if rk_ < r_plunge and (xx[0] * vv[0] + xx[1] * vv[1] + xx[2] * vv[2]) < 0.0:
                        alive[k] = False
                        plunged[k] = t_new
            y[:] = ynew
            t = t_new
            nsteps += 1
            rhs(law, coords, pair, M, a, m1, m2, kpair, l0, alive, y, dy, wk)
            K[0, :] = dy                               # FSAL value (recomputed if a member died)
            if rec_cap > 0 and nrec < rec_cap:
                rec_t[nrec] = t
                rec_y[nrec, :] = y
                nrec += 1
            if passed_peri and rc_new > r_stop and rd_new > 0.0:
                status = 0
                rc_old, rd_old, s_old = rc_new, rd_new, s_new
                break
            if passed_peri and rd_old > 0.0 and rd_new <= 0.0 and rc_new > r_apo_min:
                status = 1
                rc_old, rd_old, s_old = rc_new, rd_new, s_new
                break
            if (not alive[0]) and (not alive[1]):
                status = 5
                break
            if alive[0] != alive[1]:
                # one member captured: follow the other one alone (same stopping radii)
                ka = 0 if alive[0] else 1
                x0_, x1_, x2_ = ynew[6 * ka], ynew[6 * ka + 1], ynew[6 * ka + 2]
                ra = math.sqrt(x0_ * x0_ + x1_ * x1_ + x2_ * x2_)
                rda = (x0_ * ynew[6 * ka + 3] + x1_ * ynew[6 * ka + 4] + x2_ * ynew[6 * ka + 5]) / ra
                if ra > r_stop and rda > 0.0:
                    status = 0
                    rc_old, rd_old, s_old = rc_new, rd_new, s_new
                    break
                if rda <= 0.0 and ra > r_apo_min and passed_peri:
                    status = 1
                    rc_old, rd_old, s_old = rc_new, rd_new, s_new
                    break
            rc_old, rd_old, s_old = rc_new, rd_new, s_new
            h = h * fac
        else:
            nrej += 1
            rejected = True
            h = h * max(0.2, 0.9 * err ** exponent)
            if abs(h) < 1e-12:
                status = 4
                break
    diag = np.empty(9)
    diag[0] = t_peri
    diag[1] = r_peri
    diag[2] = a_min
    diag[3] = alpha_max
    diag[4] = t_s
    diag[5] = rcm_ts
    diag[6] = plunged[0]
    diag[7] = plunged[1]
    diag[8] = eb_min
    return status, t, y, diag, rec_t[:nrec], rec_y[:nrec], nrec, nsteps, nrej


# ------------------------------------------------------------------------------------------
# initial data (article.tex appendix AB, appendix.tex:138-179)
# ------------------------------------------------------------------------------------------
def kerr_equatorial_L(rp, spin, M=1.0, E=1.0):
    """Lz of the equatorial Kerr geodesic with energy E and radial turning point rp (BL r):
    R(rp) = [E (r^2 + a^2) - a L]^2 - Delta [r^2 + (L - a E)^2] = 0, root with L > 0
    (orbit co-rotating with the coordinate phi; spin > 0 means prograde with respect to the hole)."""
    from scipy.optimize import brentq
    a = spin * M
    D = rp * rp - 2 * M * rp + a * a

    def R(L):
        return (E * (rp * rp + a * a) - a * L) ** 2 - D * (rp * rp + (L - a * E) ** 2)

    # R(0) > 0 for rp outside the capture radius; R decreases to -inf for large L
    Lhi = 1.0
    while R(Lhi) > 0:
        Lhi *= 2
    return brentq(R, 0.0, Lhi, xtol=1e-15, rtol=1e-15)


def cm_initial(law, coords, spin, rp, r0, M=1.0):
    """Position and coordinate velocity of a test particle on the parabolic(-like) orbit with
    pericentre rp, released at radius r0 moving inwards, angular momentum along +z."""
    if law == "newton":
        L = math.sqrt(2 * M * rp)                                   # appendix.tex:167
        return (np.array([r0, 0.0, 0.0]),
                np.array([-math.sqrt(2 * M / r0 - L * L / r0 ** 2), L / r0, 0.0]))
    if coords == "sch":
        if spin != 0.0:
            raise ValueError("coords='sch' is Schwarzschild only")
        L = math.sqrt(2 * M * rp * rp / (rp - 2 * M))               # appendix.tex:175
        f0 = 1 - 2 * M / r0
        return (np.array([r0, 0.0, 0.0]),                           # appendix.tex:177-178
                np.array([-f0 * math.sqrt(2 * M / r0 - L * L / r0 ** 2 * f0), f0 * L / r0, 0.0]))
    # Cartesian Kerr-Schild: build the BL state and convert with python/nrpic/kerr.py
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "python"))
    from nrpic import kerr
    a = spin * M
    L = kerr_equatorial_L(rp, spin, M)
    D = r0 * r0 - 2 * M * r0 + a * a
    R0 = ((r0 * r0 + a * a) - a * L) ** 2 - D * (r0 * r0 + (L - a) ** 2)
    u_r = -math.sqrt(R0) / D
    xbl = np.array([r0, math.pi / 2, 0.0])
    ubl = np.array([u_r, 0.0, L])
    tc, xc, uc = kerr.convert_state(0.0, xbl, ubl, "bl", "cks", a, M)
    m = kerr.adm("cks", xc, a, M)
    U = m.gamma_inv @ uc
    W = math.sqrt(1 + uc @ U)
    v = m.alpha / W * U - m.beta
    return np.asarray(xc, float), np.asarray(v, float)


def initial_state(law="hrna", coords="sch", spin=0.0, mb=1e-6, q12=1.0, a0=1.013, beta=None,
                  rp=None, phase=0.0, sense=1, r0_rt=50.0, M=1.0, ic_gamma=False):
    """Members on a circular Newtonian binary around the CM (appendix.tex:143-159), CM on the
    parabolic(-like) orbit of the chosen law.  Member 1 sits at +(m2/mb) a0 e(phase).
    ic_gamma=True (not the paper's convention): the internal angular velocity is divided by the
    CM's Gamma = dt/dtau at release, so that the binary is circular in the CM proper time to
    leading order under HRNA (test of the r0 dependence, JOURNAL C2)."""
    rt = (M / mb) ** (1 / 3) * a0
    if rp is None:
        rp = rt / beta
    r0 = r0_rt * rt
    xc, vc = cm_initial(law, coords, spin, rp, r0, M)
    m1 = mb / (1 + q12)
    m2 = mb * q12 / (1 + q12)
    w = sense * math.sqrt(mb / a0 ** 3)
    if ic_gamma and law != "newton":
        g, gi, dg = np.zeros((4, 4)), np.zeros((4, 4)), np.zeros((3, 4, 4))
        cc = COORDS_CKS if coords == "cks" else COORDS_SCH
        _, _, gam = energy_lz(LAW_HRNA, cc, M, spin * M, xc, vc, g, gi, dg)
        w = w / gam
    e = np.array([math.cos(phase), math.sin(phase), 0.0])
    et = np.array([-math.sin(phase), math.cos(phase), 0.0])
    x1 = xc + (m2 / mb) * a0 * e
    x2 = xc - (m1 / mb) * a0 * e
    v1 = vc + (m2 / mb) * a0 * w * et
    v2 = vc - (m1 / mb) * a0 * w * et
    return np.concatenate([x1, v1, x2, v2]), dict(rt=rt, rp=rp, r0=r0, m1=m1, m2=m2)


# ------------------------------------------------------------------------------------------
# driver (interface shared with tracks/F-hills/newton3, see README.md)
# ------------------------------------------------------------------------------------------
_WK = None


def run_encounter(law="hrna", coords="sch", spin=0.0, mb=1e-6, q12=1.0, a0=1.013, beta=None,
                  rp=None, phase=0.0, sense=1, r0_rt=50.0, rf_rt=150.0, rtol=1e-12, atol=1e-14,
                  record=0, r_plunge=None, max_steps=20_000_000, t_max=None, M=1.0,
                  m1=None, m2=None, a=None, D=None, theta=None, varphi=None, e_b=0.0, e_orb=1.0,
                  ic_gamma=False):
    """Run one encounter and return the outcome dictionary of README.md (plus the trajectory
    if record > 0: up to `record` accepted steps).

    Aliases with the names of tracks/F-hills/newton3 (HillsSetup): m1, m2 (instead of mb, q12),
    a (= a0), D = rp/r_t (= 1/beta), varphi = +pi/2 (prograde) or -pi/2 (retrograde) with
    theta = pi/2 (coplanar only).  `phase` here is the binary phase at release (2404
    convention), not newton3's effective phase at pericentre."""
    global _WK
    if _WK is None:
        _WK = _work()
    if e_b != 0.0 or e_orb != 1.0:
        raise NotImplementedError("circular binary on a parabolic(-like) orbit only")
    if m1 is not None or m2 is not None:
        mb = m1 + m2
        q12 = m2 / m1
    if a is not None:
        a0 = a
    if D is not None:
        beta = 1.0 / D
    if theta is not None or varphi is not None:
        if abs((theta if theta is not None else math.pi / 2) - math.pi / 2) > 1e-12:
            raise NotImplementedError("coplanar encounters only")
        sense = 1 if (varphi if varphi is not None else math.pi / 2) > 0 else -1
    y0, info = initial_state(law, coords, spin, mb, q12, a0, beta, rp, phase, sense, r0_rt, M,
                             ic_gamma)
    lawc = LAW_NEWTON if law == "newton" else LAW_HRNA
    cc = COORDS_CKS if coords == "cks" else COORDS_SCH
    a = spin * M
    rt = info["rt"]
    if r_plunge is None:
        if lawc == LAW_NEWTON:
            r_plunge = 0.0
        elif cc == COORDS_SCH:
            r_plunge = 2.5 * M
        else:
            r_plunge = M + math.sqrt(M * M - a * a) + 0.05 * M
    T0 = 2 * math.pi * math.sqrt(a0 ** 3 / mb)
    if t_max is None:                       # four parabolic in- and out-fall times
        t_max = 4.0 * (math.sqrt(2.0) / 3.0) * (info["r0"] ** 1.5 + (rf_rt * rt) ** 1.5) + 10 * T0
    status, t, y, diag, rec_t, rec_y, nrec, nsteps, nrej = integrate(
        lawc, cc, PAIR_GRAVITY, M, a, info["m1"], info["m2"], 0.0, 0.0, y0, T0 / 200.0, rtol,
        atol, rf_rt * rt, 10.0 * rt, r_plunge, t_max, max_steps, a0, int(record),
        _A, _B, _C, _E3, _E5, _WK)
    out = summarize(lawc, cc, M, a, info["m1"], info["m2"], a0, y, diag, T0)
    out.update(status=int(status), t_end=float(t), nsteps=int(nsteps), nrej=int(nrej),
               rt=rt, rp=info["rp"], r0=info["r0"], T0=T0)
    if record:
        out["rec_t"] = np.array(rec_t)
        out["rec_y"] = np.array(rec_y)
    return out


def summarize(lawc, cc, M, a, m1, m2, a0, y, diag, T0):
    g, gi, dg = np.zeros((4, 4)), np.zeros((4, 4)), np.zeros((3, 4, 4))
    mb = m1 + m2
    x1, v1, x2, v2 = y[0:3], y[3:6], y[6:9], y[9:12]
    def safe_el(x, v):
        # the flat-space CM of a pair with a captured member can sit where the metric is
        # singular or the averaged velocity is not timelike: no test-particle energy there
        try:
            E, L, _ = energy_lz(lawc, cc, M, a, x, v, g, gi, dg)
            return E, L
        except (ZeroDivisionError, ValueError):
            return math.nan, math.nan

    E1, L1 = safe_el(x1, v1)
    E2, L2 = safe_el(x2, v2)
    xc = (m1 * x1 + m2 * x2) / mb
    vc = (m1 * v1 + m2 * v2) / mb
    Ec, Lc = safe_el(xc, vc)
    d = x1 - x2
    w = v1 - v2
    r12 = float(np.linalg.norm(d))
    Eb = 0.5 * float(w @ w) - mb / r12                          # article.tex:365
    Lb = float(np.linalg.norm(np.cross(d, w)))                 # article.tex:366
    arg = 1 + 2 * Eb * Lb ** 2 / mb ** 2                      # article.tex:367
    eb = math.sqrt(arg) if arg > 0 else 0.0
    eps1, eps2 = E1 - 1.0, E2 - 1.0
    plunged = 1 if diag[6] > 0 else (2 if diag[7] > 0 else 0)
    if diag[6] > 0 and diag[7] > 0:
        plunged = 3
    em = max(eps1 if diag[6] == 0 else -1e300, eps2 if diag[7] == 0 else -1e300)
    t_peri = float(diag[0])
    # outcome code of tracks/F-hills/newton3 (threebody.py): 0 survived, 1 m1 bound / m2 free,
    # 2 m2 bound / m1 free, 3 both bound, 4 both free; 6 (here only) a member was captured
    if plunged:
        outcome = 6
    elif Eb < 0:
        outcome = 0
    elif eps1 < 0 <= eps2:
        outcome = 1
    elif eps2 < 0 <= eps1:
        outcome = 2
    elif eps1 < 0 and eps2 < 0:
        outcome = 3
    else:
        outcome = 4
    E_unit = m1 * m2 / a0 * (M / mb) ** (1 / 3)              # newton3 energy unit
    return dict(
        outcome=outcome, E1_u=m1 * eps1 / E_unit, E2_u=m2 * eps2 / E_unit,
        separated=bool(Eb > 0 or plunged > 0), Eb_end=Eb, eb_end=eb,
        ab_end=(-mb / (2 * Eb) if Eb < 0 else math.inf),
        eps1=eps1, eps2=eps2, L1=L1, L2=L2, eps_cm=Ec - 1.0, L_cm=Lc,
        vinf=(math.sqrt(2 * em) if em > 0 else 0.0),
        vinf_exact=(math.sqrt(1 - 1 / (1 + em) ** 2) if em > 0 else 0.0),
        t_peri=t_peri, r_peri=float(diag[1]),
        t_s=(float(diag[4]) - t_peri) / T0 if not math.isnan(diag[4]) else math.nan,
        rcm_ts=float(diag[5]), a_min=float(diag[2]) / a0, alpha_max=float(diag[3]),
        alpha_all=float(diag[8]),
        plunged=plunged, r12_end=r12)
