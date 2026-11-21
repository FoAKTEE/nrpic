#!/usr/bin/env python3
"""Test B of periodic_diag (JOURNAL.md entry 0): linear stability of the discrete Z4c
gauge and light subsystems with the stencils of release core-v0.6 at nghost = 4.

Frozen coefficients about a homogeneous slice with conformal metric = identity, zero shift
(advection left out), lapse alpha0 and conformal factor chi0. Space: the sixth-order
centred first and second derivatives of athenak/src/utils/finite_diff.hpp (NGHOST == 4),
mixed derivatives as products of first derivatives (Dxy there), and the Kreiss-Oliger term
Diss<4> x diss with diss = <z4c> diss x 2^-8 x (-1) (z4c.cpp:177), whose symbol per
direction is -diss sin^8(theta/2)/dx. Time: classical RK4, R(z) = 1 + z + z^2/2 + z^3/6 +
z^4/24. Subsystems (z4c_calcrhs.cpp):

  shift   d_t beta^i = mu Gam^i - eta beta^i
          d_t Gam^i  = gt^jk d_j d_k beta^i + (1/3) gt^ij d_j d_k beta^k        (mu = 0.75)
  lapse   d_t alpha  = -2 alpha0 Khat - leak alpha,   d_t Khat = -chi0 gt^ij d_i d_j alpha
          (1+log; the relaxation (alpha/T) ln alpha linearized above alpha = 1: rate 1/T)
  light   a scalar wave of speed alpha0 sqrt(chi0) (the gt_ij, At_ij pair)

For each subsystem and each dt/dx the largest |R(lambda dt)| over the Brillouin zone
(theta in [0, pi]^3 by symmetry, pi included) is computed.

  python -I vonneumann.py --out DIR [--dx 0.01953125] [--alpha0 1.06] [--chi0 0.12]
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def symbols(th):
    """Return (s1, s2, ko) for the angle th = k dx: D1 -> i s1/dx, D2 -> -s2/dx^2,
    Kreiss-Oliger operator (without diss) -> -ko/dx."""
    s1 = 1.5 * np.sin(th) - 0.3 * np.sin(2 * th) + np.sin(3 * th) / 30.0
    s2 = 49.0 / 18.0 - 3.0 * np.cos(th) + 0.3 * np.cos(2 * th) - np.cos(3 * th) / 45.0
    ko = np.sin(th / 2.0) ** 8
    return s1, s2, ko


def rk4(z):
    return 1 + z + z ** 2 / 2 + z ** 3 / 6 + z ** 4 / 24


def theta_grid(n):
    t = np.linspace(0.0, np.pi, n)
    T1, T2, T3 = np.meshgrid(t, t, t, indexing="ij")
    return np.stack([T1.ravel(), T2.ravel(), T3.ravel()], axis=1)


def shift_eigs(th, dx, mu, eta, diss):
    """Eigenvalues (times dx) of the shift subsystem for every wave vector of th (N x 3):
    6 x 6 per wave vector; returned as lam*dx, with eta*dx folded in."""
    s1, s2, ko = symbols(th)
    S2 = s2.sum(axis=1)
    KO = diss * ko.sum(axis=1)
    n = th.shape[0]
    M = np.zeros((n, 6, 6))
    eye = np.eye(3)
    L = -(S2[:, None, None] * eye[None] + (1.0 / 3.0) * s1[:, :, None] * s1[:, None, :])
    # lam*dx: d_t beta = mu Gam - eta beta - KO beta/dx ; d_t Gam = L beta / dx^2 - KO Gam/dx
    # scale Gam by 1/dx so that every entry is (1/dx) x O(1): Gam' = Gam dx
    M[:, :3, :3] = -(KO[:, None, None] + eta * dx) * eye[None]
    M[:, :3, 3:] = mu * eye[None]
    M[:, 3:, :3] = L
    M[:, 3:, 3:] = -KO[:, None, None] * eye[None]
    return np.linalg.eigvals(M)


def wave_eigs(th, dx, c2, diss, damp_first=0.0):
    """lam*dx of a two-field wave system u' = -a v - damp u, v' = b D2 u with a b = c^2:
    lam = -KO -(damp dx)/2 +- sqrt(((damp dx)/2)^2 - c^2 S2)."""
    s1, s2, ko = symbols(th)
    S2 = s2.sum(axis=1)
    KO = diss * ko.sum(axis=1)
    d = damp_first * dx
    # 2x2 [[-KO-d, -1],[c2*S2, -KO]] (scaled): eigenvalues
    tr = -2 * KO - d
    det = (KO + d) * KO + c2 * S2
    disc = np.sqrt((tr / 2) ** 2 - det + 0j)
    return np.stack([tr / 2 + disc, tr / 2 - disc], axis=1)


def growth(eigs_dx, r):
    """Largest |R| over all eigenvalues for dt/dx = r."""
    return np.abs(rk4(eigs_dx * r)).max()


def threshold(eigs_dx, rs):
    g = np.array([growth(eigs_dx, r) for r in rs])
    bad = np.nonzero(g > 1.0 + 1e-10)[0]
    return g, (float(rs[bad[0]]) if bad.size else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=41)
    ap.add_argument("--diss", type=float, default=0.5)
    ap.add_argument("--mu", type=float, default=0.75)
    ap.add_argument("--eta", type=float, default=2.0)
    ap.add_argument("--leak", type=float, default=20.0)
    ap.add_argument("--alpha0", type=float, default=1.06)
    ap.add_argument("--chi0", type=float, default=0.12)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    th = theta_grid(args.n)
    rs = np.round(np.arange(0.30, 1.2001, 0.0025), 6)
    res = {"inputs": vars(args), "cases": {}}
    cases = {
        # (dx, description)
        "card_level4": 0.01953125,
        "uniform_root": 0.3125,
    }
    curves = {}
    for name, dx in cases.items():
        e_shift = shift_eigs(th, dx, args.mu, args.eta, args.diss)
        e_shift0 = shift_eigs(th, dx, args.mu, args.eta, 0.0)
        e_lapse = wave_eigs(th, dx, 2 * args.alpha0 * args.chi0, args.diss, args.leak)
        e_light = wave_eigs(th, dx, args.alpha0 ** 2 * args.chi0, args.diss)
        out = {"dx": dx}
        for lab, e in (("shift", e_shift), ("shift_nodiss", e_shift0),
                       ("lapse", e_lapse), ("light", e_light)):
            g, thr = threshold(e, rs)
            curves[(name, lab)] = g
            out[lab] = {"threshold_dt_over_dx": thr,
                        "max_abs_R_at": {f"{r:.3f}": float(growth(e, r)) for r in
                                         (0.60, 0.65, 0.70, 0.733, 0.746, 0.78, 0.80,
                                          0.81, 0.825, 0.90, 1.00)}}
        # where in the Brillouin zone the shift mode grows first
        if out["shift"]["threshold_dt_over_dx"] is not None:
            r = out["shift"]["threshold_dt_over_dx"] + 0.02
            gk = np.abs(rk4(e_shift * r)).max(axis=1)
            k = int(np.argmax(gk))
            out["shift"]["most_unstable_theta_over_pi_at_threshold_plus_0.02"] = \
                (th[k] / np.pi).round(3).tolist()
        res["cases"][name] = out
    # the corner estimate written in JOURNAL.md entry 0 (no dissipation)
    s2pi = symbols(np.array([np.pi]))[1][0]
    res["corner_estimate_no_diss"] = float(2 * np.sqrt(2) / np.sqrt(args.mu * (3 + 1 / 3) * s2pi))
    res["s2_at_pi"] = float(s2pi)
    with open(os.path.join(args.out, "vonneumann.json"), "w") as f:
        json.dump(res, f, indent=1)
    np.savez(os.path.join(args.out, "vonneumann_curves.npz"), rs=rs,
             **{f"{a}__{b}": v for (a, b), v in curves.items()})

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0), sharey=True)
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.16, top=0.9, wspace=0.06)
    cols = {"shift": fs.PAL["red"], "shift_nodiss": fs.PAL["orange"],
            "lapse": fs.PAL["blue"], "light": fs.PAL["green"]}
    labs = {"shift": "Gamma-driver shift", "shift_nodiss": "shift, no KO",
            "lapse": r"1+log lapse ($\alpha_0$=%.2f, $\chi_0$=%.2f)" % (args.alpha0, args.chi0),
            "light": "light"}
    for ax, name in zip(axs, cases):
        for lab in ("shift", "shift_nodiss", "lapse", "light"):
            ax.plot(rs, curves[(name, lab)], color=cols[lab], label=labs[lab],
                    ls="--" if lab == "shift_nodiss" else "-")
        ax.axhline(1.0, **fs.THIN)
        ax.set_yscale("log")
        ax.set_ylim(0.3, 3.0)
        ax.set_xlabel(r"$\Delta t/\Delta x$")
        ax.set_title({"card_level4": r"$\Delta x$ = 0.0195 (card, level 4)",
                      "uniform_root": r"$\Delta x$ = 0.3125 (uniform 64$^3$)"}[name])
        thr = res["cases"][name]["shift"]["threshold_dt_over_dx"]
        if thr:
            ax.axvline(thr, **fs.MASK_LINE)
    axs[0].set_ylabel(r"max $|R|$ over the Brillouin zone")
    axs[0].legend(loc="upper left", fontsize=8)
    fig.savefig(os.path.join(args.out, "fig_vonneumann.png"))
    print(json.dumps({k: {l: v[l]["threshold_dt_over_dx"] for l in
                          ("shift", "shift_nodiss", "lapse", "light")}
                      for k, v in res["cases"].items()}, indent=1))
    print("corner estimate", res["corner_estimate_no_diss"])
    for name in cases:
        print(name, res["cases"][name]["shift"]["max_abs_R_at"])


if __name__ == "__main__":
    main()
