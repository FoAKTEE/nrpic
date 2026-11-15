#!/usr/bin/env python3
"""Analysis of a Hills passage run (P1) with the readers of nrread.py (package nr_first).

Reads from <rundir>: the three trackers (segments kept by athena_keep_trackers.sh merged),
the horizon summaries, the history and the r psi4 modes if present. Bodies: comp0 = m1,
comp1 = m2, comp2 = M (the order of the P1 input). Masses: the bare masses given with
--masses=m1,m2,M (default 0.125,0.125,1), or the median horizon masses with --horizon-masses.
Velocities: the trackers' own v (= -beta at the tracker); --f=<factor> divides them by a
gauge factor (E3's speed ratio) as a crude correction.
Outputs (<out>): p1_analysis.json and fig_p1_analysis.{png,pdf}:
  distances of the members from the heavy hole and from each other, with the baselines of
  baselines_p1.json overlaid (--baselines=<json>), member energies in units
  (m1 m2 / a_b)(M / m_b)^(1/3) with a_b = 5 (two-body with M; against the barycentre of M and
  the other member), horizon masses, constraint norm and radiated energy.
Usage: p1_analysis.py <rundir> [--out=<dir>] [--baselines=<json>] [--masses=a,b,c]
                      [--horizon-masses] [--f=<factor>] [--a0=5.0]
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(WT, "python"))
import nrread as nr  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402


def opts(argv):
    o = {"rundir": argv[1], "out": os.environ.get("NRPIC_RUN_DIR"), "baselines": None,
         "masses": [0.125, 0.125, 1.0], "horizon_masses": False, "f": 1.0, "a0": 5.0}
    for a in argv[2:]:
        k, _, v = a.lstrip("-").partition("=")
        if k == "out":
            o["out"] = v
        elif k == "baselines":
            o["baselines"] = v
        elif k == "masses":
            o["masses"] = [float(x) for x in v.split(",")]
        elif k == "horizon-masses":
            o["horizon_masses"] = True
        elif k == "f":
            o["f"] = float(v)
        elif k == "a0":
            o["a0"] = float(v)
    if not o["out"]:
        o["out"] = o["rundir"]
    return o


def main():
    o = opts(sys.argv)
    rd, out = o["rundir"], o["out"]
    os.makedirs(out, exist_ok=True)
    trk = nr.read_trackers(rd)
    hz = nr.read_horizons(rd)
    hst_files = [f for f in os.listdir(rd) if f.endswith(".z4c.user.hst")]
    hst = nr.read_hst(os.path.join(rd, hst_files[0])) if hst_files else None
    t, X, V = nr.common_times(trk, keys=[0, 1, 2])
    V = V / o["f"]
    m = np.array(o["masses"], dtype=float)
    hmed = {}
    for n in (0, 1, 2):
        if n in hz and len(hz[n][0]["mass"]):
            hmed[n] = float(np.median(hz[n][0]["mass"]))
    if o["horizon_masses"] and len(hmed) == 3:
        m = np.array([hmed[0], hmed[1], hmed[2]])
    m1, m2, M = m
    mb = m1 + m2
    Eu = m1 * m2 / o["a0"] * (M / mb) ** (1 / 3)
    E = nr.member_energies(X, V, m, iM=2)
    # which member recedes at the end: the one farther from M and moving away
    rr = [E["r_0M"], E["r_1M"]]
    vr = [np.gradient(r, t) for r in rr]
    k_out = int(np.argmax([rr[0][-1], rr[1][-1]]))
    k_in = 1 - k_out
    res = dict(rundir=rd, masses=m.tolist(), unit_E=Eu, f=o["f"], t_end=float(t[-1]),
               rows=int(len(t)), horizon_median=hmed,
               horizon_found={n: int(len(hz[n][0]["mass"])) for n in hz},
               horizon_missed={n: int(hz[n][1]) for n in hz},
               receding=f"m{k_out + 1} (comp{k_out})" if vr[k_out][-1] > 0 else "none",
               at_end=dict(r_1M=float(rr[0][-1]), r_2M=float(rr[1][-1]),
                           r_12=float(E["r_12"][-1]),
                           E_receding_bc_u=float(E[f"E_{k_out}_bc"][-1] / Eu),
                           E_receding_M_u=float(E[f"E_{k_out}_M"][-1] / Eu),
                           E_other_M_u=float(E[f"E_{k_in}_M"][-1] / Eu)),
               min_r_1M=float(rr[0].min()), min_r_2M=float(rr[1].min()),
               heavy_displacement=float(np.linalg.norm(X[-1, 2] - X[0, 2])))
    sep = E["r_12"] > 2 * o["a0"]
    res["t_binary_wider_than_2a"] = float(t[np.argmax(sep)]) if sep.any() else None
    if hst is not None:
        res["H_t0"] = float(np.sqrt(hst["H2"][0]))
        res["H_max"] = float(np.sqrt(hst["H2"].max()))
        res["volume_ratio_end"] = float(hst["Volume"][-1] / hst["Volume"][0])
    wav = {}
    wdir = os.path.join(rd, "waveforms")
    if os.path.isdir(wdir):
        radii = sorted(int(f[-8:-4]) for f in os.listdir(wdir) if f.startswith("rpsi4_real_"))
        res["E_rad"] = {}
        for R in radii:
            tw, modes = nr.read_rpsi4(rd, R)
            Er, _, _ = nr.radiated_energy(tw, modes)
            wav[R] = (tw, Er)
            res["E_rad"][str(R)] = float(Er[-1])
    print(json.dumps(res, indent=1, default=str))
    json.dump(res, open(os.path.join(out, "p1_analysis.json"), "w"), indent=1, default=str)

    base = json.load(open(o["baselines"])) if o["baselines"] else None
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.6))
    a = ax[0, 0]
    a.plot(t, rr[0], color=fs.PAL["blue"], lw=1.4, label=r"$m_1$ from $M$")
    a.plot(t, rr[1], color=fs.PAL["red"], lw=1.4, label=r"$m_2$ from $M$")
    a.plot(t, E["r_12"], color=fs.PAL["yellow"], lw=1.0, label=r"$|x_1-x_2|$")
    if base:
        for key, ls in (("newton", "--"), ("hrna", ":")):
            b = base[key]["at_t_run"]
            a.plot([base["t_run"]], [b["r_1M"]], marker="o" if key == "newton" else "s",
                   mfc="none", color=fs.PAL["blue"], ls="none", label=f"{key} at t = {base['t_run']:.0f}")
            a.plot([base["t_run"]], [b["r_2M"]], marker="o" if key == "newton" else "s",
                   mfc="none", color=fs.PAL["red"], ls="none")
    a.axhline(4.0, **fs.MASK_LINE)
    a.set_yscale("log")
    a.set_ylabel(r"coordinate distance $[M]$")
    a.legend(frameon=False, fontsize=6.5, loc="upper left")
    a = ax[0, 1]
    for k, col in ((0, fs.PAL["blue"]), (1, fs.PAL["red"])):
        a.plot(t, E[f"E_{k}_M"] / Eu, color=col, lw=0.8, ls="--")
        a.plot(t, E[f"E_{k}_bc"] / Eu, color=col, lw=1.4)
    if base:
        a.axhline(base["newton"]["E_ejected_bc_u"], color=fs.PAL["blue"], **{k: v for k, v in fs.GUIDE.items() if k != "color"})
        a.axhline(base["hrna"]["E2_u"], color=fs.PAL["red"], ls=":", lw=1.5)
    a.set_ylim(-4, 4)
    a.set_ylabel("member energy [units]")
    a.set_title("solid: against barycentre of M + other; dashed: with M", fontsize=8)
    a = ax[1, 0]
    for n, col in ((0, fs.PAL["blue"]), (1, fs.PAL["red"]), (2, "k")):
        if n in hz and len(hz[n][0]["mass"]):
            h = hz[n][0]
            a.plot(h["t"], h["mass"] / h["mass"][0] - 1, ".", ms=2, color=col,
                   label=f"horizon {n}: {h['mass'][0]:.5f} first, {hz[n][1]} missed")
    a.set_ylabel(r"$M_{\rm AH}(t)/M_{\rm AH}(t_{\rm first})-1$")
    a.legend(frameon=False, fontsize=6.5)
    a = ax[1, 1]
    if hst is not None:
        a.semilogy(hst["time"], np.sqrt(hst["H2"]), color="k", lw=1.0, label=r"$\langle H^2\rangle^{1/2}$")
    for R, (tw, Er) in wav.items():
        a.semilogy(tw, np.maximum(Er, 1e-14), lw=1.0, label=f"$E_{{\\rm rad}}$, R = {R}")
    a.legend(frameon=False, fontsize=6.5)
    for a in ax.ravel():
        a.set_xlabel(r"$t\,[M]$")
    fig.tight_layout()
    for pth in fs.save(fig, os.path.join(out, "fig_p1_analysis")):
        print("figure:", pth)


if __name__ == "__main__":
    main()
