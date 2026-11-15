#!/usr/bin/env python3
"""Test T3b of tracks/core/JOURNAL-scalar2.md: the three parts of the constraint
violation of the 32^3 slow-roll case.

    python3 t3b_parts.py --exe EXE --prev DIR --out OUT

DIR is the output of t23_evolve.py (runs bg025, m1, p05, m05 with the mode functions
scaled by s = +1, -1, +1/2, -1/2, and the controls).  This script adds the run with
s = 0 (a homogeneous universe on the same mesh with the same step) and splits the
constraint fields of the dumps taken at equal times into
  H0      the field of the s = 0 run (time integration of the background),
  O(s)    the part odd in s (first order: truncation error of the stencils),
  C2(s)   the even part minus H0 (second order),
and compares their rms between s = 1 and s = 1/2 (expected factors 2 and 4).
Writes OUT/summary.json and OUT/fig_parts.png."""
import argparse
import glob
import os

import common
from common import np
from nrpic import scalar_field as sf

INP = os.path.join(common.PROB, "sr_stochastic.athinput")
MODES = os.path.join(common.PROB, "sr_stochastic_modes.txt")


def dumps(rundir):
    out = {}
    for f in sorted(glob.glob(os.path.join(rundir, "sr.sf.?????.dump"))):
        d = sf.read_dump(f)
        out[int(d["cycle"])] = d
    return out


def rms(x):
    return float(np.sqrt((x*x).mean()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--prev", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tshort", type=float, default=3.2)
    a = ap.parse_args()
    out, prev = os.path.abspath(a.out), os.path.abspath(a.prev)
    os.makedirs(out, exist_ok=True)
    args = [f"scalar_field/noise_mode_file={MODES}", f"time/tlim={a.tshort}",
            "scalar_field/dump_dt=0.4", "scalar_field/dump_noise=false",
            "scalar_field/dump_metric=false", "scalar_field/noise_mode_scale=0.0"]
    wall = common.run_case(os.path.abspath(a.exe), os.path.join(out, "p0"), INP, args)
    dd = {k: dumps(os.path.join(prev, k)) for k in ("bg025", "m1", "p05", "m05", "ctl_p1",
                                                    "ctl_m1")}
    dd["p0"] = dumps(os.path.join(out, "p0"))
    rows = []
    for c in sorted(dd["p0"]):
        t = [dd[k][c]["time"] for k in dd if c in dd[k]]
        if len(t) < len(dd) or max(t) - min(t) > 1e-9:
            continue          # the last step of the short runs is cut at tlim
        f0 = dd["p0"][c]["fields"]
        row = dict(cycle=c, time=t[0], efolds=float(-0.5*np.log(f0["chi"].mean())),
                   H0_mean=float(f0["H"].mean()), H0_std=float(f0["H"].std()),
                   M0_rms=rms(np.sqrt(sum(f0[x]**2 for x in ("Mx", "My", "Mz")))))
        for lab, kp, km in (("s1", "bg025", "m1"), ("s05", "p05", "m05"),
                            ("ctl", "ctl_p1", "ctl_m1")):
            fp, fm = dd[kp][c]["fields"], dd[km][c]["fields"]
            oh = 0.5*(fp["H"] - fm["H"])
            eh = 0.5*(fp["H"] + fm["H"])
            c2 = eh - f0["H"]
            om = np.sqrt(sum((0.5*(fp[x] - fm[x]))**2 for x in ("Mx", "My", "Mz")))
            em = np.sqrt(sum((0.5*(fp[x] + fm[x]))**2 for x in ("Mx", "My", "Mz")))
            row[lab] = dict(H_odd=rms(oh), H_even=rms(eh), H_second=rms(c2),
                            H_second_mean=float(c2.mean()), M_odd=rms(om), M_even=rms(em))
        rows.append(row)
    summ = dict(exe=os.path.abspath(a.exe), prev=prev, wall_s=wall, rows=rows)
    summ["second_s1_over_s05_H"] = [r["s1"]["H_second"]/r["s05"]["H_second"] for r in rows]
    summ["odd_s1_over_s05_H"] = [r["s1"]["H_odd"]/r["s05"]["H_odd"] for r in rows]
    summ["even_s1_over_s05_M"] = [r["s1"]["M_even"]/r["s05"]["M_even"] for r in rows]
    summ["odd_s1_over_s05_M"] = [r["s1"]["M_odd"]/r["s05"]["M_odd"] for r in rows]
    c0 = sf.read_con_history(os.path.join(out, "p0", "sr.sf.con.hst"))
    summ["H0_ratio_to_Hmag"] = dict(time=c0["time"][::8].tolist(),
                                    H_ratio=c0["H_ratio"][::8].tolist())
    common.dump_json(summ, os.path.join(out, "summary.json"))

    fs = common.style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.4))
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.14, top=0.96, wspace=0.26)
    en = [r["efolds"] for r in rows]
    p = ax[0]
    p.plot(en, [abs(r["H0_mean"]) for r in rows], "k-", label="$s=0$ (background)")
    for lab, cl, lbl in (("s1", fs.PAL["blue"], "$s=1$"), ("s05", fs.PAL["green"],
                                                           "$s=1/2$")):
        p.plot(en, [r[lab]["H_odd"] for r in rows], "s--", ms=3, mfc="none", color=cl,
               label="odd part, " + lbl)
        p.plot(en, [r[lab]["H_second"] for r in rows], "o-", ms=3, color=cl,
               label="even part minus $s=0$, " + lbl)
    p.plot(en, [r["ctl"]["H_odd"] for r in rows], "s--", ms=3, mfc="none",
           color=fs.PAL["red"], label="odd part, control")
    p.axvline(np.log(8.0), **fs.MASK_LINE)
    p.set_yscale("log")
    p.set_xlabel("e-folds after $N_*$")
    p.set_ylabel("rms of the parts of $H$")
    p.legend(loc="center left", fontsize=7, bbox_to_anchor=(0.0, 0.62))
    p = ax[1]
    for lab, cl, lbl in (("s1", fs.PAL["blue"], "$s=1$"), ("s05", fs.PAL["green"],
                                                           "$s=1/2$")):
        p.plot(en, [r[lab]["M_odd"] for r in rows], "s--", ms=3, mfc="none", color=cl,
               label="odd part, " + lbl)
        p.plot(en, [r[lab]["M_even"] for r in rows], "o-", ms=3, color=cl,
               label="even part, " + lbl)
    p.plot(en, [r["ctl"]["M_odd"] for r in rows], "s--", ms=3, mfc="none",
           color=fs.PAL["red"], label="odd part, control")
    p.axvline(np.log(8.0), **fs.MASK_LINE)
    p.set_yscale("log")
    p.set_xlabel("e-folds after $N_*$")
    p.set_ylabel("rms of the parts of $|M|$")
    p.legend(loc="center left", fontsize=7, bbox_to_anchor=(0.0, 0.62))
    fig.savefig(os.path.join(out, "fig_parts.png"), dpi=200)
    print("T3b done:", os.path.join(out, "summary.json"))


if __name__ == "__main__":
    main()
