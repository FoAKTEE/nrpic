"""Follow-up of judge_modes (JOURNAL entry 2): what sets max D_n at k <= 32 dk.

The odd part of R^NR at amplitude s is O(s) = s L + s^3 T + ... (L linear, with the lattice
and time-step error; T third order). From the seed-A pairs at s = 1 and 1/2:
L = (8 O(1/2) - O(1))/3 (Richardson in s^2), checked with the pair at s = 1/4. D_lin = |L/p - 1|
is the discretisation error alone; D_3 = |O(1) - L|/|p| the third-order share at s = 1.
Also D_n at the axis modes |n| = 32 for 256^3 and 320^3.

python3 extra_modes.py --ref REFDIR --modes MODESDIR --out DIR
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vlib  # noqa: E402

L32 = vlib.L_BOX ** -1.5


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", required=True)
    ap.add_argument("--modes", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    ref = np.load(os.path.join(a.ref, "reference_dumps.npz"))
    n = np.load(os.path.join(a.modes, "modes_n.npy"))
    n2 = (n ** 2).sum(1)
    sh = np.searchsorted(ref["q2"], n2)
    i = int(np.argmin(np.abs(ref["t"] - 10.437508874065651)))
    p = L32 * ref["W"][i][sh] * ref["R"][i][sh] * vlib.alpha_modes(vlib.SEED["A"], n)
    c = lambda lab: np.load(os.path.join(a.modes, f"{lab}_d20.npz"))["c"]
    O = {1.0: 0.5 * (c("U256ap") - c("U256am")), 0.5: (c("U256hp") - c("U256hm")),
         0.25: 2.0 * (c("U256qp") - c("U256qm"))}          # O(s)/s
    O320 = 0.5 * (c("U320ap") - c("U320am"))
    half = n2 <= 1024
    Lr = (4.0 * O[0.5] - O[1.0]) / 3.0                    # Richardson from s = 1, 1/2
    Lq = (4.0 * O[0.25] - O[0.5]) / 3.0                   # from s = 1/2, 1/4
    Dlin = np.abs(Lr / p - 1)
    D3 = np.abs(O[1.0] - Lr) / np.abs(p)
    # 320: subtract the third-order part measured at 256 (assumed resolution-independent)
    Dlin320 = np.abs((O320 - (O[1.0] - Lr)) / p - 1)
    res = {
        "max_D_s1_k32": float(np.abs(O[1.0] / p - 1)[half].max()),
        "max_Dlin_k32": float(Dlin[half].max()),
        "argmax_Dlin": n[half][int(np.argmax(Dlin[half]))].tolist(),
        "max_D3_s1_k32": float(D3[half].max()),
        "median_D3_s1_k32": float(np.median(D3[half])),
        "Richardson_consistency_k32_max": float((np.abs(Lr - Lq) / np.abs(p))[half].max()),
        "Richardson_consistency_k32_median": float(np.median((np.abs(Lr - Lq) / np.abs(p))[half])),
        "max_D320_k32": float(np.abs(O320 / p - 1)[half].max()),
        "max_Dlin320_k32": float(Dlin320[half].max()),
        "factor_maxDlin_256_over_320": float(Dlin[half].max() / Dlin320[half].max()),
    }
    ax = np.array([[32, 0, 0], [0, 32, 0], [0, 0, 32]])
    idx = [int(np.nonzero((n == v).all(1))[0][0]) for v in ax]
    res["axis32"] = {str(v.tolist()): {"D256_s1": float(abs(O[1.0][j] / p[j] - 1)),
                                       "D256_s05": float(abs(O[0.5][j] / p[j] - 1)),
                                       "D256_s025": float(abs(O[0.25][j] / p[j] - 1)),
                                       "D256_lin": float(Dlin[j]),
                                       "D320_s1": float(abs(O320[j] / p[j] - 1)),
                                       "D320_lin": float(Dlin320[j])}
                     for v, j in zip(ax, idx)}
    d256 = np.mean([r["D256_lin"] for r in res["axis32"].values()])
    d320 = np.mean([r["D320_lin"] for r in res["axis32"].values()])
    res["axis32_factor_256lin_over_320"] = float(d256 / d320)
    # share of modes k <= 32 whose D at s = 1 is set by the third-order part
    res["frac_k32_D3_gt_Dlin"] = float((D3[half] > Dlin[half]).mean())
    json.dump(res, open(os.path.join(a.out, "extra_modes.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle
    figstyle.use_style()
    k = np.sqrt(n2)
    kb = np.floor(k).astype(int)
    fig, x = plt.subplots(figsize=(5.5, 3.8))
    for arr, lab in ((np.abs(O[1.0] / p - 1), "D (s = 1, 256)"), (Dlin, "D_lin (Richardson, 256)"),
                     (D3, "third-order share at s = 1"), (np.abs(O320 / p - 1), "D (s = 1, 320)")):
        mx = np.zeros(65)
        np.maximum.at(mx, kb, arr)
        x.semilogy(np.arange(1, 65), mx[1:], label=lab)
    x.axvline(32, color="0.5", ls=":", lw=0.8)
    x.set_xlabel("k / dk (bin of width 1)")
    x.set_ylabel("max over the bin")
    x.set_title("what sets max D_n at N_f (seed A)", fontsize=8)
    x.legend(fontsize=6)
    fig.tight_layout()
    fig.savefig(os.path.join(a.out, "fig_extra_modes.png"), dpi=150)


if __name__ == "__main__":
    main()
