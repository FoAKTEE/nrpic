#!/usr/bin/env python3
"""Test T4 (processor part) of tracks/core/JOURNAL-scalar2.md: the 32^3 slow-roll case
from the initial slice for 20 steps with 1, 8 and 64 MeshBlocks and through a restart at
cycle 10.  Dumps at cycles 0, 10 and 20 (layout NRSFDMP2 with the metric and the
constraints).

    python3 t7_layout.py --exe EXE --out DIR [--card-run DIR2/card32]

Compares the fields of the dumps bit by bit between the layouts, the dump files byte by
byte between the restarted and the uninterrupted run and, with --card-run, every field
of the one-MeshBlock run with the same run on a card.  Writes DIR/summary.json and, with
--card-run, DIR/fig_card.png."""
import argparse
import filecmp
import glob
import os

import common
from common import np
from nrpic import scalar_field as sf

INP = os.path.join(common.PROB, "sr_stochastic.athinput")
MODES = os.path.join(common.PROB, "sr_stochastic_modes.txt")


def dumps(rundir):
    out = {}
    for f in sorted(glob.glob(os.path.join(rundir, "sr.sf.?????.dump"))):
        d = sf.read_dump(f)
        out[int(d["cycle"])] = (f, d)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--card-run")
    ap.add_argument("--analyse-only", action="store_true")
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    exe = os.path.abspath(a.exe)
    # the example input with a restart file every 10 cycles
    inp = os.path.join(out, "sr_rst.athinput")
    with open(inp, "w") as fp:
        fp.write(open(INP).read() + "\n<output1>\nfile_type  = rst\ndcycle     = 10\n")
    args = [f"scalar_field/noise_mode_file={MODES}", "time/nlim=20",
            "scalar_field/dump_dt=0.49", "scalar_field/dump_noise=false"]
    summ = dict(exe=exe)
    if not a.analyse_only:
        cases = [(os.path.join(out, f"mb{b}"), inp, args + common.mesh_args(32, b))
                 for b in (32, 16, 8)]
        walls = common.run_many(exe, cases, 3)
        rst = sorted(glob.glob(os.path.join(out, "mb16", "rst", "*.00001.rst")))[0]
        walls.append(common.run_case(exe, os.path.join(out, "mb16_rst"), rst, []))
        summ["wall_s"] = walls
    d = {k: dumps(os.path.join(out, k)) for k in ("mb32", "mb16", "mb8", "mb16_rst")}
    summ["dump_cycles"] = {k: sorted(v) for k, v in d.items()}

    # ---- layouts: fields bit by bit
    lay = {}
    for other in ("mb16", "mb8"):
        worst = 0.0
        nvar = 0
        for c in sorted(d["mb32"]):
            fa, fb = d["mb32"][c][1]["fields"], d[other][c][1]["fields"]
            for name in fa:
                worst = max(worst, float(np.abs(fa[name] - fb[name]).max()))
                nvar += 1
        lay[other] = dict(fields_compared=nvar, max_abs_difference=worst,
                          bit_identical=bool(worst == 0.0))
    summ["layouts_vs_one_meshblock"] = lay
    # ---- restart: files byte by byte (cycle 20; the restarted run numbers its dumps on)
    rs = {}
    for c in sorted(d["mb16_rst"]):
        rs[c] = bool(filecmp.cmp(d["mb16"][c][0], d["mb16_rst"][c][0], shallow=False))
    summ["restart_dump_files_identical"] = rs
    # histories of the layouts: largest relative difference of a column
    h1 = np.loadtxt(os.path.join(out, "mb32", "sr.sf.con.hst"))
    h8 = np.loadtxt(os.path.join(out, "mb16", "sr.sf.con.hst"))
    with np.errstate(divide="ignore", invalid="ignore"):
        rel = np.abs(h8 - h1)/np.abs(h1)
    summ["con_history_layout_max_rel_diff"] = float(np.nanmax(rel[:, 2:]))

    # ---- card against processors
    if a.card_run:
        dc = dumps(os.path.abspath(a.card_run))
        card = {}
        curves = {}
        for c in sorted(d["mb32"]):
            fa, fb = d["mb32"][c][1]["fields"], dc[c][1]["fields"]
            row = {}
            for name in fa:
                diff = float(np.abs(fa[name] - fb[name]).max())
                scale = float(np.abs(fa[name]).max())
                row[name] = dict(max_abs_diff=diff, max_abs=scale,
                                 rel=diff/scale if scale > 0.0 else 0.0)
            card[c] = row
            curves[c] = row
        summ["card_vs_processor"] = card
        hc = np.loadtxt(os.path.join(os.path.abspath(a.card_run), "sr.sf.con.hst"))
        with np.errstate(divide="ignore", invalid="ignore"):
            rel = np.abs(hc - h1)/np.abs(h1)
        names = sf.CON_HIST_VARS
        summ["card_con_history_max_rel_diff"] = {names[i]: float(np.nanmax(rel[:, i]))
                                                 for i in range(2, len(names))}
        hp = np.loadtxt(os.path.join(out, "mb32", "sr.sf.hst"))
        hg = np.loadtxt(os.path.join(os.path.abspath(a.card_run), "sr.sf.hst"))
        with np.errstate(divide="ignore", invalid="ignore"):
            rel = np.abs(hg - hp)/np.abs(hp)
        summ["card_history_means_max_rel_diff"] = float(np.nanmax(rel[:, 2:7]))
        fs = common.style()
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(1, 1, figsize=(fs.FULL_WIDTH, 3.6))
        fig.subplots_adjust(left=0.09, right=0.985, bottom=0.2, top=0.96)
        names_f = list(card[sorted(card)[0]])
        x = np.arange(len(names_f))
        for c, cl in zip(sorted(card), fs.SERIES):
            y = [max(card[c][n]["max_abs_diff"], 1e-30) for n in names_f]
            ax.plot(x, y, "o", ms=4, color=cl, label=f"cycle {c}: |card - processor|")
            ys = [max(card[c][n]["max_abs"], 1e-30) for n in names_f]
            ax.plot(x, ys, "_", ms=9, color=cl, alpha=0.5)
        ax.set_yscale("log")
        ax.set_xticks(x)
        ax.set_xticklabels(names_f, rotation=60, fontsize=8)
        ax.tick_params(axis="x", which="minor", bottom=False, top=False)
        ax.set_ylabel("largest difference (dots), largest value (bars)")
        ax.legend(loc="center right", fontsize=8)
        fig.savefig(os.path.join(out, "fig_card.png"), dpi=200)
    common.dump_json(summ, os.path.join(out, "summary.json"))
    print("layout test done:", os.path.join(out, "summary.json"))


if __name__ == "__main__":
    main()
