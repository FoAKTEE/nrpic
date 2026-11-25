"""Two small checks after reading the package's claims (JOURNAL entry 5):
(1) the release pair U256ap/am against the scouting pair U256/U256m (core_scalar-3) at N_f,
    variable by variable (max |difference|), one variable of each file at a time;
(2) the part of the odd-part error common to all modes, mean Re(O/(s p) - 1) over k <= 16 dk,
    at s = 1, 1/2, 1/4 (256^3) and s = 1 (320^3).

python3 checks2.py --ref REFDIR --modes MODESDIR --out DIR
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vlib  # noqa: E402

SCOUT = {"U256ap": os.path.join(vlib.SCRATCH, "E-20261121-075255-8cf90e7", "U256", "usr.sf.00020.dump"),
         "U256am": os.path.join(vlib.SCRATCH, "E-20261121-085221-1f579fe", "U256m", "usr.sf.00020.dump")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", required=True)
    ap.add_argument("--modes", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = {"release_vs_scouting": {}}
    for lab, sp in SCOUT.items():
        hr = vlib.dump_header(vlib.dump_path(lab, 20))
        hs = vlib.dump_header(sp)
        r = {"t_release": hr["time"], "t_scouting": hs["time"], "cycle": [hr["cycle"], hs["cycle"]],
             "names_equal": hr["names"] == hs["names"], "max_abs_diff": {}}
        for nm in hr["names"]:
            x = vlib.read_var(hr, nm)
            y = vlib.read_var(hs, nm)
            r["max_abs_diff"][nm] = float(np.abs(x - y).max())
            del x, y
        r["all_identical"] = all(v == 0.0 for v in r["max_abs_diff"].values())
        res["release_vs_scouting"][lab] = r
        print(lab, json.dumps(r), flush=True)
    ref = np.load(os.path.join(a.ref, "reference_dumps.npz"))
    n = np.load(os.path.join(a.modes, "modes_n.npy"))
    n2 = (n ** 2).sum(1)
    sh = np.searchsorted(ref["q2"], n2)
    i = int(np.argmin(np.abs(ref["t"] - 10.437508874065651)))
    p = vlib.L_BOX ** -1.5 * ref["W"][i][sh] * ref["R"][i][sh] * vlib.alpha_modes(vlib.SEED["A"], n)
    c = lambda lab: np.load(os.path.join(a.modes, f"{lab}_d20.npz"))["c"]
    low = n2 <= 256
    cm = {}
    for key, (lp, lm, s) in {"s1_256": ("U256ap", "U256am", 1.0), "s05_256": ("U256hp", "U256hm", 0.5),
                             "s025_256": ("U256qp", "U256qm", 0.25), "s1_320": ("U320ap", "U320am", 1.0)}.items():
        O = 0.5 * (c(lp) - c(lm))
        d = np.real(O[low] / (s * p[low]) - 1)
        cm[key] = {"mean": float(d.mean()), "std": float(d.std())}
    cm["ratio_s1_over_s05"] = cm["s1_256"]["mean"] / cm["s05_256"]["mean"]
    cm["ratio_s05_over_s025"] = cm["s05_256"]["mean"] / cm["s025_256"]["mean"]
    res["common_mode_k_le_16"] = cm
    json.dump(res, open(os.path.join(a.out, "checks2.json"), "w"), indent=1)
    print(json.dumps(cm, indent=1))


if __name__ == "__main__":
    main()
