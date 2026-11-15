"""Separation probability and ejection energy from r_p = 1000 down to 4 r_g (S1 + S2).

    <venv>/bin/python -I analysis_strong.py <s1.npz> <s2.npz> <outdir>

Writes strong_summary.json (checks Q1-Q4 of JOURNAL.md) and the figure strong_rp.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "python"))
from nrpic import figstyle as fs  # noqa: E402

C_KMS = 299792.458


def load(path):
    d = np.load(path)
    meta = json.loads(str(d["meta"]))
    return d, meta


def stats(d, meta, law, sense):
    """Per beta: s.f.; capture (a member crossed r < 2.5 r_g inwards); point-mass near-collision
    (a_min < 1e-4 a0, where the Newtonian pair force drives the members to relativistic speed
    and the model is meaningless: reported, excluded from capture and speed statistics);
    runs stopped at t_max; ejection speed of the escaping member (also when its companion was
    captured)."""
    i, j = meta["laws"].index(law), meta["senses"].index(sense)
    sep = d["separated"][i, j] > 0
    coll = d["a_min"][i, j] < 1e-4
    cap = (d["plunged"][i, j] > 0) & ~coll
    tmax = d["status"][i, j] == 2
    v = d["vinf"][i, j] * C_KMS
    ej = sep & ~coll & (v > 0)
    nb = sep.shape[0]
    vm = np.array([v[b][ej[b]].mean() if ej[b].any() else np.nan for b in range(nb)])
    vx = np.array([v[b][ej[b]].max() if ej[b].any() else np.nan for b in range(nb)])
    vmed = np.array([np.median(v[b][ej[b]]) if ej[b].any() else np.nan for b in range(nb)])
    return dict(sf=sep.mean(-1), cap=cap.mean(-1), coll=coll.mean(-1), tmax=tmax.mean(-1),
                v_mean=vm, v_max=vx, v_med=vmed,
                alpha_med=np.median(d["alpha_max"][i, j], -1), alpha_max=d["alpha_max"][i, j].max(-1),
                alpha_all_med=np.median(np.where(coll, np.nan, d["alpha_all"][i, j]), -1),
                alpha_all_max=np.nanmax(np.where(coll, np.nan, d["alpha_all"][i, j]), -1),
                bad=((d["status"][i, j] >= 2) & (d["status"][i, j] != 5)).sum(-1))


def main(s1, s2, outdir):
    os.makedirs(outdir, exist_ok=True)
    d1, m1 = load(s1)
    d2, m2 = load(s2)
    a0, mb = m1["kw"]["a0"], m1["kw"]["mb"]
    rt = a0 * mb ** (-1 / 3)
    E0 = np.sqrt(mb / (a0 * rt))
    S = {}
    for law in ("newton", "hrna"):
        for s, sn in ((1, "pro"), (-1, "retro")):
            A, B = stats(d1, m1, law, s), stats(d2, m2, law, s)
            keep2 = d2["betas"] > d1["betas"].max() + 1e-9
            S[f"{sn}_{law}"] = {k: np.concatenate([A[k], B[k][keep2]]) for k in A}
    betas = np.concatenate([d1["betas"], d2["betas"][d2["betas"] > d1["betas"].max() + 1e-9]])
    rp = rt / betas
    chk = {}
    b20 = np.argmin(np.abs(betas - 20))
    chk["Q1_retro_sf_hrna_beta20"] = float(S["retro_hrna"]["sf"][b20])
    chk["Q1_retro_sf_newton_max_beta_le_25"] = float(S["retro_newton"]["sf"].max())
    sel18 = betas >= 18
    chk["Q1_retro_sf_hrna_min_beta_ge_18"] = float(S["retro_hrna"]["sf"][sel18].min())
    for sn in ("pro", "retro"):
        r = S[f"{sn}_hrna"]["v_mean"] / S[f"{sn}_newton"]["v_mean"] - 1
        chk[f"Q2_{sn}_vmean_rel_excess_beta20"] = float(r[b20])
        chk[f"Q2_{sn}_vmean_rel_excess_min_beta_ge_15"] = float(np.nanmin(r[betas >= 15]))
    for sn in ("pro", "retro"):
        c = S[f"{sn}_hrna"]["cap"]
        chk[f"Q3_{sn}_capture_frac_beta25"] = float(c[-1])
        chk[f"Q3_{sn}_first_beta_with_capture"] = float(betas[np.argmax(c > 0)]) if (c > 0).any() else None
        chk[f"Q3_{sn}_capture_frac_beta22.5"] = float(c[np.argmin(np.abs(betas - 22.5))])
    for sn in ("pro", "retro"):
        chk[f"Q4_{sn}_alpha_bound_max_beta15"] = float(S[f"{sn}_hrna"]["alpha_max"][np.argmin(np.abs(betas - 15))])
        chk[f"Q4_{sn}_alpha_bound_median_beta15"] = float(S[f"{sn}_hrna"]["alpha_med"][np.argmin(np.abs(betas - 15))])
        for bb in (8.5, 10, 15, 20):
            kb = int(np.argmin(np.abs(betas - bb)))
            chk[f"Q4_{sn}_alpha_all_max_beta{bb}"] = float(S[f"{sn}_hrna"]["alpha_all_max"][kb])
            chk[f"Q4_{sn}_alpha_all_median_beta{bb}"] = float(S[f"{sn}_hrna"]["alpha_all_med"][kb])
    chk["runs_status_tmax_or_maxsteps"] = int(sum(S[k]["bad"].sum() for k in S))
    for nm, dd in (("S1", d1), ("S2", d2)):
        chk[f"{nm}_runs_step_underflow"] = int((dd["status"] == 4).sum())
        chk[f"{nm}_runs_a_min_below_1e-4_a0"] = int((dd["a_min"] < 1e-4).sum())
        chk[f"{nm}_runs_total"] = int(dd["status"].size)
    table = []
    for b in (1, 2, 3, 5, 10, 15, 18, 20, 22, 24, 25):
        k = int(np.argmin(np.abs(betas - b)))
        row = dict(beta=float(betas[k]), rp=float(rp[k]))
        for key in S:
            row[f"sf_{key}"] = float(S[key]["sf"][k])
            row[f"vmean_kms_{key}"] = (float(S[key]["v_mean"][k]) if np.isfinite(S[key]["v_mean"][k]) else None)
            row[f"cap_{key}"] = float(S[key]["cap"][k])
            row[f"tmax_{key}"] = float(S[key]["tmax"][k])
            row[f"coll_{key}"] = float(S[key]["coll"][k])
        table.append(row)
    out = dict(checks=chk, table=table, r_t=rt, E0=E0,
               series={k: {kk: np.asarray(vv).tolist() for kk, vv in v.items()} for k, v in S.items()},
               betas=betas.tolist())
    with open(os.path.join(outdir, "strong_summary.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps(dict(checks=chk, table=table), indent=1))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fs.use_style()
    col = {"newton": fs.PAL["blue"], "hrna": fs.PAL["red"]}
    lab = {"newton": "Newton", "hrna": "HRNA"}
    ls = {"pro": "-", "retro": "--"}
    fig = plt.figure(figsize=(fs.COLUMN_WIDTH, 6.6))
    axs = [fs.inch_axes(fig, 0.66, 4.55, 3.2, 1.95), fs.inch_axes(fig, 0.66, 2.5, 3.2, 1.95),
           fs.inch_axes(fig, 0.66, 0.45, 3.2, 1.95)]
    for law in ("newton", "hrna"):
        for sn in ("pro", "retro"):
            s = S[f"{sn}_{law}"]
            lb = f"{lab[law]}, {'prograde' if sn == 'pro' else 'retrograde'}"
            axs[0].plot(rp, s["sf"], color=col[law], ls=ls[sn], label=lb)
            axs[1].plot(rp, s["v_mean"] / 1e3, color=col[law], ls=ls[sn])
            if law == "hrna":
                axs[2].plot(rp, s["cap"], color=col[law], ls=ls[sn], label=f"captured member, {sn}")
                axs[2].plot(rp, s["alpha_all_max"], color=fs.PAL["yellow"], ls=ls[sn], label=f"max $a/\\mathcal{{R}}$, {sn}")
    for ax in axs:
        ax.set_xscale("log")
        ax.set_xlim(rp.max() * 1.05, 3.8)
        ax.axvline(4.0, **fs.MASK_LINE)
        ax.axvline(10.13, **fs.MASK_LINE)
    axs[0].set_ylabel("separation fraction")
    axs[0].set_ylim(-0.02, 1.02)
    axs[0].legend(loc="upper left", fontsize=7)
    axs[0].text(9.0, 0.05, r"$\beta=10$", fontsize=8)
    axs[1].set_ylabel(r"$\langle v_\infty\rangle\ [10^3\,{\rm km\,s^{-1}}]$")
    axs[2].set_ylabel("fraction, ratio")
    axs[2].set_yscale("log")
    axs[2].set_ylim(1e-3, 1.5)
    axs[2].legend(loc="upper left", fontsize=7)
    axs[2].set_xlabel(r"$r_p/r_g$  ($r_t = 101.3\,r_g$, $m_b = 10^{-6}M$)")
    for ax in axs[:2]:
        ax.xaxis.set_major_formatter(plt.NullFormatter())
    fs.save(fig, os.path.join(outdir, "strong_rp"))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
