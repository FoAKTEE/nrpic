#!/usr/bin/env python3
"""Test A of tracks/core/JOURNAL-scalar3.md: the first-order part of the constraints
and of R^NR on the mesh, predicted by the linear twin (nrpic.sf_lattice: the linearised
equations of the code per wave vector with the symbols of its difference operators),
against the dumps of runs of the second package.

    python3 a1_twin.py --ladder DIR --t8 DIR --t12 DIR [--out DIR] [--skip-scan]

  DIR of --ladder  card run core-20261115-155404-24c88e3: lad{32,64,128}_{p1,m1}
                   (quadratic case, nmax2 = 64, s = +-1, dumps with H, M_i every 0.4)
  DIR of --t8      run core-20261115-160134-3fde433: run/ (32^3, dumps with the metric)
  DIR of --t12     run core-20261115-175842-7d54ff5: p1, m1, p05, m05, s0 (64^3, dumps
                   with the metric and the constraint fields)
Parts:
  A  rms over the box of the part of H and of |M| odd in s: twin against dumps, N = 32,
     64, 128; per-mode coefficients of H at N = 32
  B  variants of the twin at N = 32: every second derivative the first difference
     applied twice (scheme d1d1); mode functions of the sources with the lattice K2
  C  R^NR per mode: deviation of the twin from W R alpha against the measured one, and
     the dump against the twin directly (N = 32 single run, N = 64 odd part)
  D  scan of the resolution at fixed modes (nmax2 = 64): first-order parts of the twin
     against the measured second-order parts (which do not depend on N)
Writes OUT/summary.json and OUT/fig_twin.png."""
import argparse
import os
import time

import s3
from s3 import common, inf, np, sf
from nrpic import sf_lattice as sl

NMAX2 = 64


def odd_fields(dp, dm, c):
    fp, fm = dp[c]["fields"], dm[c]["fields"]
    oh = 0.5*(fp["H"] - fm["H"])
    om = [0.5*(fp[x] - fm[x]) for x in ("Mx", "My", "Mz")]
    return oh, om


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ladder", required=True)
    ap.add_argument("--t8", required=True)
    ap.add_argument("--t12", required=True)
    ap.add_argument("--out")
    ap.add_argument("--skip-scan", action="store_true")
    a = ap.parse_args()
    out = s3.run_dir(a.out)
    case = s3.case("sr", 1)
    v, dv, phi0, pi0 = inf.code_background(case)
    m2 = case["mass"]**2

    def d2v(x):
        return m2 + 0.0*x

    sh_n2, sh_r, sh_dr = inf.read_mode_file(os.path.join(common.PROB,
                                                         "sr_stochastic_modes.txt"))
    n, n2 = sf.mode_set(NMAX2)
    al = sf.mode_alpha(s3.SEED, 0, 0, n)
    nc, inv = sl.canonical(n)
    q = np.sqrt(n2.astype(float))
    summ = dict(modes=int(n.shape[0]), canonical=int(nc.shape[0]),
                phi0=phi0, pi0=pi0, mass=case["mass"])

    def twin(nroot, times, **kw):
        t0 = time.time()
        tw = sl.Twin(nc, nroot, s3.LENGTH, v, dv, d2v, phi0, pi0, sh_n2, sh_r, sh_dr,
                     **kw)
        sol = tw.integrate(times)
        dg = tw.diagnostics(sol)
        dg["wall"] = round(time.time() - t0, 1)
        return dg

    def rms_first(dg, it):
        hh = dg["dH"][it][inv]*al
        mm = dg["dM"][it][inv]*al[:, None]
        return (float(np.sqrt(2.0*(np.abs(hh)**2).sum())),
                float(np.sqrt(2.0*(np.abs(mm)**2).sum())), hh)

    # ---- mismatch of the symbols
    tab = []
    for cells in (4, 5, 6, 8, 10, 12, 16, 24, 32):
        kh = 2.0*np.pi/cells
        qq, kk = sf.d1_symbol(kh, 4)**2, sf.d2_symbol(kh, 4)
        tab.append(dict(cells_per_wavelength=cells, k_dx=kh, mu_over_k2=(kk - qq)/kh**2,
                        d2_error=1.0 - kk/kh**2, d1sq_error=1.0 - qq/kh**2))
    summ["symbols_sixth_order"] = tab

    # ---- A: ladder
    lad = {}
    series = {}
    for nroot in (32, 64, 128):
        dp = s3.dumps(os.path.join(a.ladder, f"lad{nroot}_p1"), "sr")
        dm = s3.dumps(os.path.join(a.ladder, f"lad{nroot}_m1"), "sr")
        cyc = sorted(set(dp) & set(dm))
        times = np.array([dp[c]["time"] for c in cyc])
        dg = twin(nroot, times[1:])
        rows = []
        for it, c in enumerate(cyc[1:]):
            th, tm, hh = rms_first(dg, it)
            oh, om = odd_fields(dp, dm, c)
            mh = s3.rms(oh)
            mm = float(np.sqrt(sum((x*x).mean() for x in om)))
            ch, _ = sf.analyse(oh, n)
            crms = float(np.sqrt((np.abs(ch)**2).mean()))
            top = n2 >= 49
            ent = dg["w"][it] > 0.5
            dev = np.abs(dg["rnr"][it]/dg["ref"][it] - 1.0)
            rows.append(dict(
                time=float(times[it+1]), H_twin=th, H_meas=mh, H_ratio=th/mh,
                M_twin=tm, M_meas=mm, M_ratio=tm/mm,
                H_coef_maxdiff_over_rms=float(np.abs(ch - hh).max()/crms),
                H_coef_maxdiff_top_over_rms_top=float(
                    np.abs(ch - hh)[top].max()/np.sqrt((np.abs(ch[top])**2).mean())),
                rnr_dev_twin_all=float(dev[ent].max()) if ent.any() else None,
                rnr_dev_twin_n_le_4=float(dev[ent & (inv_q(nc, inv) <= 4.0 + 1e-9)].max())
                if ent.any() else None))
        lad[nroot] = rows
        series[nroot] = (times[1:], rows)
        summ.setdefault("ladder", {})[str(nroot)] = dict(wall_twin_s=dg["wall"],
                                                          rows=rows)

    # ---- B: variants at N = 32
    t32 = series[32][0]
    var = {}
    for lab, kw in (("d1d1", dict(scheme="d1d1")), ("lattice_k2", dict(mode_k2="lattice")),
                    ("bssn", dict(z4c=False)), ("continuum", dict(scheme="continuum"))):
        dg = twin(32, t32, **kw)
        rows = []
        for it in range(t32.size):
            th, tm, _ = rms_first(dg, it)
            ent = dg["w"][it] > 0.5
            dev = np.abs(dg["rnr"][it]/dg["ref"][it] - 1.0)
            rows.append(dict(time=float(t32[it]), H_twin=th, M_twin=tm,
                             H_over_mesh=th/lad[32][it]["H_twin"],
                             M_over_mesh=tm/lad[32][it]["M_twin"],
                             rnr_dev_all=float(dev[ent].max()) if ent.any() else None))
        var[lab] = rows
    summ["variants_N32"] = var

    # ---- C: R^NR, dump against twin
    rn = {}
    d8 = s3.dumps(os.path.join(a.t8, "run"), "sr")
    cyc = sorted(d8)
    times = np.array([d8[c]["time"] for c in cyc])
    dg = twin(32, times[1:])
    rows = []
    cdata = {}
    for it, c in enumerate(cyc[1:]):
        rp, _ = s3.rnr_of_dump(d8[c], n, n2)
        tw_r = dg["rnr"][it][inv]*al
        ref = dg["ref"][it][inv]*al
        ent = dg["w"][it][inv] > 0.5
        if not ent.any():
            continue
        rows.append(dict(time=float(times[it+1]), modes_in=int(ent.sum()),
                         meas_vs_ref_max=float(np.abs(rp/ref - 1.0)[ent].max()),
                         twin_vs_ref_max=float(np.abs(tw_r/ref - 1.0)[ent].max()),
                         meas_vs_twin_max=float(np.abs(rp/tw_r - 1.0)[ent].max()),
                         meas_vs_twin_n_le_4=float(
                             np.abs(rp/tw_r - 1.0)[ent & (q <= 4.0 + 1e-9)].max())))
        cdata[32] = (q[ent], np.abs(rp/ref - 1.0)[ent], np.abs(tw_r/ref - 1.0)[ent],
                     np.abs(rp/tw_r - 1.0)[ent])
    rn["32_single_run"] = rows
    dp = s3.dumps(os.path.join(a.t12, "p1"), "sr")
    dm = s3.dumps(os.path.join(a.t12, "m1"), "sr")
    cyc = sorted(set(dp) & set(dm))
    times = np.array([dp[c]["time"] for c in cyc])
    dg = twin(64, times[1:])
    rows = []
    for it, c in enumerate(cyc[1:]):
        rp, _ = s3.rnr_of_dump(dp[c], n, n2)
        rm, _ = s3.rnr_of_dump(dm[c], n, n2)
        odd = 0.5*(rp - rm)
        tw_r = dg["rnr"][it][inv]*al
        ref = dg["ref"][it][inv]*al
        ent = dg["w"][it][inv] > 0.5
        if not ent.any():
            continue
        rows.append(dict(time=float(times[it+1]), modes_in=int(ent.sum()),
                         odd_vs_ref_max=float(np.abs(odd/ref - 1.0)[ent].max()),
                         twin_vs_ref_max=float(np.abs(tw_r/ref - 1.0)[ent].max()),
                         odd_vs_twin_max=float(np.abs(odd/tw_r - 1.0)[ent].max()),
                         odd_vs_twin_n_le_4=float(
                             np.abs(odd/tw_r - 1.0)[ent & (q <= 4.0 + 1e-9)].max())))
        cdata[64] = (q[ent], np.abs(odd/ref - 1.0)[ent], np.abs(tw_r/ref - 1.0)[ent],
                     np.abs(odd/tw_r - 1.0)[ent])
    rn["64_odd_part"] = rows
    summ["rnr"] = rn

    # ---- second-order parts measured at 64^3 (they do not depend on N)
    d0 = s3.dumps(os.path.join(a.t12, "s0"), "sr")
    sec = []
    for c in cyc[1:]:
        fp, fm = dp[c]["fields"], dm[c]["fields"]
        h0 = d0[c]["fields"]["H"]
        eh = 0.5*(fp["H"] + fm["H"]) - h0
        em = [0.5*(fp[x] + fm[x]) for x in ("Mx", "My", "Mz")]
        oh, om = odd_fields(dp, dm, c)
        sec.append(dict(time=float(dp[c]["time"]), H_second=s3.rms(eh),
                        M_second=float(np.sqrt(sum((x*x).mean() for x in em))),
                        H_first_meas=s3.rms(oh),
                        M_first_meas=float(np.sqrt(sum((x*x).mean() for x in om))),
                        H0=float(h0.mean())))
    summ["second_order_measured_64"] = sec
    tsec = np.array([r["time"] for r in sec])

    # ---- D: scan of the resolution at fixed modes
    scan = []
    if not a.skip_scan:
        for nroot in (32, 40, 48, 64, 80, 96, 128):
            dg = twin(nroot, tsec)
            row = dict(N=nroot, cells_per_shortest_wavelength=nroot/8.0,
                       kmax_dx=2.0*np.pi*8.0/nroot, rows=[])
            for it in range(tsec.size):
                th, tm, _ = rms_first(dg, it)
                ent = dg["w"][it] > 0.5
                dev = np.abs(dg["rnr"][it]/dg["ref"][it] - 1.0)
                row["rows"].append(dict(
                    time=float(tsec[it]), H_first=th, M_first=tm,
                    H_first_over_second=th/sec[it]["H_second"],
                    M_first_over_second=tm/sec[it]["M_second"],
                    rnr_dev_all=float(dev[ent].max()) if ent.any() else None))
            row["H_first_over_second_max"] = max(r["H_first_over_second"]
                                                 for r in row["rows"])
            row["M_first_over_second_max"] = max(r["M_first_over_second"]
                                                 for r in row["rows"])
            row["rnr_dev_end"] = row["rows"][-1]["rnr_dev_all"]
            scan.append(row)
        summ["scan"] = scan
        # cells per shortest wavelength at which the first-order part falls to the
        # second-order one and to a tenth of it (log-log interpolation)
        cw = np.log([r["cells_per_shortest_wavelength"] for r in scan])
        for key in ("H", "M"):
            y = np.log([r[key + "_first_over_second_max"] for r in scan])
            for lev, lab in ((1.0, "equal"), (0.1, "tenth")):
                summ[f"cells_for_{key}_first_{lab}_second"] = float(
                    np.exp(np.interp(-np.log(lev), -y[::-1], cw[::-1]))) \
                    if y.min() < np.log(lev) < y.max() else None
    common.dump_json(summ, os.path.join(out, "summary.json"))

    # ---- figure
    fs = common.style()
    import matplotlib.pyplot as plt
    B, R_, G, O = (fs.PAL[x] for x in ("blue", "red", "green", "orange"))
    fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.6))
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.09, top=0.97, wspace=0.27,
                        hspace=0.27)
    for nroot, cl in ((32, B), (64, G), (128, R_)):
        t, rows = series[nroot]
        for j, key in ((0, "H"), (1, "M")):
            ax[0, j].plot(t, [r[key + "_twin"] for r in rows], "-", color=cl,
                          label=f"$N={nroot}$, twin")
            ax[0, j].plot(t, [r[key + "_meas"] for r in rows], "o", ms=4, mfc="none",
                          color=cl, label=f"$N={nroot}$, runs")
    ax[0, 0].plot(tsec, [r["H_second"] for r in sec], "--", color="k", lw=1,
                  label="second order (runs, $N=64$)")
    ax[0, 1].plot(tsec, [r["M_second"] for r in sec], "--", color="k", lw=1,
                  label="second order (runs, $N=64$)")
    for j, lab in ((0, r"rms of the part of $\mathcal{H}$ odd in $s$"),
                   (1, r"rms of the part of $|\mathcal{M}|$ odd in $s$")):
        ax[0, j].set_yscale("log")
        ax[0, j].set_ylim(1e-16, 3e-9)
        ax[0, j].set_xlabel("$t$ (e-folds within 6 percent)")
        ax[0, j].set_ylabel(lab)
        ax[0, j].legend(loc="lower right", fontsize=6, ncol=2)
    for nroot, cl in ((32, B), (64, G)):
        if nroot not in cdata:
            continue
        qq, meas, tw, direct = cdata[nroot]
        lab = "run" if nroot == 32 else "odd part"
        ax[1, 0].plot(qq, meas, ".", ms=3, color=cl,
                      label=f"$N={nroot}$: {lab} against $W R\\,\\alpha$")
        ax[1, 0].plot(qq, tw, "x", ms=2.5, color="k", alpha=0.5,
                      label="twin against $W R\\,\\alpha$" if nroot == 32 else None)
        ax[1, 0].plot(qq, direct, "+", ms=3, color=cl, alpha=0.6,
                      label=f"$N={nroot}$: {lab} against twin")
    ax[1, 0].set_yscale("log")
    ax[1, 0].set_xlabel(r"$|n|$")
    ax[1, 0].set_ylabel(r"deviation of $R^{\rm NR}_n$ at the last dump")
    ax[1, 0].legend(loc="lower right", fontsize=6)
    if scan:
        cells = [r["cells_per_shortest_wavelength"] for r in scan]
        ax[1, 1].plot(cells, [r["H_first_over_second_max"] for r in scan], "o-",
                      color=B, label=r"$\mathcal{H}$")
        ax[1, 1].plot(cells, [r["M_first_over_second_max"] for r in scan], "s-",
                      color=R_, label=r"$|\mathcal{M}|$")
        ax[1, 1].plot(cells, [r["rnr_dev_end"] for r in scan], "^-", color=G,
                      label=r"$|R^{\rm NR}/(WR\alpha)-1|$, largest")
        ax[1, 1].axhline(1.0, **fs.MASK_LINE)
        ax[1, 1].axhline(0.1, **fs.MASK_LINE)
        ax[1, 1].set_xscale("log")
        ax[1, 1].set_yscale("log")
        ax[1, 1].set_xlabel("cells per shortest wavelength of the sources")
        ax[1, 1].set_ylabel("first-order over second-order part (largest in time)")
        ax[1, 1].legend(loc="lower left", fontsize=7)
    fig.savefig(os.path.join(out, "fig_twin.png"), dpi=200)
    print("A done:", os.path.join(out, "summary.json"))


def inv_q(nc, inv):
    """|n| of the canonical wave vectors."""
    return np.sqrt((nc.astype(float)**2).sum(axis=1))


if __name__ == "__main__":
    main()
