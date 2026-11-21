#!/usr/bin/env python3
"""Test A on the inflection case (tracks/core/JOURNAL-scalar3.md): the linear twin of
the mesh (nrpic.sf_lattice) for the ultra-slow-roll runs of test U, against their dumps.

    python3 a2_twin_usr.py --data DIR [DIR ...] [--out DIR] [--n 32] [--nmax2 64]
                           [--pair p01:m01:0.1] [--prefix ""] [--modefile FILE]
                           [--tmax T]

DIR holds the run directories of u1_usr.py (or of the card list, with --prefix).  For
the pair of runs with the mode scales +s and -s: the part of R^NR, of H and of M_i odd
in s from the dumps against the twin, mode by mode and in rms; and the deviation of the
twin from the continuum reference W R alpha (the lattice error of the entering shells,
which the twin predicts).  Writes OUT/summary.json and OUT/fig_twin_usr.png."""
import argparse
import os
import time

import s3
from s3 import common, inf, np, sf
from nrpic import sf_lattice as sl

BASE = "usr"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", nargs="+", required=True,
                    help="directories that hold the run directories (searched in order)")
    ap.add_argument("--out")
    ap.add_argument("--n", type=int, default=32)
    ap.add_argument("--nmax2", type=int, default=64)
    ap.add_argument("--pair", default="p01:m01:0.1")
    ap.add_argument("--prefix", default="")
    ap.add_argument("--modefile")
    ap.add_argument("--tmax", type=float, default=1e9)
    ap.add_argument("--rtol", type=float, default=1e-10)
    a = ap.parse_args()
    out = s3.run_dir(a.out)
    kp, km, sc = a.pair.split(":")
    sc = float(sc)
    case = s3.case("usr", 1)
    v, dv, phi0, pi0 = inf.code_background(case)
    d2v = inf.code_d2v(case)
    if a.modefile:
        sh_n2, sh_r, sh_dr = inf.read_mode_file(a.modefile)
    else:
        cm = s3.case("usr", a.nmax2)
        sh_n2, sh_r, sh_dr = cm["n2"], cm["R"], cm["dR"]
    n, n2 = sf.mode_set(a.nmax2)
    al = sf.mode_alpha(s3.SEED, 0, 0, n)
    q = np.sqrt(n2.astype(float))
    qtop = float(q.max())
    nc, inv = sl.canonical(n)
    def find(name):
        for d in a.data:
            p = os.path.join(d, a.prefix + name)
            if os.path.exists(os.path.join(p, BASE + ".sf.hst")):
                return p
        raise SystemExit(f"run {a.prefix + name} not found in {a.data}")

    rp_dir, rm_dir = find(kp), find(km)
    dp = s3.dumps(rp_dir, BASE)
    dm = s3.dumps(rm_dir, BASE)
    cyc = [c for c in sorted(set(dp) & set(dm)) if dp[c]["time"] <= a.tmax]
    times = np.array([dp[c]["time"] for c in cyc])
    t0 = time.time()
    tw = sl.Twin(nc, a.n, s3.LENGTH, v, dv, d2v, phi0, pi0, sh_n2, sh_r, sh_dr)
    sol = tw.integrate(times[1:], rtol=a.rtol)
    dg = tw.diagnostics(sol)
    # the twin with the time integration of the code, at the steps of the run
    hist = sf.read_history(os.path.join(rp_dir, BASE + ".sf.hst"))
    twc = sl.CodeTwin(nc, a.n, s3.LENGTH, v, dv, d2v, phi0, pi0, sh_n2, sh_r, sh_dr)
    solc = twc.integrate_steps(hist["time"], cyc)
    dgc = twc.diagnostics(solc)
    itc = {int(c): i for i, c in enumerate(solc["cycle"])}
    summ = dict(data=[os.path.abspath(rp_dir), os.path.abspath(rm_dir)], pair=a.pair, n=a.n, nmax2=a.nmax2,
                modes=int(n.shape[0]), canonical=int(nc.shape[0]),
                wall_twin_s=round(time.time() - t0, 1), rows=[])
    keep = []
    for it, c in enumerate(cyc[1:]):
        fp, fm = dp[c]["fields"], dm[c]["fields"]
        ent = dg["w"][it][inv] > 0.5
        tw_r = sc*dg["rnr"][it][inv]*al
        ref = sc*dg["ref"][it][inv]*al
        row = dict(time=float(times[it+1]), efolds=float(sol["ln_a"][it]),
                   eps1=float(sol["eps1"][it]), eps2=float(sol["eps2"][it]),
                   modes_in=int(ent.sum()))
        dev_tw = np.abs(tw_r/ref - 1.0)
        for lab, sel in (("n_le_2", ent & (q <= 2.0 + 1e-9)),
                         ("n_le_4", ent & (q <= 4.0 + 1e-9)),
                         ("top_shell", ent & (q >= qtop - 1e-9)), ("all_in", ent)):
            if sel.any():
                row["twin_vs_ref_" + lab] = float(dev_tw[sel].max())
        if "gxx" in fp and "gxx" in fm:
            rp, _ = s3.rnr_of_dump(dp[c], n, n2)
            rm, _ = s3.rnr_of_dump(dm[c], n, n2)
            odd = 0.5*(rp - rm)
            dev_d = np.abs(odd/tw_r - 1.0)
            dev_r = np.abs(odd/ref - 1.0)
            for lab, sel in (("n_le_2", ent & (q <= 2.0 + 1e-9)),
                             ("n_le_4", ent & (q <= 4.0 + 1e-9)),
                             ("top_shell", ent & (q >= qtop - 1e-9)), ("all_in", ent)):
                if sel.any():
                    row["odd_vs_twin_" + lab] = float(dev_d[sel].max())
                    row["odd_vs_ref_" + lab] = float(dev_r[sel].max())
            keep.append((row["efolds"], q[ent], dev_r[ent], dev_tw[ent], dev_d[ent]))
            if c in itc:
                tc_r = sc*dgc["rnr"][itc[c]][inv]*al
                dev_c = np.abs(odd/tc_r - 1.0)
                for lab, sel in (("n_le_2", ent & (q <= 2.0 + 1e-9)),
                                 ("n_le_4", ent & (q <= 4.0 + 1e-9)),
                                 ("top_shell", ent & (q >= qtop - 1e-9)),
                                 ("all_in", ent)):
                    if sel.any():
                        row["odd_vs_codetwin_" + lab] = float(dev_c[sel].max())
        if "H" in fp:
            oh = 0.5*(fp["H"] - fm["H"])
            om = [0.5*(fp[x] - fm[x]) for x in ("Mx", "My", "Mz")]
            hh = sc*dg["dH"][it][inv]*al
            mm = sc*dg["dM"][it][inv]*al[:, None]
            row.update(H_odd_meas=s3.rms(oh),
                       H_odd_twin=float(np.sqrt(2.0*(np.abs(hh)**2).sum())),
                       M_odd_meas=float(np.sqrt(sum((x*x).mean() for x in om))),
                       M_odd_twin=float(np.sqrt(2.0*(np.abs(mm)**2).sum())))
            row["H_odd_twin_over_meas"] = row["H_odd_twin"]/row["H_odd_meas"]
            row["M_odd_twin_over_meas"] = row["M_odd_twin"]/row["M_odd_meas"]
            if c in itc:
                i2 = itc[c]
                hc = sc*dgc["dH"][i2][inv]*al
                mc = sc*dgc["dM"][i2][inv]*al[:, None]
                ch, _ = sf.analyse(oh, n)
                row.update(
                    H_odd_codetwin=float(np.sqrt(2.0*(np.abs(hc)**2).sum())),
                    M_odd_codetwin=float(np.sqrt(2.0*(np.abs(mc)**2).sum())),
                    H_coef_maxdiff_over_rms=float(
                        np.abs(ch - hc).max()/np.sqrt((np.abs(ch)**2).mean())),
                    H0_codetwin=float(solc["H0"][i2]),
                    Pi0_codetwin=float(solc["Pi0"][i2]),
                    Pi_box_mean_plus=float(fp["Pi"].mean()))
                row["H_odd_codetwin_over_meas"] = row["H_odd_codetwin"]/row["H_odd_meas"]
                row["M_odd_codetwin_over_meas"] = row["M_odd_codetwin"]/row["M_odd_meas"]
        summ["rows"].append(row)
    common.dump_json(summ, os.path.join(out, "summary.json"))

    fs = common.style()
    import matplotlib.pyplot as plt
    from matplotlib import cm
    B, R_, G, O = (fs.PAL[x] for x in ("blue", "red", "green", "orange"))
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.075, right=0.99, bottom=0.16, top=0.95, wspace=0.32)
    rows = summ["rows"]
    ne = [r["efolds"] for r in rows]
    for lab, cl, lbl in (("n_le_2", B, r"$|n|\leq2$"), ("n_le_4", G, r"$|n|\leq4$"),
                         ("top_shell", R_, "top shell")):
        ax[0].plot(ne, [r.get("odd_vs_ref_" + lab, np.nan) for r in rows], "o", ms=3,
                   mfc="none", color=cl, label=lbl + ": runs")
        ax[0].plot(ne, [r.get("twin_vs_ref_" + lab, np.nan) for r in rows], "-",
                   color=cl, label=lbl + ": twin")
        ax[1].plot(ne, [r.get("odd_vs_twin_" + lab, np.nan) for r in rows], "o-", ms=3,
                   color=cl, label=lbl)
        ax[1].plot(ne, [r.get("odd_vs_codetwin_" + lab, np.nan) for r in rows], "s:",
                   ms=3, mfc="none", color=cl)
    ax[0].set_yscale("log")
    ax[0].set_xlabel("e-folds after $N_*$")
    ax[0].set_ylabel(r"largest $|R^{\rm NR}_n/(W R\,\alpha_n)-1|$ (odd in $s$)")
    ax[0].legend(loc="lower right", fontsize=6, ncol=2)
    ax[1].set_yscale("log")
    ax[1].set_xlabel("e-folds after $N_*$")
    ax[1].set_ylabel(r"largest $|R^{\rm NR}_n/R^{\rm twin}_n-1|$ (dotted: with time int.)")
    ax[1].legend(loc="upper left", fontsize=7)
    if rows and "H_odd_meas" in rows[0]:
        ax[2].plot(ne, [r["H_odd_meas"]/sc for r in rows], "o", ms=3, mfc="none",
                   color=B, label=r"$\mathcal{H}$: runs")
        ax[2].plot(ne, [r["H_odd_twin"]/sc for r in rows], "-", color=B,
                   label=r"$\mathcal{H}$: twin")
        ax[2].plot(ne, [r["M_odd_meas"]/sc for r in rows], "s", ms=3, mfc="none",
                   color=R_, label=r"$|\mathcal{M}|$: runs")
        ax[2].plot(ne, [r["M_odd_twin"]/sc for r in rows], "-", color=R_,
                   label=r"$|\mathcal{M}|$: twin")
        ax[2].plot(ne, [r.get("H_odd_codetwin", np.nan)/sc for r in rows], ":",
                   color=B, label="with the time integration")
        ax[2].plot(ne, [r.get("M_odd_codetwin", np.nan)/sc for r in rows], ":",
                   color=R_)
        ax[2].set_yscale("log")
        ax[2].set_xlabel("e-folds after $N_*$")
        ax[2].set_ylabel("rms of the part odd in $s$, over $s$")
        ax[2].legend(loc="upper right", fontsize=7)
    fig.savefig(os.path.join(out, "fig_twin_usr.png"), dpi=200)
    print("A (inflection case) done:", os.path.join(out, "summary.json"))


if __name__ == "__main__":
    main()
