#!/usr/bin/env python3
"""Compare the dumps of v6_athenak.sh: bit identity across MeshBlock layouts and restart,
the size of the momentum constraint against the negative control, and the timings.

Reader written here from the format at athenak/src/scalar_field/scalar_field_io.cpp:12-17
(NRSFDMP1: int64 nmb, nx1, nx2, nx3, nvar, cycle, nnoise; double time; per MeshBlock int64
level, lx1, lx2, lx3; six doubles of the extent; nvar arrays (nvar = 10 + nnoise, io.cpp:244),
first index fastest). Variables: phi, Pi, chi, K, alpha, H, M_x, M_y, M_z, E, noise fields.
"""
import glob
import json
import os
import re
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402,F401

NAMES = ["phi", "Pi", "chi", "K", "alpha", "H", "Mx", "My", "Mz", "E"]


def read_dump(path):
    with open(path, "rb") as fh:
        buf = fh.read()
    assert buf[:8] == b"NRSFDMP1", path
    h = np.frombuffer(buf, np.int64, 7, 8)
    nmb, nx1, nx2, nx3, nvar, cycle, nnoise = (int(x) for x in h)
    time = np.frombuffer(buf, np.float64, 1, 64)[0]
    off = 72
    nv = nvar                       # nvar counts the noise fields (io.cpp:244)
    blocks = []
    for _ in range(nmb):
        loc = np.frombuffer(buf, np.int64, 4, off)
        off += 32 + 48
        data = np.frombuffer(buf, np.float64, nv * nx1 * nx2 * nx3, off).reshape(nv, nx3, nx2, nx1)
        off += 8 * nv * nx1 * nx2 * nx3
        blocks.append((loc, data))
    assert off == len(buf), (off, len(buf))
    NX = (1 + max(b[0][1] for b in blocks)) * nx1
    NY = (1 + max(b[0][2] for b in blocks)) * nx2
    NZ = (1 + max(b[0][3] for b in blocks)) * nx3
    g = np.zeros((nv, NZ, NY, NX))
    for loc, d in blocks:
        _, lx1, lx2, lx3 = (int(x) for x in loc)
        g[:, lx3 * nx3:(lx3 + 1) * nx3, lx2 * nx2:(lx2 + 1) * nx2, lx1 * nx1:(lx1 + 1) * nx1] = d
    return dict(cycle=cycle, time=time, nvar=nvar, nnoise=nnoise, f=g)


def dumps(run_dir):
    out = {}
    for p in sorted(glob.glob(os.path.join(run_dir, "*.sf.*.dump"))):
        d = read_dump(p)
        out[d["cycle"]] = d
    return out


def main():
    out = sys.argv[1]
    res = {}
    D = {n: dumps(os.path.join(out, n)) for n in ("B32", "B16", "B3216", "RST", "NEG", "CONT")}
    ref = D["B32"]
    res["cycles"] = sorted(ref)
    for n in ("B16", "B3216", "RST", "NEG", "CONT"):
        rows = {}
        for c, d in D[n].items():
            if c not in ref:
                continue
            a, b = ref[c]["f"], d["f"]
            same = bool(np.array_equal(a.view(np.uint64), b.view(np.uint64)))
            diff = np.max(np.abs(a - b), axis=(1, 2, 3))
            rows[str(c)] = dict(bit_identical=same, max_abs_diff=diff.tolist(),
                                time_equal=bool(ref[c]["time"] == d["time"]))
        res[n] = rows
    # constraint sizes: max |M| and max |H| per dump, normal, negative control, continuum
    def cmax(d, i):
        return float(np.max(np.abs(d["f"][i])))
    cons = {}
    for n in ("B16", "NEG", "CONT"):
        cons[n] = {str(c): dict(H=cmax(d, 5), M=max(cmax(d, 6), cmax(d, 7), cmax(d, 8)),
                                dK=float(np.max(np.abs(d["f"][3] - d["f"][3].mean()))),
                                dPi=float(np.max(np.abs(d["f"][1] - d["f"][1].mean()))))
                   for c, d in sorted(D[n].items())}
    res["constraints"] = cons
    # timings
    tim = {}
    for n in ("T0", "T64", "T225", "T225b8", "T0b8", "B32", "B16"):
        p = os.path.join(out, n, "athena.log")
        if os.path.exists(p):
            m = re.search(r"zone-cycles/cpu_second = ([0-9.eE+-]+)", open(p).read())
            tim[n] = float(m.group(1)) if m else None
    res["zcps"] = tim
    with open(os.path.join(out, "v6.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    for n in ("B16", "B3216", "RST", "NEG", "CONT"):
        print(n, {c: (r["bit_identical"], max(r["max_abs_diff"])) for c, r in res[n].items()})
    for n, v in cons.items():
        print("constraints", n, v)
    print("zone-cycles/s", tim)

    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(1, 3, figsize=(8.0, 2.9))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.17, top=0.88, wspace=0.42)
    cyc = sorted(int(c) for c in cons["B16"])
    for n, col in (("B16", fs.PAL["blue"]), ("NEG", fs.PAL["red"]), ("CONT", fs.PAL["yellow"])):
        ax[0].semilogy(cyc, [max(cons[n][str(c)]["M"], 1e-300) for c in cyc], "o-", color=col,
                       label={"B16": "kicks (stencil)", "NEG": "Pi sign flipped",
                              "CONT": "continuum projector"}[n])
        ax[1].semilogy(cyc, [max(cons[n][str(c)]["H"], 1e-300) for c in cyc], "o-", color=col)
    ax[0].set_title(r"max $|\mathcal{M}_i|$", fontsize=9)
    ax[1].set_title(r"max $|\mathcal{H}|$", fontsize=9)
    for x in ax[:2]:
        x.set_xlabel("cycle")
    ax[0].legend(fontsize=7)
    # bit identity: max abs difference against B32 at the last common dump (0 plotted at 1e-20)
    last = str(max(int(c) for c in res["B16"]))
    labels, vals = [], []
    for n in ("B16", "B3216", "RST", "NEG"):
        if last in res[n]:
            labels.append(n)
            vals.append(max(max(res[n][last]["max_abs_diff"]), 1e-20))
    ax[2].bar(range(len(vals)), vals, color=[fs.PAL["blue"]] * 3 + [fs.PAL["red"]])
    ax[2].set_yscale("log")
    ax[2].set_xticks(range(len(vals)))
    ax[2].set_xticklabels(labels, fontsize=8)
    ax[2].set_title("max |diff| vs B32, cycle %s (0 at 1e-20)" % last, fontsize=8)
    fig.savefig(os.path.join(out, "fig_v6.png"))

    fig, ax = plt.subplots(figsize=(4.0, 3.0))
    fig.subplots_adjust(left=0.2, right=0.96, bottom=0.17, top=0.9)
    names = [n for n in ("T0", "T64", "T225", "T0b8", "T225b8") if tim.get(n)]
    ax.bar(range(len(names)), [tim[n] for n in names], color=fs.PAL["blue"])
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names)
    ax.set_ylabel("zone-cycles / s (one core)")
    ax.set_title("processor timing, $32^3$, 12 cycles", fontsize=9)
    fig.savefig(os.path.join(out, "fig_v7_timing.png"))


if __name__ == "__main__":
    main()
