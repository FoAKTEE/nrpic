#!/usr/bin/env python3
"""Can <fastflow> diagnostics be switched on in a run continued from a restart file?
(decision 0042 item 4; Tracks D and F.)  Prediction F1 of tracks/core/JOURNAL.md
(2026-11-26T02:36Z).

    diag_restart.py --exe ATHENA --out DIR

Deck: problems/tests/by_horizon_coarse.athinput (one cycle, a horizon search after it)
with a restart output every cycle.  Then three continuations to cycle 2:
  a  -r rst fastflow/diagnostics=true          (command line)
  b  -r rst -i add.athinput                     (add.athinput: <fastflow> diagnostics = true)
  c  -r rst                                     (control)
Writes DIR/summary.json and DIR/fig_diag_restart.{pdf,png}; exit 0 if F1a-F1c hold.
"""
import argparse
import glob
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))


def run(cmd, d, name):
    with open(os.path.join(d, name + ".log"), "w") as log:
        return subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, cwd=d).returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    deck = open(os.path.join(REPO, "problems", "tests", "by_horizon_coarse.athinput")).read()
    deck += "\n<output2>\nfile_type = rst\ndcycle    = 1\n"
    d0 = os.path.join(out, "first")
    os.makedirs(d0, exist_ok=True)
    with open(os.path.join(d0, "hc.athinput"), "w") as fp:
        fp.write(deck)
    res = {"first": run([a.exe, "-i", "hc.athinput"], d0, "athena")}
    rst = sorted(glob.glob(os.path.join(d0, "rst", "*.rst")) + glob.glob(os.path.join(d0, "*.rst")))
    res["restart_files"] = [os.path.relpath(r, out) for r in rst]
    if not rst:
        print("no restart file")
        json.dump(res, open(os.path.join(out, "summary.json"), "w"), indent=1)
        return 1
    r = rst[0]
    cases = {"a": ["fastflow/diagnostics=true"], "b": ["-i", "add.athinput"], "c": []}
    for c, extra in cases.items():
        d = os.path.join(out, c)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "add.athinput"), "w") as fp:
            fp.write("<fastflow>\ndiagnostics = true\n")
        st = run([a.exe, "-r", r] + extra + ["time/nlim=2"], d, "athena")
        sf = glob.glob(os.path.join(d, "**", "*horizon_status*"), recursive=True)
        lines = open(sf[0]).read().splitlines() if sf else []
        log = open(os.path.join(d, "athena.log")).read()
        res[c] = {"status": st, "status_files": [os.path.relpath(s, out) for s in sf],
                  "status_lines": lines[:6], "n_records": sum(1 for l in lines if not l.startswith("#")),
                  "not_found_message": "on command line not found" in log}
        print(c, json.dumps(res[c]))
    chk = {
        "F1a": res["a"]["status"] != 0 and res["a"]["not_found_message"] and not res["a"]["status_files"],
        "F1b": res["b"]["status"] == 0 and res["b"]["n_records"] >= 1,
        "F1c": res["c"]["status"] == 0 and not res["c"]["status_files"],
    }
    res["checks"] = chk
    res["verdict"] = "PASS" if all(chk.values()) else "FAIL"
    json.dump(res, open(os.path.join(out, "summary.json"), "w"), indent=1)
    for k, v in chk.items():
        print(k, "HOLDS" if v else "FAILS")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle
    figstyle.use_style()
    fig, ax = plt.subplots(figsize=(5.2, 2.6))
    labels = ["a: command line", "b: -i add.athinput", "c: control"]
    recs = [res[c]["n_records"] for c in "abc"]
    sts = [res[c]["status"] for c in "abc"]
    cols = [figstyle.PAL["red"] if s else figstyle.PAL["blue"] for s in sts]
    ax.barh(labels, recs, color=cols)
    for i, (n, s) in enumerate(zip(recs, sts)):
        ax.text(max(n, 0) + 0.05, i, "exit %d, %d record(s)" % (s, n), va="center", fontsize=8)
    ax.set_xlabel("records in the horizon status file of the continued run")
    ax.set_xlim(0, max(recs + [1]) + 2)
    ax.set_title("<fastflow> diagnostics after a restart (red: run refused)", fontsize=9)
    fig.tight_layout()
    figstyle.save(fig, os.path.join(out, "fig_diag_restart"))
    print("DIAG RESTART", res["verdict"])
    return 0 if res["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
