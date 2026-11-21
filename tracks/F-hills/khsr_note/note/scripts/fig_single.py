"""Figure: a single member on the card: gauge settling of its tracker and drift of its horizon.

Reads the raw outputs of the two single-puncture card runs of test E3 (common.RUNS["e3raw"]:
one Bowen-York puncture of mass m with momentum P = 0.25 m, finest cells m/8; S3 with shift
damping eta m = 2, S2 with eta m = 0.25, the damping a member of the q = 4 passage sees),
each file checked against the run's sha256sums.txt, with the readers of the code's output
(common.nrread(): trackers, horizon summaries with failed searches counted as missed). The
reference values (P/M_ADM, rest mass of the full solution) come from single_analysis.json of
the lead's rerun (common.RUNS["e3"]); the window means of the speed ratio and the window
medians of the horizon mass are recomputed here and checked against that file and against
s2g_compare.json of E10a (common.RUNS["e10a"]). Both runs stopped on the slot limit of their
input (t = 22 m and 14 m). Writes fig_single.{pdf,png} and fig_single_numbers.json.
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
import czstyle as cz  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

STEM = "fig_single"
HRMS_GOOD = 1e-3          # E10a: a search counts as a good surface below this residual
RUNS = (("S3", r"$\eta m=2$", cz.PAL["yellow"]), ("S2", r"$\eta m=0.25$", cz.PAL["red"]))


def wmean(t, y, a, b):
    s = (t >= a) & (t < b)
    return float(np.mean(y[s])) if np.any(s) else math.nan


def wmed(t, y, a, b):
    s = (t >= a) & (t <= b)
    return float(np.median(y[s])) if np.any(s) else math.nan


def main():
    out = C.out_dir("figures")
    nr = C.nrread()
    ref = C.load_json("e3", "single_analysis.json")
    e10a = C.load_json("e10a", "s2g_compare.json")
    vb = ref["reference"]["v_boost"]
    mrest = ref["reference"]["M_rest_full"]
    rdir = os.path.join(C.SCRATCH, C.RUNS["e3raw"])
    nums = {"runs": [C.RUNS["e3raw"], C.RUNS["e3"], C.RUNS["e10a"]], "v_boost": vb,
            "M_rest_full": mrest}
    data = {}
    for name, _, _ in RUNS:
        for rel in ("single.co_0.txt", "single.horizon_summary_0.txt", "single.z4c.user.hst"):
            C.run_file("e3raw", f"{name}/{rel}")
        rd = os.path.join(rdir, name)
        trk = nr.read_trackers(rd)[0]
        hz, nmiss = nr.read_horizons(rd)[0]
        t, v = trk["t"], trk["v"][:, 0]
        f = v / vb
        good = hz["hrms"] < HRMS_GOOD
        r = dict(t_end=float(t[-1]), x_end=float(trk["x"][-1, 0]),
                 yz_max=float(np.max(np.abs(trk["x"][:, 1:]))),
                 f_mean={f"{a}-{b}": wmean(t, f, a, b) for a, b in ((0, 5), (5, 10), (10, 20), (20, 30))},
                 f_med_10_14=wmed(t, f, 10, 14), f_max=float(f.max()),
                 searches=int(len(hz["t"]) + nmiss), missed=int(nmiss), bad_hrms=int(np.sum(~good)),
                 m_first=float(hz["mass"][0]), t_first=float(hz["t"][0]),
                 first_good=[float(hz["t"][good][0]), float(hz["mass"][good][0])],
                 m_med={f"{a}-{b}": wmed(hz["t"][good], hz["mass"][good], a, b)
                        for a, b in ((4, 6), (12, 14), (17, 22))})
        r["drift_4_6_to_12_14"] = r["m_med"]["12-14"] / r["m_med"]["4-6"] - 1
        r["m_first_rel"] = r["m_first"] / mrest - 1
        # checks against the analysis runs
        for w in ("0-5", "5-10", "10-20", "20-30"):
            a, b = r["f_mean"][w], ref[name]["f_mean"][w]
            if not (math.isnan(a) and math.isnan(b)):
                C.close(a, b, 1e-9, f"{name} f_mean {w}")
        C.close(r["t_end"], ref[name]["t_end"], 1e-12, f"{name} t_end")
        C.close(r["x_end"], ref[name]["x_end"], 1e-12, f"{name} x_end")
        C.close(r["m_first"], ref[name]["horizon"]["m_first"], 1e-12, f"{name} first mass")
        assert r["missed"] == ref[name]["horizon"]["missed"], f"{name} missed searches"
        C.close(r["f_med_10_14"], e10a["runs"][name]["f_win"]["10-14"], 1e-9, f"{name} f 10-14")
        for w in ("4-6", "12-14"):
            C.close(r["m_med"][w], e10a["runs"][name]["m_win"][w], 1e-12, f"{name} m {w}")
        C.close(r["drift_4_6_to_12_14"], e10a["S2_vs_S3"]["drift_4_6_to_12_14"][name], 1e-9,
                f"{name} drift")
        C.close(r["first_good"][0], e10a["runs"][name]["first_good"][0], 1e-12, f"{name} first good")
        nums[name] = r
        data[name] = dict(t=t, f=f, th=hz["t"], mh=hz["mass"], good=good)
    nums["drift_ratio_S2_over_S3"] = nums["S2"]["drift_4_6_to_12_14"] / nums["S3"]["drift_4_6_to_12_14"]

    cz.use_style()
    fig, axs = plt.subplots(2, 1, figsize=(3.4, 4.3), sharex=True)
    fig.subplots_adjust(left=0.2, right=0.965, bottom=0.1, top=0.985, hspace=0.08)
    a, b = axs
    for name, lab, col in RUNS:
        d = data[name]
        a.plot(d["t"], d["f"], color=col, lw=1.2, label=lab)
        a.plot([d["t"][-1]], [d["f"][-1]], "x", color=col, ms=5, mew=1.3)
        g = d["good"]
        b.plot(d["th"][g], 1e3 * (d["mh"][g] / mrest - 1), "o-", color=col, ms=2.4, lw=0.9)
        b.plot(d["th"][~g], 1e3 * (d["mh"][~g] / mrest - 1), "o", color=col, ms=3.2,
               mfc="none", mew=0.9)
        for w in ("4-6", "12-14"):
            t0, t1 = map(float, w.split("-"))
            m = nums[name]["m_med"][w]
            b.plot([t0, t1], [1e3 * (m / mrest - 1)] * 2, color="k", lw=1.6)
    a.axhline(1.0, **cz.MASK_LINE)
    a.set_ylabel(r"$v_{\rm tracker}/(P/M_{\rm ADM})$")
    a.set_ylim(-0.15, 1.1)
    a.legend(frameon=False, fontsize=7.5, loc="lower right")
    a.text(0.03, 0.87, "x: end of the run", transform=a.transAxes, fontsize=7, va="top")
    b.set_ylabel(r"$10^3\,(M_{\rm AH}/M_{\rm rest}-1)$")
    b.set_xlabel(r"$t\;[m]$")
    b.set_xlim(0, 23)
    b.set_ylim(-12, 4)
    b.text(0.97, 0.94, "open: residual of the surface above $10^{-3}$", transform=b.transAxes,
           fontsize=6.8, ha="right", va="top")
    lo = [(name, float(th), float(1e3 * (m / mrest - 1))) for name, _, _ in RUNS
          for th, m in zip(data[name]["th"], data[name]["mh"]) if 1e3 * (m / mrest - 1) < -12]
    nums["off_scale"] = lo
    if lo:
        tl = sorted(set(round(x[1], 3) for x in lo))
        b.annotate("off scale: " + ", ".join(f"$t={x:g}$" for x in tl) + f" at {min(x[2] for x in lo):.0f}",
                   xy=(tl[0], -12), xytext=(tl[0] + 2.0, -10.8), fontsize=6.8, va="center",
                   arrowprops=dict(arrowstyle="->", lw=0.8, color="k"))
    cz.save(fig, os.path.join(out, STEM))
    C.write_numbers(out, STEM, nums)
    C.report_checks(STEM)


if __name__ == "__main__":
    main()
