#!/usr/bin/env python3
"""Batch 25, prediction R25 of tracks/F-hills/JOURNAL.md: does a restart with an extra input
file (`-r <rst> -i <file>` holding `<fastflow> diagnostics = true`, decision 0043 item 5) start
on the build of A2's chain, write the finder's status file, and leave every other output of a
few cycles byte-identical?

    b25_diag_restart.py --out DIR [--exe ATHENA] [--wrapper WRAPPER]

The executable is run through the chain's own wrapper (athena_resume_bc.sh) with
NRPIC_REAL_ATHENA pointing at the processor build of release core-v0.5 (the release of A2's
card build), with the chain's argument order `-r rst/<file> -d <dir> -t 00:50:00 <extra>`.
Deck: problems/tests/by_horizon_coarse.athinput (nrpic_cf puncture, AMR, tracker, finder every
cycle) with a restart output every cycle.
  first: -i deck, nlim = 2
  b:  -r <copy of first's newest restart> ... -i add.athinput time/nlim=5
  c:  -r <same> ... time/nlim=5                       (control)
  b2: -r <b's newest restart> ... -i add.athinput time/nlim=6
Writes DIR/summary.json and DIR/fig_diag_restart.{pdf,png}; exit 0 if R25-1 to R25-3 hold.
"""
import argparse
import filecmp
import glob
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TRACK = os.path.abspath(os.path.join(HERE, "..", ".."))
REPO = os.path.abspath(os.path.join(TRACK, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))

EXE = "/data/haiyangw/nrpic/.work/build_cpu_v05/src/athena"
WRAP = os.path.join(TRACK, "binary_conv", "scripts", "athena_resume_bc.sh")


def run(cmd, d, name, env=None):
    t0 = time.time()
    with open(os.path.join(d, name + ".log"), "w") as log:
        rc = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, cwd=d, env=env).returncode
    return rc, time.time() - t0


def newest_rst(d):
    r = sorted(glob.glob(os.path.join(d, "rst", "*.rst")))
    return r[-1] if r else None


def outputs(d):
    """Output files of a run directory, relative paths, without logs, inputs and restarts."""
    out = []
    for p in sorted(glob.glob(os.path.join(d, "*"))):
        b = os.path.basename(p)
        if os.path.isdir(p) or b.endswith(".log") or b.endswith(".athinput"):
            continue
        out.append(b)
    return out


def records(path):
    if not os.path.exists(path):
        return []
    return [l for l in open(path).read().splitlines() if l.strip() and not l.startswith("#")]


def fastflow_block(rst):
    with open(rst, "rb") as f:
        head = f.read(200000).decode("latin-1")
    i = head.find("<fastflow>")
    if i < 0:
        return ""
    j = head.find("\n<", i + 5)
    return head[i:j if j > 0 else i + 20000]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--exe", default=EXE)
    ap.add_argument("--wrapper", default=WRAP)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    env = dict(os.environ, NRPIC_REAL_ATHENA=a.exe, OMP_NUM_THREADS="1")
    res = {"exe": a.exe, "wrapper": a.wrapper}

    deck = open(os.path.join(REPO, "problems", "tests", "by_horizon_coarse.athinput")).read()
    deck += "\n<output2>\nfile_type = rst\ndcycle    = 1\n"
    d0 = os.path.join(out, "first")
    os.makedirs(d0, exist_ok=True)
    with open(os.path.join(d0, "hc.athinput"), "w") as fp:
        fp.write(deck)
    rc, wt = run([a.wrapper, "-i", "hc.athinput", "-d", d0, "-t", "00:50:00", "time/nlim=2"],
                 d0, "athena", env)
    res["first"] = {"status": rc, "wall_s": round(wt, 1)}
    r0 = newest_rst(d0)
    res["first"]["restart"] = os.path.relpath(r0, out) if r0 else None
    if not r0:
        json.dump(res, open(os.path.join(out, "summary.json"), "w"), indent=1)
        print("no restart file from the first run")
        return 1

    def cont(name, src_rst, extra, nlim):
        d = os.path.join(out, name)
        os.makedirs(os.path.join(d, "rst"), exist_ok=True)
        with open(os.path.join(d, "add.athinput"), "w") as fp:
            fp.write("<fastflow>\ndiagnostics = true\n")
        own = os.path.join(d, "rst", os.path.basename(src_rst))
        shutil.copy2(src_rst, own)
        cmd = [a.wrapper, "-r", own, "-d", d, "-t", "00:50:00"] + extra + ["time/nlim=%d" % nlim]
        rc, wt = run(cmd, d, "athena", env)
        sf = sorted(glob.glob(os.path.join(d, "*horizon_status*")))
        recs = records(sf[0]) if sf else []
        log = open(os.path.join(d, "athena.log")).read()
        return d, {"cmd": cmd, "status": rc, "wall_s": round(wt, 1),
                   "status_files": [os.path.basename(s) for s in sf], "n_records": len(recs),
                   "status_records": recs[:6], "outputs": outputs(d),
                   "log_tail": log.splitlines()[-3:]}

    add = ["-i", "add.athinput"]
    db, res["b"] = cont("b", r0, add, 5)
    dc, res["c"] = cont("c", r0, [], 5)
    print("b", res["b"]["status"], res["b"]["n_records"], "c", res["c"]["status"], res["c"]["status_files"])

    # R25-2: byte comparison of every output but the status file
    cmp = {}
    names = sorted(set(res["b"]["outputs"]) | set(res["c"]["outputs"]))
    for n in names:
        if "horizon_status" in n:
            continue
        pb, pc = os.path.join(db, n), os.path.join(dc, n)
        if not (os.path.exists(pb) and os.path.exists(pc)):
            cmp[n] = "missing in " + ("c" if os.path.exists(pb) else "b")
        else:
            cmp[n] = "identical" if filecmp.cmp(pb, pc, shallow=False) else "DIFFERENT"
    res["compare_b_c"] = cmp

    # R25-3: b's restart carries the parameter; a second continuation with the same -i runs
    rb = newest_rst(db)
    blk = fastflow_block(rb) if rb else ""
    res["b_last_restart"] = os.path.relpath(rb, out) if rb else None
    res["b_restart_has_diagnostics"] = any(l.split("=")[0].strip() == "diagnostics"
                                           for l in blk.splitlines())
    res["b_restart_diag_line"] = [l for l in blk.splitlines() if l.strip().startswith("diagnostics")]
    d2, res["b2"] = cont("b2", rb, add, 6) if rb else (None, {"status": -1, "n_records": 0})

    chk = {
        "R25-1": res["b"]["status"] == 0 and res["b"]["n_records"] >= 1
                 and res["c"]["status"] == 0 and not res["c"]["status_files"],
        "R25-2": bool(cmp) and all(v == "identical" for v in cmp.values()),
        "R25-3": res["b_restart_has_diagnostics"] and res["b2"]["status"] == 0
                 and res["b2"]["n_records"] >= 1,
    }
    res["checks"] = chk
    res["verdict"] = "PASS" if all(chk.values()) else "FAIL"
    json.dump(res, open(os.path.join(out, "summary.json"), "w"), indent=1)
    for k, v in chk.items():
        print(k, "HOLDS" if v else "FAILS")
    for n, v in cmp.items():
        print("  ", n, v)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle
    figstyle.use_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.4, 2.8), gridspec_kw={"width_ratios": [1, 1.3]})
    labels = ["b: -r rst -i add", "c: -r rst (control)", "b2: -r b's rst -i add"]
    recs = [res[c]["n_records"] for c in ("b", "c", "b2")]
    sts = [res[c]["status"] for c in ("b", "c", "b2")]
    cols = [figstyle.PAL["red"] if s else figstyle.PAL["blue"] for s in sts]
    ax1.barh(labels, recs, color=cols)
    for i, (n, s) in enumerate(zip(recs, sts)):
        ax1.text(max(n, 0) + 0.05, i, "exit %d, %d rec." % (s, n), va="center", fontsize=7)
    ax1.set_xlabel("records in horizon_status_0")
    ax1.set_xlim(0, max(recs + [1]) + 3)
    ax1.set_title("status file (red: exit not 0)", fontsize=8)
    ns = list(cmp.keys())
    ok = [1 if cmp[n] == "identical" else 0 for n in ns]
    ax2.barh(ns, [1] * len(ns), color=[figstyle.PAL["blue"] if o else figstyle.PAL["red"] for o in ok])
    for i, n in enumerate(ns):
        ax2.text(0.03, i, cmp[n], va="center", fontsize=7, color="white")
    ax2.set_xticks([])
    ax2.tick_params(axis="y", labelsize=6)
    ax2.set_title("b against c, byte for byte (blue: identical)", fontsize=8)
    fig.suptitle("core-v0.5 processor build through the chain wrapper: verdict %s" % res["verdict"],
                 fontsize=9)
    fig.tight_layout()
    figstyle.save(fig, os.path.join(out, "fig_diag_restart"))
    print("DIAG RESTART", res["verdict"])
    return 0 if res["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
