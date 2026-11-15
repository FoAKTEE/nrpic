#!/usr/bin/env python3
"""Independent integrators for the second check of F-hills G0 (wave 2).

Written from the equations of the sources, without importing the track's drivers
(geodesic_binary/hrna.py, newton3/hills3):

  newton_fixed  two members, hole of mass M fixed at the origin, Newtonian forces.
  newton_full   three free bodies (M, m1, m2), Newtonian forces, barycentric frame.
  hrna          the hybrid relativistic-Newtonian approximation of arXiv:2404.16270
                (article.tex l. 245-267, Eq. CoordtEqs): each member moves under the exact
                Schwarzschild coordinate-time acceleration in Schwarzschild coordinates (written
                here in Cartesian form x = r n) plus the Newtonian pair acceleration a_p
                raised with g^ij and divided by Gamma^2:
                  a = -(M/r^2) [f + 2 v^2 - rdot^2 (2 + 1/f)] n + (2 M rdot / (r^2 f)) v
                      + (1/Gamma^2) [a_p - (2M/r) (n.a_p) n],
                  1/Gamma^2 = f - v^2 - 2 M rdot^2 / (r f),   f = 1 - 2M/r.
                The geodesic part follows from the radial and azimuthal equations
                  r'' = -f M/r^2 + 3 M r'^2/(r^2 f) + r f Omega^2,
                  d(r^2 phi')/dt = (2 M r'/(r^2 f)) r^2 phi'
                (Christoffel symbols of Schwarzschild); self-test SC0 checks it through the
                conservation of E = f Gamma and L = Gamma |x x v| with the pair force off.

Initial data (2404 appendix.tex l. 143-179): CM at (r0, 0, 0) on the parabolic(-like) orbit
of pericentre r_p of the law (Newton: L = sqrt(2 M r_p); Schwarzschild: L = sqrt(2 M r_p^2 /
(r_p - 2M)) with the coordinate velocities of l. 177-178); members on a circular Newtonian
binary of separation a0 and phase phi at release, prograde = same sense as the CM orbit.
Option gamma_ic: the binary's angular velocity divided by Gamma of the CM (circular in the
CM proper time to leading order). newton_full: the relative orbit of the binary's CM about M
is the Newtonian parabola with mu = M + m_b and pericentre r_p, barycentric frame.
"""
import math

import numpy as np
from scipy.integrate import solve_ivp

R_PLUNGE = 2.5          # a member crossing r < 2.5 M inwards is captured (as in V6/V7)


# ----------------------------------------------------------------------------------------
# accelerations
# ----------------------------------------------------------------------------------------
def sch_terms(x, y, z, vx, vy, vz, M):
    r = math.sqrt(x * x + y * y + z * z)
    nx, ny, nz = x / r, y / r, z / r
    f = 1.0 - 2.0 * M / r
    rd = nx * vx + ny * vy + nz * vz
    v2 = vx * vx + vy * vy + vz * vz
    cn = -(M / (r * r)) * (f + 2.0 * v2 - rd * rd * (2.0 + 1.0 / f))
    cv = 2.0 * M * rd / (r * r * f)
    ig2 = f - v2 - 2.0 * M * rd * rd / (r * f)
    return r, nx, ny, nz, cn, cv, ig2


def rhs_two(t, s, law, M, m1, m2, alive1, alive2):
    """s = (x1, v1, x2, v2); law 'hrna' or 'newton' (hole fixed)."""
    x1, y1, z1, u1, w1, q1, x2, y2, z2, u2, w2, q2 = s
    if alive1 and alive2:
        dx, dy, dz = x1 - x2, y1 - y2, z1 - z2
        d3 = (dx * dx + dy * dy + dz * dz) ** 1.5
        a1 = (-m2 * dx / d3, -m2 * dy / d3, -m2 * dz / d3)
        a2 = (m1 * dx / d3, m1 * dy / d3, m1 * dz / d3)
    else:
        a1 = a2 = (0.0, 0.0, 0.0)
    out = [0.0] * 12
    cm_fac = None
    if law == "hrna_sym" and alive1 and alive2:
        mb = m1 + m2
        xc = ((m1 * x1 + m2 * x2) / mb, (m1 * y1 + m2 * y2) / mb, (m1 * z1 + m2 * z2) / mb)
        vc = ((m1 * u1 + m2 * u2) / mb, (m1 * w1 + m2 * w2) / mb, (m1 * q1 + m2 * q2) / mb)
        rc, ncx, ncy, ncz, _, _, _ = sch_terms(*xc, *vc, M)
        # one factor for both members: the geometric mean of their own 1/Gamma^2 (equal to
        # 1/Gamma_cm^2 up to second order in the internal velocities; it vanishes when either
        # member approaches the speed of light, like 2404's member-wise factor), so that
        # sum_i m_i a_pair,i = 0 holds exactly
        g1 = sch_terms(x1, y1, z1, u1, w1, q1, M)[6]
        g2 = sch_terms(x2, y2, z2, u2, w2, q2, M)[6]
        cm_fac = (math.sqrt(max(0.0, g1) * max(0.0, g2)), 2.0 * M / rc, (ncx, ncy, ncz))
    for k, (alive, X, V, ap) in enumerate((
            (alive1, (x1, y1, z1), (u1, w1, q1), a1),
            (alive2, (x2, y2, z2), (u2, w2, q2), a2))):
        if not alive:
            continue
        o = 6 * k
        out[o:o + 3] = V
        if law == "newton":
            r3 = (X[0] * X[0] + X[1] * X[1] + X[2] * X[2]) ** 1.5
            for i in range(3):
                out[o + 3 + i] = -M * X[i] / r3 + ap[i]
        elif law == "hrna_sym" and alive1 and alive2:
            # diagnostic variant (not 2404): the factor (1/Gamma^2) g^ij of the pair force is
            # evaluated at the binary's CM for both members, so that m1 a_p1 + m2 a_p2 = 0
            r, nx, ny, nz, cn, cv, _ = sch_terms(*X, *V, M)
            n = (nx, ny, nz)
            for i in range(3):
                out[o + 3 + i] = cn * n[i] + cv * V[i] + cm_fac[0] * (
                    ap[i] - cm_fac[1] * (cm_fac[2][0] * ap[0] + cm_fac[2][1] * ap[1]
                                         + cm_fac[2][2] * ap[2]) * cm_fac[2][i])
        else:
            r, nx, ny, nz, cn, cv, ig2 = sch_terms(*X, *V, M)
            n = (nx, ny, nz)
            apn = nx * ap[0] + ny * ap[1] + nz * ap[2]
            for i in range(3):
                out[o + 3 + i] = cn * n[i] + cv * V[i] + ig2 * (ap[i] - 2.0 * M / r * apn * n[i])
    return out


def rhs_full(t, s, masses):
    """Three free bodies, s = (x_0, x_1, x_2, v_0, v_1, v_2), body 0 = the hole."""
    X = s[:9]
    out = list(s[9:]) + [0.0] * 9
    for i in range(3):
        for j in range(i + 1, 3):
            dx = X[3 * j] - X[3 * i]
            dy = X[3 * j + 1] - X[3 * i + 1]
            dz = X[3 * j + 2] - X[3 * i + 2]
            d3 = (dx * dx + dy * dy + dz * dz) ** 1.5
            out[9 + 3 * i] += masses[j] * dx / d3
            out[9 + 3 * i + 1] += masses[j] * dy / d3
            out[9 + 3 * i + 2] += masses[j] * dz / d3
            out[9 + 3 * j] -= masses[i] * dx / d3
            out[9 + 3 * j + 1] -= masses[i] * dy / d3
            out[9 + 3 * j + 2] -= masses[i] * dz / d3
    return out


# ----------------------------------------------------------------------------------------
# test-particle invariants and the Schwarzschild capture criterion
# ----------------------------------------------------------------------------------------
def invariants(law, x, v, M=1.0):
    """(E, Lz, rdot): E = f Gamma, Lz = Gamma (x x v)_z for hrna; 1 + v^2/2 - M/r and (x x v)_z
    for Newton."""
    x = np.asarray(x, float)
    v = np.asarray(v, float)
    r = float(np.linalg.norm(x))
    rd = float(x @ v) / r
    lz = float(x[0] * v[1] - x[1] * v[0])
    if law in ("hrna", "hrna_sym"):
        _, _, _, _, _, _, ig2 = sch_terms(*x, *v, M)
        if ig2 <= 0:
            return math.nan, math.nan, rd
        gam = 1.0 / math.sqrt(ig2)
        return (1.0 - 2.0 * M / r) * gam, gam * lz, rd
    return 1.0 + 0.5 * float(v @ v) - M / r, lz, rd


def barrier_E2(L, M=1.0):
    """Maximum of V^2 = (1 - 2M/r)(1 + L^2/r^2) over r (the barrier), or None if L^2 < 12 M^2."""
    L2 = L * L
    if L2 <= 12.0 * M * M:
        return None
    r = (L2 - math.sqrt(L2 * L2 - 12.0 * M * M * L2)) / (2.0 * M)
    return (1.0 - 2.0 * M / r) * (1.0 + L2 / (r * r))


def gr_captured(E, L, rdot, M=1.0):
    """Would a Schwarzschild test particle with (E, L) be captured? Bound particles (E < 1)
    return to pericentre; unbound ones only if moving inwards. Captured when there is no
    barrier or E^2 exceeds it."""
    if not np.isfinite(E) or not np.isfinite(L):
        return False
    if E >= 1.0 and rdot > 0.0:
        return False
    b = barrier_E2(abs(L), M)
    return True if b is None else E * E > b


# ----------------------------------------------------------------------------------------
# initial data
# ----------------------------------------------------------------------------------------
def cm_state(law, rp, r0, mu=1.0):
    if law == "hrna":
        L = math.sqrt(2.0 * mu * rp * rp / (rp - 2.0 * mu))
        f0 = 1.0 - 2.0 * mu / r0
        return (np.array([r0, 0.0, 0.0]),
                np.array([-f0 * math.sqrt(2.0 * mu / r0 - L * L / r0 ** 2 * f0), f0 * L / r0, 0.0]))
    L = math.sqrt(2.0 * mu * rp)
    return (np.array([r0, 0.0, 0.0]),
            np.array([-math.sqrt(2.0 * mu / r0 - L * L / r0 ** 2), L / r0, 0.0]))


def gamma_of(x, v, M=1.0):
    _, _, _, _, _, _, ig2 = sch_terms(*x, *v, M)
    return 1.0 / math.sqrt(ig2)


def initial_state(model, M, m1, m2, a0, rp, phase, r0, sense=1, gamma_ic=False):
    mb = m1 + m2
    law = "hrna" if model in ("hrna", "hrna_sym") else "newton"
    mu = M + mb if model == "newton_full" else M
    xc, vc = cm_state(law, rp, r0, mu)
    w = sense * math.sqrt(mb / a0 ** 3)
    if gamma_ic and law == "hrna":
        w /= gamma_of(xc, vc, M)
    e = np.array([math.cos(phase), math.sin(phase), 0.0])
    et = np.array([-math.sin(phase), math.cos(phase), 0.0])
    x1 = xc + (m2 / mb) * a0 * e
    x2 = xc - (m1 / mb) * a0 * e
    v1 = vc + (m2 / mb) * a0 * w * et
    v2 = vc - (m1 / mb) * a0 * w * et
    if model != "newton_full":
        return np.concatenate([x1, v1, x2, v2])
    # barycentric: hole at -(mb/Mt) R, binary CM at +(M/Mt) R, with R, V the relative state
    Mt = M + mb
    xh, vh = -(mb / Mt) * xc, -(mb / Mt) * vc
    sh = (M / Mt) * xc - xc          # shift that puts the binary CM at (M/Mt) R
    svh = (M / Mt) * vc - vc
    return np.concatenate([xh, x1 + sh, x2 + sh, vh, v1 + svh, v2 + svh])


# ----------------------------------------------------------------------------------------
# one encounter
# ----------------------------------------------------------------------------------------
def _members_rel(model, s):
    """Positions and velocities of the members relative to the hole."""
    if model == "newton_full":
        xh, vh = s[0:3], s[9:12]
        return (s[3:6] - xh, s[12:15] - vh, s[6:9] - xh, s[15:18] - vh)
    return s[0:3], s[3:6], s[6:9], s[9:12]


def run(model, rp, phase, M=1.0, m1=0.05, m2=0.05, a0=3.0, r0_rt=4.0, rstop_rt=30.0,
        gamma_ic=False, y0=None, rtol=1e-11, atol=1e-13, t_max=None, record_dt=None,
        seg=10.0):
    """Integrate one encounter; returns a dict of outcome and diagnostics.

    model: 'newton_fixed', 'newton_full', 'hrna'. y0 overrides the initial data (same layout
    as initial_state). record_dt: sample the members' states every record_dt (relative to
    the hole) for figures."""
    mb = m1 + m2
    rt = a0 * (M / mb) ** (1.0 / 3.0)
    r0 = r0_rt * rt
    rstop = rstop_rt * rt
    if y0 is None:
        y0 = initial_state(model, M, m1, m2, a0, rp, phase, r0, gamma_ic=gamma_ic)
    s = np.array(y0, float)
    law = {"hrna": "hrna", "hrna_sym": "hrna_sym"}.get(model, "newton")
    rel = law != "newton"
    lawE = "hrna" if rel else "newton"
    if t_max is None:
        t_max = 4.0 * (math.sqrt(2.0) / 3.0) * (r0 ** 1.5 + rstop ** 1.5) + 2000.0
    alive = [True, True]
    plunge_t = [math.nan, math.nan]
    plunge_inv = [None, None]
    plunge_ratio = [math.nan, math.nan]
    peri = [[], []]
    rec_t, rec = [], []
    t = 0.0
    nfev = 0
    status = "tmax"
    rmin = [math.inf, math.inf]

    def ev_plunge(k):
        def ev(tt, ss, *args):
            return math.sqrt(ss[6 * k] ** 2 + ss[6 * k + 1] ** 2 + ss[6 * k + 2] ** 2) - R_PLUNGE
        ev.terminal = True
        ev.direction = -1
        return ev

    def ev_peri(k):
        def ev(tt, ss, *args):
            if model == "newton_full":
                o = 3 + 3 * k
                d = ss[o:o + 3] - ss[0:3]
                w = ss[9 + o:9 + o + 3] - ss[9:12]
            else:
                d = ss[6 * k:6 * k + 3]
                w = ss[6 * k + 3:6 * k + 6]
            return float(d[0] * w[0] + d[1] * w[1] + d[2] * w[2])
        ev.terminal = False
        ev.direction = 1
        return ev

    def cm_inv(ss):
        x1_, v1_, x2_, v2_ = _members_rel(model, ss)
        return invariants(lawE, (m1 * x1_ + m2 * x2_) / mb, (m1 * v1_ + m2 * v2_) / mb, M)

    cm0 = cm_inv(s)
    cm2 = [None]

    def ev_cm2(tt, ss, *args):
        x1_, _, x2_, _ = _members_rel(model, ss)
        return float(np.linalg.norm((m1 * x1_ + m2 * x2_) / mb)) - 2.0 * rt
    ev_cm2.terminal = False
    ev_cm2.direction = -1

    def ev_cm(tt, ss, *args):
        x1_, v1_, x2_, v2_ = _members_rel(model, ss)
        return float((m1 * x1_ + m2 * x2_) @ (m1 * v1_ + m2 * v2_))
    ev_cm.terminal = False
    ev_cm.direction = 1
    cm_peri = []

    def never(tt, ss, *a):
        return 1.0

    def ev_lum(k):
        # 1/Gamma^2 of member k reaching zero: the member moves faster than light (a point-mass
        # near-collision under the Newtonian pair force); the run is stopped and flagged
        def ev(tt, ss, *args):
            return sch_terms(*ss[6 * k:6 * k + 6], M)[6] - 1e-6
        ev.terminal = True
        ev.direction = -1
        return ev

    def ev_sep(tt, ss, *args):
        x1_, v1_, x2_, v2_ = _members_rel(model, ss)
        return float((x1_ - x2_) @ (v1_ - v2_))
    ev_sep.terminal = False
    ev_sep.direction = 1
    sep_min = [math.inf]

    while t < t_max:
        t1 = min(t + seg, t_max)
        cm_ev = ev_cm if (alive[0] and alive[1]) else never
        if model == "newton_full":
            fun, args = rhs_full, (np.array([M, m1, m2]),)
            events = [ev_peri(0), ev_peri(1), cm_ev]
        else:
            fun, args = rhs_two, (law, M, m1, m2, alive[0], alive[1])
            events = [ev_peri(0), ev_peri(1), cm_ev]
            if rel:
                events += [ev_plunge(k) if alive[k] else never for k in (0, 1)]
                events += [ev_lum(k) if alive[k] else never for k in (0, 1)]
        events.append(ev_cm2 if (alive[0] and alive[1] and cm2[0] is None) else never)
        events.append(ev_sep if (alive[0] and alive[1]) else never)
        sol = solve_ivp(fun, (t, t1), s, method="DOP853", rtol=rtol, atol=atol, args=args,
                        events=events, dense_output=bool(record_dt))
        nfev += sol.nfev
        if sol.status < 0:
            status = "fail:" + sol.message
            break
        for k in (0, 1):
            for tp, yp in zip(sol.t_events[k], sol.y_events[k]):
                xr = _members_rel(model, yp)[2 * k]
                peri[k].append((float(tp), float(np.linalg.norm(xr))))
        if cm2[0] is None and len(sol.y_events[-2]):
            cm2[0] = cm_inv(sol.y_events[-2][0])
        for yp in sol.y_events[-1]:
            x1_, _, x2_, _ = _members_rel(model, yp)
            sep_min[0] = min(sep_min[0], float(np.linalg.norm(x1_ - x2_)))
        for tp, yp in zip(sol.t_events[2], sol.y_events[2]):
            x1_, _, x2_, _ = _members_rel(model, yp)
            cm_peri.append((float(tp), float(np.linalg.norm((m1 * x1_ + m2 * x2_) / mb))))
        if record_dt:
            k0 = math.ceil(t / record_dt - 1e-9)
            k1 = math.floor(float(sol.t[-1]) / record_dt + 1e-9)
            for kk in range(k0, k1 + 1):
                tt = kk * record_dt
                if rec_t and tt <= rec_t[-1] + 1e-9:
                    continue
                rec_t.append(tt)
                rec.append(np.concatenate(_members_rel(model, sol.sol(tt))))
        s = sol.y[:, -1].copy()
        t = float(sol.t[-1])
        if alive[0] and alive[1]:
            x1_, _, x2_, _ = _members_rel(model, s)
            sep_min[0] = min(sep_min[0], float(np.linalg.norm(x1_ - x2_)))
        if sol.status == 1 and rel and any(len(sol.t_events[5 + k]) for k in (0, 1)):
            status = "superluminal"
            break
        if sol.status == 1:      # a plunge event
            for k in (0, 1):
                if rel and alive[k] and len(sol.t_events[3 + k]):
                    alive[k] = False
                    plunge_t[k] = t
                    xk, vk = s[6 * k:6 * k + 3], s[6 * k + 3:6 * k + 6]
                    plunge_inv[k] = invariants("hrna", xk, vk, M)
                    if alive[1 - k]:
                        o = 6 * (1 - k)
                        d = float(np.linalg.norm(xk - s[o:o + 3]))
                        r = float(np.linalg.norm(xk))
                        plunge_ratio[k] = (m1 + m2 - (m1 if k == 0 else m2)) / d ** 2 / (M / r ** 2)
            if not (alive[0] or alive[1]):
                status = "both_plunged"
                break
            continue
        # stopping tests
        x1, v1, x2, v2 = _members_rel(model, s)
        if alive[0] and alive[1]:
            xc = (m1 * x1 + m2 * x2) / mb
            vc = (m1 * v1 + m2 * v2) / mb
            rc = float(np.linalg.norm(xc))
            if rc > rstop and float(xc @ vc) > 0:
                status = "cm_out"
                break
        settled = True
        for k, (xk, vk) in enumerate(((x1, v1), (x2, v2))):
            if not alive[k]:
                continue
            r = float(np.linalg.norm(xk))
            E, L, rd = invariants(lawE, xk, vk, M)
            if alive[1 - k]:
                xo = x2 if k == 0 else x1
                d = float(np.linalg.norm(xk - xo))
                ratio = (m2 if k == 0 else m1) / d ** 2 / (M / r ** 2)
            else:
                ratio = 0.0
            out_free = r > rstop and rd > 0 and E >= 1.0
            bound_quiet = E < 1.0 and ratio < 1e-3 and len(peri[k]) >= 1
            if not (out_free or bound_quiet):
                settled = False
        if settled:
            status = "settled"
            break
    # final classification
    x1, v1, x2, v2 = _members_rel(model, s)
    inv = []
    for k, (xk, vk) in enumerate(((x1, v1), (x2, v2))):
        inv.append(plunge_inv[k] if not alive[k] else invariants(lawE, xk, vk, M))
    for k in (0, 1):
        if peri[k]:
            rmin[k] = min(p[1] for p in peri[k])
        if not alive[k]:
            rmin[k] = min(rmin[k], R_PLUNGE)
    plunged = [not alive[0], not alive[1]]
    if alive[0] and alive[1]:
        d = x1 - x2
        w = v1 - v2
        Eb = 0.5 * float(w @ w) - mb / float(np.linalg.norm(d))
    else:
        Eb = math.nan
    eps = [inv[0][0] - 1.0, inv[1][0] - 1.0]
    if any(plunged):
        outcome = 6
    elif Eb < 0:
        outcome = 0
    elif eps[0] < 0 <= eps[1]:
        outcome = 1
    elif eps[1] < 0 <= eps[0]:
        outcome = 2
    elif eps[0] < 0 and eps[1] < 0:
        outcome = 3
    else:
        outcome = 4
    E_unit = m1 * m2 / a0 * (M / mb) ** (1.0 / 3.0)
    gr_cap = [bool(gr_captured(inv[k][0], inv[k][1], inv[k][2], M)) if alive[k] else True
              for k in (0, 1)]
    res = dict(model=model, rp=rp, phase=phase, gamma_ic=gamma_ic, r0_rt=r0_rt, status=status,
               t_end=t, nfev=nfev, outcome=outcome, separated=bool(any(plunged) or Eb > 0),
               plunged=plunged, plunge_t=plunge_t, plunge_ratio=plunge_ratio,
               E=[inv[0][0], inv[1][0]], L=[inv[0][1], inv[1][1]], rdot=[inv[0][2], inv[1][2]],
               E_u=[m1 * eps[0] / E_unit, m2 * eps[1] / E_unit], Eb=Eb,
               rmin=rmin, cm_peri=(cm_peri[0] if cm_peri else None),
               sep_min=sep_min[0] / a0,
               cm_EL_release=[cm0[0], cm0[1]],
               cm_EL_2rt=(None if cm2[0] is None else [cm2[0][0], cm2[0][1]]),
               first_peri=[peri[0][0] if peri[0] else None,
                                      peri[1][0] if peri[1] else None],
               gr_capture_criterion=gr_cap)
    if record_dt:
        res["rec_t"] = np.array(rec_t)
        res["rec"] = np.array(rec)
    return res
