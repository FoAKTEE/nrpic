#!/usr/bin/env python3
"""P16' of JOURNAL.md (wave 3): the jittered lattice without any wave (jit0p3_nw) against the
jittered null with the x wave (jit0p3), same deviates, 64^3.

    python3 p16_compare.py nw=<case json> j3=<case json> pred_nw=<null_prediction.json>
                           pred_j3=<null_prediction.json> spec_nw=<null_spectrum.json>
                           spec_j3=<null_spectrum.json> [kcut=16] [shells=16,24,31]
                                                                       (output: $NRPIC_RUN_DIR)

case json: analyze_scan.py; null_prediction.json: null_prediction.py on the initial data;
null_spectrum.json: null_spectrum.py with the dumps named <x>_tau0.1, <x>_a2, <x>_a12
(x = nw, j3). kcut is the shell number of k h = pi/2 (16 at 64^3, 8 at 32^3) and shells the
shells where the per-shell ratios are reported (16,24,31 at 64^3; 8,12,15 at 32^3); the
"16" in the names of the keys below is kcut. Writes p16_summary.json and p16_compare.{png,pdf}:
  (i)   non-TT shell power of h at |k|L/2pi >= 16, nw over j3, per dump;
  (ii)  D = TT shell power of h at |k|L/2pi >= 16, nw over j3, per dump, and the per-shell
        ratio P_TT/P_nonTT of nw over that of j3 at |k|L/2pi = 16, 24, 31;
  (iv)  box modes of nw against the prediction (noise-noise term; cross term of the x-mean
        of the noise) for 3 <= a <= 20;
  (v)   c(j3) - c(nw) at K1, K2 against cross x g_cross of j3's prediction, 3 <= a <= 20;
  (vi)  rms TT of all modes, nw over j3, 2 <= a <= 20.
"""
import json
import os
import sys

import numpy as np
from scipy.interpolate import CubicSpline

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fslib"))
import paths  # noqa: E402,F401
from fslib import reference as ref  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

DUMPS = ("tau0.1", "a2", "a12")


def load(path, kind="bin"):
    c = json.load(open(path))
    rows = [r for r in c["rows"] if r.get("kind") == kind and "error" not in r]
    rows.sort(key=lambda r: r["time"])
    out, last = [], None
    for r in rows:
        if last is None or r["time"] > last + 1e-9:
            out.append(r)
            last = r["time"]
    return out


def cplx(rows, key):
    v = np.array([r[key] for r in rows], dtype=float)
    return v[:, 0] + 1j * v[:, 1]


def interp(t_src, y_src, t):
    if np.iscomplexobj(y_src):
        return interp(t_src, y_src.real, t) + 1j * interp(t_src, y_src.imag, t)
    out = CubicSpline(t_src, y_src)(t)
    out[(t < t_src[0]) | (t > t_src[-1])] = np.nan
    return out


def mmm(x):
    x = np.asarray(x)
    x = x[np.isfinite(x)]
    return [float(np.min(x)), float(np.median(x)), float(np.max(x))] if x.size else None


def pred_series(pred, name, K, part):
    pc = pred["cases"][name]
    out = 0.0
    if part in ("cross", "both"):
        out = out + complex(*pc[f"cross_{K}_plus"]) * np.array(pred["g_cross"])
    if part in ("nn", "both"):
        out = out + complex(*pc[f"nn_{K}_plus"]) * np.array(pred["g_nn"])
    return np.array(pred["tau"]), out


def main():
    od = os.environ.get("NRPIC_RUN_DIR", ".")
    arg = dict(a.split("=", 1) for a in sys.argv[1:])
    kc = int(arg.get("kcut", "16"))
    SHELLS = tuple(int(v) for v in arg.get("shells", "16,24,31").split(","))
    nw, j3 = load(arg["nw"]), load(arg["j3"])
    pnw, pj3 = json.load(open(arg["pred_nw"])), json.load(open(arg["pred_j3"]))
    snw, sj3 = json.load(open(arg["spec_nw"])), json.load(open(arg["spec_j3"]))
    name_nw = [n for n in pnw["cases"] if n.startswith("jit0p3")][0]
    S = {"inputs": arg, "pred_case_nw": name_nw}

    # (i), (ii): shell spectra
    spec = {}
    for d in DUMPS:
        a, b = snw[f"nw_{d}"]["h"], sj3[f"j3_{d}"]["h"]
        tn, nn_ = np.array(a["shell_TT"]), np.array(a["shell_nonTT"])
        tj, nj = np.array(b["shell_TT"]), np.array(b["shell_nonTT"])
        r = {"a_nw": snw[f"nw_{d}"]["a"], "a_j3": sj3[f"j3_{d}"]["a"],
             "kcut": kc,
             "nonTT_ge16_nw_over_j3": float(nn_[kc:].sum() / nj[kc:].sum()),
             "D_TT_ge16_nw_over_j3": float(tn[kc:].sum() / tj[kc:].sum()),
             "frac_TT_ge_kcut_nw": float(tn[kc:].sum() / tn[1:].sum()),
             "frac_TT_ge_kcut_j3": float(tj[kc:].sum() / tj[1:].sum()),
             "TT_lt8_nw_over_j3": float(tn[1:kc // 2].sum() / tj[1:kc // 2].sum()),
             "nonTT_lt8_nw_over_j3": float(nn_[1:kc // 2].sum() / nj[1:kc // 2].sum()),
             "frac_TT_ge16_nw": a["frac_TT_ge16"], "frac_TT_ge16_j3": b["frac_TT_ge16"],
             "rms_TT_nw": a["rms_TT"], "rms_TT_j3": b["rms_TT"]}
        for s in SHELLS:
            r[f"ratio_of_TT_over_nonTT_shell{s}_nw_over_j3"] = float((tn[s] / nn_[s]) / (tj[s] / nj[s]))
            r[f"TT_over_nonTT_shell{s}_nw"] = float(tn[s] / nn_[s])
            r[f"TT_over_nonTT_shell{s}_j3"] = float(tj[s] / nj[s])
        spec[d] = r
    S["spectra"] = spec

    # (iv), (v), (vi): time series
    tnw, tj3 = np.array([r["time"] for r in nw]), np.array([r["time"] for r in j3])
    anw = ref.a_of_tau(tnw)
    box = {}
    for K in ("K1", "K2"):
        meas = cplx(nw, f"h_{K}_plus")
        pt, pr = pred_series(pnw, name_nw, K, "both")
        p_at = interp(pt, pr, tnw)
        m = (anw >= 3.0) & (anw <= 20.0)
        box[f"nw_{K}_mod_ratio_3_20"] = mmm(np.abs(meas[m]) / np.abs(p_at[m]))
        box[f"nw_{K}_phase_diff_3_20"] = mmm(np.angle(meas[m] / p_at[m]))
        box[f"nw_{K}_pred_static_nn"] = pnw["cases"][name_nw][f"nn_{K}_plus"]
        box[f"nw_{K}_pred_static_cross"] = pnw["cases"][name_nw][f"cross_{K}_plus"]
        # (v) difference on the times of the no-wave run
        dj = interp(tj3, cplx(j3, f"h_{K}_plus"), tnw) - meas
        pt3, pc3 = pred_series(pj3, "jit0p3", K, "cross")
        pc_at = interp(pt3, pc3, tnw)
        box[f"diff_{K}_mod_ratio_3_20"] = mmm(np.abs(dj[m]) / np.abs(pc_at[m]))
        box[f"diff_{K}_phase_diff_3_20"] = mmm(np.angle(dj[m] / pc_at[m]))
        box[f"_series_{K}"] = {"a": anw.tolist(), "nw": [[z.real, z.imag] for z in meas],
                               "pred_nw": [[z.real, z.imag] for z in p_at],
                               "diff": [[z.real, z.imag] for z in dj],
                               "pred_cross": [[z.real, z.imag] for z in pc_at]}
    S["box_modes"] = {k: v for k, v in box.items() if not k.startswith("_")}
    rms_nw = np.array([r["rms_TT"] for r in nw])
    rms_j3 = interp(tj3, np.array([r["rms_TT"] for r in j3]), tnw)
    rt = rms_nw / rms_j3
    S["rmsTT_nw_over_j3"] = {f"a{lo}_{hi}": mmm(rt[(anw >= lo) & (anw <= hi)])
                             for lo, hi in ((1.0, 2.0), (2.0, 20.0), (2.0, 5.0), (5.0, 20.0))}
    S["rmsTT_nw_first_dumps"] = [[float(anw[i]), float(rms_nw[i]), float(rms_j3[i])] for i in range(min(4, len(anw)))]
    S["last_nw"] = {k: nw[-1].get(k) for k in ("a", "rms_TT", "max_TT_mode", "rho_kin", "rho_grad", "rms_nonTT")}

    # figure
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 4, figsize=(13.0, 3.1))
    for d, col in zip(DUMPS, ("C0", "C1", "C2")):
        a, b = snw[f"nw_{d}"]["h"], sj3[f"j3_{d}"]["h"]
        kb = np.arange(len(a["shell_TT"]))
        tn, nn_ = np.array(a["shell_TT"]), np.array(a["shell_nonTT"])
        tj, nj = np.array(b["shell_TT"]), np.array(b["shell_nonTT"])
        mk = (kb > 0) & (nj > 0) & (nn_ > 0)
        ax[0].plot(kb[mk], tn[mk], color=col, label=f"no wave, {d} (a={spec[d]['a_nw']:.1f})")
        ax[0].plot(kb[mk], tj[mk], color=col, ls="--", lw=0.8, label=f"jit0p3, {d}")
        with np.errstate(divide="ignore", invalid="ignore"):
            ax[1].plot(kb[mk], (tn[mk] / nn_[mk]) / (tj[mk] / nj[mk]), color=col, label=f"TT/nonTT ratio, {d}")
            ax[1].plot(kb[mk], nn_[mk] / nj[mk], color=col, ls=":", lw=0.8, label=f"nonTT power ratio, {d}")
    ax[0].set_xscale("log")
    ax[0].set_yscale("log")
    ax[0].set_xlabel("|k| L / 2 pi")
    ax[0].set_ylabel("TT shell power of h")
    ax[0].axvline(kc, color="0.6", lw=0.6)
    ax[0].legend(fontsize=5)
    ax[1].set_xscale("log")
    ax[1].set_yscale("log")
    ax[1].set_xlabel("|k| L / 2 pi")
    ax[1].set_ylabel("no wave / jit0p3 (per shell)")
    ax[1].axhspan(0.5, 2.0, color="0.92", zorder=0)
    ax[1].axvline(kc, color="0.6", lw=0.6)
    ax[1].legend(fontsize=5)
    for K, ls in (("K1", "-"), ("K2", ":")):
        sr = box[f"_series_{K}"]
        a_ = np.array(sr["a"])
        f = lambda v: np.abs(np.array(v)[:, 0] + 1j * np.array(v)[:, 1])  # noqa: E731
        ax[2].plot(a_, f(sr["nw"]), color="C0", ls=ls, label=f"no wave {K}")
        ax[2].plot(a_, f(sr["pred_nw"]), color="C0", ls=ls, lw=2.5, alpha=0.35)
        ax[2].plot(a_, f(sr["diff"]), color="C3", ls=ls, label=f"jit0p3 - no wave {K}")
        ax[2].plot(a_, f(sr["pred_cross"]), color="C3", ls=ls, lw=2.5, alpha=0.35)
    ax[2].set_xscale("log")
    ax[2].set_yscale("log")
    ax[2].set_xlabel("a")
    ax[2].set_ylabel("|h_+| box modes (thick pale: prediction)")
    ax[2].axvspan(3, 20, color="0.94", zorder=0)
    ax[2].legend(fontsize=5)
    ax[3].plot(anw, rms_nw, color="C0", label="rms TT, no wave")
    ax[3].plot(anw, rms_j3, color="C1", ls="--", label="rms TT, jit0p3")
    ax[3].plot(anw, [r["max_TT_mode"] for r in nw], color="C0", lw=0.6, alpha=0.6, label="largest TT mode, no wave")
    ax[3].set_xscale("log")
    ax[3].set_yscale("log")
    ax[3].set_xlabel("a")
    ax[3].set_ylabel("TT of h")
    ax[3].legend(fontsize=5)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(od, f"p16_compare.{ext}"), dpi=150)
    with open(os.path.join(od, "p16_summary.json"), "w") as f:
        json.dump(S, f, indent=1)
    print(json.dumps({k: v for k, v in S.items() if k != "inputs"}, indent=1))


if __name__ == "__main__":
    main()
