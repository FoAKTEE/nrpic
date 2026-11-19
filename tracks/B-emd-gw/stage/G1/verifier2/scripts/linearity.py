"""Linearity of c_+(k,k,0) in eps, pair by pair, from the single- (bin) and double-precision
(rst) dumps of the scan diagnostics (verifier2).

    python3 linearity.py SCANDIR OUTDIR       (OUTDIR "-": $NRPIC_RUN_DIR)

For the pairs (0.1, 0.3), (0.1, 1), (0.3, 1) at 64^3 and 32^3: r = (c(e1)/e1)/(c(e2)/e2) - 1
against a (bin: cubic spline of the second series at the dump times of the first; rst: the
restart dumps of both runs at the same nominal times, times compared). Fourth-order
perturbation theory with the x <-> y symmetry gives c = Phi1 Phi2 [alpha + beta (Phi1^2 +
Phi2^2)], so r(e1, e2) = R (e1^2 - e2^2) with one R(a) for all pairs: the test is
r(0.1,0.3) / r(0.1,1) = 0.08/0.99 = 0.0808.
Writes OUTDIR/linearity.json and OUTDIR/linearity.{pdf,png}.
"""
import json
import os
import sys

import numpy as np
from scipy.interpolate import CubicSpline

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle as fs  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

EPS = {"eps0p1": 0.1, "eps0p3": 0.3, "eps1": 1.0}


def ser(scandir, label, kind):
    with open(os.path.join(scandir, f"{label}.json")) as f:
        r = [x for x in json.load(f)["records"] if x["kind"] == kind]
    return np.array([x["time"] for x in r]), np.array([x["h"]["K1"][0] for x in r])


def main():
    scandir = sys.argv[1]
    outdir = sys.argv[2] if sys.argv[2] != "-" else os.environ["NRPIC_RUN_DIR"]
    fs.use_style()
    res = {}
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.4), sharey=True)
    fig.subplots_adjust(left=0.1, right=0.98, bottom=0.15, top=0.93, wspace=0.05)
    pairs = [("eps0p1", "eps0p3"), ("eps0p1", "eps1"), ("eps0p3", "eps1")]
    cols = [fs.PAL["blue"], fs.PAL["red"], fs.PAL["green"]]
    for j, n in enumerate((64, 32)):
        for (e1, e2), col in zip(pairs, cols):
            t1, c1 = ser(scandir, f"n{n}_{e1}", "bin")
            t2, c2 = ser(scandir, f"n{n}_{e2}", "bin")
            m = (t1 > 0.3) & (t1 <= t2[-1])
            t, c = t1[m], c1[m]
            r = (c/EPS[e1])/(CubicSpline(t2, c2)(t)/EPS[e2]) - 1.0
            a = (1 + t/2)**2
            T1, C1 = ser(scandir, f"n{n}_{e1}", "rst")
            T2, C2 = ser(scandir, f"n{n}_{e2}", "rst")
            k = min(len(T1), len(T2))
            mm = T1[:k] > 0.3
            R = (C1[:k][mm]/EPS[e1])/(C2[:k][mm]/EPS[e2]) - 1.0
            A = (1 + T1[:k][mm]/2)**2
            key = f"n{n}_{e1}_{e2}"
            res[key] = {
                "bin": {str(at): float(r[int(np.argmin(np.abs(a - at)))]) for at in (2, 3, 5, 7, 10, 15, 20, 30, 40, 60)},
                "rst": {f"{x:.2f}": float(y) for x, y in zip(A, R) if x <= 60},
                "rst_time_mismatch_max": float(np.abs(T1[:k] - T2[:k]).max()),
                "bin_max_abs_a2_10": float(np.abs(r[(a >= 2) & (a <= 10)]).max()),
            }
            ax[j].plot(a, 100*r, color=col, label=fr"$\epsilon$ = {EPS[e1]} vs {EPS[e2]}")
            ax[j].plot(A, 100*R, "o", color=col, ms=3)
        ax[j].set_xscale("log")
        ax[j].set_yscale("symlog", linthresh=0.01)
        ax[j].axhline(0, **fs.THIN)
        ax[j].set_xlim(1.3, 60)
        ax[j].set_xlabel(r"$a$")
        ax[j].set_title(f"${n}^3$ (lines bin, dots rst)", fontsize=10)
    ax[0].set_ylabel(r"$(c_+/\epsilon)_1/(c_+/\epsilon)_2 - 1$ [%]")
    ax[0].legend(loc="upper left")
    for n in (64, 32):
        for at in ("5", "10", "20", "40"):
            r13 = res[f"n{n}_eps0p1_eps0p3"]["bin"][at]
            r11 = res[f"n{n}_eps0p1_eps1"]["bin"][at]
            res.setdefault("ratio_r(0.1,0.3)/r(0.1,1)", {})[f"n{n}_a{at}"] = r13/r11
    with open(os.path.join(outdir, "linearity.json"), "w") as f:
        json.dump(res, f, indent=1)
    fs.save(fig, os.path.join(outdir, "linearity"))
    print(json.dumps(res, indent=1)[:6000])


if __name__ == "__main__":
    main()
