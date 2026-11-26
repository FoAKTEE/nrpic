"""V3-V6: growth criterion G ((iii), D2), closure D1, D3, D4 timing, removal reasons, for
the dust-filled members, from the removal records, finder summaries and acc.hst, with the
verifier's own reference (ltbref_*.npz of v1_reference.py).

python3 v3_growth.py --scratch <scratch/D-bh-dress> --ref <V1 run dir> --out <dir>
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ltb  # noqa: E402
import vio  # noqa: E402
import figstyle as fs  # noqa: E402

DATA = {"N": "D-20261121-203042-82deeec", "4N": "D-20261124-130942-29c5de2",
        "N/4": "D-20261124-131050-ed0a535"}
CTRL = {"V-1L": ("D-20261121-203124-a34cf1f", "v1l"),
        "V-1L16": ("D-20261121-203151-37e7b2d", "v1l16"),
        "V-1L4": ("D-20261123-022715-ab5d983", "v1l4")}
# label: run id, base, lattice, control, band of (iii), initial_radius_0
MEMBERS = {
    "ES-FL": ("D-20261121-203150-15f2bad", "esfl", "N", "V-1L", 0.01, 0.8),
    "FK": ("D-20261123-022725-a553496", "esflk", "N", "V-1L", 0.01, 1.6),
    "FN4": ("D-20261124-134157-b17938b", "esflk4n", "4N", "V-1L", 0.01, 1.6),
    "FNQ": ("D-20261124-172725-2f426b6", "esflkq", "N/4", "V-1L", 0.02, 1.6),
    "FL16": ("D-20261124-172745-72472ed", "esfl16", "N", "V-1L16", 0.01, 0.8),
    "FF4": ("D-20261123-022727-1c17e73", "esfl4", "N", "V-1L4", 0.01, 0.8),
}
NTRAC = 140


def acc_table(path):
    a = vio.read_text_table(path)
    t = a[:, 0]
    rev = t[::-1]
    _, idx = np.unique(rev, return_index=True)
    keep = np.sort(len(t) - 1 - idx)
    a = a[keep]
    return a[np.argsort(a[:, 0], kind="stable")]


def first_sample_at_or_after(ts, t):
    i = np.searchsorted(ts, t - 1e-12, side="left")
    return np.minimum(i, len(ts) - 1), i < len(ts)


def member(scr, ref_dir, lab, tag_check=False):
    rid, base, lat, ctrl, band, r_init = MEMBERS[lab]
    d = os.path.join(scr, rid)
    z = np.load(os.path.join(ref_dir, f"ltbref_{lat.replace('/', 'q')}.npz"))
    R0, EK, mrest, mdisc = z["R0"], z["EK"], z["m"], z["mdisc"]
    tauH_tab, tauH_mid, tauH_inc = z["tauH_tab"], z["tauH_mid"], z["tauH"]
    curve_tab = (z["tH_tab"], z["m_tab"])
    curve_lat = (z["tH_curve"], z["m_curve"])
    out = {"run": rid, "lattice": lat, "control": ctrl}
    s, bad = vio.read_summary(os.path.join(d, f"{base}.horizon_summary_0.txt"))
    ts, Ms, rmin = s[:, 1], s[:, 2], s[:, 11]
    good = ~bad
    sc, badc = vio.read_summary(os.path.join(scr, CTRL[ctrl][0],
                                             f"{CTRL[ctrl][1]}.horizon_summary_0.txt"))
    tc, Mc = sc[~badc, 1], sc[~badc, 2]
    rec_raw = vio.read_removed(os.path.join(d, f"{base}.removed.bin"))
    rec, ndrop, nback = vio.dedupe_removed(rec_raw)
    out.update(n_records_raw=int(len(rec_raw)), n_dropped_duplicates=int(ndrop),
               n_time_backwards=int(nback))
    tag = rec[:, vio.RTAG].astype(np.int64)
    reason = rec[:, vio.RREASON].astype(int)
    dust = tag >= NTRAC
    # rest mass in the record must equal the particle file's (checks the tag -> index map)
    out["tag_mass_maxrel"] = float(np.max(np.abs(rec[:, vio.RM][dust] / mrest[tag[dust]] - 1)))
    reasons = {int(r): int(np.sum(dust & (reason == r))) for r in np.unique(reason)}
    out["dust_removals_by_reason"] = reasons
    out["tracer_removals"] = int(np.sum(~dust))
    sel = dust & ((reason == 2) | (reason == 3))
    tr, taur, tg = rec[sel, vio.RT], rec[sel, vio.RTAU], tag[sel]
    mEK = mrest[tg] * EK[tg]
    F_rem_cum = np.cumsum(mEK)
    # removal reason switch (ES-FL: reason 3 -> 2)
    r2 = dust & (reason == 2)
    r3 = dust & (reason == 3)
    out["reason2_first_t_after_50"] = float(rec[r2 & (rec[:, 0] > 50), 0].min()) if np.any(r2 & (rec[:, 0] > 50)) else None
    out["reason3_last_t"] = float(rec[r3, 0].max()) if np.any(r3) else None
    cross = np.where(good & (rmin >= 4 * r_init))[0]
    out["t_minradius_ge_4rinit"] = float(ts[cross[0]]) if len(cross) else None
    out["minradius_end"] = float(rmin[-1])
    out["t_end"] = float(ts[-1])
    # (iii)
    i, ok = first_sample_at_or_after(ts, tr)
    MAH_at = Ms[i]
    res = {}
    for name, curve in [("tab", curve_tab), ("lattice", curve_lat)]:
        ratio = MAH_at / ltb.growth_from_curve(curve, taur) - 1
        w = ok & (taur <= 650)
        edges = np.arange(0, 660, 10.0)
        k = np.digitize(taur[w], edges) - 1
        meds, cen, cnt = [], [], []
        for b in range(len(edges) - 1):
            m = k == b
            if m.sum() >= 20:
                meds.append(float(np.median(ratio[w][m])))
                cen.append(float(edges[b] + 5))
                cnt.append(int(m.sum()))
        meds = np.array(meds)
        res[name] = dict(nbins=len(meds), max_abs_median=float(np.max(np.abs(meds))),
                         bin_of_max=cen[int(np.argmax(np.abs(meds)))],
                         n_outside_band=int(np.sum(np.abs(meds) > band)),
                         tau_last_bin=cen[-1], overall_median=float(np.median(ratio[w])),
                         centres=cen, medians=[float(x) for x in meds], counts=cnt)
    out["iii"] = res
    out["band"] = band
    # D2 bracket at the finder samples after 20 M
    acc = acc_table(os.path.join(d, f"{base}.acc.hst"))
    ta, mEin, mEout = acc[:, 0], acc[:, 19], acc[:, 22]
    x0, _, m0, _ = vio.read_nrp(os.path.join(scr, DATA[lat], "esf.nrp"))
    r0 = np.sqrt(np.sum(x0 ** 2, axis=1))
    C0 = float(np.sum((m0 * EK)[r0 < 5.0]))
    w2 = good & (ts >= 20.0) & (ts <= tc[-1])
    tt = ts[w2]
    Mctrl = np.interp(tt, tc, Mc)
    lhs = Ms[w2] - Mctrl
    Frem_t = np.concatenate([[0.0], F_rem_cum])[np.searchsorted(tr, tt, side="right")]
    Fsph_t = C0 + np.interp(tt, ta, mEin - mEout)
    lo = lhs - (Frem_t - 3e-3)
    hi = (Fsph_t + 3e-3) - lhs
    out["D2"] = dict(n=int(len(tt)), holds=bool(np.all(lo >= 0) & np.all(hi >= 0)),
                     min_lower_margin=float(lo.min()), t_min_lower=float(tt[np.argmin(lo)]),
                     min_upper_margin=float(hi.min()), t_min_upper=float(tt[np.argmin(hi)]),
                     n_viol=int(np.sum((lo < 0) | (hi < 0))), C0=C0)
    # D1 and growth numbers
    M0 = Ms[good][0]
    Mc0 = Mc[0]
    te = tt[-1]
    D1raw = (Ms[w2][-1] - M0) - Frem_t[-1]
    D1ctl = (Ms[w2][-1] - M0) - (Mctrl[-1] - Mc0) - Frem_t[-1]
    out["D1"] = dict(t=float(te), raw=float(D1raw), control_subtracted=float(D1ctl))
    out["M_AH"] = {str(T): float(np.interp(T, ts[good], Ms[good])) for T in
                   [20, 100, 200, 219, 300, 400, 500] if T <= ts[-1]}
    out["F_rem"] = {str(T): float(np.concatenate([[0.0], F_rem_cum])[np.searchsorted(tr, T, side="right")])
                    for T in [100, 200, 300, 399.5, 400, 500] if T <= ts[-1] + 0.5}
    # D3 as written: M_AH(t) - [M_ctrl(t) - 1] >= m_disc(R0) - 3e-4 at the first sample after removal
    Mc_at = np.interp(ts[i], tc, Mc)
    d3 = (MAH_at - (Mc_at - 1.0)) - (mdisc[tg] - 3e-4)
    w3 = ok & (ts[i] <= tc[-1])
    out["D3"] = dict(n=int(w3.sum()), n_viol=int(np.sum(d3[w3] < 0)),
                     first_viol_t=float(tr[w3][d3[w3] < 0].min()) if np.any(d3[w3] < 0) else None,
                     n_viol_before_219=int(np.sum((d3 < 0) & w3 & (tr <= 219))))
    # D4 timing: tau_rem - tau_H(R0), continuum and lattice references
    d4 = {}
    for name, tH in [("tab", tauH_tab), ("mid", tauH_mid), ("incl", tauH_inc)]:
        dd = taur - tH[tg]
        d4[name] = dict(frac_neg=float(np.mean(dd < 0)), min=float(dd.min()),
                        frac_neg_t_le_219=float(np.mean(dd[tr <= 219] < 0)) if np.any(tr <= 219) else None,
                        frac_neg_t_gt_235=float(np.mean(dd[tr > 235] < 0)) if np.any(tr > 235) else None,
                        frac_neg_t_gt_170=float(np.mean(dd[tr > 170] < 0)) if np.any(tr > 170) else None,
                        median_t_gt_235=float(np.median(dd[tr > 235])) if np.any(tr > 235) else None,
                        median_t_le_219=float(np.median(dd[tr <= 219])) if np.any(tr <= 219) else None)
    out["D4"] = d4
    arrays = dict(ts=ts, Ms=Ms, rmin=rmin, tt=tt, lhs=lhs, Frem_t=Frem_t, Fsph_t=Fsph_t,
                  tr=tr, taur=taur, tg=tg, d4tab=taur - tauH_tab[tg],
                  d4mid=taur - tauH_mid[tg], reason=reason[sel], dist=rec[sel, vio.RDIST],
                  ratio_tab=MAH_at / ltb.growth_from_curve(curve_tab, taur) - 1,
                  R0=R0[tg], mrest=mrest[tg])
    # tracers: removal proper time against the exact crossing
    trc = ~dust
    if np.any(trc):
        tt_tag = tag[trc]
        out["tracers_removed"] = {}
        for g in [6.0, 10.0, 20.0, 28.0]:
            m = np.abs(R0[tt_tag] - g) < 1e-3
            if m.any():
                out["tracers_removed"][str(g)] = dict(
                    n=int(m.sum()), t_rem_median=float(np.median(rec[trc, 0][m])),
                    tau_rem_minus_tauH_tab=[float(np.min(rec[trc, vio.RTAU][m] - tauH_tab[tt_tag[m]])),
                                            float(np.median(rec[trc, vio.RTAU][m] - tauH_tab[tt_tag[m]])),
                                            float(np.max(rec[trc, vio.RTAU][m] - tauH_tab[tt_tag[m]]))],
                    reasons=sorted(set(int(x) for x in rec[trc, vio.RREASON][m])))
    return out, arrays


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--members", default=",".join(MEMBERS))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    allres = {}
    arrs = {}
    for lab in a.members.split(","):
        r, arr = member(a.scratch, a.ref, lab)
        allres[lab] = r
        arrs[lab] = arr
        np.savez_compressed(os.path.join(a.out, f"v3_{lab.replace('/', 'q')}.npz"), **arr)
        print(lab, json.dumps({k: v for k, v in r.items() if k not in ("iii",)}, indent=None)[:3000])
        print(lab, "iii", {k: {kk: vv for kk, vv in v.items() if kk not in ("centres", "medians", "counts")}
                           for k, v in r["iii"].items()})
    json.dump(allres, open(os.path.join(a.out, "v3_growth.json"), "w"), indent=1)

    fs.use_style()
    import matplotlib.pyplot as plt
    cols = {"ES-FL": fs.PAL["red"], "FK": fs.PAL["blue"], "FN4": fs.PAL["yellow"],
            "FNQ": fs.PAL["green"], "FL16": fs.PAL["orange"], "FF4": "grey"}
    fig = plt.figure(figsize=(8, 6.4))
    ax1 = fig.add_axes([0.09, 0.57, 0.38, 0.39])
    ax2 = fig.add_axes([0.59, 0.57, 0.38, 0.39])
    ax3 = fig.add_axes([0.09, 0.08, 0.38, 0.39])
    ax4 = fig.add_axes([0.59, 0.08, 0.38, 0.39])
    for lab, r in allres.items():
        c = cols.get(lab, "k")
        ax1.plot(r["iii"]["tab"]["centres"], 100 * np.array(r["iii"]["tab"]["medians"]), "o-",
                 ms=2.5, lw=1, color=c, label=lab)
        A = arrs[lab]
        ax2.plot(A["tt"], A["lhs"] - A["Frem_t"], color=c, lw=1, label=lab)
        ax2.plot(A["tt"], A["Fsph_t"] - A["Frem_t"], color=c, lw=1, ls=":")
    ax1.axhline(1, color="k", ls="--", lw=1)
    ax1.axhline(-1, color="k", ls="--", lw=1)
    ax1.set_xlabel(r"$\tau_{\rm rem}$ [M]")
    ax1.set_ylabel(r"median $M_{AH}/M_{\rm LTB}(\tau_{\rm rem})-1$ [%]")
    ax1.set_ylim(-1.5, 1.5)
    ax1.legend(loc="lower left", ncol=3, fontsize=8)
    ax2.axhline(-3e-3, color="k", ls="--", lw=1)
    ax2.set_xlabel("t [M]")
    ax2.set_ylabel(r"$(M_{AH}-M_{\rm ctrl})-F_{\rm rem}$; dotted $F_{\rm sph}-F_{\rm rem}$")
    ax2.set_ylim(-0.005, 0.03)
    for lab in ["ES-FL", "FK", "FN4"]:
        if lab in arrs:
            A = arrs[lab]
            ax3.plot(A["tr"], A["d4tab"], ",", color=cols[lab], alpha=0.3, rasterized=True)
            # running fraction of early removals
            edges = np.arange(0, 505, 10.0)
            k = np.digitize(A["tr"], edges) - 1
            fr = [np.mean(A["d4tab"][k == b] < 0) if np.sum(k == b) > 20 else np.nan
                  for b in range(len(edges) - 1)]
            ax4.plot(edges[:-1] + 5, fr, color=cols[lab], label=f"{lab} (continuum ref.)")
            frm = [np.mean(A["d4mid"][k == b] < 0) if np.sum(k == b) > 20 else np.nan
                   for b in range(len(edges) - 1)]
            ax4.plot(edges[:-1] + 5, frm, color=cols[lab], ls=":", label=f"{lab} (lattice ref.)")
    ax3.axhline(0, color="k", lw=1)
    ax3.set_ylim(-3, 6)
    ax3.set_xlabel(r"$t_{\rm rem}$ [M]")
    ax3.set_ylabel(r"$\tau_{\rm rem}-\tau_H(R_0)$ [M]")
    ax4.set_xlabel(r"$t_{\rm rem}$ [M]")
    ax4.set_ylabel(r"fraction with $\tau_{\rm rem}<\tau_H$")
    ax4.set_ylim(0, 1)
    ax4.legend(loc="upper left", fontsize=8)
    fs.save(fig, os.path.join(a.out, "v3_growth"))


if __name__ == "__main__":
    main()
