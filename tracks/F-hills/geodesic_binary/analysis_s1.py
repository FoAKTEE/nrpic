"""Analysis of the S1 reproduction scan against 2404 section IV.

    <venv>/bin/python -I analysis_s1.py <s1.npz> <digitized-dir or -> <outdir>

<digitized-dir> holds sep_fraction.json, v8-asymp.json, frac-surv-Rgr-2.json written by
digitize_2404.py from kb-data/raw/arxiv/2404.16270/v1/src/Figures/ (curves read from the
paper's vector figures; calibration constants below come from the tick marks in those files).
Writes s1_summary.json and the figures s1_sepfrac, s1_vinf, s1_bound.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "python"))
from nrpic import figstyle as fs  # noqa: E402

C_KMS = 299792.458


# ---- digitized curves of 2404 (calibration from the tick marks of each PDF) ----
def _xy(points, x0, x1, xv0, xv1, y0, y1, yv0, yv1):
    p = np.array(points)
    x = xv0 + (p[:, 0] - x0) / (x1 - x0) * (xv1 - xv0)
    y = yv0 + (p[:, 1] - y0) / (y1 - y0) * (yv1 - yv0)
    return x, y


def paper_sepfrac(ddir):
    d = json.load(open(os.path.join(ddir, "sep_fraction.json")))
    cal = (36.285756, 259.485756, 0, 10, 39.971353, 191.171353, 0, 1)
    cur = [_xy(c["points"], *cal) for c in d["curves"]]
    # plotting order in the file (identified by the values at beta = 10 and the legend):
    # retrograde Newton, 1PN, HRNA, then prograde Newton, 1PN, HRNA
    names = ["retro_newton", "retro_1pn", "retro_hrna", "pro_newton", "pro_1pn", "pro_hrna"]
    return dict(zip(names, cur))


def paper_vinf(ddir):
    d = json.load(open(os.path.join(ddir, "v8-asymp.json")))
    calx = (31.662949, 280.618185, 0, 10)
    top = calx + (174.382127, 195.084283, 0, 3)          # prograde, 10^3 km/s
    bot = calx + (34.069003, 65.302884, 0, 1)            # retrograde
    c = d["curves"]
    out = {}
    for name, cc, cal in (("pro_hrna_band", c[0], top), ("pro_newton_band", c[1], top),
                          ("pro_hrna_mean", c[2], top), ("pro_newton_mean", c[3], top),
                          ("retro_hrna_band", c[4], bot), ("retro_newton_band", c[5], bot),
                          ("retro_hrna_mean", c[6], bot), ("retro_newton_mean", c[7], bot)):
        x, y = _xy(cc["points"], *cal)
        if name.endswith("band"):
            # polygon: split into upper and lower envelopes on a beta grid
            xs = np.linspace(x.min(), x.max(), 200)
            up, lo = [], []
            for xi in xs:
                m = np.abs(x - xi) < 0.06
                up.append(y[m].max() if m.any() else np.nan)
                lo.append(y[m].min() if m.any() else np.nan)
            out[name] = (xs, np.array(lo), np.array(up))
        else:
            out[name] = (x, y)
    return out


def paper_bound(ddir):
    d = json.load(open(os.path.join(ddir, "frac-surv-Rgr-2.json")))
    cal = (36.285756, 259.485756, 0, 10, 39.971353, 191.171353, 0, 1)
    cur = [_xy(c["points"], *cal) for c in d["curves"]]
    hr = cur[0]
    # the two blue curves: the one closer to HRNA for 2 <= beta <= 6 is 1PN (article.tex:760)
    g = np.linspace(2.5, 6, 30)
    dev = [np.mean(np.abs(np.interp(g, c[0], c[1]) - np.interp(g, hr[0], hr[1]))) for c in cur[1:]]
    i1pn = 1 + int(np.argmin(dev))
    inew = 3 - i1pn
    return dict(retro_hrna=hr, retro_1pn=cur[i1pn], retro_newton=cur[inew])


def main(npz, ddir, outdir):
    os.makedirs(outdir, exist_ok=True)
    d = np.load(npz)
    meta = json.loads(str(d["meta"]))
    laws, senses = meta["laws"], meta["senses"]
    betas = d["betas"]
    sep = d["separated"] > 0
    il = {k: laws.index(k) for k in laws}
    js = {s: senses.index(s) for s in senses}
    S = {}
    for law in laws:
        for s, sn in ((1, "pro"), (-1, "retro")):
            i, j = il[law], js[s]
            sp = sep[i, j]
            vinf = d["vinf"][i, j] * C_KMS
            v_mean = np.array([vinf[b][sp[b]].mean() if sp[b].any() else 0.0 for b in range(len(betas))])
            v_min = np.array([vinf[b][sp[b]].min() if sp[b].any() else 0.0 for b in range(len(betas))])
            v_max = np.array([vinf[b][sp[b]].max() if sp[b].any() else 0.0 for b in range(len(betas))])
            surv = ~sp
            bound = d["eps_cm"][i, j] < 0
            fb = np.array([(bound[b] & surv[b]).sum() / surv[b].sum() if surv[b].any() else np.nan
                           for b in range(len(betas))])
            S[f"{sn}_{law}"] = dict(sf=sp.mean(-1), v_mean=v_mean, v_min=v_min, v_max=v_max,
                                    bound_frac=fb, alpha_all_max=d["alpha_all"][i, j].max(-1),
                                    plunged=(d["plunged"][i, j] > 0).sum(-1),
                                    status_bad=((d["status"][i, j] >= 2) & (d["status"][i, j] != 5)).sum(-1))
    summ = {"betas": betas.tolist(), "n_phases": int(sep.shape[-1])}
    for k, v in S.items():
        summ[k] = {kk: np.asarray(vv).tolist() for kk, vv in v.items()}
    # ---- checks P1-P6 ----
    chk = {}
    for law in ("newton", "hrna"):
        sf = S[f"retro_{law}"]["sf"]
        chk[f"P1_retro_onset_{law}"] = float(betas[np.argmax(sf > 0.01)])
    dpro = np.abs(S["pro_hrna"]["sf"] - S["pro_newton"]["sf"])
    chk["P2_pro_max_abs_diff_beta_le_9"] = float(dpro[betas <= 9].max())
    sel = (betas >= 3) & (betas <= 10)
    rel = S["retro_hrna"]["sf"][sel] / S["retro_newton"]["sf"][sel] - 1
    chk["P3_retro_max_rel_excess_beta3to10"] = float(rel.max())
    chk["P3_retro_max_abs_excess"] = float((S["retro_hrna"]["sf"] - S["retro_newton"]["sf"]).max())
    vm_h, vm_n = S["retro_hrna"]["v_mean"], S["retro_newton"]["v_mean"]
    ok = vm_n > 0
    chk["P4_retro_vmean_max_rel_excess"] = float((vm_h[ok] / vm_n[ok] - 1).max())
    chk["P4_retro_vmean_max_abs_excess_kms"] = float((vm_h[ok] - vm_n[ok]).max())
    selp = betas > 9
    chk["P5_pro_vmax_excess_kms_beta_gt_9"] = float((S["pro_hrna"]["v_max"][selp] - S["pro_newton"]["v_max"][selp]).max())
    sel8 = betas > 8
    chk["P6_retro_bound_frac_beta_gt_8_hrna_mean"] = float(np.nanmean(S["retro_hrna"]["bound_frac"][sel8]))
    chk["P6_retro_bound_frac_beta_gt_8_newton_mean"] = float(np.nanmean(S["retro_newton"]["bound_frac"][sel8]))
    selw = (betas >= 0.5) & (betas <= 1.2)
    chk["P6_retro_beta0.5to1.2_sf_max"] = float(max(S["retro_hrna"]["sf"][selw].max(), S["retro_newton"]["sf"][selw].max()))
    chk["P6_retro_beta0.5to1.2_bound_frac_min_hrna"] = float(np.nanmin(S["retro_hrna"]["bound_frac"][selw]))
    chk["P6_retro_beta0.5to1.2_bound_frac_min_newton"] = float(np.nanmin(S["retro_newton"]["bound_frac"][selw]))
    chk["alpha_all_max_beta_le_10"] = float(max(S[k]["alpha_all_max"].max() for k in S if "hrna" in k))
    chk["runs_status_tmax_or_maxsteps"] = int(sum(S[k]["status_bad"].sum() for k in S))
    chk["members_captured"] = int(sum(S[k]["plunged"].sum() for k in S))
    # comparison with the digitized curves
    if ddir != "-":
        P = paper_sepfrac(ddir)
        for k in ("retro_newton", "retro_hrna", "pro_newton", "pro_hrna"):
            x, y = P[k]
            sel = (betas >= x.min()) & (betas <= x.max())
            chk[f"digitized_sf_max_abs_dev_{k}"] = float(np.max(np.abs(np.interp(betas[sel], x, y) - S[k]["sf"][sel])))
            chk[f"digitized_sf_mean_abs_dev_{k}"] = float(np.mean(np.abs(np.interp(betas[sel], x, y) - S[k]["sf"][sel])))
        V = paper_vinf(ddir)
        for k in ("pro_hrna", "pro_newton", "retro_hrna", "retro_newton"):
            x, y = V[k + "_mean"]
            m = S[k]["v_mean"] > 0
            sel = m & (betas >= x.min()) & (betas <= x.max())
            yp = np.interp(betas[sel], x, y) * 1e3
            chk[f"digitized_vmean_max_rel_dev_{k}"] = float(np.max(np.abs(S[k]["v_mean"][sel] / yp - 1)))
            xs, lo, up = V[k + "_band"]
            chk[f"digitized_vmax_at_beta10_{k}_paper_kms"] = float(np.interp(9.95, xs, up) * 1e3)
            chk[f"vmax_at_beta10_{k}_ours_kms"] = float(S[k]["v_max"][-1])
        B = paper_bound(ddir)
        for k in ("retro_hrna", "retro_newton"):
            x, y = B[k]
            sel = (betas >= 1.0) & (betas <= x.max()) & np.isfinite(S[k]["bound_frac"])
            chk[f"digitized_bound_max_abs_dev_{k}_beta_ge_1"] = float(np.max(np.abs(np.interp(betas[sel], x, y) - S[k]["bound_frac"][sel])))
    summ["checks"] = chk
    with open(os.path.join(outdir, "s1_summary.json"), "w") as fh:
        json.dump(summ, fh, indent=1)
    print(json.dumps(chk, indent=1))
    figures(S, betas, ddir, outdir)


def figures(S, betas, ddir, outdir):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fs.use_style()
    col = {"newton": fs.PAL["blue"], "hrna": fs.PAL["red"]}
    lab = {"newton": "Newton", "hrna": "HRNA"}
    P = paper_sepfrac(ddir) if ddir != "-" else None
    # separation fraction
    fig = plt.figure(figsize=(fs.COLUMN_WIDTH, 3.2))
    ax = fig.add_axes([0.16, 0.14, 0.8, 0.72])
    for law in ("newton", "hrna"):
        for sn in ("pro", "retro"):
            ax.plot(betas, S[f"{sn}_{law}"]["sf"], color=col[law], label=f"{lab[law]} (this work)" if sn == "pro" else None)
            if P is not None:
                x, y = P[f"{sn}_{law}"]
                ax.plot(x, y, color=col[law], ls=":", lw=1.5, label=f"{lab[law]} (2404, digitized)" if sn == "pro" else None)
    if P is not None:
        for sn in ("pro", "retro"):
            x, y = P[f"{sn}_1pn"]
            ax.plot(x, y, color="k", ls=":", lw=1.0, label="1PN (2404, digitized)" if sn == "pro" else None)
    ax.set_xlabel(r"$\beta = r_t/r_p$")
    ax.set_ylabel("separation fraction")
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.02, 1.02)
    ax.text(1.6, 0.86, "prograde")
    ax.text(5.6, 0.45, "retrograde")
    ax.legend(loc="lower right", fontsize=7)
    sec = ax.secondary_xaxis("top", functions=(lambda b: 101.3 / np.maximum(b, 1e-3), lambda r: 101.3 / np.maximum(r, 1e-3)))
    sec.set_xticks([101.3, 50.65, 20.26, 10.13])
    sec.set_xticklabels(["101", "51", "20", "10"])
    sec.set_xlabel(r"$r_p/r_g$", labelpad=2)
    fs.save(fig, os.path.join(outdir, "s1_sepfrac"))
    plt.close(fig)
    # ejection speed
    V = paper_vinf(ddir) if ddir != "-" else None
    fig = plt.figure(figsize=(fs.COLUMN_WIDTH, 4.6))
    axs = [fs.inch_axes(fig, 0.62, 2.45, 3.25, 2.0), fs.inch_axes(fig, 0.62, 0.42, 3.25, 2.0)]
    for ax, sn in zip(axs, ("pro", "retro")):
        for law in ("newton", "hrna"):
            s = S[f"{sn}_{law}"]
            m = s["v_mean"] > 0
            ax.plot(betas[m], s["v_mean"][m] / 1e3, color=col[law], label=f"{lab[law]} mean (this work)")
            ax.plot(betas[m], s["v_max"][m] / 1e3, color=col[law], ls="--", lw=1.0, label=f"{lab[law]} min, max" if sn == "pro" else None)
            ax.plot(betas[m], s["v_min"][m] / 1e3, color=col[law], ls="--", lw=1.0)
            if V is not None:
                x, y = V[f"{sn}_{law}_mean"]
                ax.plot(x, y, color=col[law], ls=":", label="2404 (digitized)" if law == "hrna" else None)
                xs, lo, up = V[f"{sn}_{law}_band"]
                fs.band(ax, xs, lo, up, col[law], alpha=0.12)
        ax.set_xlim(0, 10)
        ax.set_ylabel(r"$v_\infty\ [10^3\,{\rm km\,s^{-1}}]$")
        ax.text(0.3, 0.9 * ax.get_ylim()[1], "prograde" if sn == "pro" else "retrograde")
    axs[0].xaxis.set_major_formatter(plt.NullFormatter())
    axs[1].set_xlabel(r"$\beta$")
    axs[0].legend(loc="lower right", fontsize=7, ncol=2)
    fs.save(fig, os.path.join(outdir, "s1_vinf"))
    plt.close(fig)
    # bound fraction of retrograde survivors
    B = paper_bound(ddir) if ddir != "-" else None
    fig = plt.figure(figsize=(fs.COLUMN_WIDTH, 3.0))
    ax = fig.add_axes([0.16, 0.15, 0.8, 0.8])
    for law in ("newton", "hrna"):
        ax.plot(betas, S[f"retro_{law}"]["bound_frac"], color=col[law], label=f"{lab[law]} (this work)")
        if B is not None:
            x, y = B[f"retro_{law}"]
            ax.plot(x, y, color=col[law], ls=":", label="2404 (digitized)")
    if B is not None:
        x, y = B["retro_1pn"]
        ax.plot(x, y, color="k", ls=":", lw=1.0, label="1PN (2404)")
    ax.set_xlabel(r"$\beta$")
    ax.set_ylabel("bound fraction of survivors (retro)")
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.02, 1.02)
    ax.legend(loc="upper right", fontsize=7, ncol=2)
    fs.save(fig, os.path.join(outdir, "s1_bound"))
    plt.close(fig)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
