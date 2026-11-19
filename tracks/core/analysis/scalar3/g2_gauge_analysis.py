#!/usr/bin/env python3
"""Analysis of tests G1 and G2 of tracks/core/JOURNAL-scalar3.md (runs of g1_gauge.py):
the stochastic sources under a lapse that is not geodesic.

    python3 g2_gauge_analysis.py --data DIR [DIR ...] [--out DIR]

For the runs geo, harm (lapse_harmonic = 0.05) and kdrv (lapse_kdriver = 2): box means
against the lockstep background of the sources (which runs in the proper time of the
mean lapse); the mean lapse of harm against 1/(1 - 0.15 int H dt); rms of the lapse
perturbation from the dumps; R^NR per mode against L^(-3/2) W R alpha of the lockstep
record; constraint ratios.  Writes OUT/summary.json and OUT/fig_gauge.png."""
import argparse
import os

import s3
from s3 import common, np, sf

BASE = "srg"
NMAX2 = 64


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", nargs="+", required=True)
    ap.add_argument("--out")
    a = ap.parse_args()
    out = s3.run_dir(a.out)
    data = [os.path.abspath(d) for d in a.data]
    case = s3.case("sr", 1)
    mass = case["mass"]
    n, n2 = sf.mode_set(NMAX2)
    al = sf.mode_alpha(s3.SEED, 0, 0, n)
    q = np.sqrt(n2.astype(float))
    summ = dict(data=data, runs={})
    keep = {}
    for k in ("geo", "harm", "kdrv"):
        rd = next(os.path.join(d, k) for d in data
                  if os.path.exists(os.path.join(d, k, BASE + ".sf.hst")))
        h = sf.read_history(os.path.join(rd, BASE + ".sf.hst"))
        c = sf.read_con_history(os.path.join(rd, BASE + ".sf.con.hst"))
        hub = np.sqrt((8.0*np.pi/3.0)*(0.5*h["Pi_b"]**2 + 0.5*mass**2*h["phi_b"]**2))
        r = dict(t_end=float(h["time"][-1]), efolds_end=float(h["ln_a"][-1]),
                 steps=int(h["time"].size - 1),
                 alpha_mean_end=float(h["alpha"][-1]),
                 alpha_mean_max_dev_from_1=float(np.abs(h["alpha"] - 1.0).max()),
                 max_phi_vs_lock=float(np.abs(h["phi"]/h["phi_b"] - 1.0).max()),
                 max_Pi_vs_lock=float(np.abs(h["Pi"]/h["Pi_b"] - 1.0).max()),
                 max_K_vs_lock=float(np.abs(h["K"]/(-3.0*hub) - 1.0).max()),
                 max_efolds_vs_lock=float(np.abs(-0.5*np.log(h["chi"]) - h["ln_a"]).max()),
                 H_ratio_max=float(c["H_ratio"].max()),
                 M_ratio_max=float(c["M_ratio"].max()),
                 H_ratio_end=float(c["H_ratio"][-1]), M_ratio_end=float(c["M_ratio"][-1]))
        if k == "harm":
            # 1/alpha = 1 - 3 c int H dt (coordinate time), H of the lockstep background
            ih = np.concatenate([[0.0], np.cumsum(0.5*(hub[1:] + hub[:-1])
                                                  * np.diff(h["time"]))])
            pred = 1.0/(1.0 - 0.15*ih)
            r["alpha_vs_formula_max"] = float(np.abs(h["alpha"]/pred - 1.0).max())
            r["alpha_formula_end"] = float(pred[-1])
        dd = s3.dumps(rd, BASE)
        rows = []
        for cy in sorted(dd):
            d = dd[cy]
            rp, means = s3.rnr_of_dump(d, n, n2)
            ref, w, head, _ = s3.lock_reference(d["file"], n2)
            ref = ref*al
            ent = w > 0.5
            row = dict(cycle=cy, time=float(d["time"]), efolds=float(np.log(head["a"])),
                       alpha_mean=float(d["fields"]["alpha"].mean()),
                       alpha_rms=float(d["fields"]["alpha"].std()),
                       K_rms=float(d["fields"]["K"].std()), modes_in=int(ent.sum()))
            dev = np.abs(rp/ref - 1.0)
            for lab, sel in (("n_le_2", ent & (q <= 2.0 + 1e-9)),
                             ("n_le_4", ent & (q <= 4.0 + 1e-9)), ("all_in", ent)):
                row[lab] = float(dev[sel].max()) if sel.any() else None
            sel = w > 1e-3
            row["w_gt_1e-3"] = float(dev[sel].max())
            rows.append(row)
        r["dumps"] = rows
        late = [x for x in rows if x["time"] > 0.0]
        for lab in ("n_le_2", "n_le_4", "all_in"):
            vals = [x[lab] for x in late if x[lab] is not None]
            r["max_dev_" + lab] = max(vals)
            r["end_dev_" + lab] = vals[-1]
        r["alpha_rms_max"] = max(x["alpha_rms"] for x in rows)
        summ["runs"][k] = r
        keep[k] = (h, c, rows)
    g = summ["runs"]["geo"]
    for k in ("harm", "kdrv"):
        r = summ["runs"][k]
        for lab in ("n_le_2", "n_le_4", "all_in"):
            r[f"max_dev_{lab}_over_geo"] = r["max_dev_" + lab]/g["max_dev_" + lab]
            r[f"end_dev_{lab}_over_geo"] = r["end_dev_" + lab]/g["end_dev_" + lab]
        r["H_ratio_max_over_geo"] = r["H_ratio_max"]/g["H_ratio_max"]
        r["M_ratio_max_over_geo"] = r["M_ratio_max"]/g["M_ratio_max"]
    common.dump_json(summ, os.path.join(out, "summary.json"))

    fs = common.style()
    import matplotlib.pyplot as plt
    cols = dict(geo=fs.PAL["blue"], harm=fs.PAL["red"], kdrv=fs.PAL["green"])
    labs = dict(geo="geodesic", harm=r"$\partial_t\alpha=-0.05\,\alpha^2\hat K$",
                kdrv=r"driver, $\mu=2$")
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.8))
    fig.subplots_adjust(left=0.075, right=0.99, bottom=0.16, top=0.95, wspace=0.32)
    for k, (h, c, rows) in keep.items():
        ne = [x["efolds"] for x in rows]
        ax[0].plot(h["ln_a"], h["alpha"], color=cols[k], label=labs[k])
        ax[0].plot(ne, [1.0 + x["alpha_rms"]*1e5 for x in rows], ":", color=cols[k])
        ax[1].plot(ne[1:], [x["n_le_2"] for x in rows[1:]], "-", color=cols[k],
                   label=labs[k])
        ax[1].plot(ne[1:], [x["all_in"] for x in rows[1:]], "--", color=cols[k])
        ax[2].plot(c["efolds"][1:], c["H_ratio"][1:], "-", color=cols[k])
        ax[2].plot(c["efolds"][1:], c["M_ratio"][1:], "--", color=cols[k])
    ax[0].set_xlabel("e-folds after $N_*$")
    ax[0].set_ylabel(r"$\langle\alpha\rangle$ (dotted: $1+10^5\,{\rm rms}\,\delta\alpha$)")
    ax[0].legend(loc="upper left", fontsize=7)
    ax[1].set_yscale("log")
    ax[1].axhline(2e-2, **fs.MASK_LINE)
    ax[1].set_xlabel("e-folds after $N_*$")
    ax[1].set_ylabel(r"$|R^{\rm NR}_n/(W R\alpha_n)-1|$: $|n|\leq2$, all (dashed)")
    ax[1].legend(loc="lower right", fontsize=6.5)
    ax[2].set_yscale("log")
    ax[2].set_xlabel("e-folds after $N_*$")
    ax[2].set_ylabel(r"$\langle|\mathcal{H}|/[\mathcal{H}]\rangle$, "
                     r"$\langle|\mathcal{M}|/[\mathcal{M}]\rangle$ (dashed)")
    fig.savefig(os.path.join(out, "fig_gauge.png"), dpi=200)
    print("G1/G2 analysis done:", os.path.join(out, "summary.json"))


if __name__ == "__main__":
    main()
