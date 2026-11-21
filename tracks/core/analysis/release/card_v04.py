#!/usr/bin/env python3
"""Card check of release candidate core-v0.4: the cases of card_v04.list (the READY
example of every merged branch, run on one A100 with the merged card executable) against
the processor runs of the same inputs made by quick_v04.py with the merged processor
executable.

    card_v04.py --card CARD_RUN_DIR --cpu QUICK_RUN_DIR --out DIR

Checks (prediction C of tracks/core/JOURNAL.md, 2026-11-20 and 2026-11-21):
  C1  every case of the list ended with status 0 (batch.list.status);
  C2  the numbers of quick_v04.py, computed from the card runs, lie in the same bands;
  C3  counts: outer iterations of the initial-data solve, collisions per step, pairs
      without a root, equal to the processor run;
  C4  card against processor: tracer radius, constraint norms of the clump at t = 0,
      lapse of the homogeneous universe, snapshots of the perturbing-force case;
  C5  linear wave: absolute difference of the error norms; the first session's bound
      (1e-12 relative) is evaluated and reported beside it.
Also, for every history file both runs have, the largest difference of a column over
the largest magnitude of that column (reported, not judged).
Writes DIR/card_summary.json and DIR/fig_card_v04.{pdf,png}; exit status 0 if C1 to C5
hold.
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
import quick_v04 as qk                         # noqa: E402

CASES = ["lw16", "lw32", "leak", "eta", "sr", "clump", "clump0", "ids", "tracer", "pert",
         "coll"]
BOUND = {"tracer_dr": 1.0e-9, "clump_norm": 1.0e-10, "leak_alpha": 1.0e-10,
         "pert_snap": 1.0e-12, "lw_abs": 1.0e-14, "lw_rel_first_session": 1.0e-12}


def status(card):
    rc = {}
    path = os.path.join(card, "batch.list.status")
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                tok = line.split()
                if len(tok) >= 3 and tok[1].startswith("rc="):
                    rc[os.path.basename(tok[2])] = int(tok[1][3:])
    return rc


def table(path):
    """numeric rows of a history file (comment lines skipped)."""
    return np.atleast_2d(np.loadtxt(path))


def hst_difference(a, b):
    """largest |a - b| of a column over the largest magnitude of that column, with the
    index of the column (1-based) where it is reached; the shapes if they differ."""
    ta, tb = table(a), table(b)
    if ta.shape != tb.shape:
        return {"shape_card": list(ta.shape), "shape_cpu": list(tb.shape)}
    # columns a run does not fill hold nan or inf: such entries count as equal when
    # both runs have the same one, and are counted when they differ
    bad = ~np.isfinite(ta) | ~np.isfinite(tb)
    mismatch = int(np.sum(bad & ~((ta == tb) | (np.isnan(ta) & np.isnan(tb)))))
    ta, tb = np.where(bad, 0.0, ta), np.where(bad, 0.0, tb)
    scale = np.maximum(np.abs(ta).max(axis=0), np.abs(tb).max(axis=0))
    d = np.abs(ta - tb).max(axis=0)
    ok = scale > 0.0
    rel = np.where(ok, d/np.where(ok, scale, 1.0), 0.0)
    j = int(np.argmax(rel))
    return {"rows": int(ta.shape[0]), "columns": int(ta.shape[1]),
            "max_rel": float(rel[j]), "column": j + 1,
            "equal_columns": int(np.sum(d == 0.0)), "nonfinite_mismatch": mismatch}


def snapshot(path):
    """(time, N, array N x 7 of x^i, u_i, m) of <base>.part.NNNNN.bin (docs/FORMATS.md)."""
    with open(path, "rb") as f:
        buf = f.read()
    assert buf[:8] == b"NRPSNAP1", path
    t = float(np.frombuffer(buf, "<f8", 1, 8)[0])
    n = int(np.frombuffer(buf, "<i8", 1, 16)[0])
    return t, n, np.frombuffer(buf, "<f8", 7*n, 32).reshape(n, 7)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--card", required=True)
    ap.add_argument("--cpu", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    card, cpu, out = (os.path.abspath(x) for x in (a.card, a.cpu, a.out))
    os.makedirs(out, exist_ok=True)

    def c(case, name):
        return os.path.join(card, case, name)

    def p(case, name):
        return os.path.join(cpu, case, "new", name)

    summ = {"card_run": card, "cpu_run": cpu, "bounds": BOUND, "checks": {}}
    ck = summ["checks"]

    # C1
    rc = status(card)
    summ["status"] = {n: rc.get(n) for n in CASES}
    ck["C1_all_status_0"] = all(rc.get(n) == 0 for n in CASES)
    have = [n for n in CASES if rc.get(n) == 0]

    # C2: the numbers of the quick test from the card runs (a tree of links with the
    # layout quick_v04.evaluate reads)
    tree = os.path.join(out, "tree")
    for n in have:
        os.makedirs(os.path.join(tree, n), exist_ok=True)
        dst = os.path.join(tree, n, "new")
        if not os.path.lexists(dst):
            os.symlink(os.path.join(card, n), dst)
    num, curves = qk.evaluate(tree, have)
    with open(os.path.join(cpu, "summary.json")) as f:
        ref = json.load(f)["numbers"]
    summ["numbers"] = {}
    for k, v in num.items():
        r = ref[k]["value"]
        v["cpu"] = r
        v["abs_diff"] = abs(v["value"] - r)
        v["rel_diff"] = abs(v["value"] - r)/abs(r) if r != 0.0 else abs(v["value"])
        summ["numbers"][k] = v
    ck["C2_numbers_inside_bands"] = (len(num) == len(ref)
                                     and all(v["inside"] for v in num.values()))

    # C3: counts
    cnt = {}
    if "ids" in have:
        ra = table(c("ids", "gauss.idsolve.txt"))
        rb = table(p("ids", "gauss.idsolve.txt"))
        cnt["ids_outer_iterations"] = [int(ra[-1, 0]), int(rb[-1, 0])]
        cnt["ids_cg_steps_equal"] = bool(ra.shape == rb.shape
                                         and np.array_equal(ra[:, 10], rb[:, 10]))
        cnt["ids_v_cycles_equal"] = bool(ra.shape == rb.shape
                                         and np.array_equal(ra[:, 11], rb[:, 11]))
    if "coll" in have:
        ha = qk.hst(c("coll", "box.coll.hst"))
        hb = qk.hst(p("coll", "box.coll.hst"))
        cnt["coll_collisions"] = [int(ha["n_coll"].sum()), int(hb["n_coll"].sum())]
        cnt["coll_per_step_equal"] = bool(np.array_equal(ha["n_coll"], hb["n_coll"]))
        cnt["coll_n_noroot"] = [int(ha["n_noroot"].sum()), int(hb["n_noroot"].sum())]
        cnt["coll_n_balance"] = [int(ha["n_balance"].sum()), int(hb["n_balance"].sum())]
    summ["counts"] = cnt
    ck["C3_counts_equal"] = bool(
        cnt.get("ids_outer_iterations", [0, 1])[0] == cnt.get("ids_outer_iterations",
                                                              [0, 1])[1]
        and cnt.get("coll_per_step_equal", False)
        and cnt.get("coll_n_noroot", [1, 1]) == [0, 0])

    # C4: card against processor
    dif = {}
    if "tracer" in have:
        ta = np.fromfile(c("tracer", "trc.traj.bin")).reshape(-1, 8)
        tb = np.fromfile(p("tracer", "trc.traj.bin")).reshape(-1, 8)
        if ta.shape == tb.shape:
            dr = np.abs(np.linalg.norm(ta[:, 2:5], axis=1)
                        - np.linalg.norm(tb[:, 2:5], axis=1))
            dif["tracer_dr"] = float(dr.max())
            dif["tracer_dx"] = float(np.abs(ta[:, 2:5] - tb[:, 2:5]).max())
            curves["tracer_dr"] = {"t": ta[::10, 0].tolist(), "dr": dr[::10].tolist()}
    if "clump" in have:
        ha = qk.hst(c("clump", "clump.z4c.user.hst"))
        hb = qk.hst(p("clump", "clump.z4c.user.hst"))
        dif["clump_norm"] = float(max(abs(ha[k][0]/hb[k][0] - 1.0)
                                      for k in ("M-norm2", "H-norm2")))
    if "leak" in have:
        ha = qk.hst(c("leak", "flrwleak.nrpic.hst"))
        hb = qk.hst(p("leak", "flrwleak.nrpic.hst"))
        if ha["time"].shape == hb["time"].shape:
            dif["leak_time_equal"] = bool(np.array_equal(ha["time"], hb["time"]))
            dif["leak_alpha"] = float(np.abs(ha["alpha_max"]/hb["alpha_max"] - 1.0).max())
    if "pert" in have:
        d = 0.0
        files = sorted(glob.glob(c("pert", "pert.part.*.bin")))
        for f in files:
            t1, n1, x1 = snapshot(f)
            t2, n2, x2 = snapshot(p("pert", os.path.basename(f)))
            d = max(d, abs(t1 - t2), float(np.abs(x1 - x2).max()) if n1 == n2 else 1.0)
        dif["pert_snap"] = d if files else None
        dif["pert_files"] = len(files)
    summ["card_minus_cpu"] = dif
    ck["C4_differences_in_bounds"] = all(
        dif.get(k) is not None and dif[k] <= BOUND[k]
        for k in ("tracer_dr", "clump_norm", "leak_alpha", "pert_snap"))

    # C5: linear wave
    lw = {}
    for n in (16, 32):
        if "lw%d" % n in have:
            ea = float(table(c("lw%d" % n, "lwo-errs.dat"))[-1, 4])
            eb = float(table(p("lw%d" % n, "lwo-errs.dat"))[-1, 4])
            lw[str(n)] = {"card": ea, "cpu": eb, "abs_diff": abs(ea - eb),
                          "rel_diff": abs(ea - eb)/eb}
    summ["linear_wave"] = lw
    ck["C5_lw_abs_diff_in_bound"] = (len(lw) == 2 and all(
        v["abs_diff"] <= BOUND["lw_abs"] for v in lw.values()))
    ck["first_session_lw_rel_1e-12"] = (len(lw) == 2 and all(
        v["rel_diff"] <= BOUND["lw_rel_first_session"] for v in lw.values()))

    # every history file both runs have (reported)
    hist = {}
    for n in have:
        for f in sorted(glob.glob(c(n, "*.hst"))):
            g = p(n, os.path.basename(f))
            if os.path.exists(g):
                hist["%s/%s" % (n, os.path.basename(f))] = hst_difference(f, g)
    summ["histories"] = hist

    judged = ("C1_all_status_0", "C2_numbers_inside_bands", "C3_counts_equal",
              "C4_differences_in_bounds", "C5_lw_abs_diff_in_bound")
    summ["verdict"] = "PASS" if all(ck[k] for k in judged) else "FAIL"
    with open(os.path.join(out, "card_summary.json"), "w") as f:
        json.dump(summ, f, indent=1)
        f.write("\n")
    figure(out, summ, curves)

    for n in CASES:
        print("status %-7s %s" % (n, summ["status"][n]))
    for k, v in summ["numbers"].items():
        print("%-24s card %.9g  cpu %.9g  rel diff %.2e  %s"
              % (k, v["value"], v["cpu"], v["rel_diff"],
                 "inside" if v["inside"] else "OUTSIDE"))
    print("counts", json.dumps(cnt))
    print("card minus cpu", json.dumps(dif))
    print("linear wave", json.dumps(lw))
    for k, v in hist.items():
        print("history %-28s %s" % (k, json.dumps(v)))
    for k, v in ck.items():
        print("%-32s %s" % (k, v))
    print("CARD CHECK", summ["verdict"])
    return 0 if summ["verdict"] == "PASS" else 1


def figure(out, summ, curves):
    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 3.6))
    fig.subplots_adjust(left=0.215, right=0.985, bottom=0.14, top=0.92, wspace=0.95)
    red, blue = fs.PAL["red"], fs.PAL["blue"]
    floor = 1.0e-17

    a = ax[0]
    keys = list(summ["numbers"])
    y = np.arange(len(keys))[::-1]
    rel = np.array([max(summ["numbers"][k]["rel_diff"], floor) for k in keys])
    a.semilogx(rel, y, "o", color=red)
    a.axvline(2.2e-16, **fs.GUIDE)
    a.set_yticks(y)
    a.set_yticklabels([k.replace("_", " ") for k in keys], fontsize=8)
    a.tick_params(axis="y", which="minor", left=False, right=False)
    a.set_xlim(floor/3, 1.0)
    a.set_xlabel("|card - processor| / |processor|", labelpad=2)
    a.set_title("numbers of the quick test", fontsize=10)

    a = ax[1]
    hk = [k for k, v in summ["histories"].items() if "max_rel" in v]
    y = np.arange(len(hk))[::-1]
    rel = np.array([max(summ["histories"][k]["max_rel"], floor) for k in hk])
    a.semilogx(rel, y, "s", color=red)
    a.axvline(2.2e-16, **fs.GUIDE)
    a.set_yticks(y)
    a.set_yticklabels([k.replace(".hst", "") for k in hk], fontsize=7)
    a.tick_params(axis="y", which="minor", left=False, right=False)
    a.set_xlim(floor/3, 1.0)
    a.set_xlabel("largest column difference / column maximum", labelpad=2)
    a.set_title("history files", fontsize=10)

    a = ax[2]
    lw = summ["linear_wave"]
    if len(lw) == 2:
        n = np.array([16.0, 32.0])
        a.loglog(n, [lw["16"]["cpu"], lw["32"]["cpu"]], "o-", color=blue,
                 label="processor")
        a.loglog(n, [lw["16"]["card"], lw["32"]["card"]], "x--", color=red, label="card")
        a.loglog(n, [max(lw["16"]["abs_diff"], floor), max(lw["32"]["abs_diff"], floor)],
                 "s:", color=red, label="|difference|")
        a.loglog(n, lw["16"]["cpu"]*(n/16.0)**-6, label=r"$N^{-6}$", **fs.GUIDE)
        a.set_xticks([16, 32])
        a.set_xticklabels(["16", "32"])
        a.minorticks_off()
        a.legend(loc="center left", fontsize=8)
    a.set_xlabel("cells per side $N$", labelpad=2)
    a.set_ylabel(r"$L_1$ error of $\tilde\gamma_{ij}$, oblique wave")
    a.set_title("linear wave", fontsize=10)
    fs.save(fig, os.path.join(out, "fig_card_v04"))


if __name__ == "__main__":
    sys.exit(main())
