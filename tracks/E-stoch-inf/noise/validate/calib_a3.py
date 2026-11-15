#!/usr/bin/env python3
"""T-N6: calibration of the A3 decisions on correct output (after T-N3 was refuted).

    python3 calib_a3.py --out DIR [--seeds 2000]

For the base case of the unit test (frozen, tanh, N = 64), draws the amplitudes of
degrees of freedom 0 and 1 for many seeds and makes exactly the A3 decisions of
validate_noise.py (KS of |w|^2 against Exp(1), KS of arg w against uniform, z of the
fourth moment from 1000 modes; for c0 to c3 at cycles 100, 101, 200, 300; w = alpha on the
selection |G| > 1e-3 max |G|). Reports (i) the fraction of single decisions with p below
1e-2, 1e-3, 1e-4 (calibration of one decision) and (ii) the fraction of seeds in which
at least one A3 decision has p < 1e-4 (the family-wise false-alarm rate of A3 per
validation). Writes calib_a3.json, summary.txt, fig_calib_a3.png/pdf.
"""
import argparse
import json
import os
import sys

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "ref"))
import noise_ref as nr                                    # noqa: E402
import philox_ref as pr                                   # noqa: E402
import athenak_io as aio                                  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seeds", type=int, default=2000)
    a = ap.parse_args()
    p = nr.default_params()
    lat = nr.Lattice(p["N"], p["L"], p["nmax2"])
    fields = []
    for cyc in p["cycles"]:
        for c in range(4):
            G = nr.transfer(lat, c, cyc, p)
            sel = np.abs(G) > 1e-3 * np.abs(G).max()
            fields.append((c, cyc, sel, nr.TEST_DOF[c]))
    single = []
    fam_min = []
    ndec = None
    for s in range(a.seeds):
        seed = 700000 + 7919 * s
        al = {d: pr.mode_alpha(seed, d, 0, lat.n) for d in (0, 1)}
        ps = []
        for c, cyc, sel, d in fields:
            w = al[d][sel]                     # G^c / G^c = 1: w = alpha on the selection
            m2 = np.abs(w)**2
            ps.append(stats.kstest(m2, "expon").pvalue)
            ps.append(stats.kstest(np.angle(w) / (2 * np.pi) + 0.5, "uniform").pvalue)
            if m2.size >= 1000:
                z4 = (np.mean(m2**2) - 2.0) / np.sqrt(20.0 / m2.size)
                ps.append(2 * stats.norm.sf(abs(z4)))
        ndec = len(ps)
        single += ps
        fam_min.append(min(ps))
    single = np.array(single)
    fam_min = np.array(fam_min)
    res = dict(seeds=a.seeds, decisions_per_validation=ndec,
               single_frac_below={str(t): float((single < t).mean()) for t in (1e-2, 1e-3, 1e-4)},
               family_rate_p_below_1e-4=float((fam_min < 1e-4).mean()),
               family_rate_p_below_1e-3_over_D=float((fam_min < 1e-3 / ndec).mean()),
               family_rate_binomial_sd=float(np.sqrt((fam_min < 1e-4).mean() *
                                                     (1 - (fam_min < 1e-4).mean()) / a.seeds)))
    with open(os.path.join(a.out, "calib_a3.json"), "w") as f:
        json.dump(res, f, indent=1)
    with open(os.path.join(a.out, "summary.txt"), "w") as f:
        f.write(json.dumps(res) + "\n")
    print(json.dumps(res, indent=1))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, os.path.join(aio.REPO, "python"))
    from nrpic import figstyle as fs
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    bins = np.logspace(-6, 0, 31)
    ax[0].hist(single, bins=bins, histtype="step", lw=1.5, color=fs.PAL["blue"],
               label="single decisions")
    ax[0].plot(bins[:-1], single.size * np.diff(bins), **fs.GUIDE, label="uniform p")
    ax[0].set_xscale("log")
    ax[0].set_yscale("log")
    ax[0].set_xlabel("p")
    ax[0].set_ylabel("count")
    ax[0].legend(loc="upper left", fontsize=8)
    srt = np.sort(fam_min)
    ax[1].loglog(srt, np.arange(1, srt.size + 1) / srt.size, color=fs.PAL["red"],
                 label=f"min p of {ndec} A3 decisions")
    xx = np.logspace(-6, 0, 50)
    ax[1].loglog(xx, np.minimum(1, ndec * xx), **fs.GUIDE, label=r"$D\,p$ (independent)")
    ax[1].axvline(1e-4, **fs.MASK_LINE)
    ax[1].set_xlabel("p")
    ax[1].set_ylabel("fraction of validations below p")
    ax[1].legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    fs.save(fig, os.path.join(a.out, "fig_calib_a3"))


if __name__ == "__main__":
    main()
