#!/usr/bin/env python3
"""Tests T2 and T3 of tracks/core/JOURNAL-scalar2.md: the slow-roll case evolved from the
initial slice with the stochastic sources.

    python3 t23_evolve.py --exe EXE --out DIR [--workers 8] [--n 32] [--tlong 8.44]
                          [--tshort 3.2] [--analyse-only]

Runs problems/scalar/sr_stochastic.athinput (N = 32, nmax2 = 64, geodesic slicing):
  bg025   s = +1, Courant 0.25, to t = tlong (8 e-folds)
  bg0125  s = +1, Courant 0.125, to t = tlong
  m1, p05, m05     s = -1, +1/2, -1/2 to t = tshort
  ctl_p1, ctl_m1   noise_pi_sign = -1 (negative control), s = +-1, to t = tshort
T2: box means against the Friedmann reference (nrpic.scalar_field.friedmann).
T3: constraint ratios in time; even and odd parts in s of the constraint fields of the
dumps (second-order part and first-order part).
Writes DIR/summary.json, DIR/fig_background.png, DIR/fig_constraints.png."""
import argparse
import glob
import os

import common
from common import inf, np
from nrpic import scalar_field as sf

INP = os.path.join(common.PROB, "sr_stochastic.athinput")


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
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--n", type=int, default=32)
    ap.add_argument("--tlong", type=float, default=8.44)
    ap.add_argument("--tshort", type=float, default=3.2)
    ap.add_argument("--analyse-only", action="store_true")
    ap.add_argument("--data", help="with --analyse-only: directory of the runs of an "
                    "earlier execution (summary and figure go to --out)")
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    data = os.path.abspath(a.data) if a.data else out
    case = common.sr_case(64)
    base = common.write_case(case, out) + common.mesh_args(a.n) + [
        "scalar_field/dump_dt=0.4", "scalar_field/dump_noise=false",
        "scalar_field/dump_metric=false"]
    v, dv, phi0, pi0 = inf.code_background(case)

    spec = {
        "bg025": [f"time/tlim={a.tlong}"],
        "bg0125": [f"time/tlim={a.tlong}", "time/cfl_number=0.125"],
        "m1": [f"time/tlim={a.tshort}", "scalar_field/noise_mode_scale=-1.0"],
        "p05": [f"time/tlim={a.tshort}", "scalar_field/noise_mode_scale=0.5"],
        "m05": [f"time/tlim={a.tshort}", "scalar_field/noise_mode_scale=-0.5"],
        "ctl_p1": [f"time/tlim={a.tshort}", "scalar_field/noise_pi_sign=-1.0"],
        "ctl_m1": [f"time/tlim={a.tshort}", "scalar_field/noise_pi_sign=-1.0",
                   "scalar_field/noise_mode_scale=-1.0"],
    }
    summ = dict(exe=os.path.abspath(a.exe), n=a.n)
    if not a.analyse_only:
        cases = [(os.path.join(out, k), INP, base + x) for k, x in spec.items()]
        walls = common.run_many(os.path.abspath(a.exe), cases, a.workers)
        summ["wall_s"] = dict(zip(spec, walls))

    summ["data"] = data
    hist = {k: sf.read_history(os.path.join(data, k, "sr.sf.hst")) for k in spec}
    con = {k: sf.read_con_history(os.path.join(data, k, "sr.sf.con.hst")) for k in spec}

    # ------------------------------------------------------------------ T2 background
    t2 = {}
    curves = {}
    for k in ("bg025", "bg0125"):
        h = hist[k]
        ref = sf.friedmann(v, dv, phi0, pi0, h["time"][1:])
        rel = {}
        for name, key in (("phi", "phi"), ("Pi", "Pi"), ("K", "K")):
            rel[name] = np.abs(h[name][1:]/ref[key] - 1.0)
        dn = np.abs(-0.5*np.log(h["chi"][1:]) - ref["ln_a"])
        lock = {}
        for name, key in (("phi_b", "phi"), ("Pi_b", "Pi")):
            lock[name] = np.abs(h[name][1:]/ref[key] - 1.0)
        lock["ln_a"] = np.abs(h["ln_a"][1:] - ref["ln_a"])
        t2[k] = dict(steps=int(h["cycle"][-1]), t_end=float(h["time"][-1]),
                     efolds_end=float(ref["ln_a"][-1]),
                     max_rel={n_: float(x.max()) for n_, x in rel.items()},
                     end_rel={n_: float(x[-1]) for n_, x in rel.items()},
                     max_efold_diff=float(dn.max()), end_efold_diff=float(dn[-1]),
                     lockstep_max={n_: float(x.max()) for n_, x in lock.items()})
        curves[k] = (ref, rel, dn, lock)
    t2["efold_error_ratio_025_over_0125"] = (t2["bg025"]["end_efold_diff"]
                                             / t2["bg0125"]["end_efold_diff"])
    for name in ("phi", "Pi", "K"):
        t2[f"{name}_error_ratio_025_over_0125"] = (t2["bg025"]["end_rel"][name]
                                                   / t2["bg0125"]["end_rel"][name])
    summ["T2"] = t2

    # ----------------------------------------------------------- T3 constraints in time
    t3 = {}
    c1 = con["bg025"]
    sel = c1["time"] <= a.tshort + 1e-9
    t3["scale1_max_H_ratio"] = float(c1["H_ratio"].max())
    t3["scale1_max_M_ratio"] = float(c1["M_ratio"].max())
    t3["scale1_max_H_ratio_after_entry"] = float(c1["H_ratio"][c1["efolds"] > 2.6].max())
    t3["scale1_H_ratio_at_end"] = float(c1["H_ratio"][-1])
    t3["scale1_M_ratio_at_end"] = float(c1["M_ratio"][-1])
    t3["scale1_max_Mbssn_adm_over_Mrms"] = float(
        (c1["M_bssn_adm"][sel]/c1["M_rms"][sel]).max())
    # ratio of the box-mean ratios between s = 1 and s = 1/2 at the same cycles
    nc = min(len(con["p05"]["time"]), sel.sum())
    t3["H_ratio_s1_over_s05"] = (c1["H_ratio"][:nc]/con["p05"]["H_ratio"][:nc]).tolist()
    t3["M_ratio_s1_over_s05"] = (c1["M_ratio"][:nc]/con["p05"]["M_ratio"][:nc]).tolist()
    # control
    cc = con["ctl_p1"]
    first = (cc["efolds"] <= 1.0) & (cc["cycle"] > 0)
    t3["control_over_proper_H_ratio_max_first_efold"] = float(
        (cc["H_ratio"][first]/c1["H_ratio"][:len(cc["time"])][first]).max())
    t3["control_H_ratio_max"] = float(cc["H_ratio"].max())
    t3["control_M_ratio_at_1_efold"] = float(np.interp(1.0, cc["efolds"], cc["M_ratio"]))
    t3["control_M_ratio_max"] = float(cc["M_ratio"].max())

    # even and odd parts in s from the dumps
    dd = {k: dumps(os.path.join(data, k)) for k in spec if k != "bg0125"}
    cyc = sorted(set(dd["bg025"]) & set(dd["m1"]) & set(dd["p05"]) & set(dd["m05"]))
    parts = []
    for c in cyc:
        # equal times only: the short runs cut their last step at tlim
        tt = [dd[k][c]["time"] for k in dd]
        if max(tt) - min(tt) > 1e-9:
            continue
        row = dict(cycle=c, time=dd["bg025"][c]["time"])
        row["efolds"] = float(-0.5*np.log(dd["bg025"][c]["fields"]["chi"].mean()))
        for lab, kp, km in (("s1", "bg025", "m1"), ("s05", "p05", "m05"),
                            ("ctl", "ctl_p1", "ctl_m1")):
            fp, fm = dd[kp][c]["fields"], dd[km][c]["fields"]
            oh, eh = 0.5*(fp["H"] - fm["H"]), 0.5*(fp["H"] + fm["H"])
            om = np.sqrt(sum((0.5*(fp[x] - fm[x]))**2 for x in ("Mx", "My", "Mz")))
            em = np.sqrt(sum((0.5*(fp[x] + fm[x]))**2 for x in ("Mx", "My", "Mz")))
            row[lab] = dict(H_odd=rms(oh), H_even=rms(eh), M_odd=rms(om), M_even=rms(em),
                            H=rms(fp["H"]))
        parts.append(row)
    t3["parts"] = parts
    t3["even_s1_over_s05_H"] = [r["s1"]["H_even"]/r["s05"]["H_even"] for r in parts]
    t3["odd_s1_over_s05_H"] = [r["s1"]["H_odd"]/r["s05"]["H_odd"] for r in parts]
    t3["even_s1_over_s05_M"] = [r["s1"]["M_even"]/r["s05"]["M_even"] for r in parts]
    t3["odd_s1_over_s05_M"] = [r["s1"]["M_odd"]/r["s05"]["M_odd"] for r in parts]
    t3["odd_over_even_H_s1"] = [r["s1"]["H_odd"]/r["s1"]["H_even"] for r in parts]
    t3["odd_over_even_H_ctl"] = [r["ctl"]["H_odd"]/r["ctl"]["H_even"] for r in parts]
    summ["T3"] = t3
    common.dump_json(summ, os.path.join(out, "summary.json"))

    # ------------------------------------------------------------------------ figures
    fs = common.style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 6.0))
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.08, top=0.97, wspace=0.27,
                        hspace=0.22)
    h = hist["bg025"]
    ref, rel, dn, lock = curves["bg025"]
    p = ax[0, 0]
    p.plot(ref["ln_a"], ref["phi"]/phi0, color=fs.PAL["blue"], label=r"$\phi/\phi_*$")
    p.plot(ref["ln_a"], ref["Pi"]/pi0, color=fs.PAL["green"], label=r"$\Pi/\Pi_*$")
    p.plot(ref["ln_a"], ref["K"]/ref["K"][0], color=fs.PAL["orange"], label=r"$K/K_*$")
    st = max(1, len(h["time"])//40)
    en = -0.5*np.log(h["chi"])
    p.plot(en[::st], h["phi"][::st]/phi0, "o", ms=3, mfc="none", color=fs.PAL["red"],
           label="box means")
    p.plot(en[::st], h["Pi"][::st]/pi0, "o", ms=3, mfc="none", color=fs.PAL["red"])
    p.plot(en[::st], h["K"][::st]/h["K"][0], "o", ms=3, mfc="none", color=fs.PAL["red"])
    p.set_xlabel("e-folds after $N_*$", labelpad=0)
    p.set_ylabel("background (lines: Friedmann reference)")
    p.legend(loc="lower left", fontsize=8)
    p = ax[0, 1]
    for k, ls in (("bg025", "-"), ("bg0125", "--")):
        ref, rel, dn, lock = curves[k]
        lbl = "Courant 0.25" if k == "bg025" else "Courant 0.125"
        p.plot(ref["ln_a"], rel["phi"], ls, color=fs.PAL["blue"],
               label=r"$\langle\phi\rangle$, " + lbl)
        p.plot(ref["ln_a"], rel["Pi"], ls, color=fs.PAL["green"],
               label=r"$\langle\Pi\rangle$")
        p.plot(ref["ln_a"], rel["K"], ls, color=fs.PAL["orange"],
               label=r"$\langle K\rangle$")
        p.plot(ref["ln_a"], dn, ls, color=fs.PAL["red"], label="e-folds (absolute)")
    p.axhline(1e-4, **fs.MASK_LINE)
    p.set_yscale("log")
    p.set_xlabel("e-folds after $N_*$", labelpad=0)
    p.set_ylabel("difference to the Friedmann reference")
    p.legend(loc="center", bbox_to_anchor=(0.5, 0.47), fontsize=7, ncol=2)
    p = ax[1, 0]
    for k, cl, lbl in (("bg025", fs.PAL["blue"], "$s=1$"), ("p05", fs.PAL["green"],
                                                             "$s=1/2$"),
                       ("ctl_p1", fs.PAL["red"], "control, $s=1$")):
        c = con[k]
        p.plot(c["efolds"], c["H_ratio"], "-", color=cl,
               label=r"$\langle|H|/[H]\rangle$, " + lbl)
        p.plot(c["efolds"], c["M_ratio"], "--", color=cl,
               label=r"$\langle|M|/[M]\rangle$")
    p.axvline(np.log(8.0), **fs.MASK_LINE)
    p.set_yscale("log")
    p.set_xlabel("e-folds after $N_*$", labelpad=0)
    p.set_ylabel("constraint ratio")
    p.legend(loc="lower right", bbox_to_anchor=(0.995, 0.13), fontsize=6.5, ncol=2)
    p = ax[1, 1]
    en = np.array([r["efolds"] for r in parts])
    for lab, cl, lbl in (("s1", fs.PAL["blue"], "$s=1$"), ("s05", fs.PAL["green"],
                                                           "$s=1/2$"),
                         ("ctl", fs.PAL["red"], "control")):
        p.plot(en, [r[lab]["H_even"] for r in parts], "o-", ms=3, color=cl,
               label="even part of $H$, " + lbl)
        p.plot(en, [r[lab]["H_odd"] for r in parts], "s--", ms=3, mfc="none", color=cl,
               label="odd part")
    p.set_yscale("log")
    p.set_xlabel("e-folds after $N_*$", labelpad=0)
    p.set_ylabel("rms of the parts of $H$ in $s$")
    p.set_ylim(top=1e-2)
    p.legend(loc="upper center", fontsize=7, ncol=2)
    fig.savefig(os.path.join(out, "fig_evolve.png"), dpi=200)
    print("T2, T3 done:", os.path.join(out, "summary.json"))


if __name__ == "__main__":
    main()
