#!/usr/bin/env python3
"""Calculation B of the scope review: the G3 criteria of Claim G applied to G2's registered outputs.

Reads only raw finder summaries (column 2 time, column 3 mass; a repeated time keeps its last line) and
the registered esf_criteria.json / fp_analyse.json files named below. Imports nothing of the track's tools.
Usage: g2_analogs.py OUTDIR
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import figstyle as fs  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

S = Path("/data/haiyangw/nrpic/scratch/D-bh-dress")
RUNS = {  # card runs of G2 (g2long JOURNAL entries 3, 6, 10, 15)
    "ES-FL": ("D-20261121-203150-15f2bad", "esfl"),       # M/8, N, excision ends at 219.5 M
    "FK": ("D-20261123-022725-a553496", "esflk"),         # M/8, N, excision to the end
    "FN4": ("D-20261124-134157-b17938b", "esflk4n"),      # M/8, 4N
    "FNQ": ("D-20261124-172725-2f426b6", "esflkq"),       # M/8, N/4
    "FL16": ("D-20261124-172745-72472ed", "esfl16"),      # M/16 (level 8 +-3 M), N, to 300 M
}
CRIT = {  # registered esf_criteria readings (iii)
    "ES-FL": "D-20261123-020614-7ba5874", "FK": "D-20261125-115647-fd2f3f7",
    "FN4": "D-20261125-122827-c5735f8", "FNQ": "D-20261126-054616-a13a888",
    "FL16": "D-20261126-055158-30ae09c",
}
FP = "D-20261124-172508-c847ee4"  # converged-finder re-search (g2long entries 10, 14)
H = 5.58116e-3  # Hubble rate of the data (scope section 1)


def summary(name):
    run, base = RUNS[name]
    d = {}
    for line in open(S / run / f"{base}.horizon_summary_0.txt"):
        if line.startswith("#") or not line.strip():
            continue
        c = line.split()
        d[float(c[1])] = float(c[2])
    t = np.array(sorted(d))
    return t, np.array([d[x] for x in t])


def on_grid(name, grid):
    t, m = summary(name)
    return np.interp(grid, t, m, left=np.nan, right=np.nan)


def bins(name):
    b = json.load(open(S / CRIT[name] / "esf_criteria.json"))["iii"]["dust"]["bins"]
    return {round(x["lo"]): x["median"] for x in b if x["counted"]}


def lna(tau):
    return (2.0 / 3.0) * np.log1p(1.5 * H * np.asarray(tau))


def surrogate(x, rng):
    """Phase-randomised copy of x (same power spectrum)."""
    f = np.fft.rfft(x - x.mean())
    ph = np.exp(2j * np.pi * rng.random(f.size))
    ph[0] = 1.0
    if x.size % 2 == 0:
        ph[-1] = 1.0
    return np.fft.irfft(f * ph, n=x.size)


def boxcar(x, w):
    k = np.ones(w) / w
    return np.convolve(x, k, mode="same")


def main():
    out = Path(sys.argv[1])
    res = {}
    grid = np.arange(20.0, 399.75, 0.5)
    M = {n: on_grid(n, grid) for n in ("FK", "FN4", "FNQ", "ES-FL")}
    g300 = grid[grid <= 299.0]
    M16 = on_grid("FL16", g300)

    # ---- B1: G3-G4 analog, ratio of window rms one factor coarser (N/4, N, 4N)
    b1 = []
    for lo in range(50, 400, 50):
        w = (grid >= lo) & (grid < lo + 50)
        a = M["FNQ"][w] - M["FK"][w]
        b = M["FK"][w] - M["FN4"][w]
        rms_a, rms_b = np.sqrt(np.nanmean(a ** 2)), np.sqrt(np.nanmean(b ** 2))
        b1.append(dict(window=[lo, lo + 50], rms_Nq_minus_N=rms_a, rms_N_minus_4N=rms_b, ratio=rms_a / rms_b,
                       std_ratio=np.nanstd(a) / np.nanstd(b), inside_1p4_3=bool(1.4 <= rms_a / rms_b <= 3.0),
                       inside_1p2_4=bool(1.2 <= rms_a / rms_b <= 4.0)))
    res["B1"] = dict(windows=b1, n_outside_1p4_3=sum(not x["inside_1p4_3"] for x in b1),
                     n_outside_1p2_4=sum(not x["inside_1p2_4"] for x in b1))

    # ---- noise model for one member at N (from FK - FN4) and the mesh correlation (FL16 - ES-FL)
    n_fk4 = M["FK"] - M["FN4"]
    sigma_N = np.nanstd(n_fk4) / np.sqrt(1.25)
    hp = n_fk4 - boxcar(n_fk4, 101)              # high-pass: 50 M running mean removed
    sigma_N_hp = np.nanstd(hp[60:-60]) / np.sqrt(1.25)
    d16 = (M16 - M16[0]) - (M["ES-FL"][: g300.size] - M["ES-FL"][0])   # Delta M_16 - Delta M_8 from 20 M
    d16_hp = d16 - boxcar(d16, 101)
    var_mesh_hp = np.nanvar(d16_hp[60:-60])
    rho = float(np.clip(1.0 - var_mesh_hp / (2 * sigma_N_hp ** 2), 0.0, 0.95))
    w = (g300 >= 250) & (g300 <= 299)
    res["noise"] = dict(sigma_N_full=float(sigma_N), sigma_N_highpass=float(sigma_N_hp),
                        mesh_diff_highpass_std=float(np.sqrt(var_mesh_hp)), rho_mesh=rho,
                        D16_8_mean_250_299=float(np.nanmean(d16[w])), D16_8_env_20_299=float(np.nanmax(np.abs(d16))))

    # ---- B2: Monte Carlo power of G3-G3 as written, and of a mean-based alternative
    rng = np.random.default_rng(20261127)
    base = np.nan_to_num(hp - np.nanmean(hp)) / np.sqrt(1.25)  # one N member, high-pass part
    full = np.nan_to_num(n_fk4 - np.nanmean(n_fk4)) / np.sqrt(1.25)
    A16 = res["noise"]["D16_8_mean_250_299"]
    ramp = np.clip((grid - 20.0) / 130.0, 0.0, 1.0)
    wins = [(lo, lo + 50) for lo in range(100, 400, 50)]
    b2 = []
    for p in (1.0, 2.0):
        h = {8: 1 / 8, 12: 1 / 12, 16: 1 / 16}
        c = A16 / (h[16] ** p - h[8] ** p)
        for amp in (0.5, 1.0, 2.0, 4.0):
            for noise_kind, src in (("highpass", base), ("full", full)):
                npass, npass_mean, ratios = 0, 0, []
                nmc = 1000
                for _ in range(nmc):
                    com = surrogate(src, rng)
                    nz = {k: np.sqrt(rho) * com + np.sqrt(1 - rho) * surrogate(src, rng) for k in h}
                    dm = {k: amp * c * h[k] ** p * ramp + nz[k] - nz[k][0] for k in h}
                    D812, D1216 = dm[8] - dm[12], dm[12] - dm[16]
                    ok, okm = True, 0
                    for lo, hi in wins:
                        s = (grid >= lo) & (grid < hi)
                        e1, e2 = np.max(np.abs(D812[s])), np.max(np.abs(D1216[s]))
                        r = e1 / e2
                        ratios.append(r)
                        ok &= (e1 > e2) and (1.5 <= r <= 8.0)
                        m1, m2 = np.mean(D812[s]), np.mean(D1216[s])
                        okm += int(np.sign(m1) == np.sign(m2) and abs(m1) > abs(m2))
                    npass += ok
                    npass_mean += okm >= 5
                b2.append(dict(p=p, amp=amp, noise=noise_kind, P_pass_as_written=npass / nmc,
                               P_pass_mean_ordered_5of6=npass_mean / nmc,
                               ratio_median=float(np.median(ratios)),
                               ratio_q10_q90=[float(np.quantile(ratios, 0.1)), float(np.quantile(ratios, 0.9))],
                               det_D812_late=float(amp * c * (h[8] ** p - h[12] ** p)),
                               det_D1216_late=float(amp * c * (h[12] ** p - h[16] ** p))))
    res["B2"] = b2

    # ---- B3: e_8 - e_16 per 10 M bin of tau_rem (excision on in both before tau_rem ~ 285 M)
    e = {n: bins(n) for n in CRIT}
    common = sorted(k for k in e["ES-FL"] if k in e["FL16"] and 50 <= k < 280)
    d = np.array([e["ES-FL"][k] - e["FL16"][k] for k in common])
    res["B3"] = dict(bins=common, e8=[e["ES-FL"][k] for k in common], e16=[e["FL16"][k] for k in common],
                     diff_mean=float(d.mean()), diff_std=float(d.std(ddof=1)), frac_e8_gt_e16=float(np.mean(d > 0)),
                     frac_abs8_gt_abs16=float(np.mean([abs(e["ES-FL"][k]) > abs(e["FL16"][k]) for k in common])))
    # particle legs: window means of e over 50 M of tau_rem
    pm = []
    for lo in range(50, 500, 50):
        row = dict(window=[lo, lo + 50])
        for n in ("FNQ", "FK", "FN4"):
            v = [e[n][k] for k in e[n] if lo <= k < lo + 50]
            row[n] = float(np.mean(v)) if v else None
        if all(row[n] is not None for n in ("FNQ", "FK", "FN4")):
            row["max_pair_diff"] = max(row["FNQ"], row["FK"], row["FN4"]) - min(row["FNQ"], row["FK"], row["FN4"])
        pm.append(row)
    res["B3_particle_window_means"] = pm

    # ---- B4: model test with a known defect (ES-FL loses excision at 219.5 M; FK keeps it)
    b4 = {}
    for n in ("ES-FL", "FK", "FN4", "FNQ"):
        ks = sorted(k for k in e[n] if k >= 50)
        tau = np.array(ks) + 5.0
        y = np.log1p(np.array([e[n][k] for k in ks]))
        x = lna(tau)
        fixed = []
        x0 = lna(50.0)
        j = 0
        while x0 + 0.1 * (j + 1) <= x[-1] + 1e-9:
            s = (x >= x0 + 0.1 * j) & (x < x0 + 0.1 * (j + 1))
            if s.sum() >= 2:
                fixed.append(dict(lna=[float(x0 + 0.1 * j), float(x0 + 0.1 * (j + 1))],
                                  ds=float(np.polyfit(x[s], y[s], 1)[0]), nbins=int(s.sum())))
            j += 1
        slide = []
        for i in range(len(x)):
            s = (x >= x[i]) & (x < x[i] + 0.1)
            if s.sum() >= 3 and x[i] + 0.1 <= x[-1] + 1e-9:
                slide.append(float(np.polyfit(x[s], y[s], 1)[0]))
        b4[n] = dict(max_abs_bin=float(np.max(np.abs(np.expm1(y)))), fixed_windows=fixed,
                     max_abs_ds_fixed=float(max(abs(f["ds"]) for f in fixed)),
                     max_abs_ds_sliding=float(max(abs(v) for v in slide)), G1_holds=bool(np.max(np.abs(np.expm1(y))) <= 5e-3),
                     G5_holds_fixed=bool(max(abs(f["ds"]) for f in fixed) <= 0.03),
                     G5_holds_sliding=bool(max(abs(v) for v in slide) <= 0.03))
    res["B4"] = b4

    # ---- B7: converged vacuum horizon-mass offsets per mesh (fp_analyse) and the null test G3-N1
    fp = json.load(open(S / FP / "fp_analyse.json"))
    res["B7"] = dict(e_tight_A16_200M=fp["FP4"]["e_A16_tight"], e_tight_A32_200M=fp["FP4"]["e"],
                     null_tight_M8=fp["FPX"]["null_tight"], null_tight_M16=fp["FP5"]["diff"]["M16"],
                     null_tight_M8_common_200_300=fp["FP5"]["diff"]["M8"])
    m8 = max(abs(v) for k, v in fp["FPX"]["null_tight"].items() if float(k) >= 100)
    m8c = max(abs(v) for v in fp["FP5"]["diff"]["M8"].values())
    m16 = max(abs(v) for v in fp["FP5"]["diff"]["M16"].values())
    res["B7"].update(max_M8_100_500=m8, max_M8_200_300=m8c, max_M16_200_300=m16,
                     ratio_full_windows=m8 / m16, ratio_common_window=m8c / m16)

    (out / "g2_analogs.json").write_text(json.dumps(res, indent=1, default=float))

    # ---- figure
    fs.use_style()
    fig, ax = plt.subplots(2, 2, figsize=(7.2, 5.6))
    a = ax[0, 0]
    a.plot(grid, (M["FNQ"] - M["FK"]) * 1e3, lw=0.6, label="N/4 - N")
    a.plot(grid, (M["FK"] - M["FN4"]) * 1e3, lw=0.6, label="N - 4N")
    a.plot(g300, d16 * 1e3, lw=0.8, label=r"$\Delta M_{16}-\Delta M_{8}$")
    for lo in range(50, 401, 50):
        a.axvline(lo, color="0.85", lw=0.5, zorder=0)
    a.set_xlabel("t / M"); a.set_ylabel(r"difference of $M_{AH}$ / $10^{-3}$"); a.legend(fontsize=7, loc="upper left")
    a.set_title("(a) G2 differences (raw finder)", fontsize=8)
    a = ax[0, 1]
    xs = [np.mean(x["window"]) for x in b1]
    a.plot(xs, [x["ratio"] for x in b1], "o-", label="rms ratio (N/4-N)/(N-4N)")
    a.axhspan(1.4, 3.0, color="0.9", zorder=0, label="G3-G4 band [1.4, 3]")
    a.axhline(2.0, color="k", lw=0.5, ls="--")
    a.set_xlabel("window centre t / M"); a.set_ylabel("ratio"); a.legend(fontsize=7)
    a.set_title("(b) B1: the G3-G4 test one factor coarser", fontsize=8)
    a = ax[1, 0]
    for n, mk in (("ES-FL", "o"), ("FL16", "s"), ("FK", "^"), ("FN4", "v"), ("FNQ", "x")):
        ks = sorted(e[n])
        a.plot(np.array(ks) + 5, np.array([e[n][k] for k in ks]) * 100, mk, ms=3, lw=0.6, ls="-", label=n)
    a.axhspan(-0.5, 0.5, color="0.93", zorder=0)
    a.set_xlabel(r"$\tau_{rem}$ / M"); a.set_ylabel(r"bin median of $r$ / per cent"); a.legend(fontsize=6, ncol=2)
    a.set_title("(c) e_h per 10 M bin; grey: G3-G1 band", fontsize=8)
    a = ax[1, 1]
    for n, mk in (("ES-FL", "o"), ("FK", "^")):
        fw = b4[n]["fixed_windows"]
        a.plot([np.mean(f["lna"]) for f in fw], [f["ds"] for f in fw], mk + "-", ms=4, label=n)
    a.axhspan(-0.03, 0.03, color="0.9", zorder=0, label="G3-G5 band")
    a.set_xlabel(r"$\ln a$ (window centre)"); a.set_ylabel(r"$s_h - s_{LTB}$"); a.legend(fontsize=7)
    a.set_title("(d) B4: slope test, known defect (ES-FL)", fontsize=8)
    fig.tight_layout()
    fig.savefig(out / "g2_analogs.png", dpi=150)
    fig.savefig(out / "g2_analogs.pdf")
    print(json.dumps({k: res[k] for k in ("B1", "noise", "B3", "B7")}, indent=1, default=float)[:6000])
    for r in res["B2"]:
        print(r)
    for n, v in b4.items():
        print(n, {k: v[k] for k in v if k != "fixed_windows"})
    return 0


if __name__ == "__main__":
    sys.exit(main())
