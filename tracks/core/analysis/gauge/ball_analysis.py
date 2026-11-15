#!/usr/bin/env python3
"""Tests L1 and L2 of the work package "gauge": the expanding ball with the old and the
new lapse against the exact solution (tracks/core/JOURNAL-gauge.md).

For every registered run with tag g-* or gc-* (ball_runs.py): areal radius of the tracked
shells against their proper time and the exact Lemaitre-Tolman-Bondi radius (the
analysis of tracks/core/analysis/id/test2_evolution.py), the lapse at the centre against
the reference of lapse_ref.py, lapse profiles, the coordinate speed of light, the
constraint norms.  Writes ball_numbers.json and figs/ball_*.png|pdf.

    ball_analysis.py [--prefix g]
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "tracks/core/analysis/id"))
sys.path.insert(0, os.path.join(WT, "python"))
sys.path.insert(0, HERE)

import idlib                                   # noqa: E402
import test2_evolution as t2                   # noqa: E402
from lapse_ref import central_lapse            # noqa: E402
from nrpic import figstyle as fs               # noqa: E402
import matplotlib.pyplot as plt                # noqa: E402

FIGS = os.path.join(HERE, "figs")
GROUPS = ("core", "mid", "outer", "surface")


def leak_time(man):
    """Relaxation time T of a run (0: plain 1+log), and whether the lapse is 1+log."""
    args = {a.split("=")[0]: a.split("=")[1] for a in man["command"] if "=" in a}
    rate = float(args.get("z4c/lapse_leak", 1.0))
    oplog = float(args.get("z4c/lapse_oplog", 2.0))
    return (1.0 / rate if rate > 0.0 else 0.0), oplog != 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefix", default="g")
    a = ap.parse_args()
    mans = idlib.manifests(a.prefix + "-")
    runs, numbers = {}, {}
    for tag, m in sorted(mans.items()):
        name = tag[len(a.prefix) + 1:]
        if not os.path.exists(os.path.join(m["output_directory"], "ball.traj.bin")):
            continue
        try:
            d = t2.load(m)
        except ValueError as err:
            print(f"SKIPPED {tag} ({m['run_id']}): {err}")
            numbers[name] = dict(run_id=m["run_id"], skipped=str(err))
            continue
        runs[name] = d
        T, oplog = leak_time(m)
        g = t2.gauge_numbers(d)
        t = np.array(g["t"])
        ref = None
        if oplog:
            rt, rtau, ra, ral = central_lapse(d["ball"], T, float(t[-1]), dt=0.01)
            ref = np.interp(t, rt, ral)
        cs = d["cstat"]
        numbers[name] = dict(
            run_id=m["run_id"], cells=d["n"], dx=d["dx"], half=d["half"], T=T,
            wall_s=m["wall_time_s"], card_hours=m["card_hours"], t_end=float(d["t"][-1]),
            groups=t2.group_numbers(d), gauge=g,
            alpha_ref=None if ref is None else ref.tolist(),
            regions=t2.region_constraints(d),
            cstat=dict(t=cs[:, 0].tolist(), H_max=cs[:, 8].tolist(), H_mean=cs[:, 9].tolist(),
                       M_max=cs[:, 12].tolist(), M_mean=cs[:, 13].tolist(),
                       Theta_max=cs[:, 7].tolist(), K_min=cs[:, 3].tolist(),
                       K_max=cs[:, 4].tolist()))
    with open(os.path.join(HERE, f"ball_numbers_{a.prefix}.json"), "w") as f:
        json.dump(numbers, f)
        f.write("\n")

    # ---- tables
    print("central lapse against the reference (plain 1+log: 1 + 6 ln a) at t = 2, 4, ...")
    for k, v in numbers.items():
        if "skipped" in v or v["alpha_ref"] is None:
            continue
        g = v["gauge"]
        t = np.array(g["t"])
        row = "%-22s T=%-4g" % (k, v["T"])
        dev = 0.0
        for tt in np.arange(2.0, v["t_end"] + 0.01, 2.0):
            i = int(np.argmin(np.abs(t - tt)))
            row += "  %.3f/%.3f" % (g["alpha_centre"][i], v["alpha_ref"][i])
        rel = np.abs(np.array(g["alpha_centre"]) / np.array(v["alpha_ref"]) - 1.0)
        sel = t <= 10.0
        row += "   max dev (t<=10) %.3f at t=%.2f   alpha_max %.3f  c_max %.3f" % (
            rel[sel].max(), t[sel][int(np.argmax(rel[sel]))], max(g["alpha_max"]),
            max(g["light_speed_max"]))
        print(row)
    print("\nlargest |eps| over the whole run by group; H mean at the end; wall time")
    print("%-22s %5s" % ("case", "dx") + "".join(" %9s" % g for g in GROUPS)
          + " %9s %9s %7s" % ("Hmean_e", "Theta_e", "wall"))
    for k, v in numbers.items():
        if "skipped" in v:
            print("%-22s skipped: %s" % (k, v["skipped"]))
            continue
        row = "%-22s %5.3f" % (k, v["dx"])
        for g in GROUPS:
            row += " %9.2e" % v["groups"][g]["maxabs_all"]
        row += " %9.2e %9.2e %7.0f" % (v["cstat"]["H_mean"][-1], v["cstat"]["Theta_max"][-1],
                                      v["wall_s"])
        print(row)
    print("\nturnaround of the bound ball (exact a_max = 1.25 at tau = 9.542 M)")
    for k, v in numbers.items():
        if "skipped" in v or not k.startswith("bound"):
            continue
        row = "%-22s" % k
        for g in GROUPS:
            t = v["groups"][g].get("turnaround")
            row += ("  %s %.4f at %.3f" % (g, t["a_max_mean"], t["tau_mean"])) if t else f"  {g} -"
        print(row)

    os.makedirs(FIGS, exist_ok=True)
    fs.use_style()
    figures(a.prefix, runs, numbers)


def figures(pre, runs, numbers):
    col = {"mp": fs.PAL["red"], "ct": fs.PAL["yellow"], "leak05": fs.PAL["green"],
           "leak025": fs.PAL["orange"], "leak0125": "k",
           "leak1": fs.PAL["blue"], "leak2": fs.PAL["purple"] if "purple" in fs.PAL else "purple",
           "leak4": "grey"}
    lab = {"mp": "1+log (old)", "ct": "conformal time", "leak05": r"new, $T=0.5\,M$",
           "leak025": r"new, $T=0.25\,M$", "leak0125": r"new, $T=0.125\,M$",
           "leak1": r"new, $T=1\,M$", "leak2": r"new, $T=2\,M$", "leak4": r"new, $T=4\,M$"}

    def lapse_of(k):
        return k.replace("bound-", "").split("-")[0]

    sets = {
        "sharp": [k for k in runs if not k.startswith("bound") and "edge" not in k],
        "edge2": [k for k in runs if "edge2" in k],
        "bound": [k for k in runs if k.startswith("bound")],
    }
    for sname, keys in sets.items():
        if not keys:
            continue
        dxs = sorted({numbers[k]["dx"] for k in keys}, reverse=True)
        for dx in dxs:
            ks = [k for k in keys if numbers[k]["dx"] == dx]
            fig, ax = plt.subplots(2, 3, figsize=(fs.FULL_WIDTH, 5.4))
            fig.subplots_adjust(left=0.08, right=0.985, bottom=0.09, top=0.95, wspace=0.34,
                                hspace=0.26)
            for k in ks:
                g = numbers[k]["gauge"]
                c = col.get(lapse_of(k), "k")
                ax[0, 0].plot(g["t"], g["alpha_centre"], color=c, label=lab.get(lapse_of(k), k))
                if numbers[k]["alpha_ref"] is not None:
                    ax[0, 0].plot(g["t"], numbers[k]["alpha_ref"], color=c, ls=":", lw=1.0)
                ax[0, 1].plot(g["light_speed_time"], g["light_speed_max"], color=c)
                d = runs[k]
                for a, grp in zip((ax[1, 0], ax[1, 1], ax[1, 2]), ("core", "outer", "surface")):
                    idx = d["groups"][grp]
                    a.plot(d["tau"][:, idx].mean(axis=1), np.abs(d["eps"][:, idx]).max(axis=1),
                           color=c)
                reg = numbers[k]["regions"]
                if reg:
                    rec = reg[-1]
                    ax[0, 2].plot(rec["profile"]["r"], rec["profile"]["alpha"], color=c)
                    ax[0, 2].axvline(rec["r_surface"], color=c, lw=0.6, alpha=0.5)
            ax[0, 0].plot([], [], color="k", ls=":", lw=1.0, label="homogeneous reference")
            ax[0, 0].legend(fontsize=7)
            ax[0, 0].set_xlabel(r"coordinate time $t/M$", labelpad=-2)
            ax[0, 0].set_ylabel("lapse at the centre")
            ax[0, 1].set_xlabel(r"coordinate time $t/M$", labelpad=-2)
            ax[0, 1].set_ylabel(r"largest $\alpha/\sqrt{\gamma_{rr}}$ at the particles")
            ax[0, 2].set_xlabel(r"coordinate radius $r/M$", labelpad=-2)
            ax[0, 2].set_ylabel("lapse at the last dump (shell means)")
            for a, grp in zip((ax[1, 0], ax[1, 1], ax[1, 2]), ("core", "outer", "surface")):
                a.set_yscale("log")
                a.set_ylim(1e-5, 1.0)
                a.set_xlabel(r"proper time $\tau/M$", labelpad=-2)
                a.set_title(f"{grp} shells", fontsize=9)
            ax[1, 0].set_ylabel(r"largest $|R/R_{\rm exact}-1|$")
            fig.suptitle(r"%s, $\Delta x=%g\,M$" % (sname, dx), fontsize=9, y=0.995)
            fs.save(fig, os.path.join(FIGS, f"ball_{pre}_{sname}_dx{dx:g}".replace(".", "p")))
            plt.close(fig)

        # lapse profiles in time: old against new, at the finest common resolution
        dx = dxs[-1]
        ks = [k for k in keys if numbers[k]["dx"] == dx and lapse_of(k) in ("mp", "leak1", "ct")]
        if ks:
            fig, ax = plt.subplots(1, len(ks), figsize=(fs.FULL_WIDTH, 2.9), squeeze=False)
            fig.subplots_adjust(left=0.08, right=0.985, bottom=0.16, top=0.90, wspace=0.28)
            for a, k in zip(ax[0], ks):
                reg = numbers[k]["regions"]
                for rec, c in zip(reg, fs.series_colors(len(reg), cmap="viridis")):
                    a.plot(rec["profile"]["r"], rec["profile"]["alpha"], color=c,
                           label=r"$t=%g\,M$" % rec["time"])
                    a.axvline(rec["r_surface"], color=c, lw=0.6, alpha=0.5)
                a.set_title(lab.get(lapse_of(k), k) + r", $\Delta x=%g\,M$" % dx, fontsize=9)
                a.set_xlabel(r"coordinate radius $r/M$", labelpad=-2)
            ax[0, 0].set_ylabel("lapse (shell means)")
            ax[0, 0].legend(fontsize=7, ncol=2)
            fs.save(fig, os.path.join(FIGS, f"ball_{pre}_{sname}_lapse_profiles"))
            plt.close(fig)


if __name__ == "__main__":
    main()
