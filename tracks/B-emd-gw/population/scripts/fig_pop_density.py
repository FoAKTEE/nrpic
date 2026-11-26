"""Figure pop_density of the Newtonian population analysis: projected density of the GW case at four epochs (reads its snapshots).

    python3 fig_pop_density.py ANALYSIS.json [--gw NAME] [--lscale LAMBDA] [--out DIR]

One script per figure (G2 item C15): reads the JSON that analyze.py wrote (analysis<tag>.json)
and draws pop_density.png (PDF beside) only, with the drawing code of analyze.py. --lscale must be
the value the analysis ran with (the box lambda L).
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyze as A  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("analysis")
    ap.add_argument("--gw", default=None, help="case name of the GW analysis (default: the first)")
    ap.add_argument("--lscale", type=float, default=1.0)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    a = ap.parse_args()
    A.LSCALE = a.lscale
    os.makedirs(a.out, exist_ok=True)
    results = json.load(open(a.analysis))
    A.fig_density(results, a.out, a.gw or results[0]["name"])


if __name__ == "__main__":
    main()
