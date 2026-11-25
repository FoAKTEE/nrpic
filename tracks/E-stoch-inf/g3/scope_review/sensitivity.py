"""Scope review of G3 (items 1, 2 and 5): what size of error the comparison of SCOPE 4d.3 can see.

Inputs: the per-box scatter of F_pm(nu) and of the skewness from `box_stats.py` (Gaussian two-point formula
with the record's spectrum, run E-20261125-131002-ceefa2f), the one-patch reference of the 128 band
(`../../langevin/results/ref_inflection_n32.json`, run E-20261125-115707-b845282: skewness and its standard
error at 2e5 realisations), and the expected variance of its lattice variant (`ref_bins.py`, run
E-20261125-130854-ef74ef8). For S seeds and n_ref reference realisations (direct sampling) it gives the
relative standard errors of F(nu) on both sides, the combined three-standard-error threshold on
r(nu) = F_NR/F_ref - 1, and what that threshold means as
  - an amplitude (sigma) error:            dF/F = (nu phi/Q) dsigma/sigma,
  - a skewness difference (Edgeworth):     dF/F = (He2(nu)/6) (phi/Q) dS,
  - an excess-kurtosis difference:         dF/F = (He3(nu)/24) (phi/Q) dK,
and the shift of F_ref that the bin artefact of the lattice variant produces (variance ratio from ref_bins).
Also: the direct comparison of the skewness (combined standard error), and the seed count beyond which the
reference dominates the error (NR error a third of the reference's).

Usage: sensitivity.py OUTDIR --box <box_stats.json> --ref <ref_inflection_n32.json> --bins <ref_bins.json>
       [--seeds 256] [--nref 4e6]
Writes OUTDIR/sensitivity.json and OUTDIR/fig_sensitivity.{pdf,png}.
"""
import argparse
import json
import os
import sys

import numpy as np
from scipy.stats import norm

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python", "nrpic"))
import figstyle as fs  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--box", required=True)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--bins", required=True)
    ap.add_argument("--seeds", type=int, default=256)
    ap.add_argument("--nref", type=float, default=4e6)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    box = json.load(open(a.box))
    ref = json.load(open(a.ref))
    bins = json.load(open(a.bins))
    S, nref = a.seeds, a.nref
    lat = ref["s0.01_lattice"]["Ne"]
    cont = ref["s0.01"]["Ne"]
    out = dict(seeds=S, nref=nref, inputs=dict(box=a.box, ref=a.ref, bins=a.bins), nu={})
    vr = bins["bands"]["32"]["V_variant_over_lattice"]
    for nu in (3.0, 4.0):
        q, ph = norm.sf(nu), norm.pdf(nu)
        g = ph / q
        rel_box = box["neff_ensemble"][f"{nu:g}"]["rel_sd"]
        se_nr = rel_box / np.sqrt(S)
        se_ref = np.sqrt((1 - q) / (q * nref))
        comb = np.hypot(se_nr, se_ref)
        thr = 3 * comb
        he2, he3 = nu ** 2 - 1, nu ** 3 - 3 * nu
        rec = dict(Q=q, rel_sd_per_box=rel_box, rel_se_nr=se_nr, rel_se_ref_direct=se_ref,
                   rel_se_combined=comb, threshold_3se=thr,
                   dlnF_dlnsigma=nu * g, dlnF_dskew=he2 / 6 * g, dlnF_dexkurt=he3 / 24 * g,
                   sigma_error_seen=thr / (nu * g), skew_diff_seen=thr / (he2 / 6 * g),
                   exkurt_diff_seen=thr / (he3 / 24 * g),
                   seeds_where_ref_dominates=float((rel_box / (se_ref / 3)) ** 2),
                   edgeworth_excess_from_ref_skew_lattice=he2 / 6 * g * lat["skew"],
                   edgeworth_excess_from_ref_skew_continuum=he2 / 6 * g * cont["skew"],
                   shift_of_Fref_from_bin_artefact=float(norm.sf(nu / np.sqrt(vr)) / q - 1),
                   shift_in_combined_se=float((norm.sf(nu / np.sqrt(vr)) / q - 1) / comb))
        out["nu"][f"{nu:g}"] = rec
    se_sk_nr = box["neff_ensemble"]["skew_se_gauss"] / np.sqrt(S)
    se_sk_ref = lat["se_skew"] * np.sqrt(ref["s0.01_lattice"]["n"] / nref)
    out["skewness_direct"] = dict(se_nr=se_sk_nr, se_ref=se_sk_ref, combined=float(np.hypot(se_sk_nr, se_sk_ref)),
                                  threshold_3se=float(3 * np.hypot(se_sk_nr, se_sk_ref)),
                                  ref_skew_lattice=lat["skew"], ref_skew_continuum=cont["skew"],
                                  box_Rnr_implied_skew=box["pair"]["total"]["implied_skew"])
    with open(os.path.join(a.out, "sensitivity.json"), "w") as fp:
        json.dump(out, fp, indent=1)
    print(json.dumps(out, indent=1))
    # figure: relative s.e. of F(nu) against the number of seeds, with the reference floor and the size of
    # three effects on F_ref / F_NR
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    Ss = np.logspace(0, 3.5, 100)
    for j, nu in enumerate(("3", "4")):
        ax = axes[j]
        r = out["nu"][nu]
        ax.loglog(Ss, r["rel_sd_per_box"] / np.sqrt(Ss), color=fs.SERIES[0], label="NR, per seed count")
        ax.axhline(r["rel_se_ref_direct"], color=fs.SERIES[1], ls="--",
                   label=f"reference, {nref:.0e} direct")
        ax.loglog(Ss, 3 * np.hypot(r["rel_sd_per_box"] / np.sqrt(Ss), r["rel_se_ref_direct"]), color="k",
                  lw=1.0, label="3 combined s.e.")
        ax.axvline(S, color="grey", lw=0.8)
        eff = [(abs(r["shift_of_Fref_from_bin_artefact"]), "ref. top-bin artefact"),
               (r["dlnF_dlnsigma"] * 0.01, r"$\delta\sigma/\sigma=1\%$"),
               (r["edgeworth_excess_from_ref_skew_lattice"], r"all $\delta N$ skewness")]
        for k, (v, lab) in enumerate(eff):
            ax.axhline(v, color=fs.SERIES[2 + k], lw=1.2, ls=":", label=lab)
        ax.set_xlabel("seeds $S$")
        ax.set_ylabel(fr"relative error of $F_+({nu})$")
        ax.set_ylim(1e-3, 1.0)
        ax.legend(fontsize=6, frameon=False, loc="lower left")
        ax.set_title(fr"$\nu={nu}$", fontsize=9)
    fig.tight_layout()
    fs.save(fig, os.path.join(a.out, "fig_sensitivity"))


if __name__ == "__main__":
    main()
