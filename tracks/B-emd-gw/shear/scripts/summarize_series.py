#!/usr/bin/env python3
"""Summary of a shear series (rays.json of every case of one run directory): Richardson
extrapolation of cos(theta) per case family over N_y = 32, 64, 128, observed order, the
constraint means at t = 0 and up to the arrival of the rays against N_y, the exact
conservation drifts, the metric at O, and the legs of P10 (lapse) and P11 (particles per
cell). Outcomes P4-P12 of JOURNAL.md are judged from summary.json and fig_series.png.

    python3 summarize_series.py <series run dir> [<out dir>]   (default $NRPIC_RUN_DIR)
"""
import json
import math
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle as fs  # noqa: E402

NYS = (32, 64, 128)


def load_cases(rundir):
    cases = {}
    for name in sorted(os.listdir(rundir)):
        p = os.path.join(rundir, name, "rays.json")
        if os.path.isfile(p):
            with open(p) as f:
                cases[name] = json.load(f)
        elif os.path.isdir(os.path.join(rundir, name)) and name[:1] in "SML":
            cases[name] = None                      # ran or failed without rays.json
    return cases


def richardson(c):
    """c = cos at N_y = 32, 64, 128. Observed order from the two differences; extrapolate
    with it when 1 <= p <= 6, else with p = 2 (stated in the result)."""
    d1, d2 = c[0] - c[1], c[1] - c[2]
    p = math.log2(d1/d2) if d1*d2 > 0 else float("nan")
    p_use = p if (math.isfinite(p) and 1.0 <= p <= 6.0) else 2.0
    ext = c[2] + (c[2] - c[1])/(2.0**p_use - 1.0)
    return p, p_use, ext


def main():
    rundir = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.environ["NRPIC_RUN_DIR"]
    os.makedirs(out, exist_ok=True)
    cases = load_cases(rundir)
    res = {"series_run": os.path.basename(os.path.normpath(rundir)), "cases": {},
           "families": {}, "legs": {}, "missing": []}
    for name, r in cases.items():
        if r is None or not r.get("shoot_A", {}).get("ok", False) or "cos" not in r:
            res["missing"].append(name)
            continue
        res["cases"][name] = {k: r.get(k) for k in (
            "beta", "HL", "ny", "ppc_y", "lapse", "cos_lin", "cos", "Delta",
            "Delta_no_transport", "ray_kx_kz_drift", "tracer_ux_uz_drift",
            "gxy_O_maxrel_dev", "alpha_over_aO_maxdev", "aO_over_abg_maxdev", "a_end")}
        res["cases"][name]["cstat_t0"] = r.get("cstat_t0")
        res["cases"][name]["cstat_max_to_arrival"] = r.get("cstat_max_to_arrival")
    fams = sorted({n.split("_")[0] for n in cases if n.split("_")[0][:1] in "SML"})
    for fam in fams:
        names = [f"{fam}_n{n}" for n in NYS]
        have = [n in res["cases"] for n in names]
        fr = {"names": names, "complete": all(have)}
        if all(have):
            cs = [res["cases"][n]["cos"] for n in names]
            lin = res["cases"][names[0]]["cos_lin"]
            p, p_use, ext = richardson(cs)
            fr.update({"cos": cs, "cos_lin": lin, "Delta": [c/lin - 1 for c in cs],
                       "p_obs": p, "p_used": p_use, "cos_ext": ext,
                       "Delta_ext": ext/lin - 1, "err128": cs[2]/lin - ext/lin})
            for key in ("cstat_t0", "cstat_max_to_arrival"):
                for q in ("Hr_mean", "Mr_mean"):
                    v = [res["cases"][n][key][q] for n in names]
                    fr[f"{key}.{q}"] = v
                    fr[f"{key}.{q}.ratios"] = [v[0]/v[1], v[1]/v[2]]
        res["families"][fam] = fr
    base = res["cases"].get("S1_n64")
    for leg in ("S1_n64_lap1", "S1_n64_ppc2", "S1_n64_ppc4"):
        if leg in res["cases"] and base:
            res["legs"][leg] = {"cos": res["cases"][leg]["cos"],
                                "rel_to_S1_n64": res["cases"][leg]["cos"]/base["cos"] - 1}
        else:
            res["legs"][leg] = {"missing": True}
    allc = list(res["cases"].values())
    res["max_ray_kx_kz_drift"] = max(c["ray_kx_kz_drift"] for c in allc)
    res["max_tracer_ux_uz_drift"] = max(c["tracer_ux_uz_drift"] for c in allc)
    with open(os.path.join(out, "summary.json"), "w") as f:
        json.dump(res, f, indent=1)

    # text table
    lines = ["family  HL     beta   Delta(32)    Delta(64)    Delta(128)   p_obs  Delta_ext    err128"]
    for fam, fr in res["families"].items():
        if not fr["complete"]:
            lines.append(f"{fam:6s}  incomplete: {[n for n in fr['names'] if n not in res['cases']]}")
            continue
        c = res["cases"][fr["names"][0]]
        d = fr["Delta"]
        lines.append(f"{fam:6s}  {c['HL']:<6g} {c['beta']:<6g} {d[0]:+.3e}  {d[1]:+.3e}  {d[2]:+.3e}  "
                     f"{fr['p_obs']:5.2f}  {fr['Delta_ext']:+.3e}  {fr['err128']:+.2e}")
    for fam, fr in res["families"].items():
        if fr["complete"]:
            lines.append(f"{fam} constraints t0 Hr {fr['cstat_t0.Hr_mean']} Mr {fr['cstat_t0.Mr_mean']}; "
                         f"max to arrival Hr {fr['cstat_max_to_arrival.Hr_mean']} "
                         f"Mr {fr['cstat_max_to_arrival.Mr_mean']}")
    for leg, v in res["legs"].items():
        lines.append(f"{leg}: {v}")
    lines.append(f"missing: {res['missing']}")
    lines.append(f"max drifts: ray k_x,k_z {res['max_ray_kx_kz_drift']:.2e}, tracer u_x,u_z "
                 f"{res['max_tracer_ux_uz_drift']:.2e}")
    txt = "\n".join(lines)
    print(txt)
    with open(os.path.join(out, "summary.txt"), "w") as f:
        f.write(txt + "\n")

    # figure
    fs.use_style()
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH*1.35, 3.1))
    complete = [f for f, fr in res["families"].items() if fr["complete"]]
    cols = fs.series_colors(max(len(complete), 2))
    ny = np.array(NYS, float)
    for i, fam in enumerate(complete):
        fr = res["families"][fam]
        axs[0].plot(ny, np.abs(fr["Delta"]), "o-", color=cols[i], label=fam)
        axs[0].axhline(abs(fr["Delta_ext"]), color=cols[i], lw=1.0, ls="--")
        axs[1].plot(ny, fr["cstat_t0.Mr_mean"], "o-", color=cols[i], label=fam)
        axs[2].plot(ny, fr["cstat_max_to_arrival.Mr_mean"], "o-", color=cols[i], label=fam)
        axs[2].plot(ny, fr["cstat_max_to_arrival.Hr_mean"], "s:", color=cols[i])
    for ax in axs:
        ax.set_xscale("log", base=2)
        ax.set_yscale("log")
        ax.set_xticks(NYS)
        ax.set_xticklabels([str(n) for n in NYS])
        ax.set_xlabel(r"$N_y$")
    axs[0].axhline(3e-4, **fs.MASK_LINE)
    axs[0].set_ylabel(r"$|\Delta| = |\cos\theta/\cos\theta_{\rm lin} - 1|$ (dashed: extrapolated)")
    axs[1].set_ylabel(r"$t = 0$: mean $M_r$")
    axs[2].set_ylabel(r"max to arrival: mean $M_r$ (o), $H_r$ (s)")
    for x0, ax in zip((32, 32), (axs[1], axs[2])):
        ax.plot(ny, ax.get_ylim()[1]*0.5*(ny/x0)**-4, **fs.GUIDE)
    axs[0].legend(fontsize=7, ncol=2, loc="lower left")
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(out, f"fig_series.{ext}"), dpi=150)


if __name__ == "__main__":
    main()
