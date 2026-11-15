"""P2 analysis: AthenaK test-particle runs of the spike distribution function.

Reads the snapshots of K runs (one per particle file of sample_spike.py), and checks
 (a) stationarity: binned species-0 counts against the reference profile
     dN/dr = 4 pi r^2 rho(r) / sqrt(1 - 2/r) of the truncated DF (E <= E_cut), at every
     snapshot (Poisson chi^2 and the inner-bin time series);
 (b) invariants: E = -u_t and L = |x x u| of every particle against the initial values;
 (c) loss cone: horizon crossings (KS r < 2 in a snapshot) against the exact prediction
     (species 0: none; species 1: exactly the s = -1 particles, at the predicted time).

usage: python3 analyze_spike.py --ic <ic dir> --runs <run dirs ...> --out <dir>
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
from spike_lib import SpikeModel  # noqa
from nrpic import kerr, figstyle  # noqa

warnings.simplefilter("ignore", RuntimeWarning)


def read_snap(fn):
    with open(fn, "rb") as f:
        if f.read(8) != b"NRPSNAP1":
            raise ValueError(fn)
        t = float(np.frombuffer(f.read(8), "<f8")[0])
        n = int(np.frombuffer(f.read(8), "<i8")[0])
        f.read(8)
        rec = np.frombuffer(f.read(56 * n), "<f8").reshape(n, 7)
        tag = np.frombuffer(f.read(4 * n), "<i4")
        sp = np.frombuffer(f.read(4 * n), "<i4")
    return t, rec, tag, sp


def losscone_figure(out, tt, s0, s1, fate, tpred, first_in, meta, q, snap_dt):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    figstyle.use_style()
    P = figstyle.PAL
    fig, axs = plt.subplots(1, 2, figsize=(8.0, 3.4))
    fig.subplots_adjust(left=0.08, right=0.98, top=0.95, bottom=0.15, wspace=0.28)
    a = axs[0]
    pl = s1 & fate
    cr = np.isfinite(first_in)
    a.plot(tpred[pl & cr], first_in[pl & cr] - tpred[pl & cr], ".", ms=3, color=P["red"],
           label="plunging, crossed")
    a.axhspan(0, snap_dt, color=P["blue"], alpha=0.2, label="[t_pred, t_pred + snapshot interval)")
    miss = pl & ~cr
    if miss.any():
        a.plot(tpred[miss], np.zeros(miss.sum()), "x", color="k", label="plunging, not crossed")
    a.set_xlabel(r"predicted crossing time $t_{\rm pred}/Gm$")
    a.set_ylabel(r"first snapshot inside $-\ t_{\rm pred}$ [$Gm$]")
    a.legend(loc="upper right", fontsize=7)
    b = axs[1]
    qq = q[s1]
    crossed = cr[s1]
    b.semilogx(np.abs(qq[qq > 0]), crossed[qq > 0].astype(float) + 0.02 * np.random.default_rng(0).standard_normal(np.sum(qq > 0)),
               ".", ms=3, color=P["green"], label=r"$L^2 = L_c^2(1+q)$ (outside)")
    b.semilogx(np.abs(qq[qq < 0]), crossed[qq < 0].astype(float) + 0.02 * np.random.default_rng(1).standard_normal(np.sum(qq < 0)),
               ".", ms=3, color=P["red"], label=r"$L^2 = L_c^2(1-q)$ (loss cone)")
    b.set_yticks([0, 1]); b.set_yticklabels(["stays out", "crossed r = 2"])
    b.set_xlabel(r"distance to the separatrix $|q|$")
    b.legend(loc="center left", fontsize=7)
    for ext in ("pdf", "png"):
        fig.savefig(out / f"losscone.{ext}")
    plt.close(fig)
    shutil.copy(out / "losscone.png", HERE / "figs" / "losscone.png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ic", required=True)
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--nbins", type=int, default=24)
    args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    ic = Path(args.ic)
    meta = np.load(ic / "ic_meta.npz")
    summ = json.loads((ic / "ic_summary.json").read_text())
    ecut = summ["args"]["ecut"]
    E0, L0, sp0 = meta["E"], meta["L"], meta["species"]
    ntot = E0.size
    n0 = int(np.sum(sp0 == 0))

    # ---- gather snapshots ----------------------------------------------------------------
    runs = [Path(r) for r in args.runs]
    files = {}
    for r in runs:
        # which particle file did this run read?  (recorded by the driver in run_file.txt)
        fname = (r / "run_file.txt").read_text().strip()
        files[r] = np.array(summ["file_index"][fname])
    snaps = [sorted(glob.glob(str(r / "spike.part.*.bin"))) for r in runs]
    nsnap = min(len(s) for s in snaps)
    times = np.zeros(nsnap)
    R = np.full((nsnap, ntot), np.nan)
    Ef = np.full(ntot, np.nan); Lf = np.full(ntot, np.nan)
    first_in = np.full(ntot, np.inf)         # first snapshot time with r < 2
    left_after_in = np.zeros(ntot, bool)     # r > 2 after having been inside (bogus)
    maxdE = np.zeros(ntot); maxdL = np.zeros(ntot)
    present = np.zeros(ntot, bool)           # particles of the analysed runs
    nonfinite = 0
    for k in range(nsnap):
        for r, s in zip(runs, snaps):
            t, rec, tag, sp = read_snap(s[k])
            gid = files[r][tag]
            present[gid] = True
            x, u = rec[:, :3], rec[:, 3:6]
            fin = np.isfinite(rec).all(axis=1)
            nonfinite += int((~fin).sum())
            rr = np.linalg.norm(x, axis=1)
            R[k, gid] = rr
            inside = rr < 2.0
            newly = inside & ~np.isfinite(first_in[gid])
            first_in[gid[newly]] = t
            left_after_in[gid] |= (~inside) & np.isfinite(first_in[gid])
            out_ = ~inside & fin
            if out_.any():
                E = kerr.energy("cks", x[out_], u[out_], a=0.0, M=1.0)
                L = np.linalg.norm(np.cross(x[out_], u[out_]), axis=1)
                g = gid[out_]
                dE = np.abs(E / E0[g] - 1); dL = np.abs(L / L0[g] - 1)
                maxdE[g] = np.maximum(maxdE[g], dE); maxdL[g] = np.maximum(maxdL[g], dL)
                if k == nsnap - 1:
                    Ef[g] = E; Lf[g] = L
        times[k] = t
    res = {"nsnap": nsnap, "t_end": float(times[-1]), "nonfinite_records": nonfinite}

    # ---- (b) invariants -----------------------------------------------------------------
    s0 = (sp0 == 0) & present
    n0 = int(s0.sum())
    res["n_species0"] = n0; res["n_species1"] = int(np.sum((sp0 == 1) & present))
    res["invariants_species0"] = {} if n0 == 0 else {
        "max_over_snapshots_dE/E_median_p99_max": [float(np.median(maxdE[s0])),
                                                   float(np.quantile(maxdE[s0], 0.99)),
                                                   float(np.max(maxdE[s0]))],
        "max_over_snapshots_dL/L_median_p99_max": [float(np.median(maxdL[s0])),
                                                   float(np.quantile(maxdL[s0], 0.99)),
                                                   float(np.max(maxdL[s0]))]}

    # ---- (c) loss cone ------------------------------------------------------------------
    s1 = (sp0 == 1) & present
    fate = meta["fate_plunge"].astype(bool)
    tpred = meta["tcross"]
    crossed = np.isfinite(first_in)
    q = meta["q"]
    res["losscone"] = {
        "species0_crossed": int(np.sum(crossed & s0)),
        "species0_crossed_ids": np.where(crossed & s0)[0].tolist()[:50],
        "species1_predicted_plunge": int(np.sum(s1 & fate)),
        "species1_predicted_plunge_crossed": int(np.sum(s1 & fate & crossed)),
        "species1_predicted_bound_crossed": int(np.sum(s1 & ~fate & crossed)),
        "species1_predicted_plunge_not_crossed": int(np.sum(s1 & fate & ~crossed
                                                          & (tpred < times[-1]))),
        "bogus_exit_after_crossing": int(np.sum(left_after_in)),
    }
    sel = s1 & fate & crossed
    dts = first_in[sel] - tpred[sel]            # measured minus predicted, in [0, snap_dt)
    snap_dt = float(np.median(np.diff(times)))
    res["losscone"]["first_snapshot_inside_minus_predicted"] = {
        "min": float(dts.min()) if dts.size else None,
        "max": float(dts.max()) if dts.size else None,
        "snap_dt": snap_dt,
        "n_outside_[0,snap_dt)": int(np.sum((dts < -1e-6) | (dts >= snap_dt + 1e-6)))}
    # semi-analytic cumulative removal curve
    tt = times
    pred_cum = np.array([np.sum(s1 & fate & (tpred <= t)) for t in tt])
    meas_cum = np.array([np.sum(s1 & (first_in <= t)) for t in tt])

    # ---- (a) stationarity ---------------------------------------------------------------
    if n0 == 0:
        (out / "analysis.json").write_text(json.dumps(res, indent=1))
        losscone_figure(out, tt, s0, s1, fate, tpred, first_in, meta, q, snap_dt)
        print(json.dumps(res, indent=1))
        return
    sm = SpikeModel(m_sun=summ["args"]["m"])
    rmin_s = float(np.nanmin(R[:, s0]))
    rmax_s = float(np.nanmax(R[:, s0]))
    rg = np.unique(np.concatenate([4.0 + np.logspace(-3, np.log10(6.0), 60),
                                   np.logspace(1.0, np.log10(max(rmax_s, 12) * 1.05), 120)]))
    rho_t = sm.rho_rel(rg, "canonical", Eup=ecut)
    rho_f = sm.rho_rel(rg, "canonical", Eup=1.0)
    dNdr = 4 * np.pi * rg**2 * rho_t / np.sqrt(1 - 2 / rg)
    # cumulative of the reference, normalized to the species-0 count
    cdf = np.concatenate([[0], np.cumsum(0.5 * (dNdr[1:] + dNdr[:-1]) * np.diff(rg))])
    norm_tot = cdf[-1]
    edges = np.unique(np.concatenate([[4.0], np.logspace(np.log10(4.5), np.log10(rmax_s * 1.01),
                                                         args.nbins)]))
    exp_counts = n0 * np.diff(np.interp(edges, rg, cdf)) / norm_tot
    counts = np.array([np.histogram(R[k, s0], edges)[0] for k in range(nsnap)])
    good = exp_counts > 20
    chi2 = np.sum((counts[:, good] - exp_counts[good]) ** 2 / exp_counts[good], axis=1)
    dof = int(good.sum())
    res["stationarity"] = {
        "edges": edges.tolist(), "expected": exp_counts.tolist(),
        "chi2_per_snapshot": chi2.tolist(), "dof": dof,
        "chi2_t0": float(chi2[0]), "chi2_median": float(np.median(chi2)),
        "chi2_max": float(np.max(chi2)), "reference_mass_fraction_lost_beyond": None,
    }
    # inner ranges
    ranges = [(4.0, 6.0), (6.0, 10.0), (10.0, 20.0), (20.0, 50.0)]
    ser = {}
    for a, b in ranges:
        e = n0 * (np.interp(b, rg, cdf) - np.interp(a, rg, cdf)) / norm_tot
        c = np.array([np.sum((R[k, s0] >= a) & (R[k, s0] < b)) for k in range(nsnap)])
        ser[f"{a:g}-{b:g}"] = {"expected": float(e), "t0": int(c[0]),
                               "mean_over_t": float(c.mean()), "min": int(c.min()),
                               "max": int(c.max()),
                               "late_half_mean_over_expected": float(c[nsnap // 2:].mean() / e),
                               "series": c.tolist()}
    res["stationarity"]["inner_ranges"] = ser
    (out / "analysis.json").write_text(json.dumps(res, indent=1))

    # ---- figures ------------------------------------------------------------------------
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    figstyle.use_style()
    P = figstyle.PAL
    mid = 0.5 * (edges[1:] + edges[:-1])
    width = np.diff(edges)
    shell = lambda c: c / width / (4 * np.pi * mid**2) * np.sqrt(1 - 2 / mid)  # noqa

    fig, axs = plt.subplots(2, 1, figsize=(4.0, 5.0), sharex=True,
                            gridspec_kw=dict(height_ratios=[3, 1.6]))
    fig.subplots_adjust(left=0.17, right=0.97, top=0.97, bottom=0.10, hspace=0.0)
    a = axs[0]
    scale = n0 / norm_tot
    a.plot(rg, rho_t * scale, color=P["blue"], label=r"reference, $E\leq E_{\rm cut}$")
    a.plot(rg, rho_f * scale, **figstyle.GUIDE, label="reference, full DF")
    ks = [0, nsnap // 2, nsnap - 1]
    cols = [P["red"], P["yellow"], P["green"]]
    for k, c in zip(ks, cols):
        a.step(edges, np.append(shell(counts[k]), np.nan), where="post", color=c,
               label=f"AthenaK, t = {times[k]:.0f} M")
    a.set_xscale("log"); a.set_yscale("log")
    a.set_ylabel(r"$\rho$ (arbitrary units)")
    a.legend(loc="lower left", fontsize=7)
    a.set_ylim(bottom=np.nanmax(rho_t * scale) * 1e-3)
    b = axs[1]
    sig = 1 / np.sqrt(np.maximum(exp_counts, 1))
    b.fill_between(edges, np.append(1 - sig, np.nan), np.append(1 + sig, np.nan),
                   step="post", color=P["blue"], alpha=0.2, label=r"$\pm1\sigma$ Poisson")
    for k, c in zip(ks, cols):
        b.step(edges, np.append(counts[k] / exp_counts, np.nan), where="post", color=c)
    b.step(edges, np.append(counts.mean(axis=0) / exp_counts, np.nan), where="post",
           color="k", lw=1.0, label="mean over snapshots")
    b.axhline(1, **figstyle.THIN)
    b.set_ylim(0.8, 1.2); b.set_xlabel(r"$r/Gm$ (Kerr-Schild = Schwarzschild $r$)")
    b.set_ylabel("counts / expected")
    b.legend(loc="upper right", fontsize=7, ncol=2)
    for ext in ("pdf", "png"):
        fig.savefig(out / f"stationarity_profile.{ext}")
    plt.close(fig)

    fig, axs = plt.subplots(2, 1, figsize=(4.0, 4.6), sharex=True)
    fig.subplots_adjust(left=0.17, right=0.97, top=0.97, bottom=0.11, hspace=0.0)
    a = axs[0]
    for (rng_, d), c in zip(ser.items(), [P["red"], P["yellow"], P["green"], P["orange"]]):
        y = np.array(d["series"]) / d["expected"]
        a.plot(times, y, color=c, lw=1.0, label=f"{rng_} Gm (N_exp = {d['expected']:.0f})")
        s_ = 1 / np.sqrt(d["expected"])
        a.axhspan(1 - s_, 1 + s_, color=c, alpha=0.08)
    a.axhline(1, **figstyle.THIN)
    a.set_ylabel("counts / expected"); a.set_ylim(0.85, 1.15)
    a.legend(loc="upper right", fontsize=7, ncol=2)
    b = axs[1]
    b.plot(times, chi2 / dof, color=P["red"], lw=1.0, label=rf"$\chi^2/{dof}$")
    b.axhline(1, **figstyle.GUIDE)
    b.set_xlabel(r"$t/Gm$"); b.set_ylabel(r"$\chi^2$ per bin")
    b.legend(loc="upper right", fontsize=7)
    for ext in ("pdf", "png"):
        fig.savefig(out / f"stationarity_time.{ext}")
    plt.close(fig)

    fig, axs = plt.subplots(1, 2, figsize=(8.0, 3.4))
    fig.subplots_adjust(left=0.08, right=0.98, top=0.95, bottom=0.15, wspace=0.28)
    a = axs[0]
    rp = meta["rp"]
    fin = s0 & np.isfinite(maxdE) & (maxdE > 0)
    a.loglog(rp[fin], maxdE[fin], ".", ms=1.5, color=P["red"], alpha=0.4, rasterized=True,
             label=r"max$_t\,|\Delta E/E|$")
    a.loglog(rp[fin], maxdL[fin], ".", ms=1.5, color=P["blue"], alpha=0.4, rasterized=True,
             label=r"max$_t\,|\Delta L/L|$")
    a.set_xlabel(r"pericentre $r_p/Gm$"); a.set_ylabel("relative error, species 0")
    a.legend(loc="upper right", fontsize=7, markerscale=6)
    b = axs[1]
    pl = s1 & fate
    b.plot(tt, pred_cum, color=P["blue"], lw=3, alpha=0.5, label="predicted (exact geodesics)")
    b.step(tt, meas_cum, where="post", color=P["red"], label="AthenaK: species 1 inside r = 2")
    b.step(tt, [np.sum(s0 & (first_in <= t)) for t in tt], where="post", color=P["green"],
           label="AthenaK: species 0 inside r = 2")
    b.set_xscale("symlog", linthresh=100); b.set_xlabel(r"$t/Gm$")
    b.set_ylabel("particles that crossed the horizon")
    b.legend(loc="center right", fontsize=7)
    for ext in ("pdf", "png"):
        fig.savefig(out / f"invariants_losscone.{ext}")
    plt.close(fig)

    figdir = HERE / "figs"; figdir.mkdir(exist_ok=True)
    for f in ("stationarity_profile.png", "stationarity_time.png", "invariants_losscone.png"):
        shutil.copy(out / f, figdir / f)
    print(json.dumps({k: v for k, v in res.items() if k != "stationarity"}, indent=1))
    st = res["stationarity"]
    print("chi2 t0 %.1f median %.1f max %.1f dof %d" % (st["chi2_t0"], st["chi2_median"],
                                                       st["chi2_max"], st["dof"]))
    for k, v in st["inner_ranges"].items():
        print(k, {kk: vv for kk, vv in v.items() if kk != "series"})


if __name__ == "__main__":
    main()
