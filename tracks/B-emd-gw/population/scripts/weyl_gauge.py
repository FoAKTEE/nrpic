#!/usr/bin/env python3
"""Gauge-invariant reading of the late strain of the population box (decision 0050 item 2a).

Predictions W0-W3: population/JOURNAL.md, entry 2026-11-27 19:37 PST (written before this script ran).

Both 128^3 members of the gauge leg evolve the lapse with the same condition along the normal
from the same initial slice, so their slices are the same and only the spatial coordinates
differ. A scalar of the slice's geometry averaged over proper volume is then the same number in
both, up to truncation. Measure: I_B = <B_ij B^ij>_V, B_ij the magnetic part of the Weyl tensor
(gw_diag/gwdiag/weyl.py, the reader of the wave tests), computed from the trace-free part of K_ij
(the trace adds an antisymmetric term that the symmetrization removes). Slice checks: the
proper volume V, <K>_V and <alpha>_V. Secondary: the coordinate band power |n| <= 8 of B_ij and
the track's band strain (analyze_gr._dump_job, corrected spectra, compare_legs.band_rms2).

  weyl_gauge.py test --out DIR            W0: analytic plane wave, before and after a map
  weyl_gauge.py data --out DIR [--np 4]   W1-W3 from the dumps of the three members
  weyl_gauge.py fig --out DIR             figure weyl_gauge.png from both JSON files
"""
import argparse
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(PKG, "..", "gw_diag"))
sys.path.insert(0, os.path.join(ROOT, "python"))
from gwdiag import binio, readers, tt, weyl          # noqa: E402
from gwdiag.grid import Grid                          # noqa: E402

S = "/data/haiyangw/nrpic/scratch/B-emd-gw"
RUNS = {"zs128": f"{S}/B-20261123-014847-f295ab4/bin/pop.z4cd.%05d.bin",
        "gd128": f"{S}/B-20261124-210431-6bf48af/bin/pop.z4cd.%05d.bin",
        "gd256": f"{S}/B-20261126-105021-6343c13/bin/pop.z4cd.%05d.bin"}
# code time t of each epoch; a = (1 + t/2)^2; 128^3 dumps every 0.25, 256^3 every 1.0
T_EPOCH = [8.0, 12.0, 14.0, 16.0, 18.0, 20.0, 21.0]
T_256 = [12.0, 14.0, 18.0, 21.0]
NBAND = 8


def scale(t):
    return (1.0 + 0.5 * t) ** 2


def band_power(F, grid, nmax=NBAND):
    """sum over 1 <= |n| <= nmax of |F|^2 (rfft coefficients of a (3, 3, ...) field)."""
    k = grid.kvec(real=True)
    kk = np.sqrt((k ** 2).sum(0))
    nk = np.rint(kk / (2 * np.pi / grid.L[0])).astype(int)
    w = np.asarray(grid.rfft_weights())
    ok = (~grid.nyquist_mask(real=True)) & (nk >= 1) & (nk <= nmax)
    p = (np.abs(F) ** 2).sum((0, 1)) * w
    return float(p[ok].sum()) / float(np.prod(grid.n)) ** 2


def invariants(gamma, Ktf, trK, alpha, grid, order=4):
    detg = tt.det3(gamma)
    sq = np.sqrt(detg)
    _, B = weyl.electric_magnetic(gamma, Ktf, grid, order=order)
    gi = tt.inv3(gamma)
    Bup = np.einsum("ia...,jb...,ab...->ij...", gi, gi, B)
    B2 = np.einsum("ij...,ij...->...", B, Bup)
    dV = float(np.prod(grid.dx))
    W = sq.sum()
    out = {"V": float(W * dV), "I_B": float((sq * B2).sum() / W),
           "K_V": float((sq * trK).sum() / W), "alpha_V": float((sq * alpha).sum() / W),
           "B2_p99": float(np.percentile(B2, 99.0)), "B2_max": float(B2.max())}
    out["B_band"] = band_power(tt.tensor_rfft(B), grid)
    return out


# ------------------------------------------------------------------------------- test W0
def analytic(n=64, Lb=1.0, A=1e-3, nwave=2, eps=0.0, order=4):
    grid = Grid((n, n, n), (Lb, Lb, Lb), (0.0, 0.0, 0.0))
    c = (np.arange(n) + 0.5) * Lb / n
    Z, Y, X = np.meshgrid(c, c, c, indexing="ij")
    k = 2 * np.pi * nwave / Lb
    q = 2 * np.pi / Lb
    s = eps / q
    # x = y + xi(y): xi^x = s sin(q y), xi^y = s sin(q z), xi^z = s sin(q x)
    zx = Z + s * np.sin(q * X)          # x^z as a function of the new coordinates
    J = np.zeros((3, 3) + X.shape)       # J[i, a] = d x^i / d y^a
    for i in range(3):
        J[i, i] = 1.0
    J[0, 1] = eps * np.cos(q * Y)
    J[1, 2] = eps * np.cos(q * Z)
    J[2, 0] = eps * np.cos(q * X)
    g0 = np.zeros((3, 3) + X.shape)
    K0 = np.zeros((3, 3) + X.shape)
    for i in range(3):
        g0[i, i] = 1.0
    g0[0, 0] += A * np.cos(k * zx)
    g0[1, 1] -= A * np.cos(k * zx)
    K0[0, 0] = -(A * k / 2) * np.sin(k * zx)
    K0[1, 1] = +(A * k / 2) * np.sin(k * zx)
    gamma = np.einsum("ia...,jb...,ij...->ab...", J, J, g0)
    K = np.einsum("ia...,jb...,ij...->ab...", J, J, K0)
    gi = tt.inv3(gamma)
    trK = np.einsum("ij...,ij...->...", gi, K)
    Ktf = K - gamma * trK / 3.0
    out = invariants(gamma, Ktf, trK, np.ones_like(trK), grid, order=order)
    h = gamma - np.eye(3)[:, :, None, None, None]
    out["h_band"] = band_power(tt.tt_project_fourier(h, grid), grid)
    out["I_B_exact"] = A ** 2 * k ** 4 / 4.0
    out.update({"n": n, "eps": eps, "A": A, "k": k})
    return out


def cmd_test(args):
    rows = []
    for n in (32, 64):
        for eps in (0.0, 0.03, 0.3):
            t0 = time.time()
            r = analytic(n=n, eps=eps)
            r["wall_s"] = time.time() - t0
            rows.append(r)
            print(f"n={n} eps={eps}: I_B={r['I_B']:.6e} (exact {r['I_B_exact']:.6e}) "
                  f"V={r['V']:.9f} h_band={r['h_band']:.4e} B_band={r['B_band']:.4e} "
                  f"({r['wall_s']:.1f} s)", flush=True)
    ref = {n: next(r for r in rows if r["n"] == n and r["eps"] == 0.0) for n in (32, 64)}
    for r in rows:
        b = ref[r["n"]]
        r["dI_B_rel"] = r["I_B"] / b["I_B"] - 1.0
        r["dV_rel"] = r["V"] / b["V"] - 1.0
        r["dh_band_rel"] = r["h_band"] / b["h_band"] - 1.0
        r["I_B_vs_exact"] = r["I_B"] / r["I_B_exact"] - 1.0
    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "weyl_test.json"), "w") as f:
        json.dump(rows, f, indent=1)
    for r in rows:
        print(f"n={r['n']} eps={r['eps']}: I_B/exact-1={r['I_B_vs_exact']:+.2e} "
              f"dI_B={r['dI_B_rel']:+.2e} dV={r['dV_rel']:+.2e} dh_band={r['dh_band_rel']:+.3e}")


# ------------------------------------------------------------------------------- data W1-W3
def dump_job(job):
    run, t = job
    step = 0.25 if run.endswith("128") else 1.0
    idx = int(round(t / step))
    path = RUNS[run] % idx
    t0 = time.time()
    d = binio.read_bin(path, strip_prefix=True)
    grid = d["grid"]
    chi, gt, At, trK, alpha, beta = readers.z4c_tensors(d)
    p = d.get("chi_psi_power", -4.0)
    psi4 = chi ** (4.0 / p)
    gamma = psi4 * gt
    Ktf = psi4 * At
    row = {"run": run, "file": path, "t": float(d["time"]), "a": float(scale(float(d["time"]))),
           "n": int(grid.n[0])}
    row.update(invariants(gamma, Ktf, trK, alpha, grid))
    row["beta_rms"] = float(np.sqrt((beta ** 2).sum(0).mean()))
    del d, chi, gt, At, gamma, Ktf
    if row["n"] == 128:
        import analyze_gr as ag
        import compare_legs as cl
        r2 = ag._dump_job((path, None, True))
        row["band_cor"] = cl.band_rms2(r2["spec_cor"], NBAND)
        row["band_raw"] = cl.band_rms2(r2["spec_raw"], NBAND)
    row["wall_s"] = time.time() - t0
    print(f"{run} t={row['t']:.2f} a={row['a']:.1f} I_B={row['I_B']:.4e} V={row['V']:.6e} "
          f"K_V={row['K_V']:.6e} ({row['wall_s']:.0f} s)", flush=True)
    return row


def cmd_data(args):
    jobs = [(r, t) for t in T_EPOCH for r in ("zs128", "gd128")]
    big = [("gd256", t) for t in T_256]
    rows = []
    with Pool(args.np) as pool:
        res_small = pool.map_async(dump_job, jobs, chunksize=1)
        with Pool(args.np_big) as pool2:
            rows += pool2.map(dump_job, big, chunksize=1)
        rows += res_small.get()
    os.makedirs(args.out, exist_ok=True)
    by = {(r["run"], round(r["t"], 2)): r for r in rows}
    table = []
    for t in T_EPOCH:
        zs, gd = by[("zs128", t)], by[("gd128", t)]
        e = {"t": t, "a": scale(t),
             "R_B": gd["I_B"] / zs["I_B"],
             "R_V": gd["V"] / zs["V"], "R_K": gd["K_V"] / zs["K_V"],
             "R_alpha": gd["alpha_V"] / zs["alpha_V"],
             "R_Bband": gd["B_band"] / zs["B_band"],
             "R_band_cor": np.sqrt(gd["band_cor"] / zs["band_cor"]),
             "R_band_raw": np.sqrt(gd["band_raw"] / zs["band_raw"])}
        if ("gd256", t) in by:
            b = by[("gd256", t)]
            e["M_B"] = b["I_B"] / gd["I_B"]
            e["M_V"] = b["V"] / gd["V"]
            e["M_K"] = b["K_V"] / gd["K_V"]
        table.append(e)
        print(json.dumps({k: (round(v, 5) if isinstance(v, float) else v) for k, v in e.items()}))
    with open(os.path.join(args.out, "weyl_gauge.json"), "w") as f:
        json.dump({"rows": rows, "table": table}, f, indent=1, default=float)


# ------------------------------------------------------------------------------- figure
def cmd_fig(args):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.apply() if hasattr(fs, "apply") else None
    test = json.load(open(os.path.join(args.out, "weyl_test.json")))
    data = json.load(open(os.path.join(args.out, "weyl_gauge.json")))
    tab = data["table"]
    fig, ax = plt.subplots(2, 2, figsize=(9.0, 7.0))
    # (a) analytic test
    a0 = ax[0, 0]
    for n, mk in ((32, "o"), (64, "s")):
        rr = [r for r in test if r["n"] == n and r["eps"] > 0]
        e = [r["eps"] for r in rr]
        a0.plot(e, [abs(r["dI_B_rel"]) for r in rr], mk + "-", label=f"$I_B$, $N={n}$")
        a0.plot(e, [abs(r["dV_rel"]) + 1e-17 for r in rr], mk + ":", label=f"$V$, $N={n}$")
        a0.plot(e, [abs(r["dh_band_rel"]) for r in rr], mk + "--", label=f"TT band, $N={n}$")
    a0.axhline(1e-3, color="0.5", lw=0.8)
    a0.set_xscale("log"); a0.set_yscale("log")
    a0.set_xlabel(r"map amplitude $\max|\partial\xi|$")
    a0.set_ylabel("relative change under the map")
    a0.set_title("(a) W0: analytic wave, coordinates mapped", fontsize=9)
    a0.legend(fontsize=6.5, ncol=2)
    # (b) gauge ratios against a
    a1 = ax[0, 1]
    A = [e["a"] for e in tab]
    a1.plot(A, [e["R_band_cor"] for e in tab], "o-", label="band strain, coordinate (W3)")
    a1.plot(A, [e["R_B"] for e in tab], "s-", label=r"$I_B=\langle B_{ij}B^{ij}\rangle_V$ (W2)")
    a1.plot(A, [np.sqrt(e["R_Bband"]) for e in tab], "^--", label=r"$B_{ij}$ band $|n|\le 8$, rms")
    am = [e["a"] for e in tab if "M_B" in e]
    a1.plot(am, [e["M_B"] for e in tab if "M_B" in e], "kd:", label=r"$I_B$: $256^3/128^3$, Gamma driver")
    a1.axhspan(0.95, 1.05, color="0.9", zorder=0)
    a1.axhline(1.0, color="0.5", lw=0.8)
    a1.set_xlabel("$a$"); a1.set_ylabel("Gamma driver / zero shift ($128^3$)")
    a1.set_title("(b) gauge ratio of each measure", fontsize=9)
    a1.legend(fontsize=6.5)
    # (c) slice checks
    a2 = ax[1, 0]
    a2.plot(A, [abs(e["R_V"] - 1) for e in tab], "o-", label="proper volume $V$")
    a2.plot(A, [abs(e["R_K"] - 1) for e in tab], "s-", label=r"$\langle K\rangle_V$")
    a2.plot(A, [abs(e["R_alpha"] - 1) for e in tab], "^-", label=r"$\langle\alpha\rangle_V$")
    a2.plot(am, [abs(e["M_K"] - 1) for e in tab if "M_K" in e], "kd:", label=r"$\langle K\rangle_V$ mesh, Gamma driver")
    a2.axhline(1e-3, color="0.5", lw=0.8)
    a2.set_yscale("log"); a2.set_xlabel("$a$"); a2.set_ylabel("|gauge ratio - 1|")
    a2.set_title("(c) W1: are the slices the same?", fontsize=9)
    a2.legend(fontsize=6.5)
    # (d) I_B itself
    a3 = ax[1, 1]
    for run, mk in (("zs128", "o-"), ("gd128", "s-"), ("gd256", "kd:")):
        rr = sorted([r for r in data["rows"] if r["run"] == run], key=lambda r: r["a"])
        a3.plot([r["a"] for r in rr], [r["I_B"] for r in rr], mk, label=run)
    a3.set_yscale("log"); a3.set_xlabel("$a$"); a3.set_ylabel(r"$I_B$ (code units)")
    a3.set_title(r"(d) $\langle B_{ij}B^{ij}\rangle_V$ of the three members", fontsize=9)
    a3.legend(fontsize=7)
    fig.tight_layout()
    fn = os.path.join(args.out, "weyl_gauge.png")
    fig.savefig(fn, dpi=150)
    print(fn)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["test", "data", "fig"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--np", type=int, default=3)
    ap.add_argument("--np-big", type=int, default=2)
    args = ap.parse_args()
    {"test": cmd_test, "data": cmd_data, "fig": cmd_fig}[args.mode](args)


if __name__ == "__main__":
    main()
