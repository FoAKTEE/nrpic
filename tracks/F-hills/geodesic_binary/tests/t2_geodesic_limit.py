"""T2: single-body limit of the HRNA integrator against python/nrpic/geodesic.py.

Pair force off (member masses 1e-300).  Member 1: parabolic orbit (E = 1) with r_p = 10 r_g,
released at r = 200 r_g; member 2: bound orbit (Schwarzschild: turning points 8 and 30 r_g;
Kerr: inclined orbit from BL (r, theta, phi) = (30, 1.0, 0.5)).  Coordinates 'sch' are compared
with geodesic.integrate('bl', a = 0) mapped to Cartesian form, 'cks' with geodesic.integrate('cks').

Run: <venv>/bin/python -I tests/t2_geodesic_limit.py <outdir>
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
sys.path.insert(0, PKG)
sys.path.insert(0, os.path.join(PKG, "..", "..", "..", "python"))
import hrna  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402
from nrpic import geodesic, kerr  # noqa: E402

T_END = 2800.0


def cart_to_bl_state(x, v):
    """Cartesian Schwarzschild (x, xdot) -> spherical (r, th, ph) and covariant u_i."""
    r = np.linalg.norm(x)
    th = math.acos(x[2] / r)
    ph = math.atan2(x[1], x[0])
    f = 1 - 2 / r
    rd = x @ v / r
    # angular velocities
    st, ct, sp, cp = math.sin(th), math.cos(th), math.sin(ph), math.cos(ph)
    e_th = np.array([ct * cp, ct * sp, -st])
    e_ph = np.array([-sp, cp, 0.0])
    thd = (v @ e_th) / r
    phd = (v @ e_ph) / (r * st)
    gam = 1 / math.sqrt(f - rd ** 2 / f - r ** 2 * thd ** 2 - r ** 2 * st ** 2 * phd ** 2)
    u = gam * np.array([rd / f, r ** 2 * thd, r ** 2 * st ** 2 * phd])
    return np.array([r, th, ph]), u


def cks_u_from_v(x, v, a):
    g, gi, dg = np.zeros((4, 4)), np.zeros((4, 4)), np.zeros((3, 4, 4))
    hrna.metric(hrna.COORDS_CKS, x, 1.0, a, g, gi, dg)
    xd = np.array([1.0, *v])
    gam = 1 / math.sqrt(-(xd @ g @ xd))
    return gam * (g[1:, :] @ xd)


def v_from_u(system, x, u, a):
    m = kerr.adm(system, x, a, 1.0)
    U = m.gamma_inv @ u
    W = math.sqrt(1 + u @ U)
    return m.alpha / W * U - m.beta


def bound_sch_state():
    r1, r2 = 8.0, 30.0
    f1, f2 = 1 - 2 / r1, 1 - 2 / r2
    L2 = (f2 - f1) / (f1 / r1 ** 2 - f2 / r2 ** 2)
    E = math.sqrt(f2 * (1 + L2 / r2 ** 2))
    L = math.sqrt(L2)
    return np.array([0.0, r2, 0.0]), np.array([-f2 * L / (E * r2), 0.0, 0.0])


def run_case(coords_name, a):
    cc = hrna.COORDS_SCH if coords_name == "sch" else hrna.COORDS_CKS
    x1, v1 = hrna.cm_initial("hrna", coords_name, a, 10.0, 200.0)
    if coords_name == "sch":
        x2, v2 = bound_sch_state()
    else:
        xbl = np.array([30.0, 1.0, 0.5])
        ubl = np.array([0.0, 2.0, 3.0])
        _, x2, u2 = kerr.convert_state(0.0, xbl, ubl, "bl", "cks", a, 1.0)
        x2 = np.asarray(x2, float)
        v2 = v_from_u("cks", x2, np.asarray(u2, float), a)
    y0 = np.concatenate([x1, v1, x2, v2])
    m = 1e-300
    out = hrna.integrate(hrna.LAW_HRNA, cc, hrna.PAIR_GRAVITY, 1.0, a, m, m, 0.0, 0.0, y0, 1.0,
                         1e-12, 1e-14, 1e300, 1e300, 0.0, T_END, 10 ** 7, 1.0, 10 ** 6,
                         hrna._A, hrna._B, hrna._C, hrna._E3, hrna._E5, hrna._work())
    t, Y = out[4], out[5]
    keep = t <= T_END
    t, Y = t[keep], Y[keep]
    res = {"nsteps": int(out[7])}
    curves = {}
    g, gi, dg = np.zeros((4, 4)), np.zeros((4, 4)), np.zeros((3, 4, 4))
    for k, (xk, vk) in enumerate(((x1, v1), (x2, v2))):
        if coords_name == "sch":
            xs, us = cart_to_bl_state(xk, vk)
            ref = geodesic.integrate("bl", xs, us, t[-1], t_eval=t, rtol=1e-13, atol=1e-13, a=0.0, M=1.0)
            r, th, ph = ref.x[:, 0], ref.x[:, 1], ref.x[:, 2]
            xr = np.stack([r * np.sin(th) * np.cos(ph), r * np.sin(th) * np.sin(ph), r * np.cos(th)], 1)
        else:
            us = cks_u_from_v(xk, vk, a)
            ref = geodesic.integrate("cks", xk, us, t[-1], t_eval=t, rtol=1e-13, atol=1e-13, a=a, M=1.0)
            xr = ref.x
        xm = Y[:, 6 * k:6 * k + 3]
        dx = np.linalg.norm(xm - xr, axis=1)
        EL = np.array([hrna.energy_lz(hrna.LAW_HRNA, cc, 1.0, a, Y[i, 6 * k:6 * k + 3],
                                      Y[i, 6 * k + 3:6 * k + 6], g, gi, dg)[:2] for i in range(len(t))])
        dE = EL[:, 0] / EL[0, 0] - 1
        dL = EL[:, 1] / EL[0, 1] - 1
        rr = np.array([hrna.radius(cc, xm[i], a) for i in range(len(t))])
        res[f"member{k + 1}"] = dict(max_dx=float(dx.max()), max_rel_dE=float(np.abs(dE).max()),
                                     max_rel_dLz=float(np.abs(dL).max()), E=float(EL[0, 0]),
                                     Lz=float(EL[0, 1]), r_min=float(rr.min()), r_max=float(rr.max()))
        curves[k] = (t, dx, dE, dL, rr)
    return res, curves


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    results, allc = {}, {}
    for name, a in (("sch", 0.0), ("cks", 0.9)):
        results[f"{name}_a{a}"], allc[name] = run_case(name, a)
    with open(os.path.join(outdir, "t2_geodesic_limit.json"), "w") as fh:
        json.dump(results, fh, indent=1)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 5.0))
    axes = [[fs.inch_axes(fig, 0.75 + j * 3.75, 0.5 + (1 - i) * 2.25, 3.2, 2.05) for j in range(2)]
            for i in range(2)]
    for j, name in enumerate(("sch", "cks")):
        for k, ls in ((0, "-"), (1, "--")):
            t, dx, dE, dL, rr = allc[name][k]
            lab = ("parabolic, $r_p=10$" if k == 0 else "bound") + (" (Schwarzschild)" if j == 0 else " (Kerr $a=0.9$)")
            axes[0][j].semilogy(t, dx + 1e-18, color=fs.PAL["red"], ls=ls, label=lab)
            axes[1][j].semilogy(t, np.abs(dE) + 1e-18, color=fs.PAL["red"], ls=ls, label=r"$|\Delta E/E|$" if k == 0 else None)
            axes[1][j].semilogy(t, np.abs(dL) + 1e-18, color=fs.PAL["blue"], ls=ls, label=r"$|\Delta L_z/L_z|$" if k == 0 else None)
        axes[0][j].set_ylabel(r"$|\mathbf{x}-\mathbf{x}_{\rm ref}|\ [r_g]$")
        axes[1][j].set_ylabel("relative drift")
        axes[1][j].set_xlabel(r"$t\ [GM/c^3]$")
        axes[0][j].legend(loc="upper left", fontsize=8)
        axes[1][j].legend(loc="upper left", fontsize=8)
    fs.save(fig, os.path.join(outdir, "t2_geodesic_limit"))
    print(json.dumps(results, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
