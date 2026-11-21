#!/usr/bin/env python3
"""T9: amplitude scan of the oblique linear wave on processors at N = 32 (prediction P11
of tracks/core/JOURNAL-bfix.md): is the non-TT part of second order in A (R2), and is the
floor of Psi_4 rounding that grows as N^2/A (R1)? A = 1e-6 is read from the evol stage of
T1 (--t1 DIR).

    python3 t9_amp_cpu.py --exe EXE --t1 DIR [--out DIR]
"""
import argparse
import glob
import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import bfix_common as bc  # noqa: E402
from bfix_common import fs  # noqa: E402
import t1_linear_wave as t1  # noqa: E402
from t8_analysis import second_order_fields  # noqa: E402

K = (1, 1, 1)
N = 32
AMPS = ("1e-09", "1e-08", "1e-07", "1e-05")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--t1", required=True)
    ap.add_argument("--bdir", default=bc.B_DEFAULT)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = bc.out_dir(a.out)
    B = bc.track_b(a.bdir)
    jobs = {f"amp{s}": (os.path.abspath(a.exe), t1.INP, os.path.join(out, f"N{N}_a{s}"),
                        bc.mesh_overrides(N) + [f"problem/amp={s}"]) for s in AMPS}
    recs = bc.run_many(jobs, len(AMPS))
    rows = {}
    with open(os.path.join(a.t1, "results_t1.json")) as f:
        r1 = json.load(f)["evol"][str(N)]
    l6 = dict(r1["last"])
    l6["gain_phase"] = -l6["gain_phase"]      # T1 stored exact minus numerical (journal)
    l6.update(second_order_fields(sorted(glob.glob(
        os.path.join(a.t1, "evol", f"N{N}", "bin", "*.z4c.*.bin")))[-1]))
    rows["1e-06"] = {"last": l6, "pred_gain_abs_minus_1": r1["pred_gain_abs_minus_1"],
                     "pred_gain_phase": r1["pred_gain_phase"], "source": "T1"}
    for s in AMPS:
        rd = recs[f"amp{s}"]["rundir"]
        files = sorted(glob.glob(os.path.join(rd, "bin", "*.z4c.*.bin")))
        last, _ = t1.analyse_dump(B, files[-1], K, float(s), 0.0, 0.0)
        last.update(second_order_fields(files[-1]))
        pa, pp = t1.predict3d(B, K, N, last["t"], last["cycle"])
        rows[s] = {"last": last, "pred_gain_abs_minus_1": pa, "pred_gain_phase": pp,
                   "wall_s": recs[f"amp{s}"]["wall_s"], "source": "T9"}
    keys = sorted(rows, key=float)
    for s in keys:
        l = rows[s]["last"]
        A = float(s)
        rows[s]["alpha_minus_1_over_A2"] = l["max_abs_alpha_minus_1"]/A**2
        rows[s]["gain_minus_pred"] = l["gain_abs_minus_1"] - rows[s]["pred_gain_abs_minus_1"]
        print(f"N={N} A={s}: nonTT/A {l['nonTT_over_A']:.4e}, |alpha-1|/A^2 "
              f"{rows[s]['alpha_minus_1_over_A2']:.4e}, psi4 rev {l['psi4_reverse_over_max']:.3e},"
              f" psi4 err {l['psi4_err_rel']:.3e}, gain-1 {l['gain_abs_minus_1']:+.4e} (pred "
              f"{rows[s]['pred_gain_abs_minus_1']:+.4e}), phase {l['gain_phase']:+.4e} (pred "
              f"{rows[s]['pred_gain_phase']:+.4e}), gt err/A {l['max_err_gt_over_A']:.3e}")
    res = {"meta": {"exe": os.path.abspath(a.exe), "t1": a.t1, "commit": bc.git_rev(), "N": N},
           "rows": rows}
    bc.save_json(res, os.path.join(out, "results_t9.json"))

    fs.use_style()
    A = np.array([float(s) for s in keys])
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.4))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.15, top=0.93, wspace=0.3)
    ax = axs[0]
    ax.loglog(A, [rows[s]["last"]["nonTT_over_A"] for s in keys], "o-", color=fs.PAL["red"],
              label="non-TT part / A")
    ax.loglog(A, [rows[s]["alpha_minus_1_over_A2"]*float(s) for s in keys], "s--",
              color=fs.PAL["green"], label="max |alpha - 1| / A")
    ax.loglog(A, [rows[s]["last"]["max_err_gt_over_A"] for s in keys], "^:",
              color=fs.PAL["blue"], label="max |gt - exact| / A")
    ax.loglog(A, 3.38e-6*A/1e-6, color="k", lw=0.7, label=r"$\propto A$")
    ax.loglog(A, 1.1e-16/A, color="k", lw=0.7, ls="--", label=r"$10^{-16}/A$")
    ax.set_xlabel("amplitude A")
    ax.set_ylabel(f"after one period, N = {N}")
    ax.legend(fontsize=6, loc="upper center")
    ax = axs[1]
    ax.loglog(A, [rows[s]["last"]["psi4_reverse_over_max"] for s in keys], "o-",
              color=fs.PAL["red"], label=r"$\Psi_4$ along $-k$ / max")
    ax.loglog(A, [rows[s]["last"]["psi4_err_rel"] for s in keys], "s--", mfc="none",
              color=fs.PAL["yellow"], label=r"$\Psi_4$ error (relative)")
    ax.loglog(A, 4.9e-8*1e-6/A, color="k", lw=0.7, label=r"prediction R1: $4.9\times10^{-14}/A$")
    ax.set_xlabel("amplitude A")
    ax.legend(fontsize=6, loc="upper right")
    print("figures:", fs.save(fig, os.path.join(out, "t9_amp_cpu")))


if __name__ == "__main__":
    main()
