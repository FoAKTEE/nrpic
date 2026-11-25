"""V3, U-A2', U-A2n, U-A3, U-R, U-S from the coefficient caches of modes_nf.py and the
own reference of reference.py; alpha from noise/ref/philox_ref.py.

python3 judge_modes.py --ref REFDIR --modes MODESDIR --out DIR
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vlib  # noqa: E402

L32 = vlib.L_BOX ** -1.5


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", required=True)
    ap.add_argument("--modes", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    ref = np.load(os.path.join(a.ref, "reference_dumps.npz"))
    meta = json.load(open(os.path.join(a.modes, "modes_nf.json")))
    n = np.load(os.path.join(a.modes, "modes_n.npy"))
    n2 = (n ** 2).sum(1)
    k = np.sqrt(n2)
    sh = np.searchsorted(ref["q2"], n2)
    assert np.all(ref["q2"][sh] == n2)
    half = n2 <= 1024
    alpha = {s: vlib.alpha_modes(vlib.SEED[s], n) for s in ("A", "B")}

    def pred(seed, t):
        i = int(np.argmin(np.abs(ref["t"] - t)))
        assert abs(ref["t"][i] - t) < 1e-12, (t, ref["t"][i])
        return L32 * ref["W"][i][sh] * ref["R"][i][sh] * alpha[seed]

    def load(lab, d):
        z = np.load(os.path.join(a.modes, f"{lab}_d{d:02d}.npz"))
        return {kk: z[kk] for kk in z.files}, meta[f"{lab}_d{d:02d}"]

    res = {}
    # --- V3: extraction at t = 0
    for lab, seed in (("U256ap", "A"), ("U256bp", "B")):
        c, m = load(lab, 0)
        p = pred(seed, m["time"])
        i0 = int(np.argmin(np.abs(ref["t"] - m["time"])))
        W0 = ref["W"][i0][sh]
        sel = W0 > 0.5
        rel = np.abs(c["c"][sel] / p[sel] - 1)
        res[f"V3_{lab}"] = {"t": m["time"], "n_modes_W_gt_half": int(sel.sum()),
                            "max_rel": float(rel.max()),
                            "max_rel_n2_le_4": float(np.abs(c["c"][n2 <= 4] / p[n2 <= 4] - 1).max()),
                            "sign": float(np.real(np.vdot(p[sel], c["c"][sel])))}

    # --- N_f
    C = {}
    for lab in ("U256ap", "U256am", "U256bp", "U256bm", "U256hp", "U256hm", "U256qp", "U256qm",
                "U320ap", "U320am"):
        C[lab] = load(lab, 20)
    tN = {lab: C[lab][1]["time"] for lab in C}
    res["Nf_times"] = tN
    res["Nf_max_dt"] = float(max(abs(v - tN["U256ap"]) for v in tN.values()))
    pairs = {"A256": ("U256ap", "U256am", 1.0, "A"), "B256": ("U256bp", "U256bm", 1.0, "B"),
             "A256h": ("U256hp", "U256hm", 0.5, "A"), "A256q": ("U256qp", "U256qm", 0.25, "A"),
             "A320": ("U320ap", "U320am", 1.0, "A")}
    D = {}
    for key, (lp, lm, s, seed) in pairs.items():
        cp, cm = C[lp][0]["c"], C[lm][0]["c"]
        O = 0.5 * (cp - cm)
        E = 0.5 * (cp + cm)
        p = pred(seed, tN[lp])
        Dn = np.abs(O / (s * p) - 1)
        D[key] = Dn
        Ds = np.abs(cp / (s * p) - 1)
        imax = int(np.argmax(np.where(half, Dn, -1)))
        absal = np.abs(alpha[seed])
        rank = float((absal < absal[imax]).mean())
        # variant without the gt term of Phi (sensitivity of the extraction)
        Ov = 0.5 * ((cp - C[lp][0]["c_gt"]) - (cm - C[lm][0]["c_gt"]))
        Dv = np.abs(Ov / (s * p) - 1)
        r = {"s": s, "seed": seed,
             "U-A2p_max_D_k_le_32": float(Dn[half].max()),
             "argmax_n": n[imax].tolist(), "argmax_absalpha_quantile": rank,
             "max_D_all_band": float(Dn.max()),
             "argmax_all_n": n[int(np.argmax(Dn))].tolist(),
             "median_D_k_le_32": float(np.median(Dn[half])),
             "single_run_max_D_k_le_32": float(Ds[half].max()),
             "single_run_max_D_all": float(Ds.max()),
             "U-A2n_even_over_odd_band": float(np.sqrt((np.abs(E) ** 2).sum() / (np.abs(O) ** 2).sum())),
             "U-A2n_even_over_odd_k_le_32": float(np.sqrt((np.abs(E[half]) ** 2).sum() /
                                                          (np.abs(O[half]) ** 2).sum())),
             "variant_no_gt_max_D_k_le_32": float(Dv[half].max()),
             "gt_part_rms_over_c_rms": float(np.sqrt((np.abs(C[lp][0]["c_gt"]) ** 2).sum() /
                                                     (np.abs(cp) ** 2).sum())),
             "chi_part_rms_over_c_rms": float(np.sqrt((np.abs(C[lp][0]["c_chi"]) ** 2).sum() /
                                                      (np.abs(cp) ** 2).sum()))}
        low = n2 <= 9
        r["U-A3_n_modes"] = int(low.sum())
        r["U-A3_single_ratio_minmax"] = [float(x) for x in
                                         (np.abs(cp[low]) ** 2 / np.abs(s * p[low]) ** 2)[[0]]]
        rat_s = np.abs(cp[low]) ** 2 / np.abs(s * p[low]) ** 2
        rat_o = np.abs(O[low]) ** 2 / np.abs(s * p[low]) ** 2
        r["U-A3_single_ratio_minmax"] = [float(rat_s.min()), float(rat_s.max())]
        r["U-A3_odd_ratio_minmax"] = [float(rat_o.min()), float(rat_o.max())]
        r["U-A3_max_dev_single"] = float(np.abs(rat_s - 1).max())
        r["U-A3_max_dev_odd"] = float(np.abs(rat_o - 1).max())
        # one-point
        r["rms_band_plus"] = C[lp][1]["rms_band"]
        r["rms_band_minus"] = C[lm][1]["rms_band"]
        r["rms_full_plus"] = C[lp][1].get("rms_full")
        r["max_abs_full_plus"] = C[lp][1].get("max_abs_full")
        r["skew_full_plus"] = C[lp][1].get("skew_full")
        r["exkurt_full_plus"] = C[lp][1].get("exkurt_full")
        r["realisation_lattice_rms"] = float(np.sqrt(2.0 * (np.abs(s * p) ** 2).sum()))
        res[key] = r

    # --- U-R
    ur = {}
    ur["i_factor_256_over_320"] = res["A256"]["U-A2p_max_D_k_le_32"] / res["A320"]["U-A2p_max_D_k_le_32"]
    P = {}
    for lab in ("U256ap", "U320ap"):
        P[lab] = np.bincount(n2, weights=np.abs(C[lab][0]["c"]) ** 2, minlength=4097)
    qs = np.nonzero(P["U256ap"] > 0)[0]
    rel = P["U320ap"][qs] / P["U256ap"][qs] - 1
    ur["ii_max_shell_dev_k_le_32"] = float(np.abs(rel[qs <= 1024]).max())
    ur["ii_max_shell_dev_k_le_64"] = float(np.abs(rel).max())
    ur["ii_q_at_max"] = int(qs[np.argmax(np.abs(rel))])
    e256 = res["A256"]["U-A2n_even_over_odd_band"]
    e320 = res["A320"]["U-A2n_even_over_odd_band"]
    ur["iii_even_odd_256"] = e256
    ur["iii_even_odd_320"] = e320
    ur["iii_rel_diff"] = abs(e320 / e256 - 1)
    ur["iii_rel_diff_k_le_32"] = abs(res["A320"]["U-A2n_even_over_odd_k_le_32"] /
                                     res["A256"]["U-A2n_even_over_odd_k_le_32"] - 1)
    ur["verdict"] = {"i": 2.0 <= ur["i_factor_256_over_320"] <= 4.5,
                     "ii": ur["ii_max_shell_dev_k_le_32"] < 1e-3 and ur["ii_max_shell_dev_k_le_64"] < 1e-2,
                     "iii": ur["iii_rel_diff"] < 0.05}
    res["U-R"] = ur
    # --- U-S
    ens = json.load(open(os.path.join(a.ref, "reference.json")))["lattice_rms_Nf"]
    res["U-S"] = {"ensemble_lattice_rms_own": ens,
                  "rms_band_bp": res["B256"]["rms_band_plus"],
                  "rms_band_bm": res["B256"]["rms_band_minus"],
                  "dev_from_0.89366": res["B256"]["rms_band_plus"] - 0.89366,
                  "dev_from_own_ensemble": res["B256"]["rms_band_plus"] - ens,
                  "seed_B_realisation_lattice_rms": res["B256"]["realisation_lattice_rms"],
                  "rms_full_bp": res["B256"]["rms_full_plus"],
                  "pass": abs(res["B256"]["rms_band_plus"] - 0.89366) < 5e-3,
                  "seed_A_rms_band": res["A256"]["rms_band_plus"]}
    res["verdicts"] = {
        "U-A2p_A": res["A256"]["U-A2p_max_D_k_le_32"] < 0.02,
        "U-A2p_B": res["B256"]["U-A2p_max_D_k_le_32"] < 0.02,
        "U-A2n_A_lt_0.3": res["A256"]["U-A2n_even_over_odd_band"] < 0.3,
        "U-A2n_B_lt_0.3": res["B256"]["U-A2n_even_over_odd_band"] < 0.3,
        "U-A3_A": res["A256"]["U-A3_max_dev_single"] < 0.1,
        "U-A3_B": res["B256"]["U-A3_max_dev_single"] < 0.1}
    json.dump(res, open(os.path.join(a.out, "judge_modes.json"), "w"), indent=1, default=float)
    print(json.dumps(res, indent=1, default=float))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle
    figstyle.use_style()
    fig, ax = plt.subplots(2, 2, figsize=(10, 7))
    x = ax[0, 0]
    rng = np.random.default_rng(1)
    sub = rng.choice(len(n), 60000, replace=False)
    for key, c in zip(("A256", "B256", "A320"), figstyle.series_colors(3)):
        x.loglog(k[sub], D[key][sub], ".", ms=0.6, color=c, alpha=0.5, label=key)
    x.axhline(0.02, color="k", ls="--", lw=0.8)
    x.axvline(32, color="0.5", ls=":", lw=0.8)
    x.set_xlabel("k / dk")
    x.set_ylabel("D_n (odd part, N_f)")
    x.set_title("U-A2': 60000 random band modes; dashed: 0.02", fontsize=8)
    x.legend(fontsize=6, markerscale=10)
    x = ax[0, 1]
    for key, c in zip(("A256", "A256h", "A256q"), figstyle.series_colors(3)):
        mx = np.zeros(65)
        kb = np.floor(k).astype(int)
        np.maximum.at(mx, kb, D[key])
        x.semilogy(np.arange(65)[1:], mx[1:], "-", color=c, label=key)
    x.axhline(0.02, color="k", ls="--", lw=0.8)
    x.set_xlabel("k / dk (bin of width 1)")
    x.set_ylabel("max D_n in bin")
    x.set_title("max D_n per k bin, s = 1, 1/2, 1/4", fontsize=8)
    x.legend(fontsize=6)
    x = ax[1, 0]
    x.semilogy(np.sqrt(qs), np.abs(rel), ".", ms=1.5)
    x.axhline(1e-3, color="k", ls="--", lw=0.8)
    x.axhline(1e-2, color="k", ls=":", lw=0.8)
    x.axvline(32, color="0.5", ls=":", lw=0.8)
    x.set_xlabel("k / dk (shell)")
    x.set_ylabel("|P_320 / P_256 - 1| (s = +1, N_f)")
    x.set_title("U-R (ii): shell power between resolutions", fontsize=8)
    x = ax[1, 1]
    low = n2 <= 9
    for key, c in zip(("A256", "B256"), figstyle.series_colors(2)):
        lp = pairs[key][0]
        p = pred(pairs[key][3], tN[lp])
        x.plot(k[low], np.abs(C[lp][0]["c"][low]) ** 2 / np.abs(p[low]) ** 2, "o", ms=3, color=c,
               label=f"{key} single s = +1")
    x.axhspan(0.9, 1.1, color="0.9")
    x.set_xlabel("k / dk")
    x.set_ylabel("|c_n|^2 / |W R alpha L^-3/2|^2")
    x.set_title("U-A3: modes k <= 3 dk at N_f (band: 10 percent)", fontsize=8)
    x.legend(fontsize=6)
    fig.tight_layout()
    fig.savefig(os.path.join(a.out, "fig_modes.png"), dpi=150)


if __name__ == "__main__":
    main()
