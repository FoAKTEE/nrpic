#!/usr/bin/env python3
"""Analysis of the card job of the review (journal entry 8, list card_review.list).

    card_review.py --run DIR --smoke DIR --out DIR

--run    the batch directory of the new executable (sr64_l2, usr64_l2, sr256_l2_time,
         sr256_l0m_time)
--smoke  Track E's smoke batch of the executable of 6ca93cba (sr64_l2, usr64_l2)
Byte comparison of every .hst, .dump, .modes of the two 64^3 level-2 runs; if a file
differs, the largest relative difference of the history columns.  Throughput of the two
256^3 runs from their logs, next to that of Track E's ablation runs AL2S and AL0S (old
executable, from their chain logs: numbers on the command line).
Writes DIR/card_review.json and DIR/fig_card.png."""
import argparse
import filecmp
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import nl2                                  # noqa: E402
import numpy as np                          # noqa: E402


def throughput(rundir):
    out = {}
    for ln in open(os.path.join(rundir, "athena.log"), errors="replace"):
        for key, pat in (("zcps", r"zone-cycles/cpu_second = (\S+)"),
                         ("cpu_s", r"cpu time used\s+= (\S+)"),
                         ("cycles", r"MeshBlock-cycles = (\S+)")):
            m = re.search(pat, ln)
            if m:
                out[key] = float(m.group(1))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--smoke", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--old-l2", type=float, default=6.907721e6,
                    help="zone-cycles/s of AL2S, E-20261123-152119-38957ba")
    ap.add_argument("--old-l0m", type=float, default=1.127143e7,
                    help="zone-cycles/s of AL0S, E-20261123-153347-18e7c21")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = dict(run=os.path.abspath(a.run), smoke=os.path.abspath(a.smoke), cases={})
    for case in ("sr64_l2", "usr64_l2"):
        da, db = os.path.join(a.smoke, case), os.path.join(a.run, case)
        names = sorted(os.path.basename(f) for f in glob.glob(os.path.join(da, "*.sf.*")))
        same = [f for f in names if os.path.exists(os.path.join(db, f))
                and filecmp.cmp(os.path.join(da, f), os.path.join(db, f), shallow=False)]
        differ = [f for f in names if f not in same]
        ent = dict(files=len(names), identical=len(same), differ=differ)
        hst = [f for f in names if f.endswith(".sf.hst")]
        if hst and os.path.exists(os.path.join(db, hst[0])):
            ha = np.loadtxt(os.path.join(da, hst[0]), comments="#")
            hb = np.loadtxt(os.path.join(db, hst[0]), comments="#")
            n = min(len(ha), len(hb))
            den = np.maximum(np.abs(ha[:n]), 1e-300)
            rel = np.abs(ha[:n] - hb[:n])/den
            ent["rows"] = [len(ha), len(hb)]
            # columns 3-7 (means) and 8-9 (rms of the perturbations), 1-based
            ent["hst_max_rel_means"] = float(rel[:, 2:7].max())
            ent["hst_max_rel_rms"] = float(rel[:, 7:9].max())
        res["cases"][case] = ent
    tp = {c: throughput(os.path.join(a.run, c)) for c in ("sr256_l2_time",
                                                           "sr256_l0m_time")}
    res["throughput"] = dict(new=tp, old=dict(l2=a.old_l2, l0m=a.old_l0m))
    if all("zcps" in v for v in tp.values()):
        res["throughput"]["new_ratio_l0m_over_l2"] = \
            tp["sr256_l0m_time"]["zcps"]/tp["sr256_l2_time"]["zcps"]
        res["throughput"]["old_ratio_l0m_over_l2"] = a.old_l0m/a.old_l2
    nl2.dump_json(res, os.path.join(a.out, "card_review.json"))
    print(json.dumps(res, indent=1))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    fig, ax = plt.subplots(1, 1, figsize=(fs.FULL_WIDTH*0.5, 2.6))
    fig.subplots_adjust(left=0.2, right=0.97, bottom=0.2, top=0.9)
    lab = ["level 0\nmesh, old", "level 2\nold", "level 0\nmesh, new", "level 2\nnew"]
    val = [a.old_l0m, a.old_l2, tp["sr256_l0m_time"].get("zcps", 0.0),
           tp["sr256_l2_time"].get("zcps", 0.0)]
    col = [fs.PAL["blue"], fs.PAL["orange"], fs.PAL["blue"], fs.PAL["orange"]]
    ax.bar(range(4), [v/1e6 for v in val], color=col, width=0.6)
    ax.set_xticks(range(4))
    ax.set_xticklabels(lab, fontsize=6)
    ax.set_ylabel(r"$10^6$ zone-cycles per second")
    ax.set_title(r"$256^3$ on one A100", fontsize=8)
    fig.savefig(os.path.join(a.out, "fig_card.png"), dpi=200)


if __name__ == "__main__":
    main()
