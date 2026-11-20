#!/usr/bin/env python3
"""Design numbers of the G2 convergence series (package conv_ball, Track A, wave 3):
for every planned member the mesh (levels, MeshBlocks, cells), the nested particle lattice
(count per level), the memory and the card time from the cost model of nested.py, and the
data of the larger ball of the ball-radius leg (expball model: same H, same core and
compensation in units of the mass M3 of data set 3, larger Einstein-de Sitter envelope).

Writes <out>/design.json, <out>/design_table.md and <out>/fig_design.png (cell width
against radius for the members and BH-1R, with the coordinate radii of the shell groups of
BH-1R from the geometry probe, run A-20261120-222355-cc8e0af).

    design_calc.py --exact <prep dir of data set 3>/exact.json --probe <probe dir> --out <dir>
"""
import argparse
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C            # noqa: E402
import nested as NS           # noqa: E402

TLIM = 16.0
CFL = 0.25


def big_ball_spec(spec3, lam):
    """Data set 3 inside a ball lam times larger (areal radius of the envelope), with the
    same H, core, compensation radius and taper width, in units of the mass M3 of data set
    3: HRb -> lam HRb, M -> lam^3 (Einstein-de Sitter envelope: M = H^2 R_b^3 / 2)."""
    Rb3 = 2.0 * spec3.get("M", 1.0) / spec3["HRb"] ** 2
    w = spec3["edge_width"]
    s = dict(spec3)
    s["HRb"] = spec3["HRb"] * lam
    s["M"] = spec3.get("M", 1.0) * lam ** 3
    Rb = 2.0 * s["M"] / s["HRb"] ** 2
    assert abs(Rb - lam * Rb3) < 1e-9
    s["R1_over_Rb"] = spec3["R1"] / Rb
    s["R2_over_Rb"] = spec3["R2"] / Rb
    s["rm"] = Rb + w
    s["lam"] = lam
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exact", required=True)
    ap.add_argument("--probe", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--lam", type=float, nargs="+", default=[1.25, 1.35])
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    ex = C.load_json(a.exact)
    spec3 = ex["spec"]
    ball3 = C.ball_from_spec(spec3)
    rm3 = ball3.matter_rbar()
    res = dict(data_set_3=dict(spec=spec3, rm=rm3, M=ball3.M, rest_mass=ball3.rest_mass(),
                               max_2m_over_R=ball3.summary()["max_2m_over_R"]))
    balls = {}
    for lam in a.lam:
        sp = big_ball_spec(spec3, lam)
        b = C.ball_from_spec(sp)
        sm = b.summary()
        balls[lam] = (sp, b)
        res[f"ball_lam{lam:g}"] = dict(spec=sp, rm=b.matter_rbar(), M=b.M, rest_mass=b.rest_mass(),
                                       max_2m_over_R=sm["max_2m_over_R"], R_at_max=sm["R_at_max_2m_over_R"],
                                       H=b.H, H3=ball3.H, Rb=b.Rb,
                                       core_m_edge=float(b.at(np.array([spec3["R1"]]))["m"][0]),
                                       core_m_edge3=float(ball3.at(np.array([spec3["R1"]]))["m"][0]))
    # members: (name, h_f, outer, sub, ball)
    members = [("A", 1 / 16, 16.0, 1, None), ("B", 1 / 32, 16.0, 1, None), ("C", 1 / 64, 16.0, 1, None),
               ("A-N8", 1 / 16, 16.0, 2, None), ("A-N64", 1 / 16, 16.0, 4, None), ("B-N8", 1 / 32, 16.0, 2, None),
               ("A-L32", 1 / 16, 32.0, 1, None), ("B-L32", 1 / 32, 32.0, 1, None)]
    for lam in a.lam:
        members += [(f"A-R{lam:g}", 1 / 16, 16.0, 1, lam), (f"B-R{lam:g}", 1 / 32, 16.0, 1, lam)]
    rows = []
    for name, hf, outer, sub, lam in members:
        g = NS.nest_blocks(hf, outer)
        rm = rm3 if lam is None else balls[lam][0]["rm"]
        npart, per = NS.count_sites(g["levels"], sub, rm)
        steps = int(round(TLIM / (CFL * hf)))
        mem = NS.memory_mib(g["leaf_blocks"], g["block"], npart)
        sps = NS.seconds_per_step(g["leaf_cells"], g["block"], npart)
        rows.append(dict(name=name, h_f=hf, outer=outer, sub=sub, lam=lam, n_root=g["n_root"], block=g["block"],
                         leaf_blocks=g["leaf_blocks"], leaf_cells=g["leaf_cells"], particles=npart,
                         particles_per_spacing=per, steps=steps, mem_GiB=mem / 1024.0, s_per_step=sps,
                         card_hours=steps * sps / 3600.0,
                         levels=[[b, h] for b, h in g["levels"]]))
    # BH-1R for reference (measured)
    rows.append(dict(name="BH-1R (measured)", h_f=1 / 16, outer=16.0, sub=1, lam=None, n_root=256, block=32,
                     leaf_blocks=568, leaf_cells=568 * 32 ** 3, particles=1317216, steps=1024,
                     mem_GiB=80633 / 1024.0, s_per_step=1.7187, card_hours=1769.181 / 3600.0,
                     model_mem_GiB=NS.memory_mib(568, 32, 1317216) / 1024.0,
                     model_s_per_step=NS.seconds_per_step(568 * 32 ** 3, 32, 1317216),
                     levels=[[16.0, 0.125], [4.0, 0.0625]]))
    res["members"] = rows
    res["model"] = dict(MIB_PER_BLOCK32=NS.MIB_PER_BLOCK32, MIB_PER_PARTICLE=NS.MIB_PER_PARTICLE,
                        S_PER_PARTICLE_STEP=NS.S_PER_PARTICLE_STEP, S_PER_CELL_STEP32=NS.S_PER_CELL_STEP32,
                        S_STEP_FLOOR=NS.S_STEP_FLOOR)
    C.write_json(os.path.join(a.out, "design.json"), res)
    with open(os.path.join(a.out, "design_table.md"), "w") as f:
        f.write("| member | finest cell | outer | particles/cell | root cells | block | leaf blocks | leaf cells | particles | steps | memory GiB | s/step | card-h |\n")
        f.write("|---|---|---|---|---|---|---|---|---|---|---|---|---|\n")
        for r in rows:
            f.write(f"| {r['name']} | M/{1 / r['h_f']:.0f} | {r['outer']:g} | {r['sub'] ** 3} | {r['n_root']}^3 | {r['block']}^3 | "
                    f"{r['leaf_blocks']} | {r['leaf_cells'] / 1e6:.2f}e6 | {r['particles'] / 1e6:.3f}e6 | {r['steps']} | "
                    f"{r['mem_GiB']:.1f} | {r['s_per_step']:.3f} | {r['card_hours']:.3f} |\n")
    print(open(os.path.join(a.out, "design_table.md")).read())
    for k, v in res.items():
        if k.startswith("ball") or k == "data_set_3":
            print(k, {kk: vv for kk, vv in v.items() if kk != "spec"})
    print("BH-1R model check: memory", rows[-1]["model_mem_GiB"], "GiB (measured", rows[-1]["mem_GiB"], "), s/step",
          rows[-1]["model_s_per_step"], "(measured 1.7187)")

    # ------------------------------------------------------------ figure
    pr = C.load_json(os.path.join(a.probe, "geometry_numbers.json"))
    from nrpic import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(8.0, 3.5))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.15, top=0.90, wspace=0.30)
    ax = fig.add_subplot(1, 2, 1)
    rr = np.linspace(0.0, 16.0, 3201)

    def hof(levels, r):
        h = np.full_like(r, levels[0][1])
        for b, hl in levels:
            h = np.where(r < b, hl, h)
        return h
    cols = [fs.PAL["blue"], fs.PAL["red"], fs.PAL["yellow"] if "yellow" in fs.PAL else "orange"]
    for c_, nm in zip(cols, ("A", "B", "C")):
        r_ = next(x for x in rows if x["name"] == nm)
        ax.step(rr, hof(r_["levels"], rr), where="post", color=c_, lw=1.5, label=f"{nm}: finest M/{1 / r_['h_f']:.0f}")
    ax.step(rr, hof([[16.0, 0.125], [4.0, 0.0625]], rr), where="post", color="k", lw=1.0, ls=":", label="BH-1R")
    ax.axvline(rm3, **fs.MASK_LINE)
    ax.set_yscale("log", base=2)
    ax.set_xscale("log")
    ax.set_xlim(0.1, 16)
    ax.set_xlabel(r"coordinate radius along an axis $/M$")
    ax.set_ylabel(r"cell width $/M$")
    ax.legend(fontsize=7, loc="upper left")
    ax.set_title("level structure (grey: matter edge at t = 0)", fontsize=9)
    ax = fig.add_subplot(1, 2, 2)
    names = sorted(pr["groups"], key=lambda s: float(s[1:]))
    gc = fs.series_colors(len(names), "viridis")
    for c_, g in zip(gc, names):
        d = pr["groups"][g]["at"]
        ts = [v["t"] for v in d.values()]
        rs = [v["r_median"] for v in d.values()]
        ax.plot(ts, rs, "o-", color=c_, ms=3, lw=1.0, label=f"$R_i={float(g[1:]):.2f}$")
    for b in (1.0, 2.0, 4.0, 8.0):
        ax.axhline(b, **fs.GUIDE)
    if "finder" in pr:
        ax.axvline(pr["finder"]["first_t"], **fs.MASK_LINE)
    ax.set_yscale("log")
    ax.set_xlabel(r"$t\,/M$ (BH-1R)")
    ax.set_ylabel(r"coordinate radius $/M$")
    ax.set_title("BH-1R shells against the level boxes (dashed)", fontsize=9)
    ax.legend(fontsize=5.5, ncol=2, loc="lower left")
    fs.save(fig, os.path.join(a.out, "fig_design"))


if __name__ == "__main__":
    main()
