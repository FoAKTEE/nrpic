#!/usr/bin/env python3
"""Knudsen number of each near-threshold model as a function of the cross-section per unit
mass, with the relativistic collision rate (JOURNAL.md, Test 3; CONVERSION.md).

    python3 knudsen.py --out DIR [--N 10000]

Units G = c = 1, ADM mass M = 1. sigma~ = (sigma/m)/M.

    Gamma(r)  = rho0 (sigma/m) <v_Mol>,  v_Mol = [(eps1 eps2 - q1.q2)^2 - 1]^{1/2}/(eps1 eps2)
    l(r)      = <|q|/eps> / Gamma                         (mean free path)
    lambda(r) = 1/(rho0 sigma/m)                           (astro-ph/0110561 eq. lambda_SIDM, l. 388)
    H(r)      = [v1^2/(4 pi rho0)]^{1/2}, v1^2 = (p + 2 p_T)/(3 rho0)   (eq. scaleheight)
    t_d       = H/v1 = (4 pi rho0)^{-1/2}                  (line 408), proper time at r
    Kn        = l_c/H_c,  nu_c = Gamma_c t_d,c             (c: centre; shells: rho0 peak)

Kn sigma~ and nu_c Kn are properties of the model alone. <v_Mol> is computed by a
deterministic quadrature for isotropic models (closed-form direction average) and by
Monte Carlo over pairs drawn with the package's sampler for every model.
"""

import argparse
import json
import math
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np  # noqa: E402
from scipy.stats import beta as beta_dist  # noqa: E402

import evstatic as ev  # noqa: E402
import models  # noqa: E402

KN_LIST = [10.0, 3.0, 1.0, 0.3, 0.1, 0.03, 0.01]

# constants for the physical conversion [BACKGROUND]: CODATA 2018 G and c (scipy.constants),
# IAU 2015 Resolution B3 nominal solar mass parameter GM_sun = 1.3271244e20 m^3 s^-2
G_CGS = 6.67430e-8
C_CGS = 2.99792458e10
GMSUN_CGS = 1.3271244e26


def sigma_tilde_per_cgs(M_in_Msun):
    """sigma~ for sigma/m = 1 cm^2/g at ADM mass M: c^4/(G^2 M) in g/cm^2."""
    return C_CGS ** 4 / (G_CGS * GMSUN_CGS * M_in_Msun)


# ----------------------------------------------------------------------------
# Moller relative velocity
# ----------------------------------------------------------------------------
def _Gx(X):
    X = np.maximum(X, 1.0)
    return X * np.sqrt(X * X - 1.0) - np.arccosh(X)


def dir_avg_F(e1, q1, e2, q2):
    """(1/2) int_{-1}^{1} [(e1 e2 - q1 q2 mu)^2 - 1]^{1/2} dmu (isotropic directions)."""
    a = e1 * e2
    b = q1 * q2
    small = b < 1e-7 * a
    bb = np.where(small, 1.0, b)
    val = (_Gx(a + bb) - _Gx(a - bb)) / (4.0 * bb)
    return np.where(small, np.sqrt(np.maximum(a * a - 1.0, 0.0)), val)


def eps_quadrature(md, r):
    """Nodes eps_i and normalised weights p_i of the conditional eps distribution at areal
    radius r (Gauss-Jacobi in t with the endpoint powers in the weight)."""
    fam = md.fam
    y = float(md._state(np.array([r]))[0][0])
    rp = r / md.Mscale
    e = math.exp(y)
    emin = math.sqrt(1.0 + fam.L0 / (rp * rp)) if fam.L0 else 1.0
    D = e - emin
    t, W = ev._jacobi01(fam.a, fam.l + 0.5, 96)
    R = ev._eps_R(fam, t[None, :], np.array([D]), np.array([e]), np.array([emin]))[0]
    p = W * R
    return emin + D * t, p / p.sum()


def vmol_iso(md, r):
    """(<v_Mol>, <|q|/eps>) at areal radius r for an isotropic model, by quadrature."""
    eps, p = eps_quadrature(md, r)
    q = np.sqrt(np.maximum(eps * eps - 1.0, 0.0))
    F = dir_avg_F(eps[:, None], q[:, None], eps[None, :], q[None, :])
    vm = float(np.sum(p[:, None] * p[None, :] * F / (eps[:, None] * eps[None, :])))
    return vm, float(np.sum(p * q / eps))


def local_momenta(md, r, K, rng):
    """K orthonormal momenta (w, v_t cos phi, v_t sin phi) of the distribution at radius r
    (the sampler's conditional draws at fixed r)."""
    fam = md.fam
    y = float(md._state(np.array([r]))[0][0])
    rp = r / md.Mscale
    e = math.exp(y)
    emin = math.sqrt(1.0 + fam.L0 / (rp * rp)) if fam.L0 else 1.0
    D = e - emin
    U = rng.random((K, 3))
    eps = ev._invert_eps(fam, U[:, 0], np.full(K, D), np.full(K, e), np.full(K, emin))
    c = 2.0 * U[:, 1] - 1.0 if fam.l == 0 else 2.0 * beta_dist.ppf(U[:, 1], fam.l + 1, fam.l + 1) - 1.0
    d2 = np.maximum(eps * eps - emin * emin, 0.0)
    w = c * np.sqrt(d2)
    vt = np.sqrt(np.maximum(emin * emin - 1.0 + d2 * (1.0 - c * c), 0.0))
    ph = 2 * math.pi * U[:, 2]
    q = np.stack([w, vt * np.cos(ph), vt * np.sin(ph)], axis=1)
    return q, eps


def vmol_mc(md, r, K, rng):
    """Monte Carlo <v_Mol> over K independent pairs, its standard error, and <|q|/eps>."""
    q1, e1 = local_momenta(md, r, K, rng)
    q2, e2 = local_momenta(md, r, K, rng)
    X = e1 * e2 - np.sum(q1 * q2, axis=1)
    v = np.sqrt(np.maximum(X * X - 1.0, 0.0)) / (e1 * e2)
    sp = np.concatenate([np.linalg.norm(q1, axis=1) / e1, np.linalg.norm(q2, axis=1) / e2])
    return float(v.mean()), float(v.std(ddof=1) / math.sqrt(K)), float(sp.mean())


# ----------------------------------------------------------------------------
def unit_tests(rng):
    """Prediction 1: closed-form direction average against direct sampling; Newtonian limit."""
    out = {}
    worst = 0.0
    for e1, e2 in ((1.2, 1.7), (1.01, 3.0), (2.5, 2.5)):
        q1, q2 = math.sqrt(e1 * e1 - 1), math.sqrt(e2 * e2 - 1)
        mu = rng.uniform(-1, 1, 400000)
        mc = np.sqrt((e1 * e2 - q1 * q2 * mu) ** 2 - 1)
        cf = float(dir_avg_F(np.array(e1), q1, np.array(e2), q2))
        z = abs(mc.mean() - cf) / (mc.std() / math.sqrt(len(mu)))
        worst = max(worst, z)
    out["direction_average_max_z"] = worst
    q = 1e-3
    e = math.sqrt(1 + q * q)
    v = float(dir_avg_F(np.array(e), q, np.array(e), q)) / (e * e)
    out["newtonian_equal_speeds_ratio"] = v / q        # -> 4/3
    out["pass"] = bool(worst < 4.0 and abs(v / q / (4 / 3) - 1) < 1e-5)
    return out


def core_radius(md):
    fam = md.fam
    if fam.L0 == 0:
        return md.r_start * 10
    r = np.linspace(md.r_in, md.R, 4001)[1:-1]
    n = md.matter_areal(r, ("n",))["n"]
    return float(r[np.argmax(n)])


def proper_half_mass_radius(md):
    from scipy.optimize import brentq
    from scipy.integrate import quad
    rh = brentq(lambda v: md.enclosed_fraction_areal(v)[0] - 0.5, md.r_in + 1e-12, md.R)
    # proper radial distance from the centre (or the inner edge) to rh
    ell = quad(lambda v: 1.0 / math.sqrt(1.0 - 2.0 * md._state(np.array([v]))[1][0] / v)
               if v > 0 else 1.0, md.r_in, rh, limit=200)[0]
    return rh, ell


def model_conversion(spec, N, rng, Kc=200000, Kprof=20000, nprof=40):
    md = ev.Equilibrium(models.FAMILIES[spec["family"]], spec["y0"])
    iso = md.fam.l == 0 and md.fam.L0 == 0
    rc = core_radius(md)
    mo = md.matter_areal(np.array([rc]))
    rho0, rho, p, pT = (float(mo[k][0]) for k in ("n", "rho", "p", "pT"))
    alpha_core = float(md.E0 * math.exp(-md._state(np.array([rc]))[0][0]))
    v1 = math.sqrt((p + 2 * pT) / (3 * rho0))
    H = math.sqrt(v1 * v1 / (4 * math.pi * rho0))
    td = H / v1
    vm_mc, vm_err, vs_mc = vmol_mc(md, rc, Kc, rng)
    if iso:
        vm_q, vs_q = vmol_iso(md, rc)
        vm, vs = vm_q, vs_q
    else:
        vm_q = vs_q = None
        vm, vs = vm_mc, vs_mc
    # Kn sigma~ = l_c sigma~/H_c with l_c = vs/(rho0 sigma~ vm)
    Kn_sig = vs / (rho0 * vm * H)
    nu_Kn = (vs / v1)                       # nu_c * Kn
    # radial profile of alpha Gamma / sigma~ and the particle average (coordinate time)
    U = (np.arange(nprof) + 0.5) / nprof
    from scipy.optimize import brentq
    rq = np.array([brentq(lambda v: md.enclosed_fraction_areal(v)[0] - u, md.r_in + 1e-12, md.R,
                          xtol=1e-12) for u in U])
    prof = []
    for r in rq:
        if iso:
            vmr, vsr = vmol_iso(md, r)
        else:
            vmr, _, vsr = vmol_mc(md, r, Kprof, rng)
        n_r = float(md.matter_areal(np.array([r]), ("n",))["n"][0])
        al = float(md.E0 * math.exp(-md._state(np.array([r]))[0][0]))
        prof.append((r, n_r, vmr, vsr, al))
    prof = np.array(prof)
    # <alpha Gamma>_N / sigma~ = mean over equal-mass quantiles of alpha rho0 <v_Mol>
    aG = float(np.mean(prof[:, 4] * prof[:, 1] * prof[:, 2]))
    nu_bar_Kn = aG * (td / alpha_core) * Kn_sig        # nu_bar * Kn, per coordinate t_d
    rh, ell_h = proper_half_mass_radius(md)
    M0 = md.M0
    rows = []
    for Kn in KN_LIST:
        sig = Kn_sig / Kn
        lc = Kn * H
        nu_c = nu_Kn / Kn
        nu_bar = nu_bar_Kn / Kn
        mp = M0 / N
        n_p = rho0 / mp                                   # macroparticles per proper volume
        d_c = n_p ** (-1.0 / 3.0)
        rows.append(dict(Kn=Kn, sigma_tilde=sig, l_c=lc, nu_c=nu_c, nu_bar=nu_bar,
                         pair_events_per_td_N=0.5 * N * nu_bar,
                         sigma_macro_M2=sig * mp, d_c=d_c, l_over_d=lc / d_c,
                         N_in_mfp_sphere=4 * math.pi / 3 * lc ** 3 * n_p,
                         Kn_R=lc / md.R, Kn_halfmass=lc / ell_h,
                         sigma_over_m_cgs_M1Msun=sig / sigma_tilde_per_cgs(1.0),
                         sigma_over_m_cgs_M1e9Msun=sig / sigma_tilde_per_cgs(1e9)))
    res = dict(tag=spec["tag"], family=spec["family"], y0=spec["y0"], role=spec["role"],
               isotropic=iso, r_core_areal=rc, rho0_c=rho0, rho_c=rho, p_c=p, pT_c=pT,
               v1_c=v1, H_c=H, t_d_proper=td, alpha_core=alpha_core, t_d_coord=td / alpha_core,
               vmol_c=vm, vmol_c_mc=vm_mc, vmol_c_mc_err=vm_err, vmol_c_quad=vm_q,
               mean_speed_c=vs, mean_speed_c_mc=vs_mc,
               l_over_lambdaBSI=vs / vm, Kn_times_sigma_tilde=Kn_sig, nu_c_times_Kn=nu_Kn,
               nu_bar_times_Kn=nu_bar_Kn, R_areal=md.R, r_half_areal=rh, half_mass_proper=ell_h,
               M0=M0, N=N, rows=rows,
               profile=dict(r_areal=prof[:, 0].tolist(), rho0=prof[:, 1].tolist(),
                            vmol=prof[:, 2].tolist(), mean_speed=prof[:, 3].tolist(),
                            alpha=prof[:, 4].tolist(),
                            rbar=md.rbar_of(prof[:, 0]).tolist()))
    if iso:
        res["mc_vs_quad_z"] = abs(vm_mc - vm_q) / vm_err
    return res


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--N", type=int, default=10000)
    p.add_argument("--seed", type=int, default=7)
    a = p.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rng = np.random.default_rng(a.seed)
    ut = unit_tests(rng)
    print("unit tests:", ut, flush=True)
    allres = []
    for spec in models.model_set():
        r = model_conversion(spec, a.N, rng)
        allres.append(r)
        k1 = next(x for x in r["rows"] if x["Kn"] == 1.0)
        print(f"{r['tag']}: v1_c = {r['v1_c']:.4f}, H_c = {r['H_c']:.4f} M, t_d = {r['t_d_proper']:.4f} M, "
              f"<v> = {r['mean_speed_c']:.4f}, <v_Mol> = {r['vmol_c']:.4f} "
              f"(mc {r['vmol_c_mc']:.4f} +- {r['vmol_c_mc_err']:.4f}), l/lambda = {r['l_over_lambdaBSI']:.4f}, "
              f"Kn*sig = {r['Kn_times_sigma_tilde']:.4g}, nu_c*Kn = {r['nu_c_times_Kn']:.4f}, "
              f"nu_bar*Kn = {r['nu_bar_times_Kn']:.4f}; Kn=1: sigma~ = {k1['sigma_tilde']:.4g}, "
              f"l/d = {k1['l_over_d']:.3g}", flush=True)
    out = dict(unit_tests=ut, Kn_list=KN_LIST, N=a.N,
               constants=dict(G_cgs=G_CGS, c_cgs=C_CGS, GMsun_cgs=GMSUN_CGS,
                              sigma_tilde_for_1cm2g_at_1Msun=sigma_tilde_per_cgs(1.0)),
               models=allres)
    with open(os.path.join(a.out, "knudsen.json"), "w") as f:
        json.dump(out, f, indent=1)
    return 0 if ut["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
