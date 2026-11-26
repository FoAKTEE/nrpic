"""V7: remaining ledger checks. (a) D2 of FF4 (M/4) after the end of its own control (V-1L4
ends at 299 M): restricted, control held at its last value, and with V-1L; (b) particle-number
rms over +-25 M windows; (c) P9 medians of FK for tau_rem 285-500 M; (d) FK against ES-FL in
the first 20 M (only the first search should differ, P7); (e) M_AH of ES-FL at the end.

python3 v7_checks.py --scratch <scratch/D-bh-dress> --v3 <V3 run dir> --out <dir>
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vio  # noqa: E402

S = {"FF4": ("D-20261123-022727-1c17e73", "esfl4"), "V-1L4": ("D-20261123-022715-ab5d983", "v1l4"),
     "V-1L": ("D-20261121-203124-a34cf1f", "v1l"), "FNQ": ("D-20261124-172725-2f426b6", "esflkq"),
     "FK": ("D-20261123-022725-a553496", "esflk"), "FN4": ("D-20261124-134157-b17938b", "esflk4n"),
     "ES-FL": ("D-20261121-203150-15f2bad", "esfl")}


def summ(scr, lab, keep_bad=False):
    rid, base = S[lab]
    s, bad = vio.read_summary(os.path.join(scr, rid, f"{base}.horizon_summary_0.txt"))
    return (s, bad) if keep_bad else (s[~bad, 1], s[~bad, 2])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--v3", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = {}
    A = np.load(os.path.join(a.v3, "v3_FF4.npz"))
    ts, Ms = summ(a.scratch, "FF4")
    tr = A["tr"]
    mEK = A["mrest"] * np.sqrt(1 - 2.0 / A["R0"])
    Fc = np.concatenate([[0.0], np.cumsum(mEK)])
    # F_sph from acc.hst as in v3
    acc = vio.read_text_table(os.path.join(a.scratch, S["FF4"][0], "esfl4.acc.hst"))
    ta = acc[:, 0]
    _, idx = np.unique(ta[::-1], return_index=True)
    acc = acc[np.sort(len(ta) - 1 - idx)]
    acc = acc[np.argsort(acc[:, 0])]
    C0 = 0.002584060636653588  # content inside r = 5 M of the N data (v3 run, D2.C0)
    d2 = {}
    for name, ctl, hold in [("V-1L4_to_299", "V-1L4", False), ("V-1L4_held_after_299", "V-1L4", True),
                            ("V-1L", "V-1L", True)]:
        tc, Mc = summ(a.scratch, ctl)
        w = (ts >= 20) & ((ts <= tc[-1]) | hold)
        tt = ts[w]
        lhs = Ms[w] - np.interp(tt, tc, Mc)
        Fr = Fc[np.searchsorted(tr, tt, side="right")]
        Fs = C0 + np.interp(tt, acc[:, 0], acc[:, 19] - acc[:, 22])
        lo = lhs - (Fr - 3e-3)
        hi = Fs + 3e-3 - lhs
        viol = (lo < 0) | (hi < 0)
        d2[name] = dict(n=int(len(tt)), n_viol=int(viol.sum()), min_lower=float(lo.min()),
                        t_min_lower=float(tt[np.argmin(lo)]),
                        first_viol=float(tt[viol][0]) if viol.any() else None,
                        lower_margin_at_end=float(lo[-1]))
    res["FF4_D2"] = d2
    # (b) +-25 M windows
    m = {k: summ(a.scratch, k) for k in ["FNQ", "FK", "FN4"]}
    win = {}
    for T in [100.0, 200.0, 300.0, 399.5]:
        tg = np.arange(max(20.0, T - 25), min(399.5, T + 25) + 1e-9, 0.5)
        q, n, f = (np.interp(tg, *m["FNQ"]), np.interp(tg, *m["FK"]), np.interp(tg, *m["FN4"]))
        r1 = np.sqrt(np.mean((n - q) ** 2))
        r2 = np.sqrt(np.mean((f - n) ** 2))
        win[str(T)] = dict(window=[float(tg[0]), float(tg[-1])], ratio=float(r1 / r2))
    res["pn_windows_pm25"] = win
    # (c) P9: FK and ES-FL medians for tau_rem 285-500 M
    J = json.load(open(os.path.join(a.v3, "v3_growth.json")))
    for lab in ["FK", "ES-FL", "FN4", "FNQ"]:
        c = np.array(J[lab]["iii"]["tab"]["centres"])
        md = np.array(J[lab]["iii"]["tab"]["medians"])
        w = (c > 285) & (c < 500)
        res[f"P9_{lab}"] = dict(min=float(100 * md[w].min()), max=float(100 * md[w].max()),
                                nbins=int(w.sum()))
    # (d) FK against ES-FL in the first 20 M
    sF, bF = summ(a.scratch, "FK", keep_bad=True)
    sE, bE = summ(a.scratch, "ES-FL", keep_bad=True)
    common, i1, i2 = np.intersect1d(sF[:, 1], sE[:, 1], return_indices=True)
    d = np.abs(sF[i1, 2] - sE[i2, 2])
    early = common <= 20
    res["FK_vs_ESFL"] = dict(t0_FK=float(sF[0, 2]), t0_ESFL=float(sE[0, 2]),
                             max_absdiff_le20=float(np.nanmax(d[early])),
                             n_identical_le20=int(np.sum(d[early] == 0)), n_le20=int(early.sum()),
                             max_absdiff_20_219=float(np.nanmax(d[(common > 20) & (common <= 219)])),
                             first_t_diff_gt_1e12_after_1=float(common[(common > 1) & (d > 1e-12)][0])
                             if np.any((common > 1) & (d > 1e-12)) else None)
    tE, ME = summ(a.scratch, "ES-FL")
    res["ESFL_end"] = dict(t=float(tE[-1]), M=float(ME[-1]))
    json.dump(res, open(os.path.join(a.out, "v7_checks.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
