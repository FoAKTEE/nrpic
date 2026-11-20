#!/usr/bin/env python3
"""Second-agent check of the ES-F construction (flux_tools JOURNAL entry 6).

Written by a helper that did not build ES-F. It does not import esf_data.py, es_model.py
or fluxio.py: the density profile is re-implemented from its stated definition
(README section "ES-F": ES-1 plateau density rho0, smooth inner edge over 3-5 M, outer
edge over 52-60 M, the C-infinity step S(x) = 1/(1 + exp(1/x - 1/(1-x)))), the readers of
the table (coord/INTERFACES/spherical_id_format2.md) and of the particle file
(docs/FORMATS.md) are written here, and every closed form is derived with sympy first.

Part A (symbolic, sympy), spherical dust at rest in the slice, K^i_j = diag(KL, KT, KT),
sign convention of the code K_ij = -(1/(2 alpha)) d_t gamma_ij (zero shift):
  A1 momentum constraint on dl^2 + R(l)^2 dOmega^2  ->  KL = d(R KT)/dR for any KT;
  A2 Misner-Sharp mass m = (R/2)(1 - g^ab d_a R d_b R) on the slice with
     KT = -f (2m/R^3)^(1/2), f^2 = 1 - M/m  ->  (dR/dl)^2 = 1 - 2M/R (Schwarzschild of M),
     and the isotropic form psi = 1 + M/(2 rbar) has the same dR/dl and R_3 = 0;
  A3 Hamiltonian constraint: R_3 = 0 and 4 KL KT + 2 KT^2 = 4 D'/R^2, i.e. 16 pi rho
     exactly when D' = 4 pi R^2 rho (m = M + D is then the Misner-Sharp mass);
  A4 LTB: the metric -dtau^2 + R_r^2/(1+2E) dr^2 + R^2 dOmega^2 with
     R_tau^2 = 2m/R + 2E is dust with 8 pi rho = 2 m_r/(R^2 R_r) (Einstein tensor); on the
     initial slice (dR/dl)^2 = 1 + 2E and R_tau = -R KT give E = -M/R0 for every shell;
     cycloid and the times tau_H (R = 2m on the contracting branch), tau_0 (R = 0);
     rest mass and Misner-Sharp mass of a shell: dm = (1 + 2E)^(1/2) dmu.
Part B (numbers): the data run's table, particle file, per-tag energies, labels, growth
law and totals against these closed forms with an independent quadrature.

    check_esf_construction.py --data <ES-F data run dir> [--input <esf athinput>] [--out DIR]
"""
import argparse
import json
import math
import os
import struct
import sys
import time

import numpy as np
import sympy as sp
from scipy import integrate, optimize, special
from scipy.interpolate import CubicSpline

HERE = os.path.dirname(os.path.abspath(__file__))
M = 1.0
RHO0 = 3.718183334770104e-06      # ES-1 plateau density: es/es.json of D-20261115-170213-d2c2131
R_IN, R_IN2, R_OUT1, R_OUT = 3.0, 5.0, 52.0, 60.0
TRACER_R0 = (6.0, 10.0, 20.0, 28.0, 36.0, 40.0, 48.0, 56.0, 66.0, 78.0)


# ---------------------------------------------------------------- Part A: sympy
def christoffel(g, x):
    n = len(x)
    gi = sp.simplify(g.inv())
    G = [[[0] * n for _ in range(n)] for _ in range(n)]
    for a in range(n):
        for b in range(n):
            for c in range(n):
                G[a][b][c] = sp.simplify(sum(gi[a, d] * (sp.diff(g[d, c], x[b]) + sp.diff(g[d, b], x[c])
                                                         - sp.diff(g[b, c], x[d])) for d in range(n)) / 2)
    return gi, G


def ricci(g, x):
    n = len(x)
    gi, G = christoffel(g, x)
    Ric = sp.zeros(n, n)
    for b in range(n):
        for d in range(n):
            Ric[b, d] = sp.simplify(sum(sp.diff(G[a][b][d], x[a]) - sp.diff(G[a][b][a], x[d])
                                        + sum(G[a][a][e] * G[e][b][d] - G[a][d][e] * G[e][b][a]
                                              for e in range(n)) for a in range(n)))
    Rs = sp.simplify(sum(gi[b, d] * Ric[b, d] for b in range(n) for d in range(n)))
    return gi, G, Ric, Rs


def part_a():
    res = {}
    l, th, ph = sp.symbols("l theta phi", real=True)
    Mm, f, m = sp.symbols("M f m", positive=True)
    Rl = sp.Function("R")(l)
    g3 = sp.diag(1, Rl ** 2, Rl ** 2 * sp.sin(th) ** 2)
    x3 = (l, th, ph)
    gi3, G3, Ric3, R3 = ricci(g3, x3)
    # A1: momentum constraint D_j K^j_i - d_i K = 0 (S_i = 0: dust at rest in the slice)
    KLf, KTf = sp.Function("KL")(l), sp.Function("KT")(l)
    Kmix = sp.diag(KLf, KTf, KTf)                       # K^i_j
    trK = KLf + 2 * KTf
    mom = []
    for i in range(3):
        div = sum(sp.diff(Kmix[j, i], x3[j]) for j in range(3))
        div += sum(G3[j][j][k] * Kmix[k, i] for j in range(3) for k in range(3))
        div -= sum(G3[k][j][i] * Kmix[j, k] for j in range(3) for k in range(3))
        mom.append(sp.simplify(div - sp.diff(trK, x3[i])))
    res["A1_momentum_components"] = [str(c) for c in mom]
    KL_sol = sp.solve(sp.Eq(mom[0], 0), KLf)[0]
    res["A1_KL_solution"] = str(KL_sol)
    # with KT(l) = kt(R(l)): KL = kt + R kt'(R) = d(R kt)/dR
    kt = sp.Function("kt")
    KL_expr = sp.simplify(KL_sol.subs(sp.Derivative(KTf, l), sp.Derivative(kt(Rl), l).doit()).subs(KTf, kt(Rl)))
    target = sp.diff(Rl * kt(Rl), l) / sp.diff(Rl, l)   # d(R kt)/dR along the slice
    res["A1_KL_minus_dRKT_dR"] = str(sp.simplify(KL_expr - sp.simplify(target)))
    res["A1_theta_phi_components_zero"] = bool(mom[1] == 0 and mom[2] == 0)
    # A2: Misner-Sharp mass on the slice, code sign convention
    t = sp.symbols("t", real=True)
    al = sp.Function("alpha")(t, l)
    A = sp.Function("A")(t, l)
    Rtl = sp.Function("R")(t, l)
    g4 = sp.diag(-al ** 2, A ** 2, Rtl ** 2, Rtl ** 2 * sp.sin(th) ** 2)
    K_thth = -sp.diff(g4[2, 2], t) / (2 * al)          # zero shift
    KT_def = sp.simplify(K_thth / g4[2, 2])            # K^theta_theta
    U = sp.diff(Rtl, t) / al                           # n^a d_a R
    res["A2_KT_equals_minus_U_over_R"] = bool(sp.simplify(KT_def + U / Rtl) == 0)
    gradR2 = sp.simplify(-(sp.diff(Rtl, t) / al) ** 2 + (sp.diff(Rtl, l) / A) ** 2)
    m_MS = sp.simplify(Rtl / 2 * (1 - gradR2))
    # on the slice A = 1: Gamma = dR/dl, U = -R KT
    Gam2, KTs, Rr = sp.symbols("Gamma2 K_T R", real=True)
    m_slice = Rr / 2 * (1 + Rr ** 2 * KTs ** 2 - Gam2)
    res["A2_misner_sharp_slice"] = "m = (R/2)(1 + R^2 KT^2 - Gamma^2), Gamma = dR/dl"
    chk = sp.simplify(m_MS.subs({sp.diff(Rtl, t): -Rtl * KTs * al, A: 1}).subs(sp.diff(Rtl, l) ** 2, Gam2)
                      .subs(Rtl, Rr) - m_slice)
    res["A2_misner_sharp_form_check"] = str(chk)
    Gam2_sol = sp.solve(sp.Eq(m_slice, m), Gam2)[0]
    Gam2_f = sp.simplify(Gam2_sol.subs(KTs, -f * sp.sqrt(2 * m / Rr ** 3)))
    res["A2_Gamma2_general_f"] = str(Gam2_f)
    Gam2_esf = sp.simplify(Gam2_f.subs(f, sp.sqrt(1 - Mm / m)))
    res["A2_Gamma2_esf_minus_schw"] = str(sp.simplify(Gam2_esf - (1 - 2 * Mm / Rr)))
    # isotropic Schwarzschild: R = psi^2 rbar, dl = psi^2 drbar
    rb = sp.symbols("rbar", positive=True)
    psi = 1 + Mm / (2 * rb)
    Rb = psi ** 2 * rb
    Gam_iso = sp.diff(Rb, rb) / psi ** 2
    res["A2_iso_Gamma2_minus_schw"] = str(sp.simplify(Gam_iso ** 2 - (1 - 2 * Mm / Rb)))
    giso = sp.diag(psi ** 4, psi ** 4 * rb ** 2, psi ** 4 * rb ** 2 * sp.sin(th) ** 2)
    _, _, _, R3iso = ricci(giso, (rb, th, ph))
    res["A2_iso_R3"] = str(sp.simplify(R3iso))
    # A3: Hamiltonian constraint
    Rsym = sp.symbols("R", positive=True)
    Gam = sp.sqrt(1 - 2 * Mm / Rsym)
    R3_sub = R3.subs(sp.Derivative(Rl, (l, 2)), Gam * sp.diff(Gam, Rsym)).subs(sp.Derivative(Rl, l), Gam).subs(Rl, Rsym)
    res["A3_R3_general"] = str(R3)
    res["A3_R3_schw"] = str(sp.simplify(R3_sub))
    D = sp.Function("D")
    KT_R = -sp.sqrt(2 * D(Rsym) / Rsym ** 3)
    KL_R = sp.diff(Rsym * KT_R, Rsym)
    Kmat = sp.diag(KL_R, KT_R, KT_R)
    quad = sp.simplify(Kmat.trace() ** 2 - (Kmat * Kmat).trace())
    res["A3_K2_minus_KK"] = str(quad)
    res["A3_K2_minus_KK_minus_4Dp_over_R2"] = str(sp.simplify(quad - 4 * sp.diff(D(Rsym), Rsym) / Rsym ** 2))
    # Misner-Sharp mass of the data equals M + D
    m_data = sp.simplify(m_slice.subs({Gam2: 1 - 2 * Mm / Rr, KTs: -sp.sqrt(2 * D(Rr) / Rr ** 3)}))
    res["A3_misner_sharp_of_data_minus_M_minus_D"] = str(sp.simplify(m_data - Mm - D(Rr)))
    # A4: LTB
    tau, r = sp.symbols("tau r", real=True)
    RL = sp.Function("R")(tau, r)
    mr, Er = sp.Function("m")(r), sp.Function("E")(r)
    gL = sp.diag(-1, sp.diff(RL, r) ** 2 / (1 + 2 * Er), RL ** 2, RL ** 2 * sp.sin(th) ** 2)
    xL = (tau, r, th, ph)
    giL, _, RicL, RsL = ricci(gL, xL)
    GL = sp.simplify(giL * (RicL - gL * RsL / 2))      # G^a_b
    Rt = sp.sqrt(2 * mr / RL + 2 * Er)
    subs = {sp.Derivative(RL, (tau, 2)): -mr / RL ** 2,
            sp.Derivative(RL, tau, r): sp.diff(Rt, r),
            sp.Derivative(RL, r, tau): sp.diff(Rt, r)}
    GLs = GL.subs(subs).subs(sp.Derivative(RL, tau), Rt)
    GLs = sp.simplify(GLs)
    rho_ltb = sp.diff(mr, r) / (4 * sp.pi * RL ** 2 * sp.diff(RL, r))
    res["A4_G_tau_tau_plus_8pi_rho"] = str(sp.simplify(GLs[0, 0] + 8 * sp.pi * rho_ltb))
    off = [str(sp.simplify(GLs[a, b])) for a in range(4) for b in range(4) if not (a == 0 and b == 0)]
    res["A4_other_components_zero"] = all(o == "0" for o in off)
    # initial slice: Gamma = dR/dl = R_r / sqrt(g_rr) = sqrt(1 + 2E)
    E0 = sp.symbols("E", real=True)
    R0s = sp.symbols("R_0", positive=True)
    res["A4_E_from_Gamma"] = str(sp.solve(sp.Eq(1 + 2 * E0, 1 - 2 * Mm / R0s), E0)[0])
    # and from the energy equation with U = -R KT = f sqrt(2m/R)
    Uin = sp.sqrt(1 - Mm / m) * sp.sqrt(2 * m / R0s)
    res["A4_E_from_energy_eq"] = str(sp.simplify(sp.solve(sp.Eq(Uin ** 2, 2 * m / R0s + 2 * E0), E0)[0]))
    # cycloid R = (m/(2|E|))(1 - cos eta), tau = (m/(2|E|)^(3/2))(eta - sin eta), |E| = M/R0
    eta = sp.symbols("eta", real=True)
    aE = Mm / R0s
    Rc = m / (2 * aE) * (1 - sp.cos(eta))
    tc = m / (2 * aE) ** sp.Rational(3, 2) * (eta - sp.sin(eta))
    vel2 = sp.simplify((sp.diff(Rc, eta) / sp.diff(tc, eta)) ** 2)
    res["A4_cycloid_energy_eq"] = str(sp.simplify(vel2 - (2 * m / Rc - 2 * aE)))
    res["A4_cycloid_dRdeta_minus_sin"] = str(sp.simplify(sp.diff(Rc, eta) - m / (2 * aE) * sp.sin(eta)))
    res["A4_cycloid_dtaudeta_minus"] = str(sp.simplify(sp.diff(tc, eta) - m / (2 * aE) ** sp.Rational(3, 2) * (1 - sp.cos(eta))))
    res["A4_cycloid_start_R0"] = str(sp.simplify(Rc.subs(sp.cos(eta), 1 - 2 * Mm / m) - R0s))
    res["A4_cycloid_horizon_2m"] = str(sp.simplify(Rc.subs(sp.cos(eta), 1 - 4 * Mm / R0s) - 2 * m))
    res["A4_cycloid_Rmax_minus_mR0_over_M"] = str(sp.simplify(Rc.subs(sp.cos(eta), -1) - m * R0s / Mm))
    # dm/dmu = Gamma: dmu = rho 4 pi R^2 dl (dust at rest, W = 1), dm = 4 pi R^2 rho dR, dR/dl = Gamma
    rh, Gs = sp.symbols("rho Gamma", positive=True)
    dmu_dR = 4 * sp.pi * Rsym ** 2 * rh / Gs
    dm_dR = 4 * sp.pi * Rsym ** 2 * rh
    res["A4_dm_dmu"] = str(sp.simplify(dm_dR / dmu_dR))
    res["A4_dm_dmu_esf"] = str(sp.sqrt(1 + 2 * sp.solve(sp.Eq(1 + 2 * E0, 1 - 2 * Mm / R0s), E0)[0]))
    # the closed forms used in part B, as functions
    Dn, Dpn = sp.symbols("D Dp", positive=True)
    KTn = -sp.sqrt(2 * Dn / Rsym ** 3)
    KLn = sp.diff(Rsym * (-sp.sqrt(2 * D(Rsym) / Rsym ** 3)), Rsym).subs(sp.Derivative(D(Rsym), Rsym), Dpn).subs(D(Rsym), Dn)
    res["closed_KT"] = str(KTn)
    res["closed_KL"] = str(sp.simplify(KLn))
    fun = dict(KT=sp.lambdify((Rsym, Dn), KTn, "numpy"),
               KL=sp.lambdify((Rsym, Dn, Dpn), KLn, "numpy"),
               ham=sp.lambdify((Rsym, Dn, Dpn), sp.simplify(quad.subs(sp.Derivative(D(Rsym), Rsym), Dpn).subs(D(Rsym), Dn)), "numpy"))
    return res, fun


# ---------------------------------------------------------------- Part B: numbers
def S(x):
    x = np.asarray(x, float)
    out = np.where(x >= 1.0, 1.0, 0.0)
    mid = (x > 0) & (x < 1)
    xm = x[mid]
    out[mid] = special.expit(1.0 / (1.0 - xm) - 1.0 / xm)
    return out


def rho(R):
    R = np.asarray(R, float)
    return RHO0 * S((R - R_IN) / (R_IN2 - R_IN)) * (1.0 - S((R - R_OUT1) / (R_OUT - R_OUT1)))


def rho1(R):
    return float(rho(np.array([R]))[0])


def D_quad(R):
    if R <= R_IN:
        return 0.0
    pts = [p for p in (R_IN2, R_OUT1, R_OUT) if R_IN < p < R]
    v, _ = integrate.quad(lambda s: 4 * math.pi * s * s * rho1(s), R_IN, min(R, R_OUT), points=pts or None,
                          epsabs=1e-17, epsrel=1e-13, limit=400)
    return v


def D_grid(Rg):
    """Cumulative D on an increasing grid by quad over each interval."""
    out = np.zeros(Rg.size)
    acc = 0.0
    prev = R_IN
    for i, R in enumerate(Rg):
        Rc = min(max(R, R_IN), R_OUT)
        if Rc > prev:
            pts = [p for p in (R_IN2, R_OUT1) if prev < p < Rc]
            v, _ = integrate.quad(lambda s: 4 * math.pi * s * s * rho1(s), prev, Rc, points=pts or None,
                                  epsabs=1e-18, epsrel=1e-13, limit=200)
            acc += v
            prev = Rc
        out[i] = acc
    return out


def areal(rb):
    return rb * (1.0 + M / (2.0 * rb)) ** 2


def rbar_of_R(R):
    return 0.5 * ((R - M) + np.sqrt(R * R - 2 * M * R))


def times(R0, m):
    """tau_H and tau_0 from the cycloid of part A (E = -M/R0, start on the expanding branch)."""
    T = m / (2 * M / R0) ** 1.5
    eta0 = np.arccos(np.clip(1 - 2 * M / m, -1, 1))
    etaH = 2 * np.pi - np.arccos(np.clip(1 - 4 * M / R0, -1, 1))
    base = eta0 - np.sin(eta0)
    return T * ((etaH - np.sin(etaH)) - base), T * (2 * np.pi - base)


def tauH_quad(R0, m):
    """Independent: proper time from R0 out to R_max and back in to R = 2m by quadrature."""
    Rmax = m * R0 / M
    v = lambda R: 1.0 / math.sqrt(max(2 * m / R - 2 * M / R0, 1e-300))
    up, _ = integrate.quad(v, R0, Rmax, epsabs=1e-12, epsrel=1e-12, limit=400)
    dn, _ = integrate.quad(v, 2 * m, Rmax, epsabs=1e-12, epsrel=1e-12, limit=400)
    return up + dn


def read_tab(path):
    hdr = {}
    with open(path) as fh:
        for line in fh:
            if not line.startswith("#"):
                break
            if "=" in line:
                k, v = line[1:].split("=", 1)
                hdr[k.strip()] = v.strip()
    a = np.loadtxt(path, comments="#")
    return hdr, a


def read_nrp(path):
    with open(path, "rb") as fh:
        raw = fh.read()
    assert raw[:8] == b"NRPIC001", raw[:8]
    n = struct.unpack("<q", raw[8:16])[0]
    rec = np.frombuffer(raw, "<f8", 7 * n, 16).reshape(n, 7)
    spec = np.frombuffer(raw, "<i4", n, 16 + 56 * n)
    assert len(raw) == 16 + 60 * n
    return n, rec, spec


def part_b(data, fun, inp):
    out = {}
    hdr, tab = read_tab(os.path.join(data, "esf.tab"))
    out["table_header"] = {k: hdr[k] for k in ("format", "columns", "exterior") if k in hdr}
    rb, u, KL, KT, al, br = tab.T
    dr = rb[1] - rb[0]
    out["table_rows"] = int(rb.size)
    out["table_uniform"] = float(np.max(np.abs(rb - dr * np.arange(rb.size))))
    out["table_u_max_abs"] = float(np.max(np.abs(u)))
    out["table_betar_max_abs"] = float(np.max(np.abs(br)))
    out["table_rbar_max"] = float(rb[-1])
    out["mesh_corner_rbar"] = 192.0 * math.sqrt(3.0)
    inner = rb < 0.5 * M
    out["table_inner_sheet_K_max_abs"] = float(max(np.max(np.abs(KL[inner])), np.max(np.abs(KT[inner]))))
    pos = rb > 0
    out["table_alpha_minus_psi^-2_max"] = float(np.max(np.abs(al[pos] - (1 + M / (2 * rb[pos])) ** -2)))
    outer = rb >= 0.5 * M
    R = np.where(outer, areal(np.where(rb > 0, rb, 1.0)), 0.0)
    o = np.where(outer)[0]
    Dg = D_grid(R[o])
    Dp = 4 * math.pi * R[o] ** 2 * rho(R[o])
    KT_ex = np.where(Dg > 0, fun["KT"](R[o], np.maximum(Dg, 1e-300)), 0.0)
    with np.errstate(divide="ignore", invalid="ignore"):
        KL_ex = np.where(Dg > 0, fun["KL"](R[o], np.maximum(Dg, 1e-300), Dp), 0.0)
    scale = np.max(np.abs(KT_ex))
    eKT = np.abs(KT[o] - KT_ex)
    eKL = np.abs(KL[o] - KL_ex)
    out["table_KT_maxabs_err_over_maxKT"] = float(eKT.max() / scale)
    out["table_KL_maxabs_err_over_maxKT"] = float(eKL.max() / scale)
    nz = np.abs(KT_ex) > 1e-12 * scale
    out["table_KT_max_rel_err_where_nonzero"] = float(np.max(eKT[nz] / np.abs(KT_ex[nz])))
    nzl = np.abs(KL_ex) > 1e-6 * scale
    out["table_KL_max_rel_err_where_above_1e-6"] = float(np.max(eKL[nzl] / np.abs(KL_ex[nzl])))
    # sampled radii with a direct quad each
    samp = []
    for Rt in (2.5, 3.2, 3.5, 4.0, 4.5, 5.0, 7.0, 10.0, 20.0, 30.0, 40.0, 52.5, 55.0, 58.0, 59.5, 61.0, 100.0, 200.0, 330.0):
        k = int(np.argmin(np.abs(R - Rt)))
        Rk = float(R[k])
        Dk = D_quad(Rk)
        Dpk = 4 * math.pi * Rk * Rk * rho1(Rk)
        kt = float(fun["KT"](Rk, Dk)) if Dk > 0 else 0.0
        kl = float(fun["KL"](Rk, Dk, Dpk)) if Dk > 0 else 0.0
        hres = float(4 * KL[k] * KT[k] + 2 * KT[k] ** 2 - 16 * math.pi * rho1(Rk))
        samp.append(dict(rbar=float(rb[k]), R=Rk, D=Dk, KT_tab=float(KT[k]), KT_exact=kt,
                         KL_tab=float(KL[k]), KL_exact=kl,
                         dKT=float(KT[k] - kt), dKL=float(KL[k] - kl),
                         ham_residual_over_16pi_rho0=hres / (16 * math.pi * RHO0),
                         U_over_HR=float(math.sqrt(2 * Dk / Rk) / (math.sqrt(8 * math.pi * RHO0 / 3) * Rk)) if Dk > 0 else 0.0))
    out["table_samples"] = samp
    # Hamiltonian constraint at every row with the table's own KL, KT
    ham = 4 * KL[o] * KT[o] + 2 * KT[o] ** 2 - 16 * math.pi * rho(R[o])
    out["table_ham_residual_max_over_16pi_rho0"] = float(np.max(np.abs(ham)) / (16 * math.pi * RHO0))
    # momentum constraint by differences of the table: KL - d(R KT)/dR, d/dR = (d/drbar)/(dR/drbar)
    RKT = R * KT
    d4 = np.full(rb.size, np.nan)
    d4[2:-2] = (-RKT[4:] + 8 * RKT[3:-1] - 8 * RKT[1:-3] + RKT[:-4]) / (12 * dr)
    dRdrb = np.where(rb > 0, (1 + M / (2 * np.where(rb > 0, rb, 1))) * (1 - M / (2 * np.where(rb > 0, rb, 1))), 1)
    sel = outer & (R > 2.2) & np.isfinite(d4)
    mres = KL[sel] - d4[sel] / dRdrb[sel]
    out["table_mom_residual_fd4_max_over_maxKT"] = float(np.max(np.abs(mres)) / scale)
    res_rows = dict(R=R[o], KT=KT[o], KL=KL[o], KT_ex=KT_ex, KL_ex=KL_ex, ham=ham, eKT=eKT, eKL=eKL,
                    Rm=R[sel], mres=mres, scale=scale)
    # particles
    n, rec, spec = read_nrp(os.path.join(data, "esf.nrp"))
    x, uu, mm = rec[:, :3], rec[:, 3:6], rec[:, 6]
    out["n_particles"] = int(n)
    out["u_max_abs"] = float(np.max(np.abs(uu)))
    out["species_set"] = sorted(set(int(s) for s in np.unique(spec)))
    rbp = np.linalg.norm(x, axis=1)
    Rp = areal(rbp)
    ntr = 140
    trR = np.repeat(TRACER_R0, 14)
    out["tracers_mass_set"] = sorted(set(float(v) for v in mm[:ntr]))
    out["tracers_R_max_rel_err"] = float(np.max(np.abs(Rp[:ntr] / trR - 1)))
    xd, md, Rd, rbd = x[ntr:], mm[ntr:], Rp[ntr:], rbp[ntr:]
    h = 1.0
    out["dust_lattice_offset_max"] = float(np.max(np.abs(xd / h - 0.5 - np.round(xd / h - 0.5))))
    m_ex = rho(Rd) * (1 + M / (2 * rbd)) ** 6 * h ** 3
    out["dust_mass_max_rel_err"] = float(np.max(np.abs(md / m_ex - 1)))
    out["dust_R_range"] = [float(Rd.min()), float(Rd.max())]
    # my own enumeration of the lattice points that carry dust
    k = (np.arange(-62, 62) + 0.5) * h
    X, Y, Z = np.meshgrid(k, k, k, indexing="ij")
    rr = np.sqrt(X * X + Y * Y + Z * Z)
    ok = rr >= 0.5 * M
    RR = np.where(ok, areal(np.maximum(rr, 1e-300)), 0)
    ok &= (RR > R_IN) & (RR < R_OUT)
    ok[ok] &= rho(RR[ok]) > 0
    out["dust_count_mine"] = int(ok.sum())
    out["dust_count_file"] = int(xd.shape[0])
    mine = np.round(np.stack([X[ok], Y[ok], Z[ok]], 1) * 2).astype(np.int64)
    theirs = np.round(xd * 2).astype(np.int64)
    key = lambda a: np.sort(a[:, 0] * 10 ** 8 + a[:, 1] * 10 ** 4 + a[:, 2])
    out["dust_positions_identical_set"] = bool(mine.shape == theirs.shape and np.array_equal(key(mine), key(theirs)))
    # per-tag energies
    EK = np.load(os.path.join(data, "energy_by_tag.npy"))
    EK_ex = np.sqrt(1 - 2 * M / np.concatenate([trR, Rd]))
    out["energy_by_tag_len"] = int(EK.size)
    out["energy_by_tag_max_abs_err"] = float(np.max(np.abs(EK - EK_ex)))
    # labels (D from a dense cumulative grid; direct quad on a sample)
    lab = np.load(os.path.join(data, "esf_labels.npz"))
    Rg = np.linspace(R_IN, R_OUT, 57001)
    Dgd = D_grid(Rg)
    spl = CubicSpline(Rg, Dgd)
    R0 = lab["R0"]
    out["labels_R0_max_rel_err"] = float(np.max(np.abs(R0 / np.concatenate([trR, Rd]) - 1)))
    m_lab_ex = M + np.where(R0 <= R_IN, 0.0, np.where(R0 >= R_OUT, Dgd[-1], spl(np.clip(R0, R_IN, R_OUT))))
    out["labels_m_max_abs_err"] = float(np.max(np.abs(lab["m_label"] - m_lab_ex)))
    rng = np.random.default_rng(20261120)
    pick = rng.choice(R0.size, 300, replace=False)
    out["labels_m_quad_sample_max_abs_err"] = float(max(abs(lab["m_label"][i] - (M + D_quad(float(R0[i])))) for i in pick))
    out["labels_rest_equal_file"] = bool(np.array_equal(lab["rest"], mm))
    tH, t0 = times(R0, m_lab_ex)
    out["labels_tauH_max_rel_err"] = float(np.max(np.abs(lab["tauH"] / tH - 1)))
    out["labels_tau0_max_rel_err"] = float(np.max(np.abs(lab["tau0"] / t0 - 1)))
    # closed form against direct quadrature of the cycloid's energy equation
    cq = []
    for Rt in TRACER_R0 + (3.05, 3.5, 4.5, 8.0, 15.0, 25.0, 33.0, 45.0, 53.0, 59.0):
        mt = M + D_quad(Rt)
        a1 = float(times(np.array([Rt]), np.array([mt]))[0][0])
        a2 = tauH_quad(Rt, mt)
        cq.append(dict(R0=Rt, m=mt, tauH_closed=a1, tauH_quad=a2, rel=a2 / a1 - 1))
    out["tauH_closed_vs_quad"] = cq
    js = json.load(open(os.path.join(data, "esf.json")))
    out["json_tracer_tauH_max_rel_err"] = float(max(abs(js["tracer_tauH"][str(r)] / c["tauH_closed"] - 1)
                                                for r, c in zip(TRACER_R0, cq)))
    # totals
    Dtot = Dgd[-1]
    out["Dtot_mine"] = float(Dtot)
    out["Dtot_json"] = js["Dtot"]
    out["Dtot_quad_direct"] = D_quad(R_OUT)
    rest_c, _ = integrate.quad(lambda s: 4 * math.pi * s * s * rho1(s) / math.sqrt(1 - 2 * M / s), R_IN, R_OUT,
                               points=[R_IN2, R_OUT1], epsabs=1e-16, epsrel=1e-13, limit=400)
    out["continuum_rest_mine"] = rest_c
    out["continuum_rest_json"] = js["continuum_rest_mass"]
    out["lattice_rest"] = float(md.sum())
    out["lattice_sum_mEK"] = float(np.sum(md * EK[ntr:]))
    out["lattice_sum_mEK_over_Dtot_minus_1"] = float(np.sum(md * EK[ntr:]) / Dtot - 1)
    out["lattice_rest_over_continuum_minus_1"] = float(md.sum() / rest_c - 1)
    # growth law: my M_AH(tau) by root finding tau_H(R0) = tau
    gcsv = np.loadtxt(os.path.join(data, "esf_growth.csv"), delimiter=",", skiprows=1)
    mg = M + spl(np.clip(gcsv[:, 0], R_IN, R_OUT))
    tHg, t0g = times(gcsv[:, 0], mg)
    out["growth_csv_m_max_abs_err"] = float(np.max(np.abs(gcsv[:, 1] - mg)))
    out["growth_csv_tauH_max_rel_err"] = float(np.max(np.abs(gcsv[:, 2] / tHg - 1)))
    out["growth_csv_tau0_max_rel_err"] = float(np.max(np.abs(gcsv[:, 3] / t0g - 1)))
    out["growth_csv_Rmax_max_rel_err"] = float(np.max(np.abs(gcsv[:, 4] / (mg * gcsv[:, 0] / M) - 1)))
    Rfine = np.linspace(R_IN * 1.00001, R_OUT, 20001)
    tHf, _ = times(Rfine, M + spl(Rfine))
    out["tauH_monotonic_mine"] = bool(np.all(np.diff(tHf) > 0))
    gm = {}
    for tt in (25, 50, 100, 150, 200, 250, 300, 400, 600):
        g = lambda R: float(times(np.array([R]), np.array([M + spl(R)]))[0][0]) - tt
        Rr = optimize.brentq(g, R_IN * 1.00001, R_OUT, xtol=1e-13)
        gm[f"tau={tt}"] = dict(mine=float(M + spl(Rr)), json=js["growth"][f"tau={tt}"],
                               diff=float(js["growth"][f"tau={tt}"] - (M + spl(Rr))), R0=float(Rr))
    out["growth_law"] = gm
    # input file
    if inp and os.path.exists(inp):
        txt = open(inp).read()
        kv = {}
        for line in txt.splitlines():
            s = line.split("#")[0].strip()
            if "=" in s:
                a_, b_ = s.split("=", 1)
                kv[a_.strip()] = b_.strip()
        out["input"] = {k: kv.get(k) for k in ("comp0_type", "comp0_file", "comp1_type", "comp1_mass", "lapse",
                                                "shift", "particle_file", "metric_drvts", "ah_exc_factor")}
    plot_rows = dict(rows=res_rows, Rd=Rd, merr=md / m_ex - 1, eerr=EK - EK_ex, gcsv=gcsv, tHg=tHg, mg=mg, cq=cq)
    return out, plot_rows


def figure(outdir, pr):
    sys.path.insert(0, HERE)
    import figstyle
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    figstyle.use_style()
    fig, ax = plt.subplots(2, 3, figsize=(figstyle.FULL_WIDTH, 5.2))
    r = pr["rows"]
    s = (r["R"] > 2.0) & (r["R"] < 400)
    a = ax[0, 0]
    a.loglog(r["R"][s], np.abs(r["KT_ex"][s]) + 1e-30, color=figstyle.PAL["blue"], label=r"$|K_T|$ closed form")
    a.loglog(r["R"][s][::40], np.abs(r["KT"][s][::40]) + 1e-30, ".", ms=2, color=figstyle.PAL["red"], label="table")
    a.loglog(r["R"][s], np.abs(r["KL_ex"][s]) + 1e-30, color=figstyle.PAL["green"], label=r"$|K_L|$ closed form")
    a.loglog(r["R"][s][::40], np.abs(r["KL"][s][::40]) + 1e-30, ".", ms=2, color=figstyle.PAL["orange"], label="table")
    a.set_ylim(1e-7, 1e-1)
    a.set_xlabel(r"areal radius $R\ [M]$")
    a.legend(fontsize=6, ncol=1)
    a = ax[0, 1]
    a.semilogy(r["R"][s], r["eKT"][s] / r["scale"] + 1e-22, color=figstyle.PAL["red"], label=r"$K_T$")
    a.semilogy(r["R"][s], r["eKL"][s] / r["scale"] + 1e-22, color=figstyle.PAL["orange"], label=r"$K_L$")
    a.set_xscale("log")
    a.set_ylim(1e-21, 1e-10)
    a.set_xlabel(r"$R\ [M]$")
    a.set_ylabel(r"|table $-$ closed form| / max$|K_T|$")
    a.legend(fontsize=7)
    a = ax[0, 2]
    a.semilogy(r["R"][s], np.abs(r["ham"][s]) / (16 * math.pi * RHO0) + 1e-22, color=figstyle.PAL["red"],
               label=r"$|4K_LK_T+2K_T^2-16\pi\rho|/16\pi\rho_0$")
    sm = r["Rm"] < 400
    a.semilogy(r["Rm"][sm], np.abs(r["mres"][sm]) / r["scale"] + 1e-22, color=figstyle.PAL["blue"],
               label=r"$|K_L-d(RK_T)/dR|$ (4th-order diff.)/max$|K_T|$")
    a.set_xscale("log")
    a.set_ylim(1e-20, 1e-4)
    a.set_xlabel(r"$R\ [M]$")
    a.legend(fontsize=6)
    a = ax[1, 0]
    a.plot(pr["Rd"][::7], pr["merr"][::7], ",", color=figstyle.PAL["red"])
    a.set_xlabel(r"particle $R_0\ [M]$")
    a.set_ylabel(r"$m/(\rho\psi^6h^3)-1$")
    a = ax[1, 1]
    a.plot(pr["Rd"][::7], pr["eerr"][140::7], ",", color=figstyle.PAL["red"])
    a.set_xlabel(r"particle $R_0\ [M]$")
    a.set_ylabel(r"$E_K-(1-2M/R_0)^{1/2}$")
    a = ax[1, 2]
    g = pr["gcsv"]
    a.plot(pr["tHg"], pr["mg"], color=figstyle.PAL["blue"], label=r"mine: $m(R_0)$ at $\tau_H(R_0)$")
    a.plot(g[::60, 2], g[::60, 1], ".", ms=3, color=figstyle.PAL["red"], label="esf_growth.csv")
    for c in pr["cq"][:4]:
        a.axvline(c["tauH_quad"], **figstyle.MASK_LINE)
    a.set_xlim(0, 700)
    a.set_ylim(0.99, 1.65)
    a.set_xlabel(r"$\tau_H\ [M]$")
    a.set_ylabel(r"$M_{\rm AH}\ [M]$")
    a.legend(fontsize=6)
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.09, top=0.97, wspace=0.42, hspace=0.32)
    figstyle.save(fig, os.path.join(outdir, "check_esf_construction"))
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--input", default=os.path.join(HERE, "inputs", "esf_dx8.athinput"))
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    t0 = time.time()
    resA, fun = part_a()
    tA = time.time() - t0
    resB, pr = part_b(a.data, fun, a.input)
    figure(a.out, pr)
    res = dict(part_A=resA, part_B=resB, wall_s=dict(A=tA, total=time.time() - t0))
    with open(os.path.join(a.out, "check_esf_construction.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
