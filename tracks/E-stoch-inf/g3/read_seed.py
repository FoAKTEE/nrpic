"""Per-seed reader of the G3 statistic (SCOPE 4d.1), variable (i) R^NR only.

For each run directory it reads the last dump `<base>.sf.NNNNN.dump` (or the one given by --dump),
forms R^NR on the whole lattice exactly as `../repro/figs/figures/dumppass.py` does (the linear
extraction of ladder_lib.curvature: c[chi]/(2<chi>) + (1/4) khat_i khat_j c[gt_ij] + (H_b/Pi_b) c[phi]),
takes sigma_lin from the run's own lockstep `.modes` record of that dump (sum of |W_n R_n|^2 L^-3 over
every injected mode of the full lattice; the same function as `power.py`), and writes per seed:
sigma of R^NR, sigma_lin, the exceedance fractions F_pm(nu) of x = R^NR / sigma_lin for
nu = 2, 3, 4, 4.5, 5, skewness, excess kurtosis, and a histogram of x (bins of 0.1 on [-10, 10]).
Variable (ii), zeta, is not here yet: it needs its two processor tests first (SCOPE 4d.1).

Usage: read_seed.py OUTDIR --run LABEL:DIR [--run ...] [--base usr] [--fft-workers 2]
Writes OUTDIR/<label>.json and OUTDIR/<label>_hist.npz, OUTDIR/seeds.json, OUTDIR/fig_seeds.{pdf,png}.
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
sys.path.insert(0, HERE)
import figlib as fl  # noqa: E402
import figstyle as fs  # noqa: E402
from power import amplitude_grid  # noqa: E402

NUS = (2.0, 3.0, 4.0, 4.5, 5.0)
GPAIRS = (("gxx", 0, 0, 1.0), ("gyy", 1, 1, 1.0), ("gzz", 2, 2, 1.0),
          ("gxy", 0, 1, 2.0), ("gxz", 0, 2, 2.0), ("gyz", 1, 2, 2.0))
EDGES = np.linspace(-10.0, 10.0, 201)


def r_nr(path, workers):
    h = fl.ll.read_header(path)
    N = h["nx"][0]
    want = ["phi", "Pi", "chi", "K", "alpha"] + [g[0] for g in GPAIRS]
    _, f = fl.ll.read_dump(path, want)
    mean = {v: float(f[v].mean()) for v in ["phi", "Pi", "K", "chi", "alpha"]}
    kz = np.fft.fftfreq(N, 1.0 / N)[:, None, None]
    ky = np.fft.fftfreq(N, 1.0 / N)[None, :, None]
    kx = np.arange(N // 2 + 1, dtype=float)[None, None, :]
    k2 = kx * kx + ky * ky + kz * kz
    k2[0, 0, 0] = 1.0
    kv = (kx, ky, kz)
    hb = -mean["K"] / (3.0 * mean["alpha"])
    rf = lambda a: sfft.rfftn(a, workers=workers)  # noqa: E731
    F = rf(f["chi"]) / (2.0 * mean["chi"]) + (hb / mean["Pi"]) * rf(f["phi"])
    for name, i, j, w in GPAIRS:
        F += 0.25 * w * (kv[i] * kv[j] / k2) * rf(f[name])
    F[0, 0, 0] = 0.0
    Rx = sfft.irfftn(F, s=(N,) * 3, workers=workers)
    return Rx, h, N


def sigma_lin_of(modes_path, n):
    md = fl.read_modes_file(modes_path)
    amp, _ = amplitude_grid(md, n)
    wgt = np.full(amp.shape, 2.0)
    wgt[:, :, 0] = 1.0
    if n % 2 == 0:
        wgt[:, :, -1] = 1.0
    return float(np.sqrt(np.sum(wgt * amp ** 2))), md


def one(label, run, base, out, workers, dump=None):
    files = sorted(p for p in os.listdir(run) if p.startswith(base + ".sf.") and p.endswith(".dump"))
    name = files[-1] if dump is None else f"{base}.sf.{int(dump):05d}.dump"
    path = os.path.join(run, name)
    Rx, h, N = r_nr(path, workers)
    sig_lin, md = sigma_lin_of(path[:-len(".dump")] + ".modes", N)
    x = Rx / sig_lin
    xc = x - x.mean()
    v = float(np.mean(xc ** 2))
    rec = dict(label=label, run=run, dump=name, time=float(h["time"]), N=int(N),
               nmax2=int(md["n2"].max()), record_time=md["time"], sigma_lin=sig_lin,
               sigma_R=float(np.std(Rx)), ratio=float(np.std(Rx) / sig_lin), mean_x=float(x.mean()),
               skew=float(np.mean(xc ** 3) / v ** 1.5), exkurt=float(np.mean(xc ** 4) / v ** 2 - 3.0),
               x_max=float(x.max()), x_min=float(x.min()))
    for nu in NUS:
        rec[f"Fp{nu:g}"] = float(np.mean(x > nu))
        rec[f"Fm{nu:g}"] = float(np.mean(x < -nu))
        rec[f"Q{nu:g}"] = float(norm.sf(nu))
    hist, _ = np.histogram(x, bins=EDGES)
    np.savez(os.path.join(out, f"{label}_hist.npz"), edges=EDGES, hist=hist)
    with open(os.path.join(out, f"{label}.json"), "w") as fp:
        json.dump(rec, fp, indent=1)
    print(json.dumps({k: rec[k] for k in ("label", "time", "N", "sigma_lin", "ratio", "skew",
                                          "Fp3", "Fm3", "Fp4", "Fm4", "x_max")}), flush=True)
    return rec, hist


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--run", action="append", required=True, help="LABEL:DIR[:DUMP]")
    ap.add_argument("--base", default="usr")
    ap.add_argument("--fft-workers", type=int, default=2)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    recs, hists = [], []
    for spec in a.run:
        parts = spec.split(":")
        r, hst = one(parts[0], parts[1], a.base, a.out, a.fft_workers,
                     parts[2] if len(parts) > 2 else None)
        recs.append(r)
        hists.append(hst)
    with open(os.path.join(a.out, "seeds.json"), "w") as fp:
        json.dump(recs, fp, indent=1)
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(fs.COLUMN_WIDTH * 1.4, 3.0))
    c = 0.5 * (EDGES[1:] + EDGES[:-1])
    dx = EDGES[1] - EDGES[0]
    for i, (r, hst) in enumerate(zip(recs, hists)):
        p = hst / (hst.sum() * dx)
        m = p > 0
        ax.semilogy(c[m], p[m], ".", ms=3, color=fs.SERIES[i % len(fs.SERIES)],
                    label=f"{r['label']} ({r['N']}$^3$, t = {r['time']:.2f})")
    xx = np.linspace(-6, 6, 400)
    ax.semilogy(xx, norm.pdf(xx), **fs.GUIDE, label="Gaussian, linear variance")
    ax.set_xlim(-6.5, 6.5)
    ax.set_ylim(1e-8, 1.0)
    ax.set_xlabel(r"$\mathcal{R}^{\rm NR}/\sigma_{\rm lin}$")
    ax.set_ylabel("one-point density")
    ax.legend(fontsize=6.5, frameon=False)
    fig.tight_layout()
    fs.save(fig, os.path.join(a.out, "fig_seeds"))


if __name__ == "__main__":
    main()
