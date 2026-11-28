#!/usr/bin/env python3
"""Constraint ratios of the mesh pairs under several pairings of the two histories
(answer to the G2 verifier's corrections a and b, stage/G2/VERIFIER.md section 5).

(1) One particle per cell, zero shift, 128^3 over 256^3 (q0007 stops at a = 101), mean
    Hamiltonian and momentum constraint, pairings:
      E  at the catalogue epochs a = 25, 36, 49, 64, 81, 90, 100 only, both histories
         interpolated in log a (the pairing of judge_c3.py and of B-20261126-024849-87e72b7);
      F  every 256^3 record, the 128^3 history interpolated in log a;
      C  every 128^3 record, the 256^3 history interpolated in log a;
      N  every 256^3 record with the 128^3 record nearest in a.
    Smallest and largest over 25 <= a <= 100 and 36 <= a <= 100.
(2) Eight particles per cell, zero shift, 64^3 over 128^3 (q0070 against q0006 + q0042),
    pairing of judge_c3.py (every 64^3 record, 128^3 interpolated): the momentum ratio over
    a >= 36 and a >= 49; the Hamiltonian ratio likewise.

  pair_ratio.py <scratch> <run64> <out dir>
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from judge_c3 import (BASE_128, M256, P8_128, COL, history, interp, scale)   # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "python"))
from nrpic import figstyle as fs    # noqa: E402

EPOCHS = np.array([25.0, 36.0, 49.0, 64.0, 81.0, 90.0, 100.0])


def nearest(h, col, a):
    ah = scale(h[:, 0])
    j = np.abs(np.log(ah)[None, :] - np.log(a)[:, None]).argmin(axis=1)
    return np.abs(h[j, COL[col]])


def ext(a, r, lo, hi=100.0):
    s = (a >= lo) & (a <= hi)
    return [float(r[s].min()), float(r[s].max())] if s.any() else [None, None]


def main():
    scr, run64, od = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(od, exist_ok=True)
    hb, hm = history(scr, BASE_128), history(scr, M256)
    a_b, a_m = scale(hb[:, 0]), scale(hm[:, 0])
    a_stop = float(a_m[-1])
    out = {"a_last_256": a_stop, "one_ppc_zero_shift": {}, "eight_ppc": {}}
    curves = {}
    for col in ("Hr_mean", "Mr_mean"):
        res = {}
        # E: epochs
        e = EPOCHS[EPOCHS <= a_stop]
        rE = interp(hb, col, e) / interp(hm, col, e)
        res["E_epochs"] = {"a": e.tolist(), "ratio": rE.tolist(),
                           "25-100": ext(e, rE, 25), "36-100": ext(e, rE, 36)}
        # F: every 256^3 record
        s = (a_m >= 25) & (a_m <= 100)
        aF = a_m[s]
        rF = interp(hb, col, aF) / np.abs(hm[s, COL[col]])
        res["F_fine_rows"] = {"25-100": ext(aF, rF, 25), "36-100": ext(aF, rF, 36),
                              "n": int(s.sum())}
        # C: every 128^3 record
        s = (a_b >= 25) & (a_b <= min(100, a_stop))
        aC = a_b[s]
        rC = np.abs(hb[s, COL[col]]) / interp(hm, col, aC)
        res["C_coarse_rows"] = {"25-100": ext(aC, rC, 25), "36-100": ext(aC, rC, 36),
                                "n": int(s.sum())}
        # N: nearest records
        rN = nearest(hb, col, aF) / np.abs(hm[(a_m >= 25) & (a_m <= 100), COL[col]])
        res["N_nearest"] = {"25-100": ext(aF, rN, 25), "36-100": ext(aF, rN, 36)}
        out["one_ppc_zero_shift"][col] = res
        curves[col] = dict(E=(e, rE), F=(aF, rF), C=(aC, rC), N=(aF, rN))
    # eight per cell
    h64, h128 = history(scr, [run64]), history(scr, P8_128)
    a64 = scale(h64[:, 0])
    sel = (a64 >= 25) & (a64 <= min(141.0, scale(h128[-1, 0])))
    for col in ("Hr_mean", "Mr_mean"):
        r = h64[sel, COL[col]] / interp(h128, col, a64[sel])
        out["eight_ppc"][col] = {"a>=25": ext(a64[sel], r, 25, 141), "a>=36": ext(a64[sel], r, 36, 141),
                                 "a>=49": ext(a64[sel], r, 49, 141)}
        s36 = (a64[sel] >= 36) & (a64[sel] < 49)
        out["eight_ppc"][col]["36<=a<49"] = ext(a64[sel][s36], r[s36], 36, 49)
        curves["p8_" + col] = (a64[sel], r)
    with open(os.path.join(od, "pair_ratio.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))

    import matplotlib.pyplot as plt
    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.6), constrained_layout=True)
    ax = axs[0]
    c = curves["Hr_mean"]
    ax.plot(*c["F"], "-", color="C0", lw=0.9, label="F: every $256^3$ record")
    ax.plot(*c["C"], "-", color="C1", lw=0.9, label="C: every $128^3$ record")
    ax.plot(*c["N"], ".", color="0.5", ms=2, label="N: nearest record")
    ax.plot(*c["E"], "o", color="k", ms=4, mfc="none", label="E: catalogue epochs")
    ax.axhspan(1.11, 1.36, color="C2", alpha=0.15, label="Table VII band (1.11-1.36)")
    ax.axvline(36, color="0.6", ls=":", lw=0.8)
    ax.set_xscale("log")
    ax.set_xlabel("$a$")
    ax.set_ylabel(r"$\overline{H}$, $128^3$ over $256^3$ (1 ppc, ZS)")
    ax.legend(fontsize=6, loc="lower right")
    ax = axs[1]
    for col, cc, lab in (("Hr_mean", "C0", "Hamiltonian"), ("Mr_mean", "C3", "momentum")):
        a, r = curves["p8_" + col]
        ax.plot(a, r, "-", color=cc, lw=1.0, label=lab)
    ax.axvline(36, color="0.6", ls=":", lw=0.8)
    ax.axvline(49, color="0.3", ls="--", lw=0.8)
    ax.axhspan(1.71, 2.16, color="C3", alpha=0.12)
    ax.set_xscale("log")
    ax.set_xlabel("$a$")
    ax.set_ylabel("$64^3$ over $128^3$ (8 ppc, ZS)")
    ax.legend(fontsize=6, loc="lower right")
    fs.save(fig, os.path.join(od, "pair_ratio"))
    plt.close(fig)


if __name__ == "__main__":
    main()
