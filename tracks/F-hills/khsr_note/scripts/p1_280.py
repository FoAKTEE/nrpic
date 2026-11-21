#!/usr/bin/env python3
"""P1 (run F-20261119-150017-b45ec5f) after the members' merger, to its end at t = 280 M:
the remnant's orbit about the heavy hole, the recoil at the merger, the constraint history,
the horizon masses and spins, and the radiated energy at the four spheres.

Readers: package p1's p1lib (trackers joined across segments, horizon rows with hrms < 1e-3,
history) and nr_first/scripts/nrread.py (r psi4, radiated energy), both unchanged and read
only. Bodies: comp0 = m1, comp1 = m2, comp2 = M. Predictions: khsr_note/JOURNAL.md entry P.

Usage: p1_280.py [--out=<dir>] [--rundir=<dir>]   (default out: $NRPIC_RUN_DIR)
Writes p1_280.json and fig_p1_280.{png,pdf}.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "tracks", "F-hills", "p1", "scripts"))
sys.path.insert(0, HERE)
import p1lib  # noqa: E402
import figstyle as fs  # noqa: E402

nr = p1lib.nr
T_MERGE = 48.8125          # first common horizon (p1 analysis, p1_checks.json)


def linfit(t, y, t_eval):
    c = np.polyfit(t, y, 1)
    return np.polyval(c, t_eval)


def window_stats(t, y, t0, t1):
    s = (t >= t0) & (t <= t1)
    if not s.any():
        return None
    return dict(n=int(s.sum()), median=float(np.median(y[s])), min=float(y[s].min()),
                max=float(y[s].max()))


def main():
    out = p1lib.out_dir(sys.argv)
    rd = p1lib.rundir(sys.argv)
    res = {"rundir": rd}
    # ------------------------------------------------------------------ trackers
    t, X, V = p1lib.tracker_common(rd)
    r12 = np.linalg.norm(X[:, 1] - X[:, 0], axis=1)
    rem = X[:, 0]                       # after the merger both member trackers coincide
    d = np.linalg.norm(rem - X[:, 2], axis=1)          # m1 (remnant) to M
    late = t > 100.0
    i_min = np.argmin(np.where(late, d, np.inf))
    ddt = np.gradient(d, t)
    mins = [(float(t[k]), float(d[k])) for k in range(1, len(d) - 1)
            if t[k] > 60 and d[k] < d[k - 1] and d[k] <= d[k + 1]]
    res["trackers"] = dict(t_end=float(t[-1]), rows=int(len(t)),
                           max_dt=float(np.diff(t).max()), median_dt=float(np.median(np.diff(t))),
                           finite=bool(np.isfinite(X).all() and np.isfinite(V).all()),
                           r12_max_after_merger=float(r12[t > 50].max()))
    res["remnant_orbit"] = dict(
        t_closest=float(t[i_min]), d_closest=float(d[i_min]), local_minima_after_60=mins[:20],
        d_at_112=float(np.interp(112.38, t, d)), d_end=float(d[-1]), ddt_end=float(ddt[-1]),
        d_at=[(tt, float(np.interp(tt, t, d))) for tt in (120, 140, 160, 200, 240, 280)],
        heavy_hole_end=X[-1, 2].tolist(), remnant_end=X[-1, 0].tolist())
    # Newtonian two-body energy of remnant and M from coordinate positions and tracker
    # velocities (gauge-dependent: coordinate speeds of boosted members were 0.5-0.76 of the
    # boost speed in E3), with horizon masses filled in below
    # ------------------------------------------------------------------ horizons
    hz = p1lib.horizons_good(rd)
    H = {}
    for n, h in hz.items():
        chi = h["S"] / h["mass"] ** 2
        H[n] = dict(found=h["found"], missed=h["missed"], good=h["good"])
        for (a, b) in ((50, 60), (60, 100), (100, 140), (140, 200), (200, 240), (240, 280)):
            H[n][f"mass_{a}_{b}"] = window_stats(h["t"], h["mass"], a, b)
            H[n][f"chi_{a}_{b}"] = window_stats(h["t"], chi, a, b)
        H[n]["mass_max_after_50"] = float(h["mass"][h["t"] > 50].max()) if (h["t"] > 50).any() else None
        H[n]["mass_first_good"] = float(h["mass"][0])
        H[n]["t_first_good"] = float(h["t"][0])
        H[n]["mass_last_good"] = float(h["mass"][-1])
        H[n]["t_last_good"] = float(h["t"][-1])
        H[n]["chi_last_good"] = float(chi[-1])
    res["horizons"] = H
    mrem = H[0]["mass_240_280"]["median"] if H[0]["mass_240_280"] else 0.268
    mM = H[2]["mass_240_280"]["median"] if H[2]["mass_240_280"] else 1.0
    # drift of the remnant mass over 60-280 (medians of the first and last windows)
    for n in (0, 1):
        a, b = H[n]["mass_60_100"], H[n]["mass_240_280"]
        if a and b:
            H[n]["drift_60_100_to_240_280"] = b["median"] / a["median"] - 1
    a, b = H[2]["mass_first_good"], H[2]["mass_240_280"]
    if b:
        H[2]["growth_first_to_240_280"] = b["median"] / a - 1
    mu = mrem * mM / (mrem + mM)
    vrel = V[:, 0] - V[:, 2]
    E2b = mu * 0.5 * np.sum(vrel ** 2, axis=1) - mrem * mM / d
    res["remnant_orbit"]["newtonian_energy_coordinate"] = dict(
        masses=[mrem, mM], at=[(tt, float(np.interp(tt, t, E2b))) for tt in (60, 100, 112, 160, 200, 240, 280)],
        note="coordinate velocities, gauge-dependent [JUDGEMENT]")
    # ------------------------------------------------------------------ recoil
    pre = (t >= 36) & (t <= 46)
    post = (t >= 52) & (t <= 60)
    te = 56.0
    vcm_pre = np.array([linfit(t[pre], 0.5 * (V[pre, 0, c] + V[pre, 1, c]), te) for c in range(3)])
    vrem_post = np.array([linfit(t[post], V[post, 0, c], te) for c in range(3)])
    dv = vrem_post - vcm_pre
    ang = np.degrees(np.arccos(np.clip(np.dot(vcm_pre, vrem_post) /
                                       (np.linalg.norm(vcm_pre) * np.linalg.norm(vrem_post)), -1, 1)))
    # the heavy hole over the same windows (its coordinate velocity changes slowly)
    vM_pre = np.array([linfit(t[pre], V[pre, 2, c], te) for c in range(3)])
    vM_post = np.array([linfit(t[post], V[post, 2, c], te) for c in range(3)])
    res["recoil"] = dict(t_eval=te, windows=[[36, 46], [52, 60]], v_cm_pre_extrap=vcm_pre.tolist(),
                         v_remnant_post=vrem_post.tolist(), dv=dv.tolist(),
                         dv_norm=float(np.linalg.norm(dv)), angle_deg=float(ang),
                         speed_pre=float(np.linalg.norm(vcm_pre)),
                         speed_post=float(np.linalg.norm(vrem_post)),
                         heavy_dv_same_windows=float(np.linalg.norm(vM_post - vM_pre)))
    # ------------------------------------------------------------------ history
    h = p1lib.history(rd)
    th = h["time"]
    nrm = {k: np.sqrt(h[k + "2"]) for k in ("H", "M", "C", "Z")}
    i112 = np.argmin(np.abs(th - 112.0))
    hist = {}
    for k, y in nrm.items():
        s = th >= 112.0
        hist[k] = dict(t0=float(y[0]), at_112=float(y[i112]), end=float(y[-1]),
                       max_all=float(y.max()), t_max_all=float(th[np.argmax(y)]),
                       max_112_280=float(y[s].max()), t_max_112_280=float(th[s][np.argmax(y[s])]),
                       min_112_280=float(y[s].min()),
                       ratio_max_to_112=float(y[s].max() / y[i112]),
                       at=[(tt, float(np.interp(tt, th, y))) for tt in (40, 48, 50, 60, 112, 120, 160, 200, 240, 280)])
    res["history"] = dict(rows=int(len(th)), t1=float(th[-1]),
                          finite=bool(all(np.isfinite(v).all() for v in h.values())),
                          volume_rel_change_max=float(np.max(np.abs(h["Volume"] / h["Volume"][0] - 1))),
                          norms=hist)
    # ------------------------------------------------------------------ radiation
    rad = {}
    curves = {}
    for R in (40, 48, 70, 90):
        tw, modes = nr.read_rpsi4(rd, R)
        E, rate, _ = nr.radiated_energy(tw, modes)
        curves[R] = (tw, E)
        rad[str(R)] = dict(t_end=float(tw[-1]), E_end=float(E[-1]),
                           E_at_112=float(np.interp(112.25, tw, E)),
                           E_at=[(tt, float(np.interp(tt, tw, E))) for tt in (50, 100, 150, 200, 250)],
                           finite=bool(np.isfinite(E).all()))
    res["radiation"] = rad
    with open(os.path.join(out, "p1_280.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    # ------------------------------------------------------------------ figure
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(3, 2, figsize=(fs.FULL_WIDTH, 8.4))
    plt.subplots_adjust(left=0.09, right=0.91, bottom=0.06, top=0.98, wspace=0.52, hspace=0.32)
    ax = axs[0, 0]
    ax.plot(t, d, color=fs.PAL["red"], label="member 1 (remnant) to M")
    ax.plot(t, np.linalg.norm(X[:, 1] - X[:, 2], axis=1), color=fs.PAL["yellow"], ls="--",
            label="member 2 to M")
    ax.plot(t, r12, color=fs.PAL["blue"], label="member separation")
    ax.axvline(T_MERGE, **fs.MASK_LINE) if hasattr(fs, "MASK_LINE") else ax.axvline(T_MERGE, color="grey", alpha=0.4)
    ax.plot([t[i_min]], [d[i_min]], "o", color="k", ms=4)
    ax.set_xlabel("t [M]", labelpad=-2)
    ax.set_ylabel("coordinate distance [M]")
    ax.set_ylim(0, 45)
    ax.legend(loc="upper left", fontsize=8)
    ax = axs[0, 1]
    win = (t > 30) & (t < 70)
    for c, lab in ((0, "x"), (1, "y")):
        ax.plot(t[win], V[win, 0, c], color=fs.SERIES[c], label=f"$v^{lab}$ member 1")
        ax.plot(t[win], V[win, 1, c], color=fs.SERIES[c], ls=":", label=f"$v^{lab}$ member 2")
        ax.plot([te], [vcm_pre[c]], "s", color=fs.SERIES[c], ms=4, mfc="none")
        ax.plot([te], [vrem_post[c]], "o", color=fs.SERIES[c], ms=3)
    ax.axvline(T_MERGE, color="grey", alpha=0.4)
    ax.set_xlabel("t [M]", labelpad=-2)
    ax.set_ylabel("tracker velocity [c]")
    ax.set_ylim(-0.6, 0.6)
    ax.legend(loc="lower left", ncol=2, fontsize=8)
    ax = axs[1, 0]
    for n, col, lab in ((0, fs.PAL["red"], "finder 0"), (1, fs.PAL["yellow"], "finder 1")):
        hh = hz[n]
        ax.plot(hh["t"], hh["mass"], ".", ms=1.5, color=col, label=lab)
    ax.set_xlabel("t [M]", labelpad=-2)
    ax.set_ylabel("horizon mass (dots)")
    ax.set_ylim(0.12, 0.29)
    ax2 = ax.twinx()
    for n, col in ((0, fs.PAL["red"]), (1, fs.PAL["yellow"])):
        hh = hz[n]
        s = hh["t"] > T_MERGE
        ax2.plot(hh["t"][s], hh["S"][s] / hh["mass"][s] ** 2, "x", ms=1.5, color=col, alpha=0.6)
    ax2.set_ylim(0, 1.0)
    ax2.set_ylabel(r"remnant $|S|/m^2$ (crosses)", labelpad=2)
    ax.legend(loc="center right", fontsize=8)
    ax = axs[1, 1]
    hh = hz[2]
    ax.plot(hh["t"], hh["mass"], ".", ms=1.5, color=fs.PAL["blue"], label="heavy-hole mass")
    ax.set_xlabel("t [M]", labelpad=-2)
    ax.set_ylabel("heavy-hole mass (dots)")
    ax2 = ax.twinx()
    ax2.plot(hh["t"], hh["S"] / hh["mass"] ** 2, "x", ms=1.5, color=fs.PAL["green"], alpha=0.6)
    ax2.set_ylabel(r"heavy hole $|S|/M^2$ (crosses)", labelpad=2)
    ax.legend(loc="lower right", fontsize=8)
    ax = axs[2, 0]
    for k, col in (("H", fs.PAL["red"]), ("M", fs.PAL["blue"]), ("Z", fs.PAL["green"])):
        ax.semilogy(th, nrm[k], color=col, label=f"{k} norm")
    ax.axvline(T_MERGE, color="grey", alpha=0.4)
    ax.axvline(t[i_min], color="grey", alpha=0.4, ls=":")
    ax.set_xlabel("t [M]", labelpad=-2)
    ax.set_ylabel("constraint norm (volume rms)")
    ax.set_ylim(1e-7, 3e-3)
    ax.legend(loc="lower right", ncol=3, fontsize=8)
    ax = axs[2, 1]
    for R, col in zip((40, 48, 70, 90), fs.SERIES):
        tw, E = curves[R]
        ax.semilogy(tw[E > 0], E[E > 0], color=col, label=f"R = {R} M")
    ax.set_xlabel("t [M]", labelpad=-2)
    ax.set_ylabel(r"radiated energy $E(t)$ [M]")
    ax.set_ylim(1e-8, 1e-2)
    ax.legend(loc="lower right", ncol=2, fontsize=8)
    fs.save(fig, os.path.join(out, "fig_p1_280"))
    print(json.dumps({k: res[k] for k in ("remnant_orbit", "recoil")}, indent=1))


if __name__ == "__main__":
    main()
