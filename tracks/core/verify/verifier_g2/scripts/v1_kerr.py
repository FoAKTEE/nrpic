#!/usr/bin/env python3
"""V1: Kerr geodesic invariants and dt order, recomputed from the raw trajectories.

Own code only: Kerr-Schild metrics written here, own reader of <base>.traj.bin
(float64 records of 8: t, tag, x^i, u_i; docs/FORMATS.md line 121), own reference
integration of the geodesic (Hamilton's equations in spherical Kerr-Schild coordinates,
complex-step derivatives, scipy DOP853 at rtol 1e-13).

Self-test first (analytic case): the spherical Kerr-Schild inverse metric written below
equals the inverse of J^T g_CKS J built from the Cartesian Kerr-Schild form.

usage: v1_kerr.py RUNDIR OUTDIR
"""
import json
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp

M = 1.0
A = 0.9


def ginv_sph(r, th, a=A):
    """inverse metric of spherical Kerr-Schild coordinates (t, r, theta, phi)."""
    s2 = np.sin(th) ** 2
    sig = r * r + a * a * np.cos(th) ** 2
    dlt = r * r - 2 * M * r + a * a
    g = np.zeros((4, 4), dtype=np.result_type(r, th, complex) if np.iscomplexobj(r) or np.iscomplexobj(th) else float)
    g[0, 0] = -(1 + 2 * M * r / sig)
    g[0, 1] = g[1, 0] = 2 * M * r / sig
    g[1, 1] = dlt / sig
    g[1, 3] = g[3, 1] = a / sig
    g[2, 2] = 1 / sig
    g[3, 3] = 1 / (sig * s2)
    return g


def cks_r(x, y, z, a=A):
    R2 = x * x + y * y + z * z
    b = R2 - a * a
    r2 = 0.5 * (b + np.sqrt(b * b + 4 * a * a * z * z))
    return np.sqrt(r2)


def cks_l_f(x, y, z, a=A):
    r = cks_r(x, y, z, a)
    f = 2 * M * r ** 3 / (r ** 4 + a * a * z * z)
    l = np.array([1.0, (r * x + a * y) / (r * r + a * a), (r * y - a * x) / (r * r + a * a), z / r])
    return r, f, l


def g_cks(x, y, z, a=A):
    r, f, l = cks_l_f(x, y, z, a)
    eta = np.diag([-1.0, 1, 1, 1])
    return eta + f * np.outer(l, l)


def ginv_cks(x, y, z, a=A):
    r, f, l = cks_l_f(x, y, z, a)
    eta = np.diag([-1.0, 1, 1, 1])
    lu = eta @ l
    return eta - f * np.outer(lu, lu)


def sph_to_cks(r, th, ph, a=A):
    return (np.sin(th) * (r * np.cos(ph) - a * np.sin(ph)),
            np.sin(th) * (r * np.sin(ph) + a * np.cos(ph)), r * np.cos(th))


def jac_sph_to_cks(r, th, ph, a=A):
    """J[mu, alpha] = d x_cks^mu / d q_sph^alpha (t unchanged)."""
    J = np.zeros((4, 4))
    J[0, 0] = 1
    st, ct, sp, cp = np.sin(th), np.cos(th), np.sin(ph), np.cos(ph)
    J[1, 1], J[1, 2], J[1, 3] = st * cp, ct * (r * cp - a * sp), st * (-r * sp - a * cp)
    J[2, 1], J[2, 2], J[2, 3] = st * sp, ct * (r * sp + a * cp), st * (r * cp - a * sp)
    J[3, 1], J[3, 2], J[3, 3] = ct, -r * st, 0.0
    return J


def selftest():
    worst = 0.0
    rng = np.random.default_rng(7)
    for _ in range(20):
        r, th, ph = rng.uniform(1.6, 30), rng.uniform(0.2, 2.9), rng.uniform(0, 6.2)
        x, y, z = sph_to_cks(r, th, ph)
        assert abs(cks_r(x, y, z) - r) < 1e-12 * r
        J = jac_sph_to_cks(r, th, ph)
        G = J.T @ g_cks(x, y, z) @ J
        worst = max(worst, np.max(np.abs(np.linalg.inv(G) - ginv_sph(r, th))))
        worst = max(worst, np.max(np.abs(g_cks(x, y, z) @ ginv_cks(x, y, z) - np.eye(4))))
    return worst


def ut_from_shell(gi, ui):
    """u_t from g^{mu nu} u_mu u_nu = -1, future directed (u^t > 0)."""
    A2 = gi[0, 0]
    B = 2 * np.dot(gi[0, 1:], ui)
    C = ui @ gi[1:, 1:] @ ui + 1.0
    disc = np.sqrt(B * B - 4 * A2 * C)
    for ut in ((-B - disc) / (2 * A2), (-B + disc) / (2 * A2)):
        if gi[0, 0] * ut + np.dot(gi[0, 1:], ui) > 0:
            return ut
    raise RuntimeError("no future-directed root")


def invariants_sph(rec):
    r, th = rec[2], rec[3]
    ui = rec[5:8]
    ut = ut_from_shell(ginv_sph(r, th), ui)
    E, Lz, uth = -ut, ui[2], ui[1]
    Q = uth ** 2 + np.cos(th) ** 2 * (A * A * (1 - E * E) + Lz ** 2 / np.sin(th) ** 2)
    return E, Lz, Q, r, th


def invariants_cks(rec):
    x, y, z = rec[2:5]
    ui = rec[5:8]
    ut = ut_from_shell(ginv_cks(x, y, z), ui)
    r = cks_r(x, y, z)
    th = np.arccos(z / r)
    E = -ut
    Lz = x * ui[1] - y * ui[0]
    uth = (x * ui[0] + y * ui[1]) * np.cos(th) / np.sin(th) - r * np.sin(th) * ui[2]
    Q = uth ** 2 + np.cos(th) ** 2 * (A * A * (1 - E * E) + Lz ** 2 / np.sin(th) ** 2)
    return E, Lz, Q, r, th


def read_traj(path):
    d = np.fromfile(path, dtype="<f8")
    return d.reshape(-1, 8)


def rhs(t, y):
    """Hamilton's equations in coordinate time; y = (r, th, ph, u_r, u_th, u_ph, u_t)."""
    r, th, ph, ur, uth, uph, ut = y
    p = np.array([ut, ur, uth, uph])
    gi = ginv_sph(r, th)
    up = gi @ p
    h = 1e-30
    dgr = ginv_sph(r + 1j * h, th).imag / h
    dgt = ginv_sph(r, th + 1j * h).imag / h
    dHdr = 0.5 * p @ dgr @ p
    dHdt = 0.5 * p @ dgt @ p
    return [up[1] / up[0], up[2] / up[0], up[3] / up[0], -dHdr / up[0], -dHdt / up[0], 0.0, 0.0]


def reference(rec0, t_end):
    r, th, ph = rec0[2:5]
    ui = rec0[5:8]
    ut = ut_from_shell(ginv_sph(r, th), ui)
    y0 = [r, th, ph, ui[0], ui[1], ui[2], ut]
    sol = solve_ivp(rhs, (0.0, t_end), y0, method="DOP853", rtol=1e-13, atol=1e-13, dense_output=True)
    return sol


def pericentre(E, Lz, Q):
    """largest real root below 20 M of the Boyer-Lindquist radial potential R(r)."""
    # R(r) = [E (r^2 + a^2) - a Lz]^2 - Delta [r^2 + (Lz - a E)^2 + Q]
    P = np.polynomial.Polynomial
    rr = P([0, 1])
    Rp = (E * (rr ** 2 + A * A) - A * Lz) ** 2 - (rr ** 2 - 2 * M * rr + A * A) * (rr ** 2 + (Lz - A * E) ** 2 + Q)
    roots = Rp.roots()
    real = np.sort(roots[np.abs(roots.imag) < 1e-9].real)
    return max(x for x in real if x < 20.0), real


def main():
    rundir, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    res = {"selftest_metric_max_abs_diff": float(selftest())}
    cases = ["mid_ks_dt0.01", "bsym_ks_dt0.01", "mid_lat_dt0.01", "bchol_lat_dt0.01",
             "mid_ks_dt0.005", "mid_ks_dt0.02", "bsym_ks_dt0.005", "bsym_ks_dt0.02",
             "bchol_ks_dt0.005", "bchol_ks_dt0.01", "bchol_ks_dt0.02"]
    series = {}
    for c in cases:
        d = read_traj(os.path.join(rundir, c, "geo.traj.bin"))
        f = invariants_cks if "_lat_" in c else invariants_sph
        inv = np.array([f(rec) for rec in d])
        E, Lz, Q, r, th = inv.T
        rel = lambda q: np.abs(q - q[0]) / np.abs(q[0])
        i_peri = int(np.argmin(r))
        res[c] = {"n_records": int(len(d)), "t_last": float(d[-1, 0]),
                  "E0": float(E[0]), "Lz0": float(Lz[0]), "Q0": float(Q[0]),
                  "max_dE": float(rel(E).max()), "max_dLz": float(rel(Lz).max()),
                  "max_dQ": float(rel(Q).max()), "r_peri": float(r[i_peri]),
                  "t_peri": float(d[i_peri, 0])}
        series[c] = (d[:, 0], rel(E), rel(Lz), rel(Q))
    # reference integration from the first record of the ks runs (same initial state)
    d0 = read_traj(os.path.join(rundir, "mid_ks_dt0.01", "geo.traj.bin"))
    sol = reference(d0[0], 230.0)
    yref = sol.sol(230.0)
    E0, Lz0, Q0 = res["mid_ks_dt0.01"]["E0"], res["mid_ks_dt0.01"]["Lz0"], res["mid_ks_dt0.01"]["Q0"]
    rp, roots = pericentre(E0, Lz0, Q0)
    tt = np.linspace(90, 110, 200001)
    rr = sol.sol(tt)[0]
    res["reference"] = {"r_end": float(yref[0]), "th_end": float(yref[1]), "ph_end": float(yref[2]),
                        "r_peri_exact_root": float(rp), "radial_roots": [float(x) for x in roots],
                        "r_peri_ref_integration": float(rr.min()), "t_peri_ref": float(tt[np.argmin(rr)]),
                        "nfev": int(sol.nfev)}
    orders = {}
    for p in ("mid", "bsym", "bchol"):
        errs = []
        for dt in ("0.02", "0.01", "0.005"):
            d = read_traj(os.path.join(rundir, f"{p}_ks_dt{dt}", "geo.traj.bin"))
            last = d[-1]
            dph = (last[4] - yref[2] + np.pi) % (2 * np.pi) - np.pi
            errs.append(max(abs(last[2] - yref[0]), abs(last[3] - yref[1]), abs(dph)))
        orders[p] = {"final_pos_err": errs,
                     "order_pairs": [float(np.log2(errs[0] / errs[1])), float(np.log2(errs[1] / errs[2]))]}
    res["orders"] = orders
    with open(os.path.join(out, "v1_kerr.json"), "w") as fh:
        json.dump(res, fh, indent=1)

    import matplotlib
    matplotlib.use("Agg")
    sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
    import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.8))
    lab = {"mid_ks_dt0.01": "midpoint, analytic", "bsym_ks_dt0.01": "Boris sym., analytic",
           "mid_lat_dt0.01": "midpoint, Hermite lattice", "bchol_lat_dt0.01": "Boris Chol., lattice"}
    for k, (name, idx) in enumerate((("E", 1), ("L_z", 2), ("Q", 3))):
        ax = axs[k]
        for c in lab:
            t, *q = series[c]
            y = np.maximum(q[idx - 1], 1e-17)
            ax.semilogy(t[::20], y[::20], lw=0.9, label=lab[c], color=fs.SERIES[list(lab).index(c)])
        ax.set_xlabel(r"$t/M$")
        ax.set_ylabel(rf"$|\Delta {name}|/|{{{name}}}(0)|$")
    axs[0].legend(fontsize=7, loc="lower right")
    fig.suptitle("V1: Kerr a=0.9 passage, relative invariant errors (own metric), run core-20261115-065452-3629622", fontsize=8)
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "fig_v1_kerr"))
    print(json.dumps({k: res[k] for k in ("selftest_metric_max_abs_diff", "reference", "orders")}, indent=1))
    for c in lab:
        print(c, {k: res[c][k] for k in ("E0", "Lz0", "Q0", "max_dE", "max_dLz", "max_dQ", "r_peri", "t_peri")})


if __name__ == "__main__":
    main()
