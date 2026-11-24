#!/usr/bin/env python3
"""Review check R7 (journal entry 9): how far the local Z = 9 Pi^2/K^2 of level 2 is
from zero in a run.  Reads Pi and K of every dump of the given run directories (one
MeshBlock; only the two arrays are read) and records min, max and rms of Pi/<Pi> - 1 and
of Z/<Z> - 1.

    pi_range.py --out DIR NAME=RUNDIR [NAME=RUNDIR ...]

Writes DIR/pi_range.json and DIR/fig_pi_range.png."""
import argparse
import glob
import json
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import nl2                     # noqa: E402
import numpy as np             # noqa: E402

NAMES1 = ["phi", "Pi", "chi", "K", "alpha", "H", "Mx", "My", "Mz", "E"]


def read_two(fname):
    with open(fname, "rb") as fp:
        magic = fp.read(8)
        nmb, nx1, nx2, nx3, nvar, cycle, nnoise = struct.unpack("<7q", fp.read(56))
        (time,) = struct.unpack("<d", fp.read(8))
        if magic == b"NRSFDMP1":
            names = NAMES1
        elif magic == b"NRSFDMP2":
            names = [fp.read(16).rstrip(b"\0").decode() for _ in range(nvar)]
        else:
            raise ValueError(fname + ": bad magic")
        if nmb != 1:
            raise ValueError(fname + ": more than one MeshBlock")
        fp.seek(32 + 48, 1)
        base = fp.tell()
        n = nx1*nx2*nx3
        out = {}
        for v in ("Pi", "K"):
            fp.seek(base + names.index(v)*n*8)
            out[v] = np.fromfile(fp, dtype="<f8", count=n)
    return time, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--replot", help="pi_range.json of an earlier call: figure only")
    ap.add_argument("runs", nargs="*")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = json.load(open(a.replot)) if a.replot else {}
    for item in ([] if a.replot else a.runs):
        name, rd = item.split("=", 1)
        rows = []
        for f in sorted(glob.glob(os.path.join(rd, "*.sf.?????.dump"))):
            t, d = read_two(f)
            pi, kk = d["Pi"], d["K"]
            z = 9.0*pi*pi/(kk*kk)
            rp = pi/pi.mean() - 1.0
            rz = z/z.mean() - 1.0
            rows.append(dict(time=t, pi_mean=float(pi.mean()), pi_min_rel=float(rp.min()),
                             pi_max_rel=float(rp.max()), pi_rms_rel=float(rp.std()),
                             k_rms_rel=float((kk/kk.mean() - 1.0).std()),
                             z_min_rel=float(rz.min()), z_max_rel=float(rz.max()),
                             z_rms_rel=float(rz.std())))
        res[name] = dict(run=os.path.abspath(rd), dumps=rows)
    nl2.dump_json(res, os.path.join(a.out, "pi_range.json"))
    for name, r in res.items():
        w = max(r["dumps"], key=lambda q: max(abs(q["pi_min_rel"]), abs(q["pi_max_rel"])))
        print(name, "dumps", len(r["dumps"]), "largest |Pi/<Pi> - 1|",
              max(abs(w["pi_min_rel"]), abs(w["pi_max_rel"])), "at t =", w["time"],
              "rms there", w["pi_rms_rel"], "K rms there", w["k_rms_rel"])

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    fig, ax = plt.subplots(1, len(res), figsize=(fs.FULL_WIDTH, 2.8), squeeze=False)
    fig.subplots_adjust(left=0.09, right=0.99, bottom=0.17, top=0.9, wspace=0.3)
    for a_, (name, r) in zip(ax[0], res.items()):
        t = [q["time"] for q in r["dumps"]]
        a_.semilogy(t, [max(abs(q["pi_min_rel"]), abs(q["pi_max_rel"]), 1e-18)
                        for q in r["dumps"]], "o-", ms=3, color=fs.PAL["orange"],
                    label=r"max$_x|\Pi/\langle\Pi\rangle-1|$")
        a_.semilogy(t, [max(q["pi_rms_rel"], 1e-18) for q in r["dumps"]], "s-", ms=3,
                    color=fs.PAL["blue"], label=r"rms of $\Pi/\langle\Pi\rangle-1$")
        a_.semilogy(t, [max(q["k_rms_rel"], 1e-18) for q in r["dumps"]], "^-", ms=3,
                    color=fs.PAL["green"], label=r"rms of $K/\langle K\rangle-1$")
        a_.axhline(1.0, color="0.4", lw=0.8, ls="--")
        a_.set_ylim(1e-13, 1e3)
        a_.set_xlabel("$t$ (1/H$_*$)")
        a_.set_ylabel("relative to the box mean")
        a_.set_title(name, fontsize=8)
        a_.legend(fontsize=6, loc="upper left", ncol=3)
    fig.savefig(os.path.join(a.out, "fig_pi_range.png"), dpi=200)


if __name__ == "__main__":
    main()
