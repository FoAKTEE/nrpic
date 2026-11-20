"""Figure: secondary infall onto a seed computed with particles in AthenaK's Newtonian mode.

Reads the analysis run nm_ana of the three Newtonian-mode runs nm128c (cell 1.06 M),
nm64c (2.125 M), both to a/a_i = 4, and nm128Lc (2.75 M, larger box) to a/a_i = 8
(nm_growth.txt: turnaround mass and dress against time with the shell references matched
to the measured mesh kernel; nm_analysis.json: deviations, profiles in 0.1 dex bins), and
the self-similar profile of run selfsim. The bins are those of
secondary_infall/nm_analyze.py (line 37, LEDGES = geomspace(0.5, 256, 28)); the run's
profiles and the references are rho over the background density rho_b(t).
Panel (a): turnaround mass and dress against a/a_i, runs (markers) and matched shells
(lines), with the self-similar asymptotes (dashed). Panel (b): run over matched shells minus
one. Panel (c): density profiles against lambda = r / r_ta at a/a_i = 4 and 8, matched shells,
the self-similar solution and the power law lambda^(-9/4). Numbers to fig_newton_numbers.json.
"""
import json
import os
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

STEM = "fig_newton"
LEDGES = np.geomspace(0.5, 256.0, 28)            # nm_analyze.py:37
C_TA = (4.0 / (3.0 * np.pi)) ** (2.0 / 3.0)      # asymptotic (M_ta - M) / (M a/a_i)
SS_DRESS = 2.0255 ** (-2.0 / 3.0)                # self-similar dress / M_ta (nm_analyze.py:36)
RUNS = (("N128c", "nm128c", cz.PAL["red"], "o"), ("N64c", "nm64c", cz.PAL["yellow"], "s"),
        ("N128Lc", "nm128Lc", cz.PAL["blue"], "^"))


def read_growth(path):
    blocks, cur = {}, None
    for line in open(path):
        if line.startswith("# ") and ":" in line and "t_code" not in line:
            cur = line[2:].split(":")[0].strip()
            blocks[cur] = []
        elif line.strip() and not line.startswith("#"):
            blocks[cur].append([float(x) for x in line.split()])
    return {k: np.array(v) for k, v in blocks.items()}


def main():
    out = C.out_dir("figures")
    g = read_growth(C.run_file("nm_ana", "nm_growth.txt"))
    ana = C.load_json("nm_ana", "nm_analysis.json")
    ss = np.load(C.run_file("selfsim", "selfsimilar_profile.npz"))
    for lab, key, _, _ in RUNS:                    # the analysis read the runs named in common.py
        if os.path.basename(ana[lab]["run"].rstrip("/")) != C.RUNS[key]:
            raise SystemExit(f"{lab}: analysis read {ana[lab]['run']}, not {C.RUNS[key]}")
    rc = np.sqrt(LEDGES[1:] * LEDGES[:-1])
    cz.use_style()
    fig, axs = plt.subplots(1, 3, figsize=(7.0, 2.5))
    fig.subplots_adjust(left=0.085, right=0.975, bottom=0.18, top=0.96, wspace=0.45)
    a, b, c = axs
    nums = {"C_TA": C_TA, "selfsim_dress_over_mta": SS_DRESS, "runs": {}}
    for lab, key, col, mk in RUNS:
        d = g[lab]
        av, mta, dr, mk_ta, mk_dr = d[:, 1], d[:, 2], d[:, 3], d[:, 4], d[:, 5]
        a.plot(av[::2], mta[::2], mk, ms=2.6, mfc="none", mec=col, mew=0.8)
        k = dr > 0.02
        a.plot(av[k][::2], dr[k][::2], mk, ms=2.6, mfc=col, mec=col, mew=0.0)
        a.plot(av, mk_ta, color=col, lw=0.9)
        a.plot(av[k], mk_dr[k], color=col, lw=0.9)
        kk = av >= 1.2
        b.plot(av[kk], 100 * (mta[kk] / mk_ta[kk] - 1), mk, ms=2.4, mfc="none", mec=col, mew=0.7)
        kd = kk & (mk_dr > 0.02)
        b.plot(av[kd], 100 * (dr[kd] / mk_dr[kd] - 1), mk, ms=2.4, mfc=col, mec=col, mew=0.0)
        A = ana[lab]
        nums["runs"][lab] = dict(run=C.RUNS[key], dx=A["dx"], a_end=A["a_end"], growth=A["growth"],
                                 vs_kernel=A["vs_kernel"], vs_plummer=A["vs_plummer"],
                                 vs_point=A["vs_point"], dress_over_mta_end=A["dress_over_mta_end"],
                                 mta_over_a_end=A["mta_over_a_end"],
                                 dlnMdress_dlna_end=A["dlnMdress_dlna_end"],
                                 clump_com_max_over_dx=A["clump"]["com_max_over_dx"],
                                 n_alive_end=A["n_alive_end"], n_total=A["n_total"],
                                 profiles=[{k_: p[k_] for k_ in ("a", "r_sp90", "r_sp99",
                                            "ref_kernel_r_sp90", "ref_kernel_r_sp99",
                                            "r_ta_selfsim_def", "selfsim_ratio_0p1_0p35",
                                            "selfsim_lambda")} |
                                           {"ratio_kernel": {k_: p["ratio_kernel_4dx_rta"][k_] for k_ in
                                                             ("max_dev", "caustic_r", "max_dev_excl_caustic",
                                                              "rms_dev_excl_caustic")}}
                                           for p in A["profiles"]])
    aa = np.geomspace(1.0, 8.5, 60)
    a.plot(aa, 1 + C_TA * aa, **cz.GUIDE, label="self-similar rates")
    a.plot(aa, SS_DRESS * (1 + C_TA * aa), color="k", lw=1.2, ls="--")
    a.plot([], [], "o", ms=2.6, mfc="none", mec="k", mew=0.8, label="turned around")
    a.plot([], [], "o", ms=2.6, mfc="k", mec="k", label="dress")
    a.plot([], [], color="k", lw=0.9, label="matched shells")
    a.set_xscale("log")
    a.set_yscale("log")
    a.set_xlim(1.0, 8.5)
    a.set_ylim(0.02, 12)
    a.set_xticks([1, 2, 4, 8])
    a.set_xticklabels(["1", "2", "4", "8"])
    a.set_xlabel(r"$a/a_i$")
    a.set_ylabel(r"mass $[M]$")
    a.xaxis.set_minor_formatter(NullFormatter())
    a.legend(frameon=False, loc="lower right", fontsize=6.5, handlelength=1.4)
    a.text(0.05, 0.92, "(a)", transform=a.transAxes)

    b.axhline(0, color="k", lw=0.8, ls="--")
    b.set_xscale("log")
    b.set_xlim(1.15, 8.5)
    b.set_xticks([2, 4, 8])
    b.set_xticklabels(["2", "4", "8"])
    b.set_ylim(-4, 4)
    b.set_xlabel(r"$a/a_i$")
    b.xaxis.set_minor_formatter(NullFormatter())
    b.set_ylabel(r"run/shells $-\,1$ [per cent]")
    for lab, key, col, mk in RUNS:
        b.plot([], [], mk, ms=2.6, mfc="none", mec=col, mew=0.8,
               label=rf"$\Delta x$ = {ana[lab]['dx']:.3g}$\,M$")
    b.legend(frameon=False, loc="lower right", fontsize=6.5, handlelength=1.0)
    b.text(0.05, 0.9, "(b)", transform=b.transAxes)

    c.plot(ss["rc"], ss["rho"], color="k", lw=1.3, label="self-similar")
    ll = np.geomspace(3e-3, 0.3, 20)
    c.plot(ll, 3.0 * ll ** -2.25, color="grey", lw=1.0, ls="--", label=r"$\propto\lambda^{-9/4}$")
    for lab, aw, col in (("N128c", 4.0, cz.PAL["red"]), ("N128Lc", 8.0, cz.PAL["blue"])):
        p = min(ana[lab]["profiles"], key=lambda q: abs(q["a"] - aw))
        rho, ref = np.array(p["rho"]), np.array(p["ref_kernel"])
        lam = rc / p["r_ta_selfsim_def"]
        ok, okr = rho > 0, ref > 0
        c.plot(lam[ok], rho[ok], "o", ms=2.4, mfc="none", mec=col, mew=0.8,
               label=rf"$a/a_i$ = {aw:g}")
        c.plot(lam[okr], ref[okr], color=col, lw=0.9)
        c.axvline(4 * ana[lab]["dx"] / p["r_ta_selfsim_def"], color=col, lw=0.8, ls=":")
    c.set_xscale("log")
    c.set_yscale("log")
    c.set_xlim(8e-3, 2)
    c.set_ylim(0.5, 3e4)
    c.set_xlabel(r"$\lambda = r/r_{\rm ta}$")
    c.set_ylabel(r"$\rho/\rho_b$")
    c.legend(frameon=False, loc="upper right", fontsize=6.5, handlelength=1.4)
    c.text(0.05, 0.08, "(c)", transform=c.transAxes)
    cz.save(fig, os.path.join(out, STEM))
    with open(os.path.join(out, STEM + "_numbers.json"), "w") as f:
        json.dump(nums, f, indent=1)
    for lab, d in nums["runs"].items():
        gr = {x["a"]: (round(x["mta"], 4), round(x["dress"], 4)) for x in d["growth"]}
        print(f"{STEM}: {lab} dx {d['dx']}: M_ta, dress {gr}; max |M_ta/kernel - 1| after 1.5: "
              f"{d['vs_kernel']['mta_max_rel']:.2e}; dress/M_ta at end {d['dress_over_mta_end']:.3f}")
    C.report_checks(STEM)


if __name__ == "__main__":
    main()
