"""Sign of the gravitomagnetic interaction between mass currents (brief line 604, [BACKGROUND]).

Claim checked: "the gravitomagnetic interaction between co-moving mass currents is repulsive,
opposite in sign to electromagnetism".

Set-up (linearized general relativity, harmonic gauge, G = c = 1): a point mass M moves with
velocity V along x; its trace-reversed perturbation is the boost of the static one,
    hbar_{mu nu} = 4 M u_mu u_nu / R,   u = gamma (1, V, 0, 0),
    R^2 = gamma^2 (x - V t)^2 + y^2 + z^2   (distance in the rest frame of the source),
so h_{mu nu} = 4 M u_mu u_nu / R + 2 M eta_{mu nu} / R. A test particle at (t, x, y, z) =
(0, 0, b, 0) moves with velocity w along x. Its transverse coordinate acceleration follows from
the geodesic equation, d^2 y/dt^2 = -Gamma^y_{ab} v^a v^b + v^y Gamma^0_{ab} v^a v^b with
v = (1, w, 0, 0).

1. Symbolic (sympy): the linear-order acceleration and its split by metric component:
   h_00 (gravitoelectric potential), h_0x (gravitomagnetic potential), h_xx (spatial part).
2. Numerical, independent of step 1: Christoffel symbols of the full metric eta + h by central
   differences of the metric function, full inverse metric, at M/b = 1e-6, on a grid of (V, w).
3. Electromagnetic analogue: like charges, F_y = (q Q / b^2) gamma (1 - V w) (electric part
   gamma, magnetic part -gamma V w).

Writes gem_sign.json and fig_gem_sign.{pdf,png} into $NRPIC_RUN_DIR (or the first argument).
Exit status 1 if a preregistered check fails (JOURNAL.md entry 2).
"""
import json
import os
import sys

import numpy as np
import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figstyle as fs  # noqa: E402  (vendored copy of harness/style/figstyle.py)
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ETA = np.diag([-1.0, 1.0, 1.0, 1.0])


def symbolic():
    t, x, y, z = sp.symbols("t x y z", real=True)
    M, V, w = sp.symbols("M V w", real=True)
    b = sp.symbols("b", positive=True)
    g = 1 / sp.sqrt(1 - V**2)
    X = [t, x, y, z]
    eta = sp.diag(-1, 1, 1, 1)
    u_up = sp.Matrix([g, g * V, 0, 0])
    u_dn = eta * u_up
    R = sp.sqrt(g**2 * (x - V * t)**2 + y**2 + z**2)
    h = sp.zeros(4, 4)
    for a in range(4):
        for c in range(4):
            h[a, c] = 4 * M * u_dn[a] * u_dn[c] / R + 2 * M * eta[a, c] / R
    v = [1, w, 0, 0]
    at = {t: 0, x: 0, y: b, z: 0}

    def gamma_y(hh):
        # linear order: Gamma^y_{ab} = (1/2) eta^{yy} (d_a h_{yb} + d_b h_{ya} - d_y h_{ab})
        s = 0
        for a in range(4):
            for c in range(4):
                s += sp.Rational(1, 2) * (sp.diff(hh[2, c], X[a]) + sp.diff(hh[2, a], X[c])
                                          - sp.diff(hh[a, c], y)) * v[a] * v[c]
        return sp.simplify(-s.subs(at))

    total = gamma_y(h)
    parts = {}
    for name, idx in (("h00", [(0, 0)]), ("h0x", [(0, 1), (1, 0)]), ("hxx", [(1, 1)]),
                      ("hyy_hzz", [(2, 2), (3, 3)])):
        hh = sp.zeros(4, 4)
        for (a, c) in idx:
            hh[a, c] = h[a, c]
        parts[name] = gamma_y(hh)
    closed = -(M / b**2) * (2 * g**2 * (1 - V * w)**2 - (1 - w**2))
    ok_closed = sp.simplify(total - closed) == 0
    ok_sum = sp.simplify(total - sum(parts.values())) == 0
    comoving = sp.simplify(total.subs(w, V))
    ok_comoving = sp.simplify(comoving + (M / b**2) * (1 - V**2)) == 0
    f = {k: sp.lambdify((M, V, w, b), e, "numpy") for k, e in parts.items()}
    f["total"] = sp.lambdify((M, V, w, b), total, "numpy")
    return {"total": str(total), "parts": {k: str(e) for k, e in parts.items()},
            "comoving": str(comoving), "ok_closed_form": bool(ok_closed),
            "ok_parts_sum": bool(ok_sum), "ok_comoving_minus_1_over_gamma2": bool(ok_comoving)}, f


def metric(M, V, X):
    g = 1 / np.sqrt(1 - V**2)
    t, x, y, z = X
    R = np.sqrt(g**2 * (x - V * t)**2 + y**2 + z**2)
    u_dn = ETA @ np.array([g, g * V, 0.0, 0.0])
    return ETA + 4 * M * np.outer(u_dn, u_dn) / R + 2 * M * ETA / R


def accel_numeric(M, V, w, b, d=1e-3):
    """Full-metric Christoffel symbols by central differences; returns d^2y/dt^2."""
    X0 = np.array([0.0, 0.0, b, 0.0])
    dg = np.zeros((4, 4, 4))  # dg[k] = d_k g_{ab}
    for k in range(4):
        e = np.zeros(4)
        e[k] = d * b
        dg[k] = (metric(M, V, X0 + e) - metric(M, V, X0 - e)) / (2 * d * b)
    ginv = np.linalg.inv(metric(M, V, X0))
    gam = np.zeros((4, 4, 4))
    for i in range(4):
        for a in range(4):
            for c in range(4):
                gam[i, a, c] = 0.5 * sum(ginv[i, m] * (dg[a][m, c] + dg[c][m, a] - dg[m][a, c])
                                         for m in range(4))
    v = np.array([1.0, w, 0.0, 0.0])
    q = lambda i: v @ gam[i] @ v  # noqa: E731
    return -q(2) + v[2] * q(0)


def main():
    out = os.environ.get("NRPIC_RUN_DIR") or (sys.argv[1] if len(sys.argv) > 1 else ".")
    os.makedirs(out, exist_ok=True)
    res, f = symbolic()
    M, b = 1e-6, 1.0
    grid = np.linspace(-0.9, 0.9, 13)
    worst = 0.0
    for V in grid:
        for w in grid:
            an = f["total"](M, V, w, b)
            nu = accel_numeric(M, V, w, b)
            worst = max(worst, abs(nu - an) / abs(an))
    res["numeric_vs_symbolic_max_rel"] = worst
    # sign of the gravitomagnetic (h_0x) part for co-moving currents, V = w > 0
    Vs = np.linspace(0.05, 0.95, 19)
    gm_comov = np.array([f["h0x"](1.0, V, V, 1.0) for V in Vs])
    res["gm_part_comoving_all_positive_repulsive"] = bool(np.all(gm_comov > 0))
    em_mag_comov = -Vs**2 / np.sqrt(1 - Vs**2)  # magnetic part of like charges, units qQ/b^2
    res["em_magnetic_comoving_all_negative_attractive"] = bool(np.all(em_mag_comov < 0))
    checks = {
        "closed form": res["ok_closed_form"],
        "parts sum to total": res["ok_parts_sum"],
        "co-moving total = -(1 - V^2) M/b^2": res["ok_comoving_minus_1_over_gamma2"],
        "numeric agrees to 1e-5": bool(worst < 1e-5),
        "gravitomagnetic part repulsive for co-moving currents": res["gm_part_comoving_all_positive_repulsive"],
        "EM magnetic part attractive for co-moving like charges": res["em_magnetic_comoving_all_negative_attractive"],
    }
    res["checks"] = checks
    with open(os.path.join(out, "gem_sign.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps({"checks": checks, "max_rel": worst, "parts": res["parts"]}, indent=1))

    fs.use_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.3))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.16, top=0.83, wspace=0.32)
    V = 0.6
    ws = np.linspace(-0.95, 0.95, 191)
    names = {"h00": r"$h_{00}$ (gravitoelectric)", "h0x": r"$h_{0x}$ (gravitomagnetic)",
             "hxx": r"$h_{xx}$ (spatial)"}
    cols = {"h00": fs.PAL["blue"], "h0x": fs.PAL["red"], "hxx": fs.PAL["yellow"]}
    for k in ("h00", "h0x", "hxx"):
        # a part that does not depend on w comes back from lambdify as a scalar
        ax1.plot(ws, np.broadcast_to(f[k](1.0, V, ws, 1.0), ws.shape), color=cols[k],
                 label=names[k])
    ax1.plot(ws, f["total"](1.0, V, ws, 1.0), **fs.REF_LINE, label="total")
    wn = grid
    ax1.plot(wn, [accel_numeric(1e-6, V, w_, 1.0) / 1e-6 for w_ in wn], "o", ms=4,
             mfc="none", mec="k", label="finite differences")
    ax1.axhline(0, **fs.MASK_LINE)
    ax1.axvline(V, **fs.MASK_LINE)
    ax1.text(V - 0.03, 3.2, "co-moving", fontsize=9, ha="right")
    ax1.set_xlabel(r"test-particle velocity $w$ (source $V=0.6$)")
    ax1.set_ylabel(r"$b^2\,\ddot y / M$  ($>0$: repulsive)")
    ax2.plot(Vs, gm_comov, color=fs.PAL["red"], label=r"gravity, $h_{0x}$ part")
    ax2.plot(Vs, em_mag_comov, color=fs.PAL["blue"], label="EM, magnetic part (like charges)")
    ax2.plot(Vs, -(1 - Vs**2), **fs.GUIDE, label=r"$-1/\gamma^2$")
    # the total lies on -1/gamma^2: drawn as markers so that both stay visible
    ax2.plot(Vs, [f["total"](1.0, v_, v_, 1.0) for v_ in Vs], "o", ms=4, mfc="none",
             mec="k", label="gravity, total")
    ax2.axhline(0, **fs.MASK_LINE)
    ax2.set_xlabel(r"common velocity $V=w$")
    ax2.set_ylabel(r"$b^2\,\ddot y/M$ or $b^2 F_y/qQ$")
    ax2.set_ylim(-4, 8)
    for ax, lab in ((ax1, "(a)"), (ax2, "(b)")):
        ax.text(0.02, 0.95, lab, transform=ax.transAxes, va="top")
    h1, l1 = ax1.get_legend_handles_labels()
    fig.legend(h1, l1, loc="upper left", ncol=3, fontsize=8, bbox_to_anchor=(0.06, 1.0))
    ax2.legend(loc="upper left", fontsize=7, bbox_to_anchor=(0.08, 1.0))
    fs.save(fig, os.path.join(out, "fig_gem_sign"))
    plt.close(fig)
    if not all(checks.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
