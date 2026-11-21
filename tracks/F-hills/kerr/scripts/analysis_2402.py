"""Analysis of the reproduction scan (scan_2402.py) against arXiv:2402.02178 (JOURNAL entry 3).

    <venv>/bin/python -I analysis_2402.py <scan_2402.json> <outdir>

1. Digitizes the paper's Figs. InclD and afin (vector content parsed as data by digitize_2402.py,
   calibrated by paper_2402.py) from kb-data/raw/arxiv/2402.02178/v1/src into
   <outdir>/paper_2402_digitized.json (numbers with locators; the figures are not copied).
2. K1/K2 (Fig. InclD): per family and r_p the lowest surviving iota on the paper's pi/6 grid, for
   every (node, phase) sample; median and range over samples against the paper's markers and
   against the Newtonian criterion Eq. (cosiN) (main.tex:572-577).
3. K3 (Fig. afin): survival map at r_p = 10 over the paper's 48 x 36 cells, per sample and averaged,
   against the paper's map (a_fin > 0); the first surviving iota per L_z row; survival fractions;
   a_fin of survivors.
Writes kerr_2402_summary.json and the figures fig_incld.png, fig_afin.png, fig_incld_sf.png.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
SRC = "/data/haiyangw/nrpic/kb-data/raw/arxiv/2402.02178/v1/src"
FAM_PAPER = {"pos": "s0.9_Lz_pos", "neg": "s0.9_Lz_neg", "zero": "s0.9_Lz_0", "s0": "s0_shaded"}
NONE = 7  # code for "no survivor on the pi/6 grid" (one step above pi)


def digitize(outdir):
    import digitize_2402 as D
    import paper_2402 as Pp
    d = os.path.join(outdir, "digitized_raw")
    os.makedirs(d, exist_ok=True)
    for name in ("InclD", "afin10M2e4"):
        D.main(os.path.join(SRC, name + ".pdf"), os.path.join(d, f"dig_{name}.json"))
    out = os.path.join(outdir, "paper_2402_digitized.json")
    Pp.main(d, out)
    return json.load(open(out))


def cosiN_iota(beta):
    """Lowest surviving iota of Eq. (cosiN): F^-1(iota) > 6 sqrt(pi) 2^(1/4) beta^(-3/4)
    exp[-(2 sqrt 2/3) beta^(-3/2)], F = (cos i + 1)(cos i + 5)^2/72 (F decreasing in iota)."""
    rhs = 6 * math.sqrt(math.pi) * 2 ** 0.25 * beta ** -0.75 * math.exp(-(2 * math.sqrt(2) / 3) * beta ** -1.5)
    F = lambda i: (math.cos(i) + 1) * (math.cos(i) + 5) ** 2 / 72  # noqa: E731
    if 1 / F(0.0) > rhs:
        return 0.0
    lo, hi = 0.0, math.pi - 1e-12
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        if 1 / F(mid) > rhs:
            hi = mid
        else:
            lo = mid
    return hi


def main(scan_path, outdir):
    os.makedirs(outdir, exist_ok=True)
    paper = digitize(outdir)
    S = json.load(open(scan_path))
    C = {k: np.array(v) for k, v in S["columns"].items()}
    FID = S["fiducial"]
    rt = (1 / FID["mb"]) ** (1 / 3) * FID["a0"]
    summ = dict(scan=os.path.abspath(scan_path), rt=rt, n=int(S["n"]),
                status_counts={str(k): int(v) for k, v in zip(*np.unique(C["status"], return_counts=True))},
                errors=int(sum(1 for e in C["err"] if e)))
    # ------------------------------------------------------------------ scan A
    A = C["scan"] == "A"
    k6 = np.round(C["iota"] / (math.pi / 6), 6)
    on6 = np.abs(k6 - np.round(k6)) < 1e-6
    fams = ["pos", "neg", "zero", "s0", "s0cks", "newt"]
    rps = sorted(set(C["rp"][A]))
    resA = {}
    for fam in fams:
        rows = []
        for rp in rps:
            m = A & (C["fam"] == fam) & (C["rp"] == rp)
            samples = sorted(set(zip(C["Omega"][m], C["phase"][m])))
            ic = []
            for (Om, ph) in samples:
                mm = m & on6 & (C["Omega"] == Om) & (C["phase"] == ph)
                ks = np.round(k6[mm]).astype(int)
                sv = C["survived"][mm]
                surv_k = sorted(ks[sv])
                ic.append(surv_k[0] if surv_k else NONE)
            iot = sorted(set(C["iota"][m]))
            sf = [float(np.mean(C["survived"][m & (C["iota"] == i)])) for i in iot]
            ic = np.array(ic)
            # fraction-based boundary: lowest pi/6 iota with survival fraction >= 0.5
            sf6 = [(int(round(i / (math.pi / 6))), s) for i, s in zip(iot, sf) if abs(i / (math.pi / 6) - round(i / (math.pi / 6))) < 1e-6]
            k50 = next((k for k, s in sf6 if s >= 0.5), NONE)
            rows.append(dict(rp=rp, beta=rt / rp, nsamp=len(samples), ic_med=float(np.median(ic)),
                             ic_min=int(ic.min()), ic_max=int(ic.max()), ic_q25=float(np.percentile(ic, 25)),
                             ic_q75=float(np.percentile(ic, 75)), ic50=int(k50), iotas=[float(i) for i in iot],
                             sf=sf, sf_all=float(np.mean(C["survived"][m])),
                             plunged_frac=float(np.mean(C["plunged"][m] > 0)),
                             status_not0=int(np.sum(C["status"][m] != 0))))
        resA[fam] = rows
    # comparison with the paper's markers (iota in units of pi/6)
    comp = {}
    for fam, pk in FAM_PAPER.items():
        pts = paper["InclD"]["data"][pk]
        rows = []
        for r in resA[fam]:
            pr = min(pts, key=lambda p: abs(p["rp"] - r["rp"]))
            if abs(pr["rp"] - r["rp"]) > 0.05:
                continue
            kp = pr["iota_over_pi"] * 6
            rows.append(dict(rp=r["rp"], beta=r["beta"], paper_k=kp, hrna_med=r["ic_med"], hrna_min=r["ic_min"],
                             hrna_max=r["ic_max"], hrna_k50=r["ic50"],
                             # markers are digitized to 1e-5 of the axis (a marker at 0 reads -0.00002):
                             # compare in grid units with a tolerance of 0.05 step
                             in_range=bool(r["ic_min"] - 0.05 <= kp <= r["ic_max"] + 0.05),
                             within_one_of_med=bool(abs(kp - r["ic_med"]) <= 1.05),
                             within_one_of_k50=bool(abs(kp - r["ic50"]) <= 1.05)))
        comp[fam] = dict(rows=rows, n=len(rows), n_in_range=sum(r["in_range"] for r in rows),
                         n_within_one_med=sum(r["within_one_of_med"] for r in rows),
                         n_within_one_k50=sum(r["within_one_of_k50"] for r in rows))
    crit = [dict(rp=rp, beta=rt / rp, iota_c=cosiN_iota(rt / rp), k=cosiN_iota(rt / rp) / (math.pi / 6)) for rp in rps]
    newt_vs_crit = [dict(rp=r["rp"], k_newt_med=r["ic_med"], k_newt50=r["ic50"], k_crit=c["k"],
                         within_one=bool(abs(r["ic50"] - c["k"]) <= 1.05))
                    for r, c in zip(resA["newt"], crit)]
    # K2: L_z < 0 at beta > 0.9 (r_p <= 7)
    k2 = [dict(rp=r["rp"], beta=r["beta"], hrna_k50=r["ic50"], hrna_med=r["ic_med"], crit_k=c["k"],
               paper_k=[x for x in comp["neg"]["rows"] if x["rp"] == r["rp"]][0]["paper_k"])
          for r, c in zip(resA["neg"], crit) if r["rp"] <= 7.0]
    summ.update(A=resA, A_vs_paper=comp, cosiN=crit, newton_vs_cosiN=newt_vs_crit, K2=k2)
    # ------------------------------------------------------------------ scan B
    B = C["scan"] == "B"
    pa = paper["afin"]["data"]
    P_af = np.array(pa["a_fin"])                         # rows: L_z (ascending), cols: iota
    P_surv = P_af > 0
    lzs = np.array(sorted(set(C["Lz"][B])))
    ios = np.array(sorted(set(C["iota"][B])))
    samples = sorted(set(zip(C["Omega"][B], C["phase"][B])))
    maps = []
    afin_maps = []
    for (Om, ph) in samples:
        M_ = np.zeros((len(lzs), len(ios)), bool)
        Af = np.full((len(lzs), len(ios)), np.nan)
        mm = B & (C["Omega"] == Om) & (C["phase"] == ph)
        li = np.searchsorted(lzs, C["Lz"][mm])
        ii = np.searchsorted(ios, C["iota"][mm])
        M_[li, ii] = C["survived"][mm]
        Af[li, ii] = np.where(C["survived"][mm], C["a_fin"][mm], np.nan)
        maps.append(M_)
        afin_maps.append(Af)
    maps = np.array(maps)
    if maps.shape[1:] != P_surv.shape:              # smoke runs of the scan
        print("scan B grid", maps.shape, "differs from the paper's", P_surv.shape, ": B skipped")
        with open(os.path.join(outdir, "kerr_2402_summary.json"), "w") as fh:
            json.dump(summ, fh, indent=1)
        return
    sfmap = maps.mean(0)
    agree = [float(np.mean(m == P_surv)) for m in maps]
    agree_major = float(np.mean((sfmap >= 0.5) == P_surv))
    half = len(ios) // 2

    def first_surv(Mb):
        return np.array([ios[np.argmax(row)] if row.any() else np.nan for row in Mb])
    fs_paper = first_surv(P_surv)
    fs_h = np.array([first_surv(m) for m in maps])
    fs_med = np.nanmedian(fs_h, axis=0)
    dfs = (fs_med - fs_paper) / math.pi
    afs = np.array(afin_maps)
    retro_h = afs[:, :, half:]
    lz_bins = [(-5.3, -3.0), (-3.0, 0.0), (0.0, 3.0), (3.0, 5.0)]
    by_lz = []
    for lo, hi in lz_bins:
        m = (lzs >= lo) & (lzs < hi)
        by_lz.append(dict(lz_lo=lo, lz_hi=hi, iota_over_pi=(ios / math.pi).tolist(),
                          hrna=sfmap[m].mean(0).tolist(), paper=P_surv[m].mean(0).astype(float).tolist(),
                          hrna_pro=float(sfmap[m][:, :half].mean()), paper_pro=float(P_surv[m][:, :half].mean())))
    pro_per_sample = [float(m[:, :half].mean()) for m in maps]
    resB = dict(nsamples=len(samples), agree_per_sample=agree, agree_majority=agree_major,
                surv_paper=float(P_surv.mean()), surv_paper_pro=float(P_surv[:, :half].mean()),
                surv_paper_retro=float(P_surv[:, half:].mean()),
                surv_hrna=float(maps.mean()), surv_hrna_pro=float(maps[:, :, :half].mean()),
                surv_hrna_retro=float(maps[:, :, half:].mean()),
                surv_hrna_per_sample=[float(m.mean()) for m in maps],
                surv_hrna_pro_per_sample=pro_per_sample, samples=[list(s) for s in samples],
                by_lz=by_lz,
                sf_vs_iota_hrna=sfmap.mean(0).tolist(), sf_vs_iota_paper=P_surv.mean(0).astype(float).tolist(),
                first_surv_paper_over_pi=(fs_paper / math.pi).tolist(),
                first_surv_hrna_med_over_pi=(fs_med / math.pi).tolist(),
                first_surv_hrna_min_over_pi=(np.nanmin(fs_h, axis=0) / math.pi).tolist(),
                first_surv_hrna_max_over_pi=(np.nanmax(fs_h, axis=0) / math.pi).tolist(),
                rows_within_pi12=int(np.sum(np.abs(dfs) <= 1 / 12 + 1e-9)), nrows=len(lzs),
                median_dfirst_over_pi=float(np.nanmedian(dfs)),
                afin_retro_median_paper=float(np.median(P_af[:, half:][P_surv[:, half:]])),
                afin_retro_median_hrna=float(np.nanmedian(retro_h)),
                afin_retro_q10_q90_paper=[float(np.percentile(P_af[:, half:][P_surv[:, half:]], q)) for q in (10, 90)],
                afin_retro_q10_q90_hrna=[float(np.nanpercentile(retro_h, q)) for q in (10, 90)],
                lz=lzs.tolist(), iota=ios.tolist(), sfmap=sfmap.tolist())
    summ["B"] = resB
    with open(os.path.join(outdir, "kerr_2402_summary.json"), "w") as fh:
        json.dump(summ, fh, indent=1)
    brief = {k: v for k, v in resB.items() if (not isinstance(v, list) or len(v) <= 8) and k != "by_lz"}
    print(json.dumps(dict(A_vs_paper={f: {k: v for k, v in c.items() if k != "rows"} for f, c in comp.items()},
                          newton_vs_cosiN=sum(r["within_one"] for r in newt_vs_crit), K2=k2, B=brief), indent=1))
    figures(summ, paper, crit, outdir, P_surv, sfmap, fs_paper, fs_h, lzs, ios)


def figures(summ, paper, crit, outdir, P_surv, sfmap, fs_paper, fs_h, lzs, ios):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use_style()
    resA = summ["A"]
    # ---- Fig. InclD comparison
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 6.0))
    pos = [(0.7, 3.45), (4.6, 3.45), (0.7, 0.5), (4.6, 0.5)]
    titles = {"pos": r"$s=0.9$, equatorial $L_z>0$", "neg": r"$s=0.9$, equatorial $L_z<0$",
              "zero": r"$s=0.9$, $L_z=0$", "s0": r"$s=0$"}
    c_h, c_p, c_n = fs.PAL["blue"], fs.PAL["red"], "0.45"
    bc = np.array([c["beta"] for c in crit])
    for (x0, y0), fam in zip(pos, ["pos", "neg", "zero", "s0"]):
        ax = fs.inch_axes(fig, x0, y0, 3.2, 2.15)
        rows = resA[fam]
        b = np.array([r["beta"] for r in rows])
        ax.fill_between(b, [r["ic_min"] / 6 for r in rows], [min(r["ic_max"], 6) / 6 for r in rows],
                        color=c_h, alpha=0.18, lw=0, label="HRNA range (24 orientations)")
        ax.plot(b, [min(r["ic_med"], 6.5) / 6 for r in rows], "-", color=c_h, lw=1.5, label="HRNA median")
        ax.plot(b, [min(r["ic50"], 6.5) / 6 for r in rows], "o", color=c_h, ms=3, label=r"HRNA, survival $\geq 1/2$")
        if fam == "s0":
            rc = resA["s0cks"]
            ax.plot(b, [min(r["ic50"], 6.5) / 6 for r in rc], "x--", color=fs.PAL["orange"], ms=4, lw=0.8,
                    label="HRNA in 'cks' (defect)")
        rn = resA["newt"]
        ax.plot(b, [min(r["ic50"], 6.5) / 6 for r in rn], ":", color=c_n, lw=1.0, label=r"Newton law, survival $\geq 1/2$")
        ax.plot(bc, [c["iota_c"] / math.pi for c in crit], "-", color="k", lw=0.8, label="Eq. (cosiN)")
        pts = paper["InclD"]["data"][FAM_PAPER[fam]]
        ax.plot([p["beta"] for p in pts], [p["iota_over_pi"] for p in pts], "^" if fam != "neg" else "v",
                color=c_p, ms=5, mfc="none", mew=1.2, label="2402.02178 (digitized)")
        ax.set_ylim(-0.05, 1.15)
        ax.set_yticks([0, 1 / 3, 2 / 3, 1])
        ax.set_yticklabels(["0", r"$\pi/3$", r"$2\pi/3$", r"$\pi$"])
        ax.set_title(titles[fam], fontsize=8)
        ax.set_xlabel(r"$\beta = r_t/r_p$")
        ax.set_ylabel(r"lowest surviving $\iota$")
        if fam == "s0":
            ax.legend(fontsize=5.3, loc="upper left")
    fs.save(fig, os.path.join(outdir, "fig_incld"))
    # ---- survival fraction against iota for a few r_p
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 2.8))
    cols = fs.series_colors(4)
    for k, rp in enumerate((6.0, 8.0, 10.0, 14.0)):
        ax = fs.inch_axes(fig, 0.6 + 1.9 * k, 0.5, 1.6, 1.9)
        for fam, c, ls in (("pos", cols[0], "-"), ("neg", cols[1], "-"), ("zero", cols[2], "-"), ("s0", "k", "--"),
                           ("newt", "0.5", ":")):
            r = [x for x in resA[fam] if x["rp"] == rp][0]
            ax.plot(np.array(r["iotas"]) / math.pi, r["sf"], ls, color=c, label=fam)
        ax.set_title(r"$r_p=%g$, $\beta=%.2f$" % (rp, summ["rt"] / rp), fontsize=7)
        ax.set_xlabel(r"$\iota/\pi$")
        if k == 0:
            ax.set_ylabel("survival fraction")
            ax.legend(fontsize=5.5)
    fs.save(fig, os.path.join(outdir, "fig_incld_sf"))
    # ---- Fig. afin comparison
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 2.9))
    ext = [0, 1, lzs[0], lzs[-1]]
    ax1 = fs.inch_axes(fig, 0.6, 0.5, 2.1, 2.0)
    ax1.imshow(P_surv.astype(float), origin="lower", aspect="auto", extent=ext, cmap="Greys", vmin=0, vmax=1.6)
    ax1.set_title("2402.02178 survivors (digitized)", fontsize=7)
    ax2 = fs.inch_axes(fig, 3.15, 0.5, 2.1, 2.0)
    im = ax2.imshow(sfmap, origin="lower", aspect="auto", extent=ext, cmap="Blues", vmin=0, vmax=1)
    ax2.set_title("HRNA ('bks') survival fraction, 8 orientations", fontsize=7)
    for ax in (ax1, ax2):
        ax.set_xlabel(r"$\iota/\pi$")
        ax.set_ylabel(r"$L_z/M$")
    ax3 = fs.inch_axes(fig, 5.75, 0.5, 2.1, 2.0)
    ax3.plot(fs_paper / math.pi, lzs, "-", color=fs.PAL["red"], label="paper")
    ax3.fill_betweenx(lzs, np.nanmin(fs_h, 0) / math.pi, np.nanmax(fs_h, 0) / math.pi, color=fs.PAL["blue"], alpha=0.2, lw=0)
    ax3.plot(np.nanmedian(fs_h, 0) / math.pi, lzs, "-", color=fs.PAL["blue"], label="HRNA median, range")
    ax3.axvline(crit[[c["rp"] for c in crit].index(10.0)]["iota_c"] / math.pi, color="k", lw=0.8, label="Eq. (cosiN)")
    ax3.set_xlim(0.0, 0.75)
    ax3.set_xlabel(r"lowest surviving $\iota/\pi$")
    ax3.set_ylabel(r"$L_z/M$")
    ax3.legend(fontsize=5.5)
    fs.save(fig, os.path.join(outdir, "fig_afin"))
    # ---- survival against iota by L_z band (scan B) and the Newton law of scan A at r_p = 10
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 2.7))
    cols = fs.series_colors(4)
    rn = [x for x in resA["newt"] if x["rp"] == 10.0][0]
    for k, band in enumerate(summ["B"]["by_lz"]):
        ax = fs.inch_axes(fig, 0.6 + 1.9 * k, 0.5, 1.6, 1.8)
        ax.plot(band["iota_over_pi"], band["paper"], "-", color=fs.PAL["red"], label="2402.02178")
        ax.plot(band["iota_over_pi"], band["hrna"], "-", color=fs.PAL["blue"], label="HRNA (8 orient.)")
        ax.plot(np.array(rn["iotas"]) / math.pi, rn["sf"], ":", color="0.4", label="Newton, equatorial (24)")
        ax.set_title(r"$L_z\in[%g, %g)$" % (band["lz_lo"], band["lz_hi"]), fontsize=7)
        ax.set_xlabel(r"$\iota/\pi$")
        ax.set_ylim(-0.03, 1.05)
        if k == 0:
            ax.set_ylabel(r"survival fraction, $r_p=10$")
            ax.legend(fontsize=5.5, loc="lower right")
    fs.save(fig, os.path.join(outdir, "fig_afin_sf"))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
