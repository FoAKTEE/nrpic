"""Run every figure script, both schematics and the ledger of the note into one directory
(the registered run of the note package), then check that a second run of each figure
script gives the same PNG (prediction N3 of ../JOURNAL.md).

Usage (from anywhere): python run_all.py --out <dir>
Writes <dir>/figures/*.{pdf,png,svg}, <dir>/tables/*, <dir>/repeat/ and <dir>/repeat.json.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = ["fig_background", "fig_freezing", "fig_deltan", "fig_noise", "fig_cost",
        "schem_architecture", "schem_timeline"]


def main():
    out = None
    for i, a in enumerate(sys.argv):
        if a == "--out" and i + 1 < len(sys.argv):
            out = os.path.abspath(sys.argv[i + 1])
    if out is None:
        raise SystemExit("usage: run_all.py --out DIR")
    env = dict(os.environ, MPLCONFIGDIR=os.path.join(out, ".mpl"), OMP_NUM_THREADS="2")
    for name in FIGS:
        subprocess.run([sys.executable, os.path.join(HERE, name + ".py"), "--out",
                        os.path.join(out, "figures")], check=True, env=env)
    subprocess.run([sys.executable, os.path.join(HERE, "ledger.py"), "--out",
                    os.path.join(out, "tables")], check=True, env=env)
    # repeat each data figure and compare the PNG bytes and pixels
    import numpy as np
    import matplotlib.image as mpimg
    rep = {}
    for name in FIGS:
        subprocess.run([sys.executable, os.path.join(HERE, name + ".py"), "--out",
                        os.path.join(out, "repeat")], check=True, env=env)
        a = mpimg.imread(os.path.join(out, "figures", name + ".png"))
        b = mpimg.imread(os.path.join(out, "repeat", name + ".png"))
        same = a.shape == b.shape
        rms = float(np.sqrt(np.mean((a - b) ** 2))) if same else None
        rep[name] = dict(same_shape=same, pixel_rms=rms)
    with open(os.path.join(out, "repeat.json"), "w") as f:
        json.dump(rep, f, indent=1)
    print(json.dumps(rep))
    bad = [k for k, r in rep.items() if not r["same_shape"] or r["pixel_rms"] != 0.0]
    if bad:
        raise SystemExit(f"figures differ between two runs: {bad}")


if __name__ == "__main__":
    main()
