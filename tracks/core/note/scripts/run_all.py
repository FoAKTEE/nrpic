#!/usr/bin/env python3
"""Make every figure and table of the working note of core into one directory.

    run_all.py OUTDIR     (OUTDIR = $NRPIC_RUN_DIR of a registered run)

Writes OUTDIR/figures/, OUTDIR/tables/ (ledger, runinfo), OUTDIR/numbers_*.json,
OUTDIR/log.txt and OUTDIR/sha256sums.txt. Copy figures/ and tables/ into note/ after.
"""
import hashlib
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = ["fig_geodesic.py", "fig_collapse.py", "fig_clusters.py", "fig_row4_m8.py",
           "schem_architecture.py", "ledger.py"]


def main():
    out = Path(sys.argv[1]).resolve()
    out.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1")
    with open(out / "log.txt", "w") as log:
        for s in SCRIPTS:
            log.write(f"== {s}\n")
            log.flush()
            r = subprocess.run([sys.executable, str(HERE / s), str(out)], cwd=HERE, env=env,
                               stdout=log, stderr=subprocess.STDOUT)
            if r.returncode:
                raise SystemExit(f"{s} failed with status {r.returncode} (see {out / 'log.txt'})")
    run_id = os.environ.get("NRPIC_RUN_ID", "unregistered")
    (out / "tables" / "runinfo.tex").write_text(
        r"\newcommand{\noterun}{\texttt{" + run_id + "}}\n")
    lines = []
    for p in sorted(out.rglob("*")):
        if p.is_file() and p.name != "sha256sums.txt":
            lines.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(out)}")
    (out / "sha256sums.txt").write_text("\n".join(lines) + "\n")
    print(f"run_all: {len(lines)} files in {out}")


if __name__ == "__main__":
    main()
