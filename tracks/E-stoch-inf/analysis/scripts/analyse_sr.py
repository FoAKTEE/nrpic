#!/usr/bin/env python3
"""Analysis of a slow-roll scouting run made from make_sr_case.py (release executable,
homogeneous start, Mukhanov-Sasaki sources) with the estimators of ../sfa.py:

- R^NR (P-c) per dump, with the gt term from the bin output (single precision) and
  without it (what the dump alone allows); per-mode coefficients against the code's own
  linear prediction L^(-3/2) W_q R_q alpha_n (lockstep R_q, a, H of the .modes record);
- the code's lockstep R_q against an independent SciPy integration of the same mode
  equation from the same data (nrpic.scalar_field.ms_reference);
- freezing: drift of ln |c_n|^2 per e-fold from N_k + 4 to the end (SPEC 7.3);
- constraint ratios <|H|>/<[H]> (the code's [H]) and rms M / rms [M] per dump;
- shell spectra at the end.

    analyse_sr.py --run DIR --out DIR [--control DIR]
Writes DIR/analyse_sr.json and figures DIR/fig_sr_*.png.
"""
import argparse
import glob
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import sfa  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402
from nrpic import scalar_field as nsf  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def load(run):
    case = json.load(open(os.path.join(run, "case.json")))
    hist = sfa.read_history(run)
    bins = {}
    for b in glob.glob(os.path.join(run, "**", "*.z4c.*.bin"), recursive=True):
        m = sfa.read_bin_metric(b)
        bins[m["cycle"]] = b
    out = []
    for f in sfa.dump_files(run):
        d = sfa.read_dump(f)
        mf = re.sub(r"\.dump$", ".modes", f)
        out.append(dict(file=f, cycle=d["cycle"], time=d["time"], modes=sfa.read_modes(mf),
                        bin=bins.get(d["cycle"])))
    return case, hist, out


def analyse_run(run):
    case, hist, recs = load(run)
    lat = sfa.Lattice(case["N"], case["L"], case["nmax2"])
    alpha = lat.alpha(case["seed"])
    shells = np.unique(lat.n2)
    rows = []
    v, dv = nsf.potential("quadratic", mass=case["mass"])
    mode0 = np.loadtxt(os.path.join(run, "modes.txt"))
    r0 = mode0[:, 1] + 1j * mode0[:, 2]
    dr0 = mode0[:, 3] + 1j * mode0[:, 4]
    times = np.array([r["time"] for r in recs])
    ref = nsf.ms_reference(v, dv, case["phi0"], case["pi0"], mode0[:, 0], r0, dr0, case["L"],
                           times)
    coefs = []
    for i, r in enumerate(recs):
        d = sfa.read_dump(r["file"])
        md = r["modes"]
        gt = None
        if r["bin"] is not None:
            gt = sfa.read_bin_metric(r["bin"])["gt"]
        est0 = sfa.curvature_perturbation(d, None)
        c0 = lat.coefficients(est0["R"])
        if gt is not None:
            est1 = sfa.curvature_perturbation(d, gt)
            c1 = lat.coefficients(est1["R"])
        else:
            est1, c1 = None, None
        cexp = sfa.expected_coefficients(lat, md, alpha)
        con = sfa.constraint_ratios(d, hist)
        # code's lockstep R_q against SciPy (shells in the order of the mode file)
        idx = {int(s): j for j, s in enumerate(md["n2"])}
        rq_code = np.array([md["R"][idx[int(s)]] for s in mode0[:, 0]])
        rq_ref = ref["R"][i]
        lock = float(np.max(np.abs(rq_code - rq_ref) / np.abs(rq_ref)))
        rows.append(dict(cycle=r["cycle"], time=r["time"], efolds=est0["efolds"],
                         a=md["head"]["a"], H=md["head"]["H"], eps1=md["head"]["eps1"],
                         rms_R_dump=float(np.std(est0["R"])),
                         rms_gt_term=(est1["rms_gt_term"] if est1 else None),
                         lockstep_vs_scipy=lock,
                         H_ratio_l1=con["ratio_H_l1"], H_ratio_rms=con["ratio_H_rms"],
                         M_ratio_rms=con["ratio_M_rms"], Hn_hist=con.get("Hn_hist"),
                         bin=r["bin"] is not None))
        coefs.append(dict(c0=c0, c1=c1, cexp=cexp))
    return case, lat, rows, coefs, shells


def crossing_efold(rows, k, sigma=1.0):
    """N at which sigma a H = k (W = 1/2), from the lockstep a, H of the records."""
    ln_akh = np.array([np.log(sigma * r["a"] * r["H"]) for r in rows])
    n = np.array([np.log(r["a"]) for r in rows])
    return np.interp(np.log(k), ln_akh, n, left=np.nan, right=np.nan)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--control")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    case, lat, rows, coefs, shells = analyse_run(a.run)
    fin = coefs[-1]
    nf = np.log(rows[-1]["a"])
    half = lat.n2 <= lat.nmax2 / 4
    res = dict(case=case, rows=rows)
    for key, lab in (("c1", "with_gt"), ("c0", "dump_only")):
        if fin[key] is None:
            continue
        ratio = fin[key] / fin["cexp"] - 1
        res[f"final_ratio_{lab}"] = dict(
            max_abs_half=float(np.abs(ratio[half]).max()),
            max_abs_all=float(np.abs(ratio).max()),
            mean_real_half=float(ratio[half].real.mean()),
            rms_half=float(np.sqrt(np.mean(np.abs(ratio[half]) ** 2))))
    # freezing drift from N_k + 4 to the end, per mode
    nk = crossing_efold(rows, lat.k)
    ns = np.array([np.log(r["a"]) for r in rows])
    drift = {}
    for key in ("c1", "c0", "cexp"):
        if fin[key] is None:
            continue
        dd = np.full(lat.k.size, np.nan)
        for j in range(lat.k.size):
            if not np.isfinite(nk[j]) or nf - nk[j] < 5.0:
                continue
            i0 = int(np.argmin(np.abs(ns - (nk[j] + 4.0))))
            dd[j] = sfa.drift(coefs[i0][key][j], fin[key][j], ns[i0], nf)
        drift[key] = dd
    sel = np.isfinite(drift["cexp"])
    res["drift"] = {k: dict(n_modes=int(sel.sum()), max_abs=float(np.nanmax(np.abs(v[sel])))
                            if sel.any() else None) for k, v in drift.items()}
    res["final_gt_term_over_R"] = (rows[-1]["rms_gt_term"] / rows[-1]["rms_R_dump"]
                                   if rows[-1]["rms_gt_term"] is not None else None)
    res["max_lockstep_vs_scipy"] = max(r["lockstep_vs_scipy"] for r in rows)
    res["max_H_ratio_l1"] = max(r["H_ratio_l1"] for r in rows)
    if a.control:
        cc, clat, crows, ccoefs, _ = analyse_run(a.control)
        res["control_rows"] = crows
        res["control_max_H_ratio_l1"] = max(r["H_ratio_l1"] for r in crows)
    with open(os.path.join(a.out, "analyse_sr.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)
    print(json.dumps({k: v for k, v in res.items() if k not in ("rows", "control_rows")},
                     indent=1, default=float))

    fs.use_style()
    tag = f"N{case['N']}"
    # 1: per-mode ratio at the end
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2))
    for key, col, lab in (("c1", fs.PAL["red"], r"with $\tilde\gamma_{ij}$ (bin)"),
                          ("c0", fs.PAL["yellow"], "dump only")):
        if fin[key] is None:
            continue
        ratio = fin[key] / fin["cexp"] - 1
        ax[0].plot(lat.q, ratio.real, ".", color=col, ms=4, label=lab + ", Re")
        ax[0].plot(lat.q, ratio.imag, "x", color=col, ms=3, label=lab + ", Im")
    ax[0].axvline(np.sqrt(lat.nmax2) / 2, **fs.MASK_LINE)
    ax[0].axhspan(-0.02, 0.02, color=fs.PAL["blue"], alpha=0.1)
    ax[0].set_xlabel(r"$|n|$")
    ax[0].set_ylabel(r"$c_n^{\rm NR}/(L^{-3/2}W_qR_q\alpha_n)-1$ at the end")
    ax[0].legend(fontsize=7)
    for j in np.argsort(lat.q)[[0, lat.q.size // 3, -1]]:
        y_nr = [abs(c["c1"][j] if c["c1"] is not None else c["c0"][j]) ** 2 for c in coefs]
        y_ex = [abs(c["cexp"][j]) ** 2 for c in coefs]
        l, = ax[1].semilogy(ns, y_nr, "-", label=f"NR, |n| = {lat.q[j]:.2f}")
        ax[1].semilogy(ns, y_ex, "--", color=l.get_color())
    ax[1].plot([], [], **fs.GUIDE, label=r"$L^{-3}|W_qR_q|^2$ (code's lockstep)")
    ax[1].set_xlabel(r"$N = \ln a$")
    ax[1].set_ylabel(r"$|c_n|^2$")
    ax[1].legend(fontsize=7)
    fig.subplots_adjust(left=0.1, right=0.98, bottom=0.15, top=0.95, wspace=0.3)
    fs.save(fig, os.path.join(a.out, f"fig_sr_permode_{tag}"))
    plt.close(fig)
    # 2: constraints, lockstep, drift
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
    ax[0].semilogy(ns, [r["H_ratio_l1"] for r in rows], "o-", color=fs.PAL["red"], ms=3,
                   label=r"$\langle|\mathcal{H}|\rangle/\langle[\mathcal{H}]\rangle$")
    ax[0].semilogy(ns, [r["M_ratio_rms"] for r in rows], "s-", color=fs.PAL["blue"], ms=3,
                   label=r"rms $\mathcal{M}$/rms $[\mathcal{M}]$")
    if a.control:
        cns = [np.log(r["a"]) for r in crows]
        ax[0].semilogy(cns, [r["H_ratio_l1"] for r in crows], "o:", color=fs.PAL["red"], ms=3,
                       label="control (sign of the $\\Pi$ kick)")
        ax[0].semilogy(cns, [r["M_ratio_rms"] for r in crows], "s:", color=fs.PAL["blue"], ms=3)
    ax[0].set_xlabel(r"$N$")
    ax[0].legend(fontsize=6)
    ax[1].semilogy(ns, [max(r["lockstep_vs_scipy"], 1e-17) for r in rows], "o-",
                   color=fs.PAL["red"], ms=3)
    ax[1].set_xlabel(r"$N$")
    ax[1].set_ylabel(r"max$_q|R_q^{\rm code}-R_q^{\rm SciPy}|/|R_q|$")
    for key, col, lab in (("c1", fs.PAL["red"], "NR, with gt"), ("c0", fs.PAL["yellow"],
                                                                 "NR, dump only"),
                          ("cexp", fs.PAL["blue"], r"$W_qR_q$ (lockstep)")):
        if key in drift:
            ax[2].plot(lat.q[sel], drift[key][sel], ".", color=col, ms=4, label=lab)
    ax[2].axhspan(-2.5e-3, 2.5e-3, color="grey", alpha=0.15)
    ax[2].axhline(-4 * case["eps1_start"], **fs.GUIDE, label=r"$-4\varepsilon_1$ (FLRW lattice)")
    ax[2].set_xlabel(r"$|n|$")
    ax[2].set_ylabel(r"d ln$|c_n|^2$/d$N$ from $N_k+4$")
    ax[2].legend(fontsize=6)
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.17, top=0.95, wspace=0.42)
    fs.save(fig, os.path.join(a.out, f"fig_sr_constraints_{tag}"))
    plt.close(fig)
    # 3: spectra at the end
    fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH, 3.0))
    for key, col, lab, mk in (("cexp", fs.PAL["blue"], r"$L^{-3/2}W_qR_q\alpha_n$", "-"),
                              ("c1", fs.PAL["red"], "NR, with gt", "o"),
                              ("c0", fs.PAL["yellow"], "NR, dump only", "x")):
        if fin[key] is None:
            continue
        k, dl, cnt = sfa.shell_spectrum(lat, fin[key])
        ax.loglog(k, dl, mk, color=col, ms=4, label=lab)
    ax.set_xlabel("$k$")
    ax.set_ylabel(r"$\Delta_\mathcal{R}(k)$ at the end")
    ax.legend(fontsize=7)
    fig.subplots_adjust(left=0.2, right=0.96, bottom=0.16, top=0.95)
    fs.save(fig, os.path.join(a.out, f"fig_sr_spectrum_{tag}"))
    plt.close(fig)


if __name__ == "__main__":
    main()
