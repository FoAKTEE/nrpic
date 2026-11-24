#!/usr/bin/env python3
"""Tests of the orderly stop on SIGTERM (athenak/src/utils/term_signal.cpp).

    python term_test.py --exe ATHENA --out DIR [--cases S1,S2,S1d,S0] [--big 256]

S1   problems/tests/term_signal_periodic.athinput (Z4c in a periodic box, no matter)
S2   problems/tests/term_signal_particles.athinput (particles and Z4c, periodic)
S1d  S1 with two SIGTERM 0.3 s apart (Slurm sends the signal at the preemption and again
     at the end of the grace time; wrappers forward it as well)
S0   S1 with the signal sent before the main loop (during the set-up)
Each case: run A without interruption; run B is started, receives SIGTERM once its log
shows cycle >= K, must exit with status 143 after writing a restart file, and is
continued with `-r <newest restart file>` in the same directory.  Then every file of A is
compared with B byte for byte, except the logs and the restart files: B has one restart
file more, so the numbers of the later ones are shifted by one; the last restart file of
A and of B are compared after their parameter dumps, and the dumps line by line, where
only `file_number` of the restart output may differ.

--big N  measures instead how long the restart file of an N^3 box of Z4c takes to write:
the deck of S1 with N^3 cells in 64^3 MeshBlocks, SIGTERM during the set-up, time read
from the line the code prints.

Writes DIR/summary.json and DIR/fig_term_test.{pdf,png}; exit status 0 if every check
holds.
"""
import argparse
import glob
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DECKS = {"S1": "term_signal_periodic.athinput", "S2": "term_signal_particles.athinput",
         "S1d": "term_signal_periodic.athinput", "S0": "term_signal_periodic.athinput"}
KSIG = {"S1": 100, "S2": 25, "S1d": 60, "S0": -1}    # cycle at which the signal is sent


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def last_cycle(log):
    try:
        with open(log, "rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - 4000))
            tail = f.read().decode(errors="replace")
    except OSError:
        return -1
    m = re.findall(r"cycle=(\d+)", tail)
    return int(m[-1]) if m else -1


def start(exe, args, rundir, log):
    os.makedirs(rundir, exist_ok=True)
    f = open(log, "ab")
    p = subprocess.Popen([exe] + args + ["-d", rundir], stdout=f, stderr=subprocess.STDOUT,
                         cwd=rundir)
    return p, f


def newest_rst(rundir):
    fs = glob.glob(os.path.join(rundir, "rst", "*.rst"))
    return max(fs, key=lambda x: (os.path.getmtime(x), x)) if fs else None


def split_rst(path):
    with open(path, "rb") as f:
        b = f.read()
    i = b.index(b"<par_end>")
    return b[:i].decode(errors="replace").splitlines(), b[i:]


def prepare(case, out, extra):
    deck = os.path.join(REPO, "problems", "tests", DECKS[case])
    args = ["-i", deck] + extra
    pre = None
    if case == "S2":
        ic = os.path.join(out, case, "ic")
        os.makedirs(ic, exist_ok=True)
        if not os.path.exists(os.path.join(ic, "particles.nrp")):
            subprocess.run([sys.executable, os.path.join(REPO, "cosmo", "ic", "make_lattice.py"),
                            "--n", "16", "--ppc", "1", "--L", "4", "--noise-x", "0.05",
                            "--noise-u", "0.05", "--seed", "7", "--out", ic], check=True,
                           cwd=os.path.join(REPO, "cosmo", "ic"))
        args += ["particles/particle_file=" + os.path.join(ic, "particles.nrp")]
        pre = sha(os.path.join(ic, "particles.nrp"))
    return args, pre


def run_case(case, exe, out):
    res = {"case": case, "deck": DECKS[case], "checks": {}}
    args, pre = prepare(case, out, [])
    res["particle_file_sha256"] = pre
    da, db = os.path.join(out, case, "A"), os.path.join(out, case, "B")
    # A: uninterrupted
    t0 = time.time()
    p, f = start(exe, args, da, os.path.join(da, "athena.log"))
    rc = p.wait(); f.close()
    res["A_rc"], res["A_wall_s"] = rc, round(time.time() - t0, 2)
    res["A_cycles"] = last_cycle(os.path.join(da, "athena.log"))
    # B: signal, then continuation
    log1 = os.path.join(db, "athena.seg1.log")
    p, f = start(exe, args, db, log1)
    k = KSIG[case]
    if k < 0:
        time.sleep(0.05)                    # during the set-up
    else:
        while p.poll() is None and last_cycle(log1) < k:
            time.sleep(0.01)
    t_sig = time.time()
    if p.poll() is None:
        os.kill(p.pid, signal.SIGTERM)
        if case == "S1d":
            time.sleep(0.3)
            if p.poll() is None:
                os.kill(p.pid, signal.SIGTERM)
    rc1 = p.wait(); f.close()
    res["B_seg1_rc"] = rc1
    res["B_exit_after_signal_s"] = round(time.time() - t_sig, 3)
    txt = open(log1, errors="replace").read()
    m = re.search(r"restart outputs written after the cycle in progress: (\d+) in ([0-9.]+) s, "
                  r"done ([0-9.]+) s after the signal", txt)
    res["B_message"] = m.group(0) if m else None
    res["B_seg1_cycle"] = last_cycle(log1)
    rst = newest_rst(db)
    res["B_restart_on_signal"] = os.path.relpath(rst, db) if rst else None
    ck = res["checks"]
    ck["A ended by itself (status 0)"] = (res["A_rc"] == 0)
    ck["B stopped with status 143"] = (rc1 == 143)
    ck["B printed 'Terminating on signal SIGTERM'"] = ("Terminating on signal SIGTERM" in txt)
    ck["B stopped before the end"] = (0 <= res["B_seg1_cycle"] < res["A_cycles"]) or k < 0
    ck["B wrote a restart file on the signal"] = bool(m) and rst is not None and \
        os.path.getmtime(rst) >= t_sig - 1.0
    if rst is None:
        return res
    log2 = os.path.join(db, "athena.seg2.log")
    p, f = start(exe, ["-r", rst], db, log2)
    rc2 = p.wait(); f.close()
    res["B_seg2_rc"] = rc2
    ck["B continued to the end (status 0)"] = (rc2 == 0)
    # comparison
    skip = re.compile(r"(^|/)(athena[^/]*\.log|rst/.*)$")
    fa = sorted(os.path.relpath(os.path.join(r, x), da) for r, _, xs in os.walk(da) for x in xs)
    fb = sorted(os.path.relpath(os.path.join(r, x), db) for r, _, xs in os.walk(db) for x in xs)
    fa_c = [x for x in fa if not skip.search(x)]
    fb_c = [x for x in fb if not skip.search(x)]
    diff, nbytes = [], 0
    for x in fa_c:
        pa, pb = os.path.join(da, x), os.path.join(db, x)
        if not os.path.exists(pb) or sha(pa) != sha(pb):
            diff.append(x)
        nbytes += os.path.getsize(pa)
    res["files_compared"], res["bytes_compared"] = len(fa_c), nbytes
    res["files_differing"] = diff
    res["files_only_in_B"] = [x for x in fb_c if x not in fa_c]
    ck["same set of output files"] = (fa_c == fb_c)
    ck["every output file byte-identical"] = (not diff)
    ra = sorted(glob.glob(os.path.join(da, "rst", "*.rst")))
    rb = sorted(glob.glob(os.path.join(db, "rst", "*.rst")))
    res["A_rst"], res["B_rst"] = len(ra), len(rb)
    ck["B has one restart file more"] = (len(rb) == len(ra) + 1)
    if ra and rb:
        (pa, ba), (pb, bb) = split_rst(ra[-1]), split_rst(rb[-1])
        ck["last restart file: data identical"] = (ba == bb)
        res["last_rst_bytes"] = len(ba)
        dl = [(x, y) for x, y in zip(pa, pb) if x != y]
        res["last_rst_parameter_lines_differing"] = dl
        ck["last restart file: parameters differ only in file_number of the rst output"] = (
            len(pa) == len(pb) and len(dl) <= 1 and all("file_number" in x for x, _ in dl))
        for ext in (".prt", ".amr", ".sf"):
            if os.path.exists(ra[-1] + ext):
                ck["last restart file: %s identical" % ext] = (
                    os.path.exists(rb[-1] + ext) and sha(ra[-1] + ext) == sha(rb[-1] + ext))
    return res


def run_big(n, exe, out):
    deck = os.path.join(REPO, "problems", "tests", DECKS["S1"])
    d = os.path.join(out, "big%d" % n)
    args = ["-i", deck, "mesh/nx1=%d" % n, "mesh/nx2=%d" % n, "mesh/nx3=%d" % n,
            "meshblock/nx1=64", "meshblock/nx2=64", "meshblock/nx3=64", "time/nlim=2"]
    log = os.path.join(d, "athena.log")
    t0 = time.time()
    p, f = start(exe, args, d, log)
    time.sleep(2.0)
    os.kill(p.pid, signal.SIGTERM)
    rc = p.wait(); f.close()
    txt = open(log, errors="replace").read()
    m = re.search(r"restart outputs written after the cycle in progress: (\d+) in ([0-9.]+) s, "
                  r"done ([0-9.]+) s after the signal", txt)
    rst = newest_rst(d)
    res = {"case": "big%d" % n, "rc": rc, "wall_s": round(time.time() - t0, 1),
           "message": m.group(0) if m else None,
           "write_s": float(m.group(2)) if m else None,
           "after_signal_s": float(m.group(3)) if m else None,
           "cycle": last_cycle(log),
           "rst_bytes": os.path.getsize(rst) if rst else None,
           "rst_files": sorted(os.path.basename(x) for x in glob.glob(os.path.join(d, "rst", "*")))}
    if res["write_s"] and res["rst_bytes"]:
        res["MB_per_s"] = round(res["rst_bytes"]/1e6/res["write_s"], 1)
    res["checks"] = {"stopped with status 143": rc == 143, "restart file written": bool(m and rst)}
    # the restart files of this measurement are large and of no further use
    for x in glob.glob(os.path.join(d, "rst", "tsp.*.rst")):
        os.unlink(x)
    return res


def read_hst(path):
    rows = []
    with open(path) as f:
        for ln in f:
            if ln.startswith("#") or not ln.strip():
                continue
            try:
                rows.append([float(v) for v in ln.split()])
            except ValueError:
                pass
    return rows


def figure(out, results):
    sys.path.insert(0, os.path.join(REPO, "python"))
    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    import numpy as np
    fs.use_style()
    cases = [r for r in results if r["case"] in DECKS and "B_seg2_rc" in r]
    if not cases:
        return
    fig, axs = plt.subplots(2, len(cases), figsize=(3.4*len(cases), 4.6), squeeze=False,
                            sharex="col")
    for j, r in enumerate(cases):
        c = r["case"]
        base = "tsq" if c == "S2" else "tsp"
        ha = np.array(read_hst(os.path.join(out, c, "A", base + ".z4c.user.hst")))
        hb = np.array(read_hst(os.path.join(out, c, "B", base + ".z4c.user.hst")))
        col = min(3, ha.shape[1] - 1)
        ax = axs[0, j]
        ax.semilogy(ha[:, 0], np.abs(ha[:, col]) + 1e-300, "-", color=fs.SERIES[0], lw=1.6,
                    label="uninterrupted")
        ax.semilogy(hb[:, 0], np.abs(hb[:, col]) + 1e-300, "--", color=fs.SERIES[1], lw=1.0,
                    label="SIGTERM, continued")
        tsig = None
        for ln in open(os.path.join(out, c, "B", "athena.seg1.log"), errors="replace"):
            m = re.match(r"time=([-+0-9.eE]+) cycle=", ln)
            if m:
                tsig = float(m.group(1))
        if tsig is not None:
            for a in axs[:, j]:
                a.axvline(tsig, color="k", lw=0.6, ls=":")
        ax.set_title("%s: %s" % (c, r["deck"].replace(".athinput", "")), fontsize=8)
        ax.set_ylabel("history column %d" % (col + 1))
        if j == 0:
            ax.legend(frameon=False, fontsize=7)
        ax = axs[1, j]
        n = min(len(ha), len(hb))
        d = np.max(np.abs(ha[:n, 1:] - hb[:n, 1:]), axis=1)
        ax.plot(ha[:n, 0], d, "o", ms=2.5, color=fs.SERIES[2])
        ax.set_ylabel("max |difference|, all columns")
        ax.set_xlabel("t")
        ax.set_ylim(-1e-16, 1e-15)
        ax.text(0.04, 0.86, "%d files, %.1f MB compared: %d differ" % (
            r["files_compared"], r["bytes_compared"]/1e6, len(r["files_differing"])),
            transform=ax.transAxes, fontsize=7)
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "fig_term_test"))
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cases", default="S1,S2,S1d,S0")
    ap.add_argument("--big", type=int, default=0)
    a = ap.parse_args()
    exe, out = os.path.abspath(a.exe), os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    results = []
    if a.big:
        results.append(run_big(a.big, exe, out))
    else:
        for c in a.cases.split(","):
            results.append(run_case(c, exe, out))
    ok = all(all(r["checks"].values()) for r in results)
    summary = {"exe": exe, "exe_sha256": sha(exe), "results": results,
               "verdict": "PASS" if ok else "FAIL"}
    with open(os.path.join(out, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1)
        f.write("\n")
    for r in results:
        print("==", r["case"], {k: v for k, v in r.items() if k not in ("checks",)})
        for k, v in r["checks"].items():
            print("   %-78s %s" % (k, "held" if v else "FAILED"))
    if not a.big:
        figure(out, results)
    print("TEST", summary["verdict"])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
