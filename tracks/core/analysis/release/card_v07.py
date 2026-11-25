#!/usr/bin/env python3
"""Card check of release candidate core-v0.7: the new cases of card_v07.list, run on one
A100 with the merged card executable, against the processor runs of the quick test
(quick_v07.py).  The fifteen cases of core-v0.6 in the same list are judged by
card_v06.py and card_v05.py, as for that release.

    card_v07.py --card CARD_RUN_DIR --quick QUICK_RUN_DIR --out DIR

Cases (processor run QUICK/<case>/new) and checks (prediction K7 of
tracks/core/JOURNAL.md, entry of 2026-11-25T02:12Z, amended before the run was queued):
  status    every case of NEW ended with status 0 (batch.list.status)
  n_l2      level 2 of the stochastic backreaction, 32^3, 24 cycles: sr.sf.hst within
            1e-9 (columns above 1e-6 of the largest column: largest difference over the
            largest magnitude of the column); the per-mode records *.rmodes within 1e-9
            of their largest entry
  x_l2dt    the same with dt_gauge = 0.9: as n_l2
  s_lim     flat space with noise of 1e-10 under dt_gauge = 0.9: the same number of
            records (cycles) and flat.z4c.user.hst within 1e-3 (the noise is 1e-10 of
            the fields, so rounding of 1e-16 is 1e-6 of what the history measures)
  g_hole    coarse vacuum mesh with lapse_leak_hole = 8: v1s.nrpic.hst and
            v1s.z4c.user.hst within 1e-7
  x_holedt  the same with dt_gauge = 0.9: as g_hole
  c_static  moving table cluster, initial data: both histories within 1e-7
  c_solve   the same under id_solve: outer iterations of clump.idsolve.txt equal,
            psi_max within 1e-12, histories within 1e-7
Reported and not bounded: sr.sf.con.hst (constraint means of the scalar-field runs, in
part differences of rounding-level numbers) and every other history both runs have.
Writes DIR/card_v07.json and DIR/fig_card_v07.{pdf,png}; exit status 0 if all hold.
Nothing is run here.
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
from card_v06 import status, hst_pair          # noqa: E402

# case -> (bound, histories it applies to)
BOUND = {
    "n_l2": (1e-9, ("sr.sf.hst",)),
    "x_l2dt": (1e-9, ("sr.sf.hst",)),
    "s_lim": (1e-3, ("flat.z4c.user.hst",)),
    "g_hole": (1e-7, ("v1s.nrpic.hst", "v1s.z4c.user.hst")),
    "x_holedt": (1e-7, ("v1s.nrpic.hst", "v1s.z4c.user.hst")),
    "c_static": (1e-7, ("clump.nrpic.hst", "clump.z4c.user.hst")),
    "c_solve": (1e-7, ("clump.nrpic.hst", "clump.z4c.user.hst")),
}
NEW = tuple(BOUND)


def table_pair(pa, pb):
    """largest difference of two numeric text tables over their largest entry"""
    try:
        a, b = np.loadtxt(pa, ndmin=2), np.loadtxt(pb, ndmin=2)
    except (OSError, ValueError) as e:
        return dict(error=str(e))
    if a.shape != b.shape:
        return dict(error="shapes %s and %s" % (a.shape, b.shape))
    big = max(float(np.abs(a).max()), float(np.abs(b).max()), 1e-300)
    return dict(rows=int(a.shape[0]), rel=float(np.abs(a - b).max()/big))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--card", required=True)
    ap.add_argument("--quick", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rc = status(a.card)
    rep = dict(card=a.card, quick=a.quick, status={n: rc.get(n) for n in NEW}, cases={})
    checks = {"status": all(rc.get(n) == 0 for n in NEW)}
    for n in NEW:
        dc, dp = os.path.join(a.card, n), os.path.join(a.quick, n, "new")
        e = dict(hst={}, rmodes={})
        for p in sorted(glob.glob(os.path.join(dp, "*.hst"))):
            q = os.path.join(dc, os.path.basename(p))
            e["hst"][os.path.basename(p)] = (hst_pair(q, p) if os.path.exists(q)
                                             else dict(error="missing on the card"))
        for p in sorted(glob.glob(os.path.join(dp, "*.rmodes"))):
            q = os.path.join(dc, os.path.basename(p))
            e["rmodes"][os.path.basename(p)] = (table_pair(q, p) if os.path.exists(q)
                                                else dict(error="missing on the card"))
        rec = glob.glob(os.path.join(dp, "*.idsolve.txt"))
        if rec:
            e["solve_cpu"] = qk.idsolve_record(rec[0])
            e["solve_card"] = qk.idsolve_record(os.path.join(dc, os.path.basename(rec[0])))
        bound, names = BOUND[n]
        hs = [e["hst"].get(k, dict(error="no such history")) for k in names]
        ok = all(v.get("rel_large", float("inf")) <= bound for v in hs)
        if e["rmodes"]:
            ok = ok and all(v.get("rel", float("inf")) <= 1e-9 for v in e["rmodes"].values())
        if rec:
            c, g = e["solve_cpu"], e["solve_card"]
            ok = ok and (c["outer"] is not None and c["outer"] == g["outer"] and
                         abs(c["psi_max"] - g["psi_max"]) <= 1e-12*abs(c["psi_max"]))
        e["bound"] = bound
        e["worst_bounded"] = max([v.get("rel_large", float("inf")) for v in hs] or [0.0])
        rep["cases"][n] = e
        checks[n] = bool(ok)
        print("%-9s exit %s  bounded histories worst %.2e (bound %.0e)  %s  %s" % (
            n, rc.get(n), e["worst_bounded"], bound, "held" if ok else "FAILED",
            {k: v.get("rel_large", v.get("error")) for k, v in e["hst"].items()}))
    rep["checks"] = checks
    with open(os.path.join(a.out, "card_v07.json"), "w") as f:
        json.dump(rep, f, indent=1)

    from nrpic import figstyle as fs
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(1, 1, figsize=(fs.FULL_WIDTH, 2.8))
    labels, vals, bnds, cols = [], [], [], []
    for n in NEW:
        for k, v in rep["cases"][n]["hst"].items():
            bounded = k in BOUND[n][1]
            labels.append("%s\n%s" % (n, k.split(".", 1)[1].replace(".hst", "")))
            vals.append(max(v.get("rel_large", 1.0), 1e-18))
            bnds.append(BOUND[n][0] if bounded else np.nan)
            cols.append(fs.PAL["blue"] if bounded else "0.6")
    x = np.arange(len(vals))
    ax.bar(x, vals, color=cols)
    ax.plot(x, bnds, ls="none", marker="_", ms=10, mew=1.2, color=fs.PAL["red"],
            label="bound of this history")
    ax.bar([np.nan], [np.nan], color="0.6", label="reported, not bounded")
    ax.set_yscale("log")
    ax.set_ylim(1e-18, 1e0)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=4, rotation=60, ha="right")
    ax.set_ylabel("card against processors:\nlargest column difference / column", fontsize=6)
    ax.legend(fontsize=5, loc="upper left")
    fig.tight_layout()
    fs.save(fig, os.path.join(a.out, "fig_card_v07"))
    plt.close(fig)
    ok = all(checks.values())
    for k, v in checks.items():
        print("%-9s %s" % (k, "held" if v else "FAILED"))
    print("CARD", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
