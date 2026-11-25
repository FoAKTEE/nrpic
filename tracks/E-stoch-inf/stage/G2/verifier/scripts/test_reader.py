"""V0, V2: reader and extraction on an analytic field; floor formula; alpha twins.

python3 test_reader.py --out DIR
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vlib  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rng = np.random.default_rng(12345)
    res = {}

    # --- V0a: synthetic dump, known plane waves in phi, chi, gt_ij; amplitude scale
    # 1 (sizes of the USR fields) and 1e3 (to separate the rounding of the stored fields)
    N, nmax2 = 32, 64
    band = vlib.hemisphere(nmax2)
    for scale in (1.0, 1e3):
        tag = "V0a" if scale == 1.0 else "V0a_x1e3"
        pick = rng.choice(len(band), 40, replace=False)
        n = band[pick]
        cphi = (rng.normal(size=40) + 1j * rng.normal(size=40)) * 1e-6 * scale
        cx = (rng.normal(size=40) + 1j * rng.normal(size=40)) * 1e-5 * scale
        cg = {nm: (rng.normal(size=40) + 1j * rng.normal(size=40)) * 1e-7 * scale
              for nm, _, _ in vlib.GT}
        chi_b, phi_b, Pi_b, K_b = 0.37, -0.16, 3.2e-2, -2.9
        fields = {
            "phi": phi_b + vlib.synth(n, cphi, N),
            "Pi": np.full((N, N, N), Pi_b),
            "chi": chi_b * (1.0 + vlib.synth(n, cx, N)),
            "K": np.full((N, N, N), K_b),
            "alpha": np.ones((N, N, N)),
        }
        for nm, i, j in vlib.GT:
            fields[nm] = (1.0 if i == j else 0.0) + vlib.synth(n, cg[nm], N)
        path = os.path.join(a.out, "synthetic.dump")
        vlib.write_dump(path, fields, time=1.25, cycle=7)
        h = vlib.dump_header(path)
        res[tag + "_header"] = dict(time=h["time"], cycle=h["cycle"], names=h["names"], nx=h["nx"])
        res[tag + "_readback_maxdiff"] = float(max(np.abs(vlib.read_var(h, nm) - fields[nm]).max()
                                                   for nm in fields))
        hop = -K_b / (3.0 * Pi_b)
        kn = n / np.sqrt((n ** 2).sum(1))[:, None]
        expect = hop * cphi + 0.5 * cx
        for nm, i, j in vlib.GT:
            expect = expect + (1.0 if i == j else 2.0) * 0.25 * kn[:, i] * kn[:, j] * cg[nm]
        r = vlib.rnr_from_dump(path, band, want_full=True)
        got = r["c"][pick]
        rmsx = np.sqrt(np.mean(np.abs(expect) ** 2))
        res[tag + "_set_err_rel_rms"] = float(np.abs(got - expect).max() / rmsx)
        other = np.ones(len(band), bool)
        other[pick] = False
        res[tag + "_outside_rel_rms"] = float(np.abs(r["c"][other]).max() / rmsx)
        res[tag + "_rms_full_over_band"] = float(r["rms_full"] / r["rms_band"])
        res[tag + "_H_over_Pi"] = [r["H_over_Pi"], hop]
        os.remove(path)

    # --- V0b: floor formula on synthetic odd parts o_s = s A + F_s
    M = 64 ** 3
    A = rng.normal(size=M)
    f_true = 0.3
    Fs = {s: f_true * rng.normal(size=M) for s in (1.0, 0.5)}
    o = {s: np.sqrt(np.mean((s * A + Fs[s]) ** 2)) for s in (1.0, 0.5)}
    f = np.sqrt(vlib.floor2(o[1.0], o[0.5]))
    res["V0b_floor_recovered_over_true"] = float(f / f_true)
    # same floor field in both (correlated floor)
    Fc = f_true * rng.normal(size=M)
    o = {s: np.sqrt(np.mean((s * A + Fc) ** 2)) for s in (1.0, 0.5)}
    res["V0b_floor_recovered_over_true_correlated"] = float(np.sqrt(vlib.floor2(o[1.0], o[0.5])) / f_true)

    # --- V2: alpha from philox_ref against core's twin
    big = vlib.hemisphere(4096)
    res["n_modes_4096"] = int(len(big))
    res["n_modes_1024"] = int(len(vlib.hemisphere(1024)))
    smp = big[rng.choice(len(big), 2000, replace=False)]
    for seed in (20261115, 20261116):
        a1 = vlib.alpha_modes(seed, smp)
        a2 = vlib.alpha_modes_core_twin(seed, smp)
        res[f"V2_alpha_maxdiff_seed{seed}"] = float(np.abs(a1 - a2).max())
        res[f"V2_alpha_mean_abs2_seed{seed}"] = float(np.mean(np.abs(a1) ** 2))
    json.dump(res, open(os.path.join(a.out, "test_reader.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
