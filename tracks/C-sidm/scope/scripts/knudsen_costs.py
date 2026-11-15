#!/usr/bin/env python3
"""Knudsen numbers, collision time scales and measured costs for the scoping of Track C.

1. Candidate initial models near the collisionless instability threshold (code units
   G = c = M_ADM = 1): the monoenergetic sequence (python/nrpic/st_cluster.py) at its
   binding-energy maximum and at the two models that bracket it in the first paper
   (y_c = 0.756, 0.605); the truncated Maxwell-Boltzmann (relativistic King) family of
   arXiv:2108.11967 at b = 0.1 (maximum of the fractional binding energy, adiabatic-index
   criterion) and at b = 1 (the King model of arXiv:2009.08163), from king_sequence.py.
2. Definitions (SCOPE.md section 4): lambda = 1/(n sigma) = m/(rho_0 sigma) with rho_0 the
   rest-mass density; H = (p/(4 pi rho^2))^(1/2) (rho energy density); Kn = lambda/H
   (arXiv:2010.15132, smbh.tex line 116, in its relativistic form); Kn_R = lambda_c/R;
   t_dyn = (4 pi rho)^(-1/2); relaxation time t_r = lambda/(a v), a = (16/pi)^(1/2),
   v = (p/rho)^(1/2) (astro-ph/0110561 line 310; 2601.17117 line 233), so t_r = t_dyn Kn/a.
3. Physical cross-section per unit mass: sigma/m = (sigma/m)_code G^2 M / c^4.
4. Requirements of a pairwise Monte Carlo operator (arXiv:1101.3097, sidm1.tex lines
   667-697): collision probability per step below 0.1, and the k = 32 collision partners
   inside one mean free path, i.e. N >= k M_0 / (rho_0c (4 pi/3) lambda_c^3).
5. Measured costs of the relativistic-cluster runs of the first paper, parsed from their
   AthenaK logs (wall clock of the run, "cpu time used" = Kokkos::Timer), and the
   particle cost per particle and cycle from the 2.1e6-particle periodic run.

Output (in $NRPIC_RUN_DIR): knudsen_costs.json, fig_knudsen.{pdf,png}, fig_costs.{pdf,png}.
"""
import glob
import json
import math
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, *[".."] * 4))
sys.path.insert(0, os.path.join(ROOT, "python"))
sys.path.insert(0, HERE)
from nrpic import st_cluster as st          # noqa: E402
from nrpic import figstyle as fs           # noqa: E402
import king_sequence as ks                 # noqa: E402
import matplotlib.pyplot as plt            # noqa: E402

OUT = os.environ.get("NRPIC_RUN_DIR", ".")
RUNS = "/data/haiyangw/nrpic/runs"        # untracked run directories of the main checkout
G, C_LIGHT, MSUN = 6.674e-8, 2.998e10, 1.989e33
A_HS = math.sqrt(16.0 / math.pi)
K_NB = 32


def unit_sigma_over_m(M_msun):
    """cm^2/g of (sigma/m)_code = 1 for a cluster of ADM mass M (G^2 M / c^4)."""
    return G * G * M_msun * MSUN / C_LIGHT ** 4


def candidates():
    out = []
    bmax = st.binding_energy_maximum()
    for name, yc in [("mono y_c,max", bmax["yc"]), ("mono 0.756", 0.756),
                     ("mono 0.605", 0.605)]:
        m = st.STModel(yc)
        out.append(dict(name=name, family="monoenergetic", param=yc, M0=m.M0, R=m.R,
                        rho_c=m.rho_c, p_c=m.P_c, rho0_c=float(m.rho0_nodes[0]),
                        H_c=math.sqrt(m.P_c / (4 * math.pi * m.rho_c ** 2)), zc=m.zc,
                        eps_b=m.Eb_over_M0))
    js = {}
    for b, w0, name in [(0.1, None, "King b=0.1 eps max"), (0.1, "ad", "King b=0.1 <gamma>=gamma_cr"),
                        (1.0, None, "King b=1 eps max")]:
        if w0 is None:
            lo, hi = {0.1: (2.0, 4.5), 1.0: (0.1, 0.6)}[b]
            mm = ks.eps_max(b, lo, hi)
        else:
            from scipy.optimize import brentq
            wc = brentq(lambda x: (lambda g: g[0] - g[1])(ks.adiabatic(0.1, x)), 3.5, 4.5,
                        xtol=1e-6)
            mm = ks.model(0.1, wc)
        Mh = mm["M"]
        # scale to M = 1: lengths / Mh, densities * Mh^2; rest-mass density m n
        out.append(dict(name=name, family="truncated Maxwell-Boltzmann", param=mm["w0"], b=b,
                        M0=mm["E_rest"] / Mh, R=mm["R"] / Mh, rho_c=mm["rho_c"] * Mh ** 2,
                        p_c=mm["p_c"] * Mh ** 2, rho0_c=mm["n_c"] * Mh ** 2,
                        H_c=mm["H_c"] / Mh, zc=mm["Z0"], eps_b=mm["eps_b"]))
    for c in out:
        c["t_dyn"] = 1.0 / math.sqrt(4 * math.pi * c["rho_c"])
        c["T_core"] = math.pi * math.sqrt(3.0 / (4 * math.pi * c["rho_c"]))
        c["v1d_c"] = math.sqrt(c["p_c"] / c["rho_c"])
        c["R_over_H"] = c["R"] / c["H_c"]
        # sigma/m (code units) for Kn_c = 1
        c["sigma_code_Kn1"] = 1.0 / (c["rho0_c"] * c["H_c"])
    return out


def phys_table(cands):
    rows = []
    for c in cands:
        for Mm in (1.0, 200.0, 1.9e9):
            u = unit_sigma_over_m(Mm)
            for s in (1.0, 5.0, 100.0):
                sc = s / u
                kn = 1.0 / (c["rho0_c"] * c["H_c"] * sc)
                rows.append(dict(model=c["name"], M_msun=Mm, sigma_over_m_cgs=s,
                                 Kn_c=kn, Kn_R=kn * c["H_c"] / c["R"]))
            rows.append(dict(model=c["name"], M_msun=Mm, sigma_over_m_cgs_for_Kn1=
                             c["sigma_code_Kn1"] * u))
    return rows


def requirements(c, kn, dt):
    lam = kn * c["H_c"]
    t_r = kn * c["t_dyn"] / A_HS
    return dict(Kn_c=kn, lambda_c=lam, t_r=t_r, collisions_per_step=dt / t_r,
                subcycles=max(1, math.ceil(10.0 * dt / t_r)),
                N_required=K_NB * c["M0"] / (c["rho0_c"] * 4.0 / 3.0 * math.pi * lam ** 3),
                dx_required=lam)


# ---- measured costs ----------------------------------------------------------------
def parse_log(path):
    txt = open(path).read()
    d = dict(path=path)
    for key, pat in [("wall_s", r"cpu time used\s*=\s*([0-9.eE+-]+)"),
                     ("mb_cycles", r"MeshBlock-cycles\s*=\s*([0-9]+)"),
                     ("zcps", r"zone-cycles/cpu_second\s*=\s*([0-9.eE+-]+)"),
                     ("npart", r"NRPIC: read ([0-9]+) particles"),
                     ("gpu_peak_MiB", r"gpu_mem_peak_MiB=([0-9]+)"),
                     ("tlim_arg", r"time/tlim=([0-9.]+)"),
                     ("tlim", r"tlim=([0-9.eE+-]+) nlim")]:
        m = re.findall(pat, txt)
        if m:
            d[key] = float(m[-1])
    m = re.findall(r"wall-clock limit reached at 'time=([0-9.eE+-]+) cycle=([0-9]+)'", txt)
    d["term"] = "wall" if "Terminating on wall clock limit" in txt else "tlim"
    return d


SETUPS = [
    ("static, dx=M/2, L=1024M, 7 levels; y_c=0.819 kick", ["st/yc0819_v4/athena.20261113-062220.log"],
     (0.0, 300.0)),
    ("static, dx=M/4, L=512M; y_c=0.5 migration", ["st/migration_yc0500_v4/chain/seg00*.log"],
     (0.0, 2500.0)),
    ("static, dx=M/4, L=1024M, 8 levels; y_c=0.756 unperturbed",
     ["st/yc0756_unpert/chain/seg001.job4216.a1.log"], (0.0, 800.0)),
    ("adaptive 1/4->1/16, L=512M, 9 levels; y_c=0.605 collapse",
     ["st/yc0605_v5/athena.20261113-083550.log", "st/yc0605_v5/athena.20261113-100905.log"],
     (0.0, 300.0)),
    ("adaptive 1/4->1/16, L=512M, 9 levels; y_c=0.5 collapse",
     ["st/yc0500_v5/athena.20261113-083550.log"], (0.0, 120.0)),
]
PART_RUN = "cosmo/dav_c256_n64/athena.20261114-031241.log"   # 2.1e6 particles, 64^3, 8 blocks
Z4C_ZCPS_32 = 1.9e7   # docs/TESTLOG.md line 46: 128^3 RK4, 32^3 MeshBlocks, nghost 4


def costs():
    out = []
    for name, pats, (t0, t1) in SETUPS:
        files = sorted(f for p in pats for f in glob.glob(os.path.join(RUNS, p)))
        logs = [parse_log(f) for f in files]
        wall = sum(l["wall_s"] for l in logs)
        out.append(dict(setup=name, logs=[os.path.relpath(f, "/data/haiyangw/nrpic")
                                          for f in files],
                        t_span_M=t1 - t0, wall_s=wall, s_per_M=wall / (t1 - t0),
                        card_h_per_100M=wall / (t1 - t0) * 100 / 3600,
                        zcps=[l.get("zcps") for l in logs],
                        gpu_peak_MiB=max(l.get("gpu_peak_MiB", 0) for l in logs),
                        npart=logs[0].get("npart")))
    l = parse_log(os.path.join(RUNS, PART_RUN))
    cycles = l["mb_cycles"] / 8.0
    t_cycle = l["wall_s"] / cycles
    t_z4c = 64 ** 3 / Z4C_ZCPS_32
    part = dict(log=os.path.relpath(os.path.join(RUNS, PART_RUN), "/data/haiyangw/nrpic"),
                npart=l.get("npart"), cycles=cycles, s_per_cycle=t_cycle,
                z4c_s_per_cycle_estimate=t_z4c,
                s_per_particle_cycle=(t_cycle - t_z4c) / l["npart"],
                gpu_peak_MiB=l.get("gpu_peak_MiB"))
    return out, part


def main():
    cands = candidates()
    phys = phys_table(cands)
    kns = np.logspace(-4, 2, 61)
    req = {c["name"]: [requirements(c, k, 1.0 / 16.0) for k in kns] for c in cands}
    cost, part = costs()
    res = dict(candidates=cands, physical=phys, requirements_dt_M16=req, costs=cost,
               particle_cost=part)
    with open(os.path.join(OUT, "knudsen_costs.json"), "w") as f:
        json.dump(res, f, indent=1)

    # ---- figure 1: Knudsen numbers
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.2))
    a1 = fs.inch_axes(fig, 0.75, 0.55, 3.0, 2.5)
    a2 = fs.inch_axes(fig, 4.75, 0.55, 3.0, 2.5)
    ref = next(c for c in cands if c["name"] == "King b=0.1 eps max")
    sg = np.logspace(-24, 3, 200)
    for col, Mm, lab in zip(fs.series_colors(3), (1.0, 200.0, 1.9e9),
                            (r"$M=1\,M_\odot$", r"$M=200\,M_\odot$",
                             r"$M=1.9\times10^9\,M_\odot$")):
        kn = 1.0 / (ref["rho0_c"] * ref["H_c"] * sg / unit_sigma_over_m(Mm))
        a1.loglog(sg, kn, color=col, label=lab)
    a1.axvspan(1.0, 100.0, color="grey", alpha=0.15)
    a1.axhspan(1e-1, 1e2, color=fs.PAL["green"], alpha=0.12)
    a1.axhline(1.0, **fs.THIN)
    a1.set_xlim(1e-24, 1e3)
    a1.set_ylim(1e-22, 1e4)
    a1.set_xlabel(r"$\sigma/m$ [cm$^2$ g$^{-1}$]")
    a1.set_ylabel(r"central Knudsen number $\lambda_c/H_c$")
    a1.text(2e-3, 3e-20, "observed\n1-100", fontsize=8)
    a1.text(1e-6, 2e2, "pairwise MC, $N\leq10^6$", fontsize=8, color=fs.PAL["green"])
    a1.legend(loc="lower left", fontsize=8)
    show = ["mono y_c,max", "King b=0.1 eps max", "King b=1 eps max"]
    for col, name in zip(fs.series_colors(3), show):
        r = req[name]
        a2.loglog(kns, [x["collisions_per_step"] for x in r], color=col, label=name)
        a2.loglog(kns, [x["N_required"] for x in r], color=col, ls="--")
    a2.axhline(1e4, **fs.MASK_LINE)
    a2.axhline(2e6, **fs.MASK_LINE)
    a2.axhline(0.1, ls=":", **fs.THIN)
    a2.text(1.3e-4, 1.4e4, "N of the first paper", fontsize=7)
    a2.text(1.3e-4, 2.8e6, "N of Wu and Most", fontsize=7)
    a2.text(1.3e1, 0.14, "0.1 per step", fontsize=7)
    a2.set_xlabel(r"central Knudsen number $\lambda_c/H_c$")
    a2.set_ylabel(r"per step (solid); $N$ needed (dashed)")
    a2.set_ylim(1e-4, 1e16)
    a2.legend(loc="upper right", fontsize=7)
    fs.save(fig, os.path.join(OUT, "fig_knudsen"))

    # ---- figure 2: measured costs
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 2.8))
    ax = fs.inch_axes(fig, 3.6, 0.5, 4.2, 2.1)
    y = np.arange(len(cost))
    ax.barh(y, [c["s_per_M"] for c in cost], color=fs.PAL["blue"], alpha=0.8)
    ax.set_yticks(y)
    ax.set_yticklabels([c["setup"] for c in cost], fontsize=7)
    ax.invert_yaxis()
    ax.minorticks_off()
    ax.set_xlim(0, 20)
    ax.set_xlabel(r"wall-clock seconds per $M$ of evolution (one A100, $N=10^4$)")
    for yi, c in zip(y, cost):
        ax.text(c["s_per_M"] * 1.02, yi, f"{c['s_per_M']:.1f}", va="center", fontsize=7)
    fs.save(fig, os.path.join(OUT, "fig_costs"))

    for c in cands:
        print({k: (round(v, 6) if isinstance(v, float) else v) for k, v in c.items()})
    for r in phys:
        print(r)
    for c in cost:
        print(c["setup"], round(c["s_per_M"], 3), round(c["card_h_per_100M"], 4), c["gpu_peak_MiB"])
    print(part)


if __name__ == "__main__":
    main()
