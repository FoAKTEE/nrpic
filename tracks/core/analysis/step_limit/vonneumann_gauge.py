#!/usr/bin/env python3
"""Stability bound of the time integrator for the gauge sectors of Z4c as this code
evolves them (reference computation of the package step-limit, test T0 of
tracks/core/JOURNAL-step-limit.md).  Nothing here is a simulation: frozen coefficients,
one Fourier mode at a time.

Space: the stencils of athenak/src/utils/finite_diff.hpp, copied below with their lines
(first derivative Dx 24-63, second derivative Dxx 192-240, mixed derivative as the
product of two first derivatives, advective derivative Lx 1213-1305 with the side chosen
by the sign of the shift, Kreiss-Oliger operator Diss 1545-1611 times
diss = <z4c> diss x 2^(-2 ng) x (-1)^(ng/2+1) of z4c.cpp:177).  Time: the two-register
schemes of driver.cpp 108-177 exactly as z4c_tasks.cpp 155-184 and z4c_update.cpp apply
them; their stability polynomials are computed from the coefficients and compared with
the Taylor polynomial.

Sectors, linearized about a homogeneous slice with conformal metric g delta_ij (g is the
diagonal of the inverse conformal metric), lapse alpha0, conformal factor chi0, constant
shift b (z4c_calcrhs.cpp 587-596, 629, 658, 696-738; z4c_gauge_ext.hpp):

  shift  d_t beta^i = mu Gam^i - eta beta^i + sa b.d beta^i
         d_t Gam^i  = g d_j d_j beta^i + (g/3) d_i d_k beta^k + b.d Gam^i
         mu = shift_Gamma + alpha^2 shift_alpha2Gamma, sa = shift_advect
  lapse  d_t alpha  = -f alpha0 Khat - delta alpha + la b.d alpha
         d_t Khat   = -chi0 g d_j d_j alpha + b.d Khat
         f alpha0 = 2 alpha0 for 1+log; delta = lapse_leak (1 + ln(alpha0/alpha_ref))
         where the lapse exceeds its reference; la = lapse_advect
  light  a pair with squared speed alpha0^2 chi0 g, both members advected

Full model: the largest |R(lambda dt)| over the Brillouin zone.  Reduced model (what
Z4c::GaugeTimeStep evaluates in every cell): the eigenvalue pair of the grid-scale corner
theta = (pi, pi, pi), where the advective stencil is purely damping, and the damping of
the homogeneous mode, each against the first-exit radius rho(phi) of the stability region
along its ray.

  python vonneumann_gauge.py --out DIR [--n 41] [--quick]
"""
import argparse
import itertools
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

# ---------------------------------------------------------------------------------------
# stencils of finite_diff.hpp: offset -> coefficient (times 1/dx or 1/dx^2)
D1 = {2: {-1: -1/2, 1: 1/2},
      3: {-2: 1/12, 2: -1/12, -1: -2/3, 1: 2/3},
      4: {-3: -1/60, 3: 1/60, -2: 3/20, 2: -3/20, -1: -3/4, 1: 3/4}}
D2 = {2: {-1: 1.0, 1: 1.0, 0: -2.0},
      3: {-2: -1/12, 2: -1/12, -1: 4/3, 1: 4/3, 0: -5/2},
      4: {-3: 1/90, 3: 1/90, -2: -3/20, 2: -3/20, -1: 3/2, 1: 3/2, 0: -49/18}}
# advective derivative for a positive speed ("dr" of Lx; "dl" is its mirror image)
ADV = {2: {2: -0.5, 1: 2.0, 0: -1.5},
       3: {3: 1/12, 2: -6/12, 1: 18/12, 0: -10/12, -1: -3/12},
       4: {4: -1/60, 3: 2/15, 2: -1/2, 1: 4/3, 0: -7/12, -1: -2/5, -2: 1/30}}
KO = {2: {-2: 1.0, 2: 1.0, -1: -4.0, 1: -4.0, 0: 6.0},
      3: {-3: 1.0, 3: 1.0, -2: -6.0, 2: -6.0, -1: 15.0, 1: 15.0, 0: -20.0},
      4: {-4: 1.0, 4: 1.0, -3: -8.0, 3: -8.0, -2: 28.0, 2: 28.0, -1: -56.0, 1: -56.0,
          0: 70.0}}
# two-register integrators of driver.cpp: (gam0, gam1, beta, delta)
RK = {
    "rk2": ([0.0, 0.5], [1.0, 0.5], [1.0, 0.5], None),
    "rk3": ([0.0, 0.25, 2/3], [1.0, 0.75, 1/3], [1.0, 0.25, 2/3], None),
    "rk4": ([0.0, 0.121098479554482, -3.843833699660025, 0.546370891121863],
            [1.0, 0.721781678111411, 2.121209265338722, 0.198653035682705],
            [1.193743905974738, 0.099279895495783, 1.131678018054042, 0.310665766509336],
            [1.0, 0.217683334308543, 1.065841341361089, 0.0]),
}
NTAB = 129   # entries of the first-exit table, as in z4c_newdt_gauge.cpp


def sym(st, th):
    """Fourier symbol sum_j c_j exp(i j theta) of a stencil."""
    out = np.zeros(np.shape(th), dtype=complex)
    for j, c in st.items():
        out = out + c * np.exp(1j * j * np.asarray(th))
    return out


def diss_factor(ng, diss):
    return diss * 2.0 ** (-2 * ng) * (-1.0 if ng % 2 == 0 else 1.0)


def symbols(th, ng):
    """s1, s2, ko (real, D1 -> i s1/dx, D2 -> -s2/dx^2, KO x factor -> -diss ko/dx) and
    the complex symbol adv of the advective derivative for a positive speed."""
    s1 = sym(D1[ng], th).imag
    s2 = -sym(D2[ng], th).real
    ko = -(sym(KO[ng], th).real * diss_factor(ng, 1.0))
    adv = sym(ADV[ng], th)
    return s1, s2, ko, adv


def stab_poly(name):
    """Stability polynomial (coefficients, lowest order first) of a two-register scheme
    applied to y' = lambda y as the code applies it."""
    g0, g1, be, de = RK[name]
    P = np.polynomial.Polynomial
    u0 = P([1.0])
    u1 = P([0.0])
    z = P([0.0, 1.0])
    for s in range(len(g0)):
        if s == 0:
            u1 = u0
        elif de is not None:
            u1 = u1 + de[s] * u0
        u0 = g0[s] * u0 + g1[s] * u1 + be[s] * z * u0
    return u0.coef


def taylor(order):
    c = [1.0]
    for k in range(1, order + 1):
        c.append(c[-1] / k)
    return np.array(c)


def R(coef, z):
    out = np.zeros(np.shape(z), dtype=complex) + coef[-1]
    for c in coef[-2::-1]:
        out = out * z + c
    return out


def first_exit(coef, lam, rmax=12.0, step=0.01, tol=1e-12):
    """Smallest r > 0 at which max |R(r lam)| over the array lam exceeds 1 (bisected)."""
    lam = np.asarray(lam).ravel()
    r = step
    while r <= rmax:
        if np.abs(R(coef, r * lam)).max() > 1.0 + tol:
            lo, hi = r - step, r
            for _ in range(40):
                mid = 0.5 * (lo + hi)
                if np.abs(R(coef, mid * lam)).max() > 1.0 + tol:
                    hi = mid
                else:
                    lo = mid
            return lo
        r += step
    return np.inf


def rho_table(coef, ntab=NTAB):
    """First-exit radius of the stability region along the ray at the angle phi from the
    negative real axis, phi_i = (pi/2) i/(ntab-1)."""
    tab = np.zeros(ntab)
    for i in range(ntab):
        phi = 0.5 * np.pi * i / (ntab - 1)
        tab[i] = first_exit(coef, np.array([np.exp(1j * (np.pi - phi))]), step=0.002)
    return tab


def rho_lookup(tab, re, im):
    """The table as the kernel reads it: the smaller of the two neighbouring entries."""
    phi = np.arctan2(abs(im), -re)
    phi = min(max(phi, 0.0), 0.5 * np.pi)
    x = phi / (0.5 * np.pi) * (len(tab) - 1)
    i = min(int(x), len(tab) - 2)
    return min(tab[i], tab[i + 1])


# ---------------------------------------------------------------------------------------
# full model

def theta_grid(n, signed):
    """theta in [0, pi]^3 (n points per direction, pi included); the directions flagged in
    signed run over [-pi, pi]."""
    axes = []
    for d in range(3):
        if signed[d]:
            axes.append(np.linspace(-np.pi, np.pi, 2 * n - 1))
        else:
            axes.append(np.linspace(0.0, np.pi, n))
    T = np.meshgrid(*axes, indexing="ij")
    return np.stack([t.ravel() for t in T], axis=1)


def pair_eigs(a, d, prod):
    """Eigenvalues of [[a, p], [q, d]] with p q = -prod."""
    tr2 = 0.5 * (a + d)
    disc = np.sqrt((0.5 * (a - d)) ** 2 - prod + 0j)
    return np.stack([tr2 + disc, tr2 - disc], axis=-1)


def full_eigs(sector, th, ng, p):
    """lambda dx of a sector for every wave vector of th.  p: diss, g, b (3 speeds >= 0),
    and per sector mu, etadx, sa | c2, deltadx, la | c2."""
    s1, s2, ko, adv = symbols(th, ng)
    kod = p["diss"] * ko.sum(axis=1)
    b = np.asarray(p.get("b", (0.0, 0.0, 0.0)))
    advc = (adv * b[None, :]).sum(axis=1)
    S2 = p["g"] * s2.sum(axis=1)
    if sector == "shift":
        a = -kod - p["etadx"] + p.get("sa", 1.0) * advc
        d = -kod + advc
        lon = pair_eigs(a, d, p["mu"] * (S2 + p["g"] * (s1 ** 2).sum(axis=1) / 3.0))
        tra = pair_eigs(a, d, p["mu"] * S2)
        return np.concatenate([lon, tra], axis=-1)
    if sector == "lapse":
        a = -kod - p["deltadx"] + p.get("la", 1.0) * advc
        d = -kod + advc
        return pair_eigs(a, d, p["c2"] * S2 / p["g"] * p["g"])
    if sector == "light":
        a = -kod + advc
        return pair_eigs(a, a, p["c2"] * S2 / p["g"] * p["g"])
    raise ValueError(sector)


def shift_eigs_6x6(th, ng, p):
    """The shift sector as the 6 x 6 matrix per wave vector (no advection), to check the
    split into longitudinal and transverse pairs."""
    s1, s2, ko, _ = symbols(th, ng)
    kod = p["diss"] * ko.sum(axis=1)
    n = th.shape[0]
    M = np.zeros((n, 6, 6))
    eye = np.eye(3)
    L = -p["g"] * (s2.sum(axis=1)[:, None, None] * eye[None]
                   + (1.0 / 3.0) * s1[:, :, None] * s1[:, None, :])
    M[:, :3, :3] = -(kod[:, None, None] + p["etadx"]) * eye[None]
    M[:, :3, 3:] = p["mu"] * eye[None]
    M[:, 3:, :3] = L
    M[:, 3:, 3:] = -kod[:, None, None] * eye[None]
    return np.linalg.eigvals(M)


# ---------------------------------------------------------------------------------------
# reduced model: the formulas of Z4c::GaugeTimeStep, in units of dx (cubic cells)

def corner_consts(ng):
    s1, s2, ko, adv = symbols(np.array([np.pi]), ng)
    return float(s2[0]), float(-adv[0].real), float(abs(adv[0].imag))


def reduced_bound(tab, ng, om2, diss, bsum, d1x, d2x, a1=1.0, a2=1.0):
    """Largest stable dt/dx of a pair: om2 = sum_d (squared speed)_d (the code multiplies
    by s2max), diss, bsum = sum_d |b_d|, d1x, d2x the dampings of the two members times
    dx without advection, a1, a2 their advection factors."""
    s2max, aadv, _ = corner_consts(ng)
    kod = 3.0 * diss
    adv = aadv * bsum
    e1 = d1x + a1 * adv
    e2 = d2x + a2 * adv
    m = kod + 0.5 * (e1 + e2)
    h = 0.5 * (e1 - e2)
    disc = h * h - s2max * om2
    if disc <= 0.0:
        re, im = -m, np.sqrt(-disc)
    else:
        re, im = -(m + np.sqrt(disc)), 0.0
    mod = np.hypot(re, im)
    r = rho_lookup(tab, re, im) / mod if mod > 0.0 else np.inf
    dh = max(d1x, d2x)                      # homogeneous mode
    if dh > 0.0:
        r = min(r, tab[0] / dh)
    return r


def reduced_sector(tab, ng, sector, p):
    b = np.asarray(p.get("b", (0.0, 0.0, 0.0)))
    bsum = float(np.abs(b).sum())
    if sector == "shift":
        return reduced_bound(tab, ng, 3.0 * p["mu"] * p["g"], p["diss"], bsum,
                             p["etadx"], 0.0, p.get("sa", 1.0), 1.0)
    if sector == "lapse":
        return reduced_bound(tab, ng, 3.0 * p["c2"], p["diss"], bsum, p["deltadx"], 0.0,
                             p.get("la", 1.0), 1.0)
    return reduced_bound(tab, ng, 3.0 * p["c2"], p["diss"], bsum, 0.0, 0.0)


# ---------------------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=41)
    ap.add_argument("--quick", action="store_true", help="smaller parameter survey")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    res = {"n": args.n}

    # ---- (a) closed forms of the symbols and the integrators
    th = np.linspace(0.0, np.pi, 201)
    chk = {}
    for ng in (2, 3, 4):
        s1, s2, ko, adv = symbols(th, ng)
        chk[f"ng{ng}"] = {
            "ko_minus_sin_power": float(np.abs(ko - np.sin(th / 2) ** (2 * ng)).max()),
            "s2_at_pi": float(s2[-1]), "s1_at_pi": float(s1[-1]),
            "adv_at_pi": [float(adv[-1].real), float(adv[-1].imag)],
            "s2_monotonic": bool(np.all(np.diff(s2) > 0)),
            "s2_minus_s1sq_min": float((s2 - s1 ** 2).min()),
            "max_s2_plus_s1sq_over_3": float((s2 + s1 ** 2 / 3).max()),
        }
    coefs = {}
    for name, order in (("rk2", 2), ("rk3", 3), ("rk4", 4)):
        c = stab_poly(name)
        coefs[name] = c
        chk[name] = {"poly": c.tolist(),
                     "minus_taylor": float(np.abs(c - taylor(order)).max())}
    tabs = {name: rho_table(coefs[name]) for name in ("rk3", "rk4")}
    for name in tabs:
        chk[name]["rho_real_axis"] = float(tabs[name][0])
        chk[name]["rho_imag_axis"] = float(tabs[name][-1])
        chk[name]["rho_min"] = float(tabs[name].min())
        chk[name]["rho_max"] = float(tabs[name].max())
        chk[name]["rho_max_step"] = float(np.abs(np.diff(tabs[name])).max())
    res["checks"] = chk
    np.savez(os.path.join(args.out, "rho_tables.npz"), **tabs)

    # ---- (b) Track A's cases (its vonneumann.py: mu 0.75, eta 2, diss 0.5, leak 20,
    #          alpha0 1.06, chi0 0.12, nghost 4, RK4), full scan and reduced model
    th0 = theta_grid(args.n, (False, False, False))
    rk4 = coefs["rk4"]
    a_claims = {"card_level4": {"shift": 0.685, "shift_nodiss": 0.77, "lapse": 0.97},
                "uniform_root": {"shift": 0.65, "lapse": 0.405},
                "mu0.3_level4": {"shift": 0.94}, "mu0.3_root": {"shift": 0.90}}
    cases = {}
    curves = {}
    rs = np.round(np.arange(0.30, 1.6001, 0.0025), 6)
    for label, dx, mu in (("card_level4", 0.01953125, 0.75), ("uniform_root", 0.3125, 0.75),
                          ("mu0.3_level4", 0.01953125, 0.3), ("mu0.3_root", 0.3125, 0.3)):
        al, ch = 1.06, 0.12
        sets = {
            "shift": ("shift", dict(diss=0.5, g=1.0, mu=mu, etadx=2.0 * dx)),
            "shift_nodiss": ("shift", dict(diss=0.0, g=1.0, mu=mu, etadx=2.0 * dx)),
            "lapse": ("lapse", dict(diss=0.5, g=1.0, c2=2 * al * ch, deltadx=20.0 * dx)),
            "light": ("light", dict(diss=0.5, g=1.0, c2=al * al * ch)),
        }
        out = {"dx": dx}
        for key, (sec, p) in sets.items():
            e = full_eigs(sec, th0, 4, p)
            full = first_exit(rk4, e)
            red = reduced_sector(tabs["rk4"], 4, sec, p)
            # the threshold as Track A read it: first point of its grid with |R| > 1+1e-10
            g = np.array([np.abs(R(rk4, r * e)).max() for r in rs])
            bad = np.nonzero(g > 1.0 + 1e-10)[0]
            out[key] = {"full": full, "reduced": red,
                        "grid_0.0025": float(rs[bad[0]]) if bad.size else None,
                        "track_A": a_claims.get(label, {}).get(key)}
            if key in ("shift", "shift_nodiss") and label in ("card_level4",
                                                             "uniform_root"):
                e6 = shift_eigs_6x6(th0, 4, p)
                out[key]["full_6x6"] = first_exit(rk4, e6)
            if label in ("card_level4", "uniform_root"):
                curves[(label, key)] = g
            # where the mode that fails first sits
            gk = np.abs(R(rk4, (full + 0.01) * e)).max(axis=-1)
            out[key]["first_unstable_theta_over_pi"] = \
                (np.abs(th0[int(np.argmax(gk))]) / np.pi).round(3).tolist()
        cases[label] = out
    res["track_A_cases"] = cases
    # the relaxation alone: lapse_leak x dt at the grid scale and for the homogeneous mode
    p = dict(diss=0.5, g=1.0, c2=2 * 1.06 * 0.12, deltadx=20.0 * 0.3125)
    res["leak_root"] = {
        "leak_dt_full": first_exit(rk4, full_eigs("lapse", th0, 4, p)) * p["deltadx"],
        "leak_dt_reduced": reduced_sector(tabs["rk4"], 4, "lapse", p) * p["deltadx"],
        "leak_dt_homogeneous": float(tabs["rk4"][0])}
    # flat space: alpha0 = chi0 = 1 (asymptotically flat regions), mu = 0.75 and 1.0
    flat = {}
    for diss in (0.0, 0.1, 0.5):
        row = {}
        for key, sec, p in (
                ("shift_mu0.75", "shift", dict(diss=diss, g=1.0, mu=0.75, etadx=0.0)),
                ("shift_mu1.0", "shift", dict(diss=diss, g=1.0, mu=1.0, etadx=0.0)),
                ("lapse_1+log", "lapse", dict(diss=diss, g=1.0, c2=2.0, deltadx=0.0)),
                ("light", "light", dict(diss=diss, g=1.0, c2=1.0))):
            row[key] = {"full": first_exit(rk4, full_eigs(sec, th0, 4, p)),
                        "reduced": reduced_sector(tabs["rk4"], 4, sec, p)}
        flat[f"diss{diss}"] = row
    res["flat_space_rk4_ng4"] = flat

    # ---- (c) survey: reduced model against the full scan
    n2 = 17 if args.quick else 25
    grids = {False: theta_grid(n2, (False, False, False)),
             True: theta_grid(n2, (True, True, True))}
    survey = []
    disses = (0.0, 0.1, 0.5, 1.0) if not args.quick else (0.0, 0.5)
    damps = (0.0, 0.04, 0.4, 1.5, 6.0) if not args.quick else (0.0, 0.4, 6.0)
    c2s = (0.25, 1.0, 2.0)
    bs = ((0.0, 0.0, 0.0), (0.3, 0.0, 0.0), (1.0, 0.0, 0.0), (0.4, 0.4, 0.4))
    integs = ("rk4", "rk3")
    ngs = (4, 3, 2) if not args.quick else (4,)
    for integ, ng, diss, damp, b in itertools.product(integs, ngs, disses, damps, bs):
        thg = grids[bool(np.any(np.asarray(b) > 0))]
        for sec, p in (("shift", dict(diss=diss, g=1.0, mu=0.75, etadx=damp, b=b)),
                       ("lapse", dict(diss=diss, g=1.0, c2=c2s[2], deltadx=damp, b=b)),
                       ("lapse", dict(diss=diss, g=1.0, c2=c2s[0], deltadx=damp, b=b)),
                       ("light", dict(diss=diss, g=1.0, c2=c2s[1], b=b))):
            if sec == "light" and damp != damps[0]:
                continue
            full = first_exit(coefs[integ], full_eigs(sec, thg, ng, p))
            red = reduced_sector(tabs[integ], ng, sec, p)
            survey.append({"integ": integ, "ng": ng, "sector": sec, "diss": diss,
                           "dampdx": damp, "b": list(b), "c2": p.get("c2", p.get("mu")),
                           "full": full, "reduced": red,
                           "ratio": (red / full) if np.isfinite(full) and full > 0
                           else None})
    res["survey"] = survey
    rat = np.array([s["ratio"] for s in survey if s["ratio"] is not None])
    nob = np.array([s["ratio"] for s in survey
                    if s["ratio"] is not None and not any(s["b"])])
    res["survey_summary"] = {
        "cases": len(survey), "ratio_min": float(rat.min()), "ratio_max": float(rat.max()),
        "zero_shift_ratio_min": float(nob.min()), "zero_shift_ratio_max": float(nob.max()),
        "worst": sorted([s for s in survey if s["ratio"] is not None],
                        key=lambda s: -s["ratio"])[:8]}

    with open(os.path.join(args.out, "vonneumann_gauge.json"), "w") as f:
        json.dump(res, f, indent=1)

    # ---- figures
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, os.path.join(REPO, "python", "nrpic"))
    import figstyle as fs
    fs.use_style()

    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2), sharey=True)
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.16, top=0.9, wspace=0.06)
    cols = {"shift": fs.PAL["red"], "shift_nodiss": fs.PAL["orange"],
            "lapse": fs.PAL["blue"], "light": fs.PAL["green"]}
    labs = {"shift": "Gamma-driver shift", "shift_nodiss": "shift, no dissipation",
            "lapse": "1+log lapse with relaxation", "light": "light"}
    for ax, name in zip(axs, ("card_level4", "uniform_root")):
        for key in ("shift", "shift_nodiss", "lapse", "light"):
            ax.plot(rs, curves[(name, key)], color=cols[key], label=labs[key],
                    ls="--" if key == "shift_nodiss" else "-")
            red = cases[name][key]["reduced"]
            if np.isfinite(red) and red < rs[-1]:
                ax.plot([red], [1.0], marker="v", ms=7, color=cols[key], mec="k",
                        mew=0.6, ls="none")
        ax.axhline(1.0, **fs.THIN)
        ax.set_yscale("log")
        ax.set_ylim(0.3, 3.0)
        ax.set_xlim(rs[0], rs[-1])
        ax.set_xlabel(r"$\Delta t/\Delta x$")
        ax.set_title({"card_level4": r"$\Delta x$ = 0.0195 (level 4 of the card deck)",
                      "uniform_root": r"$\Delta x$ = 0.3125 (uniform 64$^3$)"}[name],
                     fontsize=10)
    axs[0].set_ylabel(r"largest $|R|$ over the Brillouin zone")
    axs[0].legend(loc="upper left", fontsize=8)
    fig.savefig(os.path.join(args.out, "fig_vonneumann.png"), dpi=150)
    plt.close(fig)

    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.4))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.15, top=0.92, wspace=0.22)
    ax = axs[0]
    xx = np.linspace(-3.4, 0.6, 321)
    yy = np.linspace(0.0, 3.4, 273)
    X, Y = np.meshgrid(xx, yy)
    for name, col in (("rk4", fs.PAL["blue"]), ("rk3", fs.PAL["orange"])):
        ax.contour(X, Y, np.abs(R(coefs[name], X + 1j * Y)), levels=[1.0], colors=[col])
        phi = 0.5 * np.pi * np.arange(NTAB) / (NTAB - 1)
        ax.plot(-tabs[name] * np.cos(phi), tabs[name] * np.sin(phi), ls="none",
                marker=".", ms=2.5, color=col, label=name + r": $\rho(\varphi)$ table")
    for name, key, mk in (("card_level4", "shift", "o"), ("uniform_root", "shift", "s"),
                          ("card_level4", "lapse", "^"), ("uniform_root", "lapse", "D")):
        dxv = cases[name]["dx"]
        pset = {"shift": dict(diss=0.5, g=1.0, mu=0.75, etadx=2.0 * dxv),
                "lapse": dict(diss=0.5, g=1.0, c2=2 * 1.06 * 0.12, deltadx=20.0 * dxv)}[key]
        ec = full_eigs(key, np.array([[np.pi, np.pi, np.pi]]), 4, pset).ravel()
        zc = ec * cases[name][key]["full"]
        zc = zc[np.argmax(np.abs(R(rk4, zc)))]
        ax.plot([zc.real], [abs(zc.imag)], marker=mk, ms=6, color=cols[key], mec="k",
                mew=0.6, ls="none", label=f"{labs[key].split()[0]} corner, "
                + ("level 4" if name == "card_level4" else "root"))
    ax.axhline(0.0, **fs.THIN)
    ax.axvline(0.0, **fs.THIN)
    ax.set_xlabel(r"Re $\lambda\,\Delta t$")
    ax.set_ylabel(r"Im $\lambda\,\Delta t$")
    ax.set_xlim(-3.4, 0.6)
    ax.set_ylim(-0.1, 3.4)
    ax.set_aspect("equal")
    ax.legend(loc="upper left", fontsize=6.5)
    ax = axs[1]
    mk = {"shift": "o", "lapse": "^", "light": "s"}
    for sec in ("shift", "lapse", "light"):
        for zero, face in ((True, None), (False, "none")):
            sel = [s for s in survey if s["sector"] == sec and s["ratio"] is not None
                   and (not any(s["b"])) == zero]
            ax.plot([s["full"] for s in sel], [s["ratio"] for s in sel], ls="none",
                    marker=mk[sec], ms=4, color=cols[sec],
                    mfc=cols[sec] if face is None else "none",
                    label=sec + (", zero shift" if zero else r", $|\beta|>0$"))
    ax.axhline(1.0, **fs.THIN)
    ax.set_xscale("log")
    ax.set_xlabel(r"full scan: largest stable $\Delta t/\Delta x$")
    ax.set_ylabel("reduced model / full scan")
    ax.legend(loc="lower left", fontsize=7, ncol=2)
    fig.savefig(os.path.join(args.out, "fig_reduced.png"), dpi=150)
    plt.close(fig)

    # ---- summary on the terminal
    print(json.dumps(res["checks"], indent=1))
    for label, out in cases.items():
        for key in ("shift", "shift_nodiss", "lapse", "light"):
            o = out[key]
            print(f"{label:14s} {key:13s} full {o['full']:.4f} reduced {o['reduced']:.4f}"
                  f" grid {o['grid_0.0025']} A {o['track_A']}"
                  f" at {o['first_unstable_theta_over_pi']}"
                  + (f" 6x6 {o['full_6x6']:.4f}" if "full_6x6" in o else ""))
    print("leak_root", res["leak_root"])
    print("flat", json.dumps(flat))
    print("survey", json.dumps(res["survey_summary"], indent=1))


if __name__ == "__main__":
    main()
