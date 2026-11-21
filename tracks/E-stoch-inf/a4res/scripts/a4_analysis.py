#!/usr/bin/env python3
"""Step 4 of package a4res (Track E): analysis of the card job of JOURNAL entry 3 with the
rules fixed there before the job ended.

    python3 a4_analysis.py --job DIR --pred PREDICTION_JSON --out DIR [--setups N64q16,...]

DIR holds one directory per run of inputs/card.list (<set-up>_<member>). Per set-up:
- pairs A = (p, m), s = +-1 and B = (ph, mh), s = +-1/2; dumps matched by time and cycle;
- odd o = (f+ - f-)/2, even e = (f+ + f-)/2 minus its box mean, rms over the cells (M:
  rms of the vector) in absolute units: O_A, E_A, O_B, E_B for f = H and M_i;
- floors f_o = rms(o_A - 2 o_B)/sqrt(5), f_e = rms(e_A - 4 e_B)/sqrt(17), f = max;
- core's CodeTwin (extracted into OUT/twin from core/scalar-3) at the run's own step
  times (sr.sf.hst), first-order rms of H and |M| at the dump cycles;
- entry window: t > 0 up to one e-fold after the top shell's window reaches 0.999;
- verdicts: strict A4 (i) O_A < E_A where max(O_A, E_A) > 3 f, (ii) E_A/E_B = 4.00 +-
  0.05 where E_B > 10 f_e, both for H and M, on the entry dumps; A4' (a) = (ii), (b) O_A/O_B
  = 2.00 +- 0.05 where O_B > 10 f_o, (c) record <|H|/[H]> <= 1e-9, <|M|/[M]> < 1e-3;
- across set-ups: largest ratio against cells, crossing of 1, even parts and odd order
  between N64q64 and N128q64 (both K = 8).
Writes OUT/a4res.json, OUT/verdicts.md and the figures OUT/fig_*.png."""
import argparse
import json
import os
import time

import numpy as np

import a4lib as A

LL = A.LL
FIELDS = ["H", "Mx", "My", "Mz"]


def rms(x):
    return float(np.sqrt(np.mean(x*x)))


def rms_vec(xs):
    return float(np.sqrt(np.mean(sum(x*x for x in xs))))


def demean(x):
    return x - x.mean()


def parts(fp, fm):
    """odd and even (box mean removed) fields of H and of the three M_i."""
    o = {k: 0.5*(fp[k] - fm[k]) for k in FIELDS}
    e = {k: demean(0.5*(fp[k] + fm[k])) for k in FIELDS}
    return o, e


def norms(d):
    return rms(d["H"]), rms_vec([d["Mx"], d["My"], d["Mz"]])


def analyse_setup(s, job, sl, sf):
    t0 = time.time()
    dirs = {m: os.path.join(job, A.run_name(s, m)) for m, _ in A.MEMBERS}
    dumps = {m: LL.dump_list(d) for m, d in dirs.items()}
    hdrs = {m: [LL.read_header(f) for f in dumps[m]] for m in dirs}
    # match by time and cycle across the four members
    rows, dropped = [], []
    tp = [(h["time"], h["cycle"]) for h in hdrs["p"]]
    idx = {}
    for m in dirs:
        idx[m] = {(round(h["time"], 12), h["cycle"]): i for i, h in enumerate(hdrs[m])}
    matched = []
    for i, (t, c) in enumerate(tp):
        key = (round(t, 12), c)
        if all(key in idx[m] for m in dirs):
            matched.append({m: idx[m][key] for m in dirs})
        else:
            dropped.append(dict(time=t, cycle=c))
    for m in dirs:
        if len(hdrs[m]) != len(matched):
            dropped.append(dict(member=m, dumps=len(hdrs[m]), matched=len(matched)))
    # constraint records
    con = {m: LL.read_con(d) for m, d in dirs.items()}
    rec = {m: dict(H_max=float(con[m][:, 3].max()), M_max=float(con[m][:, 6].max()),
                   H_max_of_max=float(con[m][:, 4].max()), M_max_of_max=float(con[m][:, 7].max()))
           for m in dirs}
    # twin at the run's own step times
    hist = np.loadtxt(os.path.join(dirs["p"], "sr.sf.hst"))
    times = hist[:, 0]
    cycles = [hdrs["p"][mm["p"]]["cycle"] for mm in matched]
    ts = A.TwinSetup(sl, sf, s)
    tw = {r["cycle"]: r for r in ts.code_twin(times, cycles)}
    K = float(np.sqrt(s["nmax2"]))
    for mm in matched:
        f = {}
        for m in dirs:
            _, f[m] = LL.read_dump(dumps[m][mm[m]], FIELDS)
        h = hdrs["p"][mm["p"]]
        oA, eA = parts(f["p"], f["m"])
        oB, eB = parts(f["ph"], f["mh"])
        del f
        dO = {k: oA[k] - 2.0*oB[k] for k in FIELDS}
        dE = {k: demean(eA[k] - 4.0*eB[k]) for k in FIELDS}
        r = dict(cycle=h["cycle"], time=h["time"])
        for (key, v) in (("O_A", oA), ("E_A", eA), ("O_B", oB), ("E_B", eB)):
            r[key + "_H"], r[key + "_M"] = norms(v)
        a, b = norms(dO)
        r["f_o_H"], r["f_o_M"] = a/np.sqrt(5.0), b/np.sqrt(5.0)
        a, b = norms(dE)
        r["f_e_H"], r["f_e_M"] = a/np.sqrt(17.0), b/np.sqrt(17.0)
        crow = con["p"][np.nonzero(con["p"][:, 1] == h["cycle"])[0][0]]
        r["Hmag"], r["Mmag"], r["efolds_rec"] = float(crow[9]), float(crow[10]), float(crow[2])
        t = tw[h["cycle"]]
        r["twin_H"], r["twin_M"] = t["H"], t["M"]
        r["efolds"], r["hubble"] = t["efolds"], t["hubble"]
        r["W_top"] = float(A.window(t["efolds"], t["hubble"], K))
        rows.append(r)
        del oA, eA, oB, eB, dO, dE
    # entry window
    nw = next((r["efolds"] for r in rows if r["W_top"] >= 0.999), rows[-1]["efolds"])
    for r in rows:
        r["entry"] = bool(r["time"] > 0 and r["efolds"] <= nw + 1.0)
    out = dict(name=s["name"], N=s["N"], nmax2=s["nmax2"], cells=A.cells(s), K=K,
               efolds_W999=nw, rows=rows, dropped=dropped, record=rec,
               wall_s=round(time.time() - t0, 1))
    out.update(verdicts(rows, rec))
    print(f"{s['name']:9s} {A.cells(s):5.2f} cells: dumps {len(rows)}, dropped {len(dropped)}, "
          f"largest ratio H {out['largest_H']:.3g} M {out['largest_M']:.3g}; strict A4 "
          f"{out['strict_A4']}; A4' {out['A4p']}; wall {out['wall_s']} s", flush=True)
    return out


def verdicts(rows, rec):
    v = {}
    for X in ("H", "M"):
        f = [max(r[f"f_o_{X}"], r[f"f_e_{X}"]) for r in rows]
        q = [r["time"] > 0 and max(r[f"O_A_{X}"], r[f"E_A_{X}"]) > 3*fi for r, fi in zip(rows, f)]
        qe = [r["entry"] and qq for r, qq in zip(rows, q)]
        ratio = [r[f"O_A_{X}"]/r[f"E_A_{X}"] for r in rows]
        v[f"largest_{X}"] = max([x for x, ok in zip(ratio, qe) if ok], default=float("nan"))
        v[f"largest_all_{X}"] = max([x for x, ok in zip(ratio, q) if ok], default=float("nan"))
        i_max = max((i for i, ok in enumerate(qe) if ok), key=lambda i: ratio[i], default=None)
        v[f"t_largest_{X}"] = rows[i_max]["time"] if i_max is not None else None
        v[f"strict_i_{X}"] = all(x < 1.0 for x, ok in zip(ratio, qe) if ok)
        he = [(r["time"], r[f"E_A_{X}"]/r[f"E_B_{X}"]) for r in rows
              if r["entry"] and r[f"E_B_{X}"] > 10*r[f"f_e_{X}"]]
        ho = [(r["time"], r[f"O_A_{X}"]/r[f"O_B_{X}"]) for r in rows
              if r["time"] > 0 and r[f"O_B_{X}"] > 10*r[f"f_o_{X}"]]
        v[f"halving_even_{X}"] = dict(n=len(he), min=min((x for _, x in he), default=None),
                                      max=max((x for _, x in he), default=None))
        v[f"halving_odd_{X}"] = dict(n=len(ho), min=min((x for _, x in ho), default=None),
                                     max=max((x for _, x in ho), default=None))
        v[f"strict_ii_{X}"] = bool(he) and all(abs(x - 4.0) <= 0.05 for _, x in he)
        v[f"A4p_b_{X}"] = bool(ho) and all(abs(x - 2.0) <= 0.05 for _, x in ho)
        tq = [(r[f"O_A_{X}"]/r[f"twin_{X}"]) for r in rows
              if r["time"] > 0 and r[f"O_A_{X}"] > 3*r[f"f_o_{X}"]]
        v[f"twin_{X}"] = dict(n=len(tq), min=min(tq, default=None), max=max(tq, default=None))
        v[f"Q3_{X}"] = bool(tq) and all(0.9 <= x <= 1.1 for x in tq)
    v["largest"] = max(v["largest_H"], v["largest_M"])
    v["strict_A4"] = "holds" if all(v[k] for k in ("strict_i_H", "strict_i_M", "strict_ii_H",
                                                     "strict_ii_M")) else "fails"
    v["record_H_max"] = max(x["H_max"] for x in rec.values())
    v["record_M_max"] = max(x["M_max"] for x in rec.values())
    v["A4p_c"] = v["record_H_max"] <= 1e-9 and v["record_M_max"] < 1e-3
    a = v["strict_ii_H"] and v["strict_ii_M"]
    b = v["A4p_b_H"] and v["A4p_b_M"]
    v["A4p"] = "passes (a,b,c; d not tested)" if (a and b and v["A4p_c"]) else \
        "fails in " + ",".join(k for k, ok in (("a", a), ("b", b), ("c", v["A4p_c"])) if not ok)
    return v


def loginterp(t, tt, yy):
    return np.exp(np.interp(t, tt, np.log(yy)))


def resolution_pair(lo, hi):
    """Even parts and odd order between two set-ups of the same K (lo coarser)."""
    out = []
    th = np.array([r["time"] for r in hi["rows"]])
    for r in lo["rows"]:
        if r["time"] <= 0 or r["time"] > th[-1] or r["time"] < th[1]:
            continue
        d = dict(time=r["time"])
        for X in ("H", "M"):
            eh = loginterp(r["time"], th, np.array([x[f"E_A_{X}"] for x in hi["rows"]]))
            oh = loginterp(r["time"], th, np.array([x[f"O_A_{X}"] for x in hi["rows"]]))
            fh = loginterp(r["time"], th, np.array([max(x[f"f_o_{X}"], x[f"f_e_{X}"])
                                                    for x in hi["rows"]]))
            twh = loginterp(r["time"], th, np.array([x[f"twin_{X}"] for x in hi["rows"]]))
            fl = max(r[f"f_o_{X}"], r[f"f_e_{X}"])
            d[f"even_ratio_{X}"] = r[f"E_A_{X}"]/eh
            d[f"even_ok_{X}"] = bool(r[f"E_A_{X}"] > 3*fl and eh > 3*fh)
            d[f"order_{X}"] = float(np.log2(r[f"O_A_{X}"]/oh))
            d[f"order_twin_{X}"] = float(np.log2(r[f"twin_{X}"]/twh))
            d[f"order_ok_{X}"] = bool(oh > 3*fh)
        out.append(d)
    q6 = all(abs(d[f"even_ratio_{X}"] - 1) <= 0.05 for d in out for X in ("H", "M")
             if d[f"even_ok_{X}"])
    q7 = all(abs(d[f"order_{X}"] - d[f"order_twin_{X}"]) <= 0.3 for d in out
             for X in ("H", "M") if d[f"order_ok_{X}"])
    a5 = all(4.0 <= d[f"order_{X}"] <= 6.0 for d in out for X in ("H", "M") if d[f"order_ok_{X}"])
    return dict(lo=lo["name"], hi=hi["name"], rows=out, Q6=q6, Q7=q7, A5_band=a5)


def crossing(cells, ratio):
    c, r = np.log(np.asarray(cells, float)), np.log(np.asarray(ratio, float))
    o = np.argsort(c)
    c, r = c[o], r[o]
    for i in range(len(c) - 1):
        if r[i]*r[i+1] <= 0 and r[i] != r[i+1]:
            return float(np.exp(c[i] - r[i]*(c[i+1] - c[i])/(r[i+1] - r[i])))
    if len(c) >= 2:   # extrapolation from the two nearest points
        j = 0 if abs(r[0]) < abs(r[-1]) else len(c) - 2
        return float(np.exp(c[j] - r[j]*(c[j+1] - c[j])/(r[j+1] - r[j])))
    return None


def figures(res, pred, out):
    import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    S = res["setups"]
    cols = fs.series_colors(len(S))
    # parts per set-up, H and M
    for X, lab in (("H", r"\mathcal{H}"), ("M", r"|\mathcal{M}|")):
        fig, ax = plt.subplots(2, 3, figsize=(fs.FULL_WIDTH, 5.0), sharex=True)
        fig.subplots_adjust(left=0.08, right=0.99, bottom=0.09, top=0.95, wspace=0.25,
                            hspace=0.22)
        for a, s in zip(ax.ravel(), S):
            t = np.array([r["time"] for r in s["rows"]])
            g = t > 0
            for key, sty, lb in ((f"O_A_{X}", dict(color=fs.PAL["red"]), "odd, $s=\\pm1$"),
                                 (f"E_A_{X}", dict(color=fs.PAL["blue"]), "even, $s=\\pm1$"),
                                 (f"O_B_{X}", dict(color=fs.PAL["red"], ls="--", lw=1),
                                  "odd, $s=\\pm1/2$"),
                                 (f"E_B_{X}", dict(color=fs.PAL["blue"], ls="--", lw=1),
                                  "even, $s=\\pm1/2$")):
                a.plot(t[g], np.array([r[key] for r in s["rows"]])[g], **sty, label=lb)
            a.plot(t[g], np.array([r[f"twin_{X}"] for r in s["rows"]])[g], "o", ms=2.5,
                   mfc="none", color="k", label="twin (odd, $s=1$)")
            a.plot(t[g], np.array([max(r[f"f_o_{X}"], r[f"f_e_{X}"]) for r in s["rows"]])[g],
                   color="grey", lw=1, label="floor $f$")
            te = [r["time"] for r in s["rows"] if r["entry"]]
            a.axvspan(te[0], te[-1], color="grey", alpha=0.08, lw=0)
            a.set_yscale("log")
            a.set_title(f"({'abcdef'[S.index(s)]}) {s['name']}, {s['cells']:.1f} cells",
                        loc="left", fontsize=7)
            if a in ax[1]:
                a.set_xlabel("$t$")
            if a in ax[:, 0]:
                a.set_ylabel(f"rms of ${lab}$")
        ax[0, 0].legend(fontsize=5, loc="lower left")
        fig.savefig(os.path.join(out, f"fig_parts_{X}.png"), dpi=200)
        plt.close(fig)
    # ratio against time and largest ratio against cells
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2))
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.14, top=0.93, wspace=0.25)
    for s, c in zip(S, cols):
        rr = [r for r in s["rows"] if r["time"] > 0]
        t = [r["time"] for r in rr]
        ax[0].plot(t, [r["O_A_H"]/r["E_A_H"] for r in rr], "-", color=c,
                   label=f"{s['name']} ({s['cells']:.1f})")
        ax[0].plot(t, [r["O_A_M"]/r["E_A_M"] for r in rr], "--", color=c, lw=1)
    ax[0].axhline(1.0, **fs.MASK_LINE)
    ax[0].set_yscale("log")
    ax[0].set_xlabel("$t$")
    ax[0].set_ylabel(r"odd/even, $s=\pm1$ ($\mathcal{H}$ solid, $|\mathcal{M}|$ dashed)")
    ax[0].legend(fontsize=5.5, loc="lower right")
    ax[0].set_title("(a)", loc="left", fontsize=8)
    cc = sorted(A.CORE_SCAN)
    ax[1].plot(cc, [A.CORE_SCAN[c] for c in cc], "o-", mfc="none", color=fs.PAL["blue"],
               label="core's scan ($n^2_{\\max}=64$, $N$ varied)")
    pmap = {p["name"]: p for p in pred["setups"]}
    for nroot, mk in ((64, "s"), (128, "D")):
        ss = [s for s in S if s["N"] == nroot]
        x = [s["cells"] for s in ss]
        ax[1].plot(x, [s["largest_H"] for s in ss], mk, color=fs.PAL["red"],
                   label=f"measured, $N={nroot}$, $\\mathcal{{H}}$")
        ax[1].plot(x, [s["largest_M"] for s in ss], mk, color=fs.PAL["red"], mfc="none",
                   label=f"measured, $N={nroot}$, $|\\mathcal{{M}}|$")
        ax[1].plot(x, [pmap[s["name"]]["max_ratio_H_pred"] for s in ss], mk, ms=3,
                   color=fs.PAL["green"], label=f"twin prediction, $N={nroot}$, $\\mathcal{{H}}$")
    ax[1].axhline(1.0, **fs.MASK_LINE)
    ax[1].axvspan(11.0, 14.5, color="grey", alpha=0.12, lw=0)
    ax[1].set_xscale("log")
    ax[1].set_yscale("log")
    ax[1].set_xlabel("cells per shortest source wavelength")
    ax[1].set_ylabel("largest odd/even in the entry")
    ax[1].legend(fontsize=5, loc="upper right")
    ax[1].set_title("(b)", loc="left", fontsize=8)
    fig.savefig(os.path.join(out, "fig_ratio.png"), dpi=200)
    plt.close(fig)
    # checks: twin, halving, resolution pair
    fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.4))
    fig.subplots_adjust(left=0.09, right=0.99, bottom=0.09, top=0.95, wspace=0.28,
                        hspace=0.3)
    for s, c in zip(S, cols):
        for X, mk in (("H", "o"), ("M", "^")):
            rr = [r for r in s["rows"] if r["time"] > 0]
            t = np.array([r["time"] for r in rr])
            above = np.array([r[f"O_A_{X}"] > 3*r[f"f_o_{X}"] for r in rr])
            y = np.array([r[f"O_A_{X}"]/r[f"twin_{X}"] for r in rr])
            ax[0, 0].plot(t[above], y[above], mk, ms=3, color=c,
                          label=f"{s['name']}" if X == "H" else None)
            ax[0, 0].plot(t[~above], y[~above], mk, ms=3, mfc="none", color=c, alpha=0.4)
            ye = np.array([r[f"E_A_{X}"]/r[f"E_B_{X}"] for r in rr])
            ok = np.array([r[f"E_B_{X}"] > 10*r[f"f_e_{X}"] for r in rr])
            ax[0, 1].plot(t[ok], ye[ok], mk, ms=3, color=c)
            ax[0, 1].plot(t[~ok], ye[~ok], mk, ms=3, mfc="none", color=c, alpha=0.4)
            yo = np.array([r[f"O_A_{X}"]/r[f"O_B_{X}"] for r in rr])
            ok = np.array([r[f"O_B_{X}"] > 10*r[f"f_o_{X}"] for r in rr])
            ax[1, 0].plot(t[ok], yo[ok], mk, ms=3, color=c)
            ax[1, 0].plot(t[~ok], yo[~ok], mk, ms=3, mfc="none", color=c, alpha=0.4)
    fs.band(ax[0, 0], [0, 4.6], [0.9, 0.9], [1.1, 1.1], "grey", 0.15)
    ax[0, 0].set_ylim(0.5, 3.0)
    ax[0, 0].set_yscale("log")
    ax[0, 0].set_ylabel("measured odd / twin")
    ax[0, 0].legend(fontsize=5, loc="upper right", ncol=2)
    fs.band(ax[0, 1], [0, 4.6], [3.95, 3.95], [4.05, 4.05], "grey", 0.3)
    ax[0, 1].set_ylim(3.0, 5.0)
    ax[0, 1].set_ylabel(r"even part: $E_A/E_B$")
    fs.band(ax[1, 0], [0, 4.6], [1.95, 1.95], [2.05, 2.05], "grey", 0.3)
    ax[1, 0].set_ylim(1.5, 2.5)
    ax[1, 0].set_ylabel(r"odd part: $O_A/O_B$")
    rp = res["resolution_pair"]
    t = [d["time"] for d in rp["rows"]]
    for X, mk in (("H", "o"), ("M", "^")):
        ax[1, 1].plot(t, [d[f"order_{X}"] for d in rp["rows"]], mk, ms=3, color=fs.PAL["red"],
                      label=f"odd order, ${X}$")
        ax[1, 1].plot(t, [d[f"order_twin_{X}"] for d in rp["rows"]], "-", color=fs.PAL["red"],
                      lw=1)
        ax[1, 1].plot(t, [4 + 10*(d[f"even_ratio_{X}"] - 1) for d in rp["rows"]], mk, ms=3,
                      color=fs.PAL["blue"], label=f"$4+10(E_{{64}}/E_{{128}}-1)$, ${X}$")
    fs.band(ax[1, 1], [0, 4.6], [3.5, 3.5], [4.5, 4.5], fs.PAL["blue"], 0.1)
    ax[1, 1].set_ylim(2.0, 8.0)
    ax[1, 1].set_ylabel("N64q64 against N128q64")
    ax[1, 1].legend(fontsize=5, loc="upper right")
    for i, a in enumerate(ax.ravel()):
        a.set_xlabel("$t$")
        a.set_title("(%s)" % "abcd"[i], loc="left", fontsize=8)
    fig.savefig(os.path.join(out, "fig_checks.png"), dpi=200)
    plt.close(fig)


def table(res):
    L = ["| set-up | cells | largest H (t) | largest M (t) | E_A/E_B range (n) | "
         "O_A/O_B range (n) | odd/twin range | strict A4 | A4' |", "|" + "---|"*9]
    f = lambda x: "-" if x is None else f"{x:.3f}"  # noqa: E731
    for s in res["setups"]:
        he = s["halving_even_H"], s["halving_even_M"]
        ho = s["halving_odd_H"], s["halving_odd_M"]
        tw = s["twin_H"], s["twin_M"]
        L.append(
            f"| {s['name']} | {s['cells']:.1f} | {s['largest_H']:.3g} ({s['t_largest_H']:.2f})"
            f" | {s['largest_M']:.3g} ({s['t_largest_M']:.2f}) | "
            f"H {f(he[0]['min'])}-{f(he[0]['max'])} ({he[0]['n']}), M {f(he[1]['min'])}-"
            f"{f(he[1]['max'])} ({he[1]['n']}) | H {f(ho[0]['min'])}-{f(ho[0]['max'])} "
            f"({ho[0]['n']}), M {f(ho[1]['min'])}-{f(ho[1]['max'])} ({ho[1]['n']}) | "
            f"H {f(tw[0]['min'])}-{f(tw[0]['max'])}, M {f(tw[1]['min'])}-{f(tw[1]['max'])} | "
            f"{s['strict_A4']} | {s['A4p']} |")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job", required=True)
    ap.add_argument("--pred", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--setups", default=",".join(s["name"] for s in A.SETUPS))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    prov = A.extract_twin(os.path.join(a.out, "twin"))
    sl, sf = A.import_twin(os.path.join(a.out, "twin"))
    pred = json.load(open(a.pred))
    want = a.setups.split(",")
    S = [analyse_setup(s, a.job, sl, sf) for s in A.SETUPS if s["name"] in want]
    res = dict(twin=prov, job=a.job, setups=S)
    names = {s["name"]: s for s in S}
    if "N64q64" in names and "N128q64" in names:
        res["resolution_pair"] = resolution_pair(names["N64q64"], names["N128q64"])
    fam = {}
    for nroot in (64, 128):
        ss = [s for s in S if s["N"] == nroot]
        if len(ss) >= 2:
            fam[str(nroot)] = dict(
                cells=[s["cells"] for s in ss], largest=[s["largest"] for s in ss],
                crossing=crossing([s["cells"] for s in ss], [s["largest"] for s in ss]),
                crossing_H=crossing([s["cells"] for s in ss], [s["largest_H"] for s in ss]),
                crossing_M=crossing([s["cells"] for s in ss], [s["largest_M"] for s in ss]))
    res["families"] = fam
    pmap = {p["name"]: p for p in pred["setups"]}
    res["Q5"] = {s["name"]: dict(
        H=s["largest_all_H"]/pmap[s["name"]]["max_ratio_H_pred"],
        M=s["largest_all_M"]/pmap[s["name"]]["max_ratio_M_pred"]) for s in S}
    A.jdump(res, os.path.join(a.out, "a4res.json"))
    with open(os.path.join(a.out, "verdicts.md"), "w") as fp:
        fp.write(table(res))
        fp.write("\nfamilies: " + json.dumps(fam) + "\n")
        if "resolution_pair" in res:
            rp = res["resolution_pair"]
            fp.write(f"resolution pair {rp['lo']}/{rp['hi']}: Q6 {rp['Q6']}, Q7 {rp['Q7']}, "
                     f"A5 band {rp['A5_band']}\n")
        fp.write("Q5 measured/predicted largest: " + json.dumps(res["Q5"]) + "\n")
    print(open(os.path.join(a.out, "verdicts.md")).read())
    if len(S) == len(A.SETUPS):
        figures(res, pred, a.out)


if __name__ == "__main__":
    main()
