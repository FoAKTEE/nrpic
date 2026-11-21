#!/usr/bin/env python3
"""Card check of release candidate core-v0.6: the new cases of card_v06.list, run on one
A100 with the merged card executable, against processor runs of the merged processor
executable.  (The nine cases of core-v0.5 in the same list are judged by card_v05.py.)

    card_v06.py --card CARD_RUN_DIR --quick QUICK_RUN_DIR --r2 R2_RUN_DIR --out DIR

Cases and the processor run they are compared with:
  n_sp, n_7p   QUICK/<case>/new   Newtonian plane wave, Fourier solver, both symbols
  f_full       QUICK/f_full/new   vacuum puncture, 8 steps, the full set of faces options
  c_cd1        QUICK/c_cd1/new    Bowen-York puncture solved by id_solve (mode code), then
                                  8 steps with the faces options
  p5_mov_n64   R2/*__p5_mov_n64   puncture with momentum in a moving shell, 64 cells
  g_smr1       R2/*__g_smr1       Gaussian on one static level (BiCGStab)
Checks (prediction K6 of tracks/core/JOURNAL.md, 2026-11-21T12:55Z):
  status   every case ended with status 0 (batch.list.status);
  newton   columns of <base>.newton.hst above 1e-6 of the largest column: card and
           processors agree to 1e-10 of the column;
  faces    the same for every history of f_full and c_cd1, bound 1e-7;
  solver   outer iterations of the record <base>.idsolve.txt equal (within one on the
           refined mesh), psi_max equal to 1e-12 (1e-9 refined).
Reported: every history both runs have (largest difference of a column over the largest
magnitude of the column, columns above 1e-6 of the largest column of the file; and the
largest absolute difference of the other columns).
Writes DIR/card_v06.json and DIR/fig_card_v06.{pdf,png}; exit status 0 if all hold.
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "python"))
import quick_v06 as qk                         # noqa: E402

NEW = ("n_sp", "n_7p", "f_full", "c_cd1", "p5_mov_n64", "g_smr1")


def status(card):
    rc = {}
    path = os.path.join(card, "batch.list.status")
    if os.path.exists(path):
        for ln in open(path):
            p = ln.split()
            if len(p) >= 3 and p[1].startswith("rc="):
                rc[os.path.basename(p[2])] = int(p[1][3:])
    return rc


def hst_pair(pa, pb):
    try:
        a, b = np.loadtxt(pa, ndmin=2), np.loadtxt(pb, ndmin=2)
    except ValueError as e:
        return dict(error=str(e))
    if a.shape != b.shape:
        return dict(error="shapes %s and %s" % (a.shape, b.shape))
    if not (np.isfinite(a).all() and np.isfinite(b).all()):
        return dict(error="non-finite value")
    mag = np.maximum(np.abs(a).max(axis=0), np.abs(b).max(axis=0))
    big = mag > 1e-6*mag.max() if mag.size else mag > 0
    d = np.abs(a - b).max(axis=0)
    rel = np.where(big, d/np.where(mag > 0, mag, 1.0), 0.0)
    return dict(records=int(a.shape[0]), columns=int(a.shape[1]),
                rel_large=float(rel.max()) if rel.size else 0.0,
                column=int(rel.argmax()) + 1 if rel.size else 0,
                abs_small=float(d[~big].max()) if (~big).any() else 0.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--card", required=True)
    ap.add_argument("--quick", required=True)
    ap.add_argument("--r2", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rc = status(a.card)
    cpu = {n: os.path.join(a.quick, n, "new") for n in NEW[:4]}
    for n in NEW[4:]:
        g = glob.glob(os.path.join(a.r2, "*__" + n))
        cpu[n] = g[0] if g else ""
    rep = dict(card=a.card, cpu=cpu, status={n: rc.get(n) for n in NEW}, cases={})
    checks = {"status": all(rc.get(n) == 0 for n in NEW)}
    worst = {}
    for n in NEW:
        dc, dp = os.path.join(a.card, n), cpu[n]
        e = dict(hst={})
        for p in sorted(glob.glob(os.path.join(dp, "*.hst"))):
            q = os.path.join(dc, os.path.basename(p))
            e["hst"][os.path.basename(p)] = (hst_pair(q, p) if os.path.exists(q)
                                             else dict(error="missing on the card"))
        rec = glob.glob(os.path.join(dp, "*.idsolve.txt"))
        if rec:
            e["solve_cpu"] = qk.idsolve_record(rec[0])
            e["solve_card"] = qk.idsolve_record(os.path.join(dc, os.path.basename(rec[0])))
        rep["cases"][n] = e
        rels = [v.get("rel_large", float("inf")) for v in e["hst"].values()]
        worst[n] = max(rels) if rels else float("nan")
        print("%-11s exit %s  histories %d  worst large column %.2e  %s" % (
            n, rc.get(n), len(e["hst"]), worst[n],
            "solve cpu %s card %s" % (e["solve_cpu"], e["solve_card"]) if rec else ""))

    def hst_ok(n, pat, bound):
        hs = [v for k, v in rep["cases"][n]["hst"].items() if pat in k]
        return bool(hs) and all(v.get("rel_large", float("inf")) <= bound for v in hs)

    def solve_ok(n, dit, bound):
        c, g = rep["cases"][n].get("solve_cpu"), rep["cases"][n].get("solve_card")
        if not c or not g or c["outer"] is None or g["outer"] is None:
            return False
        return (abs(c["outer"] - g["outer"]) <= dit and
                abs(c["psi_max"] - g["psi_max"]) <= bound*abs(c["psi_max"]))

    checks["newton"] = hst_ok("n_sp", ".newton.hst", 1e-10) and \
        hst_ok("n_7p", ".newton.hst", 1e-10)
    checks["faces"] = hst_ok("f_full", ".hst", 1e-7) and hst_ok("c_cd1", ".hst", 1e-7)
    checks["solver"] = (solve_ok("c_cd1", 0, 1e-12) and solve_ok("p5_mov_n64", 0, 1e-12)
                        and solve_ok("g_smr1", 1, 1e-9))
    rep["checks"] = checks
    with open(os.path.join(a.out, "card_v06.json"), "w") as f:
        json.dump(rep, f, indent=1)
    for k, v in checks.items():
        print("%-7s %s" % (k, "held" if v else "FAILED"))

    from nrpic import figstyle as fs
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(1, 1, figsize=(fs.FULL_WIDTH, 2.6))
    labels, vals, cols = [], [], []
    pal = [fs.PAL["blue"], fs.PAL["orange"], fs.PAL["red"], fs.PAL["green"]
           if "green" in fs.PAL else "0.4"]
    for n in NEW:
        for i, (k, v) in enumerate(rep["cases"][n]["hst"].items()):
            labels.append("%s\n%s" % (n, k.split(".", 1)[1].replace(".hst", "")))
            vals.append(max(v.get("rel_large", 1.0), 1e-18))
            cols.append(pal[i % len(pal)])
    x = np.arange(len(vals))
    ax.bar(x, vals, color=cols)
    ax.set_yscale("log")
    ax.set_ylim(1e-18, 1e-2)
    ax.axhline(1e-10, color=fs.PAL["blue"], ls="--", lw=0.6)
    ax.axhline(1e-7, color=fs.PAL["red"], ls="--", lw=0.6)
    ax.text(len(vals) - 0.5, 2e-10, "bound of the Newtonian history", fontsize=5, ha="right")
    ax.text(len(vals) - 0.5, 2e-7, "bound of the histories with the faces options",
            fontsize=5, ha="right")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=4, rotation=60, ha="right")
    ax.set_ylabel("card against processors:\nlargest column difference / column", fontsize=6)
    fig.tight_layout()
    fs.save(fig, os.path.join(a.out, "fig_card_v06"))
    plt.close(fig)
    ok = all(checks.values())
    print("CARD", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
