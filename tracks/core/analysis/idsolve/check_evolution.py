#!/usr/bin/env python3
"""Does the evolution accept the solved data, and does a restart leave them alone?

    check_evolution.py [--exe ATHENA] [--steps 8]

A  Gaussian test at 32^3 cells (mode code), evolved for --steps cycles with a restart
   dump at half of them; then a run from that dump. The solver must not run after the
   restart (the dump holds the solved state) and the two histories must agree as far as
   a Z4c restart does (rounding).
B  Triaxial ball at 64^3 cells, evolved for --steps cycles without the solve and with it
   (mode code): constraint statistics of the code against time.

Runs are registered by hand (tracks/core/tools/run_registered.py); their ids and the
numbers go to evolution_numbers.json, the figure to figs/evolution (PDF and PNG).
"""
import argparse
import os
import subprocess
import sys
import time

import numpy as np

import idlib
import run_tests
from nrpic import figstyle as fs
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

TMP = os.path.join(idlib.SCRATCH, "tmp", "idsolve", "evolve")
RST = """
<output2>
file_type = rst
dcycle    = %d
"""


def registered(purpose, tag, inputs, cmd):
    full = [sys.executable, os.path.join(idlib.WT, "tracks/core/tools/run_registered.py"),
            "--purpose", purpose, "--tag", tag, "--cores", "1"]
    for f in inputs:
        full += ["--input", f]
    out = subprocess.run(full + ["--"] + cmd, capture_output=True, text=True)
    lines = out.stdout.strip().splitlines()
    if len(lines) < 2:
        raise RuntimeError(out.stderr)
    time.sleep(1.2)
    return lines[-1], lines[-2]


def cstat(run_id, base):
    return np.loadtxt(os.path.join(idlib.run_dir(run_id), base + ".cstat.hst"), ndmin=2)


NAMES = ("time chi_min chi_max K_min K_max E_min E_max Theta_max H_max H_mean Hr_max "
         "Hr_mean M_max M_mean Mr_max Mr_mean Z_max Z_mean Theta_mean").split()


def followup(a):
    path = os.path.join(idlib.HERE, "evolution_numbers.json")
    out = idlib.load_json(path)
    # ---- C: restart of the same run without the solve
    inp = os.path.join(TMP, "gaussian_rst.athinput")
    nrp = run_tests.ic_gauss(0.5)
    args = run_tests.mesh_args(32, 16) + ["time/nlim=%d" % a.steps, "time/tlim=100.0",
                                           "particles/id_solve=false",
                                           "particles/particle_file=" + os.path.basename(nrp)]
    ra, sa = registered("initial-data solver, control: evolution of the trial Gaussian "
                        "data (no solve) with a restart dump", "idsolve-evo-gauss-off",
                        [inp, nrp], [a.exe, "-i", os.path.basename(inp)] + args)
    rst = os.path.join(idlib.run_dir(ra), "rst", "gauss.00001.rst")
    rb, sb = registered("initial-data solver, control: continuation of %s from its "
                        "restart dump" % ra, "idsolve-evo-gauss-off-restart",
                        [rst, rst + ".prt", nrp],
                        [a.exe, "-r", "gauss.00001.rst", "time/tlim=100.0"])
    ca, cb = cstat(ra, "gauss"), cstat(rb, "gauss")
    sel = np.array([np.argmin(np.abs(ca[:, 0] - t)) for t in cb[:, 0]])
    diff = np.abs(ca[sel] - cb).max(axis=0)
    out["restart_control"] = dict(run=ra, status=sa, continued=rb, status_continued=sb,
                                  max_abs_difference={n: float(v) for n, v in
                                                      zip(NAMES, diff)})
    # the same table for the solved run of test A
    r = out["restart"]
    ca, cb = cstat(r["run"], "gauss"), cstat(r["continued"], "gauss")
    sel = np.array([np.argmin(np.abs(ca[:, 0] - t)) for t in cb[:, 0]])
    diff_s = np.abs(ca[sel] - cb).max(axis=0)
    r["max_abs_difference"] = {n: float(v) for n, v in zip(NAMES, diff_s)}
    print("restart, largest absolute differences (solved run | control without solve):")
    for n, v, w in zip(NAMES, diff_s, diff):
        print("   %-10s %.3e | %.3e" % (n, v, w))

    # ---- D: smooth triaxial ball without and with the solve
    nrp, tab = run_tests.ic_tri(0.5, 0.05, 2.0)
    base = run_tests.mesh_args(64, 32) + [
        "time/nlim=%d" % a.steps, "time/tlim=100.0", "particles/nfilter=0",
        "particles/particle_file=" + os.path.basename(nrp),
        "problem/comp0_file=" + os.path.basename(tab)]
    binp = os.path.join(idlib.WT, "problems/idsolve/ball.athinput")
    res = {}
    for label, extra in (("off", ["particles/id_solve=false"]),
                         ("code", ["particles/id_residual=code"])):
        rr, s = registered("initial-data solver: evolution of the triaxial ball with a "
                           "smooth edge, solve %s" % label, "idsolve-evo-trismooth-" + label,
                           [binp, nrp, tab], [a.exe, "-i", "ball.athinput"] + base + extra)
        c = cstat(rr, "ball")
        res[label] = dict(run=rr, status=s, time=[float(v) for v in c[:, 0]],
                          H_max=[float(v) for v in c[:, 8]],
                          H_mean=[float(v) for v in c[:, 9]],
                          M_max=[float(v) for v in c[:, 12]],
                          M_mean=[float(v) for v in c[:, 13]],
                          Theta_max=[float(v) for v in c[:, 7]],
                          finite=bool(np.all(np.isfinite(c))))
        print("smooth triaxial %-4s %s finite %s\n   H_max : %s\n   H_mean: %s\n   "
              "M_mean: %s" % (label, rr, res[label]["finite"],
                              " ".join("%.2e" % x for x in res[label]["H_max"]),
                              " ".join("%.2e" % x for x in res[label]["H_mean"]),
                              " ".join("%.2e" % x for x in res[label]["M_mean"])))
    out["triaxial_smooth"] = res
    idlib.save_json(path, out)

    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.1), sharey=True)
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.15, top=0.92, wspace=0.06)
    for ax, key, title in ((axs[0], "triaxial", "triaxial ball, sharp surface"),
                           (axs[1], "triaxial_smooth", "triaxial ball, smooth edge")):
        for label, c in (("off", "k"), ("code", fs.PAL["red"])):
            v = out[key][label]
            t = np.array(v["time"])
            ax.semilogy(t, np.array(v["H_mean"]) + 1e-30, color=c, marker=".",
                        label="mean |H|, solve %s" % label)
            ax.semilogy(t, np.array(v["H_max"]) + 1e-30, color=c, ls="--", marker=".",
                        label="max |H|, solve %s" % label)
            ax.semilogy(t, np.array(v["M_mean"]) + 1e-30, color=c, ls=":", lw=1.0,
                        label="mean |M|, solve %s" % label)
        ax.set_xlabel(r"$t$")
        ax.set_title(title + ", 64 cells", fontsize=10)
    axs[0].set_ylabel("constraints of the code")
    axs[1].legend(fontsize=7, ncol=2)
    fs.save(fig, os.path.join(idlib.FIGS, "evolution_tri"))
    plt.close(fig)
    return 0


def recommended(a):
    path = os.path.join(idlib.HERE, "evolution_numbers.json")
    out = idlib.load_json(path)
    nrp, tab = run_tests.ic_tri(0.5, 0.05, 2.0)
    base = run_tests.mesh_args(64, 32) + [
        "time/nlim=%d" % a.steps, "time/tlim=100.0", "particles/nfilter=0",
        "particles/source_density=true", "particles/source_extrap=true",
        "z4c/lapse_oplog=0.0", "z4c/lapse_harmonic=0.3333333333333333",
        "particles/particle_file=" + os.path.basename(nrp),
        "problem/comp0_file=" + os.path.basename(tab)]
    binp = os.path.join(idlib.WT, "problems/idsolve/ball.athinput")
    res = {}
    for label, extra in (("off", ["particles/id_solve=false"]),
                         ("code", ["particles/id_residual=code"])):
        rr, s = registered("initial-data solver: evolution of the smooth triaxial ball "
                           "with density-form sources and the conformal-time lapse, "
                           "solve %s" % label, "idsolve-evo-trirec-" + label,
                           [binp, nrp, tab], [a.exe, "-i", "ball.athinput"] + base + extra)
        c = cstat(rr, "ball")
        res[label] = dict(run=rr, status=s, time=[float(v) for v in c[:, 0]],
                          H_max=[float(v) for v in c[:, 8]],
                          H_mean=[float(v) for v in c[:, 9]],
                          M_max=[float(v) for v in c[:, 12]],
                          M_mean=[float(v) for v in c[:, 13]],
                          Theta_max=[float(v) for v in c[:, 7]],
                          finite=bool(np.all(np.isfinite(c))))
        print("recommended settings %-4s %s finite %s\n   H_max : %s\n   H_mean: %s\n   "
              "M_mean: %s" % (label, rr, res[label]["finite"],
                              " ".join("%.2e" % x for x in res[label]["H_max"]),
                              " ".join("%.2e" % x for x in res[label]["H_mean"]),
                              " ".join("%.2e" % x for x in res[label]["M_mean"])))
    out["triaxial_smooth_recommended"] = res
    idlib.save_json(path, out)
    plot_tri(out)
    return 0


REGIONS = ("interior", "shell", "exterior", "faces")


def region_stats(path, nb_face):
    """Means of |H| and |M| over four regions of a field dump of the ball: interior
    (r < 7), surface shell (7 <= r < 13.5), exterior (the rest away from the faces) and
    the face layer (within nb_face cells of a face). Also the volume fraction of each
    region and its share of the volume integral of |H|."""
    d = idlib.read_field(path)
    n = d["n"]
    x = idlib.centres(n[0], -32.0, 32.0)
    X, Y, Z = np.meshgrid(x, x, x, indexing="ij")
    r = np.sqrt(X*X + Y*Y + Z*Z)
    face = np.zeros(n, dtype=bool)
    face[:nb_face, :, :] = face[-nb_face:, :, :] = True
    face[:, :nb_face, :] = face[:, -nb_face:, :] = True
    face[:, :, :nb_face] = face[:, :, -nb_face:] = True
    masks = dict(interior=(r < 7.0) & ~face, shell=(r >= 7.0) & (r < 13.5) & ~face,
                 exterior=(r >= 13.5) & ~face, faces=face)
    h = np.abs(d["H"])
    m = np.sqrt(d["Mx"]**2 + d["My"]**2 + d["Mz"]**2)
    tot = h.sum()
    out = dict(time=float(d["time"]), H_mean_all=float(h.mean()), M_mean_all=float(m.mean()))
    for k in REGIONS:
        mk = masks[k]
        out[k] = dict(frac=float(mk.mean()), H_mean=float(h[mk].mean()),
                      H_max=float(h[mk].max()), M_mean=float(m[mk].mean()),
                      H_share=float(h[mk].sum()/tot) if tot > 0 else 0.0)
    return out, d


def resolution(a):
    """Test F: the smooth triaxial ball with the settings of test E at 64 and 128 cells,
    without and with the solve, to t = 2, with field dumps at t = 0, 1, 2: where the
    violation made by the evolution sits, and how it scales with the cell size."""
    path = os.path.join(idlib.HERE, "evolution_numbers.json")
    # the input of the ball with two more field-dump times (a parameter given on the
    # command line must exist in the input file)
    with open(os.path.join(idlib.WT, "problems/idsolve/ball.athinput")) as f:
        txt = f.read()
    key = "field_time1    = 1.0e30"
    if key not in txt:
        raise RuntimeError("ball.athinput: line '%s' not found" % key)
    txt = txt.replace(key, "field_time1    = 1.0\nfield_time2    = 2.0\n# was: " + key)
    binp = os.path.join(TMP, "ball_fields.athinput")
    with open(binp, "w") as f:
        f.write(txt)
    res = {}
    jobs = []
    for n in (64, 128):
        h = 32.0/n
        nrp, tab = run_tests.ic_tri(h, 0.05, 2.0)
        base = run_tests.mesh_args(n, 32) + [
            "time/nlim=1000", "time/tlim=2.0", "particles/nfilter=0",
            "particles/source_density=true", "particles/source_extrap=true",
            "z4c/lapse_oplog=0.0", "z4c/lapse_harmonic=0.3333333333333333",
            "particles/particle_file=" + os.path.basename(nrp),
            "problem/comp0_file=" + os.path.basename(tab)]
        for label, extra in (("off", ["particles/id_solve=false"]),
                             ("code", ["particles/id_residual=code"])):
            jobs.append((n, label, nrp, tab, base + extra))
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        futs = {}
        for (n, label, nrp, tab, args) in jobs:
            futs[ex.submit(registered,
                           "initial-data solver, test F: smooth triaxial ball with the "
                           "settings of test E at %d cells to t = 2 with field dumps, "
                           "solve %s" % (n, label), "idsolve-evo-res-%s-n%d" % (label, n),
                           [binp, nrp, tab], [a.exe, "-i", "ball_fields.athinput"] + args)] = (
                n, label)
            time.sleep(1.5)
        for f in concurrent.futures.as_completed(futs):
            n, label = futs[f]
            rr, s = f.result()
            print("F %s n%d %s %s" % (label, n, rr, s), flush=True)
            if not os.path.exists(os.path.join(idlib.run_dir(rr), "ball.cstat.hst")):
                res["%s_n%d" % (label, n)] = dict(run=rr, status=s, n=n, failed=True)
                continue
            c = cstat(rr, "ball")
            v = dict(run=rr, status=s, n=n, time=[float(x) for x in c[:, 0]],
                     H_max=[float(x) for x in c[:, 8]], H_mean=[float(x) for x in c[:, 9]],
                     M_max=[float(x) for x in c[:, 12]], M_mean=[float(x) for x in c[:, 13]],
                     finite=bool(np.all(np.isfinite(c))), regions=[])
            for i in range(3):
                fp = os.path.join(idlib.run_dir(rr), "ball.field.%05d.bin" % i)
                if os.path.exists(fp):
                    st, _ = region_stats(fp, 4 if n == 64 else 8)
                    v["regions"].append(st)
            res["%s_n%d" % (label, n)] = v
    out = idlib.load_json(path)
    out["triaxial_smooth_resolution"] = res
    idlib.save_json(path, out)
    plot_resolution(out)
    return 0


def plot_resolution(out):
    res = {k: v for k, v in out["triaxial_smooth_resolution"].items()
           if not v.get("failed")}
    fs.use_style()
    fig, axs = plt.subplots(1, 4, figsize=(fs.FULL_WIDTH, 2.9), sharey=True)
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.16, top=0.88, wspace=0.08)
    cols = {64: fs.PAL["blue"], 128: fs.PAL["red"]}
    ax = axs[0]
    for key, v in sorted(res.items()):
        ls = "-" if key.startswith("code") else "--"
        ax.semilogy(v["time"], np.array(v["H_mean"]) + 1e-30, color=cols[v["n"]], ls=ls,
                    marker=".", ms=3)
    ax.set_title("whole mesh", fontsize=9)
    ax.set_ylabel(r"mean $|H|$")
    for ax, reg, title in ((axs[1], "interior", r"interior $r < 7$"),
                           (axs[2], "shell", r"edge shell $7 \leq r < 13.5$"),
                           (axs[3], "faces", "face layer (4 units)")):
        for key, v in sorted(res.items()):
            ls = "-" if key.startswith("code") else "--"
            t = [st["time"] for st in v["regions"]]
            ax.semilogy(t, [max(st[reg]["H_mean"], 1e-9) for st in v["regions"]],
                        color=cols[v["n"]], ls=ls, marker="o", ms=3,
                        label="%d cells, solve %s" % (v["n"], key.split("_")[0]))
        ax.set_title(title, fontsize=9)
    for ax in axs:
        ax.set_xlabel(r"$t$")
        ax.set_ylim(1e-9, 1e-3)
    axs[3].legend(fontsize=6, loc="lower right")
    fs.save(fig, os.path.join(idlib.FIGS, "evolution_res"))
    plt.close(fig)


def plot_tri(out):
    """figs/evolution_tri: the three triaxial cases (sharp, smooth, smooth with the
    settings of problems/ball), mean and max |H| and mean |M| against time."""
    fs.use_style()
    cases = [("triaxial", "sharp surface"), ("triaxial_smooth", "smooth edge"),
             ("triaxial_smooth_recommended", "smooth edge, density sources,\n"
              "conformal-time lapse")]
    cases = [c for c in cases if c[0] in out]
    fig, axs = plt.subplots(1, len(cases), figsize=(fs.FULL_WIDTH, 3.2), sharey=True)
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.14, top=0.88, wspace=0.06)
    for ax, (key, title) in zip(np.atleast_1d(axs), cases):
        for label, c in (("off", "k"), ("code", fs.PAL["red"])):
            v = out[key][label]
            t = np.array(v["time"])
            ax.semilogy(t, np.array(v["H_mean"]) + 1e-30, color=c, marker=".",
                        label="mean |H|, solve %s" % label)
            ax.semilogy(t, np.array(v["H_max"]) + 1e-30, color=c, ls="--", marker=".",
                        label="max |H|, solve %s" % label)
            ax.semilogy(t, np.array(v["M_mean"]) + 1e-30, color=c, ls=":", lw=1.0,
                        label="mean |M|, solve %s" % label)
        ax.set_xlabel(r"$t$")
        ax.set_title(title, fontsize=9)
    np.atleast_1d(axs)[0].set_ylabel("constraints of the code, 64 cells")
    np.atleast_1d(axs)[-1].legend(fontsize=6.5, ncol=1, loc="lower right")
    fs.save(fig, os.path.join(idlib.FIGS, "evolution_tri"))
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", default=os.path.join(idlib.WT, ".work/build_cpu/src/athena"))
    ap.add_argument("--steps", type=int, default=8)
    ap.add_argument("--followup", action="store_true",
                    help="tests C (restart control without the solve) and D (smooth "
                         "triaxial ball) only; results are added to the json file")
    ap.add_argument("--recommended", action="store_true",
                    help="test E only: the smooth triaxial ball with the settings that "
                         "problems/ball recommends for an evolution")
    ap.add_argument("--plot", action="store_true",
                    help="redraw figs/evolution_tri from evolution_numbers.json only")
    ap.add_argument("--resolution", action="store_true",
                    help="test F only: the smooth triaxial ball of test E at 64 and 128 "
                         "cells with field dumps (regions of the violation)")
    a = ap.parse_args()
    os.makedirs(TMP, exist_ok=True)
    out = {}
    if a.resolution:
        return resolution(a)
    if a.plot:
        o = idlib.load_json(os.path.join(idlib.HERE, "evolution_numbers.json"))
        plot_tri(o)
        if "triaxial_smooth_resolution" in o:
            plot_resolution(o)
        return 0
    if a.followup:
        return followup(a)
    if a.recommended:
        return recommended(a)

    # ---- A: restart
    inp = os.path.join(TMP, "gaussian_rst.athinput")
    with open(os.path.join(idlib.WT, "problems/idsolve/gaussian.athinput")) as f:
        txt = f.read()
    with open(inp, "w") as f:
        f.write(txt + RST % (a.steps//2))
    nrp = run_tests.ic_gauss(0.5)
    args = run_tests.mesh_args(32, 16) + ["time/nlim=%d" % a.steps, "time/tlim=100.0",
                                           "particles/particle_file=" + os.path.basename(nrp)]
    ra, sa = registered("initial-data solver: evolution of the solved Gaussian data with a "
                        "restart dump", "idsolve-evo-gauss", [inp, nrp],
                        [a.exe, "-i", os.path.basename(inp)] + args)
    da = idlib.run_dir(ra)
    rst = os.path.join(da, "rst", "gauss.00001.rst")
    rb, sb = registered("initial-data solver: continuation of %s from its restart dump" % ra,
                        "idsolve-evo-gauss-restart", [rst, rst + ".prt", nrp],
                        [a.exe, "-r", "gauss.00001.rst", "time/tlim=100.0"])
    ca, cb = cstat(ra, "gauss"), cstat(rb, "gauss")
    # the continued run writes the records after the dump
    tb = cb[:, 0]
    sel = np.array([np.argmin(np.abs(ca[:, 0] - t)) for t in tb])
    diff = np.abs(ca[sel] - cb)
    scale = np.maximum(np.abs(ca[sel]), 1.0e-300)
    with open(os.path.join(idlib.run_dir(rb), "run.log")) as f:
        log_b = f.read()
    out["restart"] = dict(
        run=ra, status=sa, continued=rb, status_continued=sb,
        records_compared=int(len(tb)), times=[float(t) for t in tb],
        solver_ran_after_restart=("initial-data solve" in log_b),
        idsolve_txt_written_after_restart=os.path.exists(
            os.path.join(idlib.run_dir(rb), "gauss.idsolve.txt")),
        max_abs_difference_H_max=float(diff[:, 8].max()),
        max_rel_difference_chi_K_E=float((diff[:, 1:7]/scale[:, 1:7]).max()),
        H_max=[float(v) for v in ca[:, 8]], H_mean=[float(v) for v in ca[:, 9]],
        Theta_max=[float(v) for v in ca[:, 7]], time=[float(v) for v in ca[:, 0]])

    # ---- B: triaxial ball without and with the solve
    nrp, tab = run_tests.ic_tri(0.5, 0.05)
    base = run_tests.mesh_args(64, 32) + [
        "time/nlim=%d" % a.steps, "time/tlim=100.0", "particles/nfilter=0",
        "particles/particle_file=" + os.path.basename(nrp),
        "problem/comp0_file=" + os.path.basename(tab)]
    binp = os.path.join(idlib.WT, "problems/idsolve/ball.athinput")
    res = {}
    for label, extra in (("off", ["particles/id_solve=false"]),
                         ("code", ["particles/id_residual=code"])):
        r, s = registered("initial-data solver: evolution of the triaxial ball, solve %s"
                          % label, "idsolve-evo-tri-" + label, [binp, nrp, tab],
                          [a.exe, "-i", "ball.athinput"] + base + extra)
        c = cstat(r, "ball")
        res[label] = dict(run=r, status=s, time=[float(v) for v in c[:, 0]],
                          H_max=[float(v) for v in c[:, 8]],
                          H_mean=[float(v) for v in c[:, 9]],
                          M_max=[float(v) for v in c[:, 12]],
                          M_mean=[float(v) for v in c[:, 13]],
                          Theta_max=[float(v) for v in c[:, 7]],
                          finite=bool(np.all(np.isfinite(c))))
    out["triaxial"] = res
    idlib.save_json(os.path.join(idlib.HERE, "evolution_numbers.json"), out)

    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.1))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.15, top=0.92, wspace=0.28)
    ax = axs[0]
    r = out["restart"]
    ax.semilogy(r["time"], np.array(r["H_mean"]) + 1e-30, color=fs.PAL["red"],
                marker=".", label="uninterrupted, mean |H|")
    ax.semilogy(tb, cb[:, 9] + 1e-30, color=fs.PAL["blue"], ls="--", marker="x",
                label="from the dump, mean |H|")
    ax.semilogy(r["time"], np.array(r["Theta_max"]) + 1e-30, color=fs.PAL["green"],
                marker=".", label=r"uninterrupted, max $|\Theta|$")
    ax.set_xlabel(r"$t$")
    ax.set_ylabel("constraint statistics of the code")
    ax.set_title("Gaussian, 32 cells, solved (code)", fontsize=10)
    ax.legend(fontsize=8)
    ax = axs[1]
    for label, c in (("off", "k"), ("code", fs.PAL["red"])):
        t = np.array(res[label]["time"])
        ax.semilogy(t, np.array(res[label]["H_mean"]) + 1e-30, color=c, marker=".",
                    label="mean |H|, solve %s" % label)
        ax.semilogy(t, np.array(res[label]["H_max"]) + 1e-30, color=c, ls="--", marker=".",
                    label="max |H|, solve %s" % label)
    ax.set_xlabel(r"$t$")
    ax.set_ylabel("Hamiltonian constraint of the code")
    ax.set_title("triaxial ball, 64 cells", fontsize=10)
    ax.legend(fontsize=8)
    fs.save(fig, os.path.join(idlib.FIGS, "evolution"))
    plt.close(fig)

    print("restart: %s continued as %s; solver ran after restart: %s; records %d; "
          "largest |difference| of H_max %.3e; largest relative difference of chi, K, E "
          "extrema %.3e" % (ra, rb, r["solver_ran_after_restart"], r["records_compared"],
                            r["max_abs_difference_H_max"], r["max_rel_difference_chi_K_E"]))
    print("   H_mean(t): " + " ".join("%.2e" % v for v in r["H_mean"]))
    for label in ("off", "code"):
        v = res[label]
        print("triaxial %-4s %s finite %s\n   H_max : %s\n   H_mean: %s\n   M_mean: %s" % (
            label, v["run"], v["finite"], " ".join("%.2e" % x for x in v["H_max"]),
            " ".join("%.2e" % x for x in v["H_mean"]),
            " ".join("%.2e" % x for x in v["M_mean"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
