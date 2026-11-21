"""T6: single-body limit of HRNA on inclined parabolic orbits in Kerr (a = 0.9), against
python/nrpic (geodesic.integrate in Cartesian Kerr-Schild, kerr.invariants for E, L_z, Q).

Pair force off (member masses 1e-300).  Orbits of 2402.02178's set-up: E = 1, r_p = 10 M,
L_z = the two ends of Eq. (Lz) (Q = 0), -3, 0, 2.2 (Fig. compF12's value), released at
BL r = 100 M in the equatorial plane moving inwards; plus r_p = 6 M at both ends of Eq. (Lz)
(the zoom-whirl case of Fig. InclD).  Checks: positions, conservation of E, L_z, Q along the
HRNA trajectory, the pericentre of the reference (BL r at dr/dt = 0) against the requested r_p
(tests Eq. rp, the Q formula and the initial data), and Q at release against Eq. (rp).

Run: <venv>/bin/python -I tests/t6_kerr_single.py <outdir>
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
sys.path.insert(0, PKG)
sys.path.insert(0, os.path.join(PKG, "scripts"))
import hrna_incl as H  # noqa: E402
import hrna  # noqa: E402
from nrpic import geodesic, kerr  # noqa: E402

A = 0.9
R0 = 100.0
TAU0 = 2 * math.pi * math.sqrt(0.125 ** 3 / 6.25e-6)     # 2402's binary period in M (main.tex:504-506)


def u_from_v(x, v, a):
    g, gi, dg = np.zeros((4, 4)), np.zeros((4, 4)), np.zeros((3, 4, 4))
    hrna.metric(hrna.COORDS_CKS, x, 1.0, a, g, gi, dg)
    xd = np.array([1.0, *v])
    gam = 1 / math.sqrt(-(xd @ g @ xd))
    return gam * (g[1:, :] @ xd)


def bl_r(x):
    return float(kerr.cks_radius(np.asarray(x, float), A))


def one_pair(rp, Lza, Lzb):
    xa, va, Qa = H.parabolic_state("cks", A, rp, Lza, R0)
    xb, vb, Qb = H.parabolic_state("cks", A, rp, Lzb, R0)
    # both orbits start at the same point: move the second one by pi/2 about the spin axis
    # (an exact symmetry of Kerr in Cartesian Kerr-Schild coordinates)
    Rz = H.rot_z(math.pi / 2)
    xb, vb = Rz @ xb, Rz @ vb
    y0 = np.concatenate([xa, va, xb, vb])
    m = 1e-300
    t_end = 6.0 * (math.sqrt(2.0) / 3.0) * 2 * R0 ** 1.5 if rp > 7 else 6000.0
    out = hrna.integrate(hrna.LAW_HRNA, hrna.COORDS_CKS, hrna.PAIR_GRAVITY, 1.0, A, m, m, 0.0, 0.0,
                         y0, 1.0, 1e-12, 1e-14, 1e300, 1e300, 0.0, t_end, 10 ** 7, 1.0, 10 ** 6,
                         hrna._A, hrna._B, hrna._C, hrna._E3, hrna._E5, hrna._work())
    t, Y = np.array(out[4]), np.array(out[5])
    res, curves = [], []
    for k, (x0, v0, Lz, Q0) in enumerate(((xa, va, Lza, Qa), (xb, vb, Lzb, Qb))):
        X = Y[:, 6 * k:6 * k + 3]
        V = Y[:, 6 * k + 3:6 * k + 6]
        rr = np.array([bl_r(x) for x in X])
        # stop the comparison when the body has come back out to r0 (or at t_end)
        back = np.where((np.arange(len(t)) > np.argmin(rr)) & (rr >= R0))[0]
        n = back[0] + 1 if len(back) else len(t)
        tk, X, V, rr = t[:n], X[:n], V[:n], rr[:n]
        u0 = u_from_v(x0, v0, A)
        ref = geodesic.integrate("cks", x0, u0, tk[-1], t_eval=tk, rtol=1e-13, atol=1e-13, a=A,
                                 M=1.0, turning_points=True)
        dx = np.linalg.norm(X - ref.x, axis=1)
        U = np.array([u_from_v(X[i], V[i], A) for i in range(n)])
        E, L, Qs = kerr.invariants("cks", X, U, A, 1.0)
        peri_t, peri_y = ref.events["peri"]
        r_peri_ref = [bl_r(yy[:3]) for yy in peri_y]
        E0, L0, Qi = kerr.invariants("cks", x0, u0, A, 1.0)
        inside = rr < 1.5 * rp
        dphi = float(np.unwrap(np.arctan2(X[:, 1], X[:, 0]))[-1] - math.atan2(X[0, 1], X[0, 0]))
        res.append(dict(rp=rp, Lz=Lz, Q_eq_rp=Q0, Q_release=float(Qi), E_release=float(E0),
                        nsamples=int(n), t_end=float(tk[-1]), max_dx=float(dx.max()),
                        max_dE=float(np.abs(E - E[0]).max()),
                        max_rel_dLz=float(np.abs(L / L[0] - 1).max()) if abs(L[0]) > 1e-12 else float(np.abs(L - L[0]).max()),
                        max_dQ=float(np.abs(Qs - Qs[0]).max()),
                        max_rel_dQ=float(np.abs(Qs / Qs[0] - 1).max()) if Qs[0] > 1e-9 else None,
                        r_peri_ref=r_peri_ref, r_peri_hrna_samples=float(rr.min()),
                        peri_err=(float(abs(r_peri_ref[0] - rp)) if r_peri_ref else None),
                        time_inside_1p5rp_over_tau0=float(np.trapezoid(inside.astype(float), tk) / TAU0),
                        azimuth_swept_over_2pi=dphi / (2 * math.pi)))
        curves.append((tk, dx, np.abs(E - E[0]), np.abs(Qs - Qs[0]), rr))
    return res, curves


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    lo, hi = H.lz_range(10.0, A)
    lo6, hi6 = H.lz_range(6.0, A)
    pairs = [(10.0, lo, hi), (10.0, -3.0, 2.2), (10.0, 0.0, 4.0), (6.0, lo6, hi6)]
    results, curves = [], []
    for rp, la, lb in pairs:
        r, c = one_pair(rp, la, lb)
        results += r
        curves += c
    ok = all(r["max_dx"] < 1e-6 and r["max_dE"] < 1e-9 and r["max_dQ"] < 1e-8 * max(1.0, r["Q_release"])
             and r["peri_err"] is not None and r["peri_err"] < 1e-6 * r["rp"]
             and abs(r["Q_release"] - r["Q_eq_rp"]) < 1e-9 * max(1.0, r["Q_eq_rp"])
             and abs(r["E_release"] - 1) < 1e-12 for r in results)
    out = dict(results=results, pass_all=bool(ok), tau0_M=TAU0, lz_range_rp10=(lo, hi), lz_range_rp6=(lo6, hi6))
    with open(os.path.join(outdir, "t6_kerr_single.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps(out, indent=1))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 5.2))
    axs = [fs.inch_axes(fig, 0.75, 2.85, 3.2, 2.1), fs.inch_axes(fig, 4.6, 2.85, 3.2, 2.1),
           fs.inch_axes(fig, 0.75, 0.45, 3.2, 2.1), fs.inch_axes(fig, 4.6, 0.45, 3.2, 2.1)]
    cols = fs.series_colors(len(results))
    for r, (t, dx, dE, dQ, rr), c in zip(results, curves, cols):
        lab = f"$r_p={r['rp']:g}$, $L_z={r['Lz']:+.2f}$"
        axs[0].semilogy(t, dx + 1e-18, color=c, label=lab)
        axs[1].semilogy(t, dE + 1e-18, color=c)
        axs[2].semilogy(t, dQ + 1e-18, color=c)
        axs[3].plot(t, rr, color=c)
    axs[0].set_ylabel(r"$|\mathbf{x}-\mathbf{x}_{\rm ref}|\ [r_g]$")
    axs[1].set_ylabel(r"$|E-E_0|$")
    axs[2].set_ylabel(r"$|Q-Q_0|$")
    axs[3].set_ylabel(r"BL $r$ [$r_g$]")
    axs[3].set_yscale("log")
    for ax in axs[2:]:
        ax.set_xlabel(r"$t\ [GM/c^3]$")
    axs[0].legend(fontsize=6, loc="lower right", ncol=2)
    fs.save(fig, os.path.join(outdir, "t6_kerr_single"))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.environ["NRPIC_RUN_DIR"])
