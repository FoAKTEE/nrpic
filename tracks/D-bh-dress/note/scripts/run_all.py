"""Run every figure, schematic and ledger script of the note into one output directory.

The command of the note's registered run (harness/bin/nrpic-run submit --package
tracks/D-bh-dress/note ...): writes figures/ and tables/ into $NRPIC_RUN_DIR (or --out DIR).
The committed copies under ../figures and ../tables are copied from that directory;
`nrpic-stage verify` regenerates the figures in place by running each fig_*.py and
schem_*.py without arguments (then ledger.py reads ../figures).
"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    a = ap.parse_args()
    if not a.out:
        raise SystemExit("give --out DIR or run under nrpic-run (NRPIC_RUN_DIR)")
    scripts = sorted(f for f in os.listdir(HERE)
                     if f.endswith(".py") and (f.startswith("fig_") or f.startswith("schem_")))
    jobs = [(f, os.path.join(a.out, "figures")) for f in scripts] + [("ledger.py", os.path.join(a.out, "tables"))]
    bad = []
    for f, d in jobs:
        os.makedirs(d, exist_ok=True)
        r = subprocess.run([sys.executable, os.path.join(HERE, f), "--out", d],
                           capture_output=True, text=True)
        sys.stdout.write(r.stdout + r.stderr)
        if r.returncode != 0 or "cut at the figure edge" in r.stdout:
            bad.append(f)
    print(f"run_all: {len(jobs) - len(bad)} of {len(jobs)} scripts ran cleanly" + (f"; failed: {bad}" if bad else ""))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
