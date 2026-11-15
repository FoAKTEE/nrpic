"""K2 analysis: AthenaK test-particle runs of the Kerr spike distribution function.

Reads the snapshots of K runs (one per particle file of sample_kerr.py) and checks
 (a) the binned counts in (ln r, |cos theta|) against the reference n(r, theta) of
     kerr_expected.py (E <= E_cut), at every snapshot (Poisson chi^2);
 (b) counts in r ranges, the equator/pole contrast and the mean Lz per range in time;
 (c) the invariants E, Lz, Q of every particle against their initial values;
 (d) no particle inside r_+ or below its predicted pericentre.

usage: python3 analyze_kerr.py --ic <ic dir> --ref <kerr_expected dir> --runs <run dirs ...>
                               --out <dir> [--tag NAME] [--nofigs]
"""
import argparse
import glob
import json
import shutil
import sys
import warnings
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "python"))
from analyze_spike import read_snap  # noqa: E402
from nrpic import kerr as nk, figstyle  # noqa: E402

warnings.simplefilter("ignore", RuntimeWarning)
RANGES = [(0.0, 4.0), (4.0, 6.0), (6.0, 10.0), (10.0, 16.0), (16.0, 40.0)]


def cumtrapz(y, x):
    return np.concatenate([[0.0], np.cumsum(0.5 * (y[1:] + y[:-1]) * np.diff(x))])


def reference(ref):
    d = np.load(Path(ref) / "expected.npz")
    x, mu, nx = d["x"], d["mu"], d["n_x"]
    lz = np.nan_to_num(d["Lz_mean"])
    tot = np.trapezoid(np.trapezoid(nx, mu, axis=1), x)
    xe_i = np.arange(0, x.size, 4)
    me_i = [0, 3, 6, 9]
    assert x.size - 1 == xe_i[-1] and mu.size == 10
    exp2 = np.zeros((xe_i.size - 1, 3))
    for i in range(xe_i.size - 1):
        for j in range(3):
            sx = slice(xe_i[i], xe_i[i + 1] + 1); sm = slice(me_i[j], me_i[j + 1] + 1)
            exp2[i, j] = np.trapezoid(np.trapezoid(nx[sx, sm], mu[sm], axis=1), x[sx])
    band = []      # per mu band: n per dx (integrated over the band), and Lz-weighted
    for j in range(3):
        sm = slice(me_i[j], me_i[j + 1] + 1)
        band.append((np.trapezoid(nx[:, sm], mu[sm], axis=1),
                     np.trapezoid(nx[:, sm] * lz[:, sm], mu[sm], axis=1)))
    return {"x": x, "mu": mu, "tot": tot, "xedges": x[xe_i], "muedges": mu[me_i],
            "frac2": exp2 / tot, "band": band}


def range_frac(R, a, b, bands=(0, 1, 2), weight="n"):
    x = R["x"]
    lo, hi = np.log(max(a, np.exp(x[0]))), np.log(b)
    s, sl = 0.0, 0.0
    for j in bands:
        n, nl = R["band"][j]
        c, cl = cumtrapz(n, x), cumtrapz(nl, x)
        s += np.interp(hi, x, c) - np.interp(lo, x, c)
        sl += np.interp(hi, x, cl) - np.interp(lo, x, cl)
    return s / R["tot"], sl / max(s, 1e-300)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ic", required=True)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tag", default="kerr")
    ap.add_argument("--nofigs", action="store_true")
    args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    ic = Path(args.ic)
    meta = np.load(ic / "ic_meta.npz")
    summ = json.loads((ic / "ic_summary.json").read_text())
    a = summ["args"]["a"]
    E0, Lz0, Q0, rp0 = meta["E"], meta["Lz"], meta["Q"], meta["rp"]
    ntot = E0.size
    R = reference(args.ref)
    rplus = 1 + np.sqrt(1 - a * a)

    runs = [Path(r) for r in args.runs]
    files = {r: np.array(summ["file_index"][(r / "run_file.txt").read_text().strip()]) for r in runs}
    snaps = [sorted(glob.glob(str(r / "*.part.*.bin"))) for r in runs]
    nsnap = min(len(s) for s in snaps)
    present = np.zeros(ntot, bool)
    for r in runs:
        present[files[r]] = True
    N = int(present.sum())
    times = np.zeros(nsnap)
    nxb, nmb = R["xedges"].size - 1, 3
    counts = np.zeros((nsnap, nxb, nmb))
    rc = np.zeros((nsnap, len(RANGES)))
    lzm = np.zeros((nsnap, len(RANGES)))
    lzsem = np.zeros((nsnap, len(RANGES)))
    contrast = np.zeros((nsnap, 2))
    rmin = np.full(ntot, np.inf)
    maxdE = np.zeros(ntot); maxdL = np.zeros(ntot); maxdQ = np.zeros(ntot)
    nonfinite = 0
    for k in range(nsnap):
        X = np.full((ntot, 3), np.nan); U = np.full((ntot, 3), np.nan)
        for r, s in zip(runs, snaps):
            t, rec, tag, sp = read_snap(s[k])
            g = files[r][tag]
            X[g], U[g] = rec[:, :3], rec[:, 3:6]
        times[k] = t
        Xp, Up = X[present], U[present]
        fin = np.isfinite(Xp).all(1) & np.isfinite(Up).all(1)
        nonfinite += int((~fin).sum())
        rr = nk.cks_radius(Xp, a)
        mu = np.abs(Xp[:, 2] / rr)
        lz = Xp[:, 0] * Up[:, 1] - Xp[:, 1] * Up[:, 0]
        counts[k] = np.histogram2d(np.log(rr), mu, [R["xedges"], R["muedges"]])[0]
        for i, (lo, hi) in enumerate(RANGES):
            m = (rr >= lo) & (rr < hi)
            rc[k, i] = m.sum(); lzm[k, i] = lz[m].mean() if m.any() else np.nan
            lzsem[k, i] = lz[m].std() / np.sqrt(max(m.sum(), 1))
        inn = rr < 16.0
        contrast[k] = [np.sum(inn & (mu < 1 / 3)), np.sum(inn & (mu >= 2 / 3))]
        gi = np.nonzero(present)[0]
        rmin[gi] = np.minimum(rmin[gi], rr)
        E, Lz, Q = nk.invariants("cks", Xp, Up, a=a, M=1.0)
        maxdE[gi] = np.maximum(maxdE[gi], np.abs(E / E0[gi] - 1))
        maxdL[gi] = np.maximum(maxdL[gi], np.abs(Lz - Lz0[gi]))
        maxdQ[gi] = np.maximum(maxdQ[gi], np.abs(Q - Q0[gi]) / np.maximum(Q0[gi], 1.0))
    exp2 = N * R["frac2"]
    good = exp2 > 20
    chi2 = np.array([np.sum((counts[k][good] - exp2[good]) ** 2 / exp2[good]) for k in range(nsnap)])
    dof = int(good.sum())
    res = {"tag": args.tag, "N": N, "nsnap": nsnap, "t_end": float(times[-1]),
           "nonfinite_records": nonfinite, "dof": dof, "chi2_t0": float(chi2[0]),
           "chi2_median": float(np.median(chi2)), "chi2_min": float(chi2.min()),
           "chi2_max": float(chi2.max()), "band_1pm3sqrt(2/dof)": [1 - 3 * np.sqrt(2 / dof),
                                                                     1 + 3 * np.sqrt(2 / dof)],
           "expected_outside_bins_frac": float(1 - R["frac2"].sum())}
    ser = {}
    for i, (lo, hi) in enumerate(RANGES):
        fr, lref = range_frac(R, lo, hi)
        e = N * fr
        c = rc[:, i]
        z = (c - e) / np.sqrt(e)
        ser[f"{lo:g}-{hi:g}"] = {
            "expected": float(e), "t0": int(c[0]), "z_min": float(z.min()), "z_max": float(z.max()),
            "late_half_mean_over_expected": float(c[nsnap // 2:].mean() / e),
            "late_half_z": float((c[nsnap // 2:].mean() - e) / np.sqrt(e)),
            "Lz_mean_ref": float(lref), "Lz_mean_t0": float(lzm[0, i]),
            "Lz_sem_t0": float(lzsem[0, i]),
            "Lz_z_t0": float((lzm[0, i] - lref) / lzsem[0, i]),
            "Lz_z_minmax_vs_ref": [float(np.nanmin((lzm[:, i] - lref) / lzsem[:, i])),
                                   float(np.nanmax((lzm[:, i] - lref) / lzsem[:, i]))],
            "Lz_mean_late_half": float(np.nanmean(lzm[nsnap // 2:, i])),
            "Lz_mean_min_max": [float(np.nanmin(lzm[:, i])), float(np.nanmax(lzm[:, i]))],
            "series": c.astype(int).tolist(), "Lz_series": lzm[:, i].tolist()}
    res["ranges"] = ser
    feq, _ = range_frac(R, 0.0, 16.0, bands=(0,)); fpo, _ = range_frac(R, 0.0, 16.0, bands=(2,))
    cr = contrast[:, 0] / contrast[:, 1]
    cr_sig = cr * np.sqrt(1 / contrast[:, 0] + 1 / contrast[:, 1])
    res["contrast_eq_over_pole_r<16"] = {"ref": feq / fpo, "t0": float(cr[0]),
                                          "min": float(cr.min()), "max": float(cr.max()),
                                          "sigma_t0": float(cr_sig[0]),
                                          "late_half_mean": float(cr[nsnap // 2:].mean())}
    s0 = present
    res["invariants"] = {
        "dE/E_median_p99_max": [float(np.median(maxdE[s0])), float(np.quantile(maxdE[s0], 0.99)),
                                float(maxdE[s0].max())],
        "dLz_median_p99_max": [float(np.median(maxdL[s0])), float(np.quantile(maxdL[s0], 0.99)),
                               float(maxdL[s0].max())],
        "dQ/max(Q,1)_median_p99_max": [float(np.median(maxdQ[s0])),
                                       float(np.quantile(maxdQ[s0], 0.99)), float(maxdQ[s0].max())],
        "rp_of_max_dE": float(rp0[s0][np.argmax(maxdE[s0])])}
    res["inner"] = {"r_plus": rplus, "min_r_over_snapshots": float(rmin[s0].min()),
                    "n_below_r_plus": int(np.sum(rmin[s0] < rplus)),
                    "n_below_pericentre_minus_1e-3": int(np.sum(rmin[s0] < rp0[s0] - 1e-3)),
                    "min_(rmin - rp)": float(np.min(rmin[s0] - rp0[s0]))}
    (out / f"{args.tag}_analysis.json").write_text(json.dumps(res, indent=1))
    np.savez(out / f"{args.tag}_series.npz", t=times, counts=counts, exp2=exp2, chi2=chi2, rc=rc,
             lzm=lzm, contrast=contrast, maxdE=maxdE, maxdL=maxdL, maxdQ=maxdQ, rp=rp0,
             present=present)
    short = {k: v for k, v in res.items() if k != "ranges"}
    print(json.dumps(short, indent=1))
    for k, v in ser.items():
        print(k, {kk: vv for kk, vv in v.items() if kk not in ("series", "Lz_series")})
    if args.nofigs:
        return

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    figstyle.use_style()
    P = figstyle.PAL
    figdir = HERE / "figs"; figdir.mkdir(exist_ok=True)
    xe, me = R["xedges"], R["muedges"]
    re_ = np.exp(xe)
    dx = np.diff(xe)
    bandlab = [r"$|\cos\theta|<1/3$ (equator)", r"$1/3\leq|\cos\theta|<2/3$",
               r"$|\cos\theta|\geq 2/3$ (poles)"]
    bcol = [P["red"], P["yellow"], P["blue"]]
    ks = [0, nsnap // 2, nsnap - 1]

    fig, axs = plt.subplots(2, 1, figsize=(4.0, 5.2), sharex=True,
                            gridspec_kw=dict(height_ratios=[3, 1.6]))
    fig.subplots_adjust(left=0.17, right=0.97, top=0.97, bottom=0.09, hspace=0.0)
    ax = axs[0]
    for j in range(3):
        n, _ = R["band"][j]
        dm = me[j + 1] - me[j]
        ax.plot(np.exp(R["x"]), N * n / R["tot"] / dm, color=bcol[j], lw=1.0, label=bandlab[j])
        for k, ls in zip(ks, ["-", "--", ":"]):
            ax.step(re_, np.append(counts[k][:, j] / dx / dm, np.nan), where="post",
                    color=bcol[j], lw=0.8, ls=ls, alpha=0.8)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_ylim(bottom=20)
    ax.set_ylabel(r"$dN/d\ln r\,d|\cos\theta|$")
    ax.legend(loc="lower center", fontsize=7, title=f"lines: reference; steps: t = 0, "
              f"{times[ks[1]]:.0f}, {times[ks[2]]:.0f} M", title_fontsize=7)
    ax = axs[1]
    for j in range(3):
        m = exp2[:, j] > 20
        rat = counts[:, :, j].mean(axis=0) / exp2[:, j]
        ax.step(re_, np.append(np.where(m, rat, np.nan), np.nan), where="post", color=bcol[j],
                lw=1.2)
        ax.step(re_, np.append(np.where(m, counts[0][:, j] / exp2[:, j], np.nan), np.nan),
                where="post", color=bcol[j], lw=0.7, ls=":")
    sig = 1 / np.sqrt(np.maximum(exp2.min(axis=1), 1))
    ax.fill_between(re_, np.append(1 - sig, np.nan), np.append(1 + sig, np.nan), step="post",
                    color="grey", alpha=0.2, label=r"$\pm1\sigma$ (least-populated band)")
    ax.axhline(1, **figstyle.THIN)
    ax.set_ylim(0.75, 1.25)
    ax.set_xlabel(r"$r/Gm$ (Kerr-Schild = Boyer-Lindquist $r$)", labelpad=-2)
    ax.set_ylabel("counts / expected")
    ax.legend(loc="upper right", fontsize=7)
    for ext in ("pdf", "png"):
        fig.savefig(out / f"{args.tag}_profile.{ext}")
    plt.close(fig)

    fig, axs = plt.subplots(3, 1, figsize=(4.0, 6.0), sharex=True)
    fig.subplots_adjust(left=0.17, right=0.97, top=0.98, bottom=0.08, hspace=0.0)
    ax = axs[0]
    cols = [P["red"], P["yellow"], P["green"], P["orange"], P["blue"]]
    for (k_, d), c in zip(ser.items(), cols):
        ax.plot(times, np.array(d["series"]) / d["expected"], color=c, lw=0.9,
                label=f"{k_} Gm ({d['expected']:.0f})")
        s_ = 1 / np.sqrt(d["expected"])
        ax.axhspan(1 - s_, 1 + s_, color=c, alpha=0.08)
    ax.axhline(1, **figstyle.THIN); ax.set_ylim(0.85, 1.15)
    ax.set_ylabel("counts / expected"); ax.legend(loc="upper right", fontsize=6, ncol=2)
    ax = axs[1]
    for (k_, d), c in zip(ser.items(), cols):
        ax.plot(times, np.array(d["Lz_series"]) - d["Lz_mean_ref"], color=c, lw=0.9)
    ax.axhline(0, **figstyle.THIN)
    ax.set_ylabel(r"$\langle L_z\rangle - \langle L_z\rangle_{\rm ref}$ [$Gm$]")
    ax2 = axs[2]
    ax2.plot(times, chi2 / dof, color=P["red"], lw=1.0, label=rf"$\chi^2/{dof}$")
    ax2.plot(times, cr / res["contrast_eq_over_pole_r<16"]["ref"], color=P["blue"], lw=1.0,
             label="equator/pole contrast / ref.")
    ax2.axhline(1, **figstyle.GUIDE)
    ax2.set_xlabel(r"$t/Gm$", labelpad=-2); ax2.legend(loc="upper right", fontsize=7)
    for ext in ("pdf", "png"):
        fig.savefig(out / f"{args.tag}_time.{ext}")
    plt.close(fig)

    fig, axs = plt.subplots(1, 2, figsize=(8.0, 3.3))
    fig.subplots_adjust(left=0.08, right=0.98, top=0.95, bottom=0.15, wspace=0.28)
    ax = axs[0]
    m = s0
    for v, c, lab in ((maxdE, P["red"], r"max$_t|\Delta E/E|$"),
                      (maxdQ, P["green"], r"max$_t|\Delta Q|/\max(Q,1)$"),
                      (maxdL, P["blue"], r"max$_t|\Delta L_z|$")):
        ax.loglog(rp0[m], np.maximum(v[m], 1e-17), ".", ms=1.2, color=c, alpha=0.35,
                  rasterized=True, label=lab)
    ax.set_xlabel(r"pericentre $r_p/Gm$"); ax.set_ylabel("largest error over snapshots")
    ax.legend(loc="upper right", fontsize=7, markerscale=6)
    ax = axs[1]
    rmid = np.sqrt(np.array([max(lo, 2.0) for lo, _ in RANGES]) * np.array([hi for _, hi in RANGES]))
    ax.plot(rmid, [d["Lz_mean_ref"] for d in ser.values()], "s-", color=P["blue"], ms=5,
            label="reference (number-weighted)")
    ax.plot(rmid, [d["Lz_mean_t0"] for d in ser.values()], "o", color=P["red"], ms=4,
            label="AthenaK t = 0")
    ax.plot(rmid, [d["Lz_mean_late_half"] for d in ser.values()], "x", color=P["green"], ms=6,
            label="AthenaK, late-half mean")
    ax.axhline(0, **figstyle.THIN)
    ax.set_xscale("log"); ax.set_xlabel(r"$r/Gm$ (range centre)")
    ax.set_ylabel(r"$\langle L_z\rangle$ [$Gm$], spin along $+z$")
    ax.legend(loc="upper left", fontsize=7)
    for ext in ("pdf", "png"):
        fig.savefig(out / f"{args.tag}_invariants.{ext}")
    plt.close(fig)
    for f in (f"{args.tag}_profile.png", f"{args.tag}_time.png", f"{args.tag}_invariants.png"):
        shutil.copy(out / f, figdir / f)


if __name__ == "__main__":
    main()
