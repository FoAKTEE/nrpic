"""verify_g0 K10, K11, K13: Newtonian three-body problem and the HRNA of arXiv:2404.16270, own code.

Coplanar (z = 0) throughout. Units G = c = M = 1.

Newton: three point masses (M, m1, m2), barycentric.
HRNA: each member on the Schwarzschild spacetime of a hole fixed at the origin, written in
Cartesian form (x^i = r n^i with the Schwarzschild r), plus the Newtonian pair force with the
Euclidean coordinate distance, Eq. (CoordtEqs) of 2404.16270 (article.tex:246-261). For this
metric the equation reduces to (derivation in ../README.md)
    xdd = (2/(f r^2)) v_r v - c f n + (1/Gamma^2) [a_N - (2/r)(n.a_N) n],
    c = h' v_r^2/2 + h (v^2 - v_r^2)/r + 1/r^2,  f = 1 - 2/r,  h = 2/(r - 2),
    Gamma^-2 = f - v^2 - h v_r^2.
A member that crosses r = 2.5 inwards is frozen and the pair force switched off (the rule
of the track's model, geodesic_binary/README.md "Stopping rule").

Modes:
  passages: from the start states of the two input files (K10, K11)
  scan:     phase scans at given (q, a_b, r_p): Newton from 10 r_t to 4 r_t, then full
            Newton, HRNA from the same state relative to M ("handoff"), and HRNA with the
            centre of mass put on the Schwarzschild parabola (E = 1) of pericentre r_p
            ("grmatched") (K13)
"""
import argparse
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vint  # noqa: E402

WT = "/data/haiyangw/nrpic/wt/F-hills"
TR = os.path.join(WT, "tracks/F-hills")
INPUTS = {"q10": os.path.join(TR, "three_punctures/inputs/hills_q10_m8.athinput"),
          "q4": os.path.join(TR, "nr_first/inputs/p1_q4.athinput")}
NOMINAL_AB = {"q10": 3.0, "q4": 5.0}
R_PLUNGE = 2.5


# ------------------------------------------------------------------ Newton
def make_newton_rhs(masses):
    m = np.asarray(masses, float)          # (3,) or (N, 3)

    def rhs(t, y, idx):
        mm = m if m.ndim == 1 else m[idx]
        x = y[:, :6].reshape(-1, 3, 2)
        v = y[:, 6:]
        acc = np.zeros_like(x)
        for i in range(3):
            for j in range(i + 1, 3):
                d = x[:, j] - x[:, i]
                r3 = np.sum(d * d, axis=1) ** 1.5
                mj = mm[j] if mm.ndim == 1 else mm[:, j]
                mi = mm[i] if mm.ndim == 1 else mm[:, i]
                acc[:, i] += (mj / r3)[:, None] * d
                acc[:, j] -= (mi / r3)[:, None] * d
        return np.concatenate([v, acc.reshape(-1, 6)], axis=1)
    return rhs


# ------------------------------------------------------------------ HRNA
def hrna_accel(x, v, aN):
    r = np.sqrt(np.sum(x * x, axis=1))
    n = x / r[:, None]
    vr = np.sum(n * v, axis=1)
    v2 = np.sum(v * v, axis=1)
    f = 1 - 2 / r
    h = 2 / (r - 2)
    hp = -2 / (r - 2) ** 2
    c = 0.5 * hp * vr ** 2 + h * (v2 - vr ** 2) / r + 1 / r ** 2
    ig2 = f - v2 - h * vr ** 2
    na = np.sum(n * aN, axis=1)
    return ((2 / (f * r * r)) * vr)[:, None] * v - (c * f)[:, None] * n + \
        ig2[:, None] * (aN - ((2 / r) * na)[:, None] * n)


def make_hrna_rhs(m1, m2, alive):
    """alive: (N, 2) boolean array, changed by the callback when a member plunges."""
    def rhs(t, y, idx):
        x1, x2 = y[:, 0:2], y[:, 2:4]
        v1, v2 = y[:, 4:6], y[:, 6:8]
        al = alive[idx]
        both = (al[:, 0] & al[:, 1]).astype(float)
        d = x2 - x1
        r3 = np.sum(d * d, axis=1) ** 1.5
        a1N = (both * m2 / r3)[:, None] * d
        a2N = -(both * m1 / r3)[:, None] * d
        acc1 = hrna_accel(x1, v1, a1N) * al[:, 0:1]
        acc2 = hrna_accel(x2, v2, a2N) * al[:, 1:2]
        return np.concatenate([v1 * al[:, 0:1], v2 * al[:, 1:2], acc1, acc2], axis=1)
    return rhs


def hrna_energy(x, v):
    """E = -u_t (per unit mass) and L = u_phi."""
    r = np.sqrt(np.sum(x * x, axis=-1))
    vr = np.sum(x * v, axis=-1) / r
    v2 = np.sum(v * v, axis=-1)
    f = 1 - 2 / r
    G = 1 / np.sqrt(f - v2 - (2 / (r - 2)) * vr ** 2)
    L = G * (x[..., 0] * v[..., 1] - x[..., 1] * v[..., 0])
    return f * G, L


# ------------------------------------------------------------------ helpers
def parse_input(path):
    vals = {}
    sect = None
    for line in open(path):
        s = line.split("#")[0].strip()
        if s.startswith("<"):
            sect = s.strip("<>")
        elif "=" in s and sect == "problem":
            k, v = [t.strip() for t in s.split("=", 1)]
            vals[k] = v
    bodies = []
    for c in range(int(vals["ncomp"])):
        g = lambda k: float(vals[f"comp{c}_{k}"])  # noqa: E731
        bodies.append((g("mass"), np.array([g("x1"), g("x2")]), np.array([g("p1"), g("p2")]) / g("mass")))
    m1, m2, M = bodies
    return M, m1, m2


def jacobi_energies(xM, x1, x2, vM, v1, v2, M, m1, m2):
    """Energies of the hierarchy (captured member c against M, ejected e against the
    barycentre of M and c); c is the member with the lower two-body energy with M."""
    def two(xa, va, ma):
        mu = M * ma / (M + ma)
        d = xa - xM
        return mu * np.sum((va - vM) ** 2, -1) / 2 - M * ma / np.sqrt(np.sum(d * d, -1))
    E1M, E2M = two(x1, v1, m1), two(x2, v2, m2)
    out = {}
    for c, e, mc, me, xc, vc, xe, ve in ((1, 2, m1, m2, x1, v1, x2, v2), (2, 1, m2, m1, x2, v2, x1, v1)):
        X = (M * xM + mc * xc) / (M + mc)
        V = (M * vM + mc * vc) / (M + mc)
        mu_out = me * (M + mc) / (M + mc + me)
        R = np.sqrt(np.sum((xe - X) ** 2, -1))
        Eout = mu_out * np.sum((ve - V) ** 2, -1) / 2 - (M + mc) * me / R
        mu_in = M * mc / (M + mc)
        Ein = mu_in * np.sum((vc - vM) ** 2, -1) / 2 - M * mc / np.sqrt(np.sum((xc - xM) ** 2, -1))
        out[c] = (Ein, Eout)
    return E1M, E2M, out


def osc(xrel, vrel, mu):
    r = np.linalg.norm(xrel)
    eps = 0.5 * vrel @ vrel - mu / r
    hz = xrel[0] * vrel[1] - xrel[1] * vrel[0]
    a = -mu / (2 * eps)
    e = np.sqrt(max(0.0, 1 + 2 * eps * hz * hz / mu ** 2))
    return a, e, a * (1 - e)


# ------------------------------------------------------------------ passages (K10, K11)
def passages(out, rtol):
    res = {}
    curves = {}
    for key, path in INPUTS.items():
        (M, xM, vM), (m1, x1, v1), (m2, x2, v2) = parse_input(path)
        q = M / (m1 + m2)
        unit = m1 * m2 / NOMINAL_AB[key] * q ** (1 / 3)
        T = 1500.0
        ts = np.arange(0, T + 1e-9, 0.25)
        y0 = np.concatenate([xM, x1, x2, vM, v1, v2])[None, :]
        rhs = make_newton_rhs([M, m1, m2])
        # dense sampling: integrate segment by segment (vint has no dense output)
        Y = [y0[0].copy()]
        y = y0.copy()
        t0 = 0.0
        for t1 in ts[1:]:
            _, y, _, _ = vint.integrate(rhs, y, t0, t1, rtol=rtol, atol=rtol * 1e-3, h0=1e-3)
            Y.append(y[0].copy())
            t0 = t1
        Y = np.array(Y)
        XM, X1, X2 = Y[:, 0:2], Y[:, 2:4], Y[:, 4:6]
        VM, V1, V2 = Y[:, 6:8], Y[:, 8:10], Y[:, 10:12]
        E1M, E2M, jac = jacobi_energies(XM, X1, X2, VM, V1, V2, M, m1, m2)
        cap = 1 if E1M[-1] < E2M[-1] else 2
        ej = 3 - cap
        Ein, Eout = jac[cap]
        d1 = np.linalg.norm(X1 - XM, axis=1)
        d2 = np.linalg.norm(X2 - XM, axis=1)
        dcap = d1 if cap == 1 else d2
        # first pericentre of the captured member
        imin = [i for i in range(1, len(ts) - 1) if dcap[i] < dcap[i - 1] and dcap[i] <= dcap[i + 1]]
        late = ts >= 300
        EejM = (E1M if ej == 1 else E2M)
        xc, vc = (X1, V1) if cap == 1 else (X2, V2)
        a_, e_, rp_ = osc(xc[-1] - XM[-1], vc[-1] - VM[-1], M + (m1 if cap == 1 else m2))
        Etot0 = None
        it280 = int(round(280 / 0.25))
        nw = dict(ejected=ej, captured=cap, unit=unit,
                  E_ej_bary_u=float(Eout[-1] / unit), E_ej_bary_spread_late_u=float(np.ptp(Eout[late]) / unit),
                  E_ej_M_late_min_u=float(EejM[late].min() / unit), E_ej_M_late_max_u=float(EejM[late].max() / unit),
                  E_ej_M_from200_min_u=float(EejM[ts >= 200].min() / unit),
                  E_ej_M_from200_max_u=float(EejM[ts >= 200].max() / unit),
                  E_cap_u=float(Ein[-1] / unit), first_pericentre=(float(ts[imin[0]]), float(dcap[imin[0]])),
                  rmin_cap=float(dcap.min()), rmin_ej=float((d1 if ej == 1 else d2).min()),
                  captured_orbit_t1500=dict(a=a_, e=e_, rp=rp_),
                  hole_displacement_t280=float(np.linalg.norm(XM[it280] - XM[0])),
                  hole_displacement_end=float(np.linalg.norm(XM[-1] - XM[0])))
        # Newton with the hole fixed at the origin, members relative to M
        def rhs_fixed(t, y, idx):
            p1, p2, w1, w2 = y[:, 0:2], y[:, 2:4], y[:, 4:6], y[:, 6:8]
            d = p2 - p1
            r3 = np.sum(d * d, 1) ** 1.5
            a1 = -p1 / (np.sum(p1 * p1, 1) ** 1.5)[:, None] + (m2 / r3)[:, None] * d
            a2 = -p2 / (np.sum(p2 * p2, 1) ** 1.5)[:, None] - (m1 / r3)[:, None] * d
            return np.concatenate([w1, w2, a1, a2], 1)
        yf = np.concatenate([x1 - xM, x2 - xM, v1 - vM, v2 - vM])[None, :]
        Yf = [yf[0].copy()]
        t0 = 0.0
        tf = np.arange(0, 600 + 1e-9, 0.25)
        for t1 in tf[1:]:
            _, yf, _, _ = vint.integrate(rhs_fixed, yf, t0, t1, rtol=rtol, atol=rtol * 1e-3, h0=1e-3)
            Yf.append(yf[0].copy())
            t0 = t1
        Yf = np.array(Yf)
        Ef = [m * (0.5 * np.sum(Yf[-1, 4 + 2 * i:6 + 2 * i] ** 2) - 1 / np.linalg.norm(Yf[-1, 2 * i:2 * i + 2]))
              for i, m in enumerate((m1, m2))]
        rminf = [np.linalg.norm(Yf[:, 2 * i:2 * i + 2], axis=1).min() for i in range(2)]
        nf = dict(E1_u=float(Ef[0] / unit), E2_u=float(Ef[1] / unit), rmin_1=float(rminf[0]), rmin_2=float(rminf[1]))
        # HRNA from the same state relative to M
        alive = np.ones((1, 2), bool)
        hr_rhs = make_hrna_rhs(m1, m2, alive)
        yh = np.concatenate([x1 - xM, x2 - xM, v1 - vM, v2 - vM])[None, :]
        th = np.arange(0, 1500 + 1e-9, 0.25)
        Yh = [yh[0].copy()]
        plunge_t = [None, None]
        t0 = 0.0
        for t1 in th[1:]:
            def cb(to, yo, tn, yn, idx):
                ynew = yn.copy()
                for i in range(2):
                    ro = np.linalg.norm(yo[:, 2 * i:2 * i + 2], axis=1)
                    rn = np.linalg.norm(yn[:, 2 * i:2 * i + 2], axis=1)
                    hit = alive[idx, i] & (rn < R_PLUNGE) & (ro >= R_PLUNGE)
                    if hit.any():
                        w = (ro - R_PLUNGE) / (ro - rn)
                        plunge_t[i] = float((to + w * (tn - to))[0])
                        alive[idx[hit], i] = False
                        ynew[hit, 4 + 2 * i:6 + 2 * i] = 0.0
                return np.zeros(len(idx), bool), ynew
            _, yh, _, _ = vint.integrate(hr_rhs, yh, t0, t1, rtol=rtol, atol=rtol * 1e-3, h0=1e-3, callback=cb)
            Yh.append(yh[0].copy())
            t0 = t1
        Yh = np.array(Yh)
        Eh, Lh = [], []
        for i in range(2):
            E_, L_ = hrna_energy(Yh[:, 2 * i:2 * i + 2], Yh[:, 4 + 2 * i:6 + 2 * i])
            Eh.append(E_)
            Lh.append(L_)
        rh = [np.linalg.norm(Yh[:, 2 * i:2 * i + 2], axis=1) for i in range(2)]
        hr = dict(plunge_t=plunge_t, alive_end=alive[0].tolist())
        for i, m in enumerate((m1, m2)):
            hr[f"E{i + 1}_u_end"] = float(m * (Eh[i][-1] - 1) / unit) if alive[0, i] else None
            hr[f"E{i + 1}_u_t600"] = float(m * (Eh[i][2400] - 1) / unit)
            hr[f"rmin_{i + 1}"] = float(rh[i].min())
            hr[f"E{i + 1}_specific_t0"] = float(Eh[i][0])
            hr[f"L{i + 1}_t0"] = float(Lh[i][0])
            mins = [j for j in range(1, len(th) - 1) if rh[i][j] < rh[i][j - 1] and rh[i][j] <= rh[i][j + 1]]
            hr[f"first_pericentre_{i + 1}"] = (float(th[mins[0]]), float(rh[i][mins[0]])) if mins else None
        res[key] = dict(newton=nw, newton_fixed=nf, hrna=hr)
        curves[key] = dict(t=ts, d1=d1, d2=d2, EejM=EejM / unit, Eout=Eout / unit, xM=XM,
                           th=th, rh1=rh[0], rh2=rh[1], tf=tf,
                           rf1=np.linalg.norm(Yf[:, 0:2], axis=1), rf2=np.linalg.norm(Yf[:, 2:4], axis=1))
        print(key, json.dumps(res[key], default=float), flush=True)
    json.dump(res, open(os.path.join(out, "passages.json"), "w"), indent=1, default=float)
    np.savez_compressed(os.path.join(out, "passage_curves.npz"),
                        **{f"{k}_{n}": v for k, c in curves.items() for n, v in c.items()})
    return res


# ------------------------------------------------------------------ scans (K13)
def start_states(M, m1, m2, ab, rp, phases, k0, mu_conv="total"):
    """mu_conv: 'total' puts the CM on the two-body parabola of M + m_b with pericentre rp
    (the convention of the passage inputs); 'M' gives it the test-mass parabola speed of M
    alone (a hypothesis about the track's V7 scan, tested in entry 4)."""
    mb = m1 + m2
    mu = M + mb
    mu_v = mu if mu_conv == "total" else M
    rt = ab * (M / mb) ** (1 / 3)
    r0 = k0 * rt
    f0 = -np.arccos(2 * rp / r0 - 1)
    p = 2 * rp
    Rx = r0 * np.array([np.cos(f0), np.sin(f0)])
    Rv = np.sqrt(mu_v / p) * np.array([-np.sin(f0), 1 + np.cos(f0)])
    u = np.tan(abs(f0) / 2)
    t_to_peri = np.sqrt(2 * rp ** 3 / mu) * (u + u ** 3 / 3)
    n = len(phases)
    y = np.zeros((n, 12))
    xM, vM = -mb / mu * Rx, -mb / mu * Rv
    xc, vc = M / mu * Rx, M / mu * Rv
    w = np.sqrt(mb / ab)
    rel = ab * np.stack([np.cos(phases), np.sin(phases)], 1)
    vrel = w * np.stack([-np.sin(phases), np.cos(phases)], 1)
    y[:, 0:2], y[:, 6:8] = xM, vM
    y[:, 2:4] = xc + m2 / mb * rel
    y[:, 4:6] = xc - m1 / mb * rel
    y[:, 8:10] = vc + m2 / mb * vrel
    y[:, 10:12] = vc - m1 / mb * vrel
    return y, rt, t_to_peri


def scan(q, ab, rp, nphase, rtol, t_after, mu_conv="total", with_u=False, max_steps=None):
    M, m1, m2 = 1.0, 0.5 / q, 0.5 / q
    mb = m1 + m2
    phases = (np.arange(nphase) + 0.5) * np.pi / nphase
    y, rt, t_to_peri = start_states(M, m1, m2, ab, rp, phases, 10.0, mu_conv)
    rhs = make_newton_rhs([M, m1, m2])
    # 10 r_t -> 4 r_t
    def cb_hand(to, yo, tn, yn, idx):
        xcm = (m1 * yn[:, 2:4] + m2 * yn[:, 4:6]) / mb
        return np.linalg.norm(xcm - yn[:, 0:2], axis=1) <= 4 * rt
    th, yh, _, _ = vint.integrate(rhs, y, 0.0, t_to_peri, rtol=rtol, atol=rtol * 1e-3, h0=1e-2, callback=cb_hand)
    t_end = t_to_peri + t_after
    out = {}
    # full Newton
    dmin = np.full((nphase, 2), np.inf)

    def cb_newton(to, yo, tn, yn, idx):
        for i in range(2):
            d = np.linalg.norm(yn[:, 2 + 2 * i:4 + 2 * i] - yn[:, 0:2], axis=1)
            dmin[idx, i] = np.minimum(dmin[idx, i], d)
        return np.zeros(len(idx), bool)
    tn, yn, _, nacc = vint.integrate(rhs, yh, th, t_end, rtol=rtol, atol=rtol * 1e-3, h0=1e-2, callback=cb_newton,
                                     max_steps=max_steps)
    d = yn[:, 4:6] - yn[:, 2:4]
    E12 = 0.5 * m1 * m2 / mb * np.sum((yn[:, 10:12] - yn[:, 8:10]) ** 2, 1) - m1 * m2 / np.linalg.norm(d, axis=1)
    a12 = np.where(E12 < 0, -m1 * m2 / (2 * np.minimum(E12, -1e-300)), np.inf)
    out["newton"] = dict(separated=float(np.mean(E12 > 0)), wide_bound=float(np.mean((E12 < 0) & (a12 > 3 * ab))),
                         member_below_4M=float(np.mean(dmin.min(1) < 4)), steps_max=int(nacc.max()),
                         unfinished=int(np.sum(tn < t_end * (1 - 1e-12))))
    # HRNA, two constructions of the state at 4 r_t
    xM, vM = yh[:, 0:2], yh[:, 6:8]
    yA = np.concatenate([yh[:, 2:4] - xM, yh[:, 4:6] - xM, yh[:, 8:10] - vM, yh[:, 10:12] - vM], 1)
    # GR-matched: CM on the Schwarzschild parabola E = 1 with pericentre rp, members' offsets kept
    xcm = (m1 * yA[:, 0:2] + m2 * yA[:, 2:4]) / mb
    vcm = (m1 * yA[:, 4:6] + m2 * yA[:, 6:8]) / mb
    r = np.linalg.norm(xcm, axis=1)
    n = xcm / r[:, None]
    tvec = np.stack([-n[:, 1], n[:, 0]], 1)
    fr = 1 - 2 / r
    Lg = np.sqrt(2 * rp ** 2 / (rp - 2))
    vr = -fr * np.sqrt(np.maximum(0, 1 - fr * (1 + Lg ** 2 / r ** 2)))
    vt = fr * Lg / r
    vcm_g = vr[:, None] * n + vt[:, None] * tvec
    yB = yA.copy()
    yB[:, 4:6] += vcm_g - vcm
    yB[:, 6:8] += vcm_g - vcm
    cons = [("hrna_handoff", yA), ("hrna_grmatched", yB)]
    if with_u:
        # hypothesis H-u: the Newtonian velocities read as u^i = dx^i/dtau of each member
        # (Schwarzschild coordinates): dx/dt = u/u^t, u^t = ((1 + u^2 + h (n.u)^2)/f)^(1/2)
        yU = yA.copy()
        for i in range(2):
            xi, ui = yA[:, 2 * i:2 * i + 2], yA[:, 4 + 2 * i:6 + 2 * i]
            ri = np.linalg.norm(xi, axis=1)
            ni = xi / ri[:, None]
            fi, hi = 1 - 2 / ri, 2 / (ri - 2)
            ur = np.sum(ni * ui, 1)
            ut = np.sqrt((1 + np.sum(ui * ui, 1) + hi * ur * ur) / fi)
            yU[:, 4 + 2 * i:6 + 2 * i] = ui / ut[:, None]
        cons.append(("hrna_u", yU))
    for lab, y0 in cons:
        alive = np.ones((nphase, 2), bool)
        hr_rhs = make_hrna_rhs(m1, m2, alive)

        def cb(to, yo, tn, yn2, idx):
            ynew = yn2.copy()
            for i in range(2):
                ro = np.linalg.norm(yo[:, 2 * i:2 * i + 2], axis=1)
                rn = np.linalg.norm(yn2[:, 2 * i:2 * i + 2], axis=1)
                hit = alive[idx, i] & (rn < R_PLUNGE) & (ro >= R_PLUNGE)
                if hit.any():
                    alive[idx[hit], i] = False
                    ynew[hit, 4 + 2 * i:6 + 2 * i] = 0.0
            return np.zeros(len(idx), bool), ynew
        vc0 = (m1 * y0[:, 4:6] + m2 * y0[:, 6:8]) / mb
        E0, L0 = hrna_energy(np.stack([xcm], 0)[0], vc0)
        tH, yH, _, nacc = vint.integrate(hr_rhs, y0, th, t_end, rtol=rtol, atol=rtol * 1e-3, h0=1e-2, callback=cb,
                                         max_steps=max_steps)
        plunged = ~alive.all(1)
        dd = yH[:, 2:4] - yH[:, 0:2]
        E12h = 0.5 * m1 * m2 / mb * np.sum((yH[:, 6:8] - yH[:, 4:6]) ** 2, 1) - m1 * m2 / np.linalg.norm(dd, axis=1)
        out[lab] = dict(separated=float(np.mean(plunged | (E12h > 0))), plunge=float(np.mean(plunged)),
                        cm_E_median=float(np.median(E0)), cm_L_median=float(np.median(L0)),
                        steps_max=int(nacc.max()), unfinished=int(np.sum(tH < t_end * (1 - 1e-12))))
    out.update(q=q, a_b=ab, rp=rp, D=rp / rt, nphase=nphase, mu_conv=mu_conv, t_handoff_median=float(np.median(th)),
               t_to_peri_from_10rt=t_to_peri, t_after=t_after, rtol=rtol)
    return out


# ------------------------------------------------------------------ 2404.16270 set-up (K5)
def s1_setup(beta, sense, nphase, rtol, k0=50.0, k1=150.0, max_steps=None):
    """HRNA at the set-up of arXiv:2404.16270 (article.tex:300-348, appendix.tex:138-179):
    M = 1, m1 = m2 = 5e-7 (M = 1e6 m_b), a0 with r_t = 101.3 M, CM released at (r0, 0),
    r0 = 50 r_t, on the Schwarzschild parabola (E = 1, L = sqrt(2 rp^2/(rp - 2))) with
    rp = r_t/beta; members at +-a0/2 (cos phi, sin phi) with the Newtonian circular velocity,
    phi uniform in [0, pi); stop when the CM is beyond 150 r_t outbound. Separated: the
    Newtonian pair energy (coordinate velocities) is positive at the end, or a member
    crossed r = 2.5 M."""
    m = 5e-7
    mb = 2 * m
    rt = 101.3
    a0 = rt * (mb / 1.0) ** (1 / 3)
    rp = rt / beta
    r0 = k0 * rt
    L = np.sqrt(2 * rp ** 2 / (rp - 2))
    f0 = 1 - 2 / r0
    xd = -f0 * np.sqrt(max(0.0, 2 / r0 - L * L / r0 ** 2 * f0))
    yd = f0 * L / r0
    phis = np.arange(nphase) * np.pi / nphase
    w = sense * np.sqrt(mb / a0 ** 3)
    y = np.zeros((nphase, 8))
    c, s = np.cos(phis), np.sin(phis)
    y[:, 0], y[:, 1] = r0 + 0.5 * a0 * c, 0.5 * a0 * s
    y[:, 2], y[:, 3] = r0 - 0.5 * a0 * c, -0.5 * a0 * s
    y[:, 4], y[:, 5] = xd - 0.5 * a0 * w * s, yd + 0.5 * a0 * w * c
    y[:, 6], y[:, 7] = xd + 0.5 * a0 * w * s, yd - 0.5 * a0 * w * c
    alive = np.ones((nphase, 2), bool)
    rhs = make_hrna_rhs(m, m, alive)
    peri_passed = np.zeros(nphase, bool)

    def cb(to, yo, tn, yn, idx):
        ynew = yn.copy()
        for i in range(2):
            ro = np.linalg.norm(yo[:, 2 * i:2 * i + 2], axis=1)
            rn = np.linalg.norm(yn[:, 2 * i:2 * i + 2], axis=1)
            hit = alive[idx, i] & (rn < R_PLUNGE) & (ro >= R_PLUNGE)
            if hit.any():
                alive[idx[hit], i] = False
                ynew[hit, 4 + 2 * i:6 + 2 * i] = 0.0
        cmo = 0.5 * (yo[:, 0:2] + yo[:, 2:4])
        cmn = 0.5 * (yn[:, 0:2] + yn[:, 2:4])
        rco, rcn = np.linalg.norm(cmo, axis=1), np.linalg.norm(cmn, axis=1)
        peri_passed[idx] |= rcn > rco
        stop = peri_passed[idx] & (rcn > k1 * rt)
        return stop, ynew
    # the time to reach 150 r_t is below 2 x (4/3)(r/2)^(3/2) for a parabola
    t_end = 2 * (4 / 3) * ((k1 * rt) / 2) ** 1.5 + 2 * (4 / 3) * (r0 / 2) ** 1.5
    t, yE, done, nacc = vint.integrate(rhs, y, 0.0, t_end, rtol=rtol, atol=rtol * 1e-4, h0=1.0, callback=cb,
                                       max_steps=max_steps)
    capped = nacc >= (max_steps or 10 ** 12)
    plunged = ~alive.all(1)
    d = yE[:, 2:4] - yE[:, 0:2]
    E12 = 0.5 * m * m / mb * np.sum((yE[:, 6:8] - yE[:, 4:6]) ** 2, 1) - m * m / np.linalg.norm(d, axis=1)
    sep = plunged | (E12 > 0)
    ok = ~capped
    return dict(beta=beta, sense=int(sense), nphase=nphase, rtol=rtol, r0_over_rt=k0, rend_over_rt=k1,
                rp=rp, a0=a0, separated=float(sep[ok].mean()), plunged=float(plunged[ok].mean()),
                n_capped=int(capped.sum()), separated_capped_counted_as_is=float(sep.mean()),
                reached_end=float(done.mean()), steps_max=int(nacc.max()), sep_flags=sep.astype(int).tolist())


# ------------------------------------------------------------------ self-tests of the HRNA
def selftest(out, rtol):
    """(a) geodesics without the pair force conserve E = -u_t and L = u_phi; (b) a circular
    geodesic at r = 10 keeps r; (c) the pericentre advance of a bound geodesic equals the
    elliptic-integral value; (d) static release: xdd = -(1 - 2/r)/r^2; (e) far from the hole
    the pair force is Newton's (binary period at r = 1e6)."""
    from scipy.integrate import quad
    res = {}
    # (a), (c): bound eccentric geodesic E = 0.97, L = 3.9 (pericentre ~ 7 M)
    E, L = 0.97, 3.9
    V2 = lambda r: (1 - 2 / r) * (1 + L * L / r ** 2) - E * E  # noqa: E731
    from scipy.optimize import brentq
    rs = np.linspace(4.0, 200, 200001)
    v = V2(rs)
    roots = [brentq(V2, rs[i], rs[i + 1]) for i in np.where(np.sign(v[:-1]) != np.sign(v[1:]))[0]]
    rp_, ra_ = roots[-2], roots[-1]
    # start at pericentre: u^r = 0, u^phi = L/r^2, u^t = E/f
    f = 1 - 2 / rp_
    vphi = (L / rp_ ** 2) / (E / f)
    alive = np.ones((1, 2), bool)
    alive[0, 1] = False
    rhs = make_hrna_rhs(1e-30, 1e-30, alive)
    y0 = np.array([[rp_, 0, 1e6, 0, 0, rp_ * vphi, 0, 0]])
    # integrate for a few radial periods, sampling to find pericentres
    t, Y, tt = 0.0, [y0[0]], [0.0]
    yy = y0
    for k in range(1, 8001):
        _, yy, _, _ = vint.integrate(rhs, yy, t, t + 0.5, rtol=rtol, atol=rtol * 1e-3, h0=1e-2)
        t += 0.5
        Y.append(yy[0].copy())
        tt.append(t)
    Y = np.array(Y)
    Eh, Lh = hrna_energy(Y[:, 0:2], Y[:, 4:6])
    res["a_dE_max"] = float(np.max(np.abs(Eh - E)))
    res["a_dL_max"] = float(np.max(np.abs(Lh - L)))
    r = np.linalg.norm(Y[:, 0:2], axis=1)
    phi = np.unwrap(np.arctan2(Y[:, 1], Y[:, 0]))
    mins = [i for i in range(1, len(r) - 1) if r[i] < r[i - 1] and r[i] <= r[i + 1]]
    # refine the pericentre angle by a parabola through three samples
    def peri_phi(i):
        c = np.polyfit(np.array(tt[i - 1:i + 2]) - tt[i], r[i - 1:i + 2], 2)
        ts_ = -c[1] / (2 * c[0])
        cp = np.polyfit(np.array(tt[i - 1:i + 2]) - tt[i], phi[i - 1:i + 2], 2)
        return np.polyval(cp, ts_)
    dphi_num = peri_phi(mins[0]) if mins[0] > 1 else None
    dphis = [peri_phi(mins[j + 1]) - peri_phi(mins[j]) for j in range(len(mins) - 1)]
    integrand = lambda rr: 2 * (L / rr ** 2) / np.sqrt(E * E - (1 - 2 / rr) * (1 + L * L / rr ** 2))  # noqa: E731
    dphi_exact = quad(integrand, rp_ * (1 + 1e-12), ra_ * (1 - 1e-12), limit=400)[0]
    res["c_dphi_num"] = float(np.mean(dphis))
    res["c_dphi_exact"] = float(dphi_exact)
    res["c_rel_err"] = float(abs(np.mean(dphis) / dphi_exact - 1))
    # (b) circular orbit at r = 10: dphi/dt = sqrt(M/r^3)
    rc = 10.0
    y0 = np.array([[rc, 0, 1e6, 0, 0, rc * np.sqrt(1 / rc ** 3), 0, 0]])
    _, yc, _, _ = vint.integrate(rhs, y0, 0.0, 2000.0, rtol=rtol, atol=rtol * 1e-3, h0=1e-2)
    res["b_circular_dr"] = float(abs(np.linalg.norm(yc[0, 0:2]) - rc))
    # (d) static release
    acc = rhs(0.0, np.array([[7.0, 0, 1e6, 0, 0, 0, 0, 0]]), np.array([0]))[0, 4]
    res["d_static_acc"] = float(acc)
    res["d_expected"] = float(-(1 - 2 / 7.0) / 49.0)
    # (e) binary far from the hole: relative orbit period against Newton's 2 pi sqrt(a^3/m)
    m = 0.05
    alive2 = np.ones((1, 2), bool)
    rhs2 = make_hrna_rhs(m, m, alive2)
    X = 1e7
    w = np.sqrt(2 * m / 3.0 ** 3)
    y0 = np.array([[X + 1.5, 0, X - 1.5, 0, 0, 1.5 * w, 0, -1.5 * w]])
    Tn = 2 * np.pi / w
    _, ye, _, _ = vint.integrate(rhs2, y0, 0.0, Tn, rtol=1e-12, atol=1e-12, h0=1e-2)
    res["e_flat_binary_return_error"] = float(np.linalg.norm(ye[0, 0:2] - y0[0, 0:2]))
    # the model's flat-space limit is Newton with each member's pair force times
    # Gamma^-2 = f - v^2 (article.tex:246-261 with g^ij -> delta^ij): integrate that directly
    fX = 1 - 2 / X

    def rhs_flat(t, y, idx):
        p1, p2, w1, w2 = y[:, 0:2], y[:, 2:4], y[:, 4:6], y[:, 6:8]
        d = p2 - p1
        r3 = np.sum(d * d, 1) ** 1.5
        g1 = fX - np.sum(w1 * w1, 1)
        g2 = fX - np.sum(w2 * w2, 1)
        return np.concatenate([w1, w2, (g1 * m / r3)[:, None] * d, -(g2 * m / r3)[:, None] * d], 1)
    yf0 = np.array([[1.5, 0, -1.5, 0, 0, 1.5 * w, 0, -1.5 * w]])
    _, yfl, _, _ = vint.integrate(rhs_flat, yf0, 0.0, Tn, rtol=1e-12, atol=1e-12, h0=1e-2)
    res["e_flat_limit_vs_scaled_newton"] = float(np.linalg.norm((ye[0, 0:2] - ye[0, 2:4]) - (yfl[0, 0:2] - yfl[0, 2:4])))
    res["e_note"] = ("return error against plain Newton is O(v^2) by construction of the model; "
                     "the comparison with Newton scaled by Gamma^-2 tests the flat limit; the "
                     "residual includes the 1e-7 curvature terms at r = 1e7")
    json.dump(res, open(os.path.join(out, "selftest.json"), "w"), indent=1)
    print(json.dumps(res))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--mode", choices=("passages", "scan", "selftest", "s1"), required=True)
    ap.add_argument("--betas", default="3,10")
    ap.add_argument("--mu-conv", choices=("total", "M"), default="total")
    ap.add_argument("--with-u", action="store_true")
    ap.add_argument("--max-steps", type=int, default=None)
    ap.add_argument("--rtol", type=float, default=1e-10)
    ap.add_argument("--nphase", type=int, default=180)
    ap.add_argument("--cases", default="10:3:8,10:3:13,4:5:9.82")
    ap.add_argument("--t-after", type=float, default=500.0)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    t0 = time.time()
    if a.mode == "passages":
        passages(a.out, a.rtol)
    elif a.mode == "selftest":
        selftest(a.out, a.rtol)
    elif a.mode == "s1":
        rows = []
        for b in (float(x) for x in a.betas.split(",")):
            for sense in (1, -1):
                row = s1_setup(b, sense, a.nphase, a.rtol, max_steps=a.max_steps)
                rows.append(row)
                print(json.dumps({k: v for k, v in row.items() if k != "sep_flags"}), flush=True)
                json.dump(rows, open(os.path.join(a.out, "s1check.json"), "w"), indent=1)
    else:
        rows = []
        for c in a.cases.split(","):
            q, ab, rp = (float(s) for s in c.split(":"))
            row = scan(q, ab, rp, a.nphase, a.rtol, a.t_after, a.mu_conv, a.with_u, a.max_steps)
            rows.append(row)
            print(json.dumps(row), flush=True)
            json.dump(rows, open(os.path.join(a.out, "scan.json"), "w"), indent=1)
    print("wall", time.time() - t0)


if __name__ == "__main__":
    main()
