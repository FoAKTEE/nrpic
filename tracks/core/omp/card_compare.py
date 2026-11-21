#!/usr/bin/env python3
"""Card smoke test of work package omp (prediction P13 of JOURNAL-omp.md): the outputs of
the card executable of this branch for the deposit cases dep and east against one thread
of the threaded processor executable, file by file, with the measures of omplib
(rel_max: largest difference over the largest number of the file), and the conservation
identity of the deposit from each run's history.

    card_compare.py --card DIR --ref DIR [--tol 1e-10] [--idtol 1e-13] --out DIR

--card  output directory of the card run (card_smoke.list: DIR/dep, DIR/east)
--ref   directory of a regression run of regress.py (DIR/<case>/O3_1, O3_4, O3_16)
Writes OUT/card_compare.json and OUT/figs/card_diff.{png,pdf}. Only files that both runs
wrote are compared (the processor regression adds a restart file to east; the card list
does not); files that one side lacks are listed, not judged. Exit status 1 if a
difference exceeds --tol, the identity exceeds --idtol, or a compared file differs in
shape or holds a non-finite number.
"""
import argparse
import filecmp
import glob
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "python"))
import omplib as L  # noqa: E402

CASES = ("dep", "east")
OTHER = ("O3_4", "O3_16")      # processor runs at 4 and 16 threads, for scale


def data_files(d):
    out = []
    for pat in ("*.hst", "*.bin", "*.txt"):
        out += [os.path.basename(f) for f in glob.glob(os.path.join(d, pat))]
    return sorted(set(out))


def diff(fa, fb):
    if filecmp.cmp(fa, fb, shallow=False):
        return {"kind": "identical", "rel_max": 0.0, "rel_floor": 0.0, "ndiff": 0}
    return L.number_diff(fa, fb)


def identity(rundir):
    """|int_E - sum_mW|/sum_mW and |int_S - sum_mu|/sum_mW per history row."""
    f = glob.glob(os.path.join(rundir, "*.nrpic.hst"))
    h = np.loadtxt(f[0], comments="#", ndmin=2)
    smw = np.abs(h[:, 4])
    return (h[:, 0], np.abs(h[:, 8] - h[:, 4])/smw,
            np.max(np.abs(h[:, 9:12] - h[:, 5:8]), axis=1)/smw)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--card", required=True)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--tol", type=float, default=1.0e-10)
    ap.add_argument("--idtol", type=float, default=1.0e-13)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", ""))
    a = ap.parse_args()
    os.makedirs(os.path.join(a.out, "figs"), exist_ok=True)
    res = {"card": a.card, "ref": a.ref, "tol": a.tol, "idtol": a.idtol, "cases": {}}
    bad = 0
    for case in CASES:
        cd = os.path.join(a.card, case)
        rd = os.path.join(a.ref, case, "O3_1")
        fc, fr = data_files(cd), data_files(rd)
        both = [f for f in fc if f in fr]
        c = {"compared": {}, "only_card": [f for f in fc if f not in fr],
             "only_ref": [f for f in fr if f not in fc], "threads": {}, "identity": {}}
        for f in both:
            r = diff(os.path.join(cd, f), os.path.join(rd, f))
            c["compared"][f] = r
            hard = r["kind"] in ("size", "text-shape") or r.get("nonfinite", 0) \
                or r.get("int_columns_differ", 0)
            flag = hard or r.get("rel_max", 0.0) > a.tol
            bad += int(bool(flag))
            print("%-5s card vs O3:1  %-22s %-10s ndiff %7s  rel_max %.2e  rel_floor %.2e%s"
                  % (case, f, r["kind"], r.get("ndiff", "-"), r.get("rel_max", 0.0),
                     r.get("rel_floor", 0.0), "  FAIL" if flag else ""))
        for o in OTHER:
            od = os.path.join(a.ref, case, o)
            if os.path.isdir(od):
                c["threads"][o] = {f: diff(os.path.join(od, f), os.path.join(rd, f))
                                   for f in both if os.path.exists(os.path.join(od, f))}
        for lab, d in [("card", cd), ("O3_1", rd)] + [(o, os.path.join(a.ref, case, o))
                                                     for o in OTHER]:
            if os.path.isdir(d):
                t, de, ds = identity(d)
                c["identity"][lab] = {"t": t.tolist(), "E": de.tolist(), "S": ds.tolist(),
                                      "E_max": float(de.max()), "S_max": float(ds.max())}
                flag = lab == "card" and max(de.max(), ds.max()) > a.idtol
                bad += int(bool(flag))
                print("%-5s identity %-5s  max |int_E - sum_mW|/sum_mW %.2e   "
                      "max |int_S - sum_mu|/sum_mW %.2e%s"
                      % (case, lab, de.max(), ds.max(), "  FAIL" if flag else ""))
        res["cases"][case] = c
    res["failures"] = bad
    L.dump(res, os.path.join(a.out, "card_compare.json"))
    figure(res, os.path.join(a.out, "figs", "card_diff"))
    print("failures: %d" % bad)
    return 1 if bad else 0


def figure(res, out):
    """Left: per output file, the largest difference over the largest number of the file,
    card against one processor thread (filled) and 4 and 16 processor threads against one
    (open), with the bound of P13 (dashed). Right: the conservation identity of the
    deposit against time for the east case (lines) and the dep case (dots at the left)."""
    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    floor = 1.0e-19
    rows = [(case, f) for case in CASES for f in res["cases"][case]["compared"]]
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 4.4),
                            gridspec_kw={"width_ratios": [1.25, 1.0]})
    fig.subplots_adjust(left=0.215, right=0.985, bottom=0.12, top=0.97, wspace=0.27)
    ax = axs[0]
    sty = {"card": ("o", fs.SERIES[1], fs.SERIES[1], "one A100 against one thread"),
           "O3_4": ("s", fs.SERIES[0], "none", "4 threads against one thread"),
           "O3_16": ("D", fs.SERIES[3], "none", "16 threads against one thread")}
    for i, (case, f) in enumerate(rows):
        c = res["cases"][case]
        vals = {"card": c["compared"][f].get("rel_max", 0.0)}
        for o in OTHER:
            if f in c["threads"].get(o, {}):
                vals[o] = c["threads"][o][f].get("rel_max", 0.0)
        for n, (k, v) in enumerate(vals.items()):
            mk, col, mfc, lab = sty[k]
            ax.plot([max(v, floor)], [i + (n - 1)*0.2], mk, color=col, mfc=mfc, ms=5,
                    label=lab if i == 0 else None)
    ax.axvline(res["tol"], **fs.GUIDE)
    ax.axvline(floor, **fs.MASK_LINE)
    ax.text(floor*2.0, -0.95, "identical", fontsize=8, color="0.4")
    ax.set_xscale("log")
    ax.set_xlim(floor/5, 1.0e-7)
    ax.set_xticks([1e-18, 1e-15, 1e-12, 1e-9])
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([f for _, f in rows], fontsize=7)
    ax.tick_params(axis="y", which="minor", left=False, right=False)
    ax.set_ylim(len(rows) - 0.4, -1.4)
    ax.set_xlabel("largest difference / largest number of the file")
    ax.legend(loc="lower right", fontsize=7)
    ax = axs[1]
    col = {"card": fs.SERIES[1], "O3_1": "0.2", "O3_4": fs.SERIES[0], "O3_16": fs.SERIES[3]}
    name = {"card": "one A100", "O3_1": "1 thread", "O3_4": "4 threads",
            "O3_16": "16 threads"}
    for lab, v in res["cases"]["east"]["identity"].items():
        ax.plot(v["t"], np.maximum(v["E"], 1e-18), "-", color=col[lab], lw=1.5,
                label="east, " + name[lab])
    for lab, v in res["cases"]["dep"]["identity"].items():
        ax.plot(v["t"], np.maximum(v["E"], 1e-18), ":", color=col[lab], lw=1.5,
                label="dep, " + name[lab] if lab == "card" else None)
    ax.axhline(res["idtol"], **fs.GUIDE)
    ax.set_yscale("log")
    ax.set_ylim(1.0e-17, 1.0e-11)
    ax.set_xlabel("time")
    ax.set_ylabel(r"$|\int E - \sum mW| / \sum mW$")
    ax.legend(loc="upper right", fontsize=7, ncol=2)
    fs.save(fig, out)
    print("wrote", out + ".png")


if __name__ == "__main__":
    sys.exit(main())
