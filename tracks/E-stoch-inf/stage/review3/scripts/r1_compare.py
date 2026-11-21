#!/usr/bin/env python3
"""Risk R1 on processors: the slow-roll rungs L32p and L32m run with the release core-v0.4
processor executable against the same rungs of run E-20261115-172636-ce98836 (tested-branch
executable core/scalar-2 a58e95b).  Every dump compared word by word in all variables (own
reader of the lead, stage/G1/scripts/lead_check.py, extended to all variables), times and
cycles; the records sr.sf.hst and sr.sf.con.hst compared value by value.

    r1_compare.py NEW_RUN_DIR OLD_RUN_DIR OUT
"""
import json
import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "G1", "scripts")))
import lead_check as LC  # noqa: E402
sys.path.insert(0, HERE)
import figstyle as fs  # noqa: E402


def names_of(path):
    with open(path, "rb") as f:
        f.read(8)
        nvar = struct.unpack("<7q", f.read(56))[4]
        f.read(8)
        return [f.read(16).split(b"\0")[0].decode() for _ in range(nvar)]


def records(d, base):
    p = os.path.join(d, base)
    return np.loadtxt(p) if os.path.exists(p) else None


def main():
    new, old, out = sys.argv[1:4]
    os.makedirs(out, exist_ok=True)
    R = {}
    for run in ("L32p", "L32m"):
        dn, do = LC.dumps(os.path.join(new, run)), LC.dumps(os.path.join(old, run))
        rows = []
        for a, b in zip(dn, do):
            names = names_of(b)
            if names_of(a) != names:
                rows.append(dict(file=os.path.basename(a), names_differ=True))
                continue
            ta, ca, xa = LC.read_dump(a, names)
            tb, cb, xb = LC.read_dump(b, names)
            diff = {}
            words = 0
            maxrel = 0.0
            for n in names:
                ua, ub = xa[n].view(np.uint64), xb[n].view(np.uint64)
                k = int(np.count_nonzero(ua != ub))
                words += ua.size
                if k:
                    diff[n] = k
                    den = np.abs(xb[n]).max()
                    if den > 0:
                        maxrel = max(maxrel, float(np.abs(xa[n] - xb[n]).max() / den))
            rows.append(dict(file=os.path.basename(a), t_new=ta, t_old=tb, cycle_new=int(ca),
                             cycle_old=int(cb), time_bits_equal=bool(ta == tb),
                             words=words, differing_words=sum(diff.values()),
                             differing_by_variable=diff, max_rel_diff=maxrel))
        rec = {}
        for base in ("sr.sf.hst", "sr.sf.con.hst"):
            A, B = records(os.path.join(new, run), base), records(os.path.join(old, run), base)
            if A is None or B is None:
                rec[base] = "missing"
                continue
            m = min(len(A), len(B))
            d = np.abs(A[:m] - B[:m])
            den = np.maximum(np.abs(B[:m]), 1e-300)
            rec[base] = dict(rows_new=int(len(A)), rows_old=int(len(B)),
                             identical_rows=int(np.all(A[:m] == B[:m], axis=1).sum()),
                             max_rel=float((d / den).max()))
        R[run] = dict(dumps_new=len(dn), dumps_old=len(do), dumps=rows, records=rec,
                      total_differing_words=int(sum(r.get("differing_words", 0) for r in rows)))
        print(run, "dumps", len(dn), len(do), "differing words", R[run]["total_differing_words"],
              "records", rec)
    with open(os.path.join(out, "r1_compare.json"), "w") as fp:
        json.dump(R, fp, indent=1)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 0.42 * fs.FULL_WIDTH))
    for run, mk in (("L32p", "o"), ("L32m", "s")):
        rows = [r for r in R[run]["dumps"] if "t_old" in r]
        ax[0].plot([r["t_old"] for r in rows], [r["differing_words"] for r in rows], mk + "-",
                   label=f"{run}: differing 64-bit words")
        ax[1].semilogy([r["t_old"] for r in rows], [max(r["max_rel_diff"], 1e-18) for r in rows],
                       mk + "-", label=run)
    ax[0].set_xlabel("t (code units)")
    ax[0].set_ylabel("differing words per dump")
    ax[0].set_title("release core-v0.4 vs core/scalar-2, 32$^3$", fontsize=9)
    ax[0].legend(fontsize=7)
    ax[1].set_xlabel("t (code units)")
    ax[1].set_ylabel("max |new - old| / max |old| (1e-18 = identical)")
    ax[1].set_ylim(1e-19, 1)
    ax[1].legend(fontsize=7)
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "fig_r1"))


if __name__ == "__main__":
    main()
