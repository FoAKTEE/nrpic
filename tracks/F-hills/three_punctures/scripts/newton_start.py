#!/usr/bin/env python3
"""T2: Newtonian outcome and start state of the first three-black-hole configuration.

Uses the newton3 driver (tracks/F-hills/newton3/hills3/threebody.py, sibling package):
  - scatter() over the binary phase from r0 = 4 r_t and from 10 r_t (k0 of 0911.1136
    prp.tex:599), same effective phase, to 30 r_t on the way out;
  - trajectory() from 10 r_t to read the binary's separation and eccentricity when its
    centre of mass passes 4 r_t (tidal distortion accumulated on the approach);
  - initial_state() at r0 = 4 r_t for the chosen phase: positions and momenta for the
    problem generator.
Writes newton_start.json and figures into the output directory (last argument) and
copies the figures into tracks/F-hills/three_punctures/figures/.

Usage: python3 newton_start.py [--choose CONFIG PHASE_DEG] <outdir>
Without --choose the phase is the centre of the longest window of clean single
ejections (fid, else wide); with it, the given configuration and phase are used.
"""
import json
import os
import shutil
import sys

import numpy as np

WT = "/data/haiyangw/nrpic/wt/F-hills"
sys.path.insert(0, os.path.join(WT, "tracks/F-hills/newton3"))
sys.path.insert(0, os.path.join(WT, "python"))
from hills3.threebody import (HillsSetup, initial_state, scatter, trajectory,  # noqa: E402
                              OUTCOME_NAMES, _pair_energy)
from nrpic import figstyle as fs  # noqa: E402

ARGS = sys.argv[1:]
CHOOSE = None
ONLY = None
while ARGS and ARGS[0].startswith("--"):
    if ARGS[0] == "--choose":          # --choose NAME PHASE_DEG | --choose NAME auto
        CHOOSE = (ARGS[1], None if ARGS[2] == "auto" else float(ARGS[2]))
        ARGS = ARGS[3:]
    elif ARGS[0] == "--only":          # --only NAME[,NAME...]: scan only these
        ONLY = ARGS[1].split(",")
        ARGS = ARGS[2:]
    else:
        raise SystemExit(f"unknown option {ARGS[0]}")
OUT = ARGS[0]
FIG = os.path.join(WT, "tracks/F-hills/three_punctures/figures")
NPH = 360
PHASES = np.linspace(0.0, 2 * np.pi, NPH, endpoint=False)
R_MB = 4.0      # marginally bound radius of Schwarzschild (areal), proxy for a plunge

CONFIGS = {
    "fid": dict(M=1.0, m1=0.05, m2=0.05, a=3.0, rp=6.0),     # D = 0.93
    "wide": dict(M=1.0, m1=0.05, m2=0.05, a=4.0, rp=8.0),    # D = 0.93
    "far": dict(M=1.0, m1=0.05, m2=0.05, a=3.0, rp=8.0),     # D = 1.24
    # q = 4, a_b = 20 m_b, the same D = 8 / 6.4633 = 1.2378 as "far"
    "q4": dict(M=1.0, m1=0.125, m2=0.125, a=5.0, rp=1.2378 * 5.0 * 4.0 ** (1.0 / 3.0)),
}
SEL = [k for k in CONFIGS if (ONLY is None and k != "q4") or (ONLY is not None and k in ONLY)]


def scan(cfg, k0):
    setups = [HillsSetup(**cfg, phase=ph) for ph in PHASES]
    r = scatter(setups, k0=k0, k_end=30.0)
    return r


def longest_window(good):
    """Longest circular run of True; returns (start index, length)."""
    n = good.size
    if good.all():
        return 0, n
    best = (0, 0)
    g2 = np.concatenate([good, good])
    i = 0
    while i < n:
        if g2[i] and (i == 0 and not g2[n - 1] or i > 0 and not g2[i - 1]):
            j = i
            while j < i + n and g2[j]:
                j += 1
            if j - i > best[1]:
                best = (i, j - i)
            i = j
        else:
            i += 1
    if good[0] and good[-1] and best[1] == 0:
        best = (0, int(good.sum()))
    return best


def state_at_radius(cfg, phase, k_from, r_read, n_out=20000):
    """Integrate from k_from r_t and return the state when the binary's centre of mass is
    at r_read from M on the way in, plus the binary's a and e there."""
    s = HillsSetup(**cfg, phase=phase)
    tt, X, V, _ = trajectory(s, k0=k_from, n_out=n_out)
    m = np.array([s.M, s.m1, s.m2])
    xc = (m[1] * X[:, 1] + m[2] * X[:, 2]) / (m[1] + m[2])
    R = np.linalg.norm(xc - X[:, 0], axis=1)
    i = int(np.argmax(R < r_read))          # first sample inside r_read
    w = (R[i - 1] - r_read) / (R[i - 1] - R[i])
    x = X[i - 1] + w * (X[i] - X[i - 1])
    v = V[i - 1] + w * (V[i] - V[i - 1])
    t = tt[i - 1] + w * (tt[i] - tt[i - 1])
    E12, a12, e12, r12 = _pair_energy(x[None], v[None], s.m1, s.m2, s.G, 1, 2)
    return dict(t=float(t), x=x, v=v, a12=float(a12[0]), e12=float(e12[0]),
                r12=float(r12[0]))


def main():
    os.makedirs(OUT, exist_ok=True)
    res = {"phases": PHASES.tolist(), "configs": {}}
    scans = {}
    for name in SEL:
        cfg = CONFIGS[name]
        s0 = HillsSetup(**cfg)
        r4 = scan(cfg, 4.0)
        r10 = scan(cfg, 10.0)
        scans[name] = (r4, r10)
        dis4 = np.isin(r4["outcome"], [1, 2, 3, 4])
        dis10 = np.isin(r10["outcome"], [1, 2, 3, 4])
        rmin4 = r4["rMmin"].min(axis=1)
        rmin10 = r10["rMmin"].min(axis=1)
        same = r4["outcome"] == r10["outcome"]
        dE = np.abs(r4["dE"] - r10["dE"])
        single = np.isin(r4["outcome"], [1, 2]) & np.isin(r10["outcome"], [1, 2])
        good = single & (rmin4 > 4.5) & (rmin10 > 4.5) & same
        i0, ln = longest_window(good)
        res["configs"][name] = dict(
            params=cfg, r_t=s0.r_t, D=s0.penetration, energy_unit=s0.energy_unit,
            disrupted_fraction_r4=float(dis4.mean()), disrupted_fraction_r10=float(dis10.mean()),
            outcome_counts_r4={OUTCOME_NAMES[k]: int((r4["outcome"] == k).sum()) for k in range(6)},
            outcome_counts_r10={OUTCOME_NAMES[k]: int((r10["outcome"] == k).sum()) for k in range(6)},
            frac_rmin_below_4_r4=float((rmin4 < R_MB).mean()),
            frac_rmin_below_4_r10=float((rmin10 < R_MB).mean()),
            frac_rmin_below_4p5_r4=float((rmin4 < 4.5).mean()),
            min_rmin_r4=float(rmin4.min()), min_rmin_r10=float(rmin10.min()),
            same_outcome_fraction=float(same.mean()),
            median_abs_dE_diff=float(np.median(dE)),
            energy_error_max=float(np.max(np.abs(np.concatenate([r4["energy_error"], r10["energy_error"]])))),
            good_window=dict(start_index=int(i0), length=int(ln),
                             phase_start=float(PHASES[i0]), n_good=int(good.sum())),
            E1_r4=r4["E1"].tolist(), E2_r4=r4["E2"].tolist(), E1_r10=r10["E1"].tolist(),
            E2_r10=r10["E2"].tolist(), outcome_r4=r4["outcome"].tolist(),
            outcome_r10=r10["outcome"].tolist(), rmin4=r4["rMmin"].tolist(),
            rmin10=r10["rMmin"].tolist(),
        )
        print(f"{name}: r_t={s0.r_t:.3f} D={s0.penetration:.3f} disrupted r4 {dis4.mean():.3f} "
              f"r10 {dis10.mean():.3f}; rmin<4: r4 {(rmin4 < R_MB).mean():.3f} r10 "
              f"{(rmin10 < R_MB).mean():.3f}; same outcome {same.mean():.3f}; good window "
              f"{ln} phases from {np.degrees(PHASES[i0]):.0f} deg; good total {good.sum()}")

    # tidal distortion on the approach: 36 phases, integrate from 10 r_t, read at 4 r_t
    distort = {}
    for name in [k for k in ("fid", "wide", "q4") if k in SEL]:
        cfg = CONFIGS[name]
        rt = HillsSetup(**cfg).r_t
        aa, ee = [], []
        for ph in PHASES[::10]:
            st = state_at_radius(cfg, ph, 10.0, 4.0 * rt, n_out=8000)
            aa.append(st["a12"] / cfg["a"])
            ee.append(st["e12"])
        distort[name] = dict(a_over_a0=aa, e=ee, max_da=float(np.max(np.abs(np.array(aa) - 1))),
                             max_e=float(np.max(ee)))
        print(f"{name}: at 4 r_t from 10 r_t: max |a/a0-1| = {distort[name]['max_da']:.4f}, "
              f"max e = {distort[name]['max_e']:.4f}")
    res["distortion_at_4rt"] = distort

    # chosen phase for run 1: centre of the longest good window of the fiducial, else wide
    choice = None
    if CHOOSE is not None and CHOOSE[1] is not None:
        choice = (CHOOSE[0], int(round(CHOOSE[1] / 360.0 * NPH)) % NPH)
    elif CHOOSE is not None:
        g = res["configs"][CHOOSE[0]]["good_window"]
        choice = (CHOOSE[0], (g["start_index"] + g["length"] // 2) % NPH)
    for name in (() if choice is not None else ("fid", "wide")):
        g = res["configs"][name]["good_window"]
        if g["length"] >= 10:
            ic = (g["start_index"] + g["length"] // 2) % NPH
            choice = (name, ic)
            break
    res["choice"] = None
    if choice is not None:
        name, ic = choice
        cfg = CONFIGS[name]
        ph = float(PHASES[ic])
        s = HillsSetup(**cfg, phase=ph)
        st = initial_state(s, r0=4.0 * s.r_t)
        st10 = state_at_radius(cfg, ph, 10.0, 4.0 * s.r_t, n_out=20000)
        r4, r10 = scans[name]
        m = st["masses"]
        res["choice"] = dict(
            config=name, phase=ph, phase_deg=float(np.degrees(ph)), index=ic,
            outcome_r4=OUTCOME_NAMES[int(r4["outcome"][ic])],
            outcome_r10=OUTCOME_NAMES[int(r10["outcome"][ic])],
            E1_r4=float(r4["E1"][ic]), E2_r4=float(r4["E2"][ic]),
            E1_r10=float(r10["E1"][ic]), E2_r10=float(r10["E2"][ic]),
            rmin_r4=r4["rMmin"][ic].tolist(), rmin_r10=r10["rMmin"][ic].tolist(),
            t_to_pericentre=st["t_to_pericentre"], r0=st["r0"], r_t=st["r_t"], r_p=st["r_p"],
            positions=st["positions"].tolist(), momenta=st["momenta"].tolist(),
            velocities=st["velocities"].tolist(), masses=m.tolist(),
            from10=dict(t=st10["t"], positions=st10["x"].tolist(),
                        momenta=(m[:, None] * st10["v"]).tolist(), a12=st10["a12"],
                        e12=st10["e12"]),
        )
        print("choice:", name, f"phase {np.degrees(ph):.1f} deg", res["choice"]["outcome_r4"],
              res["choice"]["outcome_r10"], "E1,E2 (r4)", res["choice"]["E1_r4"],
              res["choice"]["E2_r4"])
        # Newtonian positions along the passage (start 10 r_t), every 2 M from the time the
        # centre of mass passes 4 r_t to 170 M after the pericentre: for the mesh counts
        t4 = st10["t"]
        tt, X, V, _ = trajectory(s, k0=10.0, t_end=170.0, n_out=40000)
        ts = np.arange(t4, 170.0 + 1e-9, 2.0)
        Xs = np.stack([np.stack([np.interp(ts, tt, X[:, k, a]) for a in range(3)], axis=1)
                       for k in range(3)], axis=1)
        res["choice"]["track"] = dict(t=ts.tolist(), x=Xs.tolist(),
                                      note="t relative to the unperturbed pericentre time; "
                                           "start 10 r_t; bodies [M, m1, m2]")
        P = st["momenta"]
        print("|P| =", np.linalg.norm(P, axis=1), "sum P =", P.sum(axis=0))
        for k, nm in enumerate(["heavy", "m1", "m2"]):
            print(f"  {nm}: x = {st['positions'][k]}, P = {P[k]}")

    with open(os.path.join(OUT, "newton_start.json"), "w") as f:
        json.dump(res, f, indent=1)

    # ---- figures ----
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(3, len(SEL), figsize=(fs.FULL_WIDTH, 6.6), sharex=True,
                             squeeze=False)
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.08, top=0.95, hspace=0.08, wspace=0.28)
    deg = np.degrees(PHASES)
    for j, name in enumerate(SEL):
        c = res["configs"][name]
        r4, r10 = scans[name]
        ax = axes[0, j]
        ax.plot(deg, r10["E1"], color=fs.PAL["blue"], lw=1.0, label=r"$E_1$, start $10\,r_t$")
        ax.plot(deg, r4["E1"], color=fs.PAL["red"], lw=1.0, ls="--", label=r"$E_1$, start $4\,r_t$")
        ax.axhline(0, **fs.MASK_LINE)
        ax.set_title(f"a_b = {c['params']['a']:g} M, r_p = {c['params']['rp']:g} M "
                     f"(D = {c['D']:.2f})", fontsize=10)
        ax.set_ylim(-3.2, 4.8)
        if j == 0:
            ax.set_ylabel(r"$E_1$ [unit]")
            ax.legend(loc="lower left", fontsize=8)
        ax = axes[1, j]
        ax.plot(deg, r10["outcome"], ".", ms=2, color=fs.PAL["blue"])
        ax.plot(deg, np.array(r4["outcome"]) + 0.15, ".", ms=2, color=fs.PAL["red"])
        ax.set_yticks(range(6))
        ax.set_yticklabels(["surv", "m2 ej", "m1 ej", "both b", "both f", "unset"], fontsize=7)
        ax.minorticks_off()
        g = c["good_window"]
        if g["length"] > 0:
            a0 = deg[g["start_index"]]
            ax.axvspan(a0, a0 + g["length"], color=fs.PAL["green"], alpha=0.12)
        ax = axes[2, j]
        ax.plot(deg, np.min(r10["rMmin"], axis=1), color=fs.PAL["blue"], lw=1.0)
        ax.plot(deg, np.min(r4["rMmin"], axis=1), color=fs.PAL["red"], lw=1.0, ls="--")
        ax.axhline(R_MB, **fs.GUIDE)
        ax.set_ylim(0, 10)
        ax.set_xlabel("binary phase [deg]", labelpad=-1)
        if j == 0:
            ax.set_ylabel(r"min member distance to $M$")
    for ax in axes.ravel():
        ax.set_xlim(0, 360)
    tag = "" if ONLY is None else "_" + "_".join(SEL)
    p1 = fs.save(fig, os.path.join(OUT, "fig_newton_phase" + tag))
    plt.close(fig)

    if res["choice"] is not None:
        ch = res["choice"]
        cfg = CONFIGS[ch["config"]]
        s = HillsSetup(**cfg, phase=ch["phase"])
        tt, X, V, _ = trajectory(s, k0=10.0, k_end=30.0, n_out=6000)
        t4 = -ch["t_to_pericentre"]
        fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.9))
        ax = fig.add_axes([0.08, 0.12, 0.42, 0.82])
        cols = [fs.PAL["blue"], fs.PAL["red"], fs.PAL["yellow"]]
        lab = ["M", "m1", "m2"]
        for k in range(3):
            ax.plot(X[:, k, 0], X[:, k, 1], color=cols[k], lw=1.2, label=lab[k])
            i4 = int(np.argmin(np.abs(tt - t4)))
            ax.plot(X[i4, k, 0], X[i4, k, 1], "o", color=cols[k], ms=4)
        th = np.linspace(0, 2 * np.pi, 200)
        ax.plot(R_MB * np.cos(th), R_MB * np.sin(th), **fs.GUIDE, label="r = 4 M (about origin)")
        ax.set_aspect("equal")
        ax.set_xlim(-40, 40)
        ax.set_ylim(-40, 40)
        ax.set_xlabel("x [M]")
        ax.set_ylabel("y [M]")
        ax.legend(loc="upper left", fontsize=8)
        ax2 = fig.add_axes([0.60, 0.12, 0.38, 0.82])
        m = np.array([s.M, s.m1, s.m2])
        for k, (i, j) in enumerate(((0, 1), (0, 2), (1, 2))):
            d = np.linalg.norm(X[:, j] - X[:, i], axis=1)
            ax2.plot(tt, d, color=fs.SERIES[k], label=f"|{lab[j]} - {lab[i]}|")
        ax2.axvline(t4, **fs.MASK_LINE)
        ax2.axhline(R_MB, **fs.GUIDE)
        ax2.set_yscale("log")
        ax2.set_xlabel("t - t_peri [M]")
        ax2.set_ylabel("separation [M]")
        ax2.legend(loc="lower right", fontsize=8)
        p2 = fs.save(fig, os.path.join(OUT, "fig_newton_choice" + tag))
        plt.close(fig)
        p1 += p2
    for p in p1:
        if p.endswith(".png"):
            shutil.copy(p, FIG)


if __name__ == "__main__":
    main()
