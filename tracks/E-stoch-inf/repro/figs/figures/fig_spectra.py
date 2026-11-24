"""Figs. 3, 5 (P1:451-470) and 6 (P1:549-561) of arXiv:2512.14649 from the npz files of dumppass.py.

--kind R: binned Delta[R^NR] (solid: bin mean; band: bin min to max; P1:454) from the first to the last
time, and the Mukhanov-Sasaki expectation Delta_MS = k^3 |R_k|^2/(2 pi^2) of the lockstep `.modes`
file (dashed, unwindowed; up to k_max, where our mode file ends). Also a second figure <name>_ratio
with the measures at the last dump: per shell, NR over the realisation's linear power (same alpha_n)
and NR over Delta_MS with the cosmic-variance envelope 3/sqrt(count).
--kind K: three panels Delta[K], Delta[Kt] (sum_ij |Kt_ij(k)|^2), Delta[sqrt(3 Kt Kt/2)] in P1's
units (times (100 H*/Mpl)^2).
Bins: lattice shells |n|^2 with more than 10 independent modes (hemisphere count). k in P1's units.
Times: the dumps nearest to the e-folds --targets (default 0, 0.7, 1.4, 2.1, 2.8, 3.5, 5.5, last).

Usage: fig_spectra.py --pass DIR/LABEL [--pass ...] --case sr|usr --kind R|K --name fig3 --out OUT
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figlib as fl  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import figstyle as fs  # noqa: E402

MINCOUNT = 10


def load(dirs):
    rows = []
    for d in dirs:
        for p in sorted(glob.glob(os.path.join(d, "d*.npz"))):
            z = np.load(p)
            if "specR_mean" not in z.files:
                continue
            rows.append(dict(path=p, time=float(z["time"]), N=float(z["efolds_chi"])))
    rows.sort(key=lambda r: r["time"])
    out = []
    for r in rows:
        if out and abs(r["time"] - out[-1]["time"]) < 1e-9:
            continue
        out.append(r)
    return out


def pick(rows, targets):
    Ns = np.array([r["N"] for r in rows])
    idx = []
    for tg in targets:
        i = int(np.argmin(np.abs(Ns - tg)))
        if i not in idx:
            idx.append(i)
    if len(rows) - 1 not in idx:
        idx.append(len(rows) - 1)
    return sorted(idx)


def ratio_measures(z):
    """At one dump: per injected shell with count > 10, NR/lin - 1 and NR/MS - 1."""
    out = {}
    if "inj_n2" not in z.files:
        return out
    n2 = z["inj_n2"]
    cnt = z["inj_count"]
    sel = cnt > MINCOUNT
    r_lin = z["inj_pnr"] / z["inj_plin"] - 1.0
    # NR shell mean of Delta against the MS expectation (same n2)
    sh = dict(zip(z["shell_n2"].tolist(), range(z["shell_n2"].size)))
    j = np.array([sh[int(v)] for v in n2])
    dnr = z["specR_mean"][j]
    ms = dict(zip(z["ms_n2"].tolist(), z["ms_delta"].tolist()))
    dms = np.array([ms[int(v)] for v in n2])
    r_ms = dnr / dms - 1.0
    env = 3.0 / np.sqrt(cnt)
    out = dict(n2=n2[sel].tolist(), count=cnt[sel].tolist(), r_lin=r_lin[sel].tolist(),
               r_ms=r_ms[sel].tolist(), env=env[sel].tolist(),
               max_abs_r_lin=float(np.max(np.abs(r_lin[sel]))),
               rms_r_lin=float(np.sqrt(np.mean(r_lin[sel] ** 2))),
               frac_within_env=float(np.mean(np.abs(r_ms[sel]) < env[sel])),
               n_shells=int(sel.sum()))
    # the same restricted to k <= k_max/2
    half = sel & (n2 <= n2.max() / 4)
    out["max_abs_r_lin_half"] = float(np.max(np.abs(r_lin[half])))
    # above k_max: NR power against the MS expectation at the cut
    above = (z["shell_n2"] > n2.max()) & (z["shell_count"] > MINCOUNT)
    if above.any():
        out["max_above_kmax_over_ms_cut"] = float(z["specR_mean"][above].max() / dms[-1])
    if "inj_rel_rms" in z.files:
        out["per_mode_rel_rms"] = float(z["inj_rel_rms"])
        out["per_mode_rel_max"] = float(z["inj_rel_max"])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass", dest="passes", action="append", required=True)
    ap.add_argument("--case", required=True)
    ap.add_argument("--kind", default="R")
    ap.add_argument("--name", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--targets", default="0,0.7,1.4,2.1,2.8,3.5,5.5")
    ap.add_argument("--title", default="")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    rows = load(args.passes)
    sel = pick(rows, [float(x) for x in args.targets.split(",")])
    fs.use_style()
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
        "time", ["#1f2a7a", "#3b75c4", "#4aa3a0", "#b8a640", "#e57b2a", "#c4222b"])
    cols = [cmap(x) for x in np.linspace(0.0, 1.0, len(sel))]
    res = dict(case=args.case, kind=args.kind, dumps=[rows[i]["path"] for i in sel],
               efolds=[rows[i]["N"] for i in sel])
    if args.kind == "R":
        fig, ax = plt.subplots(1, 1, figsize=(fs.FULL_WIDTH, 4.2))
        fig.subplots_adjust(left=0.09, right=0.98, bottom=0.12, top=0.93)
        axes = [ax]
        keys = [("specR", r"$\Delta[\mathcal{R}^{\rm NR}_k]$")]
        scale = 1.0
    else:
        fig, axes = plt.subplots(1, 3, figsize=(1.5 * fs.FULL_WIDTH, 3.8), sharey=True)
        fig.subplots_adjust(left=0.06, right=0.99, bottom=0.14, top=0.92, wspace=0.0)
        keys = [("specK", r"$\Delta[K_k]$"), ("specKt", r"$\Delta[\tilde K_{ij,k}]$"),
                ("specQ", r"$\Delta[\sqrt{3\tilde K_{ij}\tilde K^{ij}/2}_k]$")]
        scale = fl.rate_p1(args.case) ** 2
    res["curves"] = []
    for c, i in zip(cols, sel):
        z = np.load(rows[i]["path"])
        good = z["shell_count"] > MINCOUNT
        k = fl.k_p1(np.sqrt(z["shell_n2"][good].astype(float)), args.case)
        cur = dict(N=rows[i]["N"], time=rows[i]["time"])
        for a, (key, lab) in zip(axes, keys):
            if key + "_mean" not in z.files:
                continue
            m = z[key + "_mean"][good] * scale
            lo = z[key + "_min"][good] * scale
            hi = z[key + "_max"][good] * scale
            a.fill_between(k, np.maximum(lo, 1e-60), hi, color=c, alpha=0.12, lw=0,
                           rasterized=True)
            a.plot(k, m, color=c, lw=0.7, rasterized=True,
                   label=rf"$\langle\mathcal{{N}}\rangle$ = {rows[i]['N']:.2f}")
            cur[key + "_kmax_mean"] = float(np.median(m[-200:]))
        if args.kind == "R" and "ms_delta" in z.files:
            kms = fl.k_p1(np.sqrt(z["ms_n2"].astype(float)), args.case)
            axes[0].plot(kms, z["ms_delta"], color=c, lw=1.0, ls="--")
            cur["ms_delta_kmin"] = float(z["ms_delta"][0])
            cur["ms_delta_kmax"] = float(z["ms_delta"][-1])
        res["curves"].append(cur)
    for a, (key, lab) in zip(axes, keys):
        a.set_xscale("log")
        a.set_yscale("log")
        a.set_xlabel(r"comoving wave number $k$ [$M_{\rm Pl}=100$]")
        a.set_title(lab, fontsize=10)
        kk = fl.k_p1(np.array([2.0, 128 * np.sqrt(3.0)]), args.case)
        a.set_xlim(kk[0], kk[1])
    if args.kind == "R":
        axes[0].set_ylim(1e-20, None)
        axes[0].plot([], [], color="k", ls="--", lw=1.0, label=r"$\Delta[\mathcal{R}^{\rm MS}_k]$")
        axes[0].legend(loc="lower left", ncol=3, fontsize=7)
        axes[0].set_ylabel(r"$\Delta$")
    else:
        axes[0].legend(loc="lower left", ncol=2, fontsize=7)
        axes[0].set_ylabel(r"$\Delta$  [$M_{\rm Pl}=100$]")
        lo = min(a.get_ylim()[0] for a in axes)
        for a in axes:
            a.set_ylim(max(lo, 1e-45), None)
    if args.title:
        fig.suptitle(args.title, fontsize=10)
    fs.save(fig, os.path.join(args.out, args.name))
    plt.close(fig)

    # ---- measures at the last dump
    zl = np.load(rows[-1]["path"])
    if args.kind == "R":
        res["last"] = ratio_measures(zl)
        res["last"]["N"] = rows[-1]["N"]
        m = res["last"]
        if m:
            fig, ax = plt.subplots(2, 1, figsize=(fs.FULL_WIDTH, 4.6), sharex=True)
            fig.subplots_adjust(left=0.1, right=0.98, bottom=0.11, top=0.95, hspace=0.0)
            k = fl.k_p1(np.sqrt(np.array(m["n2"], float)), args.case)
            ax[0].semilogy(k, np.abs(m["r_lin"]), color=fs.PAL["red"], lw=0.8,
                           label=r"$|\Delta_{\rm NR}/\Delta_{\rm lin}-1|$ (same $\alpha_n$)")
            ax[0].legend(loc="upper left", fontsize=8)
            ax[1].plot(k, m["r_ms"], color=fs.PAL["blue"], lw=0.8,
                       label=r"$\Delta_{\rm NR}/\Delta_{\rm MS}-1$")
            ax[1].fill_between(k, -np.array(m["env"]), m["env"], color="grey", alpha=0.25, lw=0,
                               label=r"$\pm 3/\sqrt{\rm count}$")
            ax[1].legend(loc="upper right", fontsize=8)
            ax[1].set_xscale("log")
            ax[1].set_xlabel(r"comoving wave number $k$ [$M_{\rm Pl}=100$]")
            ax[0].set_title(f"{args.title} last dump, " + rf"$\langle\mathcal{{N}}\rangle$ = "
                            f"{rows[-1]['N']:.2f}", fontsize=10)
            fs.save(fig, os.path.join(args.out, args.name + "_ratio"))
            plt.close(fig)
    else:
        # freezing / decay of Delta[K] per shell (|n| <= 32), anisotropic hierarchy at the last dump
        allrows = [np.load(r["path"]) for r in rows]
        n2 = zl["shell_n2"]
        good = (zl["shell_count"] > MINCOUNT) & (n2 <= 1024)
        Ns = np.array([r["N"] for r in rows])
        K = np.array([z["specK_mean"][good] for z in allrows])
        res["K_ratio_last_over_N55"] = None
        i55 = int(np.argmin(np.abs(Ns - 5.5)))
        rk = K[-1] / K[i55]
        res["K_last_over_N55"] = dict(median=float(np.median(rk)), min=float(rk.min()),
                                      max=float(rk.max()), N55=float(Ns[i55]))
        res["K_last_over_max"] = dict(median=float(np.median(K[-1] / K.max(axis=0))),
                                      max=float(np.max(K[-1] / K.max(axis=0))))
        if "specKt_mean" in zl.files:
            Kt = np.array([z["specKt_mean"][good] for z in allrows])
            i45 = int(np.argmin(np.abs(Ns - 4.5)))
            res["Kt_last_over_N45"] = dict(median=float(np.median(Kt[-1] / Kt[i45])),
                                           max=float(np.max(Kt[-1] / Kt[i45])), N45=float(Ns[i45]))
            inj = (zl["shell_count"] > MINCOUNT) & (n2 <= 4096)
            q_over_k = zl["specQ_mean"][inj] / zl["specK_mean"][inj]
            res["Q_over_K_last"] = dict(median=float(np.median(q_over_k)),
                                        max=float(q_over_k.max()), min=float(q_over_k.min()),
                                        frac_below_1em2=float(np.mean(q_over_k < 1e-2)))
            # at every dump: fraction of injected shells where Q is below K
            res["Q_below_K_frac_by_dump"] = [
                float(np.mean(z["specQ_mean"][inj] < z["specK_mean"][inj])) for z in allrows]
            res["efolds_all"] = Ns.tolist()
    with open(os.path.join(args.out, args.name + ".json"), "w") as fp:
        json.dump(res, fp, indent=1)


if __name__ == "__main__":
    main()
