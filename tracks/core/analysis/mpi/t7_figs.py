#!/usr/bin/env python3
"""Figures and numbers of test T7 of work package mpi (journal entry 24): what the first
session left untested on several ranks.

    python3 t7_figs.py --analytic DIR --probes DIR --ahexc DIR [--ahexc-dep DIR]
                       [--figdir DIR] [--out t7.json]

Each DIR is the output directory of one case of mpi_tests.py (with np1, np2, np4 inside).
Writes t7_probes.{pdf,png} (analytic metric and the eight probes) and
t7_ah_exc.{pdf,png} (moving puncture with horizon excision), and prints the numbers that
go into the journal (also written to --out).
"""
import argparse
import glob
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "python")))
from nrpic import figstyle as fs  # noqa: E402
import mpi_tests as mt  # noqa: E402

RANKS = (1, 2, 4)
COL = {1: fs.PAL["blue"], 2: fs.PAL["red"], 4: fs.PAL["green"]}
STY = {1: "-", 2: "--", 4: ":"}
FLOOR = 1.0e-18


def one(base, n, pattern):
    g = sorted(glob.glob(os.path.join(base, "np%d" % n, pattern)))
    return g[0] if g else None


def lab(n):
    return "%d rank%s" % (n, "" if n == 1 else "s")


# ----------------------------------------------------------------------------------------
def probes_numbers(base):
    """history columns of probe 0 (13-15) and probes 1..7 (33-53) on 1, 2, 4 ranks"""
    h = {n: mt.read_table(one(base, n, "*.nrpic.hst")) for n in RANKS}
    a = h[1]
    npr = (a.shape[1] - 32)//3
    idx = [(12, 13, 14)] + [(32 + 3*k, 33 + 3*k, 34 + 3*k) for k in range(npr)]
    res = dict(nprobe=npr, records=int(a.shape[0]), t=a[:, 0].tolist(), probes=[])
    emax = max(np.abs(a[:, i[1]]).max() for i in idx)
    for k, (ia, ie, it) in enumerate(idx):
        row = dict(probe=k, alpha_first=float(a[0, ia]), alpha_last=float(a[-1, ia]),
                   E_max=float(np.abs(a[:, ie]).max()))
        for n in RANKS[1:]:
            b = h[n]
            row["np%d" % n] = dict(
                alpha=float(np.abs(b[:, ia] - a[:, ia]).max()/np.abs(a[:, ia]).max()),
                E=float(np.abs(b[:, ie] - a[:, ie]).max()/max(emax, 1e-300)),
                tau=float(np.abs(b[:, it] - a[:, it]).max()/max(np.abs(a[:, it]).max(), 1e-300)))
        res["probes"].append(row)
    # probe 1 sits at the point of probe 0
    res["probe1_equals_probe0"] = {
        "np%d" % n: bool(np.array_equal(h[n][:, 12:15], h[n][:, 32:35])) for n in RANKS}
    res["E_max_all_probes"] = float(emax)
    return res, h, idx


def fig_probes(analytic, probes, figdirs):
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.1))
    out = {}
    # (a) analytic metric: the geodesic on 1, 2, 4 ranks
    ax = fig.add_axes([0.07, 0.17, 0.25, 0.71])
    if analytic:
        ident = {}
        ref = one(analytic, 1, "*.traj.bin")
        for n in RANKS:
            f = one(analytic, n, "*.traj.bin")
            rec = np.fromfile(f, "<f8").reshape(-1, 8)
            r, th, ph = rec[:, 2], rec[:, 3], rec[:, 4]
            ax.plot(r*np.sin(th)*np.cos(ph), r*np.sin(th)*np.sin(ph), color=COL[n],
                    ls=STY[n], lw=1.6 - 0.3*RANKS.index(n), label=lab(n))
            ident["np%d" % n] = (mt.sha256(f) == mt.sha256(ref))
        m = one(analytic, 4, "*.mpi.hst")
        per = mt.read_table(m)[:, 4:]
        out["analytic"] = dict(traj_identical=ident, records=int(len(rec)),
                               particles_per_rank_4=[int(v) for v in per.max(axis=0)])
        ax.plot([0], [0], "ko", ms=4)
        ax.set_aspect("equal", adjustable="datalim")
        ax.set_xlabel("x / M")
        ax.set_ylabel("y / M")
        ax.legend(loc="lower left", fontsize=7)
    ax.set_title("(a) analytic Kerr metric", fontsize=9)
    # (b) lapse and energy density at the eight probes, one rank
    res, h, idx = probes_numbers(probes)
    out["probes"] = res
    a = h[1]
    ax2 = fig.add_axes([0.42, 0.17, 0.23, 0.71])
    for k, (ia, ie, it) in enumerate(idx):
        ax2.plot(a[:, 0], a[:, ia], color=fs.SERIES[k % len(fs.SERIES)],
                 ls="-" if k < len(fs.SERIES) else "--", lw=1.0, label="probe %d" % k)
    ax2.set_xlabel("t / M")
    ax2.set_ylabel("lapse at the probe")
    ax2.legend(loc="center right", fontsize=6, ncol=2)
    ax2.set_title("(b) cluster, 1 rank", fontsize=9)
    # (c) differences from one rank, largest over the eight probes
    ax3 = fig.add_axes([0.75, 0.17, 0.23, 0.71])
    emax = res["E_max_all_probes"]
    for n in RANKS[1:]:
        b = h[n]
        da = np.max([np.abs(b[:, i[0]] - a[:, i[0]])/np.abs(a[:, i[0]]).max() for i in idx], axis=0)
        de = np.max([np.abs(b[:, i[1]] - a[:, i[1]])/emax for i in idx], axis=0)
        ax3.semilogy(a[:, 0], np.maximum(da, FLOOR), color=COL[n], ls="-", lw=1.0,
                     label=lab(n) + ": lapse")
        ax3.semilogy(a[:, 0], np.maximum(de, FLOOR), color=COL[n], ls="--", lw=1.0,
                     label=lab(n) + ": E")
    ax3.axhline(2.2e-16, **fs.MASK_LINE)
    ax3.set_ylim(FLOOR, 1e-9)
    ax3.set_xlabel("t / M")
    ax3.set_ylabel("largest difference from 1 rank", fontsize=8)
    ax3.legend(loc="upper left", fontsize=6)
    ax3.set_title("(c) all eight probes", fontsize=9)
    paths = []
    for d in figdirs:
        os.makedirs(d, exist_ok=True)
        paths += fs.save(fig, os.path.join(d, "t7_probes"))
    plt.close(fig)
    return out, paths


# ----------------------------------------------------------------------------------------
def ah_numbers(base):
    h = {n: mt.read_table(one(base, n, "*.nrpic.hst")) for n in RANKS}
    co = {n: mt.read_table(one(base, n, "*.co_0.txt")) for n in RANKS}
    hs = {n: mt.read_table(one(base, n, "*.horizon_summary_0.txt")) for n in RANKS}
    a = h[1]
    res = dict(records=int(a.shape[0]), t=a[:, 0].tolist(),
               n_excised={("np%d" % n): [int(v) for v in h[n][:, 16]] for n in RANKS},
               np_particles={("np%d" % n): [int(v) for v in h[n][:, 2]] for n in RANKS})
    res["excised_equal"] = {("np%d" % n): bool(np.array_equal(h[n][:, 16], a[:, 16])
                                              and np.array_equal(h[n][:, 2], a[:, 2]))
                            for n in RANKS[1:]}
    res["excised_first_step"] = int(a[1, 16]) if len(a) > 1 else 0
    res["excised_last"] = int(a[-1, 16])
    res["excision_events"] = int((np.diff(a[:, 16]) > 0).sum())
    ok1 = np.isfinite(hs[1][:, 2])
    res["horizon"] = dict(searches=int(len(hs[1])), searches_without_result=int((~ok1).sum()),
                          times_without_result=hs[1][~ok1, 1].tolist(),
                          mass_last=float(hs[1][-1, 2]),
                          minradius_first=float(hs[1][ok1, 11][0]) if ok1.any() else None,
                          minradius_last=float(hs[1][-1, 11]))
    for n in RANKS[1:]:
        res["tracker_np%d" % n] = dict(
            identical=bool(mt.sha256(one(base, n, "*.co_0.txt")) == mt.sha256(one(base, 1, "*.co_0.txt"))),
            max_abs=float(np.abs(co[n][:, 2:5] - co[1][:, 2:5]).max())
            if co[n].shape == co[1].shape else None)
        if hs[n].shape == hs[1].shape and np.array_equal(np.isfinite(hs[n]), np.isfinite(hs[1])):
            # per search: mass (col 3), area (8), smallest radius (12), relative
            rel = np.abs(hs[n][ok1][:, [2, 7, 11]] - hs[1][ok1][:, [2, 7, 11]]) \
                / np.abs(hs[1][ok1][:, [2, 7, 11]])
            worst = int(np.argmax(rel.max(axis=1)))
            res["horizon_np%d" % n] = dict(
                same_searches_without_result=True,
                max_rel_mass=float(rel[:, 0].max()), max_rel_area=float(rel[:, 1].max()),
                max_rel_minradius=float(rel[:, 2].max()),
                time_of_largest=float(hs[1][ok1][worst, 1]),
                per_search=dict(t=hs[1][ok1, 1].tolist(), mass=rel[:, 0].tolist(),
                                minradius=rel[:, 2].tolist()))
        else:
            res["horizon_np%d" % n] = "different records or different searches without result"
    # positions of all tracked particles (records ordered by time, then tag)
    t1 = np.fromfile(one(base, 1, "*.traj.bin"), "<f8").reshape(-1, 8)
    res["traj_records"] = int(len(t1))
    dpos = {}
    for n in RANKS[1:]:
        tn = np.fromfile(one(base, n, "*.traj.bin"), "<f8").reshape(-1, 8)
        if tn.shape != t1.shape or not np.array_equal(tn[:, :2], t1[:, :2]):
            res["traj_np%d" % n] = "different records"
            continue
        d = np.abs(tn[:, 2:5] - t1[:, 2:5]).max(axis=1)
        times = np.unique(t1[:, 0])
        dpos[n] = (times, np.array([d[t1[:, 0] == t].max() for t in times]))
        res["traj_np%d" % n] = dict(identical=bool(np.array_equal(tn, t1)),
                                    max_abs_position=float(d.max()),
                                    max_abs_momentum=float(np.abs(tn[:, 5:] - t1[:, 5:]).max()))
    if a.shape[1] >= 12 and np.abs(a[:, 8]).max() > 0:
        res["identity"] = {("np%d" % n): float((np.abs(h[n][:, 8] - h[n][:, 4])
                                                / np.abs(h[n][:, 4])).max()) for n in RANKS}
        res["identity_difference"] = {
            ("np%d" % n): float(np.abs((h[n][:, 8] - h[n][:, 4]) - (a[:, 8] - a[:, 4])).max()
                                / np.abs(a[:, 4]).max()) for n in RANKS[1:]}
    return res, h, co, hs, dpos


def fig_ah(base, base_dep, figdirs):
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.1))
    out = {}
    res, h, co, hs, dpos = ah_numbers(base)
    out["t7_ah_exc"] = res
    # (a) particles near the plane of the puncture at the end, 1 and 4 ranks
    ax = fig.add_axes([0.075, 0.17, 0.25, 0.69])
    snaps = sorted(glob.glob(os.path.join(base, "np1", "*.part.*.bin")))
    first, last = snaps[0], snaps[-1]
    xc, yc, zc = co[1][-1, 2:5]
    t0, r0, g0 = mt.read_snapshot(first)
    gone = np.setdiff1d(g0, mt.read_snapshot(last)[2])
    sel0 = np.isin(g0, gone)
    ax.plot(r0[sel0, 0], r0[sel0, 1], "x", color="0.45", ms=3, mew=0.6,
            label="removed (at t = 0)")
    for n, mk, ms in ((1, "o", 3.2), (4, ".", 2.0)):
        t, rec, tag = mt.read_snapshot(os.path.join(base, "np%d" % n, os.path.basename(last)))
        sel = np.abs(rec[:, 2] - zc) < 0.25
        ax.plot(rec[sel, 0], rec[sel, 1], mk, color=COL[n], ms=ms, mfc="none" if n == 1 else COL[n],
                mew=0.6, label=lab(n))
    rmin = hs[1][-1, 11]
    th = np.linspace(0, 2*np.pi, 200)
    ax.plot(xc + rmin*np.cos(th), yc + rmin*np.sin(th), "k-", lw=0.8)
    ax.plot(xc + 0.8*rmin*np.cos(th), yc + 0.8*rmin*np.sin(th), "k--", lw=0.8)
    for v in np.arange(-2.0, 2.01, 1.0):
        ax.axvline(v, color="grey", lw=0.5, alpha=0.4)
        ax.axhline(v, color="grey", lw=0.5, alpha=0.4)
    ax.set_xlim(xc - 1.5, xc + 1.5)
    ax.set_ylim(yc - 1.5, yc + 1.5)
    ax.set_aspect("equal")
    ax.set_xlabel("x / M")
    ax.set_ylabel("y / M")
    ax.legend(loc="lower left", fontsize=5.5, frameon=True, framealpha=0.92, borderpad=0.3,
              handletextpad=0.2)
    ax.set_title("(a) t = %.2f M, |z - z_p| < 0.25" % mt.read_snapshot(last)[0], fontsize=9)
    # (b) excised number against time
    ax2 = fig.add_axes([0.42, 0.17, 0.22, 0.69])
    for name, b, lw in (("test particles", base, 1.6), ("with deposit", base_dep, 1.0)):
        if not b:
            continue
        hh = h if b == base else {n: mt.read_table(one(b, n, "*.nrpic.hst")) for n in RANKS}
        for n in RANKS:
            ax2.step(hh[n][:, 0], hh[n][:, 16], where="post", color=COL[n], ls=STY[n],
                     lw=lw - 0.2*RANKS.index(n),
                     label=(lab(n) + (", " + name)) if b == base else None)
    ax2.set_xlabel("t / M")
    ax2.set_ylabel("particles removed")
    ax2.legend(loc="lower right", fontsize=6)
    ax2.set_title("(b) removed inside 0.8 r_min", fontsize=9)
    # (c) differences from one rank
    ax3 = fig.add_axes([0.745, 0.17, 0.235, 0.69])
    sets = [("test particles", base, dpos, co, "-")]
    if base_dep:
        resd, hd, cod, hsd, dposd = ah_numbers(base_dep)
        out["t7_ah_exc_dep"] = resd
        sets.append(("with deposit", base_dep, dposd, cod, "--"))
    for name, b, dp, cc, ls in sets:
        for n in RANKS[1:]:
            if n in dp:
                ax3.semilogy(dp[n][0], np.maximum(dp[n][1], FLOOR), color=COL[n], ls=ls, lw=1.0,
                             label="%s, %s: positions" % (lab(n), name), clip_on=False)
            hr = (out["t7_ah_exc"] if b == base else out["t7_ah_exc_dep"]).get("horizon_np%d" % n)
            if isinstance(hr, dict):
                ax3.semilogy(hr["per_search"]["t"], np.maximum(hr["per_search"]["minradius"], FLOOR),
                             "s" if b == base else "D", color=COL[n], ms=3, mfc="none", mew=0.7,
                             label="%s, %s: horizon" % (lab(n), name), clip_on=False)
    ax3.axhline(2.2e-16, **fs.MASK_LINE)
    ax3.set_ylim(FLOOR, 1e-6)
    ax3.set_xlabel("t / M")
    ax3.set_ylabel("positions (abs.), horizon radius (rel.)", fontsize=7)
    ax3.legend(loc="center left", bbox_to_anchor=(0.0, 0.42), fontsize=4.8, frameon=True,
               framealpha=0.92, borderpad=0.3)
    ax3.set_title("(c) differences from 1 rank", fontsize=9)
    paths = []
    for d in figdirs:
        os.makedirs(d, exist_ok=True)
        paths += fs.save(fig, os.path.join(d, "t7_ah_exc"))
    plt.close(fig)
    return out, paths


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--analytic", default=None)
    ap.add_argument("--probes", default=None)
    ap.add_argument("--ahexc", default=None)
    ap.add_argument("--ahexc-dep", default=None)
    ap.add_argument("--figdir", action="append", default=[])
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    res = {}
    if a.probes:
        r, paths = fig_probes(a.analytic, a.probes, a.figdir)
        res.update(r)
        for p in paths:
            print("figure", p)
        if "analytic" in r:
            print("analytic:", r["analytic"])
        pr = r["probes"]
        print("probes: %d records, probe 1 equals probe 0: %s, E_max %.3e"
              % (pr["records"], pr["probe1_equals_probe0"], pr["E_max_all_probes"]))
        for row in pr["probes"]:
            print("  probe %d: alpha %.4f -> %.4f, max E %.3e; "
                  % (row["probe"], row["alpha_first"], row["alpha_last"], row["E_max"])
                  + "; ".join("np%d alpha %.1e E %.1e tau %.1e"
                              % (n, row["np%d" % n]["alpha"], row["np%d" % n]["E"],
                                 row["np%d" % n]["tau"]) for n in RANKS[1:]))
    if a.ahexc:
        r, paths = fig_ah(a.ahexc, a.ahexc_dep, a.figdir)
        res.update(r)
        for p in paths:
            print("figure", p)
        for k, v in r.items():
            print(k + ":", {q: ({a: b for a, b in w.items() if a != "per_search"}
                                if isinstance(w, dict) else w) for q, w in v.items()
                            if q not in ("t", "n_excised", "np_particles")})
            print("   n_excised np1:", v["n_excised"]["np1"])
    if a.out:
        with open(a.out, "w") as f:
            json.dump(res, f, indent=1)


if __name__ == "__main__":
    main()
