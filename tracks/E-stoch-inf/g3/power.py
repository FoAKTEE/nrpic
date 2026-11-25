"""Power estimate for the G3 tail statistic (SCOPE 4d): how many 128^3 seeds are needed.

The estimator of SCOPE 4d is the exceedance fraction F_pm(nu) of the standardized lattice curvature
perturbation x = R / sigma_lin over the cells of one box at N_f, averaged over seeds. Its scatter
from seed to seed is set by how many effectively independent regions a box holds, which depends on
the shape of the spectrum. This script takes the linear spectrum of the 128^3 USR box at N_f from a
lockstep record (`.modes` of a 128^3 USR run, nmax2 = 1024), draws Gaussian random fields with that
spectrum on the 128^3 lattice (every injected mode |n|^2 <= nmax2, window W at the record time,
random complex amplitudes), and measures per box F_+(nu), F_-(nu) for nu = 2, 3, 4, the skewness and
the excess kurtosis. From the box-to-box standard deviation SD it gives the number of seeds S for
  (a) a 3-standard-error detection of a difference Delta in F(3) (S = (3 SD / Delta)^2), for the
      difference between the one-patch delta-N tail and the Gaussian one;
  (b) a relative standard error of 10 per cent on F(3) and on F(4);
  (c) a standard error of 0.01 on the skewness.
The scatter of a Gaussian field is used for the non-Gaussian lattice field [JUDGEMENT: corrections
to the estimator variance are of the order of the skewness, a few per cent].

Usage: power.py OUTDIR --modes <record .modes> [--n 128] [--boxes 400] [--seed 7]
       [--delta3 2.2e-4] [--cost 0.035]
Writes OUTDIR/power.json and OUTDIR/fig_power.{pdf,png}.
"""
import argparse
import json
import os
import sys

import numpy as np
from scipy import fft as sfft
from scipy.stats import norm

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.join(HERE, "..", "repro", "figs", "figures")
sys.path.insert(0, FIGDIR)
import figlib as fl  # noqa: E402
import figstyle as fs  # noqa: E402

NUS = (2.0, 3.0, 4.0)


def amplitude_grid(md, n):
    """|W_n R_n| L^-3/2 on the rfft grid of an n^3 lattice, zero outside the injected band."""
    k1 = sfft.fftfreq(n, 1.0 / n)
    kz = sfft.rfftfreq(n, 1.0 / n)
    n2 = (k1[:, None, None] ** 2 + k1[None, :, None] ** 2 + kz[None, None, :] ** 2).astype(np.int64)
    nmax2 = int(md["n2"].max())
    lut = np.zeros(nmax2 + 1)
    w = fl.window(np.sqrt(md["n2"].astype(float)), md["a"], md["H"])
    lut[md["n2"]] = np.abs(w * md["R"]) * fl.L_BOX ** -1.5
    amp = np.where((n2 >= 1) & (n2 <= nmax2), lut[np.minimum(n2, nmax2)], 0.0)
    return amp, n2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--modes", required=True)
    ap.add_argument("--n", type=int, default=128)
    ap.add_argument("--boxes", type=int, default=400)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--delta3", type=float, default=2.2e-4,
                    help="difference of F_+(3) between the delta-N tail and the Gaussian one")
    ap.add_argument("--cost", type=float, default=0.035, help="card-hours per 128^3 seed")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    md = fl.read_modes_file(a.modes)
    n = a.n
    amp, n2 = amplitude_grid(md, n)
    # sigma_lin of the lattice field: sum over all modes of the full grid of |c_n|^2;
    # the rfft grid counts the kz > 0 half twice, kz = 0 and kz = n/2 planes once
    wgt = np.full(amp.shape, 2.0)
    wgt[:, :, 0] = 1.0
    if n % 2 == 0:
        wgt[:, :, -1] = 1.0
    var_lin = float(np.sum(wgt * amp ** 2))
    sig_lin = np.sqrt(var_lin)
    # white noise of unit variance -> rfftn has per-mode variance n^3; field = irfftn(F amp) n^3/... :
    # x = irfftn(F * amp) * n^1.5 has per-mode amplitude variance amp^2, i.e. variance var_lin
    rng = np.random.default_rng(a.seed)
    rows = []
    for b in range(a.boxes):
        white = rng.standard_normal((n, n, n))
        F = sfft.rfftn(white, workers=2)
        x = sfft.irfftn(F * amp, s=(n, n, n), workers=2) * n ** 1.5
        x = x - x.mean()
        z = x / sig_lin
        r = {"var_ratio": float(np.var(x) / var_lin)}
        for nu in NUS:
            r[f"Fp{nu:g}"] = float(np.mean(z > nu))
            r[f"Fm{nu:g}"] = float(np.mean(z < -nu))
        zc = z - z.mean()
        v = np.mean(zc ** 2)
        r["skew"] = float(np.mean(zc ** 3) / v ** 1.5)
        r["exkurt"] = float(np.mean(zc ** 4) / v ** 2 - 3.0)
        rows.append(r)
        if b % 50 == 0:
            print(b, r, flush=True)
    keys = list(rows[0].keys())
    arr = {k: np.array([r[k] for r in rows]) for k in keys}
    summ = {k: dict(mean=float(arr[k].mean()), sd=float(arr[k].std(ddof=1)),
                    se_mean=float(arr[k].std(ddof=1) / np.sqrt(len(rows)))) for k in keys}
    gauss = {f"{nu:g}": float(norm.sf(nu)) for nu in NUS}
    sd3 = summ["Fp3"]["sd"]
    sd4 = summ["Fp4"]["sd"]
    seeds = {
        "a_detect_delta3_at_3se": float((3.0 * sd3 / a.delta3) ** 2),
        "b_rel10pct_F3": float((sd3 / (0.1 * gauss["3"])) ** 2),
        "b_rel10pct_F4": float((sd4 / (0.1 * gauss["4"])) ** 2),
        "c_skew_se_0.01": float((summ["skew"]["sd"] / 0.01) ** 2),
        "n_eff_cells_F3": float(gauss["3"] * (1 - gauss["3"]) / sd3 ** 2),
    }
    out = dict(modes=a.modes, n=n, nmax2=int(md["n2"].max()), record_time=md["time"],
               sigma_lin=sig_lin, var_lin=var_lin, boxes=a.boxes, seed=a.seed, gaussian=gauss,
               summary=summ, seeds_needed=seeds, delta3=a.delta3, cost_per_seed=a.cost,
               card_hours={k: v * a.cost for k, v in seeds.items() if k != "n_eff_cells_F3"})
    with open(os.path.join(a.out, "power.json"), "w") as fp:
        json.dump(out, fp, indent=1)
    print(json.dumps({k: out[k] for k in ("sigma_lin", "gaussian", "seeds_needed", "card_hours")},
                     indent=1))
    # figure: box-to-box spread of F_+(nu) and the seed count against the precision asked
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    ax = axes[0]
    for i, nu in enumerate(NUS):
        v = arr[f"Fp{nu:g}"]
        ax.hist(np.log10(np.maximum(v, 0.5 / n ** 3)), bins=30, histtype="step", lw=1.5,
                color=fs.SERIES[i], label=fr"$\nu={nu:g}$")
        ax.axvline(np.log10(gauss[f"{nu:g}"]), color=fs.SERIES[i], ls="--", lw=1.0)
    ax.set_xlabel(r"$\log_{10} F_+(\nu)$ per $128^3$ box")
    ax.set_ylabel("boxes")
    ax.legend(fontsize=7, frameon=False)
    ax = axes[1]
    S = np.logspace(0, 4, 100)
    for i, nu in enumerate(NUS):
        sd = summ[f"Fp{nu:g}"]["sd"]
        ax.loglog(S, sd / np.sqrt(S) / gauss[f"{nu:g}"], color=fs.SERIES[i], label=fr"$\nu={nu:g}$")
    ax.axhline(0.1, **fs.GUIDE)
    ax.axhline(a.delta3 / gauss["3"] / 3.0, color="grey", ls=":", lw=1.5)
    ax.set_xlabel("seeds $S$")
    ax.set_ylabel(r"relative standard error of $F_+(\nu)$")
    ax.legend(fontsize=7, frameon=False)
    fig.tight_layout()
    out["figures"] = fs.save(fig, os.path.join(a.out, "fig_power"))


if __name__ == "__main__":
    main()
