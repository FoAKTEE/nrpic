#!/usr/bin/env python3
"""Step 4 of drift_controls (risk R9): MeshBlock counts of the ES mesh at M/8, M/16, M/32
and of its +-384 M variants, from AthenaK's own tree (athena -i <deck> -m 1), and the
card-hours of a 200 M run from the measured rates of ES-1 and V-1.

    python3 count_blocks.py --out DIR [--exe PATH]

Decks are derived from tracks/D-bh-dress/es_runs/inputs/v1_dx8.athinput (the ES mesh:
24^3 MeshBlocks, root dx = 4 M on +-192 M, region of the finest level +-1.5 M, which with
24-cell blocks gives M/8 on +-6 M). Variants (finest level and the region it is asked on;
region bounds sit 0.1 M inside block faces as in the ES decks):
  M8        as V-1 (finest M/8 on +-6 M)
  M16       + one level on +-1.5 M      (M/16 on +-3 M)
  M32s      + two levels, the last on +-1.4 M (M/32 on +-1.5 M: the horizon, r = 2.2-2.6 M,
            is then on M/16)
  M32h      + two levels, the last on +-2.9 M (M/32 on +-3 M: the horizon on M/32)
  B384_*    the same with one coarser root level (dx = 8 M on +-384 M), as card run (b)
Cost model [JUDGEMENT]: one global time step dt = 0.25 dx_min (cfl_number = 0.25,
z4c_newdt.cpp), cycles(200 M) = 200 / dt; card-hours = a * blocks * cycles + b * cycles,
a from V-1 (0.672 card-hours, 344 blocks, 6400 cycles; 140 tracers only) and b, the
particle term of ES-1 (696688 dust particles), from ES-1 - V-1 (0.769 - 0.672 card-hours
over 6400 cycles). Run ids of the rates: D-20261115-172726-60ba4c2, D-20261115-172730-c6d151b
(manifests after nrpic-run finish).

Writes DIR/<variant>/deck.athinput, DIR/<variant>/athena_m.log, DIR/count_blocks.json,
DIR/cost_table.md, and the figure DIR/figs/cost_blocks.png|pdf.
"""
import argparse
import json
import os
import re
import subprocess
import sys

WT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "python"))
from nrpic import figstyle  # noqa: E402

BASE = os.path.join(WT, "tracks", "D-bh-dress", "es_runs", "inputs", "v1_dx8.athinput")
EXE = "/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena"
RATE_V1 = (0.672, 344, 6400)       # card-hours, blocks, cycles (V-1)
RATE_ES1 = 0.769                   # card-hours (ES-1, same mesh and cycles)


def region(n, level, h):
    return (f"<refined_region{n}>\nlevel = {level}\n" +
            "".join(f"x{a}min = {-h}\nx{a}max = {h}\n" for a in (1, 2, 3)) + "\n")


def deck(base_txt, outer384, extra):
    """extra: list of (level above V-1's finest, half width) for added fine regions."""
    txt = base_txt
    start, stop = txt.index("<refined_region1>"), txt.index("<time>")
    shift = 1 if outer384 else 0
    regs = []
    if outer384:
        for a in ("1", "2", "3"):
            txt = txt.replace(f"x{a}min     = -192.0\n", f"x{a}min     = -384.0\n")
            txt = txt.replace(f"x{a}max     = 192.0\n", f"x{a}max     = 384.0\n")
        regs.append((1, 191.9))
    regs += [(1 + shift, 95.9), (2 + shift, 47.9), (5 + shift, 1.5)]
    for dl, h in extra:
        regs.append((5 + shift + dl, h))
    start, stop = txt.index("<refined_region1>"), txt.index("<time>")
    body = "".join(region(i + 1, L, h) for i, (L, h) in enumerate(regs))
    return txt[:start] + body + txt[stop:], max(L for L, _ in regs)


VARIANTS = {
    "M8": (False, []),
    "M16": (False, [(1, 1.5)]),
    "M32s": (False, [(1, 1.5), (2, 1.4)]),
    "M32h": (False, [(1, 2.9), (2, 2.9)]),
    "B384_M8": (True, []),
    "B384_M16": (True, [(1, 1.5)]),
    "B384_M32s": (True, [(1, 1.5), (2, 1.4)]),
    "B384_M32h": (True, [(1, 2.9), (2, 2.9)]),
}


def parse_m(log):
    out = {"total": None, "per_level": {}}
    m = re.search(r"Total number of MeshBlocks = (\d+)", log)
    if m:
        out["total"] = int(m.group(1))
    for m in re.finditer(r"Physical level = (\d+) \(logical level = \d+\): (\d+) MeshBlocks", log):
        out["per_level"][int(m.group(1))] = int(m.group(2))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--exe", default=EXE)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    base_txt = open(BASE).read()
    ch_v1, nb_v1, cyc_v1 = RATE_V1
    A = ch_v1 / (nb_v1 * cyc_v1)                    # card-hours per block-cycle
    B = (RATE_ES1 - ch_v1) / cyc_v1                 # card-hours per cycle, ES-1 particles
    res = {"rate_block_cycle": A, "rate_particles_cycle": B, "variants": {}}
    for name, (o384, extra) in VARIANTS.items():
        d = os.path.join(a.out, name)
        os.makedirs(d, exist_ok=True)
        txt, finest = deck(base_txt, o384, extra)
        p = os.path.join(d, "deck.athinput")
        with open(p, "w") as f:
            f.write(txt)
        r = subprocess.run([a.exe, "-i", p, "-m", "1"], cwd=d, capture_output=True, text=True)
        log = r.stdout + r.stderr
        open(os.path.join(d, "athena_m.log"), "w").write(log)
        cnt = parse_m(log)
        root_dx = 8.0 if o384 else 4.0
        dx_min = root_dx / 2 ** max(cnt["per_level"]) if cnt["per_level"] else None
        cycles = 200.0 / (0.25 * dx_min) if dx_min else None
        rec = dict(outer=384 if o384 else 192, finest_level=finest, dx_min=dx_min,
                   blocks=cnt["total"], per_level=cnt["per_level"], cycles_200M=cycles,
                   card_hours_vacuum=A * cnt["total"] * cycles if cycles else None,
                   card_hours_es=(A * cnt["total"] + B) * cycles if cycles else None,
                   exit=r.returncode)
        res["variants"][name] = rec
        print(f"{name:10s} outer {rec['outer']} dx_min {dx_min} blocks {rec['blocks']} "
              f"per level {rec['per_level']} cycles {cycles:.0f} vacuum "
              f"{rec['card_hours_vacuum']:.2f} ES {rec['card_hours_es']:.2f} card-h")
    with open(os.path.join(a.out, "count_blocks.json"), "w") as f:
        json.dump(res, f, indent=1)
    lines = ["| variant | outer faces | dx_min | MeshBlocks (per physical level) | cycles for 200 M "
             "| card-hours V-1 type (vacuum) | card-hours ES type (696688 particles) |",
             "|---|---|---|---|---|---|---|"]
    for name, r in res["variants"].items():
        pl = ", ".join(str(r["per_level"][k]) for k in sorted(r["per_level"]))
        lines.append(f"| {name} | +-{r['outer']} M | M/{int(round(1 / r['dx_min']))} | "
                     f"{r['blocks']} ({pl}) | {r['cycles_200M']:.0f} | "
                     f"{r['card_hours_vacuum']:.2f} | {r['card_hours_es']:.2f} |")
    open(os.path.join(a.out, "cost_table.md"), "w").write("\n".join(lines) + "\n")
    # figure
    figstyle.use_style()
    import matplotlib.pyplot as plt
    fd = os.path.join(a.out, "figs")
    os.makedirs(fd, exist_ok=True)
    fig, axs = plt.subplots(1, 2, figsize=(figstyle.FULL_WIDTH, 3.4))
    fig.subplots_adjust(left=0.09, right=0.98, top=0.92, bottom=0.15, wspace=0.28)
    for o384, col, lab in ((False, figstyle.PAL["blue"], "faces at +-192 M"),
                           (True, figstyle.PAL["red"], "faces at +-384 M")):
        for kind, mk in (("s", "o"), ("h", "s")):
            xs, nb, ch = [], [], []
            for name, r in res["variants"].items():
                if (r["outer"] == 384) != o384:
                    continue
                if name.endswith("M32s") and kind == "h":
                    continue
                if name.endswith("M32h") and kind == "s":
                    continue
                xs.append(1 / r["dx_min"])
                nb.append(r["blocks"])
                ch.append(r["card_hours_es"])
            o = sorted(range(len(xs)), key=lambda i: xs[i])
            xs = [xs[i] for i in o]
            nb = [nb[i] for i in o]
            ch = [ch[i] for i in o]
            ls = "-" if kind == "s" else "--"
            axs[0].plot(xs, nb, color=col, marker=mk, ls=ls,
                        label=f"{lab}, M/32 on {'1.5' if kind == 's' else '3'} M")
            axs[1].plot(xs, ch, color=col, marker=mk, ls=ls)
    for ax in axs:
        ax.set_xscale("log", base=2)
        ax.set_yscale("log")
        ax.set_xlabel(r"$M/\Delta x_{\min}$")
    axs[0].set_ylabel("MeshBlocks ($24^3$ cells)")
    axs[1].set_ylabel("card-hours for 200 M (ES type)")
    axs[0].legend(fontsize=7)
    figstyle.save(fig, os.path.join(fd, "cost_blocks"))
    plt.close(fig)


if __name__ == "__main__":
    main()
