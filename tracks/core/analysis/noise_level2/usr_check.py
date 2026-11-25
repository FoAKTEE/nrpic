#!/usr/bin/env python3
"""Level 2 through the ultra-slow-roll phase (tracks/core/JOURNAL-noise-level2.md,
entry 5): problems/scalar/usr_stochastic.athinput (inflection, 32^3, nmax2 = 64, to its
tlim) at level 2 and at level 1 on the mesh, dumps with the per-mode record; the
relative difference of the projected coefficients and the size of R against time.

    usr_check.py --exe ATHENA --out DIR
"""
import argparse
import concurrent.futures as cf
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import nl2                     # noqa: E402
import numpy as np             # noqa: E402

INP = os.path.join(nl2.PROB, "usr_stochastic.athinput")
MODES = os.path.join(nl2.PROB, "usr_stochastic_modes.txt")
BASE = {"scalar_field/noise_mode_file": MODES, "scalar_field/noise_rmodes_dump": "true",
        "scalar_field/dump_noise": "false", "scalar_field/dump_constraints": "false"}
CASES = {"u2": {"scalar_field/noise_level": 2},
         "u1m": {"scalar_field/noise_level": 1, "scalar_field/noise_mode_eq": "mesh"}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)

    def one(name):
        inp = nl2.write_input(INP, os.path.join(out, name + ".athinput"),
                              {**BASE, **CASES[name]})
        return name, nl2.run(os.path.abspath(a.exe), os.path.join(out, name), inp)
    with cf.ThreadPoolExecutor(max_workers=2) as pool:
        rcs = dict(pool.map(one, list(CASES)))
    rows = []
    nd = len(glob.glob(os.path.join(out, "u2", "usr.sf.?????.rmodes")))
    for k in range(nd):
        try:
            h, _, n2, r2, d2 = nl2.read_rmodes(os.path.join(out, "u2", f"usr.sf.{k:05d}.rmodes"))
            _, _, _, r1, d1 = nl2.read_rmodes(os.path.join(out, "u1m", f"usr.sf.{k:05d}.rmodes"))
        except (OSError, ValueError):
            break
        rel = np.abs(r2 - r1)/np.abs(r1)
        rows.append(dict(time=h["time"], max_rel=float(rel.max()),
                         rms_rel=float(np.sqrt(np.mean(rel**2))),
                         finite=bool(np.all(np.isfinite(r2))),
                         rms_absR=float(np.sqrt(np.mean(np.abs(r1)**2)))))
    hst = {}
    for name in CASES:
        h = np.loadtxt(os.path.join(out, name, "usr.sf.hst"))
        hst[name] = dict(last_time=float(h[-1, 0]), finite=bool(np.all(np.isfinite(h))),
                         rms_phi_last=float(h[-1, 7]), pi_b_last=float(h[-1, 19]))
    nl2.dump_json(dict(exit=rcs, rows=rows, hst=hst), os.path.join(out, "summary.json"))
    import matplotlib
    matplotlib.use("Agg")
    from nrpic import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.7))
    fig.subplots_adjust(left=0.09, right=0.99, bottom=0.18, top=0.9, wspace=0.3)
    t = [r["time"] for r in rows]
    ax[0].semilogy(t, [max(r["max_rel"], 1e-17) for r in rows], "o-", ms=3,
                   color=fs.PAL["red"], label="max over modes")
    ax[0].semilogy(t, [max(r["rms_rel"], 1e-17) for r in rows], "s-", ms=3,
                   color=fs.PAL["blue"], label="rms over modes")
    ax[0].set_xlabel("$t$ (1/H$_*$)")
    ax[0].set_ylabel(r"$|c^{L2}_R/c^{L1,{\rm mesh}}_R-1|$")
    ax[0].set_title("(a) inflection case, 32$^3$", fontsize=8)
    ax[0].legend(fontsize=6)
    ax[1].semilogy(t, [r["rms_absR"] for r in rows], "o-", ms=3, color=fs.PAL["green"])
    ax[1].set_xlabel("$t$ (1/H$_*$)")
    ax[1].set_ylabel(r"rms$_n$ $|R_n|$ of the mesh field (level 1, mesh)")
    ax[1].set_title("(b) size of the mode functions", fontsize=8)
    fig.savefig(os.path.join(out, "fig_usr.png"), dpi=200)
    print(rcs, hst)
    print(rows[-1] if rows else None)


if __name__ == "__main__":
    main()
