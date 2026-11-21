#!/usr/bin/env python3
"""Card check of release candidate core-v0.5: the cases of card_v05.list (decks that
quick_v05.py wrote for the processor runs, run on one A100 with the merged card
executable) against those processor runs of the merged processor executables.

    card_v05.py --card CARD_RUN_DIR --cpu QUICK_RUN_DIR --out DIR

Cases (processor run they are compared with, relative to QUICK_RUN_DIR):
  s3g, usr      byte/<case>/new          scalar field with stochastic sources, 12 steps
  trk, peak     byte/<case>/new          tracker in a periodic box; peak with the lapse
                                         ladder and the fine-shape deposit (adaptive)
  dep, depp     threads/d_ser0, d_ser    deposit on a refined mesh; with deposit_threads
                                         = private (a card adds atomically and says so)
  fine, finet   threads/f_ser, g_ser     the same with deposit_fine_shape, cic and tsc
  cluster       mpi/t3_cluster/np1       self-gravitating cluster with every diagnostic
Checks (prediction C of tracks/core/JOURNAL.md, 2026-11-21):
  K1  every case ended with status 0 (batch.list.status);
  K2  the particle sums and the mesh integrals of the sources (columns 4 to 12 of
      <base>.nrpic.hst) agree with the processor run to 1e-10 of sum m W;
  K3  the deposit identity holds on the card to 1e-13 (energy and momentum);
  K4  MeshBlock counts of trk and peak equal at every record; tracker of trk within
      1e-12 of the processor path;
  K5  dumps of the sources (double precision) of dep, depp, fine, finet within 1e-12
      of the largest number of the dump;
  K6  depp prints the note that it adds atomically.
Reported, not judged: for every history both runs have, the largest difference of a
column over the largest magnitude of that column, separately for the columns above
1e-6 of the largest column of the file and for the others (sums that vanish, constraint
norms at rounding level).
Writes DIR/card_summary.json and DIR/fig_card_v05.{pdf,png}; exit status 0 if K1 to K6
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
import quick_v05 as qk                         # noqa: E402

CASES = {"s3g": "byte/s3g/new", "usr": "byte/usr/new", "trk": "byte/trk/new",
         "peak": "byte/peak/new", "dep": "threads/d_ser0", "depp": "threads/d_ser",
         "fine": "threads/f_ser", "finet": "threads/g_ser",
         "cluster": "mpi/t3_cluster/np1"}
DEPOSIT = ("trk", "peak", "dep", "depp", "fine", "finet", "cluster")
DUMPS = ("dep", "depp", "fine", "finet")


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


def hst_columns(a, b):
    """(worst relative difference of the columns above 1e-6 of the largest column,
    its column, worst absolute difference of the other columns) or None."""
    try:
        x, y = qk.table(a), qk.table(b)
    except (OSError, ValueError):
        return None
    if x.shape != y.shape:
        return {"shape": [list(x.shape), list(y.shape)]}
    fin = np.isfinite(x) & np.isfinite(y)
    sc = np.where(fin, np.abs(x), 0.0).max(axis=0)
    df = np.where(fin, np.abs(x - y), 0.0).max(axis=0)
    big = sc >= 1.0e-6*sc.max()
    rel = np.where(big, df/np.maximum(sc, 1.0e-300), 0.0)
    return {"records": int(x.shape[0]), "columns": int(x.shape[1]),
            "max_rel_large_columns": float(rel.max()), "column": int(np.argmax(rel)) + 1,
            "max_abs_small_columns": float(np.where(big, 0.0, df).max()),
            "nonfinite_mismatch": bool((np.isfinite(x) != np.isfinite(y)).any())}


def nrpic_hst(d):
    g = sorted(glob.glob(os.path.join(d, "*.nrpic.hst")))
    return g[0] if g else None


def sums_against(dc, dp):
    a, b = qk.table(nrpic_hst(dc)), qk.table(nrpic_hst(dp))
    if a.shape != b.shape:
        return float("inf")
    smw = np.maximum(np.abs(b[:, 4]), 1.0e-300)
    return float((np.abs(a[:, 3:12] - b[:, 3:12]).max(axis=1)/smw).max())


def identity(d):
    h = qk.table(nrpic_hst(d))
    smw = np.abs(h[:, 4])
    ok = smw > 0
    return float(max((np.abs(h[ok, 8] - h[ok, 4])/smw[ok]).max(),
                     (np.abs(h[ok, 9:12] - h[ok, 5:8]).max(axis=1)/smw[ok]).max()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--card", required=True)
    ap.add_argument("--cpu", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    card, cpu, out = (os.path.abspath(v) for v in (a.card, a.cpu, a.out))
    os.makedirs(out, exist_ok=True)
    rc = status(card)
    res = {"exit": rc, "cases": {}}
    k = {"K1": all(rc.get(n) == 0 for n in CASES)}
    sums, idn, dumps, hist = {}, {}, {}, {}
    for n, rel in CASES.items():
        dc, dp = os.path.join(card, n), os.path.join(cpu, rel)
        r = {"histories": {}}
        for f in sorted(glob.glob(os.path.join(dp, "*.hst"))):
            g = os.path.join(dc, os.path.basename(f))
            if os.path.exists(g) and not f.endswith(".mpi.hst"):
                r["histories"][os.path.basename(f)] = hst_columns(g, f)
        hist[n] = max([v["max_rel_large_columns"] for v in r["histories"].values()
                       if v and "max_rel_large_columns" in v] or [0.0])
        if n in DEPOSIT and nrpic_hst(dc) and nrpic_hst(dp):
            sums[n] = sums_against(dc, dp)
            idn[n] = identity(dc)
            r["sums_vs_cpu"], r["identity_card"] = sums[n], idn[n]
            hc, hp = qk.table(nrpic_hst(dc)), qk.table(nrpic_hst(dp))
            r["meshblocks_equal"] = bool(hc.shape == hp.shape
                                         and np.array_equal(hc[:, 22], hp[:, 22]))
            r["meshblocks_first_last"] = [int(hc[0, 22]), int(hc[-1, 22])]
        if n in DUMPS:
            dumps[n] = qk.field_diff(dc, dp)
            r["dump_vs_cpu"] = dumps[n]
        res["cases"][n] = r
    k["K2"] = bool(sums) and all(v <= 1.0e-10 for v in sums.values()) \
        and set(sums) == set(DEPOSIT)
    k["K3"] = bool(idn) and all(v <= 1.0e-13 for v in idn.values())
    trk = {}
    try:
        tc = np.loadtxt(os.path.join(card, "trk", "flrw.co_0.txt"), ndmin=2)
        tp = np.loadtxt(os.path.join(cpu, CASES["trk"], "flrw.co_0.txt"), ndmin=2)
        trk["records"] = [int(len(tc)), int(len(tp))]
        trk["path_vs_cpu"] = (float(np.abs(tc[:, 2:5] - tp[:, 2:5]).max())
                              if tc.shape == tp.shape else float("inf"))
    except OSError as exc:
        trk["error"] = repr(exc)
    res["tracker"] = trk
    k["K4"] = (res["cases"]["trk"].get("meshblocks_equal", False)
               and res["cases"]["peak"].get("meshblocks_equal", False)
               and trk.get("path_vs_cpu", float("inf")) <= 1.0e-12)
    k["K5"] = bool(dumps) and all(v <= 1.0e-12 for v in dumps.values())
    note = []
    for f in glob.glob(os.path.join(card, "depp", "*.log")):
        note += qk.grep(f, ["deposit_threads"])
    res["depp_note"] = note[:1]
    k["K6"] = bool(note)
    res["checks"] = k
    res["verdict"] = "PASS" if all(k.values()) else "FAIL"
    with open(os.path.join(out, "card_summary.json"), "w") as f:
        json.dump(res, f, indent=1)
        f.write("\n")
    for n in CASES:
        print("%-8s exit %s  history %.2e  sums %s  identity %s  dump %s"
              % (n, rc.get(n), hist[n], "%.2e" % sums[n] if n in sums else "-",
                 "%.2e" % idn[n] if n in idn else "-",
                 "%.2e" % dumps[n] if n in dumps else "-"))
    for key, v in k.items():
        print(key, "held" if v else "FAILED")

    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(9.0, 3.3))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.17, top=0.90, wspace=0.28)
    names = list(CASES)
    x = np.arange(len(names))
    w = 0.26
    for i, (lab, dct, bound) in enumerate((("sums against processors", sums, 1.0e-10),
                                           ("identity on the card", idn, 1.0e-13),
                                           ("source dumps against processors", dumps,
                                            1.0e-12))):
        v = [max(dct.get(n, np.nan), 1.0e-18) for n in names]
        ax[0].bar(x + (i - 1)*w, v, width=w, color=fs.SERIES[i], label=lab)
        ax[0].axhline(bound, color=fs.SERIES[i], lw=0.8, ls="--")
    ax[0].set_yscale("log")
    ax[0].set_ylim(1.0e-18, 1.0e-8)
    ax[0].set_xticks(x)
    ax[0].set_xticklabels(names, fontsize=7)
    ax[0].set_ylabel("difference (dashed: bound)")
    ax[0].legend(frameon=False, fontsize=7)
    ax[0].set_title("(a) deposit on one A100", fontsize=9)
    ax[1].bar(x, [max(hist[n], 1.0e-18) for n in names], color=fs.SERIES[0], width=0.55)
    ax[1].set_yscale("log")
    ax[1].set_ylim(1.0e-18, 1.0)
    ax[1].set_xticks(x)
    ax[1].set_xticklabels(names, fontsize=7)
    ax[1].set_ylabel("histories: largest column difference / column")
    ax[1].set_title("(b) card against processors, columns above rounding", fontsize=9)
    fs.save(fig, os.path.join(out, "fig_card_v05"))
    plt.close(fig)
    print("CARD", res["verdict"])
    return 0 if res["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
