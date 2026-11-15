#!/usr/bin/env python3
"""T0 of collide/TESTS.md on core's committed collision kernel (lead review of C-sidm).

    python3 tracks/C-sidm/review/t0_kernel.py COMMIT   (run through review/register.py)

Takes athenak/src/particles/nrpic_collide.hpp at COMMIT (git show), compiles t0_kernel.cpp
against it with three flag sets (-O0; -O2; -O3 -march=native -ffp-contract=fast), runs the
208 equal-mass cases of collide/REFERENCES/test_vectors.json (the one unequal-mass case is
outside an equal-mass kernel) and applies the pass criteria of TESTS.md T0: every component
of u_a', u_b' within 1e-13 max(1, |u_a|, |u_b|) of the 60-digit reference, and the pair's
four-momentum conserved to 4 eps of the pair energy (checked with 50-digit arithmetic on the
returned doubles). Also v_Mol against the reference. Output in $NRPIC_RUN_DIR: t0.json,
fig_t0_kernel.{pdf,png}.
"""
import json
import os
import subprocess
import sys

import mpmath as mp
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TRACK = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(TRACK, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "python"))
from nrpic import figstyle as fs   # noqa: E402
import matplotlib.pyplot as plt     # noqa: E402

OUT = os.environ["NRPIC_RUN_DIR"]
EPS = np.finfo(float).eps
mp.mp.dps = 50
FLAGS = {"O0": ["-O0"], "O2": ["-O2"], "O3native_fma": ["-O3", "-march=native", "-ffp-contract=fast"]}


def main(commit):
    hdr = subprocess.check_output(["git", "-C", ROOT, "show",
                                   f"{commit}:athenak/src/particles/nrpic_collide.hpp"])
    open(os.path.join(OUT, "nrpic_collide.hpp"), "wb").write(hdr)
    tv = json.load(open(os.path.join(TRACK, "collide", "REFERENCES", "test_vectors.json")))
    cases = [c for c in tv["cases"] if c["ma"] == c["mb"]]
    lines = [" ".join(c["ua"] + c["ub"] + c["nhat"]) for c in cases]
    inp = "\n".join(lines) + "\n"
    res = dict(commit=commit, n_cases=len(cases), n_skipped=len(tv["cases"]) - len(cases), flags={})
    errs = {}
    for name, fl in FLAGS.items():
        exe = os.path.join(OUT, f"t0_{name}")
        subprocess.check_call(["g++", "-std=c++17", *fl, "-I", OUT, "-o", exe,
                               os.path.join(HERE, "t0_kernel.cpp")])
        outp = subprocess.run([exe], input=inp, capture_output=True, text=True, check=True).stdout
        rows = [[float.fromhex(t) for t in ln.split()] for ln in outp.strip().splitlines()]
        assert len(rows) == len(cases)
        eu, ec, ev, fails = [], [], [], []
        for c, r in zip(cases, rows):
            ua = [float.fromhex(t) for t in c["ua"]]
            ub = [float.fromhex(t) for t in c["ub"]]
            scale = max(1.0, float(np.linalg.norm(ua)), float(np.linalg.norm(ub)))
            ref = list(c["ua_out"]) + list(c["ub_out"])
            e_u = max(abs(r[i] - ref[i]) for i in range(6)) / scale
            # conservation in 50 digits on the returned doubles
            W = lambda u: mp.sqrt(1 + sum(mp.mpf(x) ** 2 for x in u))
            Ein = W(ua) + W(ub)
            Eout = W(r[0:3]) + W(r[3:6])
            dP = max(abs(mp.mpf(r[i]) + mp.mpf(r[3 + i]) - mp.mpf(ua[i]) - mp.mpf(ub[i])) for i in range(3))
            e_c = float(max(dP, abs(Eout - Ein)) / Ein) / EPS
            e_v = abs(r[7] - c["vmol"]) / max(c["vmol"], 1e-300)
            eu.append(e_u); ec.append(e_c); ev.append(e_v)
            if not (e_u <= 1e-13 and e_c <= 4.0):
                fails.append(dict(label=c["label"], err_u=e_u, cons_eps=e_c))
        res["flags"][name] = dict(max_err_u=max(eu), median_err_u=float(np.median(eu)),
                                  max_cons_eps=max(ec), max_rel_vmol=max(ev),
                                  n_fail=len(fails), fails=fails[:10])
        errs[name] = (np.array(eu), np.array(ec), np.array(ev))
    res["pass"] = all(v["n_fail"] == 0 for v in res["flags"].values())
    json.dump(res, open(os.path.join(OUT, "t0.json"), "w"), indent=1)
    fs.use_style()
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.8))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.18, top=0.93, wspace=0.35)
    cols = [fs.PAL["blue"], fs.PAL["red"], fs.PAL["yellow"]]
    for (name, (eu, ec, ev)), col in zip(errs.items(), cols):
        bins = np.logspace(-19, -11, 41)
        ax[0].hist(np.maximum(eu, 1e-19), bins=bins, histtype="step", color=col, lw=1.5, label=name)
        ax[1].hist(np.maximum(ec, 1e-3), bins=np.logspace(-3, 1, 41), histtype="step", color=col, lw=1.5)
        ax[2].hist(np.maximum(ev, 1e-19), bins=bins, histtype="step", color=col, lw=1.5)
    ax[0].axvline(1e-13, **fs.GUIDE); ax[1].axvline(4.0, **fs.GUIDE)
    for a, lab in zip(ax, [r"$|u'-u'_{\rm ref}|/\max(1,|u|)$", r"four-momentum change / ($\epsilon\,E$)",
                           r"$|v_{\rm Mol}/v_{\rm ref}-1|$"]):
        a.set_xscale("log"); a.set_xlabel(lab)
    ax[0].set_ylabel("cases"); ax[0].legend(loc="upper left", fontsize=8)
    fs.save(fig, os.path.join(OUT, "fig_t0_kernel"))
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "fails"} for k, v in res["flags"].items()}, indent=1))
    print("PASS" if res["pass"] else "FAIL")
    return 0 if res["pass"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
