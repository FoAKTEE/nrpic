"""Figure: Newtonian-mode infall run to a/a_i = 16 (Q16), the G1 evidence for D-pre-3.

Reads the analysis run q16_ana of the Q16 run (threaded processor build, dx = 4.625 M,
520048 particles; nm_growth.txt: turnaround mass and dress against time with the matched
shell references hybrid_cc and kernel_cc; nm_analysis.json: profiles in 0.1-dex bins,
LEDGES_LATE = geomspace(0.5, 2048, 37) of secondary_infall/nm_late.py line 19; nm_late.txt:
the comparison with the self-similar profile at the last snapshot), the particle census
q16_lost (nm_lost.json) and the self-similar profile of run selfsim.
Panel (a): turnaround mass and dress against a/a_i, run (markers), matched shells (lines),
self-similar rates (dashed). Panel (b): run over matched shells minus one, both references.
Panel (c): density over the background against lambda = r/r_ta at a/a_i = 15.96: run, matched
shells (hybrid_cc), the self-similar solution and lambda^(-9/4); dotted: four cells.
Numbers into fig_q16_numbers.json (read by ledger.py).
"""
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common as C  # noqa: E402
import czstyle as cz  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import NullFormatter  # noqa: E402

STEM = "fig_q16"
LEDGES = np.geomspace(0.5, 2048.0, 37)          # secondary_infall/nm_late.py:19
C_TA = (4.0 / (3.0 * np.pi)) ** (2.0 / 3.0)
SS_DRESS = 2.0255 ** (-2.0 / 3.0)               # as fig_newton.py


def read_growth(path):
    rows = [[float(x) for x in ln.split()] for ln in open(path)
            if ln.strip() and not ln.startswith("#")]
    return np.array(rows)


def parse_late(path):
    """Rows of nm_late.txt: the main line of each a/a_i and its 'ratios run/ss' line."""
    out, cur = {}, None
    for ln in open(path):
        if ln.startswith("Q16 "):
            f = ln.split()
            cur = float(f[1])
            vs = ln.split("|")[1].split()
            out[cur] = dict(a=cur, M_ta=float(f[2]), dress=float(f[3]),
                            dress_over_mta=float(f[4]), mta_over_a=float(f[5]),
                            lam_min=float(vs[0]), nbins=int(vs[1]),
                            max_dev=float(vs[2]), rms_dev=float(vs[3]))
            if vs[1] != "0":
                out[cur].update(fit_slope=float(vs[4]), fit_slope_ss=float(vs[5].strip("()")),
                                mean_local_slope=float(vs[6]), mean_local_slope_ss=float(vs[7].strip("()")))
            m = re.search(r"hybrid_cc: ([+-][0-9.]+) ([+-][0-9.]+)", ln)
            out[cur]["hybrid_rel"] = [float(m.group(1)), float(m.group(2))]
            m = re.search(r"kernel_cc: ([+-][0-9.]+) ([+-][0-9.]+)", ln)
            out[cur]["kernel_rel"] = [float(m.group(1)), float(m.group(2))]
        elif cur is not None and ln.strip().startswith("ratios run/ss:") and "ratios" not in out[cur]:
            out[cur]["ratios"] = [[float(v) for v in x.split(":")] for x in ln.split(":", 1)[1].split()]
        elif cur is not None and "flag-free" in ln:
            m = re.search(r"M_ta\(v\) ([0-9.]+) \(r_ta measured ([0-9.]+)", ln)
            out[cur]["M_ta_flagfree"] = float(m.group(1))
            out[cur]["r_ta_measured"] = float(m.group(2))
    return out


def main():
    out = C.out_dir("figures")
    g = read_growth(C.run_file("q16_ana", "nm_growth.txt"))
    ana = C.load_json("q16_ana", "nm_analysis.json")["Q16"]
    late = parse_late(C.run_file("q16_ana", "nm_late.txt"))
    lost = C.load_json("q16_lost", "nm_lost.json")
    ss = np.load(C.run_file("selfsim", "selfsimilar_profile.npz"))
    if os.path.basename(ana["run"].rstrip("/")) != C.RUNS["q16"]:
        raise SystemExit(f"analysis read {ana['run']}, not {C.RUNS['q16']}")
    av, mta, dr = g[:, 1], g[:, 2], g[:, 3]
    k_ta, k_dr, h_ta, h_dr = g[:, 4], g[:, 5], g[:, 6], g[:, 7]
    a_last = max(late)
    L = late[a_last]
    nums = {"run": C.RUNS["q16"], "dx": ana["dx"], "a_end": ana["a_end"],
            "n_total": ana["n_total"], "n_alive_end": ana["n_alive_end"],
            "late": {f"{k:g}": v for k, v in late.items()},
            "lost": {k: lost[k] for k in lost if not isinstance(lost[k], (list, dict))}}
    k3 = (av >= 3.0 - 1e-9) & (av <= 12.0 + 1e-9) & (h_dr > 0.02)
    nums["hybrid_maxrel_a3_12"] = {"M_ta": float(np.max(np.abs(mta[k3] / h_ta[k3] - 1))),
                                   "dress": float(np.max(np.abs(dr[k3] / h_dr[k3] - 1)))}
    nums["kernel_maxrel_a3_12"] = {"M_ta": float(np.max(np.abs(mta[k3] / k_ta[k3] - 1))),
                                   "dress": float(np.max(np.abs(dr[k3] / k_dr[k3] - 1)))}

    cz.use_style()
    fig, (a, b, c) = plt.subplots(1, 3, figsize=(7.0, 2.5))
    fig.subplots_adjust(left=0.085, right=0.975, bottom=0.18, top=0.96, wspace=0.45)
    col = cz.PAL["blue"]
    a.plot(av[::3], mta[::3], "o", ms=2.6, mfc="none", mec=col, mew=0.8, label="turned around")
    k = dr > 0.02
    a.plot(av[k][::3], dr[k][::3], "o", ms=2.6, mfc=col, mec=col, mew=0.0, label="dress")
    a.plot(av, h_ta, color="k", lw=0.9, label="matched shells")
    a.plot(av[k], h_dr[k], color="k", lw=0.9)
    aa = np.geomspace(1.0, 17.0, 60)
    a.plot(aa, 1 + C_TA * aa, **cz.GUIDE, label="self-similar rates")
    a.plot(aa, SS_DRESS * (1 + C_TA * aa), color="k", lw=1.2, ls="--")
    a.set_xscale("log"); a.set_yscale("log")
    a.set_xlim(1.0, 17.0); a.set_ylim(0.02, 15)
    a.set_xticks([1, 2, 4, 8, 16]); a.set_xticklabels(["1", "2", "4", "8", "16"])
    a.xaxis.set_minor_formatter(NullFormatter())
    a.set_xlabel(r"$a/a_i$"); a.set_ylabel(r"mass $[M]$")
    a.legend(frameon=False, loc="lower right", fontsize=6.5, handlelength=1.4)
    a.text(0.05, 0.92, "(a)", transform=a.transAxes)

    kk = av >= 1.5
    for ref_ta, ref_dr, c_, lab in ((h_ta, h_dr, cz.PAL["blue"], "cell-centre force, hybrid"),
                                    (k_ta, k_dr, cz.PAL["red"], "cell-centre force, kernel")):
        b.plot(av[kk], 100 * (mta[kk] / ref_ta[kk] - 1), "o", ms=2.2, mfc="none", mec=c_, mew=0.7)
        kd = kk & (ref_dr > 0.02)
        b.plot(av[kd], 100 * (dr[kd] / ref_dr[kd] - 1), "o", ms=2.2, mfc=c_, mec=c_, mew=0.0,
               label=lab)
    b.axhline(0, color="k", lw=0.8, ls="--")
    b.set_xscale("log"); b.set_xlim(1.5, 17.0)
    b.set_xticks([2, 4, 8, 16]); b.set_xticklabels(["2", "4", "8", "16"])
    b.xaxis.set_minor_formatter(NullFormatter())
    b.set_ylim(-3, 3)
    b.set_xlabel(r"$a/a_i$"); b.set_ylabel(r"run/shells $-\,1$ [per cent]")
    b.legend(frameon=False, loc="lower left", fontsize=6.0, handlelength=1.0)
    b.text(0.05, 0.9, "(b)", transform=b.transAxes)

    p = min(ana["profiles"], key=lambda q: abs(q["a"] - a_last))
    rc = np.sqrt(LEDGES[1:] * LEDGES[:-1])
    rho, ref = np.array(p["rho"]), np.array(p["ref_hybrid_cc"])
    lam = rc / p["r_ta_selfsim_def"]
    c.plot(ss["rc"], ss["rho"], color="k", lw=1.3, label="self-similar")
    ll = np.geomspace(3e-3, 0.3, 20)
    c.plot(ll, 3.0 * ll ** -2.25, color="grey", lw=1.0, ls="--", label=r"$\propto\lambda^{-9/4}$")
    ok, okr = rho > 0, ref > 0
    c.plot(lam[ok], rho[ok], "o", ms=2.4, mfc="none", mec=col, mew=0.8,
           label=rf"run, $a/a_i$ = {p['a']:.1f}")
    c.plot(lam[okr], ref[okr], color=col, lw=0.9, label="matched shells")
    c.axvline(4 * ana["dx"] / p["r_ta_selfsim_def"], color=col, lw=0.8, ls=":")
    c.set_xscale("log"); c.set_yscale("log")
    c.set_xlim(8e-3, 2); c.set_ylim(0.5, 3e4)
    c.set_xlabel(r"$\lambda = r/r_{\rm ta}$"); c.set_ylabel(r"$\rho/\rho_b$")
    c.legend(frameon=False, loc="upper right", fontsize=6.0, handlelength=1.4)
    c.text(0.05, 0.08, "(c)", transform=c.transAxes)
    nums["profile_last"] = dict(a=p["a"], r_ta_selfsim_def=p["r_ta_selfsim_def"],
                                r_ta_measured=p["r_ta_measured"],
                                four_dx_over_rta=4 * ana["dx"] / p["r_ta_selfsim_def"])
    cz.save(fig, os.path.join(out, STEM))
    with open(os.path.join(out, STEM + "_numbers.json"), "w") as f:
        json.dump(nums, f, indent=1)
    print(json.dumps({k: nums[k] for k in ("a_end", "n_total", "n_alive_end",
                                           "hybrid_maxrel_a3_12", "kernel_maxrel_a3_12")}, indent=1))
    print(json.dumps(L, indent=1))
    C.report_checks(STEM)


if __name__ == "__main__":
    main()
