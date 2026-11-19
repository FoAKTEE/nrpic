"""Run the four recomputations of the G1 verifier and the data-flow schematic into one run
directory ($NRPIC_RUN_DIR, set by harness/bin/nrpic-run; or --out). Each part writes
<part>.json (rows: item, claim, mine, verdict, how), its figures and a log.
"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
NOTE_SCRIPTS = os.path.abspath(os.path.join(HERE, "..", "..", "..", "note", "scripts"))
ap = argparse.ArgumentParser()
ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
a = ap.parse_args()
if not a.out:
    sys.exit("no output directory (set NRPIC_RUN_DIR or --out)")
os.makedirs(a.out, exist_ok=True)
fails = []
for part in ("v_ledger", "v_criteria", "v_newton", "v_ball"):
    d = os.path.join(a.out, part[2:])
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, f"{part}.log"), "w") as log:
        rc = subprocess.call([sys.executable, "-W", "ignore", os.path.join(HERE, part + ".py"), "--out", d],
                             stdout=log, stderr=subprocess.STDOUT, cwd=HERE)
    print(part, "exit", rc, flush=True)
    if rc:
        fails.append(part)
d = os.path.join(a.out, "schem")
os.makedirs(d, exist_ok=True)
rc = subprocess.call([sys.executable, os.path.join(NOTE_SCRIPTS, "schem_dataflow.py"), "--out", d], cwd=NOTE_SCRIPTS)
print("schem_dataflow exit", rc)
if rc:
    fails.append("schem_dataflow")
sys.exit(1 if fails else 0)
