"""T8: the chart 'bks' of hrna_bks.py (Boyer-Lindquist time, Kerr-Schild space) and the
slicing artefact of 'cks' that it removes.

(a) metric: g g^-1 = 1, spatial derivatives against centred differences, and g('bks', a = 0)
    equal to hrna's Schwarzschild form 'sch' at 200 random points (r = 3..200);
(b) a = 0: whole encounters in 'bks' equal those in 'sch' step by step (same step count,
    positions to rounding) for three inclined set-ups;
(c) single body in Kerr a = 0.9 (pair force off) on the orbits of T6, integrated in 'bks' and
    compared with python/nrpic's geodesic in Cartesian Kerr-Schild at the same events
    (t_KS = t_BL + F(r)): positions, E, L_z, Q;
(d) binary energy drift on the way in (r = 100 -> pericentre) for coplanar binaries, iota = 0,
    pi/2, pi, in 'cks', 'bks' (a = 0 and 0.9) and 'sch' (a = 0): ln|E_b(t)/E_b(0)| against the
    leading-order prediction for 'cks' (JOURNAL entry 2),
        d ln|E_b|/dt = -2 H omega_b (n x v_cm) . L_hat_b,   H = M r^3/(r^4 + a^2 z^2),
    integrated along the run's own CM path with omega_b from the run's own E_b(t).

Run: <venv>/bin/python -I tests/t8_bks_chart.py <outdir>
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
import hrna_bks as B  # noqa: E402
import hrna_incl as H  # noqa: E402
import hrna  # noqa: E402
from nrpic import geodesic, kerr  # noqa: E402

P = dict(mb=6.25e-6, q12=2 / 3, a0=0.125, r0=100.0)


def part_a():
    rng = np.random.default_rng(7)
    out = dict(ginv=0.0, dg_fd=0.0, sch_g=0.0, sch_gi=0.0, sch_dg=0.0)
    for a in (0.0, 0.5, 0.9):
        for _ in range(200):
            r = 3.0 + 197.0 * rng.random()
            n = rng.standard_normal(3)
            x = r * n / np.linalg.norm(n)
            g, gi, dg = np.zeros((4, 4)), np.zeros((4, 4)), np.zeros((3, 4, 4))
            B.metric_bks(x, 1.0, a, g, gi, dg)
            out["ginv"] = max(out["ginv"], float(np.abs(g @ gi - np.eye(4)).max()))
            h = 1e-5 * max(1.0, r / 10)
            for k in range(3):
                xp, xm = x.copy(), x.copy()
                xp[k] += h
                xm[k] -= h
                gp, gm = np.zeros((4, 4)), np.zeros((4, 4))
                B.metric_bks(xp, 1.0, a, gp, np.zeros((4, 4)), np.zeros((3, 4, 4)))
                B.metric_bks(xm, 1.0, a, gm, np.zeros((4, 4)), np.zeros((3, 4, 4)))
                out["dg_fd"] = max(out["dg_fd"], float(np.abs((gp - gm) / (2 * h) - dg[k]).max()))
            if a == 0.0:
                gs, gis, dgs = np.zeros((4, 4)), np.zeros((4, 4)), np.zeros((3, 4, 4))
                hrna.metric_sch(x, 1.0, gs, gis, dgs)
                out["sch_g"] = max(out["sch_g"], float(np.abs(g - gs).max()))
                out["sch_gi"] = max(out["sch_gi"], float(np.abs(gi - gis).max()))
                out["sch_dg"] = max(out["sch_dg"], float(np.abs(dg - dgs).max()))
    return out


def run_rec(coords, spin, rp, Lz, iota, Omega, phase):
    y0, info = H.initial_state_incl("hrna", coords, spin, P["mb"], P["q12"], P["a0"], rp, Lz, iota,
                                    Omega, phase, P["r0"])
    t_max = 6.0 * (math.sqrt(2.0) / 3.0) * 2 * P["r0"] ** 1.5 + 200.0
    out = H.integrate_y0(y0, "hrna", coords, spin, info["m1"], info["m2"], P["a0"], P["r0"], 1e300,
                         t_max, record=400000)
    return np.array(out[4]), np.array(out[5]), int(out[7]), info


def part_b():
    res = []
    for rp, io, i, Om, ph in ((10.0, 0.6, 0.8, 1.1, 0.4), (7.0, 1.3, 2.2, 0.3, 2.0), (6.0, 2.4, 1.6, 2.7, 5.0)):
        Lz = H.lz_range(rp, 0.0)[1] * math.cos(io)
        tS, YS, nS, _ = run_rec("sch", 0.0, rp, Lz, i, Om, ph)
        tB, YB, nB, _ = run_rec("bks", 0.0, rp, Lz, i, Om, ph)
        n = min(len(tS), len(tB))
        # rounding moves the accepted step times (T5): compare at matched times, x_B + v_B dt
        dt = (tS[:n] - tB[:n])[:, None]
        XB = np.concatenate([YB[:n, 0:3] + YB[:n, 3:6] * dt, YB[:n, 6:9] + YB[:n, 9:12] * dt], axis=1)
        dx = np.abs(YS[:n, [0, 1, 2, 6, 7, 8]] - XB).max()
        res.append(dict(rp=rp, iota_orb=io, nsteps=(nS, nB), max_dpos=float(dx),
                        max_dpos_step_index=float(np.abs(YS[:n, [0, 1, 2, 6, 7, 8]] - YB[:n, [0, 1, 2, 6, 7, 8]]).max()),
                        max_dt=float(np.abs(tS[:n] - tB[:n]).max())))
    return res


def part_c():
    A = 0.9
    res, curves = [], []
    for rp, Lz in ((10.0, H.lz_range(10.0, A)[0]), (10.0, 2.2), (10.0, 0.0), (6.0, H.lz_range(6.0, A)[1])):
        xb, vb, Q = H.parabolic_state("bks", A, rp, Lz, P["r0"])
        m = 1e-300
        y0 = np.concatenate([xb, vb, xb + np.array([0.0, 0.0, 1e3]), vb])     # member 2 parked far away
        t_end = 6.0 * (math.sqrt(2.0) / 3.0) * 2 * P["r0"] ** 1.5 if rp > 7 else 6000.0
        out = B.integrate(hrna.LAW_HRNA, B.COORDS_BKS, hrna.PAIR_GRAVITY, 1.0, A, m, m, 0.0, 0.0, y0,
                          1.0, 1e-12, 1e-14, 1e300, 1e300, 0.0, t_end, 10 ** 7, 1.0, 10 ** 6,
                          hrna._A, hrna._B, hrna._C, hrna._E3, hrna._E5, hrna._work())
        t, Y = np.array(out[4]), np.array(out[5])
        X, V = Y[:, 0:3], Y[:, 3:6]
        rr = np.array([float(kerr.cks_radius(x, A)) for x in X])
        back = np.where((np.arange(len(t)) > np.argmin(rr)) & (rr >= P["r0"]))[0]
        n = back[0] + 1 if len(back) else len(t)
        t, X, V, rr = t[:n], X[:n], V[:n], rr[:n]
        # events in Kerr-Schild time
        tks = t + np.array([B.F_of_r(r, A) for r in rr]) - B.F_of_r(rr[0], A)
        Vks = np.array([B.bks_to_cks_velocity(X[i], V[i], A) for i in range(n)])
        # covariant u in Cartesian Kerr-Schild
        U = []
        for i in range(n):
            g, gi, dg = np.zeros((4, 4)), np.zeros((4, 4)), np.zeros((3, 4, 4))
            hrna.metric_cks(X[i], 1.0, A, g, gi, dg)
            xd = np.array([1.0, *Vks[i]])
            gam = 1 / math.sqrt(-(xd @ g @ xd))
            U.append(gam * (g[1:, :] @ xd))
        U = np.array(U)
        ref = geodesic.integrate("cks", X[0], U[0], tks[-1], t_eval=tks, rtol=1e-13, atol=1e-13, a=A,
                                 M=1.0)
        dx = np.linalg.norm(X - ref.x, axis=1)
        E, L, Qs = kerr.invariants("cks", X, U, A, 1.0)
        res.append(dict(rp=rp, Lz=Lz, Q=Q, n=int(n), max_dx=float(dx.max()),
                        max_dE=float(np.abs(E - 1).max()), max_dLz=float(np.abs(L - Lz).max()),
                        max_dQ=float(np.abs(Qs - Q).max()), r_min=float(rr.min())))
        curves.append((t, dx, rr))
    return res, curves


def drift(coords, spin, iota, rp=10.0):
    Lz = H.lz_range(rp, spin)[1]
    t, Y, _, info = run_rec(coords, spin, rp, Lz, iota, 0.0, 0.0)
    m1, m2 = info["m1"], info["m2"]
    mb = m1 + m2
    xc = (m1 * Y[:, 0:3] + m2 * Y[:, 6:9]) / mb
    vc = (m1 * Y[:, 3:6] + m2 * Y[:, 9:12]) / mb
    d = Y[:, 0:3] - Y[:, 6:9]
    w = Y[:, 3:6] - Y[:, 9:12]
    Eb = 0.5 * (w * w).sum(1) - mb / np.linalg.norm(d, axis=1)
    Lb = np.cross(d, w)
    Lh = Lb / np.linalg.norm(Lb, axis=1)[:, None]
    rc = np.linalg.norm(xc, axis=1)
    ipk = int(np.argmin(rc))
    sl = slice(0, ipk + 1)
    # leading-order prediction along the run's own path
    rbl = np.array([hrna.cks_r(x, spin) for x in xc[sl]])
    Hs = rbl ** 3 / (rbl ** 4 + spin ** 2 * xc[sl, 2] ** 2)
    n = xc[sl] / rc[sl, None]
    ab = mb / (2 * np.abs(Eb[sl]))
    om = np.sqrt(mb / ab ** 3)
    rate = -2 * Hs * om * np.einsum("ij,ij->i", np.cross(n, vc[sl]), Lh[sl])
    pred = np.concatenate([[0.0], np.cumsum(0.5 * (rate[1:] + rate[:-1]) * np.diff(t[sl]))])
    # smooth the measured curve over one binary period (the instantaneous E_b oscillates)
    lnE = np.log(np.abs(Eb[sl] / Eb[0]))
    return dict(t=t[sl], r=rc[sl], lnE=lnE, pred=pred)


def part_d():
    res, curves = [], {}
    for coords, spin in (("sch", 0.0), ("cks", 0.0), ("bks", 0.0), ("cks", 0.9), ("bks", 0.9)):
        for iota in (0.0, math.pi / 2, math.pi):
            c = drift(coords, spin, iota)
            curves[(coords, spin, iota)] = c
            row = dict(coords=coords, spin=spin, iota=iota)
            for rr in (50.0, 30.0, 15.0):
                k = int(np.argmin(np.abs(c["r"] - rr)))
                row[f"lnE_at_{rr:g}"] = float(c["lnE"][k])
                row[f"pred_cks_at_{rr:g}"] = float(c["pred"][k])
            res.append(row)
    return res, curves


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    ra = part_a()
    rb = part_b()
    rc, cc = part_c()
    rd, cd = part_d()
    ok = dict(a=ra["ginv"] < 1e-12 and ra["dg_fd"] < 1e-7 and max(ra["sch_g"], ra["sch_gi"], ra["sch_dg"]) < 1e-12,
              b=all(r["nsteps"][0] == r["nsteps"][1] and r["max_dpos"] < 1e-8 for r in rb),
              c=all(r["max_dx"] < 1e-6 and r["max_dE"] < 1e-9 and r["max_dQ"] < 1e-8 * max(1, r["Q"]) for r in rc))
    # odd part in iota of ln|E_b| (the slicing term is odd, cos iota; coordinate measures of E_b and
    # the tide's mean are even): (iota = pi minus iota = 0)/2, minus the same in 'sch' (whose odd
    # part is the physical tide plus HRNA's own terms), against the leading-order prediction
    odd = []
    for coords, spin in (("cks", 0.0), ("bks", 0.0), ("cks", 0.9), ("bks", 0.9)):
        row = dict(coords=coords, spin=spin)
        for rr in (50.0, 30.0, 15.0):
            def at(c, key):
                k = int(np.argmin(np.abs(c["r"] - rr)))
                return float(c[key][k])
            o = 0.5 * (at(cd[(coords, spin, math.pi)], "lnE") - at(cd[(coords, spin, 0.0)], "lnE"))
            o_s = 0.5 * (at(cd[("sch", 0.0, math.pi)], "lnE") - at(cd[("sch", 0.0, 0.0)], "lnE"))
            p_ = 0.5 * (at(cd[(coords, spin, math.pi)], "pred") - at(cd[(coords, spin, 0.0)], "pred"))
            row[f"odd_minus_sch_at_{rr:g}"] = o - o_s
            row[f"pred_cks_odd_at_{rr:g}"] = p_
        odd.append(row)
    res = dict(a=ra, b=rb, c=rc, d=rd, d_odd=odd, pass_=ok)
    with open(os.path.join(outdir, "t8_bks_chart.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(res, indent=1))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.0))
    ax1 = fs.inch_axes(fig, 0.7, 0.5, 2.0, 2.2)
    ax2 = fs.inch_axes(fig, 3.3, 0.5, 2.0, 2.2)
    ax3 = fs.inch_axes(fig, 5.9, 0.5, 2.0, 2.2)
    cols = fs.series_colors(4)
    for (t, dx, rr), r, c in zip(cc, rc, cols):
        ax1.semilogy(t, dx + 1e-18, color=c, label=f"$r_p={r['rp']:g}$, $L_z={r['Lz']:+.2f}$")
    ax1.set_xlabel(r"$t_{\rm BL}$ [$GM/c^3$]")
    ax1.set_ylabel(r"$|x_{\rm bks}-x_{\rm ref}|$ [$r_g$]")
    ax1.set_title("(c) single body, $a=0.9$", fontsize=8)
    ax1.legend(fontsize=5.5)
    # (d, middle) raw ln|E_b| of the retrograde binary: the runaway of 'cks'
    for (coords, spin), c, ls in ((("sch", 0.0), "k", "-"), (("cks", 0.0), cols[0], "-"), (("bks", 0.0), cols[1], ":"),
                                  (("cks", 0.9), cols[2], "-"), (("bks", 0.9), cols[3], "-")):
        cv = cd[(coords, spin, math.pi)]
        ax2.plot(cv["r"], cv["lnE"], ls, color=c, label=f"{coords} $a={spin:g}$")
    ax2.set_title(r"(d) retrograde $\iota=\pi$: $\ln|E_b/E_b(0)|$", fontsize=8)
    ax2.legend(fontsize=5.5)
    # (d, right) odd part in iota, (iota = pi minus iota = 0)/2, minus that of 'sch', on a common r grid
    rg = np.geomspace(99.0, 10.5, 300)

    def odd(coords, spin, key="lnE"):
        v = []
        for iota in (math.pi, 0.0):
            cv = cd[(coords, spin, iota)]
            v.append(np.interp(rg, cv["r"][::-1], cv[key][::-1]))
        return 0.5 * (v[0] - v[1])
    o_s = odd("sch", 0.0)
    for (coords, spin), c in ((("cks", 0.0), cols[0]), (("cks", 0.9), cols[2]), (("bks", 0.9), cols[3])):
        ax3.plot(rg, odd(coords, spin) - o_s, "-", color=c, label=f"{coords} $a={spin:g}$ minus sch")
    ax3.plot(rg, odd("cks", 0.0, "pred"), "--", color=cols[0], label="leading order (cks)")
    ax3.set_ylim(-0.1, 0.4)
    ax3.axhline(0, **fs.MASK_LINE)
    ax3.set_title(r"(d) odd part in $\iota$ of $\ln|E_b|$", fontsize=8)
    ax3.legend(fontsize=5.5)
    for ax in (ax2, ax3):
        ax.set_xscale("log")
        ax.invert_xaxis()
        ax.set_xlabel(r"CM radius on the way in [$r_g$]")
    fs.save(fig, os.path.join(outdir, "t8_bks_chart"))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.environ["NRPIC_RUN_DIR"])
