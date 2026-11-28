"""Finder 0 (m1) of A2 around the capture, row by row: status (found, reason, flow iterations,
area mass, mean expansion) joined to the summary (mass, hrms), 137-148 M; written to vf0.json
with counts by class. Run: python vf0.py --out <dir>
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vtail  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    st = vtail.read_status(os.path.join(vtail.RUN_A2, "hills.horizon_status_0.txt"))
    su = vtail.summary_by_key(os.path.join(vtail.RUN_A2, "hills.horizon_summary_0.txt"))
    common, i_s, i_u = np.intersect1d(st["key"], su["key"], return_indices=True)
    rows = []
    for k_s, k_u in zip(i_s, i_u):
        t = float(st["t"][k_s])
        if 137.0 <= t <= 148.0:
            rows.append({"t": t, "found": int(st["found"][k_s]), "reason": st["words"][k_s],
                         "flow_it": int(st["flow_it"][k_s]), "area_mass": float(st["area_mass"][k_s]),
                         "mean_exp": float(st["mean_exp"][k_s]), "mass": float(su["mass"][k_u]),
                         "hrms": float(su["hrms"][k_u])})
    f = [r for r in rows if r["found"]]
    small = [r for r in f if 0.10 < r["area_mass"] < 0.16]
    big = [r for r in f if r["area_mass"] >= 0.16]
    res = {"n_rows_137_148": len(rows), "n_found": len(f),
           "found_area_mass_0.10_0.16": {"n": len(small), "t_first_last": [small[0]["t"], small[-1]["t"]] if small else None,
                                          "abs_mean_exp_max": max(abs(r["mean_exp"]) for r in small) if small else None,
                                          "hrms_max": max(r["hrms"] for r in small) if small else None,
                                          "mass_min_max": [min(r["mass"] for r in small), max(r["mass"] for r in small)] if small else None},
           "found_area_mass_above_0.16": {"n": len(big), "t_first_last": [big[0]["t"], big[-1]["t"]] if big else None,
                                           "abs_mean_exp_min_max": [min(abs(r["mean_exp"]) for r in big), max(abs(r["mean_exp"]) for r in big)] if big else None,
                                           "hrms_min_max": [min(r["hrms"] for r in big), max(r["hrms"] for r in big)] if big else None},
           "rows_139_142": [r for r in rows if 139.0 <= r["t"] <= 142.0]}
    with open(os.path.join(a.out, "vf0.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "rows_139_142"}))


if __name__ == "__main__":
    main()
