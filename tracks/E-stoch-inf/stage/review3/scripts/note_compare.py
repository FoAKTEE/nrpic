#!/usr/bin/env python3
"""Lead review, batch 3 (E-stoch-inf): compare the note's rerun (run_all.py) with the
committed figures and tables and with the registered run E-20261121-080840-6112292.

    note_compare.py --new DIR --committed NOTE_DIR --registered RUN_DIR --out FILE.json

PNGs: byte equality and pixel rms (matplotlib.image); tables: byte equality.  PDF and SVG
carry creation stamps and are not compared.
"""
import argparse
import hashlib
import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.image as mpimg


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def cmp_png(a, b):
    if not (os.path.exists(a) and os.path.exists(b)):
        return dict(missing=[x for x in (a, b) if not os.path.exists(x)])
    same = sha(a) == sha(b)
    A, B = mpimg.imread(a), mpimg.imread(b)
    if A.shape != B.shape:
        return dict(bytes_equal=same, shape=[list(A.shape), list(B.shape)], pixel_rms=None)
    return dict(bytes_equal=same, pixel_rms=float(np.sqrt(np.mean((A - B) ** 2))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--new", required=True)
    ap.add_argument("--committed", required=True)
    ap.add_argument("--registered", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res = dict(figures={}, tables={})
    for f in sorted(os.listdir(os.path.join(a.committed, "figures"))):
        if not f.endswith(".png"):
            continue
        res["figures"][f] = dict(
            new_vs_committed=cmp_png(os.path.join(a.new, "figures", f), os.path.join(a.committed, "figures", f)),
            committed_vs_registered=cmp_png(os.path.join(a.committed, "figures", f), os.path.join(a.registered, "figures", f)))
    for f in sorted(os.listdir(os.path.join(a.committed, "tables"))):
        p_new, p_com, p_reg = (os.path.join(d, "tables", f) for d in (a.new, a.committed, a.registered))
        res["tables"][f] = dict(
            new_vs_committed=(sha(p_new) == sha(p_com)) if os.path.exists(p_new) else "missing",
            committed_vs_registered=(sha(p_com) == sha(p_reg)) if os.path.exists(p_reg) else "missing")
    figs = res["figures"].values()
    res["summary"] = dict(
        n_png=len(res["figures"]),
        png_bytes_equal_new=sum(1 for x in figs if x["new_vs_committed"].get("bytes_equal")),
        png_pixel_rms_max_new=max((x["new_vs_committed"].get("pixel_rms") or 0.0) for x in figs),
        png_bytes_equal_registered=sum(1 for x in figs if x["committed_vs_registered"].get("bytes_equal")),
        tables_equal_new=[k for k, v in res["tables"].items() if v["new_vs_committed"] is True],
        tables_differ_new=[k for k, v in res["tables"].items() if v["new_vs_committed"] is not True])
    json.dump(res, open(a.out, "w"), indent=1)
    print(json.dumps(res["summary"], indent=1))


if __name__ == "__main__":
    main()
