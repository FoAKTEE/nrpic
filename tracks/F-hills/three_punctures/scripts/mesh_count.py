#!/usr/bin/env python3
"""T3: MeshBlock count of the three-black-hole mesh, without evolution.

Writes AthenaK inputs that contain only the mesh (no physics) and the refined regions
that `puncture_setup` of branch core/multi-puncture would write
(athenak/src/pgen/nrpic/nrpic_puncture_setup.hpp lines 115-141 there: a cube of
half-width radius = puncture_radius * m around each puncture at level
puncture_level - round(log2(m / m_min))), plus optional cubes for the wave zone, and runs
the processor executable of main with -m (build the tree, print the count per level,
exit). Cases:
  A  core's by_triple.athinput at t = 0 (validation: core reports 1100 MeshBlocks);
  B  the first configuration at its start state, finest cells m/8, m/16, m/32 at the
     light holes, with and without the wave zone;
  C  the same at m/8 (and m/16) with the wave zone, the three punctures placed at their
     Newtonian positions along the passage (every 10 M), for the block count against time.
Usage: python3 mesh_count.py <newton_start.json> <outdir>
"""
import json
import math
import os
import re
import shutil
import subprocess
import sys

import numpy as np

WT = "/data/haiyangw/nrpic/wt/F-hills"
EXE = "/data/haiyangw/nrpic/.work/build_cpu_c1/src/athena"
sys.path.insert(0, os.path.join(WT, "python"))
from nrpic import figstyle as fs  # noqa: E402

NEWTON, OUT = sys.argv[1], sys.argv[2]
FIG = os.path.join(WT, "tracks/F-hills/three_punctures/figures")


def athinput(half, nroot, nlev, regions, path):
    lines = ["<job>", "basename = mesh", "<mesh>", "nghost = 4"]
    for a in (1, 2, 3):
        lines += [f"nx{a} = {nroot}", f"x{a}min = {-half}", f"x{a}max = {half}",
                  f"ix{a}_bc = outflow", f"ox{a}_bc = outflow"]
    lines += ["<meshblock>", "nx1 = 16", "nx2 = 16", "nx3 = 16",
              "<mesh_refinement>", "refinement = adaptive", f"num_levels = {nlev}",
              "max_nmb_per_rank = 1000000",
              "<time>", "evolution = dynamic", "integrator = rk4", "cfl_number = 0.25",
              "tlim = 1.0"]
    for k, (name, lev, c, r) in enumerate(regions):
        lines += [f"<refined_region_{name}>", f"level = {lev}"]
        for a in range(3):
            lines += [f"x{a+1}min = {c[a] - r:.10g}", f"x{a+1}max = {c[a] + r:.10g}"]
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


def count(case, half, nroot, nlev, regions):
    d = os.path.join(OUT, case)
    os.makedirs(d, exist_ok=True)
    inp = os.path.join(d, "mesh.athinput")
    athinput(half, nroot, nlev, regions, inp)
    p = subprocess.run([EXE, "-i", inp, "-m"], cwd=d, capture_output=True, text=True)
    with open(os.path.join(d, "stdout.txt"), "w") as f:
        f.write(p.stdout + p.stderr)
    tot = re.search(r"Total number of MeshBlocks = (\d+)", p.stdout)
    per = re.findall(r"Physical level = (\d+) \(logical level = \d+\): (\d+) MeshBlocks", p.stdout)
    ms = os.path.join(d, "mesh_structure.dat")
    if os.path.exists(ms):
        os.remove(ms)       # large and not needed: the counts are in stdout.txt
    if tot is None:
        raise RuntimeError(f"{case}: no count\n{p.stdout}\n{p.stderr}")
    return int(tot.group(1)), {int(a): int(b) for a, b in per}


def puncture_regions(pos, masses, lfine, rfac):
    mmin = min(masses)
    regs = []
    for n, (x, m) in enumerate(zip(pos, masses)):
        lev = max(lfine - int(round(math.log2(m / mmin))), 0)
        regs.append((f"punc{n}", lev, x, rfac * m))
    return regs


def wave_zone(l_inner, r_inner, l_outer, r_outer):
    return [("wz_in", l_inner, (0.0, 0.0, 0.0), r_inner),
            ("wz_out", l_outer, (0.0, 0.0, 0.0), r_outer)]


def main():
    os.makedirs(OUT, exist_ok=True)
    res = {"exe": EXE, "cases": {}}

    # ---- A: core's by_triple at t = 0 (domain +-256, 64^3, 8 levels, puncture_radius 1.8)
    pos = [(-88.0, 5.0, 0.0), (-88.0, -5.0, 0.0), (8.0, 0.0, 0.0)]
    regs = puncture_regions(pos, [0.5, 0.5, 10.0], 7, 1.8)
    n, per = count("A_by_triple", 256.0, 64, 8, regs)
    res["cases"]["A_by_triple"] = dict(total=n, per_level=per, regions=regs)
    print("A by_triple:", n, per)

    # ---- B: first configuration at its start state
    nw = json.load(open(NEWTON))["choice"]
    m = nw["masses"]                      # [M, m1, m2]
    x0 = nw["from10"]["positions"]
    half, nroot, h0 = 409.6, 64, 12.8     # root cells 12.8: level 11 = 0.00625 = m/8
    order = [1, 2, 0]                      # puncture order: m1, m2, M
    pos0 = [x0[k] for k in order]
    ms = [m[k] for k in order]
    WZ = wave_zone(3, 64.0, 2, 128.0)     # cells 1.6 within 64, 3.2 within 128 (cubes)
    for lf in (11, 12, 13):
        regs = puncture_regions(pos0, ms, lf, 1.8)
        for wz in (False, True):
            if wz and lf != 11:
                continue
            case = f"B_start_L{lf}" + ("_wz" if wz else "")
            n, per = count(case, half, nroot, lf + 1, regs + (WZ if wz else []))
            res["cases"][case] = dict(total=n, per_level=per, h_fine=h0 / 2 ** lf,
                                      cells_per_m=0.05 / (h0 / 2 ** lf), regions=regs)
            print(case, n, per)

    # ---- C: along the Newtonian passage, every 10 M
    tr = nw["track"]
    t = np.array(tr["t"])
    X = np.array(tr["x"])                 # (nt, 3 bodies [M, m1, m2], 3)
    sel = np.arange(0, t.size, 5)          # samples every 2 M -> every 10 M
    for lf in (11, 12):
        rows = []
        for i in sel:
            p = [X[i, k] for k in order]
            regs = puncture_regions(p, ms, lf, 1.8)
            n, per = count(f"C_L{lf}_t{t[i]:+07.1f}", half, nroot, lf + 1, regs + WZ)
            rows.append(dict(t=float(t[i]), total=n, per_level=per))
        res["cases"][f"C_track_L{lf}"] = rows
        print(f"C L{lf}:", [(round(r['t']), r['total']) for r in rows])

    with open(os.path.join(OUT, "mesh_count.json"), "w") as f:
        json.dump(res, f, indent=1)

    # ---- figure
    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.3))
    ax = fig.add_axes([0.08, 0.15, 0.40, 0.80])
    cols = fs.series_colors(5)
    for k, case in enumerate(["A_by_triple", "B_start_L11", "B_start_L11_wz", "B_start_L12",
                              "B_start_L13"]):
        per = res["cases"][case]["per_level"]
        lv = sorted(per)
        ax.plot(lv, [per[q] for q in lv], "o-", ms=3, color=cols[k],
                label=f"{case} ({res['cases'][case]['total']})")
    ax.set_xlabel("refinement level")
    ax.set_ylabel("MeshBlocks on the level")
    ax.set_yscale("log")
    ax.legend(loc="upper right", fontsize=7)
    ax2 = fig.add_axes([0.58, 0.15, 0.40, 0.80])
    for k, lf in enumerate((11, 12)):
        rows = res["cases"][f"C_track_L{lf}"]
        ax2.plot([r["t"] for r in rows], [r["total"] for r in rows], "o-", ms=3,
                 color=fs.SERIES[k], label=f"finest m/{0.05 / (h0 / 2 ** lf):.0f}, wave zone")
    ax2.axvline(0.0, **fs.MASK_LINE)
    ax2.axhline(2400, **fs.GUIDE)
    ax2.text(-70, 2440, "card limit (core: 2400)", fontsize=8)
    ax2.set_xlabel(r"$t - t_{\rm peri}$ [M] (Newtonian positions)")
    ax2.set_ylabel("MeshBlocks (t = 0 rule)")
    ax2.legend(loc="lower right", fontsize=8)
    for pth in fs.save(fig, os.path.join(OUT, "fig_mesh_count")):
        if pth.endswith(".png"):
            shutil.copy(pth, FIG)


if __name__ == "__main__":
    main()
