#!/usr/bin/env python3
"""Test T3d of tracks/core/JOURNAL-scalar2.md and the cost numbers: analysis of the card
runs of card_job.sh.

    python3 t3d_ladder.py --card DIR --out OUT

DIR holds lad<N>_p1, lad<N>_m1 (N = 32, 64, 128; the slow-roll case with nmax2 = 64 and
the mode functions scaled by +1 and -1, dumps every 0.4 to t = 3.2) and cost<N>_* (logs).
For each N the constraint fields of the two runs are split into the part even in the
amplitude (second order) and the odd part (first order: the truncation error of the
stencils); the orders in N follow from the rms of the parts at equal times.
Writes OUT/summary.json and OUT/fig_ladder.png."""
import argparse
import glob
import os
import re

import common
from common import np
from nrpic import scalar_field as sf

NS = (32, 64, 128)


def dumps(rundir):
    out = {}
    for f in sorted(glob.glob(os.path.join(rundir, "sr.sf.?????.dump"))):
        d = sf.read_dump(f)
        out[round(float(d["time"]), 1)] = d
    return out


def rms(x):
    return float(np.sqrt((x*x).mean()))


def zone_cycles(log):
    txt = open(log).read()
    m = re.search(r"zone-cycles/cpu_second = ([0-9.eE+-]+)", txt)
    c = re.search(r"cpu time used\s*= ([0-9.eE+-]+)", txt)
    return (float(m.group(1)) if m else None), (float(c.group(1)) if c else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--card", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    card = os.path.abspath(a.card)
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    summ = dict(card=card, status=open(os.path.join(card, "status.txt")).read().split("\n"))

    con = {n: sf.read_con_history(os.path.join(card, f"lad{n}_p1", "sr.sf.con.hst"))
           for n in NS}
    parts = {}
    for n in NS:
        dp, dm = dumps(os.path.join(card, f"lad{n}_p1")), dumps(os.path.join(card,
                                                                           f"lad{n}_m1"))
        rows = []
        for t in sorted(set(dp) & set(dm)):
            fp, fm = dp[t]["fields"], dm[t]["fields"]
            oh, eh = 0.5*(fp["H"] - fm["H"]), 0.5*(fp["H"] + fm["H"])
            om = np.sqrt(sum((0.5*(fp[x] - fm[x]))**2 for x in ("Mx", "My", "Mz")))
            em = np.sqrt(sum((0.5*(fp[x] + fm[x]))**2 for x in ("Mx", "My", "Mz")))
            rows.append(dict(time=t, efolds=float(-0.5*np.log(fp["chi"].mean())),
                             cycle=int(dp[t]["cycle"]), H_odd=rms(oh), H_even=rms(eh),
                             M_odd=rms(om), M_even=rms(em)))
        parts[n] = rows
    summ["parts"] = {str(n): r for n, r in parts.items()}
    # orders between the resolutions at the dump times common to all (same times: dump_dt)
    times = sorted(set.intersection(*[set(r["time"] for r in parts[n]) for n in NS]))
    orders = []
    for t in times:
        row = dict(time=t)
        for key in ("H_odd", "M_odd", "H_even", "M_even"):
            v = [next(r[key] for r in parts[n] if r["time"] == t) for n in NS]
            row[key] = v
            row[key + "_order"] = [float(np.log2(v[0]/v[1])) if v[1] > 0 and v[0] > 0
                                   else None,
                                   float(np.log2(v[1]/v[2])) if v[2] > 0 and v[1] > 0
                                   else None]
        orders.append(row)
    summ["orders"] = orders
    # box-mean ratios at fixed times (interpolated in time)
    tt = np.array([0.8, 1.2, 1.6, 2.0, 2.4, 2.8, 3.2])
    rat = {}
    for key in ("H_ratio", "M_ratio", "M_bssn_adm", "M_rms"):
        rat[key] = {str(n): np.interp(tt, con[n]["time"], con[n][key]).tolist() for n in NS}
    rat["times"] = tt.tolist()
    rat["H_ratio_order"] = [[float(np.log2(rat["H_ratio"]["32"][i]/rat["H_ratio"]["64"][i])),
                             float(np.log2(rat["H_ratio"]["64"][i]/rat["H_ratio"]["128"][i]))]
                            for i in range(tt.size)]
    rat["M_ratio_order"] = [[float(np.log2(rat["M_ratio"]["32"][i]/rat["M_ratio"]["64"][i])),
                             float(np.log2(rat["M_ratio"]["64"][i]/rat["M_ratio"]["128"][i]))]
                            for i in range(tt.size)]
    rat["Mbssn_adm_over_Mrms"] = {str(n): (np.array(rat["M_bssn_adm"][str(n)])
                                           / np.array(rat["M_rms"][str(n)])).tolist()
                                  for n in NS}
    summ["ratios"] = rat
    summ["max_ratios"] = {str(n): dict(H=float(con[n]["H_ratio"].max()),
                                       M=float(con[n]["M_ratio"].max())) for n in NS}

    # cost
    cost = {}
    for d in sorted(glob.glob(os.path.join(card, "cost*"))):
        zc, cpu = zone_cycles(os.path.join(d, "athena.log"))
        cost[os.path.basename(d)] = dict(zone_cycles_per_second=zc, seconds=cpu)
    for n in NS:
        zc, cpu = zone_cycles(os.path.join(card, f"lad{n}_p1", "athena.log"))
        cost[f"lad{n}_p1"] = dict(zone_cycles_per_second=zc, seconds=cpu)
    summ["cost"] = cost
    common.dump_json(summ, os.path.join(out, "summary.json"))

    fs = common.style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 6.0))
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.08, top=0.97, wspace=0.27,
                        hspace=0.22)
    cols = {32: fs.PAL["red"], 64: fs.PAL["green"], 128: fs.PAL["blue"]}
    for n in NS:
        c = con[n]
        ax[0, 0].plot(c["efolds"], c["H_ratio"], color=cols[n], label=f"$N={n}$")
        ax[0, 1].plot(c["efolds"], c["M_ratio"], color=cols[n], label=f"$N={n}$")
        en = [r["efolds"] for r in parts[n]]
        ax[1, 0].plot(en, [r["H_odd"] for r in parts[n]], "s--", ms=3, mfc="none",
                      color=cols[n], label=f"odd, $N={n}$")
        ax[1, 0].plot(en, [r["H_even"] for r in parts[n]], "o-", ms=3, color=cols[n],
                      label="even")
        ax[1, 1].plot(en, [r["M_odd"] for r in parts[n]], "s--", ms=3, mfc="none",
                      color=cols[n], label=f"odd, $N={n}$")
        ax[1, 1].plot(en, [r["M_even"] for r in parts[n]], "o-", ms=3, color=cols[n],
                      label="even")
    for p, yl in ((ax[0, 0], r"$\langle|H|/[H]\rangle$"),
                  (ax[0, 1], r"$\langle|M|/[M]\rangle$"),
                  (ax[1, 0], "rms of the parts of $H$ in the amplitude"),
                  (ax[1, 1], "rms of the parts of $|M|$ in the amplitude")):
        p.set_yscale("log")
        p.set_xlabel("e-folds after $N_*$", labelpad=-2)
        p.set_ylabel(yl)
        p.axvline(np.log(8.0), **fs.MASK_LINE)
        p.legend(loc="best", fontsize=7, ncol=2)
    fig.savefig(os.path.join(out, "fig_ladder.png"), dpi=200)
    print("ladder analysis done:", os.path.join(out, "summary.json"))


if __name__ == "__main__":
    main()
