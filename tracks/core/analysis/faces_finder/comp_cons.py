#!/usr/bin/env python3
"""Is the compensation pass of the deposit conservative on a refined mesh?  (Item 0b of
tracks/core/NEXT_SOURCE.md; prediction C1 of tracks/core/JOURNAL-faces-finder.md.)

    comp_cons.py --base ATHENA --new ATHENA --out DIR [--tlim 1.0]

Deck: problems/tests/deposit_smr.athinput (flat space, 10^4 particles with random
positions and momenta drifting across three levels of static refinement: a cube inside a
cube, so that level faces, edges and corners are all met), with the cloud and the
compensation of each case added to <particles>, in a periodic box (the case with the
prefix out_ keeps the outflow faces of the deck).  The history compares the integrals of
the deposited E and S_i over the mesh (columns 9 to 12) with the particle sums (5 to 8)
at every cycle.  Cases with the prefix uni_ run on the root mesh alone (no refinement).

Writes DIR/<case>/{base,new}/, DIR/summary.json and DIR/fig_comp_cons.{pdf,png}; exit 0
if the checks hold.
"""
import argparse
import json
import os
import re
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))
IC = "/data/haiyangw/nrpic/scratch/core/regress/ic/random.nrp"

C6 = "0.1666666666666667"
CASES = {
    # name: lines added to <particles>
    "none_pcs": ["deposit_shape = pcs"],
    "pcs_c2": ["deposit_shape = pcs", "deposit_comp_c = " + C6,
               "deposit_comp_c2 = 0.4666666666666667"],
    "pcs_c2_lim": ["deposit_shape = pcs", "deposit_comp_c = " + C6,
                   "deposit_comp_c2 = 0.4666666666666667", "deposit_comp_limit = " + C6],
    "tsc_plain": ["deposit_shape = tsc", "deposit_comp_c = 0.125"],
    "cic_plain": ["deposit_shape = cic", "deposit_comp_c = 0.0833333333333333"],
    "cic_fs": ["deposit_shape = cic", "deposit_fine_shape = true"],
    "out_pcs_c2": ["deposit_shape = pcs", "deposit_comp_c = " + C6,
                   "deposit_comp_c2 = 0.4666666666666667"],
    "uni_pcs_c2": ["deposit_shape = pcs", "deposit_comp_c = " + C6,
                   "deposit_comp_c2 = 0.4666666666666667"],
    "uni_cic_plain": ["deposit_shape = cic", "deposit_comp_c = 0.0833333333333333"],
}


def deck_text(name, tlim):
    txt = open(os.path.join(REPO, "problems", "tests", "deposit_smr.athinput")).read()
    txt = re.sub(r"(?m)^tlim\s*=.*$", "tlim       = %g" % tlim, txt)
    add = "\n".join(CASES[name])
    txt, n = re.subn(r"(?m)^(deposit\s+=\s+true.*)$", r"\1\n" + add, txt, count=1)
    assert n == 1
    if name.startswith("uni_"):
        i = txt.index("<mesh_refinement>")
        j = txt.index("<time>")
        txt = txt[:i] + txt[j:]
    if not name.startswith("out_"):
        # periodic box: the pass has a flux through an outflow face of the mesh when
        # matter lies in the cells next to it, which is not what is tested here
        txt = txt.replace("= outflow", "= periodic")
    return txt


def start(exe, d, txt):
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "dep.athinput"), "w") as f:
        f.write(txt)
    lnk = os.path.join(d, "random.nrp")
    if not os.path.exists(lnk):
        os.symlink(IC, lnk)
    log = open(os.path.join(d, "athena.log"), "w")
    return subprocess.Popen([exe, "-i", "dep.athinput"], cwd=d, stdout=log,
                            stderr=subprocess.STDOUT), log


def read_hst(d):
    a = np.loadtxt(os.path.join(d, "dep.nrpic.hst"), comments="#", ndmin=2)
    mw = a[:, 4]
    errs = np.abs(a[:, 8:12] - a[:, 4:8]) / np.abs(mw)[:, None]
    return a[:, 1], errs, a


def same_bytes(a, b):
    with open(a, "rb") as fa, open(b, "rb") as fb:
        return fa.read() == fb.read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--new", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tlim", type=float, default=1.0)
    ap.add_argument("--cases", default="all")
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    names = list(CASES) if a.cases == "all" else a.cases.split(",")
    res = {}
    for name in names:
        txt = deck_text(name, a.tlim)
        r = {}
        # the two builds side by side (two cores)
        procs = {tag: start(exe, os.path.join(out, name, tag), txt)
                 for tag, exe in (("base", a.base), ("new", a.new))}
        for tag in ("base", "new"):
            d = os.path.join(out, name, tag)
            st = procs[tag][0].wait()
            procs[tag][1].close()
            r[tag] = {"status": st}
            if st == 0:
                cyc, errs, raw = read_hst(d)
                r[tag].update(records=int(len(cyc)), max_rel_err_E=float(errs[:, 0].max()),
                              max_err_S_over_mW=float(errs[:, 1:].max()),
                              E_min=float(raw[:, 31].min()), E_max=float(raw[:, 30].max()))
        if r["base"]["status"] == 0 and r["new"]["status"] == 0:
            r["hst_identical"] = same_bytes(os.path.join(out, name, "base", "dep.nrpic.hst"),
                                            os.path.join(out, name, "new", "dep.nrpic.hst"))
            _, _, rb = read_hst(os.path.join(out, name, "base"))
            _, _, rn = read_hst(os.path.join(out, name, "new"))
            if rb.shape == rn.shape:
                # largest change of the largest energy density (a field value) between
                # the two builds, relative
                r["max_rel_change_E_max"] = float(np.max(np.abs(rb[:, 30] - rn[:, 30]) /
                                                         np.abs(rb[:, 30])))
        res[name] = r
        print(name, json.dumps(r), flush=True)

    chk = {}
    ok_all = all(r[t]["status"] == 0 for r in res.values() for t in ("base", "new"))
    chk["status"] = ok_all
    comp = [n for n in names if not n.startswith("uni_") and not n.startswith("out_")
            and n not in ("none_pcs", "cic_fs")]
    chk["C1a_new_conserves"] = all(res[n]["new"].get("max_rel_err_E", 1) < 1e-12 and
                                   res[n]["new"].get("max_err_S_over_mW", 1) < 1e-12
                                   for n in comp)
    chk["C1b_base_does_not"] = all(res[n]["base"].get("max_rel_err_E", 0) > 1e-7
                                   for n in comp)
    chk["C1c_untouched_identical"] = all(res[n].get("hst_identical", False) for n in names
                                         if n.startswith("uni_") or n == "none_pcs")
    summ = {"cases": res, "checks": chk, "verdict": "PASS" if all(chk.values()) else "FAIL"}
    json.dump(summ, open(os.path.join(out, "summary.json"), "w"), indent=1)
    for k, v in chk.items():
        print(k, "HOLDS" if v else "FAILS")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle
    figstyle.use_style()
    shown = [n for n in names if not n.startswith("uni_")]
    cols = figstyle.series_colors(max(len(shown), 2))
    fig, axs = plt.subplots(1, 2, figsize=(9.0, 3.4), sharey=True)
    for ax, tag in zip(axs, ("base", "new")):
        for c, n in zip(cols, shown):
            if res[n][tag]["status"] != 0:
                continue
            cyc, errs, _ = read_hst(os.path.join(out, n, tag))
            ax.semilogy(cyc, np.maximum(errs[:, 0], 1e-18), "o-", ms=2.5, lw=0.9, color=c,
                        label=n)
        ax.set_xlabel("cycle")
        ax.set_title({"base": "release core-v0.8", "new": "this branch"}[tag], fontsize=9)
        ax.axhline(1e-12, color="0.6", lw=0.6, ls="--")
    axs[0].set_ylabel(r"$|\int E\,dV - \sum m W| / \sum m W$")
    axs[1].legend(fontsize=7, loc="center right")
    fig.tight_layout()
    figstyle.save(fig, os.path.join(out, "fig_comp_cons"))
    print("COMP CONS", summ["verdict"])
    return 0 if summ["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
