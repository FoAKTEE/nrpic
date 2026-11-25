"""Finder mass at first detection against the exact mass of the shell at the finder's coordinate
radius (label from the tracked particles, interpolation v2), from the verifier's threshold output.
Usage: python -I vshell.py --thresh DIR --out DIR"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vref import LTB


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--thresh", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    d = json.load(open(os.path.join(a.thresh, "vthresh.json")))["members"]
    res = {}
    for n, r in d.items():
        if "first" not in r:
            continue
        L = LTB(r["table"])
        f = r["first"]
        m = float(L.shell([f["label"]])["m"][0])
        res[n] = {"label": f["label"], "core_edge_break": L.breaks[0], "m_shell_at_finder_radius": m,
                  "finder_mirr": f["mirr"], "excess": f["mirr"] / m - 1, "m_core_edge": r["exact_m_edge"],
                  "finder_vs_edge": f["mirr"] / r["exact_m_edge"] - 1}
        print("%-8s label %.4f (break %.4f) m(shell) %.5f finder %.5f excess %+.4f vs edge %+.4f" % (
            n, f["label"], L.breaks[0], m, f["mirr"], f["mirr"] / m - 1, f["mirr"] / r["exact_m_edge"] - 1))
    os.makedirs(a.out, exist_ok=True)
    json.dump(res, open(os.path.join(a.out, "vshell.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
