#!/usr/bin/env python3
"""Post-hoc checks of the window scan (written AFTER the analysis run
E-20261121-154733-0d1fbda was seen; ../JOURNAL.md entry 4 says so).

    python3 posthoc_window.py --ana ANALYSIS_RUN_DIR --out OUT

Reads the caches <run>.npz of analyse_window.py (R^NR per mode at every dump, constraint
record) and recomputes the linear reference per window, then reports for the USR case:
  1. per band of k: shell medians and maxima of the odd-part error |O/ref - 1|, the even
     part |E|/|ref| and the error of the +1 run alone |P/ref - 1| at the last dump, and the
     fraction of modes whose even part exceeds the odd-part error (where the second-order
     part is visible in a single run);
  2. the odd shell-power shift against the baseline compared with the baseline's own
     NR-vs-reference power error (how much of the error is common to the windows);
  3. the constraint records <|H|/[H]> and <|M|/[M]> at the last row and their maxima and
     the times of the maxima.
Writes OUT/posthoc_usr.json and OUT/fig/fig_usr_second_order.png.
"""
import argparse
import json
import os

import numpy as np

import window_lib as wl

BANDS = (("k<6", 0, 6), ("6<=k<12", 6, 12), ("12<=k<=16", 12, 16.0001), ("16<k<=32", 16.0001, 32.0001))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ana", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(os.path.join(a.out, "fig"), exist_ok=True)
    c = wl.CASES["usr"]
    modes = wl.Modes(c["nmesh"], c["nmax2"])
    alpha = modes.alpha()
    n2s, r0, dr0 = wl.shells("usr")
    assert np.array_equal(modes.shell_n2, n2s)
    z = {n: np.load(os.path.join(a.ana, f"{n}.npz"))
         for w in wl.WINDOWS for n in (f"{w}_p", f"{w}_m")}
    t = z["b_p"]["t"]
    ref = wl.reference("usr", n2s.astype(float), r0, dr0, t)
    st = ref.at(t.size - 1)
    k = modes.k
    ks = np.sqrt(modes.shell_n2.astype(float))
    ns = ks.size
    cnt = np.bincount(modes.shell_of, minlength=ns)
    shellP = lambda X: np.bincount(modes.shell_of, weights=np.abs(X)**2, minlength=ns) / cnt
    shell_med = lambda v: np.array([np.median(v[modes.shell_of == j]) for j in range(ns)])
    out = dict(analysis_run=os.path.basename(os.path.normpath(a.ana)), last_dump_time=float(t[-1]),
               last_dump_cN=float(st["lna"]), windows={})
    curves = {}
    Ob = Pb = refb = None
    for w, (s, sig) in wl.WINDOWS.items():
        W = wl.window(k, st["a"], st["H"], s, sig)
        refw = wl.L_BOX**-1.5 * W * st["R"][modes.shell_of] * alpha
        P = z[f"{w}_p"]["cnr"][-1]
        M = z[f"{w}_m"]["cnr"][-1]
        O, E = 0.5 * (P - M), 0.5 * (P + M)
        eo = np.abs(O / refw - 1.0)
        ee = np.abs(E) / np.abs(refw)
        ep = np.abs(P / refw - 1.0)
        ent = dict(bands={})
        for lab, lo, hi in BANDS:
            sel = (k >= lo) & (k < hi)
            ent["bands"][lab] = dict(
                nmodes=int(sel.sum()),
                odd_err_median=float(np.median(eo[sel])), odd_err_max=float(eo[sel].max()),
                even_median=float(np.median(ee[sel])), even_p90=float(np.percentile(ee[sel], 90)),
                even_max=float(ee[sel].max()),
                plus_run_err_median=float(np.median(ep[sel])), plus_run_err_max=float(ep[sel].max()),
                frac_even_gt_odd_err=float(np.mean(ee[sel] > eo[sel])))
        if w == "b":
            Ob, Pb, refb = O, P, refw
            curves["b"] = (shell_med(eo), shell_med(ee), shell_med(ep))
        else:
            dnr = shellP(O) / shellP(Ob) - 1.0
            e_b = np.abs(shellP(Ob) / shellP(refb) - 1.0)
            dE = shellP(P) / shellP(Pb) - 1.0 - dnr
            ent["shift_vs_baseline_error"] = {}
            for lab, lo, hi in BANDS:
                sel = (ks >= lo) & (ks < hi)
                ent["shift_vs_baseline_error"][lab] = dict(
                    odd_shift_max=float(np.abs(dnr[sel]).max()),
                    baseline_power_err_max=float(e_b[sel].max()),
                    ratio_max=float((np.abs(dnr[sel]) / e_b[sel]).max()),
                    even_contrib_to_plus_run_shift_max=float(np.abs(dE[sel]).max()))
            if w == "g2":
                curves["g2"] = (shell_med(eo), shell_med(ee), shell_med(ep))
        con = z[f"{w}_p"]["con"]
        late = con[:, 2] > 5.0
        ent["records"] = dict(
            H_last=float(con[-1, 3]), M_last=float(con[-1, 6]), cN_last=float(con[-1, 2]),
            H_max_late=float(con[late, 3].max()), M_max_late=float(con[late, 6].max()),
            cN_of_M_max_late=float(con[late, 2][np.argmax(con[late, 6])]),
            cN_H_below_3e_14=float(con[late, 2][np.argmax(con[late, 3] < 3e-14)])
            if (con[late, 3] < 3e-14).any() else None)
        out["windows"][w] = ent
    with open(os.path.join(a.out, "posthoc_usr.json"), "w") as fp:
        json.dump(out, fp, indent=1)
    print(json.dumps(out, indent=1))
    # ---- figure: where the second-order part is visible (shell medians at the last dump)
    import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 3.8))
    fig.subplots_adjust(left=0.14, right=0.97, top=0.96, bottom=0.13)
    sty = {"b": dict(color=fs.PAL["blue"]), "g2": dict(color="purple")}
    for w, (meo, mee, mep) in curves.items():
        lab = wl.LABEL[w]
        ax.semilogy(ks, meo, lw=1.0, ls="-", label=f"{lab}: odd part |O/ref-1|", **sty[w])
        ax.semilogy(ks, mee, lw=1.0, ls="--", label=f"{lab}: even part |E|/|ref|", **sty[w])
        ax.semilogy(ks, mep, ".", ms=2.0, label=f"{lab}: +1 run alone |P/ref-1|", **sty[w])
    ax.axvline(16.0, **fs.MASK_LINE)
    ax.set_xlabel(r"$k/dk$ (shell)")
    ax.set_ylabel(f"shell median at cN = {out['last_dump_cN']:.2f}")
    ax.legend(loc="upper left", fontsize=6.5)
    fs.save(fig, os.path.join(a.out, "fig", "fig_usr_second_order"))
    plt.close(fig)


if __name__ == "__main__":
    main()
