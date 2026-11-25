"""Median mass error of the verifier's series over the windows named in threshold_ball/JOURNAL.md
entry 11 (note before the common-window measurement): C 46.1-47.2 and 50.9-51; B 47.1-47.2,
48.2-48.8, 50.5-51. Usage: python -I vwindow.py --series DIR/vthresh_series.npz --out DIR"""
import argparse
import json
import os
import numpy as np

WIN = {"C-d0.42": [(46.1, 47.2), (50.9, 51.0)], "B-d0.42": [(47.1, 47.2), (48.2, 48.8), (50.5, 51.0)]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--series", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    z = np.load(a.series)
    res = {}
    for n, ws in WIN.items():
        t, mi, mx = z[n + "__mt"], z[n + "__mmirr"], z[n + "__mex"]
        lo, hi = z[n + "__mlo"], z[n + "__mhi"]
        dm = mi / mx - 1
        sel = np.zeros(t.size, bool)
        for a0, a1 in ws:
            sel |= (t >= a0 - 1e-9) & (t <= a1 + 1e-9)
        ok = sel & np.isfinite(dm)
        res[n] = {"windows": ws, "n": int(ok.sum()), "median": float(np.median(dm[ok])) if ok.any() else None,
                  "median_vs_next_band": float(np.nanmedian(mi[ok] / hi[ok] - 1)) if ok.any() else None,
                  "median_vs_last_trapped": float(np.nanmedian(mi[ok] / lo[ok] - 1)) if ok.any() else None}
    os.makedirs(a.out, exist_ok=True)
    json.dump(res, open(os.path.join(a.out, "vwindow.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
