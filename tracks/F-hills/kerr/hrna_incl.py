"""Inclined encounters for the HRNA of tracks/F-hills/geodesic_binary/hrna.py (read-only there).

Extension of package kerr (track F-hills, F-pre-2 for Kerr):
  * a parabolic (E = 1) centre-of-mass orbit of any inclination in Kerr, specified as in
    arXiv:2402.02178 by the pericentre r_p and L_z, with the Carter constant Q from its
    Eq. (rp) (main.tex:357-362) and the admissible L_z range of its Eq. (Lz) (main.tex:368-372);
    the CM starts in the equatorial plane at BL radius r0 moving inwards (main.tex:495-502);
  * a circular binary of any orientation: inclination iota of the binary's angular momentum
    against the CM's orbital angular momentum at release, node Omega, phase;
  * diagnostics of the final binary (energy, semi-major axis, eccentricity) with and without
    the time-dilation factor of the CM;
  * the flat-space moving binary of test R3 (HRNA's spurious self-acceleration);
  * coords 'bks' (Boyer-Lindquist time, Kerr-Schild space; hrna_bks.py) besides hrna's 'sch' and
    'cks' (JOURNAL entry 2: 'cks' pumps or drains a moving binary at first order in M/r).
The equations of motion are hrna.integrate (Eq. CoordtEqs of arXiv:2404.16270), unchanged.

Conventions (G = c = M = 1).  Frame of the binary at release: e_a = unit position of the CM,
L_hat = unit (x_cm cross v_cm) in the Cartesian coordinates of `coords`, e_b = L_hat cross e_a.
Binary basis R = [e_a e_b L_hat] Rz(Omega) Rx(iota); member 1 at +(m2/mb) a0 R (cos ph, sin ph, 0),
velocity +(m2/mb) a0 w R (-sin ph, cos ph, 0) about the CM.  iota = 0, Omega = 0 reproduces
hrna.initial_state with sense = +1 for a CM on the x axis with L along +z (test T5).
"""
from __future__ import annotations

import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("NUMBA_CACHE_DIR", "/data/haiyangw/nrpic/scratch/F-hills/tmp/kerr/numba_cache")
sys.path.insert(0, os.path.join(HERE, "..", "geodesic_binary"))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "python"))

import numpy as np  # noqa: E402

import hrna  # noqa: E402
from nrpic import kerr  # noqa: E402


# ------------------------------------------------------------------------------------------
# parabolic Kerr orbit of 2402.02178
# ------------------------------------------------------------------------------------------
def lz_range(rp, a, M=1.0):
    """Eq. (Lz) of 2402.02178 (main.tex:368-372), M = 1 there; general M here:
    (-2 a M - sqrt(2 M rp Delta)) / (rp - 2M) <= Lz <= (-2 a M + sqrt(2 M rp Delta)) / (rp - 2M)."""
    D = rp * rp - 2 * M * rp + a * a
    s = math.sqrt(2 * M * rp * D)
    return (-2 * a * M - s) / (rp - 2 * M), (-2 * a * M + s) / (rp - 2 * M)


def carter_q(rp, Lz, a, M=1.0):
    """Q of the E = 1 geodesic with radial turning point rp and L_z: Eq. (rp) of 2402.02178
    (main.tex:357-362) solved for Q:  Q = 2M [rp^3 + (a - Lz)^2 rp - Lz^2 rp^2 / (2M)] / Delta."""
    D = rp * rp - 2 * M * rp + a * a
    return 2 * M * (rp ** 3 + (a - Lz) ** 2 * rp - Lz * Lz * rp * rp / (2 * M)) / D


def radial_potential(r, Lz, Q, a, M=1.0, E=1.0):
    """R(r) = [E (r^2 + a^2) - a Lz]^2 - Delta [r^2 + (Lz - a E)^2 + Q]."""
    D = r * r - 2 * M * r + a * a
    return (E * (r * r + a * a) - a * Lz) ** 2 - D * (r * r + (Lz - a * E) ** 2 + Q)


def parabolic_bl(rp, Lz, a, r0, sigma_th=1, M=1.0):
    """BL position (r0, pi/2, 0) and covariant (u_r, u_theta, u_phi) of the E = 1 orbit with
    pericentre rp and L_z, moving inwards; sigma_th = sign of u_theta (+1: theta increases,
    the CM moves to z < 0 first)."""
    Q = carter_q(rp, Lz, a, M)
    if Q < 1e-12 * (rp * rp + Lz * Lz):
        # equatorial orbit (the ends of Eq. Lz): Q vanishes analytically; its rounding residue
        # (1e-14) would otherwise enter u_theta = sqrt(Q) at the 1e-7 level (found by test T5)
        Q = 0.0
    R0 = radial_potential(r0, Lz, Q, a, M)
    D0 = r0 * r0 - 2 * M * r0 + a * a
    u_r = -math.sqrt(R0) / D0
    u_th = sigma_th * math.sqrt(Q)          # Theta(pi/2) = Q
    return np.array([r0, math.pi / 2, 0.0]), np.array([u_r, u_th, Lz]), Q


def coord_velocity(system, x, u, a, M=1.0):
    """dx^i/dt from the covariant u_i (python/nrpic 3+1 fields)."""
    m = kerr.adm(system, x, a, M, derivs=False)
    U = m.gamma_inv @ u
    W = math.sqrt(1 + u @ U)
    return m.alpha / W * U - m.beta


def parabolic_state(coords, spin, rp, Lz, r0, sigma_th=1, M=1.0, law="hrna"):
    """Cartesian position and coordinate velocity of the CM (coords 'cks' or 'sch'; law 'newton'
    uses the Newtonian parabola of the same pericentre in the plane the relativistic L_z, Q
    define at release)."""
    a = spin * M
    xbl, ubl, Q = parabolic_bl(rp, Lz, a, r0, sigma_th, M)
    if law == "newton":
        # same orbital plane as the relativistic orbit at release; Newtonian parabola with pericentre rp
        L = math.sqrt(2 * M * rp)
        x = np.array([r0, 0.0, 0.0])
        Ltot = math.sqrt(Q + Lz * Lz)
        # tangential direction: (0, cos i, -sin i) with cos i = Lz / Ltot (theta increasing -> -z)
        ci, si = (Lz / Ltot, sigma_th * math.sqrt(Q) / Ltot) if Ltot > 0 else (1.0, 0.0)
        et = np.array([0.0, ci, -si])
        vt = L / r0
        vr = -math.sqrt(max(2 * M / r0 - vt * vt, 0.0))
        return x, vr * np.array([1.0, 0.0, 0.0]) + vt * et, Q
    if coords == "sch":
        if spin != 0.0:
            raise ValueError("coords='sch' is Schwarzschild only")
        r, th, ph = xbl
        f = 1 - 2 * M / r
        ut = 1.0 / f                                    # dt/dtau with E = 1
        rd = f * ubl[0] / ut
        thd = ubl[1] / r ** 2 / ut
        phd = ubl[2] / (r ** 2 * math.sin(th) ** 2) / ut
        n = np.array([math.sin(th) * math.cos(ph), math.sin(th) * math.sin(ph), math.cos(th)])
        e_th = np.array([math.cos(th) * math.cos(ph), math.cos(th) * math.sin(ph), -math.sin(th)])
        e_ph = np.array([-math.sin(ph), math.cos(ph), 0.0])
        return r * n, rd * n + r * thd * e_th + r * math.sin(th) * phd * e_ph, Q
    _, xc, uc = kerr.convert_state(0.0, xbl, ubl, "bl", "cks", a, M)
    xc = np.asarray(xc, float)
    vks = coord_velocity("cks", xc, np.asarray(uc, float), a, M)
    if coords == "bks":                 # same spatial point, Boyer-Lindquist time (hrna_bks.py)
        import hrna_bks
        return xc, hrna_bks.cks_to_bks_velocity(xc, vks, a, M), Q
    return xc, vks, Q


# ------------------------------------------------------------------------------------------
# binary orientation and initial state
# ------------------------------------------------------------------------------------------
def rot_x(t):
    c, s = math.cos(t), math.sin(t)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]], float)


def rot_z(t):
    c, s = math.cos(t), math.sin(t)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], float)


def rot_axis(axis, t):
    """Rotation by angle t about the unit vector axis (Rodrigues)."""
    k = np.asarray(axis, float) / np.linalg.norm(axis)
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + math.sin(t) * K + (1 - math.cos(t)) * K @ K


def orbit_frame(xc, vc):
    ea = xc / np.linalg.norm(xc)
    L = np.cross(xc, vc)
    Lh = L / np.linalg.norm(L)
    eb = np.cross(Lh, ea)
    return np.stack([ea, eb, Lh], axis=1)          # columns e_a, e_b, L_hat


def binary_basis(xc, vc, iota, Omega):
    return orbit_frame(xc, vc) @ rot_z(Omega) @ rot_x(iota)


def gamma_of(coords, spin, x, v, M=1.0):
    g, gi, dg = np.zeros((4, 4)), np.zeros((4, 4)), np.zeros((3, 4, 4))
    if coords == "bks":
        import hrna_bks
        _, _, gam = hrna_bks.energy_lz(hrna.LAW_HRNA, hrna_bks.COORDS_BKS, M, spin * M, x, v, g, gi, dg)
        return gam
    cc = hrna.COORDS_CKS if coords == "cks" else hrna.COORDS_SCH
    _, _, gam = hrna.energy_lz(hrna.LAW_HRNA, cc, M, spin * M, x, v, g, gi, dg)
    return gam


def place_binary(xc, vc, B, mb, q12, a0, phase, w_scale=1.0):
    m1 = mb / (1 + q12)
    m2 = mb * q12 / (1 + q12)
    w = math.sqrt(mb / a0 ** 3) * w_scale
    e = B @ np.array([math.cos(phase), math.sin(phase), 0.0])
    et = B @ np.array([-math.sin(phase), math.cos(phase), 0.0])
    x1 = xc + (m2 / mb) * a0 * e
    x2 = xc - (m1 / mb) * a0 * e
    v1 = vc + (m2 / mb) * a0 * w * et
    v2 = vc - (m1 / mb) * a0 * w * et
    return np.concatenate([x1, v1, x2, v2]), m1, m2


def initial_state_incl(law="hrna", coords="cks", spin=0.9, mb=6.25e-6, q12=2 / 3, a0=0.125,
                       rp=10.0, Lz=0.0, iota=0.0, Omega=0.0, phase=0.0, r0=100.0, sigma_th=1,
                       ic="gamma", M=1.0):
    """ic: 'coord' = convention of 2404 (hrna.initial_state: internal velocity in coordinate time);
    'gamma' = internal angular velocity divided by the CM's Gamma = dt/dtau at release
    (circular in the CM proper time to leading order; hrna's ic_gamma)."""
    xc, vc, Q = parabolic_state(coords, spin, rp, Lz, r0, sigma_th, M, law)
    B = binary_basis(xc, vc, iota, Omega)
    ws = 1.0
    if ic == "gamma" and law != "newton":
        ws = 1.0 / gamma_of(coords, spin, xc, vc, M)
    y0, m1, m2 = place_binary(xc, vc, B, mb, q12, a0, phase, ws)
    rt = (M / mb) ** (1 / 3) * a0
    return y0, dict(rt=rt, rp=rp, r0=r0, m1=m1, m2=m2, Q=Q, xc=xc, vc=vc, B=B, w_scale=ws)


def rotate_y(y, R):
    """Rotate a 12-vector state (x1, v1, x2, v2) by R."""
    out = np.empty_like(y)
    for k in range(4):
        out[3 * k:3 * k + 3] = R @ y[3 * k:3 * k + 3]
    return out


# ------------------------------------------------------------------------------------------
# one encounter
# ------------------------------------------------------------------------------------------
_WK = None


def integrate_y0(y0, law, coords, spin, m1, m2, a0, r_stop, r_apo_min, t_max, rtol=1e-12,
                 atol=1e-14, record=0, r_plunge=None, M=1.0, max_steps=20_000_000):
    global _WK
    if _WK is None:
        _WK = hrna._work()
    lawc = hrna.LAW_NEWTON if law == "newton" else hrna.LAW_HRNA
    cc = {"sch": hrna.COORDS_SCH, "cks": hrna.COORDS_CKS, "bks": 2}[coords]
    a = spin * M
    if r_plunge is None:
        if lawc == hrna.LAW_NEWTON:
            r_plunge = 0.0
        elif cc == hrna.COORDS_SCH:
            r_plunge = 2.5 * M
        else:
            r_plunge = M + math.sqrt(M * M - a * a) + 0.05 * M
    mb = m1 + m2
    T0 = 2 * math.pi * math.sqrt(a0 ** 3 / mb)
    integ = hrna.integrate
    if cc == 2:                         # Boyer-Lindquist time, Kerr-Schild space (hrna_bks.py)
        import hrna_bks
        integ = hrna_bks.integrate
    return integ(lawc, cc, hrna.PAIR_GRAVITY, M, a, m1, m2, 0.0, 0.0, y0, T0 / 200.0,
                          rtol, atol, r_stop, r_apo_min, r_plunge, t_max, max_steps, a0,
                          int(record), hrna._A, hrna._B, hrna._C, hrna._E3, hrna._E5, _WK)


def binary_elements(y, m1, m2, gam=1.0):
    """Newtonian elements of the pair from the coordinate state; gam multiplies the relative
    velocity (gam = CM's dt/dtau converts to proper-time velocity to leading order)."""
    mb = m1 + m2
    d = y[0:3] - y[6:9]
    w = (y[3:6] - y[9:12]) * gam
    r = float(np.linalg.norm(d))
    Eb = 0.5 * float(w @ w) - mb / r
    Lv = np.cross(d, w)
    Lb = float(np.linalg.norm(Lv))
    arg = 1 + 2 * Eb * Lb ** 2 / mb ** 2
    e = math.sqrt(arg) if arg > 0 else 0.0
    a = -mb / (2 * Eb) if Eb < 0 else math.inf
    return dict(Eb=Eb, a=a, e=e, Lhat=(Lv / Lb).tolist() if Lb > 0 else [0.0, 0.0, 0.0], r12=r)


def run_incl(law="hrna", coords="cks", spin=0.9, mb=6.25e-6, q12=2 / 3, a0=0.125, rp=10.0,
             Lz=0.0, iota=0.0, Omega=0.0, phase=0.0, r0=100.0, r_stop=None, sigma_th=1,
             ic="gamma", rtol=1e-12, atol=1e-14, record=0, M=1.0):
    """One encounter of the 2402.02178 set-up under HRNA (or law='newton').  Stops when the CM
    recedes through r_stop (default r0; 2402: 'traveled to a distance of r = 100M',
    main.tex:610-611).  Returns a dict with the outcome and the final binary."""
    y0, info = initial_state_incl(law, coords, spin, mb, q12, a0, rp, Lz, iota, Omega, phase, r0,
                                  sigma_th, ic, M)
    if r_stop is None:
        r_stop = r0
    m1, m2 = info["m1"], info["m2"]
    t_max = 6.0 * (math.sqrt(2.0) / 3.0) * (r0 ** 1.5 + r_stop ** 1.5) + 200.0
    status, t, y, diag, rec_t, rec_y, nrec, nsteps, nrej = integrate_y0(
        y0, law, coords, spin, m1, m2, a0, r_stop, 1e300, t_max, rtol, atol, record, M=M)
    mbv = m1 + m2
    xc = (m1 * y[0:3] + m2 * y[6:9]) / mbv
    vc = (m1 * y[3:6] + m2 * y[9:12]) / mbv
    try:
        gam = gamma_of(coords, spin, xc, vc, M) if law != "newton" else 1.0
    except (ValueError, ZeroDivisionError):
        gam = math.nan
    el_c = binary_elements(y, m1, m2, 1.0)
    el_g = binary_elements(y, m1, m2, gam) if np.isfinite(gam) else el_c
    plunged = int(diag[6] > 0) + 2 * int(diag[7] > 0)
    Lb0 = info["B"][:, 2]
    out = dict(status=int(status), t_end=float(t), nsteps=int(nsteps), nrej=int(nrej),
               plunged=plunged, r_peri=float(diag[1]), a_min=float(diag[2]) / a0,
               survived=bool(plunged == 0 and el_g["Eb"] < 0 and status == 0),
               survived_coord=bool(plunged == 0 and el_c["Eb"] < 0 and status == 0),
               a_fin=el_g["a"] / a0, e_fin=el_g["e"], Eb_fin=el_g["Eb"],
               a_fin_coord=el_c["a"] / a0, e_fin_coord=el_c["e"],
               cos_flip=float(np.dot(Lb0, el_g["Lhat"])), Q=info["Q"], rt=info["rt"],
               gamma_end=gam)
    if record:
        out["rec_t"] = np.array(rec_t)
        out["rec_y"] = np.array(rec_y)
    return out


# ------------------------------------------------------------------------------------------
# R3: a circular binary moving uniformly in flat space (M = 0)
# ------------------------------------------------------------------------------------------
def flat_binary_y0(m1, m2, a0, V, psi=0.0, X0=(1000.0, 0.0, 0.0), phase=0.0, w_scale=1.0):
    """Binary in the x-y plane (L along +z), CM velocity V (cos psi e_x + sin psi e_z): psi is the
    angle between V and the binary plane.  Member 1 at +(m2/mb) a0 e(phase)."""
    mb = m1 + m2
    w = math.sqrt(mb / a0 ** 3) * w_scale
    e = np.array([math.cos(phase), math.sin(phase), 0.0])
    et = np.array([-math.sin(phase), math.cos(phase), 0.0])
    vc = V * np.array([math.cos(psi), 0.0, math.sin(psi)])
    X0 = np.asarray(X0, float)
    return np.concatenate([X0 + (m2 / mb) * a0 * e, vc + (m2 / mb) * a0 * w * et,
                           X0 - (m1 / mb) * a0 * e, vc - (m1 / mb) * a0 * w * et])


def flat_run(y0, m1, m2, a0, T, rec_cap=400000, rtol=1e-12, atol=1e-14):
    """Integrate under HRNA with M = 0 (hrna.integrate, Schwarzschild-form metric with M = 0 is
    Minkowski) to time T; returns (t, Y)."""
    out = integrate_y0(y0, "hrna", "sch", 0.0, m1, m2, a0, 1e300, 1e300, T, rtol, atol,
                       record=rec_cap, r_plunge=0.0, M=0.0)
    t, Y = np.array(out[4]), np.array(out[5])
    return t, Y
