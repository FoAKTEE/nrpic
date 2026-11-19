#!/usr/bin/env python3
"""T4: where the first post-Newtonian order stops being trustworthy (test-mass limit).

Parabolic orbits of a test body about M = 1, labelled by the angular momentum per unit mass
L (gauge invariant; GR: u_phi with E = -u_t = 1; 1PN: L of 2404.16270 appendix.tex l. 186,
1PN energy 0, l. 185). For each L:
  GR     swept angle between r0 inbound and r0 outbound, by quadrature of the Schwarzschild
         orbit equation (d u/d phi)^2 = 2u/L^2 - u^2 + 2u^3 (u = M/r, E = 1) [BACKGROUND];
         areal pericentre 1/u_p, u_p the smallest positive root; capture for L < 4.
  EIH    integration of the EIH equations (eih.accel) for M = 1 and a test mass 1e-10
         (M free), started at r0 with the 1PN state of energy 0 and angular momentum L
         (eih.testmass_state), until the body is back at r0.
  1PN-Q  the same orbit by quadrature of the conserved 1PN energy and angular momentum (the
         Lagrangian 1PN dynamics; differs from EIH at 2PN order only) - a check of the EIH run.
  Newton parabola with the same L (r_p = L^2/2) between the same radii.
Pericentres are compared in harmonic coordinates (GR: r_h = r_areal - M [BACKGROUND]).
The relativistic excess Delta phi - Delta phi_Newton and its L derivative (how differently two
members with different L are deflected) are compared between GR and EIH.
Usage: trust.py [outdir]   (default $NRPIC_RUN_DIR). Writes trust.json and fig_t4_trust.
"""
import json
import math
import os
import sys

import numpy as np
from scipy.integrate import quad, solve_ivp

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
WT = os.path.abspath(os.path.join(PKG, "..", "..", ".."))
sys.path.insert(0, PKG)
sys.path.insert(0, os.path.join(WT, "python"))
import eih  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

R0 = 1.0e4


def L_of_rp_gr(rp):
    """GR parabola (E = 1) with areal pericentre rp (2404.16270 appendix.tex l. 175)."""
    return math.sqrt(2.0 * rp * rp / (rp - 2.0))


def gr_roots(L):
    d = 1.0 - 16.0 / L ** 2
    if d < 0:
        return None
    return (1 - math.sqrt(d)) / 4, (1 + math.sqrt(d)) / 4


def gr_swept(L, r0=R0):
    """Swept angle of the GR parabola between r0 and r0; areal pericentre."""
    up, u2 = gr_roots(L)
    u0 = 1.0 / r0
    g = lambda u: 1.0 / math.sqrt(2.0 * (u2 - u))  # noqa: E731
    full, _ = quad(g, 0.0, up, weight="alg", wvar=(-0.5, -0.5), limit=400, epsabs=1e-13,
                   epsrel=1e-13)
    # remove [0, u0]: integrand 1/sqrt(2u(up-u)(u2-u)) ~ smooth / sqrt(u)
    h = lambda u: 1.0 / math.sqrt(2.0 * (up - u) * (u2 - u))  # noqa: E731
    tail, _ = quad(h, 0.0, u0, weight="alg", wvar=(-0.5, 0.0), epsabs=1e-15, epsrel=1e-13)
    return 2.0 * (full - tail), 1.0 / up


def newton_swept(L, r0=R0):
    p = L * L
    return 2.0 * math.acos(p / r0 - 1.0), p / 2.0


def pn_quadrature(L, r0=R0):
    """Swept angle from the conserved 1PN E = 0 and L (2404 EIH1, EIH2) by quadrature in r."""
    def rdot_phidot(r):
        st = eih.testmass_state(0.0, L, r)
        if st is None:
            return None
        vr, vphi = st
        return vr, vphi / r

    # turning point: v_phi^2 = v^2
    from scipy.optimize import brentq

    def f(r):
        bq = 0.5 + 1.5 / r
        cq = 0.5 / r ** 2 - 1.0 / r
        disc = bq * bq - 1.5 * cq
        v2 = (-bq + math.sqrt(disc)) / 0.75
        vphi = L / (r * (1 + 0.5 * v2 + 3.0 / r))
        return v2 - vphi * vphi
    rp = brentq(f, 0.5 + 1e-9, r0, xtol=1e-14, rtol=1e-15)

    # dphi/dr = phidot/|rdot|; substitute r = rp + s^2 to remove the turning-point singularity
    def integrand(s):
        r = rp + s * s
        if s == 0.0:
            # limit: 2 s phidot / |rdot|, rdot^2 ~ f'(rp) s^2
            h = 1e-7 * rp
            dfdr = (f(rp + h) - f(rp)) / h
            vphi = L / rp / (1 + 0.5 * (L / rp) ** 2 + 3.0 / rp)
            return 2.0 * (vphi / rp) / math.sqrt(dfdr)
        vr, phid = rdot_phidot(r)
        return 2.0 * s * phid / abs(vr)
    smax = math.sqrt(r0 - rp)
    val, _ = quad(integrand, 0.0, smax, limit=800, epsabs=1e-12, epsrel=1e-12,
                  points=[min(1.0, smax / 2)])
    return 2.0 * val, rp


def eih_swept(L, r0=R0, rtol=1e-12):
    """EIH integration, M = 1 free, test mass 1e-10; start at r0 incoming."""
    vr, vphi = eih.testmass_state(0.0, L, r0)
    ms = np.array([1.0, 1e-10])
    x = np.array([[0.0, 0, 0], [r0, 0, 0]])
    v = np.array([[0.0, 0, 0], [vr, vphi, 0]])

    def rhs(t, y):
        xx = y[:6].reshape(2, 3)
        vv = y[6:].reshape(2, 3)
        return np.concatenate([vv.ravel(), eih.accel(xx, vv, ms).ravel()])

    def back(t, y):
        return np.linalg.norm(y[3:6] - y[0:3]) - r0
    back.terminal = True
    back.direction = 1

    def peri(t, y):
        d = y[3:6] - y[0:3]
        w = y[9:12] - y[6:9]
        return d @ w
    peri.direction = 1
    T = 4.0 * math.sqrt(2.0) / 3.0 * r0 ** 1.5
    phis = []

    sol = solve_ivp(rhs, (0, T), np.concatenate([x.ravel(), v.ravel()]), method="DOP853",
                    rtol=rtol, atol=1e-14, events=(back, peri), dense_output=True)
    tt = np.linspace(0, sol.t[-1], 20001)
    Y = sol.sol(tt)
    d = (Y[3:6] - Y[0:3])
    phi = np.unwrap(np.arctan2(d[1], d[0]))
    yp = sol.y_events[1]
    rp = float(np.linalg.norm(yp[0, 3:6] - yp[0, 0:3])) if len(yp) else float("nan")
    # end exactly at r0 (event)
    ye = sol.y_events[0][0]
    de = ye[3:6] - ye[0:3]
    phi_end = math.atan2(de[1], de[0])
    phi_end = phi[-1] + ((phi_end - phi[-1] + math.pi) % (2 * math.pi) - math.pi)
    E0 = eih.energy(x, v, ms)
    Ee = eih.energy(sol.y[:6, -1].reshape(2, 3), sol.y[6:, -1].reshape(2, 3), ms)
    del phis
    return float(phi_end - phi[0]), rp, float((Ee - E0) / 1e-10)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.environ["NRPIC_RUN_DIR"]
    os.makedirs(out, exist_ok=True)
    rps = [4.2, 4.5, 5, 5.5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 18, 20, 25, 30, 40, 50, 70,
           100, 150, 200, 300]
    rows = []
    for rp_a in rps:
        L = L_of_rp_gr(rp_a)
        dg, rpa = gr_swept(L)
        dn, rpn = newton_swept(L)
        de, rpe, dEe = eih_swept(L)
        dq, rpq = pn_quadrature(L)
        rows.append(dict(rp_areal=rp_a, rp_harm_gr=rpa - 1.0, L=L, swept_gr=dg, swept_newton=dn,
                         swept_eih=de, swept_pnq=dq, rp_newton=rpn, rp_eih=rpe, rp_pnq=rpq,
                         exc_gr=dg - dn, exc_eih=de - dn, exc_pnq=dq - dn,
                         err_exc=(de - dn) / (dg - dn) - 1.0, dE_eih_per_mass=dEe))
        print(json.dumps(rows[-1]))
    # L derivative (tidal shear proxy) by centred differences in L at each point
    der = []
    for r in rows:
        L = r["L"]
        h = 1e-4 * L
        gp = gr_swept(L + h)[0] - newton_swept(L + h)[0]
        gm = gr_swept(L - h)[0] - newton_swept(L - h)[0] if L - h > 4.0 else float("nan")
        ep = eih_swept(L + h)[0] - newton_swept(L + h)[0]
        em = eih_swept(L - h)[0] - newton_swept(L - h)[0]
        dgr = (gp - gm) / (2 * h)
        deih = (ep - em) / (2 * h)
        r.update(dexc_dL_gr=dgr, dexc_dL_eih=deih, err_dexc=deih / dgr - 1.0)
        der.append((r["rp_areal"], dgr, deih))
    # the 1PN "no capture" statement: EIH turning point for L below 4
    small_L = []
    for L in (0.5, 1.0, 2.0, 3.0, 3.5, 3.9, 4.0):
        try:
            de, rpe, _ = eih_swept(L, r0=2.0e3)
            small_L.append(dict(L=L, swept_eih=de, rp_eih=rpe))
        except Exception as exc:  # noqa: BLE001
            small_L.append(dict(L=L, error=str(exc)))
    rp_arr = np.array([r["rp_areal"] for r in rows])
    err = np.array([abs(r["err_exc"]) for r in rows])
    errd = np.array([abs(r["err_dexc"]) for r in rows])

    def threshold(e, lev):
        # smallest rp beyond which the error stays below lev
        ok = e < lev
        for i in range(len(rp_arr)):
            if np.all(ok[i:]):
                return float(rp_arr[i])
        return None
    thr = {f"exc_{int(l * 100)}pct": threshold(err, l) for l in (0.05, 0.1, 0.2, 0.3, 0.5)}
    thr.update({f"dexc_{int(l * 100)}pct": threshold(errd, l) for l in (0.05, 0.1, 0.2, 0.3, 0.5)})
    with open(os.path.join(out, "trust.json"), "w") as fh:
        json.dump(dict(r0=R0, rows=rows, small_L=small_L, thresholds_rp_areal=thr), fh, indent=1)
    print(json.dumps(thr))
    print(json.dumps(small_L))
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH * 1.2, 3.0))
    rpa = rp_arr
    ax[0].loglog(rpa, [r["exc_gr"] for r in rows], "o-", color=fs.SERIES[0], label="GR (exact)")
    ax[0].loglog(rpa, [r["exc_eih"] for r in rows], "s-", color=fs.SERIES[1], label="EIH (1PN)")
    ax[0].loglog(rpa, [r["exc_pnq"] for r in rows], ":", color=fs.SERIES[2], label="1PN quadrature")
    ax[0].loglog(rpa, 3 * math.pi / (rpa - 1), **fs.GUIDE, label=r"$3\pi M/r_{p,h}$")
    ax[0].set_xlabel(r"areal pericentre $r_p/M$ (GR orbit of the same $L$)")
    ax[0].set_ylabel(r"$\Delta\phi - \Delta\phi_{\rm Newton}$ [rad]")
    ax[0].legend(frameon=False, fontsize=7)
    ax[1].semilogx(rpa, 100 * np.array([r["err_exc"] for r in rows]), "o-", color=fs.SERIES[1],
                   label=r"excess $\Delta\phi$")
    ax[1].semilogx(rpa, 100 * np.array([r["err_dexc"] for r in rows]), "s--", color=fs.SERIES[3],
                   label=r"$d\Delta\phi/dL$")
    for lev in (-10, 10):
        ax[1].axhline(lev, **fs.MASK_LINE)
    for xv in (8.0, 9.82):
        ax[1].axvline(xv, color="grey", lw=0.8, ls=":")
    ax[1].set_ylim(-100, 40)
    ax[1].set_xlabel(r"areal pericentre $r_p/M$")
    ax[1].set_ylabel("EIH error relative to GR [%]")
    ax[1].legend(frameon=False, fontsize=7)
    ax[2].plot([r["L"] for r in rows], [r["rp_harm_gr"] for r in rows], "o-", color=fs.SERIES[0],
               label="GR (harmonic $r$)")
    ax[2].plot([r["L"] for r in rows], [r["rp_eih"] for r in rows], "s-", color=fs.SERIES[1],
               label="EIH")
    ax[2].plot([r["L"] for r in rows], [r["rp_newton"] for r in rows], "^-", color="grey",
               label="Newton")
    sl = [s for s in small_L if "rp_eih" in s]
    ax[2].plot([s["L"] for s in sl], [s["rp_eih"] for s in sl], "s", color=fs.SERIES[1], mfc="none")
    ax[2].axvline(4.0, **fs.MASK_LINE)
    ax[2].text(4.1, 0.6, "GR capture\nfor $L<4M$", fontsize=7)
    ax[2].set_xlim(0, 12)
    ax[2].set_ylim(0, 40)
    ax[2].set_xlabel(r"$L/M$")
    ax[2].set_ylabel(r"pericentre (harmonic) $/M$")
    ax[2].legend(frameon=False, fontsize=7)
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "fig_t4_trust"))
    plt.close(fig)


if __name__ == "__main__":
    main()
