#!/usr/bin/env python3
"""V7: unit costs from the AthenaK logs of the first paper, and the particle-number and
sub-step requirements of a pairwise Monte Carlo operator at a given Knudsen number.

Logs (main checkout, untracked runs/st/..., read only). Cost per M: sum over segments of
"cpu time used" divided by the span of simulated time (initial to final), and the
steady rate d(elapsed)/d(time) from the per-cycle lines (median over intervals).
Requirement rule read at the source: Koda & Shapiro (1101.3097 sidm1.tex:667-673,
P_bar < 0.1; 680-684, r_k <~ lambda with k ~ 32, lines 551-553, 613). Translation used
here [JUDGEMENT, the scope's]: 32 macroparticles inside a sphere of radius
lambda = Kn_c H_c at the centre; lambda = 1/(rho0 sigma/m), H = (p/(4 pi rho^2))^{1/2}.
Inputs: v_king.json and v_mono.json from earlier runs (paths as argv[2], argv[3]).
Output (argv[1]): v_costs.json, fig_v7_costs.{png,pdf}.
"""
import glob
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, *[".."] * 5))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "python"))
MAIN = "/data/haiyangw/nrpic"
SETS = {   # name: (log globs, claimed span M, wall s, s per M, peak MiB) from SCOPE.md 8
    "yc0819 dx=M/2": (["runs/st/yc0819_v4/athena.20261113-062220.log"], 300, 501, 1.67, 12281),
    "migration dx=M/4": (["runs/st/migration_yc0500_v4/chain/seg00[123]*.log"], 2500, 8198,
                         3.28, 12283),
    "yc0756 dx=M/4 L=1024": (["runs/st/yc0756_unpert/chain/seg001.job4216.a1.log"], 800, 2968,
                             3.71, 14135),
    "yc0605 AMR": (["runs/st/yc0605_v5/athena.20261113-083550.log",
                    "runs/st/yc0605_v5/athena.20261113-100905.log"], 300, 4251, 14.2, 32343),
    "yc0500 AMR": (["runs/st/yc0500_v5/athena.20261113-083550.log"], 120, 2098, 17.5, 32343),
}
RE_EL = re.compile(r"elapsed=([0-9.eE+-]+) cycle=(\d+) time=([0-9.eE+-]+)")
RE_CPU = re.compile(r"cpu time used\s*=\s*([0-9.eE+-]+)")
RE_END = re.compile(r"^time=([0-9.eE+-]+) cycle=(\d+)\s*$")
RE_MEM = re.compile(r"gpu_mem_peak_MiB=(\d+)")


def parse(paths):
    t0, t1, cpu, rates, mem, files = None, None, 0.0, [], 0, []
    for pat in paths:
        for p in sorted(glob.glob(os.path.join(MAIN, pat))):
            files.append(p)
            el, tt = [], []
            for line in open(p, errors="replace"):
                m = RE_EL.search(line)
                if m:
                    el.append(float(m.group(1)))
                    tt.append(float(m.group(3)))
                m = RE_CPU.search(line)
                if m:
                    cpu += float(m.group(1))
                m = RE_END.match(line.strip())
                if m:
                    t1 = float(m.group(1)) if t1 is None else max(t1, float(m.group(1)))
                m = RE_MEM.search(line)
                if m:
                    mem = max(mem, int(m.group(1)))
            if tt:
                t0 = tt[0] if t0 is None else min(t0, tt[0])
                el, tt = np.array(el), np.array(tt)
                d = np.diff(tt)
                ok = d > 0
                rates += list(np.diff(el)[ok] / d[ok])
    return dict(files=files, t0=t0, t1=t1, cpu=cpu, span=t1 - t0, s_per_M=cpu / (t1 - t0),
                steady_s_per_M=float(np.median(rates)), peak_MiB=mem)


def main(out, kingjson, monojson):
    os.makedirs(out, exist_ok=True)
    res = dict(costs={})
    for name, (pats, span, wall, spm, mem) in SETS.items():
        r = parse(pats)
        r.update(claimed=dict(span=span, wall=wall, s_per_M=spm, peak_MiB=mem),
                 rel_s_per_M=r["s_per_M"] / spm - 1)
        res["costs"][name] = r
    # requirements per model
    K = json.load(open(kingjson))
    M = json.load(open(monojson))
    import kingsolve as ks
    models = []
    for k in K["knudsen"]:
        crit = K["criteria"]["0.1"]
        src = {"King b=0.1 eps max": crit["eps_max"], "King b=0.1 trial root": crit["trial_root"],
               "King b=1 eps max": K["king_b1"]["at_max"]}[k["label"]]
        models.append(dict(label=k["label"], rho0=k["rho0c_M2"], H=k["Hc_scope"],
                           M0=1 / (1 - src["eps"]), vmol=k["vmol_c"], alpha=1 / (1 + src["Z0"])))
    mx = M["max"]
    yc = mx["yc"]
    qc = np.sqrt(1 / yc - 1)
    # monoenergetic: all particles at speed qc; <v_Mol> over isotropic relative angles
    mu, wmu = np.polynomial.legendre.leggauss(400)
    W = np.sqrt(1 + qc * qc)
    g = W * W - qc * qc * mu
    vm = 0.5 * np.sum(wmu * np.sqrt(np.maximum(g * g - 1, 0)) / (W * W))
    models.append(dict(label="monoenergetic max", rho0=mx["rho0c_M2"], H=mx["Hc_over_M"],
                       M0=mx["M0_over_M"], vmol=float(vm), alpha=1 / (1 + mx["zc"])))
    dt = 1 / 16.0
    for m in models:
        m["N_at_Kn"] = {str(kn): 32 * m["M0"] / (m["rho0"] * 4 * np.pi / 3 * (kn * m["H"]) ** 3)
                        for kn in (1.0, 0.1, 0.01)}
        m["P_per_step_at_Kn"] = {str(kn): m["vmol"] / (kn * m["H"]) * m["alpha"] * dt
                                 for kn in (1.0, 0.1, 0.01)}
        m["nsub_at_Kn"] = {k: max(1.0, v / 0.1) for k, v in m["P_per_step_at_Kn"].items()}
    res["requirements"] = models
    # arithmetic of the G1-G3 estimates of SCOPE.md 8 (inputs as stated there)
    res["arith"] = dict(G1_mono=16 * 400 * 3.71 / 3600, G1_king=6 * 1000 * 4 / 3600,
                        G2_N=6 * 400 * (4.0 + 4.4) / 3600, G2_dx=2 * 2 * 400 * 8 * 3.71 / 3600,
                        G3=28 * 1000 * 20 / 3600)
    with open(os.path.join(out, "v_costs.json"), "w") as fh:
        json.dump(res, fh, indent=1, default=float)
    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(8, 3.2))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.26, top=0.95, wspace=0.3)
    ax = axs[0]
    names = list(res["costs"])
    x = np.arange(len(names))
    ax.bar(x - 0.2, [res["costs"][n]["claimed"]["s_per_M"] for n in names], 0.4,
           color=fs.PAL["blue"], label="SCOPE.md table")
    ax.bar(x + 0.2, [res["costs"][n]["s_per_M"] for n in names], 0.4, color=fs.PAL["red"],
           label="from the logs")
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=25, fontsize=7, ha="right")
    ax.set_ylabel("wall s per M (one A100)")
    ax.legend(loc="upper left")
    ax = axs[1]
    kn = np.logspace(-2, 1, 50)
    for m, c in zip(models, ["red", "yellow", "green", "blue"]):
        ax.plot(kn, 32 * m["M0"] / (m["rho0"] * 4 * np.pi / 3 * (kn * m["H"]) ** 3),
                color=fs.PAL[c], label=m["label"])
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.axhline(1e4, **fs.GUIDE)
    ax.axhline(1e6, color="k", lw=1.0, ls=":")
    ax.set_xlabel("Kn$_c$ = $\\lambda_c/H_c$")
    ax.set_ylabel("N for 32 partners within $\\lambda_c$")
    ax.legend(fontsize=7, loc="upper right")
    fs.save(fig, os.path.join(out, "fig_v7_costs"))
    print(json.dumps(dict(costs={n: (r["span"], r["cpu"], r["s_per_M"], r["steady_s_per_M"],
                                     r["peak_MiB"], r["rel_s_per_M"])
                                 for n, r in res["costs"].items()},
                          req=[(m["label"], m["N_at_Kn"], m["nsub_at_Kn"], m["vmol"])
                               for m in models], arith=res["arith"]), indent=1, default=float))


if __name__ == "__main__":
    main(*sys.argv[1:4])
