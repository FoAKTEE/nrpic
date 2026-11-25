#!/usr/bin/env python3
"""Does the final serial build (step limit and SIGTERM handler) reproduce, with the step
limit ON, the build the tests T0 to T6 of the step limit ran (source 476fe0c)?

    python final_build_check.py --old ATHENA_476fe0c --new ATHENA_FINAL --out DIR

Runs problems/tests/z4c_step_limit.athinput (dt_gauge = 0.9, 300 steps; the limit sets
the step) with both and compares every output file byte for byte; the lines of the step
limit in the two logs must agree as well.  Writes DIR/final_build_check.json and a
figure of the two histories; exit status 0 if identical.
"""
import argparse
import filecmp
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DECK = os.path.join(REPO, "problems", "tests", "z4c_step_limit.athinput")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--old", required=True)
    ap.add_argument("--new", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    res = {}
    for lab, exe in (("old", a.old), ("new", a.new)):
        d = os.path.join(out, lab)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "athena.log"), "w") as f:
            rc = subprocess.run([os.path.abspath(exe), "-i", DECK, "-d", d], cwd=d, stdout=f,
                                stderr=subprocess.STDOUT).returncode
        res[lab] = {"exe": os.path.abspath(exe), "rc": rc}
    do, dn = os.path.join(out, "old"), os.path.join(out, "new")
    files = sorted(os.path.relpath(os.path.join(r, x), do) for r, _, xs in os.walk(do)
                   for x in xs if x != "athena.log")
    diff = [x for x in files if not os.path.exists(os.path.join(dn, x))
            or not filecmp.cmp(os.path.join(do, x), os.path.join(dn, x), shallow=False)]
    lim = {lab: [ln for ln in open(os.path.join(out, lab, "athena.log"), errors="replace")
                 if "Z4c step limit" in ln] for lab in ("old", "new")}
    res.update(files=len(files), bytes=sum(os.path.getsize(os.path.join(do, x)) for x in files),
               differing=diff, step_limit_lines=lim["new"],
               step_limit_lines_identical=(lim["old"] == lim["new"] and len(lim["new"]) > 0))
    res["verdict"] = "PASS" if (not diff and res["step_limit_lines_identical"]
                                and res["old"]["rc"] == 0 and res["new"]["rc"] == 0) else "FAIL"
    with open(os.path.join(out, "final_build_check.json"), "w") as f:
        json.dump(res, f, indent=1)
        f.write("\n")

    sys.path.insert(0, os.path.join(REPO, "python"))
    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    import numpy as np
    fs.use_style()

    def hst(d):
        rows = [[float(v) for v in ln.split()] for ln in open(os.path.join(d, "flat.z4c.user.hst"))
                if not ln.startswith("#") and ln.strip()]
        return np.array(rows)
    ho, hn = hst(do), hst(dn)
    fig, ax = plt.subplots(1, 2, figsize=(7.4, 2.9))
    fig.subplots_adjust(left=0.11, right=0.98, bottom=0.17, top=0.9, wspace=0.32)
    ax[0].plot(ho[:, 0], ho[:, 1] / 0.3125, "-", color=fs.SERIES[0], lw=1.8, label="source 476fe0c")
    ax[0].plot(hn[:, 0], hn[:, 1] / 0.3125, "--", color=fs.SERIES[1], lw=1.0, label="final source")
    ax[0].set_xlabel("t"); ax[0].set_ylabel("step in cells"); ax[0].legend(frameon=False, fontsize=7)
    ax[1].semilogy(ho[:, 0], np.abs(ho[:, 2]) + 1e-300, "-", color=fs.SERIES[0], lw=1.8)
    ax[1].semilogy(hn[:, 0], np.abs(hn[:, 2]) + 1e-300, "--", color=fs.SERIES[1], lw=1.0)
    ax[1].set_xlabel("t"); ax[1].set_ylabel("history column 3 (C-norm2)")
    ax[1].set_title("%d files, %d bytes: %d differ" % (res["files"], res["bytes"], len(diff)),
                    fontsize=8)
    fs.save(fig, os.path.join(out, "fig_final_build_check"))
    print(json.dumps({k: v for k, v in res.items() if k != "step_limit_lines"}, indent=1))
    for ln in res["step_limit_lines"]:
        print(ln.rstrip()[:200])
    print("CHECK", res["verdict"])
    return 0 if res["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
