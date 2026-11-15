#!/usr/bin/env python3
"""Re-search the apparent horizon of AthenaK restart dumps with other finder settings,
on the processor executable, without changing the slice.

    probe_finder.py --out DIR --tag NAME RST [RST ...] [--variants A16 A32]
                    [--threads 8] [--jobs 2] [--exe PATH]

For every dump and every variant, AthenaK is restarted from the dump for exactly one
cycle (time/nlim = ncycle + 1) with fastflow/find_every = 1, so the finder searches once,
at the last stage of that cycle (z4c_tasks.cpp:335-356). The restart output is replaced
by an event log (output2/file_type = log) so that no restart file is written at the end.

Each variant runs three horizons at once (all centred on the origin; ntheta and lmax are
global to the finder, fastflow.cpp:57-60, the rest is per horizon):
  h0  production stopping (mass_tol 1e-5, 400 iterations), started from the radius
      stored in the dump (last_a0_0, fastflow.cpp:109, 439-447): what the run itself does
  h1  tight stopping (mass_tol 1e-9, 4000 iterations), started from r = 1.0 M
  h2  production stopping, started from outside, r = 2.0 M
Variants: A16 = ntheta 16, lmax 8 (production grid); A32 = ntheta 32, lmax 16.

Output: DIR/<tag>/<run>_<dump>_<variant>/ (run = name of the directory above rst/) with punc.horizon_summary_{0,1,2}.txt and athena.log,
and DIR/<tag>/probes.json (one record per search: dump, time, ncycle, variant, horizon,
mass, Sx, Sy, Sz, S, area, hrms, hmean, mean and minimum radius, wall time).
"""
import argparse
import concurrent.futures as cf
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, "/data/haiyangw/nrpic/wt/D-bh-dress/analysis/diag")
from slicemass import rst_open  # noqa: E402  (restart header reader of this repository)

EXE = "/data/haiyangw/nrpic/.work/build_cpu_c1/src/athena"

HORIZONS = {
    0: {},  # production settings, as stored in the dump
    1: {"mass_tol": "1.0e-9", "flow_iterations": "4000", "initial_radius": "1.0"},
    2: {"mass_tol": "1.0e-5", "flow_iterations": "400", "initial_radius": "2.0"},
}
VARIANTS = {"A16": {"ntheta": "16", "lmax": "8"},
            "A32": {"ntheta": "32", "lmax": "16"}}
COLS = ["iter", "time", "mass", "Sx", "Sy", "Sz", "S", "area", "hrms", "hmean",
        "meanradius", "minradius"]


def probe_input(variant):
    """Parameter file given with -i next to -r: AthenaK loads the restart's parameters,
    then this file (adding or replacing), then the command line (main.cpp:276-288);
    the command line alone can only change parameters that already exist."""
    p = {"find_every": "1", "num_horizons": "3", "verbose": "false",
         "metric_drvts": "interpolant"}
    p.update(VARIANTS[variant])
    p.update({"mass_tol_0": "1.0e-5", "flow_iterations_0": "400"})
    for n in (1, 2):
        h = HORIZONS[n]
        p.update({f"start_time_{n}": "0.0", f"stop_time_{n}": "1.0e6",
                  f"center_x_{n}": "0.0", f"center_y_{n}": "0.0", f"center_z_{n}": "0.0",
                  f"use_puncture_{n}": "-1", f"flow_alpha_beta_const_{n}": "1.0",
                  f"hmean_tol_{n}": "100.0", f"mass_tol_{n}": h["mass_tol"],
                  f"flow_iterations_{n}": h["flow_iterations"],
                  f"initial_radius_{n}": h["initial_radius"]})
    txt = "<fastflow>\n" + "".join(f"{k} = {v}\n" for k, v in p.items())
    txt += "\n<output2>\nfile_type = log\n"
    return txt


def read_summary(path):
    rows = []
    if not os.path.exists(path):
        return rows
    for line in open(path):
        if line.startswith("#") or not line.strip():
            continue
        rows.append(dict(zip(COLS, map(float, line.split()))))
    return rows


def one(rst, variant, outdir, exe, threads):
    h = rst_open(rst, strict=True)
    run = os.path.basename(os.path.dirname(os.path.dirname(os.path.abspath(rst))))
    d = os.path.join(outdir, f"{run}_{os.path.basename(rst)[:-4]}_{variant}")
    os.makedirs(d, exist_ok=True)
    pin = os.path.join(d, "probe.athinput")
    with open(pin, "w") as f:
        f.write(probe_input(variant))
    cmd = [exe, "-r", rst, "-i", pin, "-d", d, f"time/nlim={h['ncycle'] + 1}",
           f"time/tlim={h['time'] + 10.0}"]     # a final dump has time = tlim
    env = dict(os.environ, OMP_NUM_THREADS=str(threads), OMP_PROC_BIND="false",
               OPENBLAS_NUM_THREADS="1")
    t0 = time.time()
    with open(os.path.join(d, "athena.log"), "w") as log:
        log.write("# cmd: " + " ".join(cmd) + "\n")
        log.flush()
        rc = subprocess.run(cmd, cwd=d, env=env, stdout=log, stderr=subprocess.STDOUT).returncode
    wall = time.time() - t0
    recs = []
    for n in HORIZONS:
        rows = read_summary(os.path.join(d, f"punc.horizon_summary_{n}.txt"))
        base = dict(dump=f"{run}/{os.path.basename(rst)}", run=run, rst=rst,
                    time_dump=h["time"],
                    ncycle=h["ncycle"], dt=h["dt"], variant=variant, horizon=n,
                    exit=rc, wall_s=wall)
        if rows:
            base.update(rows[-1])
            base["found"] = bool(rows[-1]["mass"] == rows[-1]["mass"])   # NaN: not found
        else:
            base["found"] = False
        recs.append(base)
    return recs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rst", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--variants", nargs="+", default=["A16", "A32"])
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--exe", default=EXE)
    a = ap.parse_args()
    outdir = os.path.join(a.out, a.tag)
    os.makedirs(outdir, exist_ok=True)
    jpath = os.path.join(outdir, "probes.json")
    allrec = json.load(open(jpath)) if os.path.exists(jpath) else []
    done = {(r["dump"], r["variant"]) for r in allrec if r["exit"] == 0 and r["found"]}
    def key(r):
        r = os.path.abspath(r)
        return f"{os.path.basename(os.path.dirname(os.path.dirname(r)))}/{os.path.basename(r)}"
    todo = [(r, v) for r in a.rst for v in a.variants if (key(r), v) not in done]
    with cf.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        futs = {ex.submit(one, r, v, outdir, a.exe, a.threads): (r, v) for r, v in todo}
        for f in cf.as_completed(futs):
            recs = f.result()
            allrec = [x for x in allrec if (x["dump"], x["variant"]) !=
                      (recs[0]["dump"], recs[0]["variant"])] + recs
            with open(jpath, "w") as fo:
                json.dump(allrec, fo, indent=1)
            for x in recs:
                print(f"{x['dump']} t={x['time_dump']:.3f} {x['variant']} h{x['horizon']} "
                      f"found={x['found']} mass={x.get('mass', float('nan')):.9f} "
                      f"S={x.get('S', float('nan')):.3e} hrms={x.get('hrms', float('nan')):.2e} "
                      f"r={x.get('meanradius', float('nan')):.5f} exit={x['exit']} "
                      f"wall={x['wall_s']:.0f}s", flush=True)


if __name__ == "__main__":
    main()
