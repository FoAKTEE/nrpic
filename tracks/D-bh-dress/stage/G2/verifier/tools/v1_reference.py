"""V1: test the verifier's LTB reference on closed forms, then build it from the particle
files of the three dust lattices (N, 4N, N/4) and compare with the data maker's numbers.

python3 v1_reference.py --data <N data run dir> --data4n <..> --dataq <..> --out <dir>
"""
import argparse
import json
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ltb  # noqa: E402
import vio  # noqa: E402
import figstyle as fs  # noqa: E402


def closed_form_tests():
    res = {}
    # (a) fall from rest at Rmax to R = 0: tau = (pi/2) sqrt(Rmax^3 / 2m)
    for Rmax, m in [(3.0, 1.0), (30.0, 1.7), (200.0, 2.5)]:
        A = Rmax / 2.0
        T = A ** 1.5 / np.sqrt(m)
        tau_cyc = T * ((2 * np.pi - 0.0) - np.pi)  # eta from pi to 2 pi
        tau_exact = 0.5 * np.pi * np.sqrt(Rmax ** 3 / (2 * m))
        res[f"fall_Rmax{Rmax}_m{m}"] = abs(tau_cyc / tau_exact - 1)
    # tau_horizon with m = M (shell at rest at R0 = Rmax) against quadrature of
    # dtau = dR / sqrt(2m/R - 2m/Rmax) from 2m to Rmax
    from scipy.integrate import quad
    for R0 in [3.0003, 10.0, 40.0]:
        m = 1.0
        f = lambda R: 1.0 / np.sqrt(2 * m / R - 2 * m / R0)
        q, _ = quad(f, 2 * m, R0, limit=200, epsabs=1e-13, epsrel=1e-13)
        res[f"rest_R0{R0}"] = abs(ltb.tau_horizon(R0, m) / q - 1)
    # (b) expanding start: RK integration of d2R/dtau2 = -m/R^2 from (R0, +sqrt(2(m-M)/R0))
    for R0, m in [(5.0, 1.02), (20.0, 1.3), (40.0, 2.0), (55.0, 3.6)]:
        v0 = np.sqrt(2 * (m - 1.0) / R0)

        def rhs(t, y):
            return [y[1], -m / y[0] ** 2]

        def ev(t, y):
            return y[0] - 2 * m
        ev.terminal = True
        ev.direction = -1
        sol = solve_ivp(rhs, [0, 1e6], [R0, v0], events=ev, rtol=1e-12, atol=1e-12,
                        method="DOP853")
        tH = sol.t_events[0][0]
        res[f"rk_R0{R0}_m{m}"] = abs(ltb.tau_horizon(R0, m) / tH - 1)
        # radius inversion at half the time
        Rh = ltb.radius_at_tau(np.array([0.5 * tH]), R0, m)[0]
        s2 = solve_ivp(rhs, [0, 0.5 * tH], [R0, v0], rtol=1e-12, atol=1e-12,
                       method="DOP853")
        res[f"Rinv_R0{R0}_m{m}"] = abs(Rh / s2.y[0, -1] - 1)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--data4n", required=True)
    ap.add_argument("--dataq", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    out = {"closed_form": closed_form_tests()}
    out["closed_form_max"] = max(out["closed_form"].values())
    curves = {}
    for lab, d in [("N", a.data), ("4N", a.data4n), ("N/4", a.dataq)]:
        x, u, m, sp = vio.read_nrp(os.path.join(d, "esf.nrp"))
        ref, curve = ltb.lattice_reference(x, m)
        dust = ref["dust"]
        info = json.load(open(os.path.join(d, "esf.json")))
        tH, mm = curve
        # V1c: half-weight lattice and the continuum of the evolved table
        dmv = m * ref["EK"]
        mid = ltb.lattice_mid(ref["R0"], dmv, dust)
        Rt, mt = ltb.table_mass(os.path.join(d, "esf.tab"))
        sel = (Rt > 3.0) & (Rt < 61.0)
        tHt = ltb.tau_horizon(Rt[sel], mt[sel])
        curve_tab = (tHt, mt[sel])
        m_tab_p = np.interp(ref["R0"], Rt, mt)
        tauH_tab = ltb.tau_horizon(ref["R0"], m_tab_p)
        tauH_mid = np.where(dust, ltb.tau_horizon(ref["R0"], np.where(dust, mid, 1.0)), np.nan)
        win = dust & (ref["R0"] > 5) & (ref["R0"] < 55)
        mid_vs_tab = float(np.max(np.abs(mid[win] - m_tab_p[win])))
        incl_vs_tab = float(np.max(np.abs(ref["mdisc"][win] - m_tab_p[win])))
        mono = bool(np.all(np.diff(tH) >= -1e-9))
        # non-monotone pairs: largest decrease
        dec = float(np.min(np.diff(tH))) if len(tH) > 1 else 0.0
        taus = [25, 50, 100, 150, 200, 250, 300, 400, 600]
        mine = ltb.growth_from_curve(curve, np.array(taus, float))
        theirs = [info["growth"][f"tau={t}"] for t in taus]
        trac = {}
        R0t = ref["R0"][~dust]
        for g in np.unique(np.round(R0t, 3)):
            sel = np.abs(R0t - g) < 1e-3
            trac[f"{g:.3f}"] = [int(sel.sum()), float(np.median(ref["tauH"][~dust][sel]))]
        out[lab] = dict(
            n=int(len(m)), n_dust=int(dust.sum()), u_max=float(np.abs(u).max()),
            rest_mass_dust=float(m[dust].sum()),
            ms_lattice=float(mm[-1] - 1.0), ms_lattice_datamaker=info["lattice_misner_sharp"],
            ms_diff=float(mm[-1] - 1.0 - info["lattice_misner_sharp"]),
            tauH_monotonic=mono, tauH_min_step=dec,
            tauH_min=float(tH[0]),
            growth_mine=dict(zip(map(str, taus), map(float, mine))),
            growth_datamaker=dict(zip(map(str, taus), theirs)),
            growth_maxdiff=float(np.max(np.abs(mine - np.array(theirs)))),
            tracers=trac,
            m_tab_edge=float(mt[sel][-1] - 1.0), Dtot=info["Dtot"],
            growth_tab=dict(zip(map(str, taus), map(float, ltb.growth_from_curve(curve_tab, np.array(taus, float))))),
            growth_tab_vs_dm=float(np.max(np.abs(ltb.growth_from_curve(curve_tab, np.array(taus, float)) - np.array(theirs)))),
            tab_monotonic=bool(np.all(np.diff(tHt) > 0)),
            mid_vs_tab_max=mid_vs_tab, incl_vs_tab_max=incl_vs_tab,
            tauH_tab_tracers={g: float(np.median(tauH_tab[~dust][np.abs(ref["R0"][~dust] - float(g)) < 1e-3])) for g in trac},
            tauH_mid_minus_tab_dust_rms=float(np.sqrt(np.nanmean((tauH_mid - tauH_tab)[win] ** 2))),
        )
        np.savez_compressed(os.path.join(a.out, f"ltbref_{lab.replace('/', 'q')}.npz"),
                            R0=ref["R0"], EK=ref["EK"], mdisc=ref["mdisc"],
                            tauH=ref["tauH"], m=m, tH_curve=tH, m_curve=mm,
                            mid=mid, tauH_mid=tauH_mid, m_tab_p=m_tab_p, tauH_tab=tauH_tab,
                            tH_tab=tHt, m_tab=mt[sel])
        curves[lab] = curve
        curves[lab + "_tab"] = curve_tab
        # continuum curve of the data maker
        g = np.loadtxt(os.path.join(d, "esf_growth.csv"), delimiter=",", skiprows=1)
        curves[lab + "_dm"] = (g[:, 2], g[:, 1])
    json.dump(out, open(os.path.join(a.out, "v1_reference.json"), "w"), indent=1)

    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(8, 3.4))
    ax1 = fig.add_axes([0.08, 0.15, 0.40, 0.78])
    ax2 = fig.add_axes([0.58, 0.15, 0.40, 0.78])
    tH, mm = curves["N"]
    ax1.plot(tH, mm, color=fs.PAL["red"], label="lattice N (verifier)")
    tg, mg = curves["N_dm"]
    ax1.plot(tg, mg, color=fs.PAL["blue"], ls="--", label="continuum (data maker)")
    ax1.plot(*curves["N_tab"], color="k", ls=":", label="continuum (from esf.tab, verifier)")
    ax1.set_xlim(0, 700)
    ax1.set_ylim(0.98, 1.75)
    ax1.set_xlabel(r"$\tau_H$ [M]")
    ax1.set_ylabel(r"$M_{\rm LTB}$ [M]")
    ax1.legend(loc="upper left")
    tt = np.linspace(5, 650, 600)
    cont = np.interp(tt, tg, mg)
    for lab, col in [("N", fs.PAL["red"]), ("4N", fs.PAL["yellow"]), ("N/4", fs.PAL["green"])]:
        ax2.plot(tt, ltb.growth_from_curve(curves[lab], tt) / cont - 1, color=col,
                 label=f"lattice {lab}")
    ax2.plot(tt, ltb.growth_from_curve(curves["N_tab"], tt) / cont - 1, color="k", ls=":",
             label="table continuum")
    ax2.axhline(0, color="k", lw=1, ls="--")
    ax2.set_xlabel(r"$\tau$ [M]")
    ax2.set_ylabel(r"$M_{\rm lattice}/M_{\rm continuum}-1$")
    ax2.legend(loc="lower right")
    fs.save(fig, os.path.join(a.out, "v1_reference"))
    print(json.dumps({k: (v if not isinstance(v, dict) else {kk: vv for kk, vv in v.items()
                      if kk not in ("growth_mine", "growth_datamaker")}) for k, v in out.items()},
                     indent=1))


if __name__ == "__main__":
    main()
