#!/usr/bin/env python3
"""Re-search of the apparent horizon in restart dumps with the new stopping rule
(core/restart-finder, item 2a; method of Track D's
tracks/D-bh-dress/puncture_drift/tools/probe_finder.py, rewritten here for the new option).

    python finder_probe.py --exe ATHENA --out DIR [--threads 2] [--jobs 3] RST [RST ...]

Each dump is restarted for exactly one cycle (time/nlim = ncycle + 1) with a parameter
file given next to -r, which adds four horizons centred on the origin, searched once at
the end of that cycle:
  h0  recommended setting: mass_tol 1e-5, 100 polishing iterations, started from the
      radius stored in the dump (what a run with the option does)
  h1  tight rule: mass_tol 1e-9, 4000 iterations, from r = 1 M (the reference)
  h2  loose tolerance with polishing: mass_tol 1e-2, 100 iterations, from r = 2 M
  h3  recommended setting from r = 2 M (outside)
(The first registered run of this script, core-20261125-131950-1fb387d, had h0 = 1e-2
with polishing from the stored radius, h2 = Track D's production rule 1e-5 without
polishing from 2 M, h3 = 1e-2 with polishing from 2 M, and the first form of the rule.)
The restart output of the dump's deck (output2) is replaced by an event log, so that no
restart file is written.  Writes DIR/probes.json (one record per dump and horizon) and
DIR/fig_finder_probe.{pdf,png}; exit status 0 if h0 and h3 lie within 2e-5 of h1 at every
dump.  "found" is taken from the status file (the summary file repeats old values when a
search fails).
"""
import argparse
import concurrent.futures as cf
import glob
import json
import os
import struct
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
COLS = ["iter", "time", "mass", "Sx", "Sy", "Sz", "S", "area", "hrms", "hmean",
        "meanradius", "minradius"]
HOR = {
    0: dict(mass_tol="1.0e-5", flow_iterations="400", polish_iterations="100"),
    1: dict(mass_tol="1.0e-9", flow_iterations="4000", initial_radius="1.0"),
    2: dict(mass_tol="1.0e-2", flow_iterations="400", polish_iterations="100",
            initial_radius="2.0"),
    3: dict(mass_tol="1.0e-5", flow_iterations="400", polish_iterations="100",
            initial_radius="2.0"),
}
NAMES = {0: "1e-5 + 100, stored radius", 1: "tight rule", 2: "1e-2 + 100 from outside",
         3: "1e-5 + 100 from outside"}


def rst_header(path):
    """time, dt and cycle of a restart file (outputs/restart.cpp: after the parameter
    dump two int32, RegionSize of nine doubles, two RegionIndcs of nineteen int32)."""
    with open(path, "rb") as f:
        b = f.read(1 << 20)
    i = b.find(b"<par_end>")
    if i < 0:
        raise SystemExit("no <par_end> in the first MiB of " + path)
    o = i + len(b"<par_end>\n") + 4 + 4 + 72 + 76 + 76
    t, dt = struct.unpack_from("<dd", b, o)
    (nc,) = struct.unpack_from("<i", b, o + 16)
    return dict(time=t, dt=dt, ncycle=nc)


def probe_input():
    p = {"find_every": "1", "num_horizons": str(len(HOR)), "verbose": "false",
         "diagnostics": "true"}
    for n, h in HOR.items():
        for k, v in h.items():
            p["%s_%d" % (k, n)] = v
        if n > 0:
            p.update({"start_time_%d" % n: "0.0", "stop_time_%d" % n: "1.0e6",
                      "center_x_%d" % n: "0.0", "center_y_%d" % n: "0.0",
                      "center_z_%d" % n: "0.0", "use_puncture_%d" % n: "-1",
                      "flow_alpha_beta_const_%d" % n: "1.0", "hmean_tol_%d" % n: "100.0"})
    txt = "<fastflow>\n" + "".join("%s = %s\n" % kv for kv in p.items())
    return txt + "\n<output2>\nfile_type = log\n"


def one(rst, out, exe, threads):
    h = rst_header(rst)
    d = os.path.join(out, os.path.basename(rst)[:-4])
    os.makedirs(d, exist_ok=True)
    pin = os.path.join(d, "probe.athinput")
    with open(pin, "w") as f:
        f.write(probe_input())
    cmd = [exe, "-r", rst, "-i", pin, "-d", d, "time/nlim=%d" % (h["ncycle"] + 1),
           "time/tlim=%.6f" % (h["time"] + 10.0)]
    env = dict(os.environ, OMP_NUM_THREADS=str(threads), OMP_PROC_BIND="false",
               OPENBLAS_NUM_THREADS="1")
    t0 = time.time()
    with open(os.path.join(d, "athena.log"), "w") as log:
        log.write("# cmd: " + " ".join(cmd) + "\n")
        log.flush()
        rc = subprocess.run(cmd, cwd=d, env=env, stdout=log,
                            stderr=subprocess.STDOUT).returncode
    wall = time.time() - t0
    recs = []
    for n in HOR:
        rec = dict(dump=os.path.basename(rst), rst=rst, time_dump=h["time"],
                   ncycle=h["ncycle"], horizon=n, rule=NAMES[n], exit=rc, wall_s=wall,
                   found=False)
        hits = glob.glob(os.path.join(d, "*.horizon_summary_%d.txt" % n))
        rows = [ln.split() for f in hits for ln in open(f)
                if ln.strip() and not ln.startswith("#")]
        if rows:
            rec.update(dict(zip(COLS, map(float, rows[-1]))))
            rec["found"] = (rec["mass"] == rec["mass"])
        st = glob.glob(os.path.join(d, "*.horizon_status_%d.txt" % n))
        rows = [ln.split("#")[0].split() for f in st for ln in open(f)
                if ln.strip() and not ln.startswith("#")]
        if rows:
            rec["flow_iterations_done"] = int(float(rows[-1][4]))
            rec["found"] = rec["found"] and (int(float(rows[-1][2])) == 1)
            rec["reason"] = int(float(rows[-1][3]))
        recs.append(rec)
    return recs


def figure(out, recs):
    import numpy as np
    sys.path.insert(0, os.path.join(REPO, "python"))
    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.11, right=0.985, bottom=0.16, top=0.96, wspace=0.3)
    cols = {0: fs.PAL["red"], 1: fs.PAL["blue"], 2: fs.PAL["yellow"], 3: fs.PAL["green"]}
    by = {}
    for r in recs:
        if r["found"]:
            by.setdefault(r["horizon"], []).append((r["time_dump"], r["mass"]))
    ref = dict(by.get(1, []))
    for n in sorted(by):
        t, m = map(np.array, zip(*sorted(by[n])))
        axs[0].plot(t, m, color=cols[n], marker="o", ms=3, ls="-" if n in (0, 1) else "--",
                    label=NAMES[n])
        if n != 1:
            dm = np.array([abs(mm - ref[tt]) for tt, mm in zip(t, m) if tt in ref])
            tt = np.array([x for x in t if x in ref])
            axs[1].semilogy(tt, np.maximum(dm, 1e-16), color=cols[n], marker="o", ms=3,
                            ls="-" if n == 0 else "--", label=NAMES[n])
    axs[1].axhline(2.0e-5, **fs.MASK_LINE)
    axs[0].set_xlabel("t / M"); axs[0].set_ylabel("horizon mass")
    axs[0].ticklabel_format(axis="y", useOffset=False)
    axs[1].set_xlabel("t / M"); axs[1].set_ylabel("|mass - mass of the tight rule|")
    axs[0].legend(loc="best", fontsize=7)
    axs[1].legend(loc="best", fontsize=7)
    fs.no_minor_labels(axs[1])
    return fs.save(fig, os.path.join(out, "fig_finder_probe"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rst", nargs="+")
    ap.add_argument("--exe", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--threads", type=int, default=2)
    ap.add_argument("--jobs", type=int, default=3)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    recs = []
    with cf.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        for f in cf.as_completed([ex.submit(one, r, out, a.exe, a.threads) for r in a.rst]):
            recs += f.result()
            with open(os.path.join(out, "probes.json"), "w") as fo:
                json.dump(sorted(recs, key=lambda r: (r["time_dump"], r["horizon"])), fo, indent=1)
    recs.sort(key=lambda r: (r["time_dump"], r["horizon"]))
    ref = {r["dump"]: r["mass"] for r in recs if r["horizon"] == 1 and r["found"]}
    worst = {}
    for r in recs:
        if r["found"] and r["dump"] in ref:
            r["dmass_tight"] = r["mass"] - ref[r["dump"]]
            worst[r["horizon"]] = max(worst.get(r["horizon"], 0.0), abs(r["dmass_tight"]))
    ndump = len(a.rst)
    ck = {
        "every probe ended with status 0": all(r["exit"] == 0 for r in recs),
        "tight rule found at every dump": len(ref) == ndump,
        "1e-5 with polishing from the stored radius within 2e-5 of the tight rule at every dump "
        "(max %.2e)" % worst.get(0, float("nan")):
            sum(1 for r in recs if r["horizon"] == 0 and r["found"]) == ndump
            and worst.get(0, 1.0) < 2.0e-5,
        "1e-5 with polishing from outside within 2e-5 of the tight rule at every dump (max %.2e)"
        % worst.get(3, float("nan")):
            sum(1 for r in recs if r["horizon"] == 3 and r["found"]) == ndump
            and worst.get(3, 1.0) < 2.0e-5,
    }
    figs = figure(out, recs)
    with open(os.path.join(out, "probes.json"), "w") as fo:
        json.dump(recs, fo, indent=1)
    with open(os.path.join(out, "summary.json"), "w") as fo:
        json.dump(dict(exe=a.exe, checks=ck, worst_abs_dmass={NAMES[k]: v for k, v in worst.items()},
                       figures=figs, all_ok=all(ck.values())), fo, indent=1)
    for k, v in ck.items():
        print("%-4s %s" % ("ok" if v else "FAIL", k))
    for r in recs:
        print("%s t=%7.2f h%d %-24s found=%s mass=%s d=%s it=%s wall=%.0f" % (
            r["dump"], r["time_dump"], r["horizon"], r["rule"], r["found"],
            "%.9f" % r["mass"] if r["found"] else "-",
            "%+.2e" % r["dmass_tight"] if "dmass_tight" in r else "-",
            r.get("flow_iterations_done", "-"), r["wall_s"]))
    return 0 if all(ck.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
