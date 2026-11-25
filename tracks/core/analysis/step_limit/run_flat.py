#!/usr/bin/env python3
"""Tests T1 and T2 of the package step-limit (tracks/core/JOURNAL-step-limit.md): the
stability bound that Z4c::GaugeTimeStep evaluates, bracketed by runs of the code.

Flat space with white noise of 1e-10 in a periodic box of 16^3 cells
(problems/tests/z4c_step_limit.athinput), one sector isolated per group:

  S  Gamma-driver alone binds: lapse frozen, shift_Gamma = 1.5
  L  1+log lapse alone binds: zero shift
  C  lapse frozen, zero shift: conformal factor and Theta bind ("light" of the kernel)
  K  relaxation of the lapse: zero shift, 1+log with lapse_leak = 32
  H  harmonic slicing (d_t alpha = -alpha^2 Khat), zero shift: the lapse pair has the
     speed of light, conformal factor and Theta bind
  D  the deck as it is (1+log and Gamma-driver with shift_Gamma = 0.75) at cfl_number 1.0

For each group the bound b (in cells) is taken from the reduced model of
vonneumann_gauge.py; the code then runs 300 steps at cfl_number = 0.93 b ("m"),
0.97 b ("a"), 1.03 b ("b"), 1.07 b ("p") and at 1.07 b with dt_gauge = 0.9 ("g"); D
runs at 1.0 without and with dt_gauge.  T1: the bounds the code prints at start-up
against the reduced model.

  python run_flat.py --exe ATHENA --out DIR [--workers 5] [--nlim 300]
"""
import argparse
import concurrent.futures as cf
import json
import os
import re
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
import vonneumann_gauge as vg  # noqa: E402

DECK = os.path.join(REPO, "problems", "tests", "z4c_step_limit.athinput")
DX = 5.0 / 16
NOSHIFT = ["z4c/shift_Gamma=0.0", "z4c/shift_eta=0.0", "z4c/shift_advect=0.0"]
NOLAPSE = ["z4c/lapse_oplog=0.0", "z4c/lapse_advect=0.0"]
GROUPS = {
    # name: (overrides, parameters of the three sectors for the reduced model)
    "S": (NOLAPSE + ["z4c/shift_Gamma=1.5"],
          dict(mu=1.5, eta=2.0, f=0.0, leak=0.0)),
    "L": (NOSHIFT, dict(mu=0.0, eta=0.0, f=2.0, leak=0.0)),
    "C": (NOSHIFT + NOLAPSE, dict(mu=0.0, eta=0.0, f=0.0, leak=0.0)),
    "K": (NOSHIFT + ["z4c/lapse_leak=32.0", "z4c/lapse_leak_alpha=1.0"],
          dict(mu=0.0, eta=0.0, f=2.0, leak=32.0)),
    "H": (NOSHIFT + ["z4c/lapse_oplog=0.0", "z4c/lapse_harmonic=1.0"],
          dict(mu=0.0, eta=0.0, f=1.0, leak=0.0)),
    "D": ([], dict(mu=0.75, eta=2.0, f=2.0, leak=0.0)),
}
EXTRA = {g: {"a": 0.97, "b": 1.03} for g in ("S", "L", "C", "K", "H")}


def model_bounds(tab, par, diss=0.5, ng=4):
    """Bounds in cells of the three sectors for flat space (alpha = chi = 1)."""
    sh = vg.reduced_sector(tab, ng, "shift",
                           dict(diss=diss, g=1.0, mu=par["mu"], etadx=par["eta"] * DX))
    la = vg.reduced_sector(tab, ng, "lapse",
                           dict(diss=diss, g=1.0, c2=par["f"], deltadx=par["leak"] * DX))
    li = vg.reduced_sector(tab, ng, "light", dict(diss=diss, g=1.0, c2=1.0))
    return [float(sh), float(la), float(li)]


def run_case(exe, out, name, args, nlim):
    d = os.path.join(out, name)
    os.makedirs(d, exist_ok=True)
    t0 = time.time()
    with open(os.path.join(d, "athena.log"), "w") as log:
        p = subprocess.run([exe, "-i", DECK, "time/nlim=%d" % nlim] + args + ["-d", d],
                           cwd=d, stdout=log, stderr=subprocess.STDOUT,
                           env=dict(os.environ, OMP_NUM_THREADS="1"))
    return name, p.returncode, round(time.time() - t0, 1)


def read_hst(path):
    rows = []
    with open(path) as f:
        for ln in f:
            if ln.startswith("#"):
                continue
            try:
                rows.append([float(x) for x in ln.split()])
            except ValueError:
                pass
    return np.array(rows)


def printed_bounds(log):
    """The three bounds (cells) of the start-up line, or of the warning."""
    txt = open(log).read()
    m = re.search(r"Gamma-driver shift ([-+.0-9eE]+), lapse ([-+.0-9eE]+), "
                  r"light ([-+.0-9eE]+)", txt)
    return [float(m.group(i)) for i in (1, 2, 3)] if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--nlim", type=int, default=300)
    args = ap.parse_args()
    args.exe = os.path.abspath(args.exe)
    args.out = os.path.abspath(args.out)
    os.makedirs(args.out, exist_ok=True)
    tab = vg.rho_table(vg.stab_poly("rk4"))

    cases = {}
    plan = {}
    for g, (ov, par) in GROUPS.items():
        b3 = model_bounds(tab, par)
        b = min(b3)
        plan[g] = {"model_bounds_cells": b3, "bound": b,
                   "binding": ("shift", "lapse", "light")[int(np.argmin(b3))]}
        if g == "D":
            cases["D_p"] = ov + ["time/cfl_number=1.0", "z4c/dt_gauge=0.0"]
            cases["D_g"] = ov + ["time/cfl_number=1.0", "z4c/dt_gauge=0.9"]
            continue
        cases[g + "_m"] = ov + ["time/cfl_number=%.6f" % (0.93 * b), "z4c/dt_gauge=0.0"]
        cases[g + "_p"] = ov + ["time/cfl_number=%.6f" % (1.07 * b), "z4c/dt_gauge=0.0"]
        cases[g + "_g"] = ov + ["time/cfl_number=%.6f" % (1.07 * b), "z4c/dt_gauge=0.9"]
        for v, fac in EXTRA.get(g, {}).items():
            cases[g + "_" + v] = ov + ["time/cfl_number=%.6f" % (fac * b),
                                       "z4c/dt_gauge=0.0"]
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(run_case, args.exe, args.out, n, a, args.nlim)
                for n, a in cases.items()]
        done = {f.result()[0]: f.result()[1:] for f in futs}

    res = {"plan": plan, "cases": {}}
    for n in cases:
        d = os.path.join(args.out, n)
        rc, wall = done[n]
        hp = os.path.join(d, "flat.z4c.user.hst")
        h = read_hst(hp) if os.path.exists(hp) else np.zeros((0, 11))
        fin = np.all(np.isfinite(h[:, 2:10]), axis=1) if h.size else np.array([])
        hf = h[fin] if h.size else h
        c0 = hf[0, 2] if hf.size else float("nan")
        cmax = hf[:, 2].max() if hf.size else float("nan")
        cend = hf[-1, 2] if hf.size else float("nan")
        log = open(os.path.join(d, "athena.log")).read()
        unstable = (rc != 0) or (not np.all(fin)) or (cmax > 1e6 * c0)
        res["cases"][n] = {
            "args": cases[n], "exit": rc, "wall_s": wall, "records": int(len(h)),
            "dt_last_over_dx": float(hf[-1, 1] / DX) if hf.size else None,
            "dt_max_over_dx": float(hf[:, 1].max() / DX) if hf.size else None,
            "C2_first": float(c0), "C2_last_finite": float(cend),
            "C2_max_over_first": float(cmax / c0) if c0 > 0 else None,
            "unstable": bool(unstable),
            "warning": bool(re.search(r"### WARNING \(Z4c step limit\)", log)),
            "leak_warning": bool(re.search(r"lapse_leak x cfl_number", log)),
            "printed_bounds_cells": printed_bounds(os.path.join(d, "athena.log")),
        }
    # verdicts against the predictions
    ver = {}
    for g in GROUPS:
        if g == "D":
            ver[g] = {"p_unstable": res["cases"]["D_p"]["unstable"],
                      "g_stable": not res["cases"]["D_g"]["unstable"]}
        else:
            ver[g] = {"m_stable": not res["cases"][g + "_m"]["unstable"],
                      "a_stable": not res["cases"][g + "_a"]["unstable"],
                      "b_unstable": res["cases"][g + "_b"]["unstable"],
                      "p_unstable": res["cases"][g + "_p"]["unstable"],
                      "g_stable": not res["cases"][g + "_g"]["unstable"]}
        pb = (res["cases"][g + "_g"]["printed_bounds_cells"]
              or res["cases"][g + "_p"]["printed_bounds_cells"])
        if pb:
            ver[g]["T1_kernel_minus_model"] = [pb[i] - plan[g]["model_bounds_cells"][i]
                                               for i in range(3)]
            ver[g]["T1_kernel"] = pb
    res["verdicts"] = ver
    with open(os.path.join(args.out, "flat_summary.json"), "w") as f:
        json.dump(res, f, indent=1)

    # ---- figure: constraint norm against the step for every group
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, os.path.join(REPO, "python", "nrpic"))
    import figstyle as fs
    fs.use_style()
    names = list(GROUPS)
    fig, axs = plt.subplots(2, 3, figsize=(fs.FULL_WIDTH * 1.25, 6.0), sharey=True)
    fig.subplots_adjust(left=0.07, right=0.99, bottom=0.08, top=0.94, wspace=0.07,
                        hspace=0.32)
    axs = axs.ravel()
    col = {"m": fs.PAL["blue"], "p": fs.PAL["red"], "g": fs.PAL["green"],
           "a": "k", "b": fs.PAL["orange"]}
    title = {"S": "Gamma-driver", "L": "1+log lapse", "C": "frozen lapse",
             "K": "lapse relaxation", "H": "harmonic lapse", "D": "deck, cfl 1.0"}
    for ax, g in zip(axs, names):
        for v in ("m", "a", "b", "p", "g"):
            n = g + "_" + v
            if n not in cases:
                continue
            h = read_hst(os.path.join(args.out, n, "flat.z4c.user.hst"))
            if not h.size:
                continue
            y = np.where(np.isfinite(h[:, 2]) & (h[:, 2] > 0), h[:, 2], np.nan)
            c = res["cases"][n]
            lab = {"m": "0.93 b", "p": "1.07 b" if g != "D" else "no limit",
                   "a": "0.97 b", "b": "1.03 b",
                   "g": ("1.07 b, " if g != "D" else "") + "dt_gauge 0.9"}[v]
            ax.plot(np.arange(len(y)), np.sqrt(y), color=col[v],
                    label=lab + r" ($\Delta t/\Delta x$ %.3f)" % c["dt_max_over_dx"])
        ax.set_yscale("log")
        ax.set_ylim(1e-9, 1e6)
        ax.set_xlabel("history record (step)")
        ax.set_title("%s: b = %.3f (%s)" % (title[g], plan[g]["bound"],
                                           plan[g]["binding"]), fontsize=9)
        ax.legend(loc="upper left", fontsize=6.5)
    for ax in axs[::3]:
        ax.set_ylabel(r"norm of the constraint monitor $\sqrt{C^2}$")
    fig.savefig(os.path.join(args.out, "fig_flat.png"), dpi=150)
    print(json.dumps({"plan": plan, "verdicts": ver}, indent=1))
    for n, c in res["cases"].items():
        print(n, "exit", c["exit"], "unstable", c["unstable"], "dt/dx", c["dt_max_over_dx"],
              "growth", c["C2_max_over_first"], "warn", c["warning"], c["leak_warning"],
              "wall", c["wall_s"])


if __name__ == "__main__":
    main()
