#!/usr/bin/env python3
"""Reader of the passage P1b (lead, batch 11): member distances and energies of the joined runs
A (+ A2, m/16) and C (+ C2, m/12) against the full Newtonian three-body problem from the same
deck. Written for the session that reads A2 and C2; tested on A to 61.8 M and C to 22 M.

Bodies: comp0 = m1, comp1 = m2, comp2 = M (P1's order). Masses: horizon masses, the median of each
finder over 3-10 M (the members' horizon masses sit 1.5 percent above B's in M's conformal
factor, RISKS R21). Velocities: the trackers' v = -beta (tracker_mode = ode); they are gauge
velocities, biased low while the shift settles (RISKS R6: about 0.76 of P/M for eta m = 0.25), so
the NR energies are coordinate quantities, not invariants [JUDGEMENT].
Energies (nrread.member_energies): E_i_M two-body with M, E_i_bc against the barycentre of M and
the other member, E_bin of the pair, in units of baselines_p1.json (unit_E = (m1 m2 / a_b)
(M / m_b)^(1/3), 4.96e-3 M).
Outcome at the last time: a member is called ejected when its E_i_M > 0 and its distance to M
grows over the last 10 M; bound when E_i_M < 0 [JUDGEMENT: provisional until the energies are
flat in time].
Output (--out): b11_passage.json, fig_b11_passage.png/.pdf.
"""
import argparse
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "tracks/F-hills/stage/G0/checks"))
sys.path.insert(0, os.path.join(WT, "tracks/F-hills/nr_first/scripts"))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(WT, "python"))
import lead_checks as lc  # noqa: E402
import nrread as nr  # noqa: E402
import b11_cards as bc  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

DECK = os.path.join(WT, "tracks/F-hills/binary_conv/inputs/p1b_R16n.athinput")
BASE = os.path.join(WT, "tracks/F-hills/nr_first/results/baselines_p1.json")
DT = 0.25


def nr_state(name):
    tr = bc.trackers(name)
    t, X, V = nr.common_times(tr, keys=[0, 1, 2], dt=DT)
    hz = bc.horizons(name)
    ms = []
    for n in (0, 1, 2):
        d, _ = hz[n]
        k = (d["t"] >= 3) & (d["t"] <= 10)
        ms.append(float(np.median(d["mass"][k])) if k.any() else float(np.median(d["mass"])))
    return t, X, V, np.array(ms)


def summary(t, E, unit, label):
    out = {"t_end": float(t[-1])}
    for key in ("E_0_M", "E_1_M", "E_0_bc", "E_1_bc", "E_bin"):
        out[key + "_at"] = {f"{T:g}": float(np.interp(T, t, E[key]) / unit)
                            for T in (10, 20, 40, 60, 80, 100, 120, 150, 180, 200) if t[0] <= T <= t[-1]}
        out[key + "_end"] = float(E[key][-1] / unit)
    for key in ("r_0M", "r_1M", "r_12"):
        out[key + "_min"] = float(E[key].min())
        out[key + "_t_min"] = float(t[np.argmin(E[key])])
        out[key + "_end"] = float(E[key][-1])
    k = t >= t[-1] - 10
    fate = {}
    for i in (0, 1):
        grow = np.polyfit(t[k], E[f"r_{i}M"][k], 1)[0] if k.sum() > 3 else float("nan")
        e = E[f"E_{i}_M"][-1]
        fate[f"m{i + 1}"] = ("ejected" if (e > 0 and grow > 0) else "bound" if e < 0 else "undecided")
    out["fate_at_end"] = fate
    out["label"] = label
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    o = ap.parse_args()
    os.makedirs(o.out, exist_ok=True)
    base = json.load(open(BASE))
    unit = base["unit_E"]
    res = {"unit_E": unit, "deck": DECK}

    m, x, p = lc.read_athinput(DECK)
    tN, Y = lc.newton_full(m, x, p, t_end=200.0, nout=4001)
    XN = Y[:, :9].reshape(-1, 3, 3)
    VN = Y[:, 9:].reshape(-1, 3, 3)
    EN = nr.member_energies(XN, VN, m, iM=2)
    res["newton"] = summary(tN, EN, unit, "Newton, bare masses, deck state")

    runs = {}
    for name in ("A", "C"):
        t, X, V, ms = nr_state(name)
        E = nr.member_energies(X, V, ms, iM=2)
        runs[name] = (t, E)
        res[name] = summary(t, E, unit, f"NR {name} joined, horizon masses {ms.round(5).tolist()}")
        res[name]["masses"] = ms.tolist()
        res[name]["parts"] = bc.parts(name)
    with open(os.path.join(o.out, "b11_passage.json"), "w") as f:
        json.dump(res, f, indent=1)

    fs.use_style()
    fig, axs = plt.subplots(3, 1, figsize=(6.4, 8.0), sharex=True)
    col = {"A": fs.PAL["blue"], "C": "#7B3FA0", "N": "k"}
    for name, (t, E) in list(runs.items()) + [("N", (tN, EN))]:
        lab = {"A": "NR m/16 (A + A2)", "C": "NR m/12 (C + C2)", "N": "Newton"}[name]
        ls = "--" if name == "N" else "-"
        axs[0].plot(t, E["r_0M"], color=col[name], ls=ls, lw=1.3, label=f"{lab}: m1 to M")
        axs[0].plot(t, E["r_1M"], color=col[name], ls=ls, lw=0.8, alpha=0.6, label=f"{lab}: m2 to M")
        axs[1].plot(t, E["E_0_bc"] / unit, color=col[name], ls=ls, lw=1.3, label=f"{lab}: m1")
        axs[1].plot(t, E["E_1_bc"] / unit, color=col[name], ls=ls, lw=0.8, alpha=0.6, label=f"{lab}: m2")
        axs[2].plot(t, E["E_bin"] / unit, color=col[name], ls=ls, lw=1.3, label=lab)
    axs[0].set_ylabel(r"distance to $M$ [$M$]")
    axs[0].set_ylim(0, 40)
    axs[0].legend(fontsize=6, ncol=2)
    axs[1].axhline(0, color="0.6", lw=0.6)
    axs[1].set_ylabel(r"$E_{i}^{\rm bc}$ [unit]")
    axs[1].legend(fontsize=6, ncol=2)
    axs[2].set_ylabel(r"$E_{\rm bin}$ [unit]")
    axs[2].set_xlabel(r"$t$ [$M$]")
    axs[2].legend(fontsize=7)
    tmax = max(max(t[-1] for t, _ in runs.values()) + 5, 70)
    for ax in axs:
        ax.set_xlim(0, min(tmax, 200))
    fig.tight_layout()
    fs.save(fig, os.path.join(o.out, "fig_b11_passage"))
    print(json.dumps({k: res[k] for k in ("newton", "A", "C")}, indent=1)[:4000])


if __name__ == "__main__":
    main()
