"""T4 of tracks/A-emd-pbh/gauge/JOURNAL.md: the uniform-lapse toy of T1 (condition
conformal_kd) against the lapse at the overdensity of the 3D run
runs/cosmo/east_d0.05_n64_kd (conformal-time lapse plus lapse_kdriver = 1, zero shift,
64 cells, no refinement; main checkout, read only).

    python3 kd_compare.py --out OUTDIR [--run /data/haiyangw/nrpic/runs/cosmo/east_d0.05_n64_kd]

3D: east.nrpic.hst columns [1] t, [13] lapse at the probe (x_i = 1, the overdensity,
problems/cosmo/east.athinput:7, 88-90), [30] largest lapse; a = (1 + t/2)^2.
Toy: the collapse epoch X of the top-hat is chosen so that the top-hat lapse reaches its
maximum at the same background a as the 3D lapse at the overdensity. Compared: the ratio
of the overdensity lapse to the largest lapse after that maximum.
"""
import argparse
import json
import os
import sys

import numpy as np
from scipy.optimize import brentq

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lapse_toy as lt  # noqa: E402
from nrpic.figstyle import use_style, SERIES, MASK_LINE, FULL_WIDTH  # noqa: E402


def load(path, cols):
    rows = []
    with open(path) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            v = line.split()
            try:
                rows.append([float(v[c - 1]) for c in cols])
            except (ValueError, IndexError):
                continue
    a = np.array(rows)
    ok = np.all(np.isfinite(a) & (np.abs(a) < 1e300), axis=1)
    return a[ok]


def toy(X):
    th = lt.TopHat(X)
    rec, status, _, _ = lt.integrate("conformal_kd", th, X, a_end_factor=3.0)
    return rec, status


def a_of_peak(X):
    rec, _ = toy(X)
    return rec["a"][np.argmax(rec["al_c"])]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--run", default="/data/haiyangw/nrpic/runs/cosmo/east_d0.05_n64_kd")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    h = load(os.path.join(args.run, "east.nrpic.hst"), [1, 13, 30])
    t3, alp3, amax3 = h[:, 0], h[:, 1], h[:, 2]
    a3 = (1 + t3 / 2) ** 2
    i_pk = int(np.argmax(alp3))
    a_pk = float(a3[i_pk])
    print(f"3D: lapse at the overdensity peaks at t = {t3[i_pk]:.4f} (a = {a_pk:.3f}), "
          f"alpha = {alp3[i_pk]:.3f}; last finite record t = {t3[-1]:.4f} "
          f"(a = {a3[-1]:.3f}), ratio there {alp3[-1] / amax3[-1]:.4f}")
    X = brentq(lambda x: a_of_peak(x) - a_pk, 5.0, 200.0, xtol=1e-3)
    rec, status = toy(X)
    ratio_toy = rec["al_c"] / rec["al_b"]
    res = {"a_peak_3D": a_pk, "t_peak_3D": float(t3[i_pk]), "X_toy": X,
           "toy_status": status, "compare": {}}
    for a_eval in (a_pk * 1.1, 18.6, 20.0, float(a3[-1])):
        r3 = float(np.interp(a_eval, a3, alp3 / amax3))
        rt = float(np.interp(a_eval, rec["a"], ratio_toy))
        res["compare"][f"{a_eval:.3f}"] = {"ratio_3D": r3, "ratio_toy": rt,
                                            "toy_over_3D": rt / r3}
        print(f"a = {a_eval:7.3f}: overdensity / largest lapse, 3D {r3:.4f}, "
              f"toy {rt:.4f}, toy/3D {rt / r3:.3f}")
    print(f"toy X = {X:.3f}, status {status}")
    with open(os.path.join(args.out, "kd_compare.json"), "w") as f:
        json.dump(res, f, indent=1)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    use_style()
    fig, axs = plt.subplots(1, 2, figsize=(FULL_WIDTH, 3.2))
    fig.subplots_adjust(left=0.08, right=0.985, bottom=0.15, top=0.95, wspace=0.28)
    ax = axs[0]
    ax.plot(a3, alp3, color=SERIES[1], label="3D, overdensity")
    ax.plot(a3, amax3, color=SERIES[1], ls="--", label="3D, largest lapse")
    ax.plot(rec["a"], rec["al_c"], color=SERIES[0], label=f"toy top-hat (X = {X:.1f})")
    ax.plot(rec["a"], rec["al_b"], color=SERIES[0], ls="--", label="toy background")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(1, 30)
    ax.set_ylim(1e-2, 40)
    ax.set_xlabel(r"background scale factor $a$")
    ax.set_ylabel(r"lapse")
    ax.legend(fontsize=8, loc="lower left")
    ax = axs[1]
    ax.plot(a3, alp3 / amax3, color=SERIES[1], label="3D")
    ax.plot(rec["a"], ratio_toy, color=SERIES[0], label="toy")
    ax.axvline(a_pk, **MASK_LINE)
    ax.set_xlim(8, 25)
    ax.set_yscale("log")
    ax.set_ylim(1e-3, 1.5)
    ax.set_xlabel(r"background scale factor $a$")
    ax.set_ylabel(r"overdensity lapse / largest lapse")
    ax.legend(fontsize=8, loc="lower left")
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(args.out, f"kd_compare.{ext}"))
    print("wrote", os.path.join(args.out, "kd_compare.png"))


if __name__ == "__main__":
    main()
