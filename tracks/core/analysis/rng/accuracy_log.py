#!/usr/bin/env python3
"""Accuracy of the logarithm used by the normal draw (NegLog52 in utils/rng.hpp,
neg_log52 in nrpic/rng.py): -ln(s 2^-52) from ten steps of the arithmetic-geometric
mean, against mpmath with 200 bits, for integers s spread over [2, 2^52): the smallest
and largest values, values next to 2^52, and values uniform in ln s. Also the number of
steps after which the result no longer changes, and the effect of the error on a
normal deviate z = v sqrt(2 L / s).

Usage: accuracy_log.py [number of values = 200000]   (writes accuracy_log.json and
fig_rng_log.png in the current directory)
"""
import json
import os
import sys

import mpmath as mp
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))
from nrpic import rng  # noqa: E402
from nrpic import figstyle  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def agm_steps(s, nit):
    a = np.ones(s.shape)
    b = s.astype(np.float64) * 2.0**-82
    for _ in range(nit):
        a, b = 0.5 * (a + b), np.sqrt(a * b)
    return float.fromhex("0x1.921fb54442d18p+0") / a - float.fromhex("0x1.62e42fefa39efp+4")


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 200000
    mp.mp.prec = 200
    gen = np.random.default_rng(11)
    s = np.concatenate([
        np.exp(gen.uniform(np.log(2.0), 52 * np.log(2.0), n)).astype(np.int64),
        np.arange(2, 2002, 2, dtype=np.int64),                       # smallest values
        (1 << 52) - np.arange(2, 2002, 2, dtype=np.int64),           # next to 2^52
        (1 << 52) - (np.int64(1) << np.arange(2, 52, dtype=np.int64)),
    ])
    s = s[(s >= 2) & (s < (1 << 52))]
    val = rng.neg_log52(s)
    ln2 = mp.log(2)
    ref_mp = [52 * ln2 - mp.log(int(v)) for v in s]
    err = np.array([float(mp.mpf(float(a)) - b) for a, b in zip(val, ref_mp)])
    ref = np.array([float(b) for b in ref_mp])
    # steps needed
    changed = {}
    prev = agm_steps(s, 6)
    for nit in range(7, 15):
        cur = agm_steps(s, nit)
        changed[nit] = int(np.count_nonzero(cur != prev))
        prev = cur
    # effect on a normal deviate: dz/z = dL / (2 L); absolute bound with |v| <= sqrt(s)
    rel = np.abs(err) / (2.0 * np.maximum(ref, 1e-300))
    dz = np.sqrt(2.0 * np.maximum(val, 0.0)) - np.sqrt(2.0 * ref)
    res = {
        "values": int(s.size),
        "max_abs_error": float(np.abs(err).max()),
        "max_abs_error_at_s": int(s[np.argmax(np.abs(err))]),
        "negative_before_clamp": int(np.count_nonzero(agm_steps(s, 10) < 0.0)),
        "min_value": float(val.min()),
        "values_changed_by_step": changed,
        "max_abs_error_of_radius_sqrt_2L": float(np.abs(dz).max()),
        "max_rel_error_of_radius_for_L_above_1e-6": float(rel[ref > 1e-6].max()),
    }
    res["ok"] = bool(res["max_abs_error"] < 3.0e-14 and res["min_value"] >= 0.0
                     and all(v == 0 for k, v in changed.items() if k >= 10))
    with open("accuracy_log.json", "w") as fp:
        json.dump(res, fp, indent=1)
    print(json.dumps(res, indent=1))

    figstyle.use_style()
    fig, ax = plt.subplots(1, 1, figsize=(8.0, 3.6))
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.15, top=0.95)
    ax.plot(ref, np.abs(err), ".", ms=1.5, color=figstyle.PAL["red"], rasterized=True,
            label="ten steps of the arithmetic-geometric mean")
    xx = np.logspace(-16, 1.6, 200)
    ax.plot(xx, 2.0**-53 * (xx + 32 * np.log(2.0)), label="half a unit in the last place "
            "of $L + 32\\ln 2$", **figstyle.GUIDE)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(1e-16, 50)
    ax.set_ylim(1e-18, 1e-12)
    ax.set_xlabel("$L = -\\ln(s\\,2^{-52})$")
    ax.set_ylabel("absolute error of $L$")
    ax.legend(loc="lower right")
    fig.savefig("fig_rng_log.png", dpi=200)
    sys.exit(0 if res["ok"] else 1)


if __name__ == "__main__":
    main()
