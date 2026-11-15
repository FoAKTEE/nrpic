#!/usr/bin/env python3
"""Offline constraint check of the ES data set (outer edge 60 M) and of the vacuum table
V-1, with einstein_straus/offline_check.py, its figures redirected into the run directory
(the package einstein_straus is read, never written).

    offline_check_es.py --data <make_data run dir> [--out DIR]

DIR defaults to $NRPIC_RUN_DIR. Writes DIR/es/offline_check.json, DIR/es/figs/check_*,
DIR/v1/offline_check.json, DIR/v1/figs/check_*, DIR/summary.json (orders per region).
"""
import argparse
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
WT = os.path.normpath(os.path.join(PKG, "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "tracks", "D-bh-dress", "einstein_straus"))
sys.path.insert(0, PKG)
sys.path.insert(0, os.path.join(WT, "python"))
import es_model as em  # noqa: E402
import offline_check as oc  # noqa: E402
from make_data import GEOM, VacuumBubble  # noqa: E402


def run_one(model, tab, out):
    os.makedirs(os.path.join(out, "figs"), exist_ok=True)
    oc.FIGS = os.path.join(out, "figs")
    res = {"model": model.summary()}
    r1, curves = oc.check_1d(model)
    res["check_1d"] = r1
    oc.fig_1d(model, curves)
    res["table"] = oc.check_table(model, tab)
    res["check_3d"] = oc.check_3d(model, tab)
    oc.fig_3d(res["check_3d"])
    with open(os.path.join(out, "offline_check.json"), "w") as fo:
        json.dump(res, fo, indent=1, default=float)
    return res


def orders(res):
    s = {"1d": {}, "3d": {}}
    for name, rec in res["check_1d"]["regions"].items():
        s["1d"][name] = dict(H_order=rec["H"]["order"], M_order=rec["M"]["order"],
                             H_max_rel=rec["H"]["max_rel"], M_max_rel=rec["M"]["max_rel"])
    s["3d"] = res["check_3d"]
    s["table"] = res["table"]
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    a = ap.parse_args()
    es_tab, _ = em.read_tab2(os.path.join(a.data, "es", "es.tab"))
    v1_tab, _ = em.read_tab2(os.path.join(a.data, "v1", "v1.tab"))
    summ = {}
    print("ES model ...", flush=True)
    summ["es"] = orders(run_one(em.EinsteinStrausBH(**GEOM), es_tab, os.path.join(a.out, "es")))
    print("V-1 model ...", flush=True)
    summ["v1"] = orders(run_one(VacuumBubble(**GEOM), v1_tab, os.path.join(a.out, "v1")))
    with open(os.path.join(a.out, "summary.json"), "w") as fo:
        json.dump(summ, fo, indent=1, default=float)
    for k in ("es", "v1"):
        for name, rec in summ[k]["1d"].items():
            print(f"{k} 1D {name:24s} H order {['%.2f' % v for v in rec['H_order']]} "
                  f"M order {['%.2f' % v for v in rec['M_order']]}")
    print(json.dumps({k: summ[k]["3d"] for k in summ}, indent=None, default=float)[:4000])


if __name__ == "__main__":
    main()
