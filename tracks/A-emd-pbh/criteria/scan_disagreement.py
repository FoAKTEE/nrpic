#!/usr/bin/env python3
"""Where do the criteria disagree over the parameter range of the brief's threshold surface?

    python3 scan_disagreement.py

Range (S1 deliverable 1 and the comparison named in the minimum publishable unit, brief
lines 347 and 362): ellipticity 0 <= e <= 0.25 and p = 0 as in the dust/particle scan of
2609.14218 (MDPBH.tex:966), prolateness -e <= p <= e as a band, amplitude 0.01 <= delta <=
1, statistical context sigma_H = 0.003, 0.01, 0.03 (zeta_rms = 5 sigma_H/2), velocity
dispersion via the adiabatic invariant, duration a_end/a_H = 10, 100. Writes
scan_summary.json and figures scan_*.{pdf,png} into scratch/A-emd-pbh/<run_id>/.
"""
import itertools
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "python"))
import emd_criteria as C  # noqa: E402
import predict as P  # noqa: E402
import runlog  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

# 2609.14218 MDPBH.tex: particle runs halt for mu <= 0.045 at e = 0.2, p = 0 (1084, 1141-1146);
# dust runs crash before horizon formation for mu <= 0.95 at e = 0.2 (1084-1086). Mapping to
# delta at horizon entry aH = k/sqrt6 (908, 913, 987): delta = (2 mu/5) k^2/(aH)^2 = 12 mu/5.
MU_TO_DELTA = 12.0 / 5.0


def thresholds_vs_e(e, sigmaH, aend):
    out = {}
    out["R1 hoop ball (1609.01588)"] = C.hoop_threshold_delta(e, 0.0)
    out["R2 hoop peak (2508.10070)"] = np.where(e < 1 / 3, C.hoop_peak_threshold_delta(e, 0.0),
                                                np.nan)
    out["R3 Kerr bound (1707.03595)"] = np.full_like(e, C.spin_threshold(0, 1, sigmaH)[0])
    out["R8 dispersion (2211.13950)"] = np.full_like(e, float(C.vd_delta_th(sigmaH, 1, 1)))
    out["R9 top hat (2507.18312)"] = np.full_like(e, C.profile_threshold(2.5 * sigmaH))
    out["R4 duration (1707.03595)"] = np.full_like(e, 1.0 / aend)
    return out


def main():
    inputs = [os.path.join(HERE, f) for f in ("emd_criteria.py", "predict.py",
                                              "scan_disagreement.py")]
    with runlog.Run("A-pre-2: scan the analytic criteria over the brief's range "
                    "(e, p, delta, sigma_v, a_end) and record where they disagree",
                    "scouting", inputs) as run:
        out = run.out
        print(f"run {run.run_id} -> {out}", flush=True)
        summary = {"run_id": run.run_id}
        e = np.linspace(0.0, 0.25, 126)
        fs.use_style()

        # ---------------- figure 1: four panels
        fig = plt.figure(figsize=(fs.FULL_WIDTH, 6.6))
        axA = fs.inch_axes(fig, 0.75, 3.75, 3.2, 2.7)
        axB = fs.inch_axes(fig, 4.65, 3.75, 3.2, 2.7)
        axC = fs.inch_axes(fig, 0.75, 0.5, 3.2, 2.7)
        axD = fs.inch_axes(fig, 4.65, 0.5, 3.2, 2.7)
        # (A) threshold amplitude vs ellipticity
        sig = 0.01
        th = thresholds_vs_e(e, sig, 100.0)
        cols = [fs.PAL["red"], fs.PAL["orange"], fs.PAL["green"], fs.PAL["blue"],
                fs.PAL["yellow"], "grey"]
        for (k, v), col in zip(th.items(), cols):
            axA.plot(e, v, color=col, ls="-" if k.startswith(("R1", "R2")) else "--")
            if k.startswith(("R1", "R2")):
                i = np.argmin(abs(e - 0.1))
                axA.text(0.1, v[i] * (0.62 if k.startswith("R1") else 1.25), k, color=col,
                         fontsize=7, ha="center")
            else:
                axA.text(0.248, v[-1] * 1.08, k, color=col, fontsize=7, ha="right",
                         va="bottom")
        pp = np.linspace(-1, 1, 41)
        band = np.array([[C.hoop_threshold_delta(x, f * x) for f in pp] for x in e])
        axA.fill_between(e, band.min(1), band.max(1), color=fs.PAL["red"], alpha=0.2, lw=0)
        axA.plot([0.2], [0.045 * MU_TO_DELTA], "*", color="k", ms=9)
        axA.text(0.2, 0.045 * MU_TO_DELTA * 1.2, "2609.14218 particles", fontsize=7,
                 ha="center", va="bottom")
        axA.annotate("", xy=(0.2, 2.6), xytext=(0.2, 0.95 * MU_TO_DELTA),
                     arrowprops=dict(arrowstyle="->", color="k", lw=1.0))
        axA.text(0.205, 2.45, "dust: horizon\nonly above", fontsize=7, va="top")
        axA.set_yscale("log")
        axA.set_ylim(5e-3, 4)
        axA.set_xlim(0, 0.25)
        axA.set_xlabel(r"ellipticity $e$  ($p=0$)", labelpad=-2)
        axA.set_ylabel(r"threshold $\delta_{\rm th}$ at horizon entry")
        axA.text(0.01, 2.5, r"$\sigma_H=0.01$, $a_{\rm end}/a_H=100$", fontsize=8)
        summary["thresholds_sigmaH_0.01"] = {k: [float(v[0]), float(v[np.argmin(abs(e - 0.1))]),
                                                 float(v[np.argmin(abs(e - 0.2))])]
                                             for k, v in th.items()}
        summary["thresholds_columns"] = "values at e = 0, 0.1, 0.2 (p = 0)"
        r = (C.hoop_peak_threshold_delta(e[1:], 0) / C.hoop_threshold_delta(e[1:], 0))
        summary["peak_over_ball_hoop_ratio_range"] = [float(np.nanmin(r)), float(np.nanmax(r))]
        summary["hoop_ball_delta_th_at_e0.2"] = float(C.hoop_threshold_delta(0.2, 0))
        summary["particle_2609_delta_at_e0.2"] = 0.045 * MU_TO_DELTA
        # (B) spin predictions vs amplitude
        d = np.geomspace(0.01, 1, 200)
        for s, col in zip((0.003, 0.01, 0.03), fs.SERIES[:3]):
            a2 = C.spin_a2(1.0, s, d)
            ok = d >= C.spin_threshold(0, 1, s)[0]
            axB.plot(d[ok], a2[ok], color=col, label=fr"1707: $a_{{*(2)}}$, $\sigma_H={s}$")
            ok9 = d >= C.profile_threshold(2.5 * s)
            axB.plot(d[ok9], C.profile_spin_rms(2.5 * s, d[ok9]), color=col, ls="--")
            axB.axhline(0.043 * math.sqrt(s / 6), color=col, ls=":", lw=1.0)
        axB.plot([], [], color="k", ls="--", label=r"2507: $\zeta^2/\delta^{5/2}$")
        axB.plot([], [], color="k", ls=":", lw=1.0,
                 label=r"2508: $0.043\,(\sigma_H/6)^{1/2}$ ($\gamma$=0.99)")
        axB.axhline(1.0, **fs.MASK_LINE)
        axB.set_xscale("log")
        axB.set_yscale("log")
        axB.set_ylim(1e-4, 3)
        axB.set_xlabel(r"$\delta$ at horizon entry", labelpad=-2)
        axB.set_ylabel(r"spin $a$")
        axB.legend(loc="lower left", fontsize=6)
        # (C) critical velocity dispersion on the initial slice vs H R there
        hr = np.linspace(0.05, 1.0, 100)
        axC.plot(hr, 1.5 * hr ** 2, color=fs.PAL["blue"],
                 label=r"2211: $\sigma_v R<3M$  ($\sigma_{v,H}<1.5$)")
        axC.plot(hr, math.sqrt(0.3) * hr ** 2, color=fs.PAL["red"],
                 label=r"2507 virial  ($\sigma_{v,H}<0.548$)")
        axC.set_xlabel(r"$H R$ on the initial slice")
        axC.set_ylabel(r"critical $\sigma_{v}$ on the initial slice")
        axC.legend(loc="upper left", fontsize=7)
        axC.set_xlim(0, 1)
        axC.set_ylim(0, 1.6)
        summary["critical_sigv_H"] = {"2211.13950": 1.5, "2507.18312": math.sqrt(0.3)}
        # (D) duration: scale factor of formation x delta, vs e
        axD.plot(e, 3 / (1 + 3 * e), color=fs.PAL["red"],
                 label=r"Zel'dovich pancake $a_c=1/\alpha$ (1609)")
        axD.axhline(1.0, color=fs.PAL["green"], label=r"$\delta(t_{\rm end})=1$ (1707)")
        for dd, ls in ((0.01, "-"), (0.3, "--")):
            axD.axhline(C.tophat_aBH(dd) * dd, color=fs.PAL["blue"], ls=ls,
                        label=fr"exact top hat $R=2M$, $\delta={dd}$")
        axD.axhline(C.tophat_amax(1.0), **fs.MASK_LINE, label="top hat turnaround")
        axD.set_ylim(0, 3.3)
        axD.set_xlim(0, 0.25)
        axD.set_xlabel(r"ellipticity $e$  ($p=0$)", labelpad=-2)
        axD.set_ylabel(r"$\delta\cdot a_{\rm form}/a_H$")
        axD.legend(loc="lower left", fontsize=6)
        summary["formation_a_times_delta"] = {
            "zeldovich_e0": 3.0, "1707_turnaround": 1.0,
            "tophat_RS_delta0.01": float(C.tophat_aBH(0.01) * 0.01),
            "tophat_RS_delta0.3": float(C.tophat_aBH(0.3) * 0.3),
            "tophat_singularity_delta0.01": float(C.tophat_acoll(0.01) * 0.01),
            "tophat_turnaround": float(C.tophat_amax(1.0))}
        fs.save(fig, os.path.join(out, "scan_criteria_overview"))
        plt.close(fig)

        # ---------------- figure 2: map of verdicts and pairwise disagreement
        dgrid = np.geomspace(0.01, 1.0, 81)
        egrid = np.linspace(0.0, 0.25, 51)
        ids = ["R1", "R2", "R3", "R8", "R9"]
        pair_frac = {}
        maps = {}
        for s in (0.003, 0.01, 0.03):
            V = {i: np.zeros((len(egrid), len(dgrid)), dtype=float) for i in ids}
            for (ie, ee), (jd, dd) in itertools.product(enumerate(egrid), enumerate(dgrid)):
                rows = P.predict(dd, ee, 0.0, 0.0, math.inf, s)
                for rr in rows:
                    if rr["id"] in V:
                        V[rr["id"]][ie, jd] = np.nan if rr["collapse"] is None else float(
                            rr["collapse"])
            maps[s] = V
            pf = {}
            for i, j in itertools.combinations(ids, 2):
                m = np.isfinite(V[i]) & np.isfinite(V[j])
                pf[f"{i}-{j}"] = float(np.mean(V[i][m] != V[j][m]))
            pair_frac[str(s)] = pf
        summary["pairwise_disagreement_fraction"] = pair_frac
        summary["grid"] = "delta in [0.01, 1] (81 log), e in [0, 0.25] (51), p = 0"
        fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.3))
        for k, s in enumerate((0.003, 0.01, 0.03)):
            ax = fs.inch_axes(fig, 0.65 + k * 2.2, 0.5, 2.0, 2.5)
            V = maps[s]
            n = sum(np.nan_to_num(V[i]) for i in ids)
            im = ax.pcolormesh(dgrid, egrid, n, cmap="viridis", vmin=0, vmax=5, shading="nearest",
                               rasterized=True)
            ax.contour(dgrid, egrid, V["R1"], levels=[0.5], colors=[fs.PAL["red"]],
                       linewidths=1.5)
            ax.contour(dgrid, egrid, np.nan_to_num(V["R2"]), levels=[0.5],
                       colors=[fs.PAL["orange"]], linewidths=1.5)
            ax.plot([0.045 * MU_TO_DELTA], [0.2], "*", color="w", ms=9, mec="k")
            ax.set_xscale("log")
            ax.set_xticks([0.01, 0.1, 1])
            ax.set_xticklabels(["0.01", "0.1", "1"])
            ax.set_xlabel(r"$\delta$")
            if k == 0:
                ax.set_ylabel(r"$e$  ($p=0$)")
            else:
                ax.set_yticklabels([])
            ax.set_title(fr"$\sigma_H={s}$", fontsize=9)
        cax = fs.inch_axes(fig, 0.65 + 3 * 2.2 - 0.05, 0.5, 0.08, 2.5)
        cb = fig.colorbar(im, cax=cax)
        cb.set_label("criteria predicting collapse (of 5)")
        fs.save(fig, os.path.join(out, "scan_verdict_map"))
        plt.close(fig)

        # ---------------- example tables for the README
        examples = [dict(delta=0.1, e=0.0, sigmaH=0.01), dict(delta=0.1, e=0.1, sigmaH=0.01),
                    dict(delta=0.1, e=0.2, sigmaH=0.01), dict(delta=0.3, e=0.02, sigmaH=0.01),
                    dict(delta=0.03, e=0.0, sigmaH=0.003, aend=100.0)]
        with open(os.path.join(out, "example_tables.txt"), "w") as f:
            for ex in examples:
                rows = P.predict(ex["delta"], ex["e"], 0.0, 0.0, ex.get("aend", math.inf),
                                 ex["sigmaH"])
                P.print_table(rows, ex, out=f)
                f.write("\n")
        with open(os.path.join(out, "scan_summary.json"), "w") as f:
            json.dump(summary, f, indent=1)
        print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
