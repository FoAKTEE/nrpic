#!/usr/bin/env python3
"""What coll_energy = particle leaves of the first-step energy defect of the King threshold
model (threshold_scan package, CC1: King b = 1, y0 = 0.334032, N = 1e5, static M/4 mesh).

    python3 king_defect.py [--kn 1,0.1,0.01] [--nlim 2] [--nproc 6] [--exe PATH]
                           [--smoke RUN_DIR] [--tag cpu]

For every Knudsen number and both modes (coll_energy = cell, the core-v0.3 operator; and
particle) the deck inputs/king_cc1.athinput runs nlim cycles on the processor executable
of core/collisions-2 with coll_budget = true and the dump of the first collision step
(coll_dump_cycle = 0). sigma~ = K/Kn with K = 168.89536939113694 (threshold_scan,
1/(rho0_c H_c)).

Measured, per step and per collision, from coll.hst (collisions.md section 5 on
core/collisions-2): the change of sum M W_p (column 31, W with the metric at each
particle: the deposited energy; the "energy defect" of threshold_scan) and of
sum M H_p (column 33, H = alpha W - beta^i u_i: the canonical energy that a pair conserves
with coll_energy = particle), each over its sum (columns 30, 32); n_noroot, n_balance,
max_dlam.
Independent check from the dump of step 1 (version 2, metric at every particle): sums
of M dW_p and M dH_p over the collided particles recomputed here with the dumped metric,
against columns 31 and 33; and per collision cell (cells as the independent units) the
mean change per collision with its standard error from the scatter of the cell sums.
Control: the cell-mode run at Kn = 1 against the release smoke run of threshold_scan
(C-20261115-172003-6422b6a, cc1_kn1): columns 1-31 of the common records identical.
Writes king_<tag>.json and king_defect_<tag>.png into $NRPIC_RUN_DIR.
"""
import argparse
import glob
import json
import math
import os
import subprocess
import sys
import time

import numpy as np

import boxlib as bl

sys.path.insert(0, os.path.join(bl.REPO, "python"))
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

K_SIGMA = 168.89536939113694
DECK = os.path.join(bl.PKG, "inputs", "king_cc1.athinput")
SMOKE = os.path.join(bl.MAIN, "scratch", "C-sidm", "C-20261115-172003-6422b6a", "cc1_kn1")


def run(rd, exe, ov):
    os.makedirs(rd, exist_ok=True)
    cmd = [exe, "-i", DECK, "-d", rd] + ov
    env = dict(os.environ, OMP_NUM_THREADS="1")
    t0 = time.time()
    with open(os.path.join(rd, "athena.log"), "w") as fh:
        fh.write(" ".join(cmd) + "\n")
        fh.flush()
        rc = subprocess.run(cmd, cwd=rd, stdout=fh, stderr=subprocess.STDOUT, env=env).returncode
    return dict(rc=rc, wall=time.time() - t0)


def per_cell(d, dW, dH, M):
    """Sums of M dW and M dH per collision cell over the collided particles, and the
    number of collisions of each cell (half the momentum updates)."""
    sel = d["nupd"] > 0
    key = (d["level"][sel].astype(np.int64) * (1 << 54) + d["I"][sel].astype(np.int64) *
           (1 << 36) + d["J"][sel].astype(np.int64) * (1 << 18) + d["K"][sel].astype(np.int64))
    uk, inv = np.unique(key, return_inverse=True)
    ncell = uk.size
    sW = np.zeros(ncell); sH = np.zeros(ncell); nc = np.zeros(ncell)
    np.add.at(sW, inv, (M * dW)[sel])
    np.add.at(sH, inv, (M * dH)[sel])
    np.add.at(nc, inv, d["nupd"][sel] / 2.0)
    return sW, sH, nc


def ratio_mean(s, n):
    """Mean per collision sum(s)/sum(n) with its standard error from the scatter of the
    cell sums (ratio estimator, cells independent)."""
    R = s.sum() / n.sum()
    k = s.size
    if k < 2:
        return float(R), float("nan")
    res = s - R * n
    se = math.sqrt(k / (k - 1) * np.sum(res ** 2)) / n.sum()
    return float(R), float(se)


def analyse(rd, kind, pmetric=None):
    h = bl.coll_history(rd, base="cc")
    out = dict(run=rd, mode=kind, records=int(h["ncycle"].size),
               n_coll=h["n_coll"].tolist(), sum_P=h["sum_P"].tolist(),
               n_tested=h["n_tested"].tolist(), max_P=h["max_P"].tolist(),
               max_nsub=h["max_nsub"].tolist(),
               sum_MW_p=h["sum_MW_particles"].tolist(), dW_p=h["dE_particles"].tolist(),
               sum_MH_p=h["sum_MH_particles"].tolist(), dH_p=h["dH_particles"].tolist(),
               n_noroot=h["n_noroot"].tolist(), n_balance=h["n_balance"].tolist(),
               max_dlam=h["max_dlam"].tolist(), dE_col20=h["dE"].tolist())
    nc = h["n_coll"]
    out["dW_per_coll_rel"] = float(h["dE_particles"].sum() / nc.sum() /
                                   h["sum_MW_particles"][0])
    out["dH_per_coll_rel"] = float(h["dH_particles"].sum() / nc.sum() /
                                   h["sum_MH_particles"][0])
    out["dH_per_coll_abs"] = float(h["dH_particles"].sum() / nc.sum())
    out["max_abs_dH_step_rel"] = float(np.max(np.abs(h["dH_particles"]) /
                                              h["sum_MH_particles"]))
    # dump of step 1
    dp = sorted(glob.glob(os.path.join(rd, "cc.coll_dump.*.bin")))
    if dp:
        d = bl.read_dump(dp[0])
        out.update(dump=os.path.basename(dp[0]), dump_version=d["version"],
                   dump_energy_mode=d["energy"], dump_pmetric_flag=d["pmetric_flag"])
        src = d if d["pmetric_flag"] == 1 else pmetric
        if src is not None:
            same_x = bool(np.array_equal(src["x"], d["x"]))
            out["metric_from"] = "own dump" if src is d else "dump of the particle run"
            out["metric_positions_identical"] = same_x
            W0, H0 = bl.particle_energies(d["u0"], src["alpha_p"], src["beta_p"], src["ginv_p"])
            W1, H1 = bl.particle_energies(d["u1"], src["alpha_p"], src["beta_p"], src["ginv_p"])
            M = d["m"]
            sel = d["nupd"] > 0
            rec = int(np.flatnonzero(h["ncycle"] == d["cycle"] + 1)[0])
            dW_sum = math.fsum(M[sel] * W1[sel]) - math.fsum(M[sel] * W0[sel])
            dH_sum = math.fsum(M[sel] * H1[sel]) - math.fsum(M[sel] * H0[sel])
            dW_sum_exact = math.fsum(np.concatenate([M[sel] * W1[sel], -M[sel] * W0[sel]]))
            dH_sum_exact = math.fsum(np.concatenate([M[sel] * H1[sel], -M[sel] * H0[sel]]))
            sW, sH, ncell = per_cell(d, W1 - W0, H1 - H0, M)
            mW, seW = ratio_mean(sW, ncell)
            mH, seH = ratio_mean(sH, ncell)
            SW = math.fsum(M * W0)       # all particles of the dump (all have a cell here)
            SH = math.fsum(M * H0)
            out.update(dump_record=rec, dump_collided=int(sel.sum()),
                       dump_collisions=float(d["nupd"].sum() / 2.0),
                       hst_n_coll_of_record=float(h["n_coll"][rec]),
                       dump_dW_sum=dW_sum_exact, dump_dH_sum=dH_sum_exact,
                       hst_dW_of_record=float(h["dE_particles"][rec]),
                       hst_dH_of_record=float(h["dH_particles"][rec]),
                       dump_sum_MW=SW, dump_sum_MH=SH,
                       hst_sum_MW_p_of_record=float(h["sum_MW_particles"][rec]),
                       cells_with_collisions=int(ncell.size),
                       cell_dW_per_coll_rel=mW / SW, cell_dW_per_coll_rel_se=seW / SW,
                       cell_dH_per_coll_rel=mH / SH, cell_dH_per_coll_rel_se=seH / SH,
                       cell_dH_abs_max=float(np.max(np.abs(sH))),
                       cell_dW_abs_max=float(np.max(np.abs(sW))),
                       hist_cell_dH=sH.tolist(), hist_cell_dW=sW.tolist(),
                       hist_cell_n=ncell.tolist())
            out["dump_vs_hst_dW_abs"] = abs(dW_sum_exact - out["hst_dW_of_record"])
            out["dump_vs_hst_dH_abs"] = abs(dH_sum_exact - out["hst_dH_of_record"])
            out["dump_dW_sum_naive"] = dW_sum
            out["dump_dH_sum_naive"] = dH_sum
    return out, (d if dp else None)


def compare_smoke(rd, smoke):
    """Columns 1-31 of the common records of rd and the release smoke run."""
    a = bl.coll_history(rd, base="cc")
    b = bl.coll_history(smoke, base="cc")
    cyc = np.intersect1d(a["ncycle"], b["ncycle"])
    ia = np.searchsorted(a["ncycle"], cyc)
    ib = np.searchsorted(b["ncycle"], cyc)
    differ = [k for k in bl.COLL_COLUMNS if not np.array_equal(a[k][ia], b[k][ib])]
    maxabs = {k: float(np.max(np.abs(a[k][ia] - b[k][ib]))) for k in differ}
    return dict(smoke=smoke, records=int(cyc.size), columns_differ=differ,
                max_abs_diff=maxabs, identical=bool(cyc.size > 0 and not differ))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kn", default="1,0.1,0.01")
    ap.add_argument("--nlim", type=int, default=2)
    ap.add_argument("--nproc", type=int, default=6)
    ap.add_argument("--exe", default=bl.EXE_CPU_C2)
    ap.add_argument("--smoke", default=SMOKE)
    ap.add_argument("--tag", default="cpu")
    a = ap.parse_args()
    out = bl.outdir()
    jobs = []
    for kn in a.kn.split(","):
        sig = K_SIGMA / float(kn)
        for mode in ("cell", "particle"):
            rd = os.path.join(out, f"king_kn{kn}_{mode}")
            ov = [f"time/nlim={a.nlim}", "particles/snap_dt=-1", "output2/dt=1e9",
                  f"particles/coll_sigma={sig!r}", f"particles/coll_energy={mode}",
                  "particles/coll_dump_cycle=0"]
            jobs.append((kn, mode, rd, ov))
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=a.nproc) as ex:
        rr = list(ex.map(lambda j: run(j[2], a.exe, j[3]), jobs))
    res = {}
    for kn in a.kn.split(","):
        pr = None
        for mode in ("particle", "cell"):          # particle first: its dump has the metric
            k = [i for i, j in enumerate(jobs) if j[0] == kn and j[1] == mode][0]
            name = os.path.basename(jobs[k][2])
            if rr[k]["rc"] != 0:
                res[name] = dict(rc=rr[k]["rc"], failed=True, wall=rr[k]["wall"])
                continue
            o, d = analyse(jobs[k][2], mode, pmetric=pr)
            if mode == "particle":
                pr = d
            o.update(rc=0, wall=rr[k]["wall"], kn=float(kn), sigma=K_SIGMA / float(kn))
            res[name] = o
    if os.path.isdir(a.smoke) and "king_kn1_cell" in res and not res["king_kn1_cell"].get("failed"):
        res["king_kn1_cell"]["vs_release_smoke"] = compare_smoke(res["king_kn1_cell"]["run"],
                                                                 a.smoke)
    summ = dict(exe=a.exe, deck=DECK, nlim=a.nlim,
                runs={k: {kk: vv for kk, vv in v.items() if not kk.startswith("hist_")}
                      for k, v in res.items()})
    bl.save_json(os.path.join(out, f"king_{a.tag}.json"), summ)
    figure(res, out, a.tag)
    for k, v in summ["runs"].items():
        print(k, json.dumps({kk: v.get(kk) for kk in (
            "n_coll", "dW_per_coll_rel", "dH_per_coll_rel", "max_abs_dH_step_rel",
            "cell_dW_per_coll_rel", "cell_dW_per_coll_rel_se", "cell_dH_per_coll_rel",
            "cell_dH_per_coll_rel_se", "dump_vs_hst_dW_abs", "dump_vs_hst_dH_abs",
            "n_noroot", "n_balance", "max_dlam", "wall")}))
    if "king_kn1_cell" in summ["runs"]:
        print("vs_release_smoke", summ["runs"]["king_kn1_cell"].get("vs_release_smoke"))


def figure(res, out, tag):
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.3))
    ax1 = fig.add_axes([0.08, 0.15, 0.38, 0.78])
    ax2 = fig.add_axes([0.58, 0.15, 0.40, 0.78])
    cols = dict(cell=fs.PAL["red"], particle=fs.PAL["blue"])
    kns = sorted({v["kn"] for v in res.values() if not v.get("failed")}, reverse=True)
    for name, v in res.items():
        if v.get("failed") or "cell_dW_per_coll_rel" not in v:
            continue
        x = kns.index(v["kn"])
        c = cols[v["mode"]]
        off = -0.12 if v["mode"] == "cell" else 0.12
        ax1.errorbar(x + off - 0.04, v["cell_dW_per_coll_rel"], yerr=v["cell_dW_per_coll_rel_se"],
                     fmt="o", color=c, ms=4, label=f"{v['mode']}: $\\Sigma MW_p$" if x == 0 else None)
        ax1.errorbar(x + off + 0.04, v["cell_dH_per_coll_rel"], yerr=v["cell_dH_per_coll_rel_se"],
                     fmt="s", color=c, mfc="none", ms=4,
                     label=f"{v['mode']}: $\\Sigma MH_p$" if x == 0 else None)
        sH = np.abs(np.array(v["hist_cell_dH"])) / np.maximum(np.array(v["hist_cell_n"]), 1)
        sH = np.sort(np.maximum(sH / v["dump_sum_MH"], 1e-30))
        if v["kn"] == kns[-1]:
            ax2.step(sH, np.arange(1, sH.size + 1) / sH.size, color=c,
                     label=f"{v['mode']}, Kn = {v['kn']:g}: $|\\Delta\\Sigma MH_p|$")
            sW = np.abs(np.array(v["hist_cell_dW"])) / np.maximum(np.array(v["hist_cell_n"]), 1)
            sW = np.sort(np.maximum(sW / v["dump_sum_MW"], 1e-30))
            ax2.step(sW, np.arange(1, sW.size + 1) / sW.size, color=c, ls="--",
                     label=f"{v['mode']}: $|\\Delta\\Sigma MW_p|$")
    ax1.axhline(0, **fs.GUIDE)
    ax1.axhline(1.74e-10, color="grey", lw=0.6, ls=":")
    ax1.set_xticks(range(len(kns)))
    ax1.set_xticklabels([f"Kn = {k:g}" for k in kns])
    ax1.set_ylabel("change per collision / sum (step 1, cells)")
    ax1.legend(loc="upper right", fontsize=6)
    ax2.set_xscale("log")
    ax2.set_xlabel("per cell: |change| per collision / sum")
    ax2.set_ylabel("cumulative fraction of cells")
    ax2.legend(loc="upper left", fontsize=6)
    fs.save(fig, os.path.join(out, f"king_defect_{tag}"))
    plt.close(fig)


if __name__ == "__main__":
    sys.exit(main())
