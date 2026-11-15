#!/usr/bin/env python3
"""Runs U1-U8 of the noise unit test (tracks/E-stoch-inf/noise/NOISE_SPEC.md section 9) with
core's processor executable, then the three validations of noise/README.md.

    python3 u_runs.py --exe EXE --base inputs/u_base.athinput --out DIR [--threads 4]
                      [--jobs 4] [--smoke]

Each variant gets its own input file (DIR/<name>/u.athinput, the base with the options of
the variant replaced), so the validator reads the parameters of the run it checks. U4 is
U2 restarted from its restart file at cycle 150. --smoke runs U1 for 4 cycles only (timing).
Writes DIR/summary.json (exit status and wall time per run, verdicts of the validations).
"""
import argparse
import concurrent.futures as cf
import glob
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
NOISE = os.path.normpath(os.path.join(HERE, "..", "..", "noise"))

def variants(n, cfl, u5_nmax2):
    """U1-U8 relative to a base mesh of n^3 cells in one MeshBlock (NOISE_SPEC section 9)."""
    b2, b4, lo = str(n // 2), str(n // 4), str(n // 2)
    blocks = lambda b: {("meshblock", "nx1"): b, ("meshblock", "nx2"): b, ("meshblock", "nx3"): b}
    return {
        "U1": {},
        "U2": blocks(b2),
        "U3": blocks(b4),
        "U5a": {("mesh", "nx1"): lo, ("mesh", "nx2"): lo, ("mesh", "nx3"): lo, **blocks(lo),
                ("time", "cfl_number"): repr(cfl / 2), ("scalar_field", "noise_nmax2"): str(u5_nmax2)},
        "U5b": {("scalar_field", "noise_nmax2"): str(u5_nmax2)},
        "U6": {("scalar_field", "noise_scheme"): "markov"},
        "U7": {("scalar_field", "noise_scheme"): "markov",
               ("scalar_field", "noise_window"): "heaviside"},
        "U8": {**blocks(b2), ("job", "rng_seed"): "20261116"},
    }


def edit_input(text, changes):
    out, block = [], None
    done = set()
    for line in text.splitlines():
        m = re.match(r"^<(\w+)>", line)
        if m:
            block = m.group(1)
        m = re.match(r"^(\s*)(\w+)(\s*=\s*)(\S+)(.*)$", line)
        if m and block is not None and (block, m.group(2)) in changes:
            key = (block, m.group(2))
            line = f"{m.group(1)}{m.group(2)}{m.group(3)}{changes[key]}{m.group(5)}"
            done.add(key)
        out.append(line)
    missing = set(changes) - done
    if missing:
        raise SystemExit(f"options not found in the base input: {sorted(missing)}")
    return "\n".join(out) + "\n"


def run_one(exe, rundir, args, threads):
    env = dict(os.environ, OMP_NUM_THREADS=str(threads), OMP_PROC_BIND="false")
    t0 = time.time()
    with open(os.path.join(rundir, "athena.log"), "w") as log:
        rc = subprocess.run([exe] + args, cwd=rundir, stdout=log, stderr=subprocess.STDOUT,
                            env=env).returncode
    return rc, time.time() - t0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--base", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--u5-nmax2", type=int, default=64)
    a = ap.parse_args()
    exe = os.path.abspath(a.exe)
    base = open(a.base).read()
    os.makedirs(a.out, exist_ok=True)
    summary = {"exe": exe, "base": os.path.abspath(a.base), "runs": {}, "validations": {}}
    n = int(re.search(r"<mesh>[^<]*?\bnx1\s*=\s*(\d+)", base).group(1))
    cfl = float(re.search(r"cfl_number\s*=\s*([0-9.eE+-]+)", base).group(1))
    VARIANTS = variants(n, cfl, a.u5_nmax2)
    names = ["U1"] if a.smoke else list(VARIANTS)
    for name in names:
        ch = dict(VARIANTS[name])
        if a.smoke:
            ch[("time", "nlim")] = "4"
        d = os.path.join(a.out, name)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "u.athinput"), "w") as f:
            f.write(edit_input(base, ch))
    with cf.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        fut = {ex.submit(run_one, exe, os.path.join(a.out, n), ["-i", "u.athinput"],
                         a.threads): n for n in names}
        for f in cf.as_completed(fut):
            rc, wall = f.result()
            summary["runs"][fut[f]] = {"exit": rc, "wall_s": round(wall, 1)}
            print(fut[f], rc, f"{wall:.1f} s", flush=True)
    if not a.smoke:
        # U4: U2 restarted from its restart file at cycle 150
        rst = sorted(glob.glob(os.path.join(a.out, "U2", "rst", "*.rst")))
        pick = None
        for r in rst:
            if r.endswith(".00001.rst"):
                pick = r
        d4 = os.path.join(a.out, "U4")
        os.makedirs(d4, exist_ok=True)
        if pick is None:
            summary["runs"]["U4"] = {"exit": -1, "note": f"no restart file at cycle 150 in {rst}"}
        else:
            import shutil
            shutil.copy(os.path.join(a.out, "U2", "u.athinput"), os.path.join(d4, "u.athinput"))
            rc, wall = run_one(exe, d4, ["-r", pick], a.threads)
            summary["runs"]["U4"] = {"exit": rc, "wall_s": round(wall, 1), "restart_file": pick}
            print("U4", rc, f"{wall:.1f} s", flush=True)
        val = os.path.join(NOISE, "validate", "validate_noise.py")
        o = a.out
        cmds = {
            "frozen": [sys.executable, val, "--input", f"{o}/U1/u.athinput", "--run", f"{o}/U1",
                       "--blocks8", f"{o}/U2", "--blocks64", f"{o}/U3", "--restart", f"{o}/U4",
                       "--res-lo", f"{o}/U5a", "--res-hi", f"{o}/U5b",
                       "--res-lo-input", f"{o}/U5a/u.athinput",
                       "--res-hi-input", f"{o}/U5b/u.athinput", "--seed2", f"{o}/U8",
                       "--seed2-input", f"{o}/U8/u.athinput", "--out", f"{o}/val_frozen"],
            "markov_tanh": [sys.executable, val, "--input", f"{o}/U6/u.athinput", "--run",
                            f"{o}/U6", "--out", f"{o}/val_markov_tanh"],
            "markov_heaviside": [sys.executable, val, "--input", f"{o}/U7/u.athinput", "--run",
                                 f"{o}/U7", "--out", f"{o}/val_markov_heaviside"],
        }
        for k, c in cmds.items():
            with open(os.path.join(o, f"val_{k}.log"), "w") as log:
                rc = subprocess.run(c, stdout=log, stderr=subprocess.STDOUT).returncode
            summary["validations"][k] = {"exit": rc, "command": " ".join(c)}
            print("validation", k, rc, flush=True)
    with open(os.path.join(a.out, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1)


if __name__ == "__main__":
    main()
