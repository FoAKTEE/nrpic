"""Scope review of G3 (item 2): expected variance of the lattice-density variant of the one-patch reference.

The variant `s0.01_lattice` of `../../langevin/scripts/ref_spec.py` multiplies the noise covariance at
e-fold N by r_i, the ratio of lattice shell counts to the continuum shell volume in the bin
[0.05 i, 0.05 (i+1)) of ln n that holds the mode crossing at N (lattice_factor_fn, lines 64-77 of that
script). Its final variance is therefore, in expectation and to linear order,

    V_variant = integral_0^{ln NLAT} r(bin(u)) P_R(e^u k_min, N_e) du,

which this script evaluates without any Monte Carlo and compares with the lattice sum the variant is
judged against (var_lattice = sum over shells of cnt P_R / (4 pi n^3), ref_spec.py line 139). The bins are
those of ref_spec.py: the last bin runs to ln NLAT + 0.05 but the band stops at ln NLAT, so its shell
volume is counted to e^0.05 NLAT while only shells up to NLAT exist. The variant with that bin truncated at
ln NLAT is evaluated beside it ("fixed").

Re-implemented here from the text of ref_spec.py; the background and the mode functions are the track's
reference code `../../langevin/sdn/` (models.HiggsInflection, linear.ClassicalBackground, linear.PR_late),
imported read-only. Measured values to compare (ref_inflection_n32.json, run E-20261125-115707-b845282;
ref_inflection.json, run E-stoch-inf-20261115-130137-176cdd6): var/var_lattice = 0.9796 +- 0.0032 (NLAT 32),
0.9905 +- 0.0016 (NLAT 64).

Usage: ref_bins.py OUTDIR [--npts 241]
Writes OUTDIR/ref_bins.json and OUTDIR/fig_ref_bins.{pdf,png}.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LANG = os.path.normpath(os.path.join(HERE, "..", "..", "langevin"))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, LANG)
sys.path.insert(0, os.path.join(REPO, "python", "nrpic"))
from sdn import models, linear  # noqa: E402
import figstyle as fs  # noqa: E402

BIN = 0.05
MEASURED = {32: (0.9796, 0.0032, "E-20261125-115707-b845282"),
            64: (0.9905, 0.0016, "E-stoch-inf-20261115-130137-176cdd6")}


def bins_of(nlat, truncate_top):
    nn, cnt = linear.lattice_shell_counts(nlat)
    edges = np.arange(0.0, np.log(nlat) + BIN + 1e-9, BIN)
    lo, hi = np.exp(edges[:-1]), np.exp(edges[1:])
    if truncate_top:
        hi = np.minimum(hi, float(nlat))
    idx = np.clip(np.searchsorted(edges, np.log(nn), side="right") - 1, 0, len(lo) - 1)
    C = np.bincount(idx, weights=cnt, minlength=len(lo))
    vol = 4 * np.pi / 3 * (hi ** 3 - lo ** 3)
    r = np.where(vol > 0, C / np.where(vol > 0, vol, 1.0), 0.0)
    return edges, r, nn, cnt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--npts", type=int, default=241)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    # background exactly as ref_spec.py setup("inflection")
    model = models.HiggsInflection()
    phi0 = -1.2
    dpdN, _ = models.h0_fixing(model, phi0)
    N0, Nstar, Ne = 0.0, 3.0, 18.0
    bg = linear.ClassicalBackground(model, phi0, dpdN, N0=N0, Nstar=Nstar, N_extra=250.0)
    kmin = bg.aH(Nstar)
    nl_max = 64
    u = np.linspace(0.0, np.log(nl_max), a.npts)
    PR = linear.PR_late(bg, kmin * np.exp(u), Ne)
    lnPR = np.log(PR)
    out = dict(kmin=kmin, u=u.tolist(), PR_Ne=PR.tolist(), bands={})
    for nlat in (32, 64):
        uu = np.linspace(0.0, np.log(nlat), 200001)
        P = np.exp(np.interp(uu, u, lnPR))
        var_cont = float(np.trapezoid(P, uu))
        edges, r, nn, cnt = bins_of(nlat, False)
        _, rfix, _, _ = bins_of(nlat, True)
        PRn = np.exp(np.interp(np.log(nn), u, lnPR))
        var_lat = float(np.sum(cnt * PRn / (4 * np.pi * nn ** 3)))
        ib = np.clip(np.floor(uu / BIN).astype(int), 0, len(r) - 1)
        v_var = float(np.trapezoid(r[ib] * P, uu))
        v_fix = float(np.trapezoid(rfix[ib] * P, uu))
        top = len(r) - 1
        sel = ib == top
        top_share = float(np.trapezoid(np.where(sel, P, 0.0), uu) / var_lat)
        meas, se, rid = MEASURED[nlat]
        rec = dict(var_cont=var_cont, var_lattice=var_lat, lattice_over_cont=var_lat / var_cont,
                   V_variant=v_var, V_variant_over_lattice=v_var / var_lat,
                   V_fixed=v_fix, V_fixed_over_lattice=v_fix / var_lat,
                   top_bin=[float(edges[top]), float(edges[top + 1])], r_top=float(r[top]),
                   r_top_fixed=float(rfix[top]), top_bin_share_of_variance=top_share,
                   measured_var_over_lattice=meas, measured_se=se, measured_run=rid,
                   pull_variant=(meas - v_var / var_lat) / se, pull_fixed=(meas - v_fix / var_lat) / se,
                   r_bins=r.tolist(), r_bins_fixed=rfix.tolist(), edges=edges.tolist())
        out["bands"][str(nlat)] = rec
        print(nlat, {k: v for k, v in rec.items() if not isinstance(v, list)}, flush=True)
    with open(os.path.join(a.out, "ref_bins.json"), "w") as fp:
        json.dump(out, fp, indent=1)
    # figure: bin factors weighted by P_R, and the expected ratio against the measured one
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    ax = axes[0]
    for j, nlat in enumerate((32, 64)):
        rec = out["bands"][str(nlat)]
        e = np.array(rec["edges"])
        ax.step(e[:-1], rec["r_bins"], where="post", color=fs.SERIES[j], lw=1.5,
                label=fr"$|n|\leq{nlat}$, as in ref_spec.py")
        ax.step(e[:-1], rec["r_bins_fixed"], where="post", color=fs.SERIES[j], lw=1.0, ls=":",
                label=fr"$|n|\leq{nlat}$, top bin truncated")
    ax.axhline(1.0, **fs.GUIDE)
    ax.set_xlim(2.0, 4.25)
    ax.set_ylim(0.0, 1.4)
    ax.set_xlabel(r"$\ln |n|$")
    ax.set_ylabel(r"lattice / continuum factor $r_i$")
    ax.legend(fontsize=6.5, frameon=False, loc="lower left")
    ax2 = ax.twinx()
    ax2.semilogy(u, PR, color="grey", lw=1.0)
    ax2.set_ylabel(r"$P_\mathcal{R}(N_e)$ (grey)")
    ax = axes[1]
    for j, nlat in enumerate((32, 64)):
        rec = out["bands"][str(nlat)]
        ax.errorbar([j - 0.1], [rec["measured_var_over_lattice"]], yerr=[rec["measured_se"]], fmt="o",
                    color=fs.SERIES[j], label="Monte Carlo (measured)" if j == 0 else None)
        ax.plot([j + 0.1], [rec["V_variant_over_lattice"]], "s", color=fs.SERIES[j], mfc="none",
                label="expected, bins of ref_spec.py" if j == 0 else None)
        ax.plot([j + 0.1], [rec["V_fixed_over_lattice"]], "^", color=fs.SERIES[j], mfc="none",
                label="expected, top bin truncated" if j == 0 else None)
    ax.axhline(1.0, **fs.GUIDE)
    ax.set_xticks([0, 1])
    ax.set_xticklabels([r"$|n|\leq32$ (128$^3$)", r"$|n|\leq64$ (256$^3$)"])
    ax.set_xlim(-0.6, 1.6)
    ax.set_ylabel(r"variance / lattice sum")
    ax.legend(fontsize=6.5, frameon=False, loc="lower right")
    fig.tight_layout()
    fs.save(fig, os.path.join(a.out, "fig_ref_bins"))


if __name__ == "__main__":
    main()
