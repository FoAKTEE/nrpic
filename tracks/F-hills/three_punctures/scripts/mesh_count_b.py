#!/usr/bin/env python3
"""T3b: MeshBlock count of the three-black-hole mesh with the wave zone refined by the
corner rule of the z4c_amr radius criterion (athenak/src/z4c/z4c_amr.cpp lines 348-366:
a block on a level below reflevel is refined when one of its eight corners lies inside
the radius about the origin), on two domains, two puncture radii and two finest cells,
at the start state and along the Newtonian passage; and the card-hours of one passage.

Puncture regions as `puncture_setup` writes them (cube of half-width radius*m at level
L_f - round(log2(m/m_min))), validated in T3 against core's 1100 MeshBlocks.
The radius criterion is emulated by refining, level by level from the root, every
existing block that has a corner inside the radius: each such block becomes a
<refined_region> equal to its own extent (shrunk by 1e-6 of its width) at the next
level; the tree builder of AthenaK adds the 2:1 padding.

Cost of one passage: sum over the track of N(t) * dt_track / (cfl * h_fine) MeshBlock
cycles, divided by the measured vacuum rate (MeshBlock-cycles per second on one A100):
2201 median, 2022 to 2310 (novelty run F-hills-20261115-045438-f62d553); core's
three-black-hole card run 2140 (8.8e6 zone-cycles/s / 4096).
Usage: python3 mesh_count_b.py <newton_start.json> <outdir>
"""
import itertools
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

ARGS = sys.argv[1:]
DOM = None          # --dom NAME HALF NROOT LFINE_M8 LEVEL_WZ: one domain, wave zone level given
while ARGS and ARGS[0].startswith("--"):
    if ARGS[0] == "--dom":
        DOM = (ARGS[1], float(ARGS[2]), int(ARGS[3]), int(ARGS[4]), int(ARGS[5]))
        ARGS = ARGS[6:]
    else:
        raise SystemExit(f"unknown option {ARGS[0]}")
NEWTON, OUT = ARGS[0], ARGS[1]
FIG = os.path.join(WT, "tracks/F-hills/three_punctures/figures")
CFL = 0.25
RATE = {"median": 2201.0, "slow": 2022.0, "fast": 2310.0}
T_PASS = 250.0     # start (4 r_t, 79.5 M before the pericentre) to 170 M after it


def athinput(half, nroot, nlev, regions, path):
    lines = ["<job>", "basename = mesh", "<mesh>", "nghost = 4"]
    for a in (1, 2, 3):
        lines += [f"nx{a} = {nroot}", f"x{a}min = {-half}", f"x{a}max = {half}",
                  f"ix{a}_bc = outflow", f"ox{a}_bc = outflow"]
    lines += ["<meshblock>", "nx1 = 16", "nx2 = 16", "nx3 = 16",
              "<mesh_refinement>", "refinement = adaptive", f"num_levels = {nlev}",
              "max_nmb_per_rank = 1000000",
              "<time>", "evolution = dynamic", "integrator = rk4", f"cfl_number = {CFL}",
              "tlim = 1.0"]
    for name, lev, lo, hi in regions:
        lines += [f"<refined_region_{name}>", f"level = {lev}"]
        for a in range(3):
            lines += [f"x{a+1}min = {lo[a]:.12g}", f"x{a+1}max = {hi[a]:.12g}"]
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


def count(case, half, nroot, nlev, regions):
    d = os.path.join(OUT, "cases", case)
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
        os.remove(ms)
    if tot is None:
        raise RuntimeError(f"{case}: no count\n{p.stdout}\n{p.stderr}")
    return int(tot.group(1)), {int(a): int(b) for a, b in per}


def puncture_regions(pos, masses, lfine, rfac):
    mmin = min(masses)
    regs = []
    for n, (x, m) in enumerate(zip(pos, masses)):
        lev = max(lfine - int(round(math.log2(m / mmin))), 0)
        r = rfac * m
        regs.append((f"punc{n}", lev, [x[a] - r for a in range(3)], [x[a] + r for a in range(3)]))
    return regs


def sphere_regions(half, nroot, shells):
    """Corner rule of the radius criterion, iterated from the root: returns refined
    regions (one per refined block). shells: list of (radius, reflevel)."""
    w0 = 2 * half / (nroot // 16)            # root block width
    nb = nroot // 16
    blocks = [(0, (i, j, k)) for i in range(nb) for j in range(nb) for k in range(nb)]
    regs = []
    lmax = max(l for _, l in shells)
    for lev in range(lmax):
        w = w0 / 2 ** lev
        nxt = []
        for (l, (i, j, k)) in blocks:
            lo = np.array([-half + i * w, -half + j * w, -half + k * w])
            hi = lo + w
            cs = np.array(list(itertools.product(*zip(lo, hi))))
            rmin = np.sqrt((cs ** 2).sum(axis=1)).min()
            if any(rmin < R and lev < L for R, L in shells):
                eps = 1e-6 * w
                regs.append((f"wz{len(regs)}", lev + 1, list(lo + eps), list(hi - eps)))
                for di, dj, dk in itertools.product((0, 1), repeat=3):
                    nxt.append((lev + 1, (2 * i + di, 2 * j + dj, 2 * k + dk)))
        blocks = nxt
    return regs


def main():
    os.makedirs(OUT, exist_ok=True)
    nw = json.load(open(NEWTON))["choice"]
    m = nw["masses"]
    order = [1, 2, 0]                         # punctures m1, m2, M
    ms = [m[k] for k in order]
    x0 = [nw["from10"]["positions"][k] for k in order]
    tr = nw["track"]
    t = np.array(tr["t"])
    X = np.array(tr["x"])
    sel = np.arange(0, t.size, 5)            # every 10 M
    # domains: (name, half width, root cells, finest level for m/8)
    doms = {"D409": (409.6, 64, 11, 3), "D205": (204.8, 64, 10, 2)}
    tracked = {"D205"}
    if DOM is not None:
        doms = {DOM[0]: DOM[1:]}
        tracked = {DOM[0]}
    mlight = min(ms)
    res = {"exe": EXE, "rate_MB_cycles_per_s": RATE, "cfl": CFL, "T_pass": T_PASS,
           "cases": {}, "tracks": {}}
    for dname, (half, nroot, l8, lwz) in doms.items():
        h0 = 2 * half / nroot                  # lwz: level of the inner wave zone
        shells = [(48.0, lwz), (100.0, lwz - 1)]
        wz = sphere_regions(half, nroot, shells)
        for dl, rfac in itertools.product((0, 1), (1.8, 1.2)):
            lf = l8 + dl
            hf = h0 / 2 ** lf
            if dname not in tracked and rfac == 1.2:
                continue
            regs = puncture_regions(x0, ms, lf, rfac)
            key = f"{dname}_m{round(mlight / hf)}_r{rfac}"
            n0, per0 = count(key + "_nowz", half, nroot, lf + 1, regs)
            n1, per1 = count(key + "_wz", half, nroot, lf + 1, regs + wz)
            res["cases"][key] = dict(h_fine=hf, cells_per_m=mlight / hf, total_nowz=n0,
                                     total_wz=n1, per_level_nowz=per0, per_level_wz=per1,
                                     n_wz_regions=len(wz))
            print(f"{key}: no wave zone {n0}, wave zone {n1}  {per1}")
            if dname in tracked:
                rows = []
                for i in sel:
                    p = [X[i, k] for k in order]
                    n, _ = count(f"{key}_t{t[i]:+07.1f}", half, nroot, lf + 1,
                                 puncture_regions(p, ms, lf, rfac) + wz)
                    rows.append((float(t[i]), n))
                tt = np.array([r[0] for r in rows])
                nn = np.array([r[1] for r in rows], dtype=float)
                # MeshBlock-cycles of the passage (trapezoid in time, tracked span)
                mbc = np.trapezoid(nn, tt) / (CFL * hf)
                span = tt[-1] - tt[0]
                hours = {k: mbc / v / 3600.0 for k, v in RATE.items()}
                res["tracks"][key] = dict(t=tt.tolist(), n=nn.tolist(), span=span,
                                          n_max=int(nn.max()), n_mean=float(nn.mean()),
                                          cycles=span / (CFL * hf), card_hours=hours)
                print(f"   track: max {nn.max():.0f} mean {nn.mean():.0f} over {span:.0f} M, "
                      f"{span / (CFL * hf):.0f} cycles, card-hours {hours}")
    with open(os.path.join(OUT, "mesh_count_b.json"), "w") as f:
        json.dump(res, f, indent=1)

    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.3))
    ax = fig.add_axes([0.08, 0.15, 0.40, 0.80])
    keys = list(res["cases"])
    cols = fs.series_colors(len(keys))
    for k, key in enumerate(keys):
        per = res["cases"][key]["per_level_wz"]
        lv = sorted(per)
        ax.plot(lv, [per[q] for q in lv], "o-", ms=3, color=cols[k],
                label=f"{key} ({res['cases'][key]['total_wz']})")
    ax.set_xlabel("refinement level")
    ax.set_ylabel("MeshBlocks on the level")
    ax.set_yscale("log")
    ax.legend(loc="upper left", fontsize=7, ncol=1)
    ax2 = fig.add_axes([0.58, 0.15, 0.40, 0.80])
    tk = list(res["tracks"])
    cols = fs.series_colors(len(tk))
    for k, key in enumerate(tk):
        r = res["tracks"][key]
        ax2.plot(r["t"], r["n"], "o-", ms=3, color=cols[k],
                 label=f"{key}: {r['card_hours']['median']:.0f} card-h")
    ax2.axvline(0.0, **fs.MASK_LINE)
    ax2.axhline(2400, **fs.GUIDE)
    ax2.set_yscale("log")
    ax2.set_xlabel(r"$t - t_{\rm peri}$ [M] (Newtonian positions)")
    ax2.set_ylabel("MeshBlocks")
    ax2.legend(loc="upper left", fontsize=7)
    for pth in fs.save(fig, os.path.join(OUT, "fig_mesh_count_b" + ("" if DOM is None else "_" + DOM[0]))):
        if pth.endswith(".png"):
            shutil.copy(pth, FIG)


if __name__ == "__main__":
    main()
