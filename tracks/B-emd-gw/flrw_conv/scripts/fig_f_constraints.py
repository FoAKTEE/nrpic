"""Figure fig_f_constraints of flrw_conv (leg F): constraint histories of every run.

    python3 fig_f_constraints.py <runs.json> [<outdir>]     (default outdir $NRPIC_RUN_DIR)

One script per figure (G2 item C15): reads the runs named in runs.json through
analyze_f.load() and draws fig_f_constraints.png (PDF beside) only.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyze_f as A  # noqa: E402


def main():
    out = sys.argv[2] if len(sys.argv) > 2 else os.environ["NRPIC_RUN_DIR"]
    os.makedirs(out, exist_ok=True)
    A.fig_constraints(A.load(sys.argv[1]), out)


if __name__ == "__main__":
    main()
