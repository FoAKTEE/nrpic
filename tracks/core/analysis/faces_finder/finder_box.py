#!/usr/bin/env python3
"""Horizon searches on a restart file of a periodic run (Track A's reproducers), one cycle.

    finder_box.py --exe ATHENA --rst FILE.rst --case CASE.json --out DIR [--threads 3]

Method of tracks/core/analysis/restart_finder/finder_probe.py and of Track A's
finder_probe_box.py: the restart file is continued for exactly one cycle (time/nlim =
ncycle + 1) with a parameter file next to -r that holds the <fastflow> block of the case,
every horizon centred on the box centre and searched once at the end of that cycle.  The
restart output of the deck (output7 in Track A's decks) is replaced by a log.

CASE.json: {"rst_output": 7, "verbose": true|false, "common": {...},
            "horizons": [{"name": ..., "initial_radius": r0, <option>: value, ...}, ...]}
Options are written as <option>_<n>.  Writes DIR/probe.athinput, DIR/athena.log, the
finder's files, DIR/summary.json (one record per horizon from the status file: decision
0040 item 3; with verbose the history of every search from the verbose file).
"""
import argparse
import glob
import json
import os
import struct
import subprocess
import sys
import time

SCOLS = ["cycle", "time", "found", "reason", "flow_iterations", "area", "area_mass",
         "meanradius", "minradius", "mean_expansion", "min_abs_mean_expansion",
         "points_outside_mesh"]
DEFAULTS = {"ah_found_a0": "false", "last_a0": "-1.0", "start_time": "0.0",
            "stop_time": "1.0e6", "center_x": "0.0", "center_y": "0.0", "center_z": "0.0",
            "use_puncture": "-1", "flow_alpha_beta_const": "1.0", "hmean_tol": "1.0e30",
            "mass_tol": "1.0e-5", "flow_iterations": "400", "polish_iterations": "0"}


def rst_header(path):
    """time, dt and cycle of a restart file."""
    with open(path, "rb") as f:
        b = f.read(1 << 20)
    i = b.find(b"<par_end>")
    if i < 0:
        raise SystemExit("no <par_end> in the first MiB of " + path)
    o = i + len(b"<par_end>\n") + 4 + 4 + 72 + 76 + 76
    t, dt = struct.unpack_from("<dd", b, o)
    (nc,) = struct.unpack_from("<i", b, o + 16)
    return dict(time=t, dt=dt, ncycle=nc)


def probe_input(case):
    hz = case["horizons"]
    lines = ["<fastflow>", "find_every = 1", "num_horizons = %d" % len(hz),
             "verbose = %s" % ("true" if case.get("verbose") else "false"),
             "diagnostics = true"]
    for k, v in case.get("common", {}).items():
        lines.append("%s = %s" % (k, v))
    for n, h in enumerate(hz):
        q = dict(DEFAULTS)
        q.update({k: str(v) for k, v in h.items() if k != "name"})
        for k, v in q.items():
            lines.append("%s_%d = %s" % (k, n, v))
    lines += ["", "<output%d>" % case.get("rst_output", 7), "file_type = log", ""]
    return "\n".join(lines)


def read_verbose(path):
    """histories of the searches in a verbose file: list of arrays (k, area, mass,
    meanradius, minradius, hmean)."""
    out, cur = [], None
    if not os.path.exists(path):
        return out
    for ln in open(path):
        p = ln.split()
        if ln.startswith("Searching for horizon"):
            cur = []
            out.append(cur)
        elif cur is not None and len(p) == 10:
            try:
                cur.append([float(x) for x in p[:6]])
            except ValueError:
                pass
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--rst", required=True)
    ap.add_argument("--case", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--threads", type=int, default=3)
    ap.add_argument("--extra", nargs="*", default=[], help="more athena arguments")
    a = ap.parse_args()
    case = json.load(open(a.case))
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    h = rst_header(a.rst)
    pin = os.path.join(out, "probe.athinput")
    with open(pin, "w") as f:
        f.write(probe_input(case))
    cmd = [a.exe, "-r", a.rst, "-i", pin, "-d", out, "time/nlim=%d" % (h["ncycle"] + 1),
           "time/tlim=%.6f" % (h["time"] + 10.0)] + list(a.extra)
    env = dict(os.environ, OMP_NUM_THREADS=str(a.threads), OMP_PROC_BIND="false",
               OPENBLAS_NUM_THREADS="1")
    t0 = time.time()
    with open(os.path.join(out, "athena.log"), "w") as log:
        log.write("# cmd: " + " ".join(cmd) + "\n")
        log.flush()
        rc = subprocess.run(cmd, cwd=out, env=env, stdout=log,
                            stderr=subprocess.STDOUT).returncode
    wall = time.time() - t0
    recs = []
    for n, hz in enumerate(case["horizons"]):
        rec = dict(horizon=n, name=hz.get("name", ""), options=hz, exit=rc, found=False)
        st = glob.glob(os.path.join(out, "*.horizon_status_%d.txt" % n))
        rows = [ln for f in st for ln in open(f) if ln.strip() and not ln.startswith("#")]
        if rows:
            vals = rows[-1].split("#")[0].split()
            rec.update(dict(zip(SCOLS, map(float, vals[:len(SCOLS)]))))
            rec["columns_all"] = [float(v) for v in vals]
            rec["found"] = int(float(vals[2])) == 1
            rec["reason"] = int(float(vals[3]))
            rec["reason_text"] = rows[-1].split("#", 1)[1].strip() if "#" in rows[-1] else ""
        vb = glob.glob(os.path.join(out, "*.horizon_verbose_%d.txt" % n))
        if vb:
            hist = read_verbose(vb[0])
            if hist and hist[-1]:
                rec["history_len"] = len(hist[-1])
                rec["history_meanradius_every20"] = [r[3] for r in hist[-1][::20]]
        recs.append(rec)
        print(n, rec.get("name"), "found" if rec["found"] else "not found",
              "reason", rec.get("reason"), "it", rec.get("flow_iterations"),
              "r", rec.get("meanradius"), "m", rec.get("area_mass"),
              "H", rec.get("mean_expansion"), flush=True)
    log = open(os.path.join(out, "athena.log")).read()
    summ = dict(exe=a.exe, rst=a.rst, header=h, exit=rc, wall_s=round(wall, 1),
                horizons=recs,
                log_lines=[ln for ln in log.splitlines()
                           if "FastFlow" in ln or "fastflow" in ln or "added" in ln][:60])
    json.dump(summ, open(os.path.join(out, "summary.json"), "w"), indent=1)
    print("exit", rc, "wall", round(wall, 1))
    return 0 if rc == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
