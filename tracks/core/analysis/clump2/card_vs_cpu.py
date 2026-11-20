#!/usr/bin/env python3
"""Tests G and G2 of tracks/core/JOURNAL-clump2.md: the card runs of TC and TE against the
processor executable of the same source.

G:  first record of cl.nrpic.hst and cl.z4c.user.hst of every card run against
    records.json of run_t0_records.py (the same inputs started on a processor).
G2: the histories of the card runs of TC against the processor runs of the same inputs
    (v0, v0.3 to 10 M; v0.3s as far as it got), at the common records.

    card_vs_cpu.py --tc RUN --te RUN --t0 RUN --early RUN [--out DIR]

Writes card_vs_cpu.json and fig_card_vs_cpu.{pdf,png} into --out.
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SCRATCH = "/data/haiyangw/nrpic/scratch/core"
sys.path.insert(0, os.path.join(WT, "python"))
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

TINY = 1e-12          # a quantity below this in both records is a round-off of zero
NORMS = ("C-norm2", "H-norm2", "M-norm2", "Mx-norm2", "My-norm2", "Mz-norm2")


def columns(header):
    """names of the columns from a header line '[1]=time [2]=...'"""
    return [w.split("=", 1)[1] for w in header.replace("#", " ").split() if "=" in w]


def first_record(path):
    with open(path) as f:
        head = [ln for ln in f if ln.startswith("#")]
    with open(path) as f:
        row = next(ln for ln in f if not ln.startswith("#") and ln.strip()).split()
    return columns(head[-1]), [float(x) for x in row]


def table(path):
    rows = [ln.split() for ln in open(path) if not ln.startswith("#") and ln.strip()]
    n = min(len(r) for r in rows)
    a = np.array([r[:n] for r in rows], dtype=float)
    _, idx = np.unique(a[::-1, 0], return_index=True)
    return a[::-1][idx]


def compare_t0(card_dir, rec):
    """per history file: the largest relative difference, where, and the columns that
    differ at all"""
    out = {}
    for kind in ("nrpic", "z4c.user"):
        path = glob.glob(os.path.join(card_dir, f"*.{kind}.hst"))[0]
        names, row = first_record(path)
        pnames, prow = columns(rec[kind]["header"]), rec[kind]["row"]
        n = min(len(row), len(prow))
        worst, where, differing, zeros = 0.0, None, [], []
        for k in range(n):
            a, b = row[k], prow[k]
            if a == b:
                continue
            if abs(a) < TINY and abs(b) < TINY:
                zeros.append(names[k])
                continue
            rel = abs(a - b) / max(abs(a), abs(b))
            differing.append([names[k], a, b, rel])
            if rel > worst:
                worst, where = rel, names[k]
        out[kind] = dict(columns_card=len(row), columns_cpu=len(prow),
                         same_names=bool(names[:n] == pnames[:n]),
                         max_rel=worst, max_rel_column=where, differing=differing,
                         zero_roundoff=zeros)
    return out


def compare_history(card_dir, cpu_dir):
    """differences card - processor at the records both runs hold"""
    hc = table(glob.glob(os.path.join(card_dir, "*.nrpic.hst"))[0])
    hp = table(glob.glob(os.path.join(cpu_dir, "*.nrpic.hst"))[0])
    zc = table(glob.glob(os.path.join(card_dir, "*.z4c.user.hst"))[0])
    zp = table(glob.glob(os.path.join(cpu_dir, "*.z4c.user.hst"))[0])
    tend = min(hc[-1, 0], hp[-1, 0])
    t = hp[hp[:, 0] <= tend + 1e-9, 0]
    ic = np.searchsorted(hc[:, 0], t)
    assert np.allclose(hc[ic, 0], t), "records of the two histories are not at the same times"
    o = dict(t_end_common=float(tend), n_records=int(len(t)))
    d = {}
    for name, col in (("alpha_min", 15), ("sum_mux", 5), ("sum_mW", 4), ("sum_m", 3),
                      ("np", 2)):
        d[name] = hc[ic, col] - hp[:len(t), col]
        o[f"max_abs_diff_{name}"] = float(np.max(np.abs(d[name])))
    tz = zp[zp[:, 0] <= tend + 1e-9, 0]
    jz = np.searchsorted(zc[:, 0], tz)
    for name, col in (("H", 3), ("M", 4)):
        a, b = np.sqrt(zc[jz, col]), np.sqrt(zp[:len(tz), col])
        d[name] = a / b - 1.0
        o[f"max_rel_diff_{name}_norm"] = float(np.max(np.abs(d[name])))
    return o, t, tz, d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tc", required=True, help="run id of the card job TC")
    ap.add_argument("--te", required=True, help="run id of the card job TE")
    ap.add_argument("--t0", required=True, help="run id of run_t0_records.py (nlim = 0)")
    ap.add_argument("--early", required=True, help="run id of the processor runs to 10 M")
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rec = json.load(open(os.path.join(SCRATCH, a.t0, "records.json")))
    res = dict(tc=a.tc, te=a.te, t0=a.t0, early=a.early, G={}, G2={})
    for name in ("v0", "v0.1", "v0.3", "v0.3s", "orbit"):
        top = a.te if name == "orbit" else a.tc
        res["G"][name] = compare_t0(os.path.join(SCRATCH, top, name), rec[name])
    hist = {}
    for name in ("v0", "v0.3", "v0.3s"):
        cpu = os.path.join(SCRATCH, a.early, name)
        if glob.glob(os.path.join(cpu, "*.nrpic.hst")):
            o, t, tz, d = compare_history(os.path.join(SCRATCH, a.tc, name), cpu)
            res["G2"][name] = o
            hist[name] = (t, tz, d)

    fs.use_style()
    col = {"v0": "k", "v0.3": fs.PAL["red"], "v0.3s": fs.PAL["orange"]}
    lab = {"v0": "at rest", "v0.3": r"$v = 0.3$", "v0.3s": r"$v = 0.3$, comoving shift"}
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.085, right=0.99, bottom=0.17, top=0.95, wspace=0.42)
    for name, (t, tz, d) in hist.items():
        ax[0].plot(t, np.abs(d["alpha_min"]) + 1e-17, color=col[name], label=lab[name])
        ax[1].plot(t, np.abs(d["sum_mux"]) + 1e-17, color=col[name], label=lab[name])
        ax[2].plot(tz, np.abs(d["H"]) + 1e-17, color=col[name], label=lab[name])
        ax[2].plot(tz, np.abs(d["M"]) + 1e-17, color=col[name], ls="--")
    ax[0].set_ylabel(r"$|\alpha_{\min}$(card) $-$ $\alpha_{\min}$(processor)$|$")
    ax[1].set_ylabel(r"$|\Delta \sum m u_x| / M$")
    ax[2].set_ylabel(r"$|$card/processor $- 1|$: $H$ (solid), $M$ (dashed)")
    for a_ in ax:
        a_.set_yscale("log")
        a_.set_xlabel(r"$t/M$")
    ax[0].legend(loc="lower right", fontsize=8)
    fs.save(fig, os.path.join(a.out, "fig_card_vs_cpu"))

    with open(os.path.join(a.out, "card_vs_cpu.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
