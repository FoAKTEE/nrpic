"""Run every figure, schematic and the ledger of the note into one output directory.

    python run_all.py [OUTDIR]      (default: $NRPIC_RUN_DIR, set by nrpic-run for a local run)

Writes OUTDIR/figures/*, OUTDIR/tables/* and OUTDIR/log.txt; when OUTDIR is given on the
command line (a run registered by hand) also OUTDIR/sha256sums.txt, which nrpic-run's
`finish` writes otherwise. The note's committed figures/ and tables/ are copies of these
outputs.
"""
import hashlib
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = ["fig_source", "fig_waves", "fig_pancake", "fig_baseline",
           "schem_architecture", "schem_timeline"]


def main():
    by_hand = len(sys.argv) > 1
    out = os.path.abspath(sys.argv[1] if by_hand else os.environ["NRPIC_RUN_DIR"])
    figs, tabs = os.path.join(out, "figures"), os.path.join(out, "tables")
    os.makedirs(figs, exist_ok=True)
    os.makedirs(tabs, exist_ok=True)
    env = dict(os.environ, MPLBACKEND="Agg", OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1")
    log = open(os.path.join(out, "log.txt"), "w")
    rc = 0
    for name in SCRIPTS + ["ledger"]:
        dest = tabs if name == "ledger" else figs
        p = subprocess.run([sys.executable, os.path.join(HERE, name + ".py"), "--out", dest],
                           env=env, capture_output=True, text=True)
        log.write(f"== {name} exit {p.returncode}\n{p.stdout}{p.stderr}\n")
        rc |= p.returncode
    log.close()
    if not by_hand:
        sys.exit(rc)
    with open(os.path.join(out, "sha256sums.txt"), "w") as f:
        for root, _, files in sorted(os.walk(out)):
            for fn in sorted(files):
                if fn == "sha256sums.txt":
                    continue
                path = os.path.join(root, fn)
                h = hashlib.sha256(open(path, "rb").read()).hexdigest()
                f.write(f"{h}  {os.path.relpath(path, out)}\n")
    sys.exit(rc)


if __name__ == "__main__":
    main()
