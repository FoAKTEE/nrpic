#!/usr/bin/env python3
"""T-N0: the draws re-implemented from rng.md (philox_ref.py) against core's twin.

    python3 check_twin.py --twin PATH/rng.py --out DIR

PATH/rng.py is core's twin, extracted with
`git show core/rng:python/nrpic/rng.py > PATH/rng.py` (repository code, not a download).
Compares the raw words and the normal pairs for every mode of the unit-test lattice
(N = 64, nmax2 = 256) for three seeds, two degrees of freedom and three epochs, and for
2000 random keys; writes check_twin.json, summary.txt and fig_check_twin.png/pdf.
"""
import argparse
import importlib.util
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "python"))
import philox_ref as pr                                   # noqa: E402
from noise_ref import Lattice                             # noqa: E402


def load_twin(path):
    spec = importlib.util.spec_from_file_location("core_rng_twin", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--twin", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    tw = load_twin(a.twin)
    lat = Lattice(64, 2.5, 256)
    ent = pr.mode_entity(lat.n)
    res = {"lattice_modes": int(lat.M)}
    word_diff = 0
    agm_bitdiff = 0
    libm_dev = []
    libm_L = []
    nkeys = 0
    for seed in (0, 20261115, (1 << 64) - 1):
        for dof in (0, 1):
            st = pr.noise_stream(dof)
            for ep in (0, 1, 400):
                for block in (0, 1):
                    w_me = pr.words(seed, st, ent, ep, 0, pr.KIND_NORMAL, block)
                    w_tw = tw.words(seed, st, ent, ep, 0, 0, tw.KIND_NORMAL, block)
                    word_diff += int(np.count_nonzero(w_me != w_tw))
                z_tw = tw.normal2(seed, st, ent, ep, 0)
                z_agm = pr.normal2(seed, st, ent, ep, 0, 0, "agm")
                z_lib = pr.normal2(seed, st, ent, ep, 0, 0, "libm")
                for i in range(2):
                    agm_bitdiff += int(np.count_nonzero(
                        z_agm[i].view(np.uint64) != z_tw[i].view(np.uint64)))
                    libm_dev.append(np.abs(z_lib[i] - z_tw[i]))
                L = 0.5 * (z_tw[0]**2 + z_tw[1]**2)       # = L for the accepted point
                libm_L += [L, L]
                nkeys += ent.size
    rng = np.random.default_rng(7)
    rk_word, rk_agm = 0, 0
    for _ in range(2000):
        seed = int(rng.integers(0, 2**63)) * 2 + int(rng.integers(0, 2))
        stream = int(rng.integers(0, 2**63))
        e = int(rng.integers(1, 2**63))
        step = int(rng.integers(0, 2**40))
        draw = int(rng.integers(0, 2**20))
        w_me = pr.words(seed, stream, [e], step, draw, pr.KIND_NORMAL, 0)
        w_tw = tw.words(seed, stream, e, step, draw, 0, tw.KIND_NORMAL, 0)
        rk_word += int(np.count_nonzero(w_me != w_tw))
        z_me = pr.normal2(seed, stream, [e], step, draw, 0, "agm")
        z_tw = tw.normal2(seed, stream, e, step, draw)
        for i in range(2):
            rk_agm += int(np.count_nonzero(np.atleast_1d(z_me[i]).view(np.uint64)
                                           != np.atleast_1d(z_tw[i]).view(np.uint64)))
    dev = np.concatenate(libm_dev)
    Ls = np.concatenate(libm_L)
    res.update(lattice_keys=nkeys, lattice_words_differing=word_diff,
               lattice_agm_deviates_not_bit_identical=agm_bitdiff,
               random_keys=2000, random_words_differing=rk_word,
               random_agm_deviates_not_bit_identical=rk_agm,
               libm_max_abs_dev=float(dev.max()), libm_median_abs_dev=float(np.median(dev)),
               libm_frac_nonzero=float(np.mean(dev > 0)))
    ok = (word_diff == 0 and rk_word == 0 and agm_bitdiff == 0 and rk_agm == 0
          and res["libm_max_abs_dev"] < 1e-9 and res["libm_median_abs_dev"] < 1e-15)
    res["prediction_holds"] = bool(ok)
    with open(os.path.join(a.out, "check_twin.json"), "w") as f:
        json.dump(res, f, indent=1)
    with open(os.path.join(a.out, "summary.txt"), "w") as f:
        f.write(json.dumps(res))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    nz = dev > 0
    ax[0].hist(np.log10(dev[nz]), bins=60, color=fs.PAL["blue"], histtype="step", lw=1.5)
    ax[0].set_xlabel(r"$\log_{10}|z_{\rm libm} - z_{\rm twin}|$")
    ax[0].set_ylabel("number of deviates")
    ax[0].text(0.03, 0.95, f"{int(nz.sum())} of {dev.size} differ\n"
               f"AGM: {agm_bitdiff} differ (bitwise)", transform=ax[0].transAxes,
               va="top", fontsize=9)
    ax[1].loglog(Ls[nz], dev[nz], ".", ms=2, color=fs.PAL["red"])
    xx = np.logspace(np.log10(Ls[nz].min()), 1, 50)
    ax[1].loglog(xx, 3e-14 / np.sqrt(2 * xx), **fs.GUIDE,
                 label=r"$3\times10^{-14}/\sqrt{2L}$")
    ax[1].set_xlabel(r"$L = -\ln(s\,2^{-52})$")
    ax[1].set_ylabel(r"$|z_{\rm libm} - z_{\rm twin}|$")
    ax[1].legend(loc="upper right")
    fig.tight_layout()
    fs.save(fig, os.path.join(a.out, "fig_check_twin"))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
