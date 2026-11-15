#!/usr/bin/env python3
"""Tests 2 and 3 of tracks/core/JOURNAL-mp.md: two and three Bowen-York punctures
evolved. Reads the registered runs t2_binary_approx and t3_triple_approx, prints
tracker, horizon and constraint numbers, writes multi_check.json and the figures
figs/binary_evolution and figs/triple_evolution.
"""
import json
import os
import re
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mp_common as mc  # noqa: E402
from mp_common import figstyle  # noqa: E402


def load(label, base, npunc):
    man = mc.run_by_label(label, status=None)
    d = man["output_directory"]
    out = {"man": man, "dir": d, "hst": mc.read_hst(os.path.join(d, base + ".z4c.user.hst")),
           "trk": [mc.read_tracker(os.path.join(d, f"{base}.co_{n}.txt"))
                   for n in range(npunc)], "hor": [], "missed": []}
    for n in range(npunc):
        h, miss = mc.read_horizon(os.path.join(d, f"{base}.horizon_summary_{n}.txt"))
        out["hor"].append(h)
        out["missed"].append(miss)
    log = open(os.path.join(d, "athena.log")).read()
    m = re.search(r"(\d+) MeshBlocks created, (\d+) deleted by AMR", log)
    out["amr"] = (int(m.group(1)), int(m.group(2))) if m else None
    m = re.search(r"Total number of MeshBlocks = (\d+)", log)
    out["nmb0"] = int(m.group(1)) if m else None
    m = re.search(r"zone-cycles/cpu_second = (\S+)", log)
    out["zcps"] = float(m.group(1)) if m else None
    m = re.search(r"MeshBlock-cycles = (\d+)", log)
    out["mbcycles"] = int(m.group(1)) if m else None
    return out


def horizon_summary(r, n):
    h = r["hor"][n]
    if len(h["mass"]) == 0:
        return {"found": 0, "missed": r["missed"][n]}
    return {"found": int(len(h["mass"])), "missed": r["missed"][n],
            "t_first": float(h["t"][0]), "m_first": float(h["mass"][0]),
            "m_last": float(h["mass"][-1]), "m_min": float(np.min(h["mass"])),
            "m_max": float(np.max(h["mass"])), "Sz_first": float(h["Sz"][0]),
            "Sz_last": float(h["Sz"][-1]), "S_last": float(h["S"][-1])}


def norms(r):
    h = r["hst"]
    hn = np.sqrt(h["H-norm2"] / h["Volume"])
    mn = np.sqrt(h["M-norm2"] / h["Volume"])
    return {"H0": float(hn[0]), "Hmax": float(np.max(hn)), "Hlast": float(hn[-1]),
            "t_Hmax": float(h["time"][np.argmax(hn)]), "M0": float(mn[0]),
            "Mmax": float(np.max(mn)), "Mlast": float(mn[-1]),
            "vol_rel_change": float(np.max(np.abs(h["Volume"] / h["Volume"][0] - 1.0))),
            "finite": bool(np.all(np.isfinite(hn)))}


def run_numbers(r):
    cycles = len(r["trk"][0]["t"]) - 1
    return {"run_id": r["man"]["run_id"], "status": r["man"]["status"],
            "t_end": float(r["trk"][0]["t"][-1]), "nmb_start": r["nmb0"], "amr": r["amr"],
            "nmb_mean": (r["mbcycles"] / cycles) if r["mbcycles"] and cycles else None,
            "zone_cycles_per_s": r["zcps"], "card_hours": r["man"].get("card_hours"),
            "card_memory_peak_mib": r["man"].get("card_memory_peak_mib")}


def binary(res):
    r = load("t2_binary_approx", "by2", 2)
    a, b = r["trk"]
    n = min(len(a["t"]), len(b["t"]))
    t = a["t"][:n]
    sep = a["x"][:n] - b["x"][:n]
    d = np.linalg.norm(sep, axis=1)
    ang = np.unwrap(np.arctan2(sep[:, 1], sep[:, 0]))
    cen = 0.5 * (a["x"][:n] + b["x"][:n])
    spd = [np.linalg.norm(q["v"][:n], axis=1) for q in (a, b)]
    e = run_numbers(r)
    e.update({"centre_max": float(np.max(np.linalg.norm(cen, axis=1))),
              "z_max": float(max(np.max(np.abs(a["x"][:, 2])), np.max(np.abs(b["x"][:, 2])))),
              "angle_end": float(ang[-1] - ang[0]), "sep_min": float(d.min()),
              "sep_max": float(d.max()), "sep_end": float(d[-1]),
              "speed_end": [float(s[-1]) for s in spd],
              "vy0_early": float(a["v"][min(n - 1, 64), 1]),
              "horizons": [horizon_summary(r, k) for k in range(2)], "norms": norms(r)})
    res["binary"] = e
    print("binary:", json.dumps(e, indent=1))

    fig, ax = plt.subplots(1, 3, figsize=(figstyle.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.075, right=0.985, bottom=0.17, top=0.95, wspace=0.36)
    cols = [figstyle.PAL["red"], figstyle.PAL["blue"]]
    for q, c in zip((a, b), cols):
        ax[0].plot(q["x"][:, 0], q["x"][:, 1], color=c)
        ax[0].plot(q["x"][0, 0], q["x"][0, 1], "o", color=c, ms=4)
    th = np.linspace(0, 2 * np.pi, 200)
    ax[0].plot(5 * np.cos(th), 5 * np.sin(th), **figstyle.MASK_LINE)
    ax[0].set_aspect("equal")
    ax[0].set_xlim(-6.5, 6.5)
    ax[0].set_ylim(-6.5, 6.5)
    ax[0].set_xlabel(r"$x/M$")
    ax[0].set_ylabel(r"$y/M$")
    ax[1].plot(t, spd[0], color=cols[0], label="puncture at +x")
    ax[1].plot(t, spd[1], color=cols[1], ls="--", label="puncture at -x")
    ax[1].axhline(0.0791 / 0.5, **figstyle.GUIDE)
    ax[1].text(0.5, 0.0791 / 0.5 * 1.03, r"$P/m$", fontsize=9)
    ax[1].set_xlabel(r"$t/M$")
    ax[1].set_ylabel("tracker speed")
    ax[1].legend(fontsize=8, loc="lower right")
    ax[2].plot(t, ang - ang[0], color=figstyle.PAL["red"], label="angle of the line (rad)")
    ax[2].plot(t, np.sqrt(1.0 / 10.0**3) * t, **figstyle.GUIDE)
    ax[2].plot(t, d - d[0], color=figstyle.PAL["blue"], label=r"separation $-$ 10")
    ax[2].set_xlabel(r"$t/M$")
    ax[2].legend(fontsize=8, loc="upper left")
    print("figure:", mc.savefig(fig, "binary_evolution"))


def triple(res):
    r = load("t3_triple_approx", "by3", 3)
    e = run_numbers(r)
    e["horizons"] = [horizon_summary(r, k) for k in range(3)]
    e["norms"] = norms(r)
    e["displacement"] = [[float(v) for v in (q["x"][-1] - q["x"][0])] for q in r["trk"]]
    e["speed_end"] = [float(np.linalg.norm(q["v"][-1])) for q in r["trk"]]
    a, b = r["trk"][0], r["trk"][1]
    n = min(len(a["t"]), len(b["t"]))
    sep = a["x"][:n] - b["x"][:n]
    ang = np.unwrap(np.arctan2(sep[:, 1], sep[:, 0]))
    e["binary_angle_end"] = float(ang[-1] - ang[0])
    e["binary_sep_end"] = float(np.linalg.norm(sep[-1]))
    res["triple"] = e
    print("triple:", json.dumps(e, indent=1))

    fig, ax = plt.subplots(1, 3, figsize=(figstyle.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.08, right=0.985, bottom=0.17, top=0.95, wspace=0.36)
    cols = [figstyle.PAL["red"], figstyle.PAL["blue"], figstyle.PAL["green"]]
    names = ["light A", "light B", "heavy"]
    for q, c, nm in zip(r["trk"], cols, names):
        ax[0].plot(q["x"][:, 0] - q["x"][0, 0], q["x"][:, 1] - q["x"][0, 1], color=c,
                   label=nm)
    ax[0].set_xlabel(r"$x-x_0$")
    ax[0].set_ylabel(r"$y-y_0$")
    ax[0].legend(fontsize=8, loc="upper left")
    h = r["hst"]
    ax[1].semilogy(h["time"], np.sqrt(h["H-norm2"] / h["Volume"]),
                   color=figstyle.PAL["red"], label=r"$H$")
    ax[1].semilogy(h["time"], np.sqrt(h["M-norm2"] / h["Volume"]),
                   color=figstyle.PAL["blue"], label=r"momentum")
    ax[1].set_xlabel(r"$t$ (binary mass)")
    ax[1].set_ylabel("constraint norms (history)")
    ax[1].legend(fontsize=8)
    for k, (c, nm) in enumerate(zip(cols, names)):
        hh = r["hor"][k]
        if len(hh["mass"]):
            ax[2].plot(hh["t"], hh["mass"] / hh["mass"][0], color=c, label=nm)
    ax[2].set_xlabel(r"$t$ (binary mass)")
    ax[2].set_ylabel("horizon mass / first value")
    ax[2].legend(fontsize=8)
    print("figure:", mc.savefig(fig, "triple_evolution"))


def main():
    figstyle.use_style()
    res = {}
    for name, fn in (("binary", binary), ("triple", triple)):
        try:
            fn(res)
        except (KeyError, FileNotFoundError, IndexError) as err:
            print(f"{name}: not available ({err})")
    with open(os.path.join(mc.HERE, "multi_check.json"), "w") as f:
        json.dump(res, f, indent=1)


if __name__ == "__main__":
    main()
