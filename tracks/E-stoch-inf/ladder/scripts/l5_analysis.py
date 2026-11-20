#!/usr/bin/env python3
"""Single-kick test L5 (../JOURNAL.md entries 14 and later): one shell |n|^2 = 5 kicked on a
homogeneous background at 64^3 (inputs/sr_l5.athinput, runs of inputs/card_bc.list).

    l5_analysis.py --run DIR --out DIR

DIR holds K1p, K1m, K2p, K2m, K0 (stencil projector, s = +-100, +-50, 0), C1p, C1m, C2p,
C2m (continuum projector), N1p, N1m (Pi kick flipped, s = +-100). Every run dumps every
cycle. Parts of a field X in s, cell by cell, at equal recorded times:
    X_o(s) = [X(s) - X(-s)]/2,   X_e(s) = [X(s) + X(-s)]/2 - X(0)
    X1 = [8 X_o(s/2) - X_o(s)]/3   (first-order part at s = 100; third order removed)
    X3 = X_o(s) - X1               (third-order part at s = 100)
rms over the box relative to the box mean <[H]> or <[M]> of the record of the s = +100 run
of the same projector (<[M]> is first order in s, so M1/<[M]> does not depend on s).
Verdicts on PL1-PL3 of JOURNAL entry 14; writes l5.json and fig_l5.png/pdf.
"""
import argparse
import json
import os

import numpy as np

import ladder_lib as LL
import l5_kick_ref as KR

RUNS = ("K1p", "K1m", "K2p", "K2m", "K0", "C1p", "C1m", "C2p", "C2m", "N1p", "N1m")
VARS = ["H", "Mx", "My", "Mz"]


def rms(x):
    return float(np.sqrt(np.mean(x * x)))


def rms_vec(m, remove_mean=False):
    if remove_mean:
        m = m - m.mean(axis=(1, 2, 3), keepdims=True)
    return float(np.sqrt(np.mean((m * m).sum(axis=0))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    dumps = {r: LL.dump_list(os.path.join(a.run, r)) for r in RUNS}
    con = {r: LL.read_con(os.path.join(a.run, r)) for r in RUNS}
    nd = min(len(v) for v in dumps.values())
    rows = []
    for i in range(nd):
        F, T, C = {}, {}, {}
        for r in RUNS:
            h, f = LL.read_dump(dumps[r][i], VARS)
            F[r] = dict(H=f["H"], M=np.stack([f["Mx"], f["My"], f["Mz"]]))
            T[r], C[r] = h["time"], h["cycle"]
        if max(T.values()) - min(T.values()) > 1e-12 or len(set(C.values())) != 1:
            raise SystemExit(f"dump {i}: times or cycles differ: {T} {C}")
        cyc = C["K1p"]
        rec = {r: con[r][np.nonzero(con[r][:, 1] == cyc)[0][0]] for r in RUNS}
        hmag = rec["K1p"][9]
        row = dict(dump=i, cycle=int(cyc), time=float(T["K1p"]), efolds=float(rec["K1p"][2]),
                   Hmag=float(hmag), Mmag_K=float(rec["K1p"][10]), Mmag_C=float(rec["C1p"][10]),
                   record_H={r: float(rec[r][3]) for r in RUNS},
                   record_M={r: float(rec[r][6]) for r in RUNS})
        H0 = F["K0"]["H"]
        row["H0_mean"] = float(H0.mean() / hmag)
        row["H0_rms_nomean"] = rms(H0 - H0.mean()) / hmag
        # H, stencil
        ho1 = 0.5 * (F["K1p"]["H"] - F["K1m"]["H"])
        ho2 = 0.5 * (F["K2p"]["H"] - F["K2m"]["H"])
        he1 = 0.5 * (F["K1p"]["H"] + F["K1m"]["H"]) - H0
        he2 = 0.5 * (F["K2p"]["H"] + F["K2m"]["H"]) - H0
        h1 = (8.0 * ho2 - ho1) / 3.0
        row.update(H_even1=rms(he1 - he1.mean()) / hmag, H_even2=rms(he2 - he2.mean()) / hmag,
                   H_even1_mean=float(he1.mean() / hmag), H_even2_mean=float(he2.mean() / hmag),
                   H_odd1=rms(ho1) / hmag, H_first=rms(h1) / hmag, H_third=rms(ho1 - h1) / hmag)
        # H, negative control
        hon = 0.5 * (F["N1p"]["H"] - F["N1m"]["H"])
        hen = 0.5 * (F["N1p"]["H"] + F["N1m"]["H"]) - H0
        row.update(NC_H_odd=rms(hon) / hmag, NC_H_even=rms(hen - hen.mean()) / hmag)
        # M
        if row["Mmag_K"] > 0 and row["Mmag_C"] > 0:
            for tag in ("K", "C"):
                mo1 = 0.5 * (F[f"{tag}1p"]["M"] - F[f"{tag}1m"]["M"])
                mo2 = 0.5 * (F[f"{tag}2p"]["M"] - F[f"{tag}2m"]["M"])
                me1 = 0.5 * (F[f"{tag}1p"]["M"] + F[f"{tag}1m"]["M"]) - F["K0"]["M"]
                m1 = (8.0 * mo2 - mo1) / 3.0
                mm = row[f"Mmag_{tag}"]
                row[f"M_first_{tag}"] = rms_vec(m1) / mm
                row[f"M_third_{tag}"] = rms_vec(mo1 - m1) / mm
                row[f"M_even_{tag}"] = rms_vec(me1, remove_mean=True) / mm
                row[f"_m1_{tag}"] = m1
            row["M_first_C_minus_K"] = rms_vec(row["_m1_C"] - row["_m1_K"]) / row["Mmag_K"]
            row["M_K0_rms"] = rms_vec(F["K0"]["M"]) / row["Mmag_K"]
            del row["_m1_K"], row["_m1_C"]
        rows.append(row)
        del F
    ref = KR.compute(64, 5)
    with open(os.path.join(a.out, "kick_ref.json"), "w") as fp:
        json.dump(ref, fp, indent=1)
    res = dict(run=a.run, rows=rows, kick_ref=ref)

    # verdicts (JOURNAL entry 14)
    later = [r for r in rows if r["cycle"] >= 1]
    floor = max(max(r["H0_rms_nomean"] for r in rows), 1e-14)
    fac = [r["H_even1"] / r["H_even2"] for r in later if r["H_even1"] > 10 * floor]
    rec_fac = [r["record_H"]["K1p"] / r["record_H"]["K2p"] for r in later]
    res["PL1"] = dict(
        even_factor_range=[min(fac), max(fac)] if fac else None,
        record_factor_range=[min(rec_fac), max(rec_fac)],
        first_over_even_max=max(r["H_first"] / r["H_even1"] for r in later),
        H_even1_range=[min(r["H_even1"] for r in later), max(r["H_even1"] for r in later)],
        floor_used=floor,
        pass_=bool(fac and 3.9 <= min(fac) and max(fac) <= 4.1 and
                   max(r["H_first"] / r["H_even1"] for r in later) < 1e-2))
    mrows = [r for r in rows if "M_first_K" in r]
    if mrows:
        r1 = mrows[0]
        refv = ref["continuum"]["rms_M_over_mean_magnitude"] if ref else None
        early = [r for r in mrows if r["cycle"] <= 8]
        tt = np.array([r["time"] for r in early])
        mk = np.array([r["M_first_K"] for r in early])
        slope = float(np.polyfit(np.log(tt), np.log(mk), 1)[0]) if len(early) >= 3 else None
        res["PL2"] = dict(
            first_dump=dict(cycle=r1["cycle"], time=r1["time"], M_first_K=r1["M_first_K"],
                            M_first_C=r1["M_first_C"], C_minus_K=r1["M_first_C_minus_K"],
                            reference=refv),
            stencil_over_continuum_first_dump=r1["M_first_K"] / r1["M_first_C"],
            C_minus_K_over_reference_first_dump=(r1["M_first_C_minus_K"] / refv) if refv else None,
            loglog_slope_M_first_K_cycles_1_8=slope,
            M_first_K_range=[min(r["M_first_K"] for r in mrows), max(r["M_first_K"] for r in mrows)],
            M_first_C_range=[min(r["M_first_C"] for r in mrows), max(r["M_first_C"] for r in mrows)],
            pass_=bool(r1["M_first_K"] < 1e-2 * r1["M_first_C"] and refv is not None and
                       abs(r1["M_first_C_minus_K"] / refv - 1) < 0.3))
    res["PL3"] = dict(
        NC_odd_over_proper_first_min=min(r["NC_H_odd"] / r["H_first"] for r in later),
        NC_odd_over_proper_even_min=min(r["NC_H_odd"] / r["H_even1"] for r in later),
        NC_odd_range=[min(r["NC_H_odd"] for r in later), max(r["NC_H_odd"] for r in later)],
        record_ratio_min=min(r["record_H"]["N1p"] / r["record_H"]["K1p"] for r in later),
        pass_=bool(min(r["NC_H_odd"] / r["H_first"] for r in later) >= 1e3 and
                   min(r["NC_H_odd"] / r["H_even1"] for r in later) >= 10))
    with open(os.path.join(a.out, "l5.json"), "w") as fp:
        json.dump(res, fp, indent=1, default=float)
    for r in rows:
        print(f"c={r['cycle']:2d} t={r['time']:.4f} He1={r['H_even1']:.3e} He2={r['H_even2']:.3e} "
              f"fac={r['H_even1'] / max(r['H_even2'], 1e-300):.4f} H1={r['H_first']:.2e} "
              f"H3={r['H_third']:.2e} NC={r['NC_H_odd']:.2e} H0={r['H0_mean']:+.1e} "
              + (f"M1K={r['M_first_K']:.2e} M1C={r['M_first_C']:.2e} "
                 f"C-K={r['M_first_C_minus_K']:.2e} MeK={r['M_even_K']:.2e}"
                 if "M_first_K" in r else ""))
    print(json.dumps({k: res[k] for k in ("PL1", "PL2", "PL3") if k in res}, indent=1,
                     default=float))
    figure(res, a.out)


def figure(res, outdir):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use_style()
    rows = [r for r in res["rows"] if r["cycle"] >= 1]
    t = np.array([r["time"] for r in rows])
    g = lambda k: np.array([r.get(k, np.nan) for r in rows])  # noqa: E731
    fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.6))
    a0 = ax[0, 0]
    a0.semilogy(t, g("H_even1"), "s-", color=fs.PAL["blue"], ms=3, label=r"even, $s=100$")
    a0.semilogy(t, 4 * g("H_even2"), "--", color=fs.PAL["green"], label=r"$4\times$ even, $s=50$")
    a0.semilogy(t, g("H_first"), "o-", color=fs.PAL["red"], ms=3, label="first order")
    a0.semilogy(t, g("H_third"), "^:", color=fs.PAL["orange"], ms=3, label="third order")
    a0.semilogy(t, g("NC_H_odd"), "d-", color="k", ms=3, label=r"odd, $\Pi$ kick flipped")
    a0.semilogy(t, np.abs(g("H0_mean")), ":", color="0.5", label=r"$|H_0|$ ($s=0$)")
    a0.set_xlabel(r"$t$ (units of $1/H_*$)")
    a0.set_ylabel(r"rms part of $\mathcal{H}$ / $\langle[\mathcal{H}]\rangle$")
    a0.legend(fontsize=6, loc="center right")
    a1 = ax[0, 1]
    a1.plot(t, g("H_even1") / g("H_even2"), "s-", color=fs.PAL["blue"], ms=3,
            label=r"even part, rms")
    a1.plot(t, g("H_even1_mean") / g("H_even2_mean"), "x--", color=fs.PAL["green"], ms=4,
            label="even part, box mean")
    a1.plot(t, [r["record_H"]["K1p"] / r["record_H"]["K2p"] for r in rows], "-", lw=2.5,
            alpha=0.5, color=fs.PAL["red"], label=r"record $\langle|\mathcal{H}|/[\mathcal{H}]\rangle$")
    a1.axhline(4.0, **fs.GUIDE)
    a1.set_ylim(3.0, 5.0)
    a1.set_xlabel(r"$t$")
    a1.set_ylabel(r"factor $s=100$ / $s=50$")
    a1.legend(fontsize=7, loc="upper right")
    a2 = ax[1, 0]
    a2.semilogy(t, g("M_first_C"), "o-", color=fs.PAL["red"], ms=3, label="first order, continuum $n$")
    a2.semilogy(t, g("M_first_K"), "s-", color=fs.PAL["blue"], ms=3, label="first order, stencil $q$")
    a2.semilogy(t, g("M_first_C_minus_K"), "x--", color="k", ms=4, label="continuum $-$ stencil")
    a2.semilogy(t, g("M_even_K"), ":", color=fs.PAL["green"], label=r"second order ($q$, $s=100$)")
    a2.semilogy(t, g("M_third_K"), "^:", color=fs.PAL["orange"], ms=3, label="third order ($q$)")
    if res.get("kick_ref"):
        a2.axhline(res["kick_ref"]["continuum"]["rms_M_over_mean_magnitude"], **fs.GUIDE)
        a2.text(t[-1], res["kick_ref"]["continuum"]["rms_M_over_mean_magnitude"] * 1.3,
                "one-step kick reference", fontsize=6, ha="right")
    a2.set_xlabel(r"$t$")
    a2.set_ylabel(r"rms part of $\mathcal{M}$ / $\langle[\mathcal{M}]\rangle$")
    a2.legend(fontsize=6, loc="lower right")
    a3 = ax[1, 1]
    for r_, c, ls in (("K1p", fs.PAL["blue"], "-"), ("K2p", fs.PAL["green"], "--"),
                      ("K0", "0.5", ":"), ("N1p", "k", "-")):
        a3.semilogy(t, [r["record_H"][r_] for r in rows], ls, color=c,
                    label=rf"$\mathcal{{H}}$, {r_}")
    for r_, c in (("K1p", fs.PAL["blue"]), ("C1p", fs.PAL["red"]), ("N1p", "k")):
        a3.semilogy(t, [r["record_M"][r_] for r in rows], "-.", color=c,
                    label=rf"$\mathcal{{M}}$, {r_}")
    a3.set_xlabel(r"$t$")
    a3.set_ylabel(r"record $\langle|\mathcal{C}|/[\mathcal{C}]\rangle$")
    a3.legend(fontsize=6, ncol=2, loc="lower right")
    fig.tight_layout()
    fs.save(fig, os.path.join(outdir, "fig_l5"))
    plt.close(fig)


if __name__ == "__main__":
    main()
