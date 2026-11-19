#!/usr/bin/env python3
"""Checks PA1 to PA6 of tracks/core/JOURNAL-clump2.md on the Python reference
python/nrpic/boosted_cluster.py (no simulation): the slice function, the momentum, the
curvature against the geometry of the static solution, the divergence, the particle
rule and the second-order correction. Writes check_boost.json and figures into --out.

    check_boost.py --out DIR [--yc 0.819]
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "python"))
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from scipy.integrate import solve_ivp  # noqa: E402
from nrpic import boosted_cluster as bc  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402
from nrpic import sampling  # noqa: E402
from nrpic import st_cluster as stc  # noqa: E402

OUT = {}
FAIL = []


def line(name, ok, text):
    print(("ok      " if ok else "FAILED  ") + name + ": " + text)
    if not ok:
        FAIL.append(name)


def d1(f, x, h, axis):
    """sixth-order central difference of f at points x[..., 3] along one axis"""
    e = np.zeros(3)
    e[axis] = h
    return (45.0 * (f(x + e) - f(x - e)) - 9.0 * (f(x + 2 * e) - f(x - 2 * e))
            + (f(x + 3 * e) - f(x - 3 * e))) / (60.0 * h)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--yc", type=float, default=0.819)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    md = stc.STModel(a.yc)
    B = bc.BoostedST(md)
    Bp = bc.BoostedST(md, slice="plain")
    rs, m = B.rs, B.m
    OUT["model"] = dict(yc=a.yc, rbar_s=rs, M=md.M, alpha_c=md.alpha_c, psi_c=md.psi_c)

    # ---- PA1: the interior solution continued through the vacuum by the ODE
    def rhs(rr, y):
        A = float(md.alpha(rr) * md.psi(rr)) ** 2
        return [y[1] / (rr * rr * A), 2.0 * A * y[0]]
    A_s = float(md.alpha(rs) * md.psi(rs)) ** 2
    y0 = [B.F_nodes[-1], rs * rs * A_s * B.dF_nodes[-1]]
    rr = np.linspace(rs, 4.0 * rs, 61)
    sol = solve_ivp(rhs, (rs, 4.0 * rs), y0, t_eval=rr, method="DOP853", rtol=1e-12,
                    atol=1e-18)
    Fc, _ = B.F_iso(rr)
    res1 = float(np.max(np.abs(sol.y[0] - Fc) / Fc))
    wa0 = float(B.wa_nodes[0])
    OUT["PA1"] = dict(kappa=B.kappa, closed_form_residual=res1, wa_centre=wa0,
                      wa_surface=float(B.wa_nodes[-1]),
                      coordinate_speed_centre_over_V=float(
                          md.alpha_c ** 2 / md.psi_c ** 4 * wa0))
    line("PA1 exterior closed form", res1 < 1e-8, f"max rel. residual {res1:.2e}, "
         f"kappa = {B.kappa:.6f}")
    line("PA1 w_a(0) in 1.05..1.3", 1.05 < wa0 < 1.3, f"w_a(0) = {wa0:.6f}, "
         f"w_a(rbar_s) = {B.wa_nodes[-1]:.6f}")

    # ---- PA2: total momentum per unit velocity
    q1 = B.pmass_iso / md.M
    q1p = Bp.pmass_iso / md.M
    OUT["PA2"] = dict(Q_inf_over_M=q1, Q_inf_over_M_plain=q1p, I4_inf=B.i4_iso,
                      I4_inf_plain=Bp.i4_iso)
    line("PA2 Q(inf) = M", abs(q1 - 1.0) < 1e-7, f"Q(inf)/M - 1 = {q1 - 1.0:+.3e}; "
         f"plain boost {q1p - 1.0:+.4e}")

    # ---- PA3: Abar from the moments against psi^6 (Lbar beta)/(2 alpha)
    V = np.array([0.3, 0.0, 0.0])
    P = B.pmass * V
    rng = np.random.default_rng(5)
    nh = sampling.unit_vectors(rng.random(40), rng.random(40))
    rad = np.concatenate([np.linspace(0.07, 0.93, 20) * rs, np.linspace(1.1, 3.0, 20) * rs])
    x = rad[:, None] * nh

    def beta(xx, k):
        r = np.sqrt(np.sum(xx * xx, axis=-1))
        n = xx / r[..., None]
        wa, wb = B.w_ab_iso(r)
        w = V * wa[..., None] + n * np.sum(V * n, axis=-1)[..., None] * wb[..., None]
        return (md.alpha(r) ** 2 / md.psi(r) ** 4)[..., None] * w

    h = 2.0e-3 * rs
    db = np.empty(x.shape[:-1] + (3, 3))        # db[..., i, j] = d_j beta^i
    for j in range(3):
        db[..., :, j] = d1(lambda xx: beta(xx, 0), x, h, j)
    div = np.trace(db, axis1=-2, axis2=-1)
    lb = db + np.swapaxes(db, -1, -2) - (2.0 / 3.0) * np.eye(3) * div[..., None, None]
    r = np.sqrt(np.sum(x * x, axis=-1))
    ab_geo = (md.psi(r) ** 6 / (2.0 * md.alpha(r)))[..., None, None] * lb
    ab_mom = B.abar(x, (0, 0, 0), P)
    scale = np.max(np.abs(ab_mom))
    e3 = np.max(np.abs(ab_geo - ab_mom), axis=(-1, -2)) / scale
    e3in, e3out = float(e3[:20].max()), float(e3[20:].max())
    k_tr = float(np.max(np.abs(div + 6.0 * np.sum(beta(x, 0) * np.stack(
        [d1(lambda xx: np.log(md.psi(np.sqrt(np.sum(xx * xx, axis=-1)))), x, h, j)
         for j in range(3)], axis=-1), axis=-1))))
    OUT["PA3"] = dict(max_rel_inside=e3in, max_rel_outside=e3out,
                      largest_component=float(scale),
                      max_abs_alpha_K=k_tr)
    line("PA3 Abar = psi^6 Lbar(beta)/(2 alpha)", max(e3in, e3out) < 1e-5,
         f"inside {e3in:.2e}, outside {e3out:.2e} of the largest component {scale:.3e}; "
         f"alpha K of the slice {k_tr:.1e}")
    # the same with the plain boost must fail (K is not zero there): sensitivity
    def beta_p(xx):
        r_ = np.sqrt(np.sum(xx * xx, axis=-1))
        return (md.alpha(r_) ** 2 / md.psi(r_) ** 4)[..., None] * V
    dbp = np.empty_like(db)
    for j in range(3):
        dbp[..., :, j] = d1(beta_p, x, h, j)
    divp = np.trace(dbp, axis1=-2, axis2=-1)
    kp = divp + 6.0 * np.sum(beta_p(x) * np.stack(
        [d1(lambda xx: np.log(md.psi(np.sqrt(np.sum(xx * xx, axis=-1)))), x, h, j)
         for j in range(3)], axis=-1), axis=-1)
    OUT["PA3"]["plain_boost_max_abs_alpha_K"] = float(np.max(np.abs(kp)))
    print(f"        plain boost: max |alpha K| = {np.max(np.abs(kp)):.3e} (not maximal)")

    # ---- PA4: divergence against the source, inside
    xi = x[:20]
    hh = 1.0e-3 * rs
    dv = np.zeros(xi.shape)
    for j in range(3):
        dv += d1(lambda xx: B.abar(xx, (0, 0, 0), P), xi, hh, j)[..., :, j]
    src = 8.0 * math.pi * B.momentum_density(xi, (0, 0, 0), P)
    smax = float(np.max(np.abs(8.0 * math.pi * B.momentum_density(
        np.array([[1e-3, 0, 0]]), (0, 0, 0), P))))
    e4 = float(np.max(np.abs(dv - src)) / smax)
    OUT["PA4"] = dict(max_rel=e4, largest_source=smax)
    line("PA4 divergence", e4 < 1e-6, f"max |d_j Abar_ij - 8 pi Stilde_i| = {e4:.2e} of "
         f"the largest source {smax:.3e}")

    # ---- PA5: particles
    N = 100000
    d, u0, m0, _ = sampling.sample_st(md, N, "stratified", 3)
    u0 = u0 - (m0[:, None] * u0).sum(0) / m0.sum()
    un, mn, Wn = B.boost_particles(d, u0, m0, V)
    tot = (mn[:, None] * un).sum(0)
    tot_now = (m0[:, None] * un).sum(0)            # without the weights
    # sampling error of the total from 20 sub-samples
    sub = np.array([(mn[k::20, None] * un[k::20]).sum(0)[0] * 20 for k in range(20)])
    err = float(sub.std(ddof=1) / math.sqrt(20))
    rp = np.sqrt(np.sum(d * d, axis=1))
    edges = np.linspace(0.0, rs, 21)
    cum = np.array([np.sum((mn * un[:, 0])[rp < e]) for e in edges[1:]])
    qref = B.moments(edges[1:])[0] * P[0]
    # the enclosed momentum of the particles is int Stilde_x d^3x = P [Q-like integral
    # with s_a + s_b/3], which is Q itself
    e5 = float(np.max(np.abs(cum - qref)))
    OUT["PA5"] = dict(N=N, sum_m_u_x=float(tot[0]), continuum=float(P[0]),
                      ratio=float(tot[0] / P[0]), sampling_error=err / P[0],
                      ratio_without_weights=float(tot_now[0] / P[0]),
                      sum_m=float(mn.sum()), M0=md.M0,
                      max_abs_shell_difference=e5,
                      transverse=[float(tot[1]), float(tot[2])])
    line("PA5 sum m u = Q(inf) V", abs(tot[0] / P[0] - 1.0) < 3.0 * err / P[0] + 1e-4,
         f"ratio {tot[0] / P[0]:.6f} +- {err / P[0]:.1e}; without the weights "
         f"{tot_now[0] / P[0]:.5f}; largest shell difference {e5 / P[0]:.2e} P")

    # ---- PA6: second order
    co = B.correction()
    dm = 2.0 * co["monopole"]
    OUT["PA6"] = dict(added_mass_over_half_M_V2=dm / (0.5 * md.M),
                      y0_centre=co["y0_centre"], iterations=list(co["iterations"]))
    line("PA6 added mass in 0.9..1.3 of M V^2/2", 0.9 < dm / (0.5 * md.M) < 1.3,
         f"2 monopole = {dm / (0.5 * md.M):.5f} M V^2/2; y_0(0) = {co['y0_centre']:.5f}")
    # exact direction average of m~ W~ for the monoenergetic model against second order
    nu, wn = np.polynomial.legendre.leggauss(64)
    rr_ = np.linspace(0.02, 0.98, 25) * rs
    p0, a0 = md.psi(rr_), md.alpha(rr_)
    qq = md.q(rr_)
    W = np.sqrt(1.0 + qq * qq)
    wa, wb = B.w_ab_iso(rr_)
    worst = {}
    for vv in (0.1, 0.31):
        rel = 0.0
        for mu in (0.0, 0.6, 1.0):
            wmag = vv * np.sqrt(wa * wa + mu * mu * (2 * wa * wb + wb * wb))
            wbar = a0 * wmag / p0 ** 2
            # q.w = q |w| nu ; u~^2/psi^4 = q^2 + 2 W q wbar nu + W^2 wbar^2
            ex = 0.5 * np.sum(wn[None, :] * (1.0 + qq[:, None] * wbar[:, None] * nu / W[:, None])
                              * np.sqrt(1.0 + qq[:, None] ** 2
                                        + 2.0 * W[:, None] * qq[:, None] * wbar[:, None] * nu
                                        + (W * wbar)[:, None] ** 2), axis=1)
            second = W + wbar ** 2 * (0.5 * W + qq * qq / (6.0 * W))
            rel = max(rel, float(np.max(np.abs(ex - second) / (second - W))))
        worst[str(vv)] = rel
    OUT["PA6"]["fourth_order_over_second"] = worst
    line("PA6 expansion of m W", all(worst[str(v)] < 2.0 * v * v for v in (0.1, 0.31)),
         "exact - second order over the second-order term: "
         + ", ".join(f"V = {k}: {v:.3e}" for k, v in worst.items()))
    # residual of the radial equations on a uniform table (as written)
    tabf = os.path.join(a.out, "corr_check.tab")
    rg, cols, tails = B.write_correction_table(tabf, [1.0, 0.0, 0.0], dr=rs / 2000.0,
                                               rlast=6.0 * rs)
    res6 = {}
    for q_, l in enumerate((0, 2)):
        y = cols[q_]
        hgrid = 8
        H = hgrid * (rg[1] - rg[0])
        i = np.arange(3 * hgrid, len(rg) - 3 * hgrid)
        d2 = (2 * (y[i + 3 * hgrid] + y[i - 3 * hgrid]) - 27 * (y[i + 2 * hgrid]
              + y[i - 2 * hgrid]) + 270 * (y[i + hgrid] + y[i - hgrid]) - 490 * y[i]) \
            / (180.0 * H * H)
        dd = (45 * (y[i + hgrid] - y[i - hgrid]) - 9 * (y[i + 2 * hgrid] - y[i - 2 * hgrid])
              + (y[i + 3 * hgrid] - y[i - 3 * hgrid])) / (60.0 * H)
        ri = rg[i]
        lap = d2 + 2.0 * dd / ri - l * (l + 1) * y[i] / ri ** 2
        sig = np.interp(ri, co["r"], co["sigma"])
        Sl = np.interp(ri, co["r"], co["S0" if l == 0 else "S2"])
        resid = lap - sig * y[i] + Sl
        ok = np.abs(ri - rs) > 0.05 * rs
        res6[l] = float(np.max(np.abs(resid[ok])) / np.max(np.abs(co["S0"])))
    OUT["PA6"]["table_residual"] = {str(k): v for k, v in res6.items()}
    OUT["PA6"]["tails"] = [float(t) for t in tails]
    line("PA6 radial equations on the table", max(res6.values()) < 1e-4,
         f"l = 0: {res6[0]:.2e}, l = 2: {res6[2]:.2e} of the largest source; tails "
         + ", ".join(f"{t:.3f}" for t in tails))

    # ---- figures
    fs.use_style()
    rn = B.r_nodes
    fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.6))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.09, top=0.97, wspace=0.26,
                        hspace=0.24)
    rx = np.linspace(1e-3, 2.5, 600) * rs
    wa_, wb_ = B.w_ab_iso(rx)
    ax[0, 0].plot(rx, wa_, color=fs.PAL["red"], label=r"$w_a = F/r$")
    ax[0, 0].plot(rx, wb_, color=fs.PAL["red"], ls="--", label=r"$w_b = F' - F/r$")
    ax[0, 0].plot(rx, md.alpha(rx) ** 2 / md.psi(rx) ** 4 * wa_, color=fs.PAL["blue"],
                  label=r"$\alpha_0^2\psi_0^{-4} w_a$ (coordinate speed$/V$)")
    ax[0, 0].axhline(1.0, **fs.GUIDE)
    ax[0, 0].axvline(rs, **fs.MASK_LINE)
    ax[0, 0].set_xlabel(r"$r/M$")
    ax[0, 0].set_ylabel("slice function")
    ax[0, 0].legend(loc="center right")
    q_, i4_ = B.moments(rx)
    qp_, i4p_ = Bp.moments(rx)
    ax[0, 1].plot(rx, q_, color=fs.PAL["red"], label=r"$Q$")
    ax[0, 1].plot(rx, i4_ / B.moments(10 * rs)[1], color=fs.PAL["red"], ls="--",
                  label=r"$I_4/I_4(\infty)$")
    ax[0, 1].plot(rx, qp_ * Bp.pmass_iso / md.M, color=fs.PAL["yellow"], ls=":",
                  label=r"$Q$, plain boost, per $MV$")
    ax[0, 1].axvline(rs, **fs.MASK_LINE)
    ax[0, 1].set_xlabel(r"$r/M$")
    ax[0, 1].set_ylabel("moments of the momentum density")
    ax[0, 1].legend(loc="lower right")
    ax[1, 0].plot(edges[1:], cum / P[0], "o", ms=3, color=fs.PAL["red"],
                  label=r"particles, $10^5$")
    ax[1, 0].plot(rx[rx < rs], B.moments(rx[rx < rs])[0], color=fs.PAL["blue"],
                  label=r"$Q(r)$")
    ax[1, 0].set_xlabel(r"$r/M$")
    ax[1, 0].set_ylabel(r"enclosed $\sum m u_x / P$")
    ax[1, 0].legend(loc="upper left")
    ax[1, 1].plot(co["r"], co["y0"], color=fs.PAL["red"], label=r"$y_0$")
    ax[1, 1].plot(co["r"], co["y2"], color=fs.PAL["red"], ls="--", label=r"$y_2$")
    ax[1, 1].plot(co["r"], co["monopole"] / co["r"], **fs.GUIDE)
    ax[1, 1].axvline(rs, **fs.MASK_LINE)
    ax[1, 1].set_xlim(0.0, 4.0 * rs)
    ax[1, 1].set_ylim(-0.01, 1.15 * co["y0_centre"])
    ax[1, 1].set_xlabel(r"$r/M$")
    ax[1, 1].set_ylabel(r"$\delta\psi/V^2$")
    ax[1, 1].legend(loc="upper right")
    fs.save(fig, os.path.join(a.out, "fig_boost_reference"))

    OUT["failed"] = FAIL
    with open(os.path.join(a.out, "check_boost.json"), "w") as f:
        json.dump(OUT, f, indent=1)
    print("ALL CHECKS HOLD" if not FAIL else "FAILED: " + ", ".join(FAIL))
    return 0


if __name__ == "__main__":
    sys.exit(main())
