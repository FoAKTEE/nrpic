"""Figure pop_gr_stop of the full-GR population box: diagnosis of a guard stop (lapse, K and density on the plane of the stop cell).

    python3 fig_pop_gr_stop.py ANALYSIS_GR.json [--newton analysis_fidL8.json] [--out DIR]

One script per figure (G2 item C15): reads the JSON that analyze_gr.py wrote (the list of runs,
as analysis_gr.json) and draws pop_gr_stop.png (PDF beside) only, with the drawing code of
analyze_gr.py.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyze_gr as A  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("analysis")
    ap.add_argument("--newton", default=None)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    R = json.load(open(a.analysis))
    R = R if isinstance(R, list) else [R]
    newton = json.load(open(a.newton))[0] if a.newton else None
    Z = next((r["stop"] for r in R if r.get("stop")), None)
    A.figure_stop(Z, a.out)


if __name__ == "__main__":
    main()
