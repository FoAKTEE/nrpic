#!/usr/bin/env python3
"""FP of periodic_threshold (JOURNAL 2026-11-26, batch 31): the core-v0.8 horizon finder with
polishing, searching again on restart files of the periodic chains (P0L6, S1L).

    finder_probe_box.py --exe ATHENA --out DIR --set NAME [--threads 3] [--jobs 2] RST [RST ...]

Method of tracks/core/analysis/restart_finder/finder_probe.py (core, on main), rewritten for the
periodic box: each restart file is continued for exactly one cycle (time/nlim = ncycle + 1) with a
parameter file next to -r that sets the horizons below, all centred on the box centre and searched
once at the end of that cycle (find_every 1).  The restart output of the deck is replaced by a log so
that no restart file is written.  Two kinds of horizons:
  search  - a search with the given rule (mass_tol, flow_iterations, polish_iterations) from a start
            radius (initial_radius; ah_found_a0 = false, so every search starts there);
  sphere  - flow_iterations 1, no polishing: the status file then holds the surface integral of the
            expansion (column 10) and the area mass of the round coordinate sphere of that radius
            itself (the first flow iteration evaluates the start sphere; z4c/fastflow.cpp FastFlowLoop).
Writes DIR/probes.json and DIR/fig_finder_probe_box.{pdf,png}.  'found' is read ONLY from the status
file (decision 0040 item 3).
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

SETS = {
    # P0L6 (deck peak_leak6, start radius 0.15): line's outermost marginal sphere at t = 140 r = 0.103
    # (JOURNAL D2 outcome); verifier's outermost tracked trapped shell r ~ 0.012 (VERIFIER.md 2.3).
    "P0L6": dict(rst_output=7, searches=[
        ("v08 rule from 0.15", dict(mass_tol="1.0e-5", flow_iterations="400", polish_iterations="100"), 0.15),
        ("v08 rule from 0.103", dict(mass_tol="1.0e-5", flow_iterations="400", polish_iterations="100"), 0.103),
        ("v08 rule, 4000 it, from 0.15", dict(mass_tol="1.0e-5", flow_iterations="4000", polish_iterations="100"), 0.15),
        ("v08 rule, 4000 it, from 0.103", dict(mass_tol="1.0e-5", flow_iterations="4000", polish_iterations="100"), 0.103),
        ("v08 rule, 4000 it, from 0.012", dict(mass_tol="1.0e-5", flow_iterations="4000", polish_iterations="100"), 0.012),
        ("tight 1e-9, 4000 it, from 0.103", dict(mass_tol="1.0e-9", flow_iterations="4000"), 0.103),
    ], spheres=[0.005, 0.01, 0.02, 0.03, 0.05, 0.07, 0.09, 0.10, 0.11, 0.12, 0.13, 0.15, 0.2, 0.3, 0.5]),
    # S1L (deck peak_leak, start radius 0.6; failed searches stall at mean radius ~0.53, m ~ 20).
    "S1L": dict(rst_output=7, searches=[
        ("v08 rule from 0.6", dict(mass_tol="1.0e-5", flow_iterations="400", polish_iterations="100"), 0.6),
        ("v08 rule from 0.2", dict(mass_tol="1.0e-5", flow_iterations="400", polish_iterations="100"), 0.2),
        ("v08 rule, 4000 it, from 0.6", dict(mass_tol="1.0e-5", flow_iterations="4000", polish_iterations="100"), 0.6),
        ("v08 rule, 4000 it, from 0.2", dict(mass_tol="1.0e-5", flow_iterations="4000", polish_iterations="100"), 0.2),
        ("v08 rule, 4000 it, from 0.1", dict(mass_tol="1.0e-5", flow_iterations="4000", polish_iterations="100"), 0.1),
        ("tight 1e-9, 4000 it, from 0.3", dict(mass_tol="1.0e-9", flow_iterations="4000"), 0.3),
    ], spheres=[0.03, 0.05, 0.08, 0.12, 0.16, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.5]),
    # FPb (JOURNAL outcome FP, 15:45): dating S1L's first trapped round sphere on earlier restart files
    "S1Lscan": dict(rst_output=7, searches=[],
                    spheres=[0.02, 0.03, 0.05, 0.08, 0.12, 0.16, 0.2, 0.3]),
    # FPb: a long search on S1L at t = 220 from inside the trapped band
    "S1Llong": dict(rst_output=7, searches=[
        ("v08 rule, 12000 it, from 0.16", dict(mass_tol="1.0e-5", flow_iterations="12000", polish_iterations="100"), 0.16),
    ], spheres=[]),
    # FPb: P0L6 just before the first tracked shell is 'trapped in the code' (t = 122.2, verifier)
    "P0L6scan": dict(rst_output=7, searches=[],
                     spheres=[0.01, 0.02, 0.03, 0.05, 0.07, 0.09, 0.11, 0.13]),
}
SCOLS = ["cycle", "time", "found", "reason", "flow_iterations", "area", "area_mass", "meanradius",
         "minradius", "mean_expansion", "min_abs_mean_expansion", "points_outside_mesh"]


def rst_header(path):
    """time, dt and cycle of a restart file (as core's finder_probe.py reads it)."""
    with open(path, "rb") as f:
        b = f.read(1 << 20)
    i = b.find(b"<par_end>")
    if i < 0:
        raise SystemExit("no <par_end> in the first MiB of " + path)
    o = i + len(b"<par_end>\n") + 4 + 4 + 72 + 76 + 76
    t, dt = struct.unpack_from("<dd", b, o)
    (nc,) = struct.unpack_from("<i", b, o + 16)
    return dict(time=t, dt=dt, ncycle=nc)


def horizons(setname):
    s = SETS[setname]
    hz = []
    for name, rule, r0 in s["searches"]:
        hz.append(dict(kind="search", name=name, r0=r0, rule=rule))
    for r in s["spheres"]:
        hz.append(dict(kind="sphere", name="sphere %.3f" % r, r0=r,
                       rule=dict(mass_tol="1.0e-5", flow_iterations="1")))
    return hz


def probe_input(setname):
    hz = horizons(setname)
    p = {"find_every": "1", "num_horizons": str(len(hz)), "verbose": "false", "diagnostics": "true"}
    for n, h in enumerate(hz):
        q = dict(h["rule"])
        q.update({"initial_radius": "%.6g" % h["r0"], "ah_found_a0": "false", "last_a0": "-1.0",
                  "start_time": "0.0", "stop_time": "1.0e6", "center_x": "0.0", "center_y": "0.0",
                  "center_z": "0.0", "use_puncture": "-1", "flow_alpha_beta_const": "1.0",
                  "hmean_tol": "1.0e30"})
        if "polish_iterations" not in q:
            q["polish_iterations"] = "0"
        for k, v in q.items():
            p["%s_%d" % (k, n)] = v
    txt = "<fastflow>\n" + "".join("%s = %s\n" % kv for kv in p.items())
    return txt + "\n<output%d>\nfile_type = log\n" % SETS[setname]["rst_output"]


def one(rst, out, exe, threads, setname):
    h = rst_header(rst)
    d = os.path.join(out, "%s_t%.1f" % (setname, h["time"]))
    os.makedirs(d, exist_ok=True)
    pin = os.path.join(d, "probe.athinput")
    with open(pin, "w") as f:
        f.write(probe_input(setname))
    cmd = [exe, "-r", rst, "-i", pin, "-d", d, "time/nlim=%d" % (h["ncycle"] + 1),
           "time/tlim=%.6f" % (h["time"] + 10.0)]
    env = dict(os.environ, OMP_NUM_THREADS=str(threads), OMP_PROC_BIND="false",
               OPENBLAS_NUM_THREADS="1")
    t0 = time.time()
    with open(os.path.join(d, "athena.log"), "w") as log:
        log.write("# cmd: " + " ".join(cmd) + "\n")
        log.flush()
        rc = subprocess.run(cmd, cwd=d, env=env, stdout=log, stderr=subprocess.STDOUT).returncode
    wall = time.time() - t0
    recs = []
    for n, hz in enumerate(horizons(setname)):
        rec = dict(set=setname, dump=os.path.basename(rst), rst=rst, time_dump=h["time"],
                   ncycle=h["ncycle"], horizon=n, kind=hz["kind"], name=hz["name"], r0=hz["r0"],
                   rule=hz["rule"], exit=rc, wall_s=wall, found=False)
        st = glob.glob(os.path.join(d, "*.horizon_status_%d.txt" % n))
        rows = [ln.split("#")[0].split() for f in st for ln in open(f)
                if ln.strip() and not ln.startswith("#")]
        if rows:
            vals = list(map(float, rows[-1][:len(SCOLS)]))
            rec.update(dict(zip(SCOLS, vals)))
            rec["found"] = int(vals[2]) == 1
            rec["reason"] = int(vals[3])
            last = [ln for f in st for ln in open(f) if ln.strip() and not ln.startswith("#")][-1]
            rec["reason_text"] = last.split("#", 1)[1].strip() if "#" in last else ""
        recs.append(rec)
    return recs


def figure(out, recs):
    import numpy as np
    sys.path.insert(0, HERE)
    import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.1))
    fig.subplots_adjust(left=0.10, right=0.985, bottom=0.16, top=0.93, wspace=0.30)
    dumps = sorted({(r["set"], r["time_dump"]) for r in recs})
    cyc = [fs.PAL[c] for c in ("blue", "red", "green", "yellow", "purple", "cyan") if c in fs.PAL]
    if len(cyc) < len(dumps):
        cyc = cyc + ["k"] * len(dumps)
    for i, (s, t) in enumerate(dumps):
        sp = sorted([r for r in recs if r["set"] == s and r["time_dump"] == t and r["kind"] == "sphere"
                     and "mean_expansion" in r], key=lambda r: r["r0"])
        if sp:
            x = np.array([r["r0"] for r in sp])
            y = np.array([r["mean_expansion"] for r in sp])
            axs[0].plot(x, np.sign(y) * np.log10(1.0 + np.abs(y)), color=cyc[i], marker="o", ms=3,
                        label="%s t = %.0f" % (s, t))
        se = [r for r in recs if r["set"] == s and r["time_dump"] == t and r["kind"] == "search"
              and "meanradius" in r]
        for r in se:
            mk = "*" if r["found"] else "x"
            axs[1].plot([r["r0"]], [r["meanradius"]], color=cyc[i], marker=mk, ms=7 if r["found"] else 5,
                        ls="none")
        axs[1].plot([], [], color=cyc[i], marker="x", ls="none", label="%s t = %.0f" % (s, t))
    axs[0].axhline(0.0, **fs.MASK_LINE)
    axs[0].set_xscale("log")
    axs[0].set_xlabel("radius of the round coordinate sphere")
    axs[0].set_ylabel(r"sign$\cdot\log_{10}(1+|\oint\Theta|)$")
    axs[0].legend(loc="best", fontsize=7)
    lim = [0.005, 2.0]
    axs[1].plot(lim, lim, **fs.MASK_LINE)
    axs[1].set_xscale("log"); axs[1].set_yscale("log")
    axs[1].set_xlabel("start radius of the search")
    axs[1].set_ylabel("mean radius at the end of the search")
    axs[1].legend(loc="best", fontsize=7, title="x not found, * found", title_fontsize=7)
    fs.no_minor_labels(axs[0]); fs.no_minor_labels(axs[1])
    return fs.save(fig, os.path.join(out, "fig_finder_probe_box"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rst", nargs="+")
    ap.add_argument("--exe", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--set", required=True, action="append",
                    help="one per rst, in order, or one for all")
    ap.add_argument("--threads", type=int, default=3)
    ap.add_argument("--jobs", type=int, default=2)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    sets = a.set if len(a.set) == len(a.rst) else a.set * len(a.rst)
    recs = []
    with cf.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        futs = [ex.submit(one, r, out, a.exe, a.threads, s) for r, s in zip(a.rst, sets)]
        for f in cf.as_completed(futs):
            recs += f.result()
            with open(os.path.join(out, "probes.json"), "w") as fo:
                json.dump(sorted(recs, key=lambda r: (r["set"], r["time_dump"], r["horizon"])), fo, indent=1)
    recs.sort(key=lambda r: (r["set"], r["time_dump"], r["horizon"]))
    figs = figure(out, recs)
    false_acc = [r for r in recs if r["found"] and (r.get("mean_expansion", 0) > 0 or r.get("meanradius", 0) > 1.0)]
    summ = dict(exe=a.exe, n_records=len(recs), exits=sorted({r["exit"] for r in recs}),
                found=[(r["set"], r["time_dump"], r["name"], r.get("area_mass"), r.get("meanradius"))
                       for r in recs if r["found"]],
                false_acceptance_candidates=[(r["set"], r["time_dump"], r["name"]) for r in false_acc],
                figures=figs)
    with open(os.path.join(out, "probes.json"), "w") as fo:
        json.dump(recs, fo, indent=1)
    with open(os.path.join(out, "summary.json"), "w") as fo:
        json.dump(summ, fo, indent=1)
    for r in recs:
        print("%-5s t=%6.1f h%02d %-34s found=%d reason=%s it=%s m=%s rbar=%s Theta=%s exit=%d wall=%.0f" % (
            r["set"], r["time_dump"], r["horizon"], r["name"], r["found"], r.get("reason"),
            r.get("flow_iterations"), "%.4g" % r["area_mass"] if "area_mass" in r else "-",
            "%.4g" % r["meanradius"] if "meanradius" in r else "-",
            "%.4g" % r["mean_expansion"] if "mean_expansion" in r else "-", r["exit"], r["wall_s"]))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
