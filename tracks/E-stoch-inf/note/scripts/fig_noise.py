"""Figure: validation of the noise generator of the AthenaK scalar-field module against the
track's contract (tests A1-A15 of the noise specification), for the three noise schemes.

Reads val_frozen/, val_markov_heaviside/ and val_markov_tanh/validation.json of run
E-20261115-140502-2957846, the lead's validation of the outputs of run
E-20261115-135523-a32c3a6 (core's processor executable of the scalar-field branch at
836ac86, scaled base case N = 32); checksums verified against the manifest's
sha256sums.txt. Each test is shown as its statistic divided by its pass threshold (a test
passes at or left of 1): deviations over their tolerance, |z| over the z threshold, the
p threshold over the p value; for A2 and A3 the largest of the sub-tests. Results that are
exactly zero (bit-identical fields) are drawn at the left edge with a left-pointing marker.
A0 (format) and A9 (not applicable to these outputs) are left out; A8 of the Markov-Heaviside
scheme is not applicable (no common active modes between outputs).
Open diamonds: the Markov-tanh scheme of the release executable (core-v0.3, same scaled
case, tests A0-A10), validated against a reference that forms the window increment without
cancellation (val_cf/validation.json of run E-20261115-172423-5234cce, the analysis helper's
run; checksums verified against its sha256sums.txt).
"""
import os
import re
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
import czstyle as cz  # noqa: E402

RUN = "E-20261115-140502-2957846"
RELEASE_RUN = "E-20261115-172423-5234cce"
SCHEMES = (("val_frozen", "frozen, tanh window", cz.PAL["blue"], "o"),
           ("val_markov_heaviside", "Markov, step window", cz.PAL["green"], "s"),
           ("val_markov_tanh", "Markov, tanh window", cz.PAL["red"], "D"))
ROWS = (("A1", 0, "reconstruction from keys"), ("A2", 0, "spectrum per shell"),
        ("A3", 0, "Gaussian amplitudes"), ("A4", 0, "correlation function"),
        ("A5", 0, "zero mean"), ("A6", 0, "shared amplitudes"),
        ("A7", 0, "independent components"), ("A8", 0, "between outputs"),
        ("A10", 0, "band limit"), ("A11", 0, "MeshBlocks 1 vs 8"),
        ("A11", 1, "MeshBlocks 1 vs 64"), ("A12", 0, "restart"),
        ("A13", 0, "resolution N vs 2N"), ("A15", 0, "seeds independent"))
FLOOR = 1e-8


def nums(s):
    return [float(x) for x in re.findall(r"(?<![\w.])(\d+(?:\.\d+)?(?:e-?\d+)?)", s)]


def ratio(t):
    """Statistic over pass threshold (<= 1 passes); 0 for exact results; None if n/a."""
    if t["passed"] is None:
        return None
    v, c = t["value"], t["criterion"]
    tid = t["id"]
    if c.startswith("bit-identical"):
        return float(v) / 1.0          # 0 when bit-identical
    if tid == "A2":
        p, z = nums(c.split("|z_pool|")[0])[-1], nums(c.split("<=")[-1])[0]
        return max(p / max(v["min_p_bonferroni"], 1e-300), abs(v["max_abs_zpool"]) / z)
    if tid == "A3":
        p, z = nums(c.split("(")[0])[-1], nums(c.split("|z4| <=")[-1])[0]
        return max(p / max(v["p_mod"], 1e-300), p / max(v["p_arg"], 1e-300), abs(v["z4"]) / z)
    if tid == "A4":
        return nums(c)[-1] / max(float(v), 1e-300)
    thr = nums(c.split("<=")[1])[0]
    return abs(float(v)) / thr


def main():
    out = C.out_dir(C.FIGDIR)
    os.makedirs(out, exist_ok=True)
    cz.use_style()
    fig = plt.figure(figsize=(3.4, 3.9))
    ax = cz.inch_axes(fig, 1.55, 0.48, 1.72, 3.05)
    nrow = len(ROWS)
    for j, (sub, lab, col, mk) in enumerate(SCHEMES):
        tests = C.load_json(RUN, f"{sub}/validation.json")
        seen = {}
        by = {}
        for t in tests:
            seen[t["id"]] = seen.get(t["id"], -1) + 1
            by[(t["id"], seen[t["id"]])] = t
        xs, ys, xe, ye = [], [], [], []
        for i, (tid, rep, _) in enumerate(ROWS):
            t = by.get((tid, rep))
            if t is None:
                continue
            r = ratio(t)
            if r is None:
                continue
            y = nrow - 1 - i + (j - 1.5) * 0.18
            if r == 0.0:
                xe.append(FLOOR * 1.6)
                ye.append(y)
            else:
                xs.append(r)
                ys.append(y)
        ax.plot(xs, ys, mk, color=col, ms=3.6, ls="none", label=lab)
        ax.plot(xe, ye, "<", color=col, ms=3.6, ls="none")
    # release executable, Markov tanh, cancellation-free reference
    tests = C.load_json(RELEASE_RUN, "val_cf/validation.json")
    xs, ys, xe, ye = [], [], [], []
    for i, (tid, rep, _) in enumerate(ROWS):
        t = next((t for t in tests if t["id"] == tid), None) if rep == 0 else None
        if t is None:
            continue
        r = ratio(t)
        if r is None:
            continue
        if r == 0.0:
            xe.append(FLOOR * 1.6)
            ye.append(nrow - 1 - i + 0.27)
        else:
            xs.append(r)
            ys.append(nrow - 1 - i + 0.27)
    ax.plot(xs, ys, "D", mfc="none", color=cz.PAL["red"], ms=3.6, ls="none",
            label="Markov, tanh, release")
    ax.plot(xe, ye, "<", mfc="none", color=cz.PAL["red"], ms=3.6, ls="none")
    ax.axvline(1.0, **cz.GUIDE)
    ax.set_xscale("log")
    ax.set_xlim(FLOOR, 1e2)
    ax.set_ylim(-0.7, nrow - 0.3)
    ax.set_yticks(range(nrow))
    ax.set_yticklabels([f"{tid} {name}" for tid, _, name in ROWS][::-1], fontsize=7)
    ax.tick_params(axis="y", which="minor", left=False, right=False)
    ax.set_xticks([1e-8, 1e-4, 1e0])
    ax.xaxis.set_minor_locator(matplotlib.ticker.LogLocator(base=10.0, subs=(1.0,), numticks=20))
    ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.set_xlabel("statistic / pass threshold")
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.32, 1.13), fontsize=6.5, ncol=2,
              handletextpad=0.2, columnspacing=0.6)
    cz.save(fig, os.path.join(out, "fig_noise"))


if __name__ == "__main__":
    main()
