#!/usr/bin/env python3
"""D3 initial data: a King b = 1 model (arXiv:2009.08163; f = exp(1 - E/E0) - 1) on the
stable side of the King-family Juttner fluid onset by more than the collisionless
controls' drift, 10^5 equal-mass particles, its offline checks, and K, sigma~ of the track's
Knudsen definition.

    python3 make_d3_ic.py [--out DIR] [--y0 0.26] [--N 100000] [--seed 1]

--out defaults to $NRPIC_RUN_DIR (harness/bin/nrpic-run). Steps, all with the track's own
reference code (decision 0010: reference solutions only):
  A. the King sequence alpha_c(y0) = 1/(1 + Z_c) for y0 = 0.24 ... 0.34 (equilibria/evstatic.py);
     its distance from the Juttner-Gamma_1 onset (Z_c of run C-20261119-151502-cb831a8,
     rv_king_onset.json, J_E_N1200) and from the controls' drift (alpha_c_max_dev_from_start of
     cc1_kninf, cc2_kninf in run C-20261115-191420-8538aa4, summary.json);
  B. the particle file, table and JSON with equilibria/make_equilibria.build (stratified);
  C. equilibria/check_equilibria.check_model on that file (matching, TOV, Hamiltonian
     constraint of the table, file round trip, ECDFs, shell counts, E <= E0, sum m W/psi,
     moments of both samplers);
  D. K = 1/(rho0_c H_c) (threshold_scan/common.kn_constant, the decks' definition,
     equilibria/CONVERSION.md section 5), sigma~ = K/Kn for Kn = 10, 1, cross-checked with
     equilibria/knudsen.model_conversion (K = (Kn sigma~)_l / (l/lambda)), and the expected
     collisions per particle in 300 M at the initial rate (nu_bar of knudsen.py).
Writes d3_ic.json, checks.json, d3_geometry.json and fig_d3_model.png into DIR; with
--from SRC only the figure and the geometry (fraction inside the M/4 region), from SRC.
"""
import argparse
import json
import math
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TR = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(TR, "equilibria"))
sys.path.insert(0, os.path.join(TR, "threshold_scan"))
import common as C  # noqa: E402
import evstatic as ev  # noqa: E402
import models  # noqa: E402
import make_equilibria as me  # noqa: E402
import check_equilibria as ce  # noqa: E402
import knudsen as kn  # noqa: E402

ONSET_RUN = "C-20261119-151502-cb831a8"
DRIFT_RUN = "C-20261115-191420-8538aa4"
WAVE2_IC = "C-20261115-165832-fccee3a"


def tag_of(y0):
    return f"king_y{y0:.5f}".replace(".", "p")


def figure(src, out, res):
    """fig_d3_model.png from d3_ic.json and the particle file in src; also the fraction of
    particles inside the M/4 region of the decks' mesh (|x|_inf < 8 M) for D3 and CC2."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, os.path.join(C.WT, "python"))
    from nrpic import figstyle as fs
    fs.use_style()
    fam = models.FAMILIES["king"]
    y0 = res["y0"]
    seq = res["sequence"]
    a_onJ = res["onset_JE"]["alpha_c"]
    drift = {k: v for k, v in res["controls_drift"].items() if k != "run"}
    on = json.load(open(os.path.join(C.SCRATCH, ONSET_RUN, "rv_king_onset.json")))
    x, u, m, sp = ev.nio.read_nrp(os.path.join(src, res["stem"] + ".nrp"))
    md = ev.Equilibrium(fam, y0)
    rb = np.linalg.norm(x, axis=1)
    W = np.sqrt(1.0 + np.sum(u * u, axis=1) / md.psi(rb) ** 4)
    Ex = md.alpha(rb) * W / md.E0
    geo = {"d3": float(np.mean(np.max(np.abs(x), axis=1) < 8.0))}
    x2, _, _, _ = ev.nio.read_nrp(os.path.join(C.SCRATCH, WAVE2_IC, "king_y0p31400_stratified_N100000_s1.nrp"))
    geo["cc2"] = float(np.mean(np.max(np.abs(x2), axis=1) < 8.0))
    geo["d3_r_max"] = float(rb.max())
    print("fraction of particles in |x|_inf < 8 M:", geo, flush=True)
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.08, right=0.985, bottom=0.16, top=0.95, wspace=0.3)
    yy = np.array([q["y0"] for q in seq])
    aa = np.array([q["alpha_c"] for q in seq])
    ax = axs[0]
    ax.plot(yy, aa, "-", color="k", lw=1.2, label=r"King $b=1$: $\alpha_c(y_0)$")
    ax.axhline(a_onJ, **fs.GUIDE, label=r"Juttner $\Gamma_1$ fluid onset")
    ax.axvline(on["eps_max_y0"], **fs.MASK_LINE)
    fs.band(ax, yy, a_onJ, a_onJ + max(drift.values()), fs.PAL["yellow"], alpha=0.3)
    for lab, y, c in (("CC2", 0.314, fs.PAL["blue"]), ("CC1", 0.334032, fs.PAL["red"]),
                      ("D3", y0, fs.PAL["green"])):
        q = next(q for q in seq if q["y0"] == y)
        ax.plot([y], [q["alpha_c"]], "o", color=c, ms=5, label=lab)
    ax.text(0.03, 0.06, "shaded: onset + largest control drift (0.033)", transform=ax.transAxes, fontsize=7)
    ax.set_xlabel(r"$y_0$")
    ax.set_ylabel(r"central lapse $\alpha_c$ of the equilibrium")
    ax.legend(fontsize=7, loc="upper right")
    ax = axs[1]
    xs, pdf, cdf = ce.energy_cdf(md)
    ax.hist(Ex, bins=np.linspace(0.7, 1.0, 61), density=True, histtype="step", color=fs.PAL["green"],
            lw=1.2, label=f"file, N = {len(m)}")
    ax.plot(xs, pdf, **fs.GUIDE, label="model")
    ax.set_xlim(0.7, 1.005)
    ax.set_xlabel(r"$E/E_0$ (Killing energy at $t=0$)")
    ax.set_ylabel("probability density")
    ax.legend(fontsize=7, loc="upper left", bbox_to_anchor=(0.0, 0.42))
    ax2 = ax.inset_axes([0.22, 0.56, 0.36, 0.39])
    rs_ = np.sort(rb)
    ax2.plot(rs_, np.arange(1, len(rs_) + 1) / len(rs_), color=fs.PAL["green"], lw=1.0)
    rr = np.linspace(0, rs_[-1], 300)
    ax2.plot(rr, md.enclosed_fraction_areal(md.areal_of(rr)), color="k", lw=0.8, ls="--")
    ax2.axvline(8.0, **fs.MASK_LINE)
    ax2.set_xlabel(r"$\bar r/M$", fontsize=6)
    ax2.set_ylabel("mass fraction", fontsize=6)
    ax2.tick_params(labelsize=6)
    fig.savefig(os.path.join(out, "fig_d3_model.png"), dpi=200)
    plt.close(fig)
    with open(os.path.join(out, "d3_geometry.json"), "w") as f:
        json.dump(dict(source=src, fraction_inside_8M=geo), f, indent=1)
    return geo


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--y0", type=float, default=0.26)
    ap.add_argument("--N", type=int, default=100000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--from", dest="src", help="figure and geometry only, from this earlier run directory")
    a = ap.parse_args()
    if not a.out:
        sys.exit("give --out or run through nrpic-run")
    os.makedirs(a.out, exist_ok=True)
    if a.src:
        figure(a.src, a.out, json.load(open(os.path.join(a.src, "d3_ic.json"))))
        return 0
    fam = models.FAMILIES["king"]
    res = dict(y0=a.y0, N=a.N, seed=a.seed)

    # A. sequence, onset, drift
    on = json.load(open(os.path.join(C.SCRATCH, ONSET_RUN, "rv_king_onset.json")))
    onJ = on["onset"]["J_E_N1200"]
    onF = on["onset"]["F21_N1200"]
    a_onJ = 1.0 / (1.0 + onJ["Z0"])
    dr = json.load(open(os.path.join(C.SCRATCH, DRIFT_RUN, "summary.json")))
    drift = {k: dr[k]["alpha_c_max_dev_from_start"] for k in ("cc1_kninf", "cc2_kninf")}
    ys = np.round(np.arange(0.24, 0.3401, 0.01), 4).tolist()
    ys = sorted(set(ys + [a.y0, 0.314, 0.334032]))
    seq = []
    for y in ys:
        s = ev.Equilibrium(fam, y).summary()
        seq.append(dict(y0=y, alpha_c=s["alpha_c"], Zc=s["Zc_infinity"], Eb=s["Eb_over_M0"],
                        R=s["R_areal"], rbar_s=s["rbar_s"], alpha_c_from_Zc=1.0 / (1.0 + s["Zc_infinity"])))
    me_ = next(q for q in seq if q["y0"] == a.y0)
    res.update(onset_JE=dict(run=ONSET_RUN, y0=onJ["y0"], Z0=onJ["Z0"], alpha_c=a_onJ),
               onset_F21=dict(run=ONSET_RUN, y0=onF["y0"], alpha_c=1.0 / (1.0 + onF["Z0"])),
               controls_drift=dict(run=DRIFT_RUN, **drift), sequence=seq,
               alpha_c=me_["alpha_c"], distance_from_JE_onset=me_["alpha_c"] - a_onJ,
               distance_over_max_drift=(me_["alpha_c"] - a_onJ) / max(drift.values()))
    for key, y in (("cc2", 0.314), ("cc1", 0.334032)):
        q = next(q for q in seq if q["y0"] == y)
        res[f"distance_{key}_from_JE_onset"] = q["alpha_c"] - a_onJ
    print(json.dumps({k: v for k, v in res.items() if k != "sequence"}, indent=1), flush=True)
    ok_dist = res["distance_from_JE_onset"] > max(drift.values())
    res["distance_exceeds_drift"] = bool(ok_dist)

    # B. particle files
    spec = dict(family="king", y0=a.y0, role="D3: stable side of the Juttner fluid onset", tag=tag_of(a.y0))
    stem, meta = me.build(spec, a.out, a.N, a.seed, "stratified")
    res["stem"] = stem
    # C. offline checks of the file
    ce.check_model(spec, a.out, a.N, a.seed)
    chk = ce.RES
    fails = [(g, n) for g, d in chk.items() if isinstance(d, dict)
             for n, v in d.items() if isinstance(v, dict) and v.get("pass") is False]
    with open(os.path.join(a.out, "checks.json"), "w") as f:
        json.dump(dict(checks=chk, failures=fails), f, indent=1, default=float)
    res["checks_failed"] = fails
    res["checks_n"] = sum(1 for d in chk.values() if isinstance(d, dict)
                          for v in d.values() if isinstance(v, dict) and "pass" in v)
    # D. Knudsen constant and expected collisions
    K, H, v1 = C.kn_constant(meta)
    res["K"] = K
    res["H_c"] = H
    res["sigma_tilde"] = {"10": K / 10.0, "1": K / 1.0}
    conv = kn.model_conversion(spec, a.N, np.random.default_rng(7))
    K_kn = conv["Kn_times_sigma_tilde"] / conv["l_over_lambdaBSI"]
    t300 = 300.0 / conv["t_d_coord"]
    res["knudsen"] = dict(Kn_times_sigma_tilde_l=conv["Kn_times_sigma_tilde"],
                          l_over_lambda=conv["l_over_lambdaBSI"], K_from_knudsen=K_kn,
                          K_rel_diff=K_kn / K - 1.0, H_c=conv["H_c"], rho0_c=conv["rho0_c"],
                          t_d_coord=conv["t_d_coord"], nu_bar_times_Kn_l=conv["nu_bar_times_Kn"],
                          nu_c_times_Kn_l=conv["nu_c_times_Kn"])
    # knudsen.py's rates are per its l-based Kn; at the deck's sigma~ = K/Kn_track the
    # l-based Kn is Kn_track * (l/lambda), so nu per t_d = nu_bar_Kn_l / (Kn_track l/lambda)
    res["collisions_per_particle_300M_initial_rate"] = {
        k: conv["nu_bar_times_Kn"] / (float(k) * conv["l_over_lambdaBSI"]) * t300 for k in ("10", "1")}
    res["meta_summary"] = {k: meta[k] for k in ("M0", "E0", "alpha_c", "Zc_infinity", "Eb_over_M0",
                                                "R_areal", "rbar_s", "n_c", "p_c", "pT_c")}
    res["particles"] = meta["particles"]
    res["particle_invariants"] = meta["particle_invariants"]
    res["table_constraint"] = meta["table_constraint"]
    # same quantities for the wave-2 CC2 file, as the comparison basis
    m2 = json.load(open(os.path.join(C.SCRATCH, WAVE2_IC, "king_y0p31400_stratified_N100000_s1.json")))
    conv2 = kn.model_conversion(dict(family="king", y0=0.314, role="CC2", tag="king_y0p31400"), a.N,
                                np.random.default_rng(7))
    t300b = 300.0 / conv2["t_d_coord"]
    res["cc2_reference"] = dict(K=C.kn_constant(m2)[0], t_d_coord=conv2["t_d_coord"],
                                collisions_per_particle_300M_initial_rate={
                                    k: conv2["nu_bar_times_Kn"] / (float(k) * conv2["l_over_lambdaBSI"]) * t300b
                                    for k in ("10", "1")})
    with open(os.path.join(a.out, "d3_ic.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)
    print("K =", K, "sigma~(Kn=10,1) =", res["sigma_tilde"], "K(knudsen) rel diff", res["knudsen"]["K_rel_diff"])
    print("collisions per particle in 300 M (initial rate):", res["collisions_per_particle_300M_initial_rate"],
          "CC2:", res["cc2_reference"]["collisions_per_particle_300M_initial_rate"])
    print("checks:", res["checks_n"], "failed:", fails, flush=True)

    figure(a.out, a.out, res)
    return 1 if (fails or not ok_dist) else 0


if __name__ == "__main__":
    sys.exit(main())
