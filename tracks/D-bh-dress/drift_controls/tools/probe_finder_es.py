#!/usr/bin/env python3
"""Part C of drift_controls (JOURNAL entry 1): re-search the apparent horizon of V-1 and
ES-1 restart dumps with other finder settings on the processor executable of the same
release, on the very slices of the run; and the pre-flight of card run (a).

    probe_finder_es.py probe --out DIR RST [RST ...] [--variants A16 A32] [--jobs 3]
    probe_finder_es.py preflight --out DIR RST [--ntheta 32 --lmax 12]

probe: for every dump and variant, AthenaK is restarted from the dump for one cycle
(time/nlim = ncycle + 1) with fastflow/find_every = 1, so the finder searches once, at the
last stage of cycle ncycle (z4c_tasks.cpp:335-356), which is the cycle of the run's own
summary row at the dump time (find_every = 16 divides the dump cycles). Restart output is
replaced by an event log (no 2 GB dump at the end). AthenaK reads the restart's
parameters, then the file given with -i (adding or replacing), then the command line.
Three horizons per run, all centred on the origin (ntheta and lmax are global,
fastflow.cpp:57-60; the rest is per horizon):
  h0  production stopping (mass_tol 1e-5, 400 iterations) from the radius stored in the
      dump (last_a0_0, fastflow.cpp:109, 499-503): what the run itself does
  h1  tight stopping (mass_tol 1e-9, 4000 iterations) from the same stored radius
      (last_a0_1 = last_a0_0, ah_found_a0_1 = true)
  h2  production stopping, started from outside at 1.3 times the stored mean radius
Variants: A16 = ntheta 16, lmax 8 (production grid); A32 = ntheta 32, lmax 12.

preflight: two runs of 2 cycles from one dump with the input of the run unchanged but for
the command line (as card run (a) will be started): "base" (no change) and "changed"
(fastflow/ntheta, fastflow/lmax on the command line); compares the summary rows, the
history rows and the Z4c fields of the final restart dumps of the two runs. Writes
DIR/preflight.json.

Output of probe: DIR/<run>_<dump>_<variant>/ with the summaries and athena.log;
DIR/probes.json (one record per horizon and run).
"""
import argparse
import concurrent.futures as cf
import glob
import json
import math
import os
import subprocess
import sys
import time

import numpy as np

WT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "analysis", "diag"))
from slicemass import rst_open, rst_params  # noqa: E402

EXE = "/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena"
VARIANTS = {"A16": {"ntheta": "16", "lmax": "8"},
            "A32": {"ntheta": "32", "lmax": "12"}}
COLS = ["stage", "time", "mass", "Sx", "Sy", "Sz", "S", "area", "hrms", "hmean",
        "meanradius", "minradius"]


def read_summary(path):
    rows = []
    if not os.path.exists(path):
        return rows
    for line in open(path):
        if line.startswith("#") or not line.strip():
            continue
        rows.append(dict(zip(COLS, map(float, line.split()))))
    return rows


def probe_input(variant, last_a0):
    r0 = last_a0 / math.sqrt(4 * math.pi)
    p = {"find_every": "1", "num_horizons": "3", "verbose": "false",
         "metric_drvts": "interpolant"}
    p.update(VARIANTS[variant])
    p.update({"mass_tol_0": "1.0e-5", "flow_iterations_0": "400"})
    hz = {1: {"mass_tol": "1.0e-9", "flow_iterations": "4000",
              "initial_radius": f"{r0:.12g}", "last_a0": f"{last_a0:.17g}",
              "ah_found_a0": "true"},
          2: {"mass_tol": "1.0e-5", "flow_iterations": "400",
              "initial_radius": f"{1.3 * r0:.12g}", "last_a0": "-1.0",
              "ah_found_a0": "false"}}
    for n, h in hz.items():
        p.update({f"start_time_{n}": "0.0", f"stop_time_{n}": "1.0e6",
                  f"center_x_{n}": "0.0", f"center_y_{n}": "0.0", f"center_z_{n}": "0.0",
                  f"use_puncture_{n}": "-1", f"flow_alpha_beta_const_{n}": "1.0",
                  f"hmean_tol_{n}": "100.0", f"mass_tol_{n}": h["mass_tol"],
                  f"flow_iterations_{n}": h["flow_iterations"],
                  f"initial_radius_{n}": h["initial_radius"],
                  f"last_a0_{n}": h["last_a0"], f"ah_found_a0_{n}": h["ah_found_a0"]})
    txt = "<fastflow>\n" + "".join(f"{k} = {v}\n" for k, v in p.items())
    txt += "\n<output2>\nfile_type = log\n"
    return txt


def run_athena(cmd, d, threads=1):
    env = dict(os.environ, OMP_NUM_THREADS=str(threads), OMP_PROC_BIND="false",
               OPENBLAS_NUM_THREADS="1")
    t0 = time.time()
    with open(os.path.join(d, "athena.log"), "w") as log:
        log.write("# cmd: " + " ".join(cmd) + "\n")
        log.flush()
        rc = subprocess.run(cmd, cwd=d, env=env, stdout=log,
                            stderr=subprocess.STDOUT).returncode
    return rc, time.time() - t0


def one_probe(rst, variant, outdir, exe):
    h = rst_open(rst, strict=True)
    par = rst_params(rst)
    base = par[("job", "basename")]
    last_a0 = float(par[("fastflow", "last_a0_0")])
    run = os.path.basename(os.path.dirname(os.path.dirname(os.path.abspath(rst))))
    d = os.path.join(outdir, f"{run}_{os.path.basename(rst)[:-4]}_{variant}")
    os.makedirs(d, exist_ok=True)
    pin = os.path.join(d, "probe.athinput")
    with open(pin, "w") as f:
        f.write(probe_input(variant, last_a0))
    cmd = [exe, "-r", os.path.abspath(rst), "-i", pin, "-d", d,
           f"time/nlim={h['ncycle'] + 1}", f"time/tlim={h['time'] + 10.0}"]
    rc, wall = run_athena(cmd, d)
    recs = []
    for n in (0, 1, 2):
        rows = read_summary(os.path.join(d, f"{base}.horizon_summary_{n}.txt"))
        rec = dict(dump=f"{run}/{os.path.basename(rst)}", run=run, base=base,
                   time_dump=h["time"], ncycle=h["ncycle"], variant=variant, horizon=n,
                   last_a0=last_a0, exit=rc, wall_s=wall)
        if rows:
            rec.update(rows[0])
            rec["n_rows"] = len(rows)
            rec["found"] = bool(rows[0]["mass"] == rows[0]["mass"])
        else:
            rec["found"] = False
        recs.append(rec)
    return recs


def cmd_probe(a):
    os.makedirs(a.out, exist_ok=True)
    jpath = os.path.join(a.out, "probes.json")
    allrec = json.load(open(jpath)) if os.path.exists(jpath) else []
    todo = [(r, v) for r in a.rst for v in a.variants]
    with cf.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        futs = {ex.submit(one_probe, r, v, a.out, a.exe): (r, v) for r, v in todo}
        for f in cf.as_completed(futs):
            recs = f.result()
            allrec = [x for x in allrec if (x["dump"], x["variant"]) !=
                      (recs[0]["dump"], recs[0]["variant"])] + recs
            with open(jpath, "w") as fo:
                json.dump(allrec, fo, indent=1)
            for x in recs:
                print(f"{x['dump']} t={x['time_dump']:.2f} {x['variant']} h{x['horizon']} "
                      f"found={x['found']} mass={x.get('mass', float('nan')):.10f} "
                      f"hrms={x.get('hrms', float('nan')):.2e} "
                      f"r={x.get('meanradius', float('nan')):.6f} exit={x['exit']} "
                      f"wall={x['wall_s']:.0f}s", flush=True)


def hst_rows(path):
    rows = []
    if not os.path.exists(path):
        return rows
    for line in open(path):
        if line.startswith("#") or not line.strip():
            continue
        rows.append([float(x) for x in line.split()])
    return rows


def cmd_preflight(a):
    os.makedirs(a.out, exist_ok=True)
    rst = os.path.abspath(a.rst[0])
    h = rst_open(rst, strict=True)
    par = rst_params(rst)
    base = par[("job", "basename")]
    nlim = h["ncycle"] + 2
    cases = {"base": [], "changed": [f"fastflow/ntheta={a.ntheta}", f"fastflow/lmax={a.lmax}"]}
    res = {"rst": rst, "time": h["time"], "ncycle": h["ncycle"], "nlim": nlim, "runs": {}}

    def go(name):
        d = os.path.join(a.out, name)
        os.makedirs(d, exist_ok=True)
        cmd = [a.exe, "-r", rst, "-d", d, f"time/nlim={nlim}"] + cases[name]
        rc, wall = run_athena(cmd, d)
        return name, d, rc, wall

    with cf.ThreadPoolExecutor(max_workers=2) as ex:
        outs = list(ex.map(go, list(cases)))
    for name, d, rc, wall in outs:
        r = {"dir": d, "exit": rc, "wall_s": wall,
             "summary": read_summary(os.path.join(d, f"{base}.horizon_summary_0.txt")),
             "z4c_hst": hst_rows(os.path.join(d, f"{base}.z4c.user.hst")),
             "nrpic_hst": hst_rows(os.path.join(d, f"{base}.nrpic.hst"))}
        log = open(os.path.join(d, "athena.log")).read()
        r["log_mentions_ntheta"] = [ln for ln in log.splitlines() if "ntheta" in ln][:5]
        dumps = sorted(glob.glob(os.path.join(d, "rst", f"{base}.*.rst")) +
                       glob.glob(os.path.join(d, f"{base}.*.rst")))
        r["final_dump"] = dumps[-1] if dumps else None
        if r["final_dump"]:
            pp = rst_params(r["final_dump"])
            r["final_dump_ntheta"] = pp.get(("fastflow", "ntheta"))
            r["final_dump_lmax"] = pp.get(("fastflow", "lmax"))
        res["runs"][name] = r
    # comparisons
    b, c = res["runs"]["base"], res["runs"]["changed"]
    cmpr = {}
    cmpr["hst_identical_z4c"] = b["z4c_hst"] == c["z4c_hst"]
    cmpr["hst_identical_nrpic"] = b["nrpic_hst"] == c["nrpic_hst"]
    cmpr["n_summary_rows"] = [len(b["summary"]), len(c["summary"])]
    if b["summary"] and c["summary"]:
        cmpr["mass_base"] = b["summary"][0]["mass"]
        cmpr["mass_changed"] = c["summary"][0]["mass"]
        cmpr["mass_changed_minus_base"] = c["summary"][0]["mass"] - b["summary"][0]["mass"]
        cmpr["time_rows"] = [b["summary"][0]["time"], c["summary"][0]["time"]]
    if b.get("final_dump") and c.get("final_dump"):
        hb, hc = rst_open(b["final_dump"], strict=True), rst_open(c["final_dump"], strict=True)
        cmpr["final_time"] = [hb["time"], hc["time"]]
        cmpr["final_ncycle"] = [hb["ncycle"], hc["ncycle"]]
        mx = 0.0
        same = hb["mm"].shape == hc["mm"].shape
        if same:
            for m in range(hb["nmb"]):
                dd = np.abs(np.asarray(hb["mm"][m]) - np.asarray(hc["mm"][m])).max()
                mx = max(mx, float(dd))
        cmpr["z4c_fields_max_abs_diff"] = mx if same else None
    # card row at the dump time, if the original summary is next to rst/
    orig = os.path.join(os.path.dirname(os.path.dirname(rst)), f"{base}.horizon_summary_0.txt")
    rows = read_summary(orig)
    sel = [r for r in rows if abs(r["time"] - h["time"]) < 1e-9]
    if sel and b["summary"]:
        cmpr["card_row_mass"] = sel[-1]["mass"]
        cmpr["processor_minus_card_rel"] = b["summary"][0]["mass"] / sel[-1]["mass"] - 1
    res["compare"] = cmpr
    with open(os.path.join(a.out, "preflight.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(cmpr, indent=1))
    for name in cases:
        r = res["runs"][name]
        print(name, "exit", r["exit"], "wall", round(r["wall_s"]), "rows", len(r["summary"]),
              "final dump", r.get("final_dump"), "ntheta in dump", r.get("final_dump_ntheta"),
              "lmax", r.get("final_dump_lmax"))
        for s in r["summary"]:
            print("   ", {k: s[k] for k in ("time", "mass", "hrms", "meanradius")})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["probe", "preflight"])
    ap.add_argument("rst", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--variants", nargs="+", default=["A16", "A32"])
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--exe", default=EXE)
    ap.add_argument("--ntheta", type=int, default=32)
    ap.add_argument("--lmax", type=int, default=12)
    a = ap.parse_args()
    if a.mode == "probe":
        cmd_probe(a)
    else:
        cmd_preflight(a)


if __name__ == "__main__":
    main()
