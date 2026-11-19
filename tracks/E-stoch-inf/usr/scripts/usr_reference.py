#!/usr/bin/env python3
"""Reference of the ultra-slow-roll (Higgs inflection) case of arXiv:2512.14649 for
AthenaK (package tracks/E-stoch-inf/usr).

Everything here is an ordinary differential equation or a sum over the lattice (decision
0010: reference solutions, no simulation):

  T0  the potential of P1:409 (Lambda = 1.86e-6, v = 0.198 Mpl, phi0 = -1.2 Mpl,
      P1:411-413) in Planck units and in the units of the code; V' and V'' from sympy;
      the closed-form V' of athenak/src/scalar_field/scalar_field.hpp:84-93 transcribed
      and compared;
  T1  the Friedmann and Klein-Gordon equations in e-folds from the Bunch-Davies time N0
      (H0 fixing, slow-roll velocity -V'/V read as dphi/dN, SPEC 5.1), N* - N0 = 3,
      N_f - N* = 10 (SCOPE 4 item 3), with the proper time t(N) as a third variable;
  T2  the same background as the code evolves it: phi, Pi, K and ln chi in code time
      (G = 1, time unit 1/H*, SPEC 2.5) with K evolved, not constrained, from the state at
      N*; compared with T1 mapped to code units; and the low-storage RK4()4[2S] of
      athenak/src/driver/driver.cpp:144-175 (update z4c_update.cpp:40, z4c_tasks.cpp:
      170-179) applied to the same equations at the step of a run (the twin of a
      homogeneous run);
  T3  landmarks (times and field values a run must reproduce) and a table every 0.5 e-fold;
  T4  Mukhanov-Sasaki mode functions of every lattice shell from Bunch-Davies data at N0
      to N* (the mode files of <scalar_field> noise_mode_file), then on to N_f with the
      full equation and with the field perturbation on an unperturbed FLRW background
      (what an FLRW lattice evolves, arXiv:2606.14853); spectra, enhancement, lattice
      variances.

Conventions as SPEC 1: Mpl = 1, eps1 = -dlnH/dN, eps2 = -dln eps1/dN (eps2 = +6 in USR);
a = exp(N - N*), so a* = 1; k_code = |n| for the box L = 2 pi/sigma with sigma = 1.
Code units (SPEC 2.5): phi_c = phi/sqrt(8 pi), V_c = V/(8 pi H*^2), t_c = H* t,
Pi_c = (dphi/dN)(H/H*)/sqrt(8 pi), R_k(code) = R_k H*^(3/2), so that
lambda_c = 8 pi Lambda/H*^2 and vev_c = v/sqrt(8 pi) in the code's form of V.

Usage (from the package directory or anywhere):
    python3 usr_reference.py --out DIR [--nmax2 16,64,256,1024,4096] [--nmesh 256]
"""
import argparse
import hashlib
import json
import os
import sys
import time

import numpy as np
import sympy as sp
from scipy.integrate import solve_ivp

SQ8PI = np.sqrt(8.0 * np.pi)
LAM, VEV, PHI0 = 1.86e-6, 0.198, -1.2          # P1:411-413
DN_STAR, DN_SIM = 3.0, 10.0                     # SCOPE 4 item 3 (P1:419-420 "~ 3", "~ 10")
SIGMA, SHARP = 1.0, 5.0                         # P1:503-506, 519

# ------------------------------------------------------------------ T0: the potential
_x = sp.symbols("x", real=True)
_V = sp.Rational(1, 3) * LAM * VEV**4 * _x**2 * (3 * _x**2 + 2 * sp.sqrt(2) * _x * VEV
                                                 + 6 * VEV**2) / (3 * _x**2 + 2 * VEV**2)**2
V = sp.lambdify(_x, _V, "numpy")
dV = sp.lambdify(_x, sp.diff(_V, _x), "numpy")
d2V = sp.lambdify(_x, sp.diff(_V, _x, 2), "numpy")
PHI_INFL = -np.sqrt(2.0) * VEV                  # double root of V' (../langevin/README.md)


def code_potential(phi, lam, vev):
    """V and V' as coded in athenak/src/scalar_field/scalar_field.hpp:84-93 (transcribed)."""
    s2 = 1.4142135623730951
    phi2 = phi * phi
    pp = 3.0 * phi2 + 2.0 * s2 * phi * vev + 6.0 * vev * vev
    qq = 3.0 * phi2 + 2.0 * vev * vev
    dpp = 6.0 * phi + 2.0 * s2 * vev
    dqq = 6.0 * phi
    c = lam * vev**4 / 3.0
    return (c * phi2 * pp / (qq * qq),
            c * ((2.0 * phi * pp + phi2 * dpp) / (qq * qq) - 2.0 * phi2 * pp * dqq / qq**3))


# ------------------------------------------------------------------ T1: background in e-folds
class Background:
    def __init__(self, n_end):
        self.n_star = DN_STAR
        y0 = [PHI0, -dV(PHI0) / V(PHI0), 0.0]
        self.sol = solve_ivp(self._rhs, (0.0, n_end), y0, method="DOP853", rtol=1e-13,
                             atol=[1e-16, 1e-18, 1e-30], dense_output=True, max_step=0.005)
        if self.sol.status != 0:
            raise RuntimeError(self.sol.message)
        self.h_star = self.state(self.n_star)["H"]
        self.t_star = self.state(self.n_star)["t"]

    @staticmethod
    def _rhs(n, y):
        f, fn, _ = y
        e1 = 0.5 * fn * fn
        h2 = V(f) / (3.0 - e1)
        return [fn, -(3.0 - e1) * fn - dV(f) / h2, 1.0 / np.sqrt(h2)]

    def state(self, n):
        f, fn, t = self.sol.sol(n)
        e1 = 0.5 * fn * fn
        h2 = V(f) / (3.0 - e1)
        fnn = -(3.0 - e1) * fn - dV(f) / h2
        return dict(phi=f, phiN=fn, phiNN=fnn, eps1=e1, eps2=-2.0 * fnn / fn,
                    H=np.sqrt(h2), t=t)

    def code(self, n):
        """Background at e-fold n in the units of the code."""
        s = self.state(n)
        hh = s["H"] / self.h_star
        return dict(cN=n - self.n_star, t=(s["t"] - self.t_star) * self.h_star,
                    a=np.exp(n - self.n_star), chi=np.exp(-2.0 * (n - self.n_star)),
                    phi=s["phi"] / SQ8PI, Pi=s["phiN"] * hh / SQ8PI, K=-3.0 * hh, H=hh,
                    eps1=s["eps1"], eps2=s["eps2"],
                    V=V(s["phi"]) / (8.0 * np.pi * self.h_star**2))


# ------------------------------------------------------------------ T2: code-time twins
def code_rhs(lam_c, vev_c):
    def f(t, y):
        phi, pi, k, lnchi = y
        v, dv = code_potential(phi, lam_c, vev_c)
        return np.array([pi, k * pi - dv, k * k / 3.0 + 8.0 * np.pi * (pi * pi - v),
                         2.0 * k / 3.0])
    return f


def z4c_rhs(lam_c, vev_c):
    """The homogeneous limit of AthenaK's Z4c with the scalar field (alpha = 1, zero shift,
    kappa1 = 0; z4c_calcrhs.cpp:568, 627-653): K = Khat + 2 Theta,
    d Khat = K^2/3 + 4 pi (S + E), d Theta = K^2/3 - 8 pi E, d chi = (2/3) chi K,
    d phi = Pi, d Pi = K Pi - V' (scalar_field.md section 2); E = Pi^2/2 + V,
    S = 3 (Pi^2/2 - V).  State (phi, Pi, Khat, Theta, chi)."""
    def f(t, y):
        phi, pi, kh, th, chi = y
        v, dv = code_potential(phi, lam_c, vev_c)
        k = kh + 2.0 * th
        e = 0.5 * pi * pi + v
        s = 3.0 * (0.5 * pi * pi - v)
        return np.array([pi, k * pi - dv, k * k / 3.0 + 4.0 * np.pi * (s + e),
                         k * k / 3.0 - 8.0 * np.pi * e, 2.0 * chi * k / 3.0])
    return f


RK4_2S = dict(gam0=[0.0, 0.121098479554482, -3.843833699660025, 0.546370891121863],
              gam1=[1.0, 0.721781678111411, 2.121209265338722, 0.198653035682705],
              beta=[1.193743905974738, 0.099279895495783, 1.131678018054042,
                    0.310665766509336],
              delta=[1.0, 0.217683334308543, 1.065841341361089, 0.0])


def rk4_2s(f, y0, dt, nsteps):
    """RK4()4[2S] as AthenaK applies it (stage 1: u1 = u0; stage s > 1: u1 += delta[s-1]
    u0; then u0 = gam0 u0 + gam1 u1 + beta dt f(u0)); returns the states after every
    step, row 0 the initial state."""
    c = RK4_2S
    u0 = np.array(y0, float)
    out = np.empty((nsteps + 1, u0.size))
    out[0] = u0
    for n in range(nsteps):
        u1 = u0.copy()
        for s in range(4):
            if s > 0:
                u1 = u1 + c["delta"][s] * u0
            u0 = c["gam0"][s] * u0 + c["gam1"][s] * u1 + c["beta"][s] * dt * f(0.0, u0)
        out[n + 1] = u0
    return out


# ------------------------------------------------------------------ T4: mode functions
def shells(nmax2):
    nmax = int(np.floor(np.sqrt(nmax2) + 1e-9))
    r = np.arange(-nmax, nmax + 1)
    n2 = (r[:, None, None]**2 + r[None, :, None]**2 + r[None, None, :]**2).ravel()
    n2 = n2[(n2 >= 1) & (n2 <= nmax2)]
    u, cnt = np.unique(n2, return_counts=True)
    return u, cnt                     # shells |n|^2 and their multiplicities (all n)


def bunch_davies(bg, k, n_i):
    """R_k, dR_k/dN at e-fold n_i (Planck units), v = e^{-ik tau}(1 - i/(k tau))/sqrt(2k),
    tau = -1/((1 - eps1) a H), R = v/z, z = a sqrt(2 eps1) (SPEC U4: the form of
    ../spec/ref/ms_reference.py, a [JUDGEMENT] of that package)."""
    s = bg.state(n_i)
    a = np.exp(n_i - bg.n_star)
    ah = a * s["H"]
    tau = -1.0 / ((1.0 - s["eps1"]) * ah)
    ph = np.exp(-1j * k * tau) / np.sqrt(2.0 * k)
    v = ph * (1.0 - 1j / (k * tau))
    dv = -1j * k * v + ph * 1j / (k * tau * tau)
    z = a * np.sqrt(2.0 * s["eps1"])
    dz = ah * z * (1.0 - 0.5 * s["eps2"])
    return v / z, (dv / z - v * dz / z**2) / ah


def ms_vector(bg, k, n0, n1, r0, rn0, n_eval, form="ms", rtol=1e-11):
    """All wave numbers k (Planck) at once from (r0, rn0) at n0 to n1: form 'ms' the
    Mukhanov-Sasaki equation R_NN + (3 - eps1 - eps2) R_N + (k/aH)^2 R = 0; form 'flrw' the
    field perturbation dphi_NN + (3 - eps1) dphi_N + (k^2/(aH)^2 + V''/H^2) dphi = 0 on the
    unperturbed background, returned as R = dphi/phi_N.  Returns R, R_N at n_eval."""
    m = k.size
    k2 = k * k
    if form == "ms":
        y0 = np.concatenate([r0.real, r0.imag, rn0.real, rn0.imag])
    else:
        s = bg.state(n0)
        d0 = s["phiN"] * r0
        dn0 = s["phiNN"] * r0 + s["phiN"] * rn0
        y0 = np.concatenate([d0.real, d0.imag, dn0.real, dn0.imag])
    scale = np.concatenate([np.abs(y0[:2 * m].reshape(2, m)).max(axis=0)] * 2
                           + [np.abs(y0[2 * m:].reshape(2, m)).max(axis=0)] * 2)
    scale = np.maximum(scale, 1e-300)

    def rhs(n, y):
        s = bg.state(n)
        w2 = k2 / (np.exp(2.0 * (n - bg.n_star)) * s["H"]**2)
        out = np.empty_like(y)
        out[:2 * m] = y[2 * m:]
        if form == "ms":
            fr = 3.0 - s["eps1"] - s["eps2"]
            mass = w2
        else:
            fr = 3.0 - s["eps1"]
            mass = w2 + d2V(s["phi"]) / s["H"]**2
        out[2 * m:3 * m] = -fr * y[2 * m:3 * m] - mass * y[:m]
        out[3 * m:] = -fr * y[3 * m:] - mass * y[m:2 * m]
        return out

    sol = solve_ivp(rhs, (n0, n1), y0, method="DOP853", rtol=rtol, atol=1e-13 * scale,
                    t_eval=n_eval)
    if sol.status != 0:
        raise RuntimeError(sol.message)
    y = sol.y
    r = y[:m] + 1j * y[m:2 * m]
    rn = y[2 * m:3 * m] + 1j * y[3 * m:]
    if form == "flrw":
        st = bg.state(sol.t)
        rn = (rn - st["phiNN"][None, :] * r / st["phiN"][None, :]) / st["phiN"][None, :]
        r = r / st["phiN"][None, :]
    return r, rn, sol.t


def write_mode_file(path, n2, r, dr, header):
    with open(path, "w") as fp:
        for line in header.splitlines():
            fp.write("# " + line + "\n")
        fp.write("# n2  Re_R  Im_R  Re_dR/dtau  Im_dR/dtau\n")
        for a, b, c in zip(n2, r, dr):
            fp.write(f"{int(a)} {b.real:.17e} {b.imag:.17e} {c.real:.17e} {c.imag:.17e}\n")
    with open(path, "rb") as fp:
        return hashlib.sha256(fp.read()).hexdigest()


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--nmax2", default="16,64,256,1024,4096")
    ap.add_argument("--mode-dir", default=None, help="where the mode files go (default OUT)")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    mode_dir = a.mode_dir or a.out
    os.makedirs(mode_dir, exist_ok=True)
    t_start = time.time()
    res = dict(case="inflection (USR) of arXiv:2512.14649", lam=LAM, vev=VEV, phi0_N0=PHI0,
               dn_star=DN_STAR, dn_sim=DN_SIM, sigma=SIGMA, sharpness=SHARP)

    # ---------------- T1
    n_end = DN_STAR + DN_SIM + 0.5
    bg = Background(n_end)
    hs = bg.h_star
    s0 = bg.state(0.0)
    sst = bg.state(DN_STAR)
    res["T1"] = dict(dphidN_N0=float(s0["phiN"]), H0=float(s0["H"]), H_star=float(hs),
                     phi_star=float(sst["phi"]), dphidN_star=float(sst["phiN"]),
                     eps1_star=float(sst["eps1"]), eps2_star=float(sst["eps2"]),
                     eps1_N0=float(s0["eps1"]), eps2_N0=float(s0["eps2"]))
    lam_c = 8.0 * np.pi * LAM / hs**2
    vev_c = VEV / SQ8PI
    c0 = bg.code(DN_STAR)
    res["code_inputs"] = dict(potential="inflection", **{"lambda": float(lam_c)},
                              vev=float(vev_c), phi0=float(c0["phi"]), pi0=float(c0["Pi"]),
                              K0=float(-np.sqrt(24.0 * np.pi * (0.5 * c0["Pi"]**2
                                                                + code_potential(c0["phi"], lam_c, vev_c)[0]))),
                              box=2.0 * np.pi / SIGMA, noise_sigma=SIGMA,
                              noise_sharpness=SHARP)

    # ---------------- T0
    ph = np.linspace(-1.3, -0.05, 2001)
    vc, dvc = code_potential(ph / SQ8PI, lam_c, vev_c)
    rel_v = np.max(np.abs(vc * 8.0 * np.pi * hs**2 - V(ph)) / np.abs(V(ph)))
    # V' in code units: dV_c/dphi_c = V'(phi) sqrt(8 pi)/(8 pi H*^2)
    rel_dv = np.max(np.abs(dvc - dV(ph) * SQ8PI / (8.0 * np.pi * hs**2))
                    / np.max(np.abs(dV(ph) * SQ8PI / (8.0 * np.pi * hs**2))))
    vp, dvp = code_potential(ph, LAM, VEV)
    rel_dv_planck = np.max(np.abs(dvp - dV(ph))) / np.max(np.abs(dV(ph)))
    phs = np.linspace(-0.6, -0.1, 50001)
    i_min = int(np.argmin(np.abs(dV(phs))))
    res["T0"] = dict(rel_V_code_vs_planck=float(rel_v), rel_dV_code_vs_sympy=float(rel_dv),
                     rel_dV_coded_vs_sympy_planck=float(rel_dv_planck),
                     phi_min_abs_dV=float(phs[i_min]), phi_inflection=float(PHI_INFL),
                     dV_at_inflection=float(dV(PHI_INFL)), d2V_at_inflection=float(d2V(PHI_INFL)),
                     V_at_inflection=float(V(PHI_INFL)))

    # ---------------- T3: grid, landmarks
    ng = np.linspace(DN_STAR, DN_STAR + DN_SIM, 20001)
    st = bg.state(ng)
    cg = bg.code(ng)
    e2 = st["eps2"]

    def crossings(y, level, direction):
        d = y - level
        idx = np.where((d[:-1] < 0) & (d[1:] >= 0))[0] if direction > 0 else \
            np.where((d[:-1] > 0) & (d[1:] <= 0))[0]
        out = []
        for i in idx:
            from scipy.optimize import brentq
            fn = {"eps2": lambda n: bg.state(n)["eps2"] - level,
                  "phi": lambda n: bg.state(n)["phi"] - level}[y_name]
            out.append(brentq(fn, ng[i], ng[i + 1], xtol=1e-13))
        return out

    marks = [("start N*", DN_STAR)]
    y_name = "eps2"
    up0 = crossings(e2, 0.0, +1)
    marks += [("eps2 = 0 up (eps1 maximum)", n) for n in up0]
    marks += [("eps2 = 3 up (USR onset)", n) for n in crossings(e2, 3.0, +1)]
    from scipy.optimize import minimize_scalar
    i2 = int(np.argmax(e2))
    mx = minimize_scalar(lambda n: -bg.state(n)["eps2"], bounds=(ng[max(i2 - 2, 0)],
                         ng[min(i2 + 2, ng.size - 1)]), method="bounded",
                         options=dict(xatol=1e-12))
    marks.append(("eps2 maximum", mx.x))
    marks += [("eps2 = 3 down (USR end)", n) for n in crossings(e2, 3.0, -1)]
    marks += [("eps2 = 0 down (eps1 minimum)", n) for n in crossings(e2, 0.0, -1)]
    y_name = "phi"
    marks += [("phi = -sqrt2 v (inflection point)", n)
              for n in crossings(st["phi"], PHI_INFL, +1)]
    marks.append(("end N_f", DN_STAR + DN_SIM))
    marks.sort(key=lambda m: m[1])
    land = []
    for name, n in marks:
        c = bg.code(n)
        land.append(dict(label=name, N=float(n), **{k: float(v) for k, v in c.items()},
                         phi_planck=float(bg.state(n)["phi"])))
    res["landmarks"] = land
    cols = ["label", "N", "cN", "t", "a", "chi", "phi", "Pi", "K", "H", "eps1", "eps2", "V",
            "phi_planck"]
    with open(os.path.join(a.out, "landmarks.csv"), "w") as fp:
        fp.write("# code units (G = 1, time 1/H*, a* = 1); phi_planck in Mpl; N from N0\n")
        fp.write(",".join(cols) + "\n")
        for lm in land:
            fp.write(",".join([lm["label"]] + [f"{lm[c]:.15e}" for c in cols[1:]]) + "\n")
    table = []
    for n in np.arange(DN_STAR, DN_STAR + DN_SIM + 1e-9, 0.5):
        c = bg.code(n)
        table.append({k: float(v) for k, v in c.items()})
    res["table_half_efold"] = table
    res["t_code_end"] = float(bg.code(DN_STAR + DN_SIM)["t"])
    usr = e2 > 3.0
    res["usr_cN"] = [float(ng[usr][0] - DN_STAR), float(ng[usr][-1] - DN_STAR)]
    res["eps1_min"] = float(st["eps1"].min())
    res["eps1_min_cN"] = float(ng[np.argmin(st["eps1"])] - DN_STAR)
    res["Pi_code_min"] = float(np.min(np.abs(cg["Pi"])))
    res["Pi_code_range"] = [float(cg["Pi"].min()), float(cg["Pi"].max())]

    # ---------------- T2: code-time twin, exact and RK4()4[2S]
    f = code_rhs(lam_c, vev_c)
    y0 = [c0["phi"], c0["Pi"], res["code_inputs"]["K0"], 0.0]
    t_end = res["t_code_end"]
    tw = solve_ivp(f, (0.0, t_end), y0, method="DOP853", rtol=1e-13,
                   atol=[1e-17, 1e-19, 1e-15, 1e-15], dense_output=True)
    tt = np.linspace(0.0, t_end, 2001)
    yt = tw.sol(tt)
    n_tw = DN_STAR + (-yt[3] / 2.0)                   # N = N* - ln(chi)/2
    cref = bg.code(n_tw)
    res["T2_exact"] = dict(
        max_rel_phi=float(np.max(np.abs(yt[0] - cref["phi"]) / np.abs(cref["phi"]))),
        max_rel_Pi=float(np.max(np.abs(yt[1] - cref["Pi"]) / np.abs(cref["Pi"]))),
        max_rel_K=float(np.max(np.abs(yt[2] - cref["K"]) / np.abs(cref["K"]))),
        max_abs_t_minus_tN=float(np.max(np.abs(tt - cref["t"]))),
        efolds_at_t_end=float(-yt[3][-1] / 2.0),
        ham_rel_max=float(np.max(np.abs(yt[2]**2 / 3.0 - 8.0 * np.pi * (
            0.5 * yt[1]**2 + code_potential(yt[0], lam_c, vev_c)[0])) / (yt[2]**2 / 3.0))))
    twins = {}
    fz = z4c_rhs(lam_c, vev_c)
    yz0 = [y0[0], y0[1], y0[2], 0.0, 1.0]
    for label, nmesh, cfl in (("dt=0.0491 (N=32, C=0.25)", 32, 0.25),
                              ("dt=0.0245 (N=32, C=0.125)", 32, 0.125),
                              ("dt=0.00614 (N=256, C=0.25)", 256, 0.25)):
        dt = cfl * 2.0 * np.pi / nmesh
        nst = int(np.ceil(t_end / dt - 1e-9))
        yy = rk4_2s(fz, yz0, dt, nst)
        te = dt * np.arange(nst + 1)
        ye = tw.sol(np.minimum(te, t_end))
        kz = yy[:, 2] + 2.0 * yy[:, 3]
        rel_phi = np.abs(yy[:, 0] - ye[0]) / np.abs(ye[0])
        rel_pi = np.abs(yy[:, 1] - ye[1]) / np.abs(ye[1])
        rel_k = np.abs(kz - ye[2]) / np.abs(ye[2])
        dlnchi = np.abs(np.log(yy[:, 4]) - ye[3])
        ok = te <= t_end
        twins[label] = dict(dt=dt, nsteps=nst, t_last=float(te[-1]),
                            max_rel_phi=float(rel_phi[ok].max()),
                            max_rel_Pi=float(rel_pi[ok].max()),
                            max_rel_K=float(rel_k[ok].max()),
                            max_abs_lnchi=float(dlnchi[ok].max()),
                            max_abs_theta=float(np.abs(yy[:, 3]).max()),
                            end_rel_Pi=float(rel_pi[ok][-1]))
        np.savez_compressed(os.path.join(a.out, f"twin_N{nmesh}_C{cfl:g}.npz"), t=te,
                            phi=yy[:, 0], Pi=yy[:, 1], Khat=yy[:, 2], Theta=yy[:, 3],
                            chi=yy[:, 4], dt=dt)
        if nmesh == 32 and cfl == 0.25:
            twin_curve = dict(t=te[ok], rel_phi=rel_phi[ok], rel_Pi=rel_pi[ok],
                              rel_K=rel_k[ok], dlnchi=dlnchi[ok])
    res["T2_rk4_2s"] = twins

    # ---------------- T4: mode functions, spectra
    nmax_list = [int(x) for x in a.nmax2.split(",")]
    n2_all, mult_all = shells(max(nmax_list))
    k_code = np.sqrt(n2_all.astype(float))
    k_pl = k_code * hs * np.exp(0.0)          # k = |n| a* H* sigma, a* = 1
    r_n0, rn_n0 = bunch_davies(bg, k_pl, 0.0)
    r_st, rn_st, _ = ms_vector(bg, k_pl, 0.0, DN_STAR, r_n0, rn_n0, [DN_STAR])
    r_st, rn_st = r_st[:, 0], rn_st[:, 0]
    mode_files = {}
    for nm in nmax_list:
        sel = n2_all <= nm
        hdr = (f"inflection (USR) case of arXiv:2512.14649, nmax2 = {nm}, written by "
               f"tracks/E-stoch-inf/usr/scripts/usr_reference.py\n"
               f"R_k and dR/dtau (tau = code time) at N* = N0 + {DN_STAR:g} in code units "
               f"(R_k H*^(3/2)); Bunch-Davies data at N0 for every shell\n"
               f"lambda = {lam_c:.17e} vev = {vev_c:.17e} phi0 = {c0['phi']:.17e} "
               f"pi0 = {c0['Pi']:.17e} H*/Mpl = {hs:.15e}")
        path = os.path.join(mode_dir, f"modes_usr_n{nm}.txt")
        sha = write_mode_file(path, n2_all[sel], r_st[sel] * hs**1.5, rn_st[sel] * hs**1.5,
                              hdr)
        mode_files[f"n{nm}"] = dict(path=os.path.abspath(path), sha256=sha,
                                    nshell=int(sel.sum()))
    res["mode_files"] = mode_files

    n_out = np.round(np.arange(DN_STAR, DN_STAR + DN_SIM + 1e-9, 0.1), 10)
    r_ms, rn_ms, _ = ms_vector(bg, k_pl, DN_STAR, DN_STAR + DN_SIM, r_st, rn_st, n_out)
    r_fl, rn_fl, _ = ms_vector(bg, k_pl, DN_STAR, DN_STAR + DN_SIM, r_st, rn_st, n_out,
                               form="flrw")
    delta_ms = k_pl[:, None]**3 * np.abs(r_ms)**2 / (2.0 * np.pi**2)
    delta_fl = k_pl[:, None]**3 * np.abs(r_fl)**2 / (2.0 * np.pi**2)
    # window of every shell at the output times (Friedmann a, H; sigma = 1)
    ah = np.exp(n_out - DN_STAR) * bg.state(n_out)["H"] / hs
    xw = SHARP * np.log(SIGMA * ah[None, :] / k_code[:, None])
    win = 0.5 * (1.0 + np.tanh(xw))
    # crossing k = aH and the slow-roll estimate there
    nf = np.linspace(0.0, DN_STAR + DN_SIM, 200001)
    lnah = (nf - DN_STAR) + np.log(bg.state(nf)["H"] / hs)
    n_cross = np.interp(np.log(k_code), lnah, nf)
    sx = bg.state(n_cross)
    delta_sr = sx["H"]**2 / (8.0 * np.pi**2 * sx["eps1"])
    # lattice variances of R (coarse-grained W R and plain R) for the set-ups
    setups = [(32, 16), (32, 64), (64, 256), (128, 1024), (256, 4096)]
    var = {}
    for nmesh, nm in setups:
        sel = n2_all <= nm
        w = mult_all[sel] / (4.0 * np.pi * k_code[sel]**3)
        var[f"N{nmesh}_n{nm}"] = dict(
            var_cg=(w[:, None] * (win[sel]**2) * delta_ms[sel]).sum(axis=0).tolist(),
            var=(w[:, None] * delta_ms[sel]).sum(axis=0).tolist())
    res["lattice_variance"] = dict(cN=(n_out - DN_STAR).tolist(), **var)
    pick = [1, 2, 3, 4, 8, 16, 32, 64]
    idx = [int(np.argmin(np.abs(k_code - p))) for p in pick if np.min(np.abs(k_code - p)) < 1e-9]
    with open(os.path.join(a.out, "usr_spectrum_Nf.csv"), "w") as fp:
        fp.write("# n2,k_over_dk,multiplicity,N_cross_minus_Nstar,Delta_ms_Nf,Delta_flrw_Nf,"
                 "Delta_SR_at_cross,enhancement\n")
        for i in range(k_code.size):
            fp.write(f"{int(n2_all[i])},{k_code[i]:.10g},{int(mult_all[i])},"
                     f"{n_cross[i] - DN_STAR:.10g},{delta_ms[i, -1]:.10e},"
                     f"{delta_fl[i, -1]:.10e},{delta_sr[i]:.10e},"
                     f"{delta_ms[i, -1] / delta_sr[i]:.10e}\n")
    res["spectrum_at_Nf"] = [dict(k_over_dk=float(k_code[i]), N_cross_cN=float(n_cross[i] - DN_STAR),
                                  Delta_ms=float(delta_ms[i, -1]), Delta_flrw=float(delta_fl[i, -1]),
                                  flrw_over_ms=float(delta_fl[i, -1] / delta_ms[i, -1]),
                                  Delta_SR_at_cross=float(delta_sr[i]),
                                  enhancement=float(delta_ms[i, -1] / delta_sr[i]),
                                  Delta_ms_cN5=float(delta_ms[i, 50]),
                                  drift_lnDelta_last_efold=float(np.log(delta_ms[i, -1] / delta_ms[i, -11])))
                             for i in idx]
    res["peak"] = dict(k_over_dk=float(k_code[np.argmax(delta_ms[:, -1])]),
                       Delta=float(delta_ms[:, -1].max()),
                       Delta_min=float(delta_ms[:, -1].min()),
                       k_min_over_dk=float(k_code[np.argmin(delta_ms[:, -1])]))
    np.savez_compressed(os.path.join(a.out, "usr_reference.npz"), n2=n2_all, mult=mult_all,
                        k_code=k_code, n_out=n_out, delta_ms=delta_ms, delta_fl=delta_fl,
                        win=win, n_cross=n_cross, delta_sr=delta_sr,
                        r_st=r_st * hs**1.5, rn_st=rn_st * hs**1.5,
                        bg_N=ng, bg_eps1=st["eps1"], bg_eps2=st["eps2"], bg_phi=st["phi"],
                        bg_H=st["H"] / hs, bg_t=cg["t"], bg_Pi=cg["Pi"],
                        tw_t=twin_curve["t"], tw_rel_phi=twin_curve["rel_phi"],
                        tw_rel_Pi=twin_curve["rel_Pi"], tw_rel_K=twin_curve["rel_K"],
                        tw_dlnchi=twin_curve["dlnchi"])
    res["wall_seconds"] = time.time() - t_start
    with open(os.path.join(a.out, "usr_reference.json"), "w") as fp:
        json.dump(res, fp, indent=1)
    short = {k: v for k, v in res.items() if k not in ("table_half_efold", "lattice_variance")}
    print(json.dumps(short, indent=1)[:12000])


if __name__ == "__main__":
    sys.exit(main())
