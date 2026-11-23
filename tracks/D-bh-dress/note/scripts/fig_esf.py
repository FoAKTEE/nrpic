"""Figure: first run with dust that reaches the black hole (ES-F), growth against the flux.

Reads the raw outputs of the ES-F card run (finder summary esf.horizon_summary_0.txt, record
of removed particles esf.removed.bin), the data run (energy_by_tag.npy: E_K = (1-2M/R0)^(1/2)
per particle, fixed by the initial data; esf_growth.csv: exact LTB mass m(R0) at the proper
time tau_H(R0) its shell reaches R = 2m), the vacuum control V-1 (v1.horizon_summary_0.txt,
same mesh, gauge and faces), and the bin medians of criterion (iii) from esf_criteria.json.
The flux tools of the track (flux_tools/fluxio.py) are used as readers only.

Panel (a): horizon mass M_AH(t); M_AH(0) + F_rem(t) + [M_ctrl(t) - M_ctrl(0)], with F_rem the
sum of m E_K over the particles removed at the horizon by time t; the control alone.
Panel (b): closure residual dM_AH - F_rem - dM_ctrl and the raw dM_AH - F_rem.
Panel (c): M_AH at each removal over the exact M_LTB(tau_rem), minus one, against the proper
time of the removed particle (a random tenth shown), with the bin medians of (iii).
Numbers into fig_esf_numbers.json (read by ledger.py).
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
import czstyle as cz  # noqa: E402
sys.path.insert(0, os.path.join(C.TRACK, "flux_tools"))
import fluxio  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

STEM = "fig_esf"


def main():
    out = C.out_dir("figures")
    hor = fluxio.read_horizon(C.run_file("esf", "esf.horizon_summary_0.txt"))
    rem = fluxio.read_removed(C.run_file("esf", "esf.removed.bin"))
    ctrl = fluxio.read_horizon(C.run_file("v1", "v1.horizon_summary_0.txt"))
    EK = np.load(C.run_file("esf_data", "energy_by_tag.npy"))
    grow = np.loadtxt(C.run_file("esf_data", "esf_growth.csv"), delimiter=",", skiprows=1)
    crit = C.load_json("esf_crit", "esf_criteria.json")
    ana = C.load_json("esf_ana", "esf_analysis.json")
    g_tau, g_m = grow[:, 2], grow[:, 1]
    o = np.argsort(g_tau)
    g_tau, g_m = g_tau[o], g_m[o]

    th, Mh = hor["time"], hor["mass"]
    tc, Mc = ctrl["time"], ctrl["mass"]
    dMc = np.interp(th, tc, Mc) - Mc[0]
    hz = np.isin(rem["reason"], (2, 3))
    tr, tag, tau, m = rem["time"][hz], rem["tag"][hz], rem["tau"][hz], rem["m"][hz]
    order = np.argsort(tr, kind="stable")
    cumF = np.cumsum((m * EK[tag])[order])
    tr_sorted = tr[order]
    # removed energy by each finder time (records at or before t)
    F_at = np.concatenate([[0.0], cumF])[np.searchsorted(tr_sorted, th, side="right")]
    dM = Mh - Mh[0]
    resid_raw = dM - F_at
    resid = dM - F_at - dMc
    late = th >= 20.0
    # per removal: first finder sample at or after the removal over the exact mass
    k = np.clip(np.searchsorted(th, tr, side="left"), 0, th.size - 1)
    ok = np.searchsorted(th, tr, side="left") < th.size
    is_dust = tag >= 140
    ratio = Mh[k] / np.interp(tau, g_tau, g_m, left=1.0) - 1.0
    sel = ok & is_dust & (tau <= 250.0)
    bins = [b for b in crit["iii"]["dust"]["bins"] if b["counted"]]

    nums = {"t_end": float(th[-1]), "M_AH_0": float(Mh[0]),
            "M_AH_at": {str(t): float(np.interp(t, th, Mh)) for t in (50.0, 100.0, 150.0, float(th[-1]))},
            "dM_end": float(dM[-1]), "F_rem_end": float(F_at[-1]), "dMctrl_end": float(dMc[-1]),
            "closure_raw_end": float(resid_raw[-1]), "closure_ctrl_end": float(resid[-1]),
            "closure_ctrl_max_abs_after20": float(np.max(np.abs(resid[late]))),
            "n_removed": int(hz.sum()), "n_removed_dust": int(is_dust.sum()),
            "t_first_removal": float(tr.min()),
            "iii_n": int(sel.sum()), "iii_overall_median": float(np.median(ratio[sel])),
            "iii_bin_median_range": [min(b["median"] for b in bins), max(b["median"] for b in bins)],
            "iii_n_bins": len(bins),
            "check_against_esf_criteria": {
                "D1_raw": crit["D1"]["raw"], "D1_ctrl": crit["D1"]["ctrl_subtracted"],
                "iii_overall_median": crit["iii"]["dust"]["overall_median"],
                "F_rem_end_esf_analysis": ana["bracket_energy_by_tag"]["F_rem_end"]},
            "card_hours": json.load(open(os.path.join(C.TRACK, "runs", C.RUNS["esf"],
                                                       "manifest.json")))["resources"]["gpu_hours"]}

    cz.use_style()
    fig, (a, b, c) = plt.subplots(1, 3, figsize=(7.0, 2.6))
    fig.subplots_adjust(left=0.085, right=0.985, bottom=0.17, top=0.95, wspace=0.45)
    a.plot(th, Mh, color=cz.PAL["blue"], lw=1.5, label=r"$M_{\rm AH}$")
    a.plot(th, Mh[0] + F_at + dMc, color=cz.PAL["red"], lw=1.0, ls="--",
           label=r"$M_{\rm AH}(0)+F_{\rm rem}+\Delta M_{\rm ctrl}$")
    a.plot(tc, Mc, color="0.5", lw=1.0, label="vacuum control")
    a.set_xlabel(r"$t/M$"); a.set_ylabel(r"$M_{\rm AH}/M$")
    a.legend(loc="upper left", fontsize=6.5, frameon=False)
    a.text(0.95, 0.05, "(a)", transform=a.transAxes, ha="right")
    b.plot(th, 1e3 * resid_raw, color="0.5", lw=1.0, label="raw")
    b.plot(th, 1e3 * resid, color=cz.PAL["blue"], lw=1.2, label="control subtracted")
    b.axhline(0, color="k", lw=0.8)
    b.set_ylim(-6, 12)
    b.set_xlabel(r"$t/M$"); b.set_ylabel(r"$10^3\,(\Delta M_{\rm AH}-F_{\rm rem})/M$")
    b.legend(loc="center right", bbox_to_anchor=(1.0, 0.64), fontsize=6.5, frameon=False)
    b.text(0.95, 0.05, "(b)", transform=b.transAxes, ha="right")
    rng = np.random.default_rng(1)
    show = np.flatnonzero(sel)
    show = show[rng.random(show.size) < 0.1]
    c.plot(tau[show], 1e2 * ratio[show], ".", ms=1.0, color=cz.PAL["blue"], alpha=0.4)
    c.plot([0.5 * (x["lo"] + x["hi"]) for x in bins], [1e2 * x["median"] for x in bins], "o",
           ms=3.5, color="k", label="bin medians")
    c.axhspan(-1.0, 1.0, color="0.85", zorder=0)
    c.axhline(0, color="k", lw=0.8)
    c.set_ylim(-1.5, 1.5)
    c.set_xlabel(r"$\tau_{\rm rem}/M$"); c.set_ylabel(r"$10^2\,(M_{\rm AH}/M_{\rm LTB}-1)$")
    c.legend(loc="lower right", fontsize=6.5, frameon=False)
    c.text(0.05, 0.05, "(c)", transform=c.transAxes)
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(out, f"{STEM}.{ext}"), dpi=200)
    with open(os.path.join(out, f"{STEM}_numbers.json"), "w") as f:
        json.dump(nums, f, indent=1)
    print(json.dumps({k: v for k, v in nums.items()}, indent=1))
    C.report_checks(STEM)


if __name__ == "__main__":
    main()
