#!/usr/bin/env python3
"""Package step-limit, test T6b: would the step limit of the gauge sectors, switched on
for everybody, change released results?

The set-ups of the release regression (analysis/release/regress_v04.py) that evolve Z4c
are run twice with the same executable: as they are, and with <z4c> dt_gauge = 1.0 (the
bound itself, no margin).  The histories are compared byte for byte; the log of the
second run gives the bounds at the start in cells and says whether the limit ever set
the step.

  python survey_default.py --exe ATHENA --out DIR [--cores 3]
"""
import argparse
import concurrent.futures as cf
import filecmp
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "release"))
import regress_v04 as rg  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cores", type=int, default=3)
    a = ap.parse_args()
    a.exe = os.path.abspath(a.exe)
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    ic2 = os.path.join(out, "ic")
    rg.make_ic(ic2)
    spec = rg.cases(ic2)
    names = []
    for n, (inp, _, args) in spec.items():
        txt = open(inp).read()
        dyn = re.search(r"^evolution\s*=\s*dynamic", txt, re.M)
        if "<z4c>" in txt and dyn:
            names.append(n)
    jobs = []
    for n in names:
        inp, links, args = spec[n]
        jobs.append((n, "plain", (inp, links, args)))
        # AthenaK takes on the command line only parameters the input declares, and the
        # released decks do not declare dt_gauge (the first call of this test, run
        # core-20261125-001824-536b23f, stopped there): a copy of the deck with the
        # option as the first line of its <z4c> block
        txt = open(inp).read()
        assert len(re.findall(r"^<z4c>[^\n]*$", txt, re.M)) == 1
        txt = re.sub(r"^(<z4c>[^\n]*)$", r"\1\ndt_gauge = 1.0", txt, count=1, flags=re.M)
        os.makedirs(os.path.join(out, n), exist_ok=True)
        inp_g = os.path.join(out, n, os.path.basename(inp))
        with open(inp_g, "w") as f:
            f.write(txt)
        jobs.append((n, "gauge", (inp_g, links, args)))
    codes = {}
    with cf.ThreadPoolExecutor(max_workers=a.cores) as pool:
        futs = {pool.submit(rg.run, a.exe, os.path.join(out, n, lab), sp): (n, lab)
                for n, lab, sp in jobs}
        for fut in cf.as_completed(futs):
            codes[futs[fut]] = fut.result()
    res = {"exe": a.exe, "sha256": rg.sha256(a.exe), "cases": {}}
    for n in names:
        dp, dg = os.path.join(out, n, "plain"), os.path.join(out, n, "gauge")
        hst = sorted(os.path.relpath(p, dp)
                     for p in glob.glob(os.path.join(dp, "**", "*.hst"), recursive=True))
        same = [h for h in hst if os.path.exists(os.path.join(dg, h))
                and filecmp.cmp(os.path.join(dp, h), os.path.join(dg, h), shallow=False)]
        log = open(os.path.join(dg, "athena.log")).read()
        logp = open(os.path.join(dp, "athena.log")).read()
        m = re.search(r"Gamma-driver shift ([-+.0-9eE]+), lapse ([-+.0-9eE]+), "
                      r"light ([-+.0-9eE]+); cfl_number ([-+.0-9eE]+)", log)
        res["cases"][n] = {
            "input": os.path.relpath(spec[n][0], REPO), "exit": [codes[(n, "plain")][0],
                                                               codes[(n, "gauge")][0]],
            "histories": len(hst), "histories_identical": len(same),
            "differ": [h for h in hst if h not in same],
            "bounds_cells_shift_lapse_light": [float(m.group(i)) for i in (1, 2, 3)]
            if m else None,
            "cfl_number": float(m.group(4)) if m else None,
            "limit_set_the_step": len(re.findall(r"set by dt_gauge", log)),
            "warning_without_option": bool(re.search(r"WARNING \(Z4c step limit\)", logp)),
        }
    with open(os.path.join(out, "survey_default.json"), "w") as f:
        json.dump(res, f, indent=1)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    sys.path.insert(0, os.path.join(REPO, "python", "nrpic"))
    import figstyle as fs
    fs.use_style()
    fig, ax = plt.subplots(figsize=(fs.COLUMN_WIDTH * 1.3, 3.0))
    fig.subplots_adjust(left=0.16, right=0.97, bottom=0.16, top=0.95)
    x = np.arange(len(names))
    lab = ("Gamma-driver shift", "lapse", "light")
    col = (fs.PAL["red"], fs.PAL["blue"], fs.PAL["green"])
    for i in range(3):
        y = [min(res["cases"][n]["bounds_cells_shift_lapse_light"][i], 3.0)
             if res["cases"][n]["bounds_cells_shift_lapse_light"] else np.nan
             for n in names]
        ax.bar(x + 0.25 * (i - 1), y, 0.25, color=col[i], label="bound: " + lab[i])
    ax.plot(x, [res["cases"][n]["cfl_number"] or np.nan for n in names], ls="none",
            marker="_", ms=30, mew=2.5, color="k", label="cfl_number of the set-up")
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.set_ylabel("step in cells (bars cut at 3)")
    ax.legend(fontsize=7, loc="upper right")
    fig.savefig(os.path.join(out, "fig_survey_default.png"), dpi=150)
    print(json.dumps(res["cases"], indent=1))


if __name__ == "__main__":
    main()
