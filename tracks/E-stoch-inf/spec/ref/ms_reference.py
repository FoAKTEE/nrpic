#!/usr/bin/env python3
"""Linear reference for the two test cases of arXiv:2512.14649 (E-pre-1, tests T1 and T2).

For the quadratic (slow-roll) and the Higgs-inflection (ultra-slow-roll) model of Table I of
2512.14649 this script
  1. integrates the Friedmann background from the stated parameters (test T1),
  2. solves the Mukhanov-Sasaki equation for comoving curvature R_k with Bunch-Davies initial
     data on the lattice wave numbers of the N = 256, sigma = 1 set-up (k from k*_sigma to
     N/4 k*_sigma), and the "deformed" equation without metric perturbations of
     arXiv:2606.14853 eq. (7), in two independent forms (test T2),
  3. writes the curves and a JSON summary into --out.

Conventions (SPEC.md section 2): reduced Planck mass Mpl = 1, e-folds N with N = 0 at the
Bunch-Davies time N0, a = exp(N - Nstar) so that a* = 1 at the start of the simulation,
eps1 = -dlnH/dN, eps2 = -dln(eps1)/dN (the sign of 2512.14649 eq. 4: eps2 = -0.02 for the
quadratic attractor, eps2 = +6 in USR).

Usage: python3 -I ms_reference.py --out DIR [--kmode-start 100]
"""
import argparse
import json
import os
import sys

import numpy as np
import sympy as sp
from scipy.integrate import solve_ivp

# ----------------------------------------------------------------------------- models
phi = sp.symbols("phi", real=True)


def model_quadratic():
    """Potential-position fixing (2502.06783 eq. 22, p = 2) with eps1 = 0.01, eps2 = -0.02,
    H0 = 1e-5 (2512.14649 Table I); the field rolls towards positive phi."""
    e1, e2, H0, p = 0.01, -0.02, 1e-5, 2
    phi0 = -abs((3 - e1) * p / (np.sqrt(2 * e1) * (e2 / 2 + e1 - 3)))
    lam = abs(np.sqrt(2 * e1) * (e2 / 2 + e1 - 3) / ((3 - e1) * p)) ** p * H0**2 * (3 - e1)
    V = lam * phi**2
    dphidN0 = +np.sqrt(2 * e1)            # rolls left to right (2502.06783, Notations)
    return dict(name="quadratic", V=V, phi0=phi0, dphidN0=dphidN0, dNstar=5.0, dNsim=8.0,
                params=dict(eps1=e1, eps2=e2, H0=H0, lam=lam, m=np.sqrt(2 * lam), phi0=phi0))


def model_inflection(velocity="dN"):
    """Higgs-like inflection potential (2512.14649 Table I, 2502.06783 eq. 31) with
    Lambda = 1.86e-6, v = 0.198, phi0 = -1.2, H0 fixing: slow-roll velocity
    -Mpl^2 V'/V read as dphi/dN (velocity='dN') or as dphi/dt (velocity='dt')."""
    Lam, v = 1.86e-6, 0.198
    V = Lam * v**4 * phi**2 * (3 * phi**2 + 2 * sp.sqrt(2) * phi * v + 6 * v**2) / (
        3 * (3 * phi**2 + 2 * v**2) ** 2)
    phi0 = -1.2
    Vf = sp.lambdify(phi, V)
    dVf = sp.lambdify(phi, sp.diff(V, phi))
    u = -dVf(phi0) / Vf(phi0)
    if velocity == "dN":
        dphidN0 = u
    else:
        # dphi/dt = u, so dphi/dN = u / H with H from the Friedmann equation
        # 3 H^2 = V + (dphi/dt)^2 / 2
        H = np.sqrt((Vf(phi0) + 0.5 * u**2) / 3.0)
        dphidN0 = u / H
    return dict(name="inflection" + ("" if velocity == "dN" else "_dt"), V=V, phi0=phi0,
                dphidN0=dphidN0, dNstar=3.0, dNsim=10.0,
                params=dict(Lambda=Lam, v=v, phi0=phi0, velocity_reading=velocity))


# ----------------------------------------------------------------------------- background
class Background:
    def __init__(self, mdl, Nend):
        self.m = mdl
        V = mdl["V"]
        self.V = sp.lambdify(phi, V)
        self.dV = sp.lambdify(phi, sp.diff(V, phi))
        self.d2V = sp.lambdify(phi, sp.diff(V, phi, 2))
        y0 = [mdl["phi0"], mdl["dphidN0"]]
        sol = solve_ivp(self.rhs, (0.0, Nend), y0, method="DOP853", rtol=1e-13, atol=1e-16,
                        dense_output=True, max_step=0.01)
        if sol.status != 0:
            raise RuntimeError(sol.message)
        self.sol = sol
        self.Nstar = mdl["dNstar"]
        self.Hstar = self.H(self.Nstar)

    def rhs(self, N, y):
        f, fN = y
        eps = 0.5 * fN**2
        H2 = self.V(f) / (3.0 - eps)
        return [fN, -(3.0 - eps) * fN - self.dV(f) / H2]

    def state(self, N):
        f, fN = self.sol.sol(N)
        eps = 0.5 * fN**2
        H2 = self.V(f) / (3.0 - eps)
        fNN = -(3.0 - eps) * fN - self.dV(f) / H2
        eps2 = -2.0 * fNN / fN                          # -dln(eps1)/dN
        return f, fN, fNN, eps, eps2, np.sqrt(H2)

    def H(self, N):
        return self.state(N)[5]

    def aH(self, N):
        return np.exp(N - self.Nstar) * self.H(N)


# ----------------------------------------------------------------------------- perturbations
def bd_initial(bg, k, Ni):
    """Bunch-Davies data for R_k = v_k / z, z = a sqrt(2 eps1), at e-fold Ni (Mpl = 1).
    v = exp(-i k tau) / sqrt(2k) (1 - i / (k tau)), tau = -1 / ((1 - eps1) a H)."""
    f, fN, fNN, eps, eps2, H = bg.state(Ni)
    a = np.exp(Ni - bg.Nstar)
    aH = a * H
    tau = -1.0 / ((1.0 - eps) * aH)
    v = np.exp(-1j * k * tau) / np.sqrt(2 * k) * (1 - 1j / (k * tau))
    dv_dtau = (-1j * k) * v + np.exp(-1j * k * tau) / np.sqrt(2 * k) * (1j / (k * tau**2))
    z = a * np.sqrt(2 * eps)
    # dz/dtau = aH z (1 + dln sqrt(eps)/dN) = aH z (1 - eps2/2)
    dz_dtau = aH * z * (1.0 - 0.5 * eps2)
    R = v / z
    dR_dtau = dv_dtau / z - v * dz_dtau / z**2
    return R, dR_dtau / aH                               # R and dR/dN


def ms_rhs(bg, k, deformed):
    def rhs(N, y):
        R = y[0] + 1j * y[1]
        RN = y[2] + 1j * y[3]
        f, fN, fNN, eps, eps2, H = bg.state(N)
        kaH2 = (k / (np.exp(N - bg.Nstar) * H)) ** 2
        mass = 2.0 * eps * (3.0 - eps - eps2) if deformed else 0.0
        RNN = -(3.0 - eps - eps2) * RN - (kaH2 + mass) * R
        return [RN.real, RN.imag, RNN.real, RNN.imag]
    return rhs


def dphi_rhs(bg, k):
    """Field perturbation on an unperturbed FLRW background (what an FLRW lattice evolves)."""
    def rhs(N, y):
        d = y[0] + 1j * y[1]
        dN = y[2] + 1j * y[3]
        f, fN, fNN, eps, eps2, H = bg.state(N)
        kaH2 = (k / (np.exp(N - bg.Nstar) * H)) ** 2
        dNN = -(3.0 - eps) * dN - (kaH2 + bg.d2V(f) / H**2) * d
        return [dN.real, dN.imag, dNN.real, dNN.imag]
    return rhs


def solve_mode(bg, k, Ngrid, kstart, form):
    """Return R_k on Ngrid (NaN before the start) for form in {'ms', 'def', 'dphi'}."""
    # start where k/aH = kstart, but not before N0 = 0
    from scipy.optimize import brentq
    g = lambda N: k / bg.aH(N) - kstart
    Ni = 0.0 if g(0.0) < 0 else brentq(g, 0.0, bg.sol.t[-1])
    R0, RN0 = bd_initial(bg, k, Ni)
    sel = Ngrid >= Ni
    out = np.full(Ngrid.shape, np.nan + 1j * np.nan)
    if form in ("ms", "def"):
        y0 = [R0.real, R0.imag, RN0.real, RN0.imag]
        s = solve_ivp(ms_rhs(bg, k, form == "def"), (Ni, Ngrid[-1]), y0, method="DOP853",
                      rtol=1e-11, atol=1e-30, t_eval=Ngrid[sel], max_step=0.02)
        out[sel] = s.y[0] + 1j * s.y[1]
    else:
        f, fN, fNN, eps, eps2, H = bg.state(Ni)
        d0 = fN * R0
        dN0 = fNN * R0 + fN * RN0
        y0 = [d0.real, d0.imag, dN0.real, dN0.imag]
        s = solve_ivp(dphi_rhs(bg, k), (Ni, Ngrid[-1]), y0, method="DOP853",
                      rtol=1e-11, atol=1e-30, t_eval=Ngrid[sel], max_step=0.02)
        fN_grid = np.array([bg.state(N)[1] for N in Ngrid[sel]])
        out[sel] = (s.y[0] + 1j * s.y[1]) / fN_grid
    if s.status != 0:
        raise RuntimeError(s.message)
    return out, Ni


def run(mdl, out, kstart, Nlat=256):
    Nend = mdl["dNstar"] + mdl["dNsim"]
    bg = Background(mdl, Nend + 0.5)
    Ng = np.linspace(0.0, Nend, 1301)
    st = np.array([bg.state(N) for N in Ng])
    phiN, eps1, eps2, H = st[:, 0], st[:, 3], st[:, 4], st[:, 5]
    # lattice: k*_sigma = sigma a* H* (sigma = 1), dk = k*_sigma, kmax = Nlat/4 dk
    dk = bg.aH(bg.Nstar)
    kk = dk * np.unique(np.round(np.geomspace(1.0, Nlat / 4, 25), 6))
    res = dict(model=mdl["name"], params=mdl["params"], dphidN0=mdl["dphidN0"],
               Nstar=bg.Nstar, Nf=Nend, Hstar=bg.Hstar, H0=float(H[0]),
               dk=dk, L=2 * np.pi / dk, kstart=kstart)
    curves = {}
    for form in ("ms", "def", "dphi"):
        Rk = np.empty((len(kk), len(Ng)), dtype=complex)
        Nis = []
        for i, k in enumerate(kk):
            Rk[i], Ni = solve_mode(bg, k, Ng, kstart, form)
            Nis.append(Ni)
        curves[form] = Rk
        res["Nstart_" + form] = Nis
    Delta = {f: kk[:, None] ** 3 * np.abs(curves[f]) ** 2 / (2 * np.pi**2) for f in curves}
    # crossing time k = aH and the slow-roll estimate H^2/(8 pi^2 eps1) there
    from scipy.optimize import brentq
    Nx = np.array([brentq(lambda N: bg.aH(N) - k, 0.0, Nend) for k in kk])
    sx = np.array([bg.state(N) for N in Nx])
    res["N_cross"] = Nx.tolist()
    res["Delta_SR_estimate_at_cross"] = (sx[:, 5] ** 2 / (8 * np.pi**2 * sx[:, 3])).tolist()
    res["Delta_ms_Nf"] = Delta["ms"][:, -1].tolist()
    res["Delta_def_Nf"] = Delta["def"][:, -1].tolist()
    res["k_over_dk"] = (kk / dk).tolist()
    # drift of ln Delta per e-fold from N_cross + 3 to Nf (modes with at least 1 e-fold)
    drift = {}
    for f in ("ms", "def"):
        dr = []
        for i in range(len(kk)):
            sel = (Ng >= Nx[i] + 3.0)
            if np.count_nonzero(sel) > 10 and Ng[sel][-1] - Ng[sel][0] > 1.0:
                p = np.polyfit(Ng[sel], np.log(Delta[f][i, sel]), 1)
                dr.append(p[0])
            else:
                dr.append(np.nan)
        drift[f] = dr
    res["drift_ms"] = drift["ms"]
    res["drift_def"] = drift["def"]
    res["eps1_at_N0"] = float(eps1[0])
    res["eps2_at_N0"] = float(eps2[0])
    res["eps1_at_Nf"] = float(eps1[-1])
    res["H_ratio_Nf_N0"] = float(H[-1] / H[0])
    # cross-check of the reference: deformed MS in R form vs delta-phi form
    m = np.isfinite(curves["def"]) & np.isfinite(curves["dphi"])
    rel = np.abs(curves["def"][m] - curves["dphi"][m]) / np.abs(curves["dphi"][m])
    res["max_rel_def_vs_dphi"] = float(np.max(rel))
    # USR phase in simulation time cN = N - N*
    usr = eps2 > 3.0
    if np.any(usr):
        idx = np.where(usr)[0]
        res["usr_start_cN"] = float(Ng[idx[0]] - bg.Nstar)
        res["usr_end_cN"] = float(Ng[idx[-1]] - bg.Nstar)
        res["eps2_max"] = float(np.max(eps2))
        res["eps1_min"] = float(np.min(eps1))
    res["eps2_at_Nf"] = float(eps2[-1])
    res["eps1_at_Nf"] = float(eps1[-1])
    res["phi_at_Nf"] = float(phiN[-1])
    res["inflation_ended"] = bool(np.any(eps1 >= 1.0))
    # near-inflection point: where |V'| has its local minimum between phi0 and 0
    ph = np.linspace(mdl["phi0"], -1e-3 if mdl["phi0"] < 0 else 1e-3, 20001)
    dv = np.abs(bg.dV(ph))
    i0 = np.argmin(dv[100:-100]) + 100
    res["phi_min_absdV"] = float(ph[i0])
    res["V_prime_sign_change"] = bool(np.any(np.diff(np.sign(bg.dV(ph))) != 0))
    np.savez_compressed(os.path.join(out, mdl["name"] + ".npz"), N=Ng, phi=phiN, eps1=eps1,
                        eps2=eps2, H=H, k=kk, dk=dk, Nstar=bg.Nstar, Ncross=Nx,
                        R_ms=curves["ms"], R_def=curves["def"], R_dphi=curves["dphi"])
    with open(os.path.join(out, mdl["name"] + ".json"), "w") as fh:
        json.dump(res, fh, indent=1)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--kmode-start", type=float, default=100.0,
                    help="k/aH at which a mode starts in the Bunch-Davies state (or N0)")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    summary = {}
    for mdl in (model_quadratic(), model_inflection("dN")):
        try:
            r = run(mdl, a.out, a.kmode_start)
        except Exception as e:  # keep failed readings on record
            r = dict(model=mdl["name"], error=repr(e))
        summary[mdl["name"]] = r
        print(json.dumps({k: v for k, v in r.items() if not isinstance(v, list)}, indent=1))
        sys.stdout.flush()
    with open(os.path.join(a.out, "summary.json"), "w") as fh:
        json.dump(summary, fh, indent=1)


if __name__ == "__main__":
    main()
