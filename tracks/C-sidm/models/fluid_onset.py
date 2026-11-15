#!/usr/bin/env python3
"""Fluid onset of the radial instability of the truncated Maxwell-Boltzmann (F21) cores
with the adiabatic index of a collision-dominated (Maxwell-Juttner) gas.

    python3 fluid_onset.py --out DIR [--b 0.1 0.2 0.3 0.5] [--N 600 1200]

Reference solution only (ordinary differential equation and a one-dimensional eigenvalue
problem; decision 0010): the equilibrium (b, w0) of arXiv:2108.11967 ("F21") is solved by
tracks/C-sidm/gravothermal/tmb.py and the lowest radial-pulsation eigenvalue omega_0^2 by
its finite-element solver `tmb.fem_lowest` (Chandrasekhar's equation, F21 main.tex:201-206).
Only the adiabatic index of the perturbation, gamma(r), changes between the variants:

  F21    gamma = 1 + p/u of the truncated distribution (F21 main.tex:172-175); reproduces
         the onset of the gravothermal package (run C-sidm-20261115-120722-38ab057,
         criteria.json "omega2_zero_F21gamma": b = 0.1, w0 = 3.58710, Z(0) = 0.6348)
  J_T    Gamma_1 = 1 + 1/c_v(theta) of a Juttner gas at the Tolman temperature of the model,
         theta_T = kT(r)/m = b/(1 - b w(r)) (F21 main.tex:118)
  J_E    Gamma_1 at theta_E, the temperature of the Juttner gas with the same number and
         energy density, <W>(theta_E) = rho/n (what collisions conserve locally)
  J_p    Gamma_1 at theta_p = p/n (ideal-gas temperature of the same n and p)
  J_pu   gamma = 1 + p/u of an untruncated Juttner gas at theta_T, 1 + theta/(<W> - 1)
         (F21's formula with the Juttner equation of state)

c_v = d<W>/dtheta per particle (k_B = 1) and <W>(theta) come from
tracks/C-sidm/collide/REFERENCES/mj.py (closed Bessel forms, quadrature below theta = 0.05),
tabulated here on a logarithmic grid and checked against mj.py at random points.
For a perfect gas p = n T the adiabatic index of the perturbation is
Gamma_1 = (d ln p/d ln n)_s = 1 + 1/c_v [BACKGROUND]; 5/3 for theta -> 0, 4/3 for
theta -> infinity.

Outputs: DIR/fluid_onset.json (roots in w0 and Z(0) per b, variant and resolution, the
central adiabatic indices, the tabulation check) and DIR/fluid_onset_figdata.npz.
"""

import argparse
import json
import math
import os
import sys
import time

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "gravothermal"))
sys.path.insert(0, os.path.join(HERE, "..", "collide", "REFERENCES"))

import numpy as np  # noqa: E402
from scipy.interpolate import CubicSpline  # noqa: E402
from scipy.optimize import brentq  # noqa: E402

import mj  # noqa: E402
import tmb  # noqa: E402

VARIANTS = ("F21", "J_T", "J_E", "J_p", "J_pu")

# ---------------------------------------------------------------------------- Juttner table
_LT = np.linspace(math.log(1e-7), math.log(1e3), 1601)
_KIN = np.asarray(mj.mean_kinetic(np.exp(_LT)), float)          # <W> - 1
_CV = np.asarray(mj.c_v(np.exp(_LT)), float)
_S_KIN = CubicSpline(_LT, np.log(_KIN))                           # ln<W-1>(ln theta)
_S_INV = CubicSpline(np.log(_KIN), _LT)                           # ln theta(ln<W-1>)
_S_CV = CubicSpline(_LT, _CV)


def theta_of_kinetic(k):
    k = np.asarray(k, float)
    return np.exp(_S_INV(np.log(np.clip(k, _KIN[0], _KIN[-1]))))


def c_v(theta):
    return _S_CV(np.log(np.clip(np.asarray(theta, float), 1e-7, 1e3)))


def kinetic(theta):
    return np.exp(_S_KIN(np.log(np.clip(np.asarray(theta, float), 1e-7, 1e3))))


def gamma1(theta):
    return 1.0 + 1.0 / c_v(theta)


def table_check(n=40, seed=3):
    rng = np.random.default_rng(seed)
    th = np.exp(rng.uniform(math.log(1e-4), math.log(10.0), n))
    e_cv = float(np.max(np.abs(c_v(th) / np.asarray(mj.c_v(th)) - 1)))
    e_k = float(np.max(np.abs(kinetic(th) / np.asarray(mj.mean_kinetic(th)) - 1)))
    kk = np.asarray(mj.mean_kinetic(th))
    e_inv = float(np.max(np.abs(theta_of_kinetic(kk) / th - 1)))
    return dict(points=n, theta_range=[1e-4, 10.0], max_rel_err_cv=e_cv,
                max_rel_err_kinetic=e_k, max_rel_err_inverse=e_inv,
                limits={"gamma1(theta=1e-6)": float(gamma1(1e-6)),
                        "gamma1(theta=1e3)": float(gamma1(1e3))})


# ---------------------------------------------------------------------------- local state
def local_state(b, w):
    """Hatted n, rho, p, u, gamma_F21 and theta_T at an array of cutoffs w (F21 units)."""
    w = np.clip(np.asarray(w, float), 0.0, None)
    out = np.zeros((6, len(w)))
    for i, wi in enumerate(w):
        if wi <= 0.0:
            out[:, i] = (0.0, 0.0, 0.0, 0.0, 5.0 / 3.0, b)
            continue
        In, Ir, Iu, Ip = tmb.integrals(b, wi)
        out[:, i] = (tmb.K4 * In, tmb.K4 * Ir, (2.0 / 3.0) * tmb.K4 * Ip, tmb.K4 * Iu,
                     1.0 + (2.0 / 3.0) * Ip / Iu, b / (1.0 - b * wi))
    return out


def gamma_profile(b, w, variant):
    n, rho, p, u, gF, thT = local_state(b, w)
    if variant == "F21":
        return gF
    if variant == "J_T":
        return gamma1(thT)
    if variant == "J_pu":
        return 1.0 + thT / kinetic(thT)
    good = n > 0
    th = np.full_like(n, 1e-7)
    if variant == "J_E":
        th[good] = theta_of_kinetic(np.clip(rho[good] / n[good] - 1.0, 1e-300, None))
    elif variant == "J_p":
        th[good] = p[good] / n[good]
    else:
        raise ValueError(variant)
    return gamma1(np.clip(th, 1e-7, None))


# ---------------------------------------------------------------------------- eigenvalue
def omega2(b, w0, variant, N=600):
    """Lowest omega^2 (F21 hatted units) with the adiabatic index of `variant`; nodes as
    tmb.pulsation (half uniform in r, half uniform in enclosed mass)."""
    eq, rt, Mt, wt = tmb.structure(b, w0)
    R = eq["R"]
    Msp = CubicSpline(rt, Mt)
    wsp = CubicSpline(rt, wt)
    mf = Mt / Mt[-1]
    nodes = np.unique(np.concatenate((np.linspace(0.0, R, N // 2 + 1),
                                      np.interp(np.linspace(0.0, 1.0, N // 2 + 1), mf, rt))))

    def coeff(rq):
        w = np.clip(wsp(rq), 0.0, None)
        rho, p, gF = tmb.local_vec(b, w)
        gam = gF if variant == "F21" else gamma_profile(b, w, variant)
        return Msp(rq), rho, p, gam, 1.0 - b * w

    ev, vec, trial, check = tmb.fem_lowest(nodes, coeff, 1)
    return float(ev[0]), eq


def root(b, variant, N, grid):
    vals = [omega2(b, w, variant, N)[0] for w in grid]
    for i in range(len(grid) - 1):
        if vals[i] > 0 >= vals[i + 1]:
            w0 = brentq(lambda v: omega2(b, v, variant, N)[0], grid[i], grid[i + 1],
                        xtol=1e-7, rtol=1e-10)
            eq = tmb.solve(b, w0)
            return dict(w0=w0, Z0=eq["Z0"], eps=eq["eps"], R_over_M=1.0 / eq["C"],
                        scan_w0=list(map(float, grid)), scan_omega2=vals)
    return dict(w0=None, Z0=None, scan_w0=list(map(float, grid)), scan_omega2=vals,
                note="no sign change of omega^2 on the grid")


def central_indices(b, w0):
    st = local_state(b, np.array([w0]))
    out = {v: float(gamma_profile(b, np.array([w0]), v)[0]) for v in VARIANTS}
    n, rho, p, u, gF, thT = st[:, 0]
    out.update(theta_T=float(thT), theta_E=float(theta_of_kinetic(rho / n - 1.0)),
               theta_p=float(p / n))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"),
                    help="output directory (default: $NRPIC_RUN_DIR of nrpic-run)")
    ap.add_argument("--b", type=float, nargs="*", default=[0.1, 0.2, 0.3, 0.5])
    ap.add_argument("--N", type=int, nargs="*", default=[600, 1200])
    ap.add_argument("--criteria", default=os.path.join(HERE, "..", "gravothermal", "results",
                                                       "criteria.json"))
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    crit = json.load(open(a.criteria))
    res = dict(table_check=table_check(), variants=VARIANTS, results={},
               criteria_source=os.path.relpath(os.path.abspath(a.criteria), os.path.join(HERE, "..")))
    print("table check:", res["table_check"], flush=True)
    fig = {}
    for b in a.b:
        c = crit[f"{b:g}"] if f"{b:g}" in crit else crit[str(b)]
        w_eps = c["max_eps"]["w0"]
        w_hi = c["gavg_eq_gcr"]["w0"] * 1.08
        w_lo = 0.35 * w_eps
        grid = np.linspace(w_lo, w_hi, 14)
        rb = dict(eps_max=dict(w0=w_eps, Z0=c["max_eps"]["Z0"]),
                  trial_root=dict(w0=c["gavg_eq_gcr"]["w0"], Z0=c["gavg_eq_gcr"]["Z0"]),
                  F21_onset_gravothermal=(dict(w0=c["omega2_zero_F21gamma"]["w0"],
                                               Z0=c["omega2_zero_F21gamma"]["Z0"])
                                          if c.get("omega2_zero_F21gamma") else None),
                  onset={})
        variants = VARIANTS if abs(b - 0.1) < 1e-12 else ("F21", "J_T", "J_E")
        Ns = a.N if abs(b - 0.1) < 1e-12 else a.N[:1]
        for v in variants:
            for N in Ns:
                t0 = time.time()
                r = root(b, v, N, grid)
                r["seconds"] = round(time.time() - t0, 1)
                if r["w0"] is not None:
                    r["central"] = central_indices(b, r["w0"])
                rb["onset"][f"{v}_N{N}"] = r
                print(f"b = {b:g} {v:5s} N = {N}: w0 = {r['w0']}, Z0 = {r['Z0']} "
                      f"({r['seconds']} s)", flush=True)
        # profiles of the adiabatic indices at the eps maximum and at the F21 onset
        for lab, w0 in (("epsmax", w_eps), ("F21onset", (rb["F21_onset_gravothermal"] or {}).get("w0"))):
            if w0 is None:
                continue
            eq, rt, Mt, wt = tmb.structure(b, w0, 600, 600)
            key = f"b{b:g}_{lab}"
            fig[f"{key}_r"] = rt / eq["R"]
            fig[f"{key}_M"] = Mt / Mt[-1]
            st = local_state(b, wt)
            fig[f"{key}_p"] = st[2] / st[2][0]
            for v in VARIANTS:
                fig[f"{key}_{v}"] = gamma_profile(b, wt, v)
        # omega^2 along the sequence for the figure (N = 600)
        ws = np.linspace(w_lo, w_hi, 24)
        fig[f"b{b:g}_seq_w0"] = ws
        fig[f"b{b:g}_seq_Z0"] = np.array([tmb.solve(b, w)["Z0"] for w in ws])
        for v in variants:
            fig[f"b{b:g}_seq_{v}"] = np.array([omega2(b, w, v, a.N[0])[0] for w in ws])
        res["results"][f"{b:g}"] = rb
    th = np.exp(np.linspace(math.log(1e-3), math.log(10.0), 300))
    fig["theta"] = th
    fig["gamma1"] = gamma1(th)
    fig["gamma_pu"] = 1.0 + th / kinetic(th)
    with open(os.path.join(a.out, "fluid_onset.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)
    np.savez_compressed(os.path.join(a.out, "fluid_onset_figdata.npz"), **fig)
    return 0


if __name__ == "__main__":
    sys.exit(main())
