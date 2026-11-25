#!/usr/bin/env python3
"""
Post-Newtonian (Newtonian + 1PN EIH + 1.5PN SMBH Kerr spin-orbit) 3-body scout
for the AGN Binary-EMRI ZKL oscillation full-NR simulation suite.

Tests candidate configurations with:
  - Body 0: central SMBH (M_0 = 1.0, dimensionless spin chi_0 along +z)
  - Bodies 1, 2: gravitating inner binary BH particles (m_1, m_2)
Checks Hill stability (a_in / R_Hill), ZKL timescale (t_ZKL), GR quenching
parameter (eps_GR), mesh resolution (a_in / dx_bin, m_i / dx_bin), and actual
integrated peak eccentricity e_max over t in [0, 1500] M.
"""

import json
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

CZ_DIR = "/home/schmidt/ssci-haiyangw/.gemini/config/skills/cz-figure-style/resources"
if os.path.isdir(CZ_DIR) and CZ_DIR not in sys.path:
    sys.path.insert(0, CZ_DIR)
import czstyle as cz


def accel_3body_pn(pos, vel, masses, chi0_vec):
    """
    Compute 3-body acceleration in center-of-mass / harmonic-like coords (G=c=1):
      - Newtonian pairwise attraction
      - 1PN Einstein-Infeld-Hoffmann (EIH) acceleration across all pairs
      - 1.5PN gravitomagnetic spin-orbit (Lense-Thirring) acceleration from body 0 spin S_0 = M_0^2 chi_0
    """
    n = 3
    acc_n = np.zeros((n, 3), dtype=np.float64)
    r_mat = np.zeros((n, n), dtype=np.float64)
    n_mat = np.zeros((n, n, 3), dtype=np.float64)

    for a in range(n):
        for b in range(n):
            if a == b:
                continue
            dx = pos[a] - pos[b]
            r = float(np.linalg.norm(dx))
            r_mat[a, b] = r
            nv = dx / r
            n_mat[a, b] = nv
            acc_n[a] += -(masses[b] / (r * r)) * nv

    acc_1pn = np.zeros((n, 3), dtype=np.float64)
    v2 = np.sum(vel * vel, axis=1)

    for a in range(n):
        phi_a = 0.0
        for c in range(n):
            if c != a:
                phi_a += masses[c] / r_mat[a, c]

        for b in range(n):
            if b == a:
                continue
            rab = r_mat[a, b]
            nab = n_mat[a, b]
            va = vel[a]
            vb = vel[b]
            vab_dot = float(np.dot(va, vb))
            nb_va = float(np.dot(nab, va))
            nb_vb = float(np.dot(nab, vb))

            phi_b = 0.0
            for c in range(n):
                if c != b:
                    phi_b += masses[c] / r_mat[b, c]

            # Third-body Newtonian cross-term inside EIH
            third_dot = 0.0
            third_acc = np.zeros(3, dtype=np.float64)
            for c in range(n):
                if c != a and c != b:
                    rcb = r_mat[b, c]
                    # acc of b from c = -(m_c/r_bc^2) n_bc
                    n_bc = n_mat[b, c]
                    abc = -(masses[c] / (rcb * rcb)) * n_bc
                    third_dot += float(np.dot(pos[a] - pos[b], abc))
                    third_acc += abc

            # Include pairwise Newtonian part inside a_b^(0) for 3-body EIH
            a_b_newt = -(masses[a] / (rab * rab)) * (-nab) + third_acc
            dot_xa_ab_newt = float(np.dot(pos[a] - pos[b], a_b_newt))

            c_rad = (
                4.0 * phi_a
                + 1.0 * phi_b
                + 0.5 * dot_xa_ab_newt
                - v2[a]
                - 2.0 * v2[b]
                + 4.0 * vab_dot
                + 1.5 * nb_vb * nb_vb
            )
            term_rad = (masses[b] / (rab * rab)) * c_rad * nab
            term_vel = (masses[b] / (rab * rab)) * (4.0 * nb_va - 3.0 * nb_vb) * (va - vb)
            term_lin = (3.5 * masses[b] / rab) * a_b_newt
            acc_1pn[a] += term_rad + term_vel + term_lin

    # 1.5PN Lense-Thirring spin-orbit force from primary SMBH spin S_0
    acc_so = np.zeros((n, 3), dtype=np.float64)
    s0 = (masses[0] ** 2) * chi0_vec
    if float(np.linalg.norm(s0)) > 0.0:
        for i in (1, 2):
            rvec = pos[i] - pos[0]
            vvec = vel[i] - vel[0]
            r = r_mat[i, 0]
            nv = rvec / r
            g_so = (masses[0] / masses[0])  # unit bookkeeping
            # Standard test-body / extreme-mass-ratio SO acceleration (Kidder 1995 Eq. 2.2b, mu/M -> 0 limit)
            # a_SO = (1/r^3) * [ 6 n ( (n x v) . S ) + 4 (v x S) - 6 (n . v) (n x S) ] ... factor 2 G / c^3
            v_cross_s = np.cross(vvec, s0)
            n_cross_s = np.cross(nv, s0)
            nxv_dot_s = float(np.dot(np.cross(nv, vvec), s0))
            ndotv = float(np.dot(nv, vvec))
            a_i = (2.0 / (r ** 3)) * (2.0 * v_cross_s - 3.0 * ndotv * n_cross_s - 3.0 * nxv_dot_s * nv)
            # Wait: check sign & factor! Kidder 1995 Eq. (2.2a):
            # dv/dt|_SO = (1/r^3) [ (6/(r^2)) r (h . S_eff) - 4 (v x S_eff2) + 3 rdot (n x S_eff3) ]
            # For test particle (m_i << M_0): a_SO = (2 / r^3) [ 2 (v x S_0) - 3 (n . v)(n x S_0) - ... ] -> let's double check!
            # Actually Kidder 1995: dv/dt_SO = (G/c^3 r^3) [ (12/r^2)(X x S) ?? Wait: check prograde periapsis shift!
            # Let S = (0,0,S), orbit in x-y: r=(r,0,0), v=(0,v,0), n=(1,0,0), n.v=0.
            # Prograde L_z > 0 aligned with S_z > 0 reduces effective gravity / shifts omega retrograde:
            # v x S = (v S, 0, 0) (OUTWARD!), (n x v).S = +v S -> -3 v S n (INWARD!).
            # Standard Kidder (1995) / Will GR effective force in harmonic coords for test body around Kerr S:
            # a_SO = (1/r^3) [ 6 (n x v).S n + 4 (v x S) - 6 (n.v)(n x S) ] ? Check signs: 4 vS - (-6?) = -2 vS? Wait:
            # In harmonic coords, L_SO = (2 S . (r x v)) / r^3 -> Euler-Lagrange gives F_SO = 2 (v x S)/r^3 - ... + 6 (r.(v x S)) r / r^5
            #Wait: F = 2/r^3 [ 2 (v x S) - 3 (n.v)(n x S) + 3 ( (n x v).S ) n ]?! Check coefficient for equatorial circular orbit:
            # In Kerr equatorial circular orbit (Blanchet): Omega^2 r^3 / M = 1 - 2 chi (M/r)^(3/2). Wait: at v=sqrt(M/r), centripetal excess = 2 chi (M/r)^(3/2) M/r^2 = 2 chi M^2 v / r^3 ?? Wait:
            # No: g_0i = -2 eps_{ijk} S_j x_k / r^3. d^2 x / dt^2 ~ v x (curl g_0) = v x B_g!
            # B_g = curl(-2 S x r / r^3) = -2 [ 3 n (n.S) - S ] / r^3 ! (gravitomagnetic dipole!).
            #Wait: for B_g along -S_z in equatorial plane: n.S = 0 => B_g = +2 S / r^3! Wait: check Lense-Thirring sign:
            # For prograde orbit (r=x, v=+y, S=+z): GM/r^2 inward, Coriolis-like gravitomagnetic Lorentz force = 2 (v x B_g) or (v x B_g)?
            # Wait: GEM Lorentz force in 1.5PN: F_GEM = - v x B_g with B_g = (2/r^3)(3 n(n.S) - S) ? Check!
            # Wait: radial derivative d/dr(-2 S.(r x v)/r^3) gives (-2/r^3)(v x S) - (-6/r^4)(n.(S?)) -> wait:
            # L_SO = - (2/r^3) S . (r x v) + ... Let's compute exact Euler-Lagrange from L_spin-orbit!
            # Harmonic-gauge Kerr metric at 1.5PN: ds^2 = -(1 - 2M/r)dt^2 + g_0i dt dx^i + (1+2M/r)dx^2 with g_0i = -2 (S x r)_i / r^3.
            # Particle Lagrangian L = -m sqrt(-ds^2/dt^2) -> L_1.5PN = -m g_0i v^i = + 2 (S x r).v / r^3 = + 2 S . (r x v) / r^3.
            # Notice dL/dv = + 2 (S x r) / r^3 = 2 (S x n) / r^2.
            # Time derivative d/dt (dL/dv) = 2 (S x v) / r^3 - 6 (n.v) (S x n) / r^3 = -2 (v x S)/r^3 + 6 (n.v)(n x S)/r^3.
            # Gradient dL/dr: d/dr [ 2 (v x S).r / r^3 ] = 2 (v x S)/r^3 - 6 ((v x S).n) n / r^3 = 2 (v x S)/r^3 + 6 ((n x v).S) n / r^3!
            #Wait! (v x S).n = (n x v).S! Let's check: n=(1,0,0), v=(0,v,0), S=(0,0,S): v x S = (vS,0,0), (v x S).n = +vS; n x v = (0,0,v), (n x v).S = +vS. SAME!
            # Therefore Euler-Lagrange a_SO = dL/dr - d/dt(dL/dv):
            # a_SO = [2 (v x S) - 6 ((n x v).S) n]/r^3 - [-2 (v x S) + 6 (n.v)(n x S)]/r^3
            #      = (1/r^3) [ 4 (v x S) - 6 (n.v)(n x S) - 6 ((n x v).S) n ]
            #      = (2 / r^3) [ 2 (v x S) - 3 (n.v)(n x S) - 3 ((n x v).S) n ] !!
            # Check equatorial circular orbit: n=(1,0,0), v=(0,v,0), S=(0,0,S):
            # 2 (v x S) = +4 v S xhat (OUTWARD!), -3 ((n x v).S) n = -6 v S xhat (INWARD!) -> NET = -2 v S / r^3 xhat? Wait: circular speed decreases on prograde?
            # Let's check exact Kerr geodesic Omega_+ = sqrt(M)/(r^{3/2} + chi M^{3/2}):
            # Omega^2 r = M/r^2 * (1 + chi M^{3/2}/r^{3/2})^{-2} approx M/r^2 - 2 chi M^{5/2} / r^{7/2} = M/r^2 - 2 v S / r^3 (REDUCED inward gravity => OUTWARD force +2 v S / r^3!!).
            # Check our a_SO sign: Wait why did we get +4 - 6 = -2 instead of +2?! Check L_1.5PN sign!
            # ds^2 = -(1-2M/r)dt^2 + 2 g_0i dx^i dt + ... In Schwarzschild/Kerr Boyer-Lindquist: g_{t phi} = -2 a M sin^2 th / r!
            # With g_{t phi} = -2 S_z (x dy - y dx)/r^3: ds^2 has + 2 g_{0i} dt dx^i = -4 (S x r).v / r^3 dt^2 !!
            # Then sqrt(-ds^2/dt^2) = sqrt(1 - v^2 - 2M/r - 2 g_{0i} v^i) => L = - sqrt(...) has + g_{0i} v^i = -2 (S x r).v / r^3 (OPPOSITE SIGN!).
            # Checking circular Kerr orbit immediately caught that minus sign! With the right sign g_{0i} v^i = -2 S.(r x v)/r^3:
            # a_SO = (2 / r^3) [ -2 (v x S) + 3 (n.v)(n x S) + 3 ((n x v).S) n ]!
            # At n=(1,0,0), v=(0,v,0), S=(0,0,S): -4 vS + 6 vS = +2 vS / r^3 OUTWARD!
            # That reduces effective inward gravity from M/r^2 to M/r^2 - 2 v S / r^3 = (M/r^2)(1 - 2 chi (M/r)^{3/2}), matching Kerr's exact Omega_+ = 1/(r^{3/2}+a)!!
            # And check Lense-Thirring precession of inclined orbit: dL/dt = r x a_SO = (-4/r^2)(n x (v x S)) = (4/r^3)(n.S L? No, S_vec prec!)
            # Torque r x (-2 v x S) * 2/r^3 = (-4/r^3) [ (r.S)v - (r.v)S ] averaged over circular orbit = (2/r^3)(S x L) -> dL/dt = +(2/r^3)(S x L), PROGRADE LT precession!
            # AND reaction on body 0: acc_so[0] -= (masses[i] / masses[0]) * a_i.
            a_i = (2.0 / (r ** 3)) * (-2.0 * v_cross_s + 3.0 * ndotv * n_cross_s + 3.0 * nxv_dot_s * nv)
            acc_so[i] += a_i
            acc_so[0] -= (masses[i] / masses[0]) * a_i

    return acc_n + acc_1pn + acc_so


def build_triple_ic(m0, m1, m2, a_out, a_in, e_in, inc_deg, omega_deg=0.0, lan_deg=0.0):
    """
    Construct barycentric 3-body harmonic-coordinate initial conditions with an outer
    1PN circular orbit in the x-y plane and an inner binary transformed from its local
    comoving Fermi-normal (proper) frame into global harmonic coordinates.
    """
    m_bin = m1 + m2
    m_tot = m0 + m_bin
    nu_out = (m0 * m_bin) / (m_tot * m_tot)

    # Outer 1PN circular orbit in x-y plane (binary COM vs SMBH)
    r_out_vec = np.array([a_out, 0.0, 0.0])
    v_out_newt = math.sqrt(m_tot / a_out)
    v_out_mag = v_out_newt * (1.0 - 0.5 * (3.0 - nu_out) * (m_tot / a_out))
    v_out_vec = np.array([0.0, v_out_mag, 0.0])

    # Local Fermi-normal (proper) inner binary started at apoapsis r_in = a_in*(1 + e_in)
    r_apo = a_in * (1.0 + e_in)
    v_apo = math.sqrt((m_bin / a_in) * (1.0 - e_in) / (1.0 + e_in))
    r_in_loc = np.array([r_apo, 0.0, 0.0])
    v_in_loc = np.array([0.0, v_apo, 0.0])

    # Rotate inner binary by argument of periapsis (omega), inclination (inc), ascending node (lan)
    ci, si = math.cos(math.radians(inc_deg)), math.sin(math.radians(inc_deg))
    co, so = math.cos(math.radians(omega_deg)), math.sin(math.radians(omega_deg))
    cl, sl = math.cos(math.radians(lan_deg)), math.sin(math.radians(lan_deg))

    rz_w = np.array([[co, -so, 0.0], [so, co, 0.0], [0.0, 0.0, 1.0]])
    rx_i = np.array([[1.0, 0.0, 0.0], [0.0, ci, -si], [0.0, si, ci]])
    rz_o = np.array([[cl, -sl, 0.0], [sl, cl, 0.0], [0.0, 0.0, 1.0]])
    rot = rz_o @ rx_i @ rz_w

    r_prop = rot @ r_in_loc
    v_prop = rot @ v_in_loc

    # Transform local Fermi-normal displacement/velocity -> global 1PN harmonic coordinates.
    # Matching both EIH 1PN static conformal/time factor (1 - 5 Phi0 -> u ~ 1 - 2.5 Phi0 at
    # r_harm = (1 - Phi0) R_loc) and special-relativistic Lorentz contraction & dilation.
    phi0 = m0 / a_out
    v_com_vec = (m0 / m_tot) * v_out_vec
    v2_com = float(np.dot(v_com_vec, v_com_vec))
    c_phi_r = 1.0 - phi0
    c_phi_v = 1.0 - 2.5 * phi0 - 0.5 * v2_com
    r_in_vec = c_phi_r * r_prop - 0.5 * float(np.dot(r_prop, v_com_vec)) * v_com_vec
    v_in_vec = c_phi_v * v_prop - 0.5 * float(np.dot(v_prop, v_com_vec)) * v_com_vec

    # Position/velocity of binary COM and SMBH in barycentric frame
    pos0 = -(m_bin / m_tot) * r_out_vec
    vel0 = -(m_bin / m_tot) * v_out_vec
    r_com = (m0 / m_tot) * r_out_vec
    v_com = (m0 / m_tot) * v_out_vec

    pos1 = r_com - (m2 / m_bin) * r_in_vec
    vel1 = v_com - (m2 / m_bin) * v_in_vec
    pos2 = r_com + (m1 / m_bin) * r_in_vec
    vel2 = v_com + (m1 / m_bin) * v_in_vec

    return np.vstack([pos0, pos1, pos2]), np.vstack([vel0, vel1, vel2])


def inner_elements(pos, vel, m0, m1, m2):
    """Return local Fermi-normal osculating (a_in, e_in, inc_deg, r_loc) of the inner binary."""
    m_bin = m1 + m2
    # Instantaneous outer orbit separation and barycentric COM velocity
    r_bin_com = (m1 * pos[1] + m2 * pos[2]) / m_bin
    v_bin_com = (m1 * vel[1] + m2 * vel[2]) / m_bin
    r_out_vec = r_bin_com - pos[0]
    v_out_vec = v_bin_com - vel[0]
    r_out = max(float(np.linalg.norm(r_out_vec)), 1e-12)
    phi0 = m0 / r_out
    v2_com = float(np.dot(v_bin_com, v_bin_com))

    c_phi_r = 1.0 - phi0
    c_phi_v = 1.0 - 2.5 * phi0 - 0.5 * v2_com
    dr_harm = pos[2] - pos[1]
    dv_harm = vel[2] - vel[1]

    # Exact algebraic inverse of x_harm = c * x_loc - 0.5 * (x_loc . V) * V
    k_r = 0.5 / (c_phi_r * (c_phi_r - 0.5 * v2_com))
    k_v = 0.5 / (c_phi_v * (c_phi_v - 0.5 * v2_com))
    dr = (dr_harm / c_phi_r) + k_r * float(np.dot(dr_harm, v_bin_com)) * v_bin_com
    dv = (dv_harm / c_phi_v) + k_v * float(np.dot(dv_harm, v_bin_com)) * v_bin_com

    r = float(np.linalg.norm(dr))
    v2 = float(np.dot(dv, dv))
    inv_a = 2.0 / r - v2 / m_bin
    a_in = 1.0 / inv_a if inv_a > 0 else float("nan")
    h_in = np.cross(dr, dv)
    e_vec = np.cross(dv, h_in) / m_bin - dr / r
    e_in = float(np.linalg.norm(e_vec))

    h_out = np.cross(r_out_vec, v_out_vec)
    cos_i = float(np.dot(h_in, h_out)) / max(float(np.linalg.norm(h_in) * np.linalg.norm(h_out)), 1e-30)
    cos_i = max(-1.0, min(1.0, cos_i))
    inc_deg = math.degrees(math.acos(cos_i))
    return a_in, e_in, inc_deg, r


def integrate_case(m0, m1, m2, a_out, a_in, e0, inc_deg, chi0, t_end=1500.0, dt=0.25):
    pos, vel = build_triple_ic(m0, m1, m2, a_out, a_in, e0, inc_deg, omega_deg=45.0)
    masses = (m0, m1, m2)
    chi0_vec = np.array([0.0, 0.0, chi0], dtype=np.float64)

    nsteps = int(round(t_end / dt))
    stride = max(1, int(round(2.0 / dt)))
    ts, a_hist, e_hist, i_hist, r_hist = [], [], [], [], []
    unbound = False

    def deriv(p, v):
        return v, accel_3body_pn(p, v, masses, chi0_vec)

    for step in range(nsteps + 1):
        t = step * dt
        if step % stride == 0:
            ai, ei, ii, ri = inner_elements(pos, vel, m0, m1, m2)
            ts.append(t)
            a_hist.append(ai)
            e_hist.append(ei)
            i_hist.append(ii)
            r_hist.append(ri)
            if not math.isfinite(ai) or ai <= 0 or ei >= 0.999:
                unbound = True
                break
        if step == nsteps:
            break
        k1r, k1v = deriv(pos, vel)
        k2r, k2v = deriv(pos + 0.5 * dt * k1r, vel + 0.5 * dt * k1v)
        k3r, k3v = deriv(pos + 0.5 * dt * k2r, vel + 0.5 * dt * k2v)
        k4r, k4v = deriv(pos + dt * k3r, vel + dt * k3v)
        pos = pos + (dt / 6.0) * (k1r + 2.0 * k2r + 2.0 * k3r + k4r)
        vel = vel + (dt / 6.0) * (k1v + 2.0 * k2v + 2.0 * k3v + k4v)

    return {
        "t": np.asarray(ts),
        "a_in": np.asarray(a_hist),
        "e_in": np.asarray(e_hist),
        "inc_deg": np.asarray(i_hist),
        "r_in": np.asarray(r_hist),
        "unbound": unbound,
    }


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(root, "data")
    fig_dir = os.path.join(root, "paper", "figures")
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(fig_dir, exist_ok=True)

    m0 = 1.0
    dx_bin = 1.0 / 16.0  # cheap M/16 resolution in the binary orbital shell

    # Systematic candidate suite built around fiducial AGN Binary-EMRI ZKL sweet spot
    # Check both moderate-mass/wider-orbit and compact configurations that stay Hill-stable at high inclination
    configs = [
        # Inclination sweep (Suite 1): m_bin=0.008 (m1=m2=0.004), a_out=15 M, a_in=0.72 M -> R_Hill=2.08 M, f_H=0.346, dx_bin=M/24=0.0417 -> 17.3 cells/a_in
        dict(name="I20_subcrit", suite="inclination", m1=0.004, m2=0.004, a_out=15.0, a_in=0.72, e0=0.05, inc=20.0, chi0=0.0),
        dict(name="I60_mild", suite="inclination", m1=0.004, m2=0.004, a_out=15.0, a_in=0.72, e0=0.05, inc=60.0, chi0=0.0),
        dict(name="FID_I82_chi0", suite="fiducial", m1=0.004, m2=0.004, a_out=15.0, a_in=0.72, e0=0.05, inc=82.0, chi0=0.0),
        dict(name="I86_high", suite="inclination", m1=0.004, m2=0.004, a_out=15.0, a_in=0.72, e0=0.05, inc=86.0, chi0=0.0),
        # GR quenching sweep (Suite 2: fixed m_bin=0.008, a_out=15 M, vary a_in -> eps_GR in [1.43, 7.08])
        dict(name="GR_low_a082", suite="gr_quench", m1=0.004, m2=0.004, a_out=15.0, a_in=0.82, e0=0.05, inc=82.0, chi0=0.0),
        dict(name="GR_mid_a062", suite="gr_quench", m1=0.004, m2=0.004, a_out=15.0, a_in=0.62, e0=0.05, inc=82.0, chi0=0.0),
        dict(name="GR_high_a055", suite="gr_quench", m1=0.004, m2=0.004, a_out=15.0, a_in=0.55, e0=0.05, inc=82.0, chi0=0.0),
        # Kerr SMBH spin sweep (Suite 3)
        dict(name="SPIN_p07", suite="kerr_spin", m1=0.004, m2=0.004, a_out=15.0, a_in=0.72, e0=0.05, inc=82.0, chi0=0.7),
        dict(name="SPIN_m07", suite="kerr_spin", m1=0.004, m2=0.004, a_out=15.0, a_in=0.72, e0=0.05, inc=82.0, chi0=-0.7),
        dict(name="SPIN_p09", suite="kerr_spin", m1=0.004, m2=0.004, a_out=15.0, a_in=0.72, e0=0.05, inc=82.0, chi0=0.9),
        # Unequal mass octupole-ZKL (Suite 4)
        dict(name="OCT_q3_I80", suite="octupole", m1=0.006, m2=0.002, a_out=15.0, a_in=0.72, e0=0.05, inc=80.0, chi0=0.7),
    ]

    summary = []
    trajs = {}
    t_end = 1800.0
    dx_bin = 1.0 / 24.0  # M/24 resolution on orbital shell with 32^3 blocks
    for cfg in configs:
        m_bin = cfg["m1"] + cfg["m2"]
        r_hill = cfg["a_out"] * (m_bin / (3.0 * m0)) ** (1.0 / 3.0)
        f_hill = cfg["a_in"] / r_hill
        p_out = 2.0 * math.pi * math.sqrt((cfg["a_out"] ** 3) / (m0 + m_bin))
        p_in = 2.0 * math.pi * math.sqrt((cfg["a_in"] ** 3) / m_bin)
        eps_gr = 3.0 * (m_bin ** 2) * (cfg["a_out"] ** 3) / (m0 * (cfg["a_in"] ** 4))
        t_zkl_est = 0.5 * (p_out ** 2 / p_in) * (m0 + m_bin) / m0

        res = integrate_case(
            m0, cfg["m1"], cfg["m2"], cfg["a_out"], cfg["a_in"],
            cfg["e0"], cfg["inc"], cfg["chi0"], t_end=t_end, dt=0.10
        )
        trajs[cfg["name"]] = res
        e_max = float(np.nanmax(res["e_in"]))
        i_min = float(np.nanmin(res["inc_deg"]))
        i_max = float(np.nanmax(res["inc_deg"]))
        r_min_p = float(np.nanmin(res["r_in"]))
        row = {
            **cfg,
            "m_bin": round(m_bin, 6),
            "r_hill": round(r_hill, 4),
            "a_over_rhill": round(f_hill, 4),
            "p_out": round(p_out, 2),
            "p_in": round(p_in, 2),
            "t_zkl_est": round(t_zkl_est, 1),
            "eps_gr": round(eps_gr, 3),
            "a_in_over_dx24": round(cfg["a_in"] / dx_bin, 2),
            "r_peri_min_over_dx24": round(r_min_p / dx_bin, 2),
            "m1_over_dx24": round(cfg["m1"] / dx_bin, 4),
            "e_max_1pn": round(e_max, 4),
            "inc_range_deg": [round(i_min, 2), round(i_max, 2)],
            "unbound": bool(res["unbound"]),
        }
        summary.append(row)
        print(
            f"{cfg['name']:18s} | f_H={f_hill:.3f} | eps_GR={eps_gr:.3f} | "
            f"a_in/dx={row['a_in_over_dx24']:5.1f} | t_ZKL~{t_zkl_est:6.1f} M | "
            f"e_max={e_max:.3f} | r_min={r_min_p:.3f} M | unbound={res['unbound']}"
        )

    out_json = os.path.join(data_dir, "zkl_scout_matrix.json")
    with open(out_json, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Wrote {out_json}")

    # Plot clean 3-panel Cyclic-Zoom scout diagnostic figure
    cz.use_style()
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.35), sharex=True, sharey=True)
    fig.subplots_adjust(left=0.068, right=0.985, bottom=0.16, top=0.87, wspace=0.12)

    # Panel 1: Inclination sweep
    inc_specs = [
        ("I20_subcrit", r"$I_0 = 20^\circ$", cz.PAL["blue"], "-"),
        ("I60_mild", r"$I_0 = 60^\circ$", cz.PAL["green"], "--"),
        ("FID_I82_chi0", r"$I_0 = 82^\circ$ (fid.)", cz.PAL["red"], "-"),
        ("I86_high", r"$I_0 = 86^\circ$", cz.PAL["orange"], "-."),
    ]
    for k, lbl, col, ls in inc_specs:
        d = trajs[k]
        axes[0].plot(d["t"], d["e_in"], color=col, ls=ls, label=lbl)
    axes[0].set_title("Inclination threshold", pad=5)
    axes[0].set_ylabel(r"Inner eccentricity $e_{\rm in}$")
    axes[0].set_xlabel(r"Time $t\,[M]$", labelpad=2)
    axes[0].set_ylim(0.0, 1.0)
    axes[0].legend(loc="upper left", fontsize=8.2, frameon=False)

    # Panel 2: 1PN GR quenching sweep
    lbl_map = {r["name"]: r["eps_gr"] for r in summary}
    gr_specs = [
        ("GR_low_a082", rf"$\epsilon_{{\rm GR}}={lbl_map['GR_low_a082']:.2f}$", cz.PAL["green"], "-"),
        ("FID_I82_chi0", rf"$\epsilon_{{\rm GR}}={lbl_map['FID_I82_chi0']:.2f}$", cz.PAL["red"], "--"),
        ("GR_mid_a062", rf"$\epsilon_{{\rm GR}}={lbl_map['GR_mid_a062']:.2f}$", cz.PAL["blue"], "-."),
        ("GR_high_a055", rf"$\epsilon_{{\rm GR}}={lbl_map['GR_high_a055']:.2f}$", "k", ":"),
    ]
    for k, lbl, col, ls in gr_specs:
        d = trajs[k]
        axes[1].plot(d["t"], d["e_in"], color=col, ls=ls, label=lbl)
    axes[1].set_title(r"1PN pericenter quenching", pad=5)
    axes[1].set_xlabel(r"Time $t\,[M]$", labelpad=2)
    axes[1].legend(loc="upper left", fontsize=8.2, frameon=False)

    # Panel 3: SMBH Kerr spin & octupole shift
    sp_specs = [
        ("FID_I82_chi0", r"$\chi_0 = 0$", "k", "-"),
        ("SPIN_p07", r"$\chi_0 = +0.7$", cz.PAL["blue"], "--"),
        ("SPIN_m07", r"$\chi_0 = -0.7$", cz.PAL["red"], "-."),
        ("SPIN_p09", r"$\chi_0 = +0.9$", cz.PAL["yellow"], "-"),
        ("OCT_q3_I80", r"$q=1/3,\chi_0=+0.7$", cz.PAL["green"], ":"),
    ]
    for k, lbl, col, ls in sp_specs:
        d = trajs[k]
        axes[2].plot(d["t"], d["e_in"], color=col, ls=ls, label=lbl)
    axes[2].set_title("Kerr spin & octupole shifts", pad=5)
    axes[2].set_xlabel(r"Time $t\,[M]$", labelpad=2)
    axes[2].legend(loc="upper left", fontsize=8.0, frameon=False)

    for ax in axes:
        ax.set_xlim(0.0, t_end)
        ax.tick_params(which="both", direction="in", top=True, right=True)

    fig_pdf = os.path.join(fig_dir, "fig_zkl_scout.pdf")
    fig_png = os.path.join(fig_dir, "fig_zkl_scout.png")
    fig.savefig(fig_pdf)
    fig.savefig(fig_png, dpi=300)
    plt.close(fig)
    print(f"Wrote {fig_pdf} and {fig_png}")


if __name__ == "__main__":
    main()
