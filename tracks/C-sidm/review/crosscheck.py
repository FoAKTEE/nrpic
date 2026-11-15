#!/usr/bin/env python3
"""Lead review of the four helper packages of C-sidm: independent cross-checks.

Each check compares two things that were produced independently, or a helper's result
with a computation written here. Predictions are in tracks/C-sidm/JOURNAL.md (lead entry
of 2026-11-15) before the run; outcomes after.

  X1  <v_Mol>(theta) of a Maxwell-Juttner gas: the closed form of collide/SPEC.md (R)
      against a direct three-dimensional Gauss quadrature over the two momenta written
      here (no Gondolo-Gelmini reduction, no Monte Carlo), and against collide's rate.py.
  X2  Truncated Maxwell-Boltzmann (F21, arXiv:2108.11967) sequences: scope's solver
      (scope/scripts/king_sequence.py) against gravothermal's (gravothermal/tmb.py), two
      independent implementations, at b = 0.1 and 0.5, and both against four rows of F21
      Table 1 transcribed here from main.tex:492, 495, 498, 501.
  X3  King model of arXiv:2009.08163 (= F21 family at b = 1): scope's solver against
      equilibria's evstatic.py (third independent implementation): E_b(y0), Z_c, and the
      first maximum.
  X4  The Knudsen-number definition fixed for the track (G0 REPORT section 4):
      Kn = lambda_c/H_c, lambda = 1/(rho0 sigma_m), H = (v1^2/(4 pi rho0))^(1/2),
      v1^2 = (p + 2 p_T)/(3 rho0). Computed from scope's King b = 1 model and compared with
      equilibria's knudsen.json (which uses the transport mean free path l = 0.77 lambda).
  X5  Onset of the radial instability of the b = 0.1 sequence with gamma = 1 + p/u
      (gravothermal's finite-element result Z(0) = 0.6348): sign of omega_0^2 on both sides
      at two resolutions.

Output in $NRPIC_RUN_DIR: crosscheck.json, fig_review_rate, fig_review_tmb, fig_review_onset.
"""
import json
import math
import os
import sys
import time

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

import numpy as np
from scipy import special

HERE = os.path.dirname(os.path.abspath(__file__))
TRACK = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(TRACK, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "python"))
for sub in ("scope/scripts", "gravothermal", "equilibria", "collide/REFERENCES"):
    sys.path.insert(0, os.path.join(TRACK, sub))

from nrpic import figstyle as fs   # noqa: E402
import matplotlib.pyplot as plt     # noqa: E402

OUT = os.environ.get("NRPIC_RUN_DIR", os.path.join(ROOT, "..", "..", "scratch", "C-sidm", "tmp"))
RES = {}


# ------------------------------------------------------------------ X1: <v_Mol>(theta)
def vmol_closed(theta):
    z = 1.0 / theta
    return 4.0 * special.kve(3, 2 * z) / (z * special.kve(2, z) ** 2)


def vmol_quad3(theta, nx=96, nmu=0):
    """<v_Mol> by Gauss quadrature over |p1|, |p2| (generalised Gauss-Laguerre in the kinetic
    energy, weight x^(1/2) e^-x) and over mu = cos(angle): closed-form mu integral if nmu = 0,
    Gauss-Legendre with nmu nodes otherwise. m = 1, d^3p = 4 pi p E dt, t = E - 1."""
    z = 1.0 / theta
    x, w = special.roots_genlaguerre(nx, 0.5)
    t = x / z
    E = 1.0 + t
    p = np.sqrt(t * (t + 2.0))
    # weight p E e^{-z t} dt = sqrt((t+2)/z) E * x^(1/2) e^{-x} dx / z
    wt = w * np.sqrt((t + 2.0) / z) * E / z
    E1, E2 = E[:, None], E[None, :]
    P1, P2 = p[:, None], p[None, :]
    if nmu == 0:
        gp = E1 * E2 + P1 * P2
        gm = E1 * E2 - P1 * P2
        F = lambda g: 0.5 * (g * np.sqrt(np.maximum(g * g - 1.0, 0.0)) - np.arccosh(np.maximum(g, 1.0)))
        A = (F(gp) - F(gm)) / (2.0 * P1 * P2 * E1 * E2)      # (1/2) int_{-1}^{1} v_Mol dmu
    else:
        mu, wm = np.polynomial.legendre.leggauss(nmu)
        g = E1[..., None] * E2[..., None] - P1[..., None] * P2[..., None] * mu
        v = np.sqrt(np.maximum(g * g - 1.0, 0.0)) / (E1[..., None] * E2[..., None])
        A = 0.5 * np.sum(v * wm, axis=-1)
    W = wt[:, None] * wt[None, :]
    return float(np.sum(W * A) / np.sum(W))


def x1():
    import rate
    thetas = [1e-3, 3e-3, 1e-2, 3e-2, 0.1, 0.3, 1.0, 3.0, 10.0, 100.0]
    rows = []
    for th in thetas:
        c = vmol_closed(th)
        q = vmol_quad3(th, nx=128)
        q2 = vmol_quad3(th, nx=64)
        qmu = vmol_quad3(th, nx=64, nmu=400)
        h = float(rate.vmol_mean(th))
        rows.append(dict(theta=th, closed=c, quad128=q, quad64=q2, quad64_mu400=qmu,
                         helper=h, rel_quad=(q - c) / c, rel_helper=(h - c) / c,
                         rel_quad_res=(q2 - q) / q, rel_mu=(qmu - q2) / q2))
    RES["X1"] = dict(rows=rows,
                     max_rel_quad=max(abs(r["rel_quad"]) for r in rows),
                     max_rel_helper=max(abs(r["rel_helper"]) for r in rows),
                     nr_limit_ratio_theta1e3=rows[0]["closed"] / math.sqrt(16e-3 / math.pi))
    return rows


# ------------------------------------------------------------------ X2: F21 sequences
F21_ROWS = {  # b = 0.1, main.tex lines 492, 495, 498, 501: w0, M, E_rest, eps, Z0, v0, <g>, gcr
    492: (0.6, 3.47240e-2, 3.51790e-2, 1.29311e-2, 8.71214e-2, 2.25450e-1, 1.65936, 1.37799),
    495: (1.9, 2.72897e-2, 2.81385e-2, 3.01659e-2, 2.96903e-1, 3.95398e-1, 1.64377, 1.47651),
    498: (3.2, 1.84498e-2, 1.91224e-2, 3.51754e-2, 5.47883e-1, 5.06132e-1, 1.62919, 1.57054),
    501: (4.0515, 1.42556e-2, 1.47424e-2, 3.30243e-2, 7.50107e-1, 5.66189e-1, 1.62117, 1.62117),
}


def x2():
    import king_sequence as ks
    import tmb
    out = dict(rows=[], grid={})
    for line, row in F21_ROWS.items():
        w0 = row[0]
        a = ks.model(0.1, w0)
        g = tmb.solve(0.1, w0)
        ga, gc = ks.adiabatic(0.1, w0)
        ent = dict(line=line, w0=w0)
        for key, ia, ig, ip in (("M", "M", "E", 1), ("E_rest", "E_rest", "Erest", 2),
                                ("eps", "eps_b", "eps", 3), ("Z0", "Z0", "Z0", 4),
                                ("v0", "v0", "v0", 5)):
            ent[key] = dict(paper=row[ip], scope=a[ia], grav=g[ig],
                            rel_scope=a[ia] / row[ip] - 1, rel_grav=g[ig] / row[ip] - 1,
                            rel_scope_grav=a[ia] / g[ig] - 1)
        ent["gavg"] = dict(paper=row[6], scope=ga, grav=g["gavg"])
        ent["gcr"] = dict(paper=row[7], scope=gc, grav=g["gcr"])
        out["rows"].append(ent)
    for b in (0.1, 0.5):
        w0s = np.linspace(0.3, 5.0, 48) if b == 0.1 else np.linspace(0.05, 1.0, 40)
        A = [ks.model(b, w) for w in w0s]
        G = [tmb.solve(b, w) for w in w0s]
        out["grid"][str(b)] = dict(
            w0=w0s.tolist(), Z0_scope=[x["Z0"] for x in A], eps_scope=[x["eps_b"] for x in A],
            Z0_grav=[x["Z0"] for x in G], eps_grav=[x["eps"] for x in G],
            max_rel_eps=float(max(abs(x["eps_b"] / y["eps"] - 1) for x, y in zip(A, G))),
            max_abs_Z0=float(max(abs(x["Z0"] - y["Z0"]) for x, y in zip(A, G))))
        lo, hi = (2.5, 4.0) if b == 0.1 else (0.4, 0.8)
        ms = ks.eps_max(b, lo, hi)
        mg = tmb.maximum(b, "eps", lo, hi)
        out["grid"][str(b)]["max_scope"] = dict(w0=ms["w0"], Z0=ms["Z0"], eps=ms["eps_b"])
        out["grid"][str(b)]["max_grav"] = dict(w0=mg["w0"], Z0=mg["Z0"], eps=mg["eps"])
    RES["X2"] = out
    return out


# ------------------------------------------------------------------ X3: King b = 1
def x3():
    import king_sequence as ks
    import evstatic as ev
    fam = ev.Family("king")
    y0s = np.linspace(0.05, 0.9, 35)
    rows = []
    for y in y0s:
        a = ks.model(1.0, -math.expm1(-y))      # w0 = 1 - e^{-y0}
        e = ev.integrate(fam, y)
        rows.append(dict(y0=float(y), eps_scope=a["eps_b"], eps_ev=e["Eb"], Z_scope=a["Z0"],
                         Z_ev=e["Zc_infinity"], C_scope=a["C"], C_ev=e["compactness"]))
    ms = ks.eps_max(1.0, -math.expm1(-0.25), -math.expm1(-0.45))
    yev, ebev = ev.first_maximum(fam)
    out = dict(rows=rows,
               max_rel_eps=max(abs(r["eps_scope"] / r["eps_ev"] - 1) for r in rows),
               max_abs_Z=max(abs(r["Z_scope"] - r["Z_ev"]) for r in rows),
               max_rel_C=max(abs(r["C_scope"] / r["C_ev"] - 1) for r in rows),
               ymax_scope=ms["y0"], eps_max_scope=ms["eps_b"], ymax_ev=yev, eps_max_ev=ebev,
               paper_ymax=0.334)   # 2009.08163 paper.tex:953 (printed 0.334)
    RES["X3"] = out
    return out


# ------------------------------------------------------------------ X4: Knudsen definition
def x4():
    import king_sequence as ks
    import evstatic as ev
    # King b = 1 at the E_b maximum computed in X3 (scope solver), hatted units -> M = 1
    y = RES["X3"]["ymax_ev"]
    a = ks.model(1.0, -math.expm1(-y))
    Mh = a["M"]
    rho0 = a["n_c"] * Mh ** 2           # rest-mass density, code units (m = 1)
    rho = a["rho_c"] * Mh ** 2
    p = a["p_c"] * Mh ** 2
    H_lead = math.sqrt(p / (4 * math.pi * rho0 ** 2))       # v1^2 = p/rho0 (isotropic)
    H_scope = math.sqrt(p / (4 * math.pi * rho ** 2))       # SCOPE.md section 4 (energy density)
    knsig_lead = 1.0 / (rho0 * H_lead)
    knsig_scope = 1.0 / (rho0 * H_scope)
    kj = json.load(open(os.path.join(TRACK, "equilibria", "results", "knudsen.json")))
    rows = []
    for m in kj["models"]:
        lead = 1.0 / (m["rho0_c"] * m["H_c"])
        rows.append(dict(tag=m["tag"], rho0_c=m["rho0_c"], H_c=m["H_c"],
                         Kn_sigma_lead=lead, Kn_sigma_equilibria=m["Kn_times_sigma_tilde"],
                         l_over_lambda=m["l_over_lambdaBSI"],
                         consistency=m["Kn_times_sigma_tilde"] / (lead * m["l_over_lambdaBSI"]) - 1))
    thr = [r for r in rows if r["tag"] == "king_y0p33403"][0]
    out = dict(y0=y, rho0_c=rho0, rho_c=rho, p_c=p, H_lead=H_lead, H_scope=H_scope,
               Kn_sigma_lead_scope_solver=knsig_lead, Kn_sigma_scope_def=knsig_scope,
               Kn_sigma_lead_equilibria=thr["Kn_sigma_lead"],
               rel_solver=knsig_lead / thr["Kn_sigma_lead"] - 1, models=rows,
               lead_range=[min(r["Kn_sigma_lead"] for r in rows), max(r["Kn_sigma_lead"] for r in rows)],
               cgs_per_code_at_1Msun=1.0 / 9.119e22)   # CONVERSION.md section 1 [BACKGROUND constants]
    RES["X4"] = out
    return out


# ------------------------------------------------------------------ X5: FEM onset
def x5():
    import tmb
    rows = []
    for w0 in (3.50, 3.58, 3.5871, 3.595, 3.68):
        for N in (600, 1200):
            r = tmb.pulsation(0.1, w0, N=N)
            rows.append(dict(w0=w0, N=N, omega2=float(r["omega2"][0]), Z0=r["eq"]["Z0"],
                             trial=float(r["trial"])))
    RES["X5"] = dict(rows=rows, helper_onset=dict(w0=3.58710, Z0=0.6348))
    return rows


# ------------------------------------------------------------------ figures
def figures():
    fs.use_style()
    P = fs.PAL
    # rate
    r = RES["X1"]["rows"]
    th = np.array([x["theta"] for x in r])
    fig, ax = plt.subplots(2, 1, figsize=(fs.COLUMN_WIDTH, 5.0), sharex=True)
    fig.subplots_adjust(left=0.2, right=0.96, bottom=0.1, top=0.97, hspace=0.05)
    tt = np.logspace(-3.2, 2.2, 200)
    ax[0].plot(tt, [vmol_closed(t) for t in tt], color=P["blue"], label="closed form (R)")
    ax[0].plot(th, [x["quad128"] for x in r], "o", color=P["red"], ms=4, label="3D quadrature (lead)")
    ax[0].plot(tt, np.sqrt(16 * tt / np.pi), **fs.GUIDE, label=r"$\sqrt{16\theta/\pi}$")
    ax[0].axhline(1.0, **fs.MASK_LINE)
    ax[0].set_xscale("log"); ax[0].set_yscale("log"); ax[0].set_ylim(0.02, 2)
    ax[0].set_ylabel(r"$\langle v_{\rm Mol}\rangle$")
    ax[0].legend(loc="lower right")
    ax[1].plot(th, np.abs([x["rel_quad"] for x in r]) + 1e-17, "o-", color=P["red"], ms=4,
               label="|quadrature/closed - 1|")
    ax[1].plot(th, np.abs([x["rel_helper"] for x in r]) + 1e-17, "s--", color=P["yellow"], ms=4,
               label="|rate.py/closed - 1|")
    ax[1].plot(th, np.abs([x["rel_quad_res"] for x in r]) + 1e-17, "^:", color="k", ms=4,
               label="|quad 64/128 - 1|")
    ax[1].set_yscale("log"); ax[1].set_xlabel(r"$\theta = T/m$")
    ax[1].set_ylabel("relative difference")
    ax[1].legend(loc="upper left", fontsize=8)
    fs.save(fig, os.path.join(OUT, "fig_review_rate"))
    plt.close(fig)
    # tmb / King sequences
    g = RES["X2"]["grid"]
    fig, ax = plt.subplots(2, 1, figsize=(fs.COLUMN_WIDTH, 5.4), sharex=True)
    fig.subplots_adjust(left=0.2, right=0.96, bottom=0.09, top=0.97, hspace=0.05)
    for b, col in (("0.1", P["blue"]), ("0.5", P["green"])):
        ax[0].plot(g[b]["Z0_scope"], g[b]["eps_scope"], color=col, label=f"scope, b = {b}")
        ax[0].plot(g[b]["Z0_grav"], g[b]["eps_grav"], "--", color=P["red"] if b == "0.1" else P["orange"],
                   label=f"gravothermal, b = {b}")
        rel = np.abs(np.array(g[b]["eps_scope"]) / np.array(g[b]["eps_grav"]) - 1)
        ax[1].plot(g[b]["Z0_grav"], rel + 1e-17, color=col, label=f"|scope/grav - 1|, b = {b}")
    k = RES["X3"]["rows"]
    ax[0].plot([x["Z_scope"] for x in k], [x["eps_scope"] for x in k], color=P["yellow"], label="scope, b = 1")
    ax[0].plot([x["Z_ev"] for x in k], [x["eps_ev"] for x in k], ":", color="k", label="evstatic, King")
    ax[1].plot([x["Z_ev"] for x in k], [abs(x["eps_scope"] / x["eps_ev"] - 1) + 1e-17 for x in k],
               color=P["yellow"], label="|scope/evstatic - 1|, King")
    for ent in RES["X2"]["rows"]:
        ax[0].plot(ent["Z0"]["paper"], ent["eps"]["paper"], "o", mfc="none", color="k", ms=6)
        ax[1].plot(ent["Z0"]["paper"], abs(ent["eps"]["rel_scope"]) + 1e-17, "o", mfc="none", color=P["blue"], ms=5)
        ax[1].plot(ent["Z0"]["paper"], abs(ent["eps"]["rel_grav"]) + 1e-17, "x", color=P["red"], ms=5)
    ax[0].plot([], [], "o", mfc="none", color="k", label="F21 Table 1 (b = 0.1)")
    ax[0].set_ylabel(r"$\varepsilon = 1 - M/E_{\rm rest}$")
    ax[0].set_ylim(0, 0.04); ax[0].legend(loc="lower right", fontsize=7, ncol=2)
    ax[1].set_yscale("log"); ax[1].set_xlabel(r"$Z(0)$"); ax[1].set_ylabel(r"relative difference in $\varepsilon$")
    ax[1].legend(loc="upper left", fontsize=7)
    ax[1].set_xlim(0, 1.2)
    fs.save(fig, os.path.join(OUT, "fig_review_tmb"))
    plt.close(fig)
    # onset
    rows = RES["X5"]["rows"]
    fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH, 3.0))
    fig.subplots_adjust(left=0.2, right=0.96, bottom=0.16, top=0.96)
    for N, col, mk in ((600, P["blue"], "o"), (1200, P["red"], "x")):
        sel = [x for x in rows if x["N"] == N]
        ax.plot([x["Z0"] for x in sel], [x["omega2"] for x in sel], mk + "-", color=col, ms=5, label=f"FEM, N = {N}")
    ax.axhline(0.0, **fs.THIN)
    ax.axvline(0.6348, **fs.MASK_LINE)
    ax.set_xlabel(r"$Z(0)$ ($b = 0.1$)"); ax.set_ylabel(r"$\omega_0^2$ (hatted units)")
    ax.legend(loc="upper right")
    fs.save(fig, os.path.join(OUT, "fig_review_onset"))
    plt.close(fig)


def main():
    t0 = time.time()
    os.makedirs(OUT, exist_ok=True)
    for name, fn in (("X1", x1), ("X2", x2), ("X3", x3), ("X4", x4), ("X5", x5)):
        t = time.time()
        fn()
        print(f"{name} done in {time.time() - t:.1f} s", flush=True)
    figures()
    RES["wall_s"] = time.time() - t0
    with open(os.path.join(OUT, "crosscheck.json"), "w") as f:
        json.dump(RES, f, indent=1, default=float)
    x1r, x2r, x3r, x4r = RES["X1"], RES["X2"], RES["X3"], RES["X4"]
    print("X1 max |quad/closed-1| =", x1r["max_rel_quad"], " max |rate.py/closed-1| =", x1r["max_rel_helper"])
    for b, gg in x2r["grid"].items():
        print(f"X2 b={b}: max rel eps scope/grav {gg['max_rel_eps']:.2e}, max |dZ0| {gg['max_abs_Z0']:.2e};"
              f" max scope {gg['max_scope']}, max grav {gg['max_grav']}")
    for ent in x2r["rows"]:
        print("X2 F21 line", ent["line"], {k: (round(v["rel_scope"], 7), round(v["rel_grav"], 7))
                                           for k, v in ent.items() if isinstance(v, dict) and "rel_scope" in v})
    print(f"X3 max rel eps {x3r['max_rel_eps']:.2e}, max |dZ| {x3r['max_abs_Z']:.2e}, ymax scope "
          f"{x3r['ymax_scope']:.6f} evstatic {x3r['ymax_ev']:.6f}")
    print(f"X4 Kn*sigma~ (lead def) scope solver {x4r['Kn_sigma_lead_scope_solver']:.3f}, equilibria "
          f"{x4r['Kn_sigma_lead_equilibria']:.3f}; scope def {x4r['Kn_sigma_scope_def']:.3f}; range "
          f"{x4r['lead_range']}")
    for r in RES["X5"]["rows"]:
        print("X5", r)


if __name__ == "__main__":
    main()
