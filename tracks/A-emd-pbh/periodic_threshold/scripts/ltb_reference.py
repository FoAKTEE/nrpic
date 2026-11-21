"""Exact reference of the spherical periodic peak (run P0L): per shell the turnaround, the
marginally trapped sphere R = 2M, the crunch and the first shell crossing, for

  A  the profile of arXiv:2609.14218 (ln Psi = (mu/2) e^(-k^2 r^2/6), simultaneous bang,
     MDPBH.tex:560-704; ltb2609.Profile2609), and
  B  the code's own initial slice (make_field data that P0L starts from; ltbref.py),

in code units (G = c = 1, H_i = 1 at a_i = 1, k = eps_i) and in the proper time tau of the
dust from the initial slice, which the tracked particles carry; background time t/t_H =
(t_i + tau)/t_H, t_H = t_i (6/eps_i^2)^(3/2). Also: the background of the relaxed 1+log
lapse (lapse_leak), the periodic-image estimates, a figure and a JSON summary.

    python3 ltb_reference.py --data DIR [--mu 0.3] [--rate 20] --out DIR

DIR is the P0_mu0.3 directory of build_p0l.sh (fields.bin, id.json, track.json).
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figstyle as fs   # noqa: E402
import ltbref as R      # noqa: E402

T_I = 2.0 / 3.0


def fnum(v):
    v = float(v)
    return v if math.isfinite(v) else None


def interp_mass(M_of, ev, Mq):
    """Event times of reference at the masses Mq (log-linear in M; M increasing)."""
    o = np.argsort(M_of)
    lm = np.log(M_of[o])
    return {k: np.interp(np.log(Mq), lm, v[o], left=np.nan, right=np.nan)
            for k, v in ev.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--mu", type=float, default=0.3)
    ap.add_argument("--rate", type=float, default=20.0, help="lapse_leak = 1/T")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    info = json.load(open(os.path.join(a.data, "id.json")))
    eps = float(info["eps_i"])
    k = float(info["k"])
    L = float(info["L"])
    t_H = T_I * (6.0 / eps ** 2) ** 1.5
    res = dict(mu=a.mu, eps_i=eps, k=k, L=L, t_i=T_I, t_H=t_H, data=os.path.abspath(a.data))

    # ------------------------------------------------------------------ A
    rA = np.concatenate([np.linspace(0.005, 0.2, 40), np.linspace(0.2, 9.4, 921)[1:]]) / k
    P, rA, shA = R.reference_A(a.mu, k, T_I, rA)
    evA = shA.events()
    tauA_sc, jA = R.first_crossing(shA, rA, tau_max=3000.0, n=6001)
    ts0 = float(P.t_s(0.0)) - T_I
    jmin = int(np.nanargmin(evA["tau_ah"]))
    res["A"] = dict(
        locator="ltb2609.Profile2609 (MDPBH.tex:573-743), simultaneous bang, a_i = 1 at t_i",
        r_m=P.r_m, M_rm=fnum(P.M(P.r_m)),
        tau_crunch_centre=ts0, tH_crunch_centre=fnum(R.t_over_tH(ts0, eps)),
        first_trapped=dict(r=fnum(rA[jmin]), tau=fnum(evA["tau_ah"][jmin]),
                           tau_minus_crunch_centre=fnum(evA["tau_ah"][jmin] - ts0)),
        all_shells_bound=bool(np.all(shA.E < 0)),
        first_shell_crossing_tau=fnum(tauA_sc),
        first_shell_crossing_r=fnum(rA[jA]) if jA >= 0 else None,
        crunch_time_monotone_in_r=bool(np.all(np.diff(evA["tau_c"]) > 0)),
        shells=[dict(r=fnum(rr), M=fnum(m), E=fnum(e), tau_ta=fnum(t1), tau_ah=fnum(t2),
                     tau_c=fnum(t3), R_max=fnum(rm))
                for rr, m, e, t1, t2, t3, rm in zip(rA[::20], shA.M[::20], shA.E[::20],
                                                     evA["tau_ta"][::20], evA["tau_ah"][::20],
                                                     evA["tau_c"][::20], evA["R_max"][::20])])

    # ------------------------------------------------------------------ B
    fields = R.read_fields(os.path.join(a.data, "fields.bin"))
    tr = json.load(open(os.path.join(a.data, "track.json")))
    trk = [t for t in tr["tracked"] if t["r0"] > 0]
    x0 = np.array([t["x0"] for t in trk])
    u0 = np.array([t["u0"] for t in trk])
    shB, qB = R.reference_B(fields, L, x0, u0)
    evB = shB.events()
    labels = np.array([t["label"] for t in trk])
    tags = np.array([t["tag"] for t in trk])
    # spread over directions at equal lattice offset (lattice and box anisotropy)
    axes = np.isin(labels, ["+x", "-x", "+y", "-y", "+z", "-z"])
    diag = ~axes
    # shell crossing along each direction separately
    sc = []
    for lab in np.unique(labels):
        s = labels == lab
        t_sc, j = R.first_crossing(R.Shells(shB.M[s], shB.E[s], shB.age0[s]), qB["r0"][s],
                                   tau_max=600.0, n=3001)
        sc.append((t_sc, lab, float(qB["r0"][s][j]) if j >= 0 else None))
    sc_f = [v for v in sc if math.isfinite(v[0])]
    first_sc = min(sc_f) if sc_f else (math.nan, None, None)
    # compare with A at equal Misner-Sharp mass
    evA_atB = interp_mass(shA.M, evA, shB.M)
    rel = {kk: (evB[kk] - evA_atB[kk]) / evA_atB[kk] for kk in ("tau_ta", "tau_ah", "tau_c")}
    jB = int(np.nanargmin(np.where(axes, evB["tau_ah"], np.nan)))
    inner = axes & (qB["r0"] < 0.35)
    res["B"] = dict(
        locator="ltbref.reference_B on fields.bin and track.json of the data directory",
        n_shells=int(len(trk)),
        far_field=dict(alpha=fnum(np.median(qB["alpha"][qB["r0"] > 8])),
                       psi=fnum(np.median(qB["psi"][qB["r0"] > 8]))),
        age0_range=[fnum(np.min(qB["age0"])), fnum(np.max(qB["age0"]))],
        tau_crunch_innermost=fnum(np.nanmin(evB["tau_c"][inner])),
        first_trapped_axes=dict(r0=fnum(qB["r0"][jB]), M=fnum(shB.M[jB]),
                                tau=fnum(evB["tau_ah"][jB])),
        first_shell_crossing=dict(tau=fnum(first_sc[0]), direction=first_sc[1],
                                  r0=first_sc[2]),
        crossing_per_direction={lab: fnum(t) for t, lab, _ in sc},
        all_shells_bound=bool(np.all(shB.E < 0)),
        rel_diff_B_minus_A_at_equal_M=dict(
            {kk: dict(median_r0_0p8_to_3=fnum(np.nanmedian(v[axes & (qB["r0"] > 0.8)
                                                              & (qB["r0"] < 3.0)])),
                      max_abs_r0_0p8_to_3=fnum(np.nanmax(np.abs(v[axes & (qB["r0"] > 0.8)
                                                                  & (qB["r0"] < 3.0)]))))
             for kk, v in rel.items()}),
        anisotropy_axes_vs_diag=None,
        shells=[dict(tag=int(tg), label=str(lb), r0=fnum(r0), M=fnum(m), E=fnum(e),
                     age0=fnum(ag), R0=fnum(r00), U0=fnum(uu), tau_ta=fnum(t1),
                     tau_ah=fnum(t2), tau_c=fnum(t3), R_max=fnum(rm))
                for tg, lb, r0, m, e, ag, r00, uu, t1, t2, t3, rm in zip(
                    tags, labels, qB["r0"], shB.M, shB.E, qB["age0"], qB["R0"], qB["U0"],
                    evB["tau_ta"], evB["tau_ah"], evB["tau_c"], evB["R_max"])])
    # anisotropy: M at equal r0 along axes against diagonals, interpolated in ln M against
    # ln r0 (M ~ r0^3 near the centre; a linear interpolation in r0 between axis shells
    # 0.3 apart is wrong by up to 18 per cent at r0 ~ 0.5: first run A-20261121-125808-7366ccd)
    oa = np.argsort(qB["r0"][axes])
    Md = shB.M[diag]
    Ma = np.exp(np.interp(np.log(qB["r0"][diag]), np.log(qB["r0"][axes][oa]),
                          np.log(shB.M[axes][oa])))
    sel = (qB["r0"][diag] > 0.5) & (qB["r0"][diag] < 5.0)
    s5 = qB["r0"] < 5.0
    res["B"]["anisotropy_axes_vs_diag"] = dict(
        max_rel_M_diag_minus_axes_r0_0p5_to_5_loglog=fnum(np.max(np.abs(Md[sel] / Ma[sel]
                                                                         - 1.0))))
    res["B"]["age0_range_r0_below_5"] = [fnum(np.min(qB["age0"][s5])),
                                         fnum(np.max(qB["age0"][s5]))]
    res["B"]["tH_crunch_innermost"] = fnum(R.t_over_tH(res["B"]["tau_crunch_innermost"], eps))

    # ------------------------------------------------------------------ background (lapse_leak)
    tB, aB, alB, tauB = R.leak_background(a.rate, 260.0, dt=2e-3,
                                          alpha0=res["B"]["far_field"]["alpha"] or 1.0)
    res["background_leak"] = dict(
        rate=a.rate, T=1.0 / a.rate,
        equation="d a/dt = alpha a H, d ln alpha/dt = 6 H - rate max(ln alpha, 0), H = a^-3/2",
        alpha_at={str(t): fnum(np.interp(t, tB, alB)) for t in (0.05, 0.5, 3.0, 10.0, 50.0,
                                                                100.0, 200.0)},
        a_at={str(t): fnum(np.interp(t, tB, aB)) for t in (3.0, 10.0, 50.0, 100.0, 200.0)},
        proper_minus_coordinate_at={str(t): fnum(np.interp(t, tB, tauB) - t)
                                    for t in (3.0, 10.0, 50.0, 100.0, 200.0)},
        coordinate_time_of_tH={str(x): fnum(np.interp(x * t_H - T_I, tauB, tB))
                               for x in (2.9, 8.8, 10.0, 13.0, 16.0, 21.9, 25.0)})

    # ------------------------------------------------------------------ periodic images
    u = (k * 0.5 * L) ** 2 / 6.0
    zmean = a.mu * (6.0 * math.pi) ** 1.5 / k ** 3 / L ** 3
    res["periodic_images"] = dict(
        zeta_at_face_over_mu=math.exp(-u),
        delta_at_face_over_centre=abs((1.0 - 2.0 * u / 3.0) * math.exp(-u)),
        zeta_at_image_over_mu=math.exp(-(k * L) ** 2 / 6.0),
        mean_zeta_removed=zmean,
        note=("the profile is compensated (zero mass excess at large r): an image acts on "
              "the peak only through the overlap of its tail, ~exp(-k^2 (L/2)^2/6); the "
              "zero mode removed by the periodic solve shifts the background by the mean of "
              "zeta, included in B; inscribed sphere of the box r = L/2"))

    with open(os.path.join(a.out, "ltb_reference.json"), "w") as f:
        json.dump(res, f, indent=1)
    np.savez(os.path.join(a.out, "ltb_reference.npz"), rA=rA, MA=shA.M, EA=shA.E,
             tauA_ta=evA["tau_ta"], tauA_ah=evA["tau_ah"], tauA_c=evA["tau_c"],
             tagB=tags, r0B=qB["r0"], MB=shB.M, EB=shB.E, ageB=qB["age0"],
             tauB_ta=evB["tau_ta"], tauB_ah=evB["tau_ah"], tauB_c=evB["tau_c"],
             labelB=labels, t_bg=tB, a_bg=aB, alpha_bg=alB, tau_bg=tauB)

    # ------------------------------------------------------------------ figure
    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(8.0, 6.6))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.08, top=0.97, wspace=0.3, hspace=0.32)
    c = fs.SERIES
    # (a) events against M
    ax = fig.add_subplot(2, 2, 1)
    for kk, ls, lab in (("tau_ta", ":", "turnaround"), ("tau_ah", "--", "R = 2M"),
                        ("tau_c", "-", "crunch")):
        ax.loglog(shA.M, evA[kk], color=c[0], ls=ls, label=f"A {lab}")
        ax.loglog(shB.M[axes], evB[kk][axes], ls="none", marker="o", ms=2.5, color=c[1])
        ax.loglog(shB.M[diag], evB[kk][diag], ls="none", marker="x", ms=3, color=c[2])
    ax.plot([], [], ls="none", marker="o", color=c[1], label="B axes")
    ax.plot([], [], ls="none", marker="x", color=c[2], label="B diagonals")
    ax.set_xlim(1e-3, 300)
    ax.set_ylim(20, 3000)
    ax.set_xlabel(r"Misner-Sharp mass $M$")
    ax.set_ylabel(r"proper time $\tau$ from the slice")
    ax.legend(fontsize=7, loc="upper left")
    # (b) B relative to A at equal M
    ax = fig.add_subplot(2, 2, 2)
    for kk, col, lab in (("tau_ta", c[2], "turnaround"), ("tau_ah", c[1], "R = 2M"),
                         ("tau_c", c[0], "crunch")):
        ax.semilogx(qB["r0"][axes], rel[kk][axes], ls="none", marker="o", ms=2.5,
                    color=col, label=lab)
    ax.axhline(0.0, **fs.THIN)
    ax.axvline(P.r_m, **fs.MASK_LINE)
    ax.set_xlabel(r"initial coordinate radius $r_0$ of the shell (B)")
    ax.set_ylabel(r"$(\tau_B - \tau_A)/\tau_A$ at equal $M$")
    ax.legend(fontsize=7)
    # (c) world lines R(tau) of a few shells
    ax = fig.add_subplot(2, 2, 3)
    pick = [0.6, 1.0, 1.5, 2.45, 3.5]
    cc = fs.series_colors(len(pick))
    tau = np.linspace(0, 400, 2001)
    for r0, col in zip(pick, cc):
        j = int(np.argmin(np.abs(np.where(axes, qB["r0"], 1e9) - r0)))
        RB = R.Shells(shB.M[j:j + 1], shB.E[j:j + 1], shB.age0[j:j + 1]).R(tau[:, None])[:, 0]
        ax.plot(tau, RB, color=col, label=f"B r0={qB['r0'][j]:.2f}, M={shB.M[j]:.3g}")
        iA = int(np.argmin(np.abs(np.log(shA.M / shB.M[j]))))
        RA = R.Shells(shA.M[iA:iA + 1], shA.E[iA:iA + 1], shA.age0[iA:iA + 1]).R(tau[:, None])[:, 0]
        ax.plot(tau, RA, color=col, ls="--", lw=1.0)
        ax.axhline(2 * shB.M[j], color=col, lw=0.6, ls=":")
    ax.set_xlabel(r"$\tau$")
    ax.set_ylabel(r"areal radius $R$ (dashed: A at equal $M$; dotted: $2M$)")
    ax.set_ylim(0, 90)
    ax.legend(fontsize=6.5, loc="upper right")
    # (d) background of the relaxed lapse
    ax = fig.add_subplot(2, 2, 4)
    ax.semilogx(tB[1:], alB[1:], color=c[1], label=r"$\alpha$ (T = %.3g)" % (1 / a.rate))
    ax.semilogx(tB[1:], np.exp(6.0 / a.rate * aB[1:] ** -1.5), color=c[0], ls="--",
                label=r"$\exp(6TH)$")
    ax.set_xlabel("coordinate time t")
    ax.set_ylabel(r"background lapse")
    ax2 = ax.twinx()
    ax2.semilogx(tB[1:], (tauB[1:] - tB[1:]), color=c[3], lw=1.0)
    ax2.set_ylabel(r"$\tau - t$ (green)")
    ax.legend(fontsize=7, loc="upper right")
    fs.save(fig, os.path.join(a.out, "fig_ltb_reference"))
    print(json.dumps({kk: v for kk, v in res.items() if kk not in ("A", "B")}, indent=1))
    print(json.dumps({kk: v for kk, v in res["A"].items() if kk != "shells"}, indent=1))
    print(json.dumps({kk: v for kk, v in res["B"].items() if kk != "shells"}, indent=1))


if __name__ == "__main__":
    main()
