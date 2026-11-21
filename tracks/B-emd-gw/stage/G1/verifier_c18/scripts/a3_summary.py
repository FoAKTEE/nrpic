"""A3: summary figure, ratio of each recomputed number to the printed ledger value.

Usage: python a3_summary.py <results dir> <M1e run dir>
Ledger values typed from note/tables/ledger.tex (line numbers in the labels); mine read from
the run outputs copied to results/ (a1_rows, a2_round3, p2_null_pred, p3_slicing) and M1e.
"""
import json
import os
import sys

import numpy as np

R, M1E = sys.argv[1], sys.argv[2]
OUT = os.environ.get("NRPIC_RUN_DIR", "/data/haiyangw/nrpic/scratch/B-emd-gw/tmp/a3")
os.makedirs(OUT, exist_ok=True)
J = {k: json.load(open(os.path.join(R, f"{k}.json"))) for k in ("a1_rows", "a2_round3", "p2_null_pred", "p3_slicing")}
a1, a2, p2, p3 = J["a1_rows"], J["a2_round3"], J["p2_null_pred"], J["p3_slicing"]
e = {n: {os.path.basename(r["file"]): r for r in json.load(open(os.path.join(M1E, f"m1_{n}.json")))["rows"]}
     for n in ("dav_t", "dav_pcs4bt")}
rows = [
    ("197", 9.5e-13, a1["row197"]["maxrel_2_40"]), ("197", 4.71e-13, a1["row197"]["maxrel_80_140"]),
    ("200", 1.27e-7, a1["row200"]["jit0p3"][0]), ("200", 5.98e-7, a1["row200"]["jit0p3"][1]),
    ("200", 4.41e-8, a1["row200"]["jit0p1"][0]), ("200", 2.04e-7, a1["row200"]["jit0p1"][1]),
    ("200", 2.77e-16, a1["row200"]["eps0"][1]),
    ("201", 0.927, p2["jit0p3"]["K1"]["ratio_min_med_max"][0]), ("201", 1.04, p2["jit0p3"]["K1"]["ratio_min_med_max"][1]),
    ("201", 1.33, p2["jit0p3"]["K1"]["ratio_min_med_max"][2]), ("201", 0.942, p2["jit0p1"]["K1"]["ratio_min_med_max"][0]),
    ("201", 1.03, p2["jit0p1"]["K1"]["ratio_min_med_max"][1]), ("201", 1.27, p2["jit0p1"]["K1"]["ratio_min_med_max"][2]),
    ("202", 0.741, p2["jit0p3"]["K2"]["ratio_min_med_max"][0]), ("202", 0.943, p2["jit0p3"]["K2"]["ratio_min_med_max"][1]),
    ("202", 1.0, p2["jit0p3"]["K2"]["ratio_min_med_max"][2]), ("202", 0.728, p2["jit0p1"]["K2"]["ratio_min_med_max"][0]),
    ("202", 0.951, p2["jit0p1"]["K2"]["ratio_min_med_max"][1]), ("202", 1.01, p2["jit0p1"]["K2"]["ratio_min_med_max"][2]),
    ("203", 0.364, p2["jit0p3"]["K1"]["maxabs_phase"]), ("203", 0.184, p2["jit0p1"]["K1"]["maxabs_phase"]),
    ("203", 0.0812, p2["jit0p3"]["K2"]["maxabs_phase"]), ("203", 0.0629, p2["jit0p1"]["K2"]["maxabs_phase"]),
    ("204", 2.12, a1["row204"]["min"]), ("204", 2.56, a1["row204"]["median"]), ("204", 2.65, a1["row204"]["max"]),
    ("205", 0.0148, a1["row205"]["2-20"]), ("205", 0.0251, a1["row205"]["20-80"]), ("205", 0.0314, a1["row205"]["80-140"]),
    ("206", 12.0, p2["jit0p3"]["rms_TT_over_static_estimate_3_20"][0]), ("206", 14.7, p2["jit0p3"]["rms_TT_over_static_estimate_3_20"][1]),
] + [("207", v, a1["row207"][k]["round"]) for k, v in (("j3_a2", 0.984), ("j3_a12", 0.949), ("j3_a140", 0.61), ("j1_a2", 0.985),
                                                         ("j1_a12", 0.952), ("s01_a12", 6.18e-12), ("s01_a121", 5.59e-5))] + [
    ("208", 0.0115, a1["row208"]["jit0p3"]["kin_over_grad"]), ("208", 0.00925, a1["row208"]["jit0p1"]["kin_over_grad"]),
] + [("209", v, a1["row209"][k]) for k, v in (("d01_e1", 10.3), ("d01_e0p3", 12.6), ("d0025_e1", 33.7), ("d0025_e0p3", 41.7))] + [
    ("210", v, a1["row210"][k]) for k, v in (("d01_e1", 13.0), ("d01_e0p3", 17.7), ("d0025_e1", 46.3), ("d0025_e0p3", 63.3))] + [
    ("211", v, a1["row211"][k]) for k, v in (("a20", 17.9), ("a30", 16.8), ("a40", 17.2), ("a60", 19.1))] + [
    ("212", v, a1["row212"][k]) for k, v in (("a20", 50.4), ("a30", 16.8), ("a40", 19.4), ("a60", 18.3))] + [
    ("213", 1.06, a1["row213"]["e1"][0]), ("213", 1.47, a1["row213"]["e1"][1]),
    ("213", 1.07, a1["row213"]["e0p3"][0]), ("213", 1.31, a1["row213"]["e0p3"][1])] + [
    ("214", v, a1["row214"][k]) for k, v in (("d0025_e1", 0.0939), ("d0025_e0p3", 0.0505), ("d01_e1", 1.23), ("d01_e0p3", 1.15))] + [
    ("215", v, a1["row215"][k]) for k, v in (("dbin_d0025_e1", 3.17e-4), ("dbin_d0025_e0p3", 3.49e-4), ("bin_d0025_e1", 9.56e-4),
                                             ("bin_d0025_e0p3", 2.66e-3), ("bin_d01_e1", 4.35e-3), ("bin_d01_e0p3", 2.22e-3))] + [
    ("116", 0.0055, a1["row116_117"]["eps0p1"]["max_le20"]), ("116", 0.00596, a1["row116_117"]["eps0p3"]["max_le20"]),
    ("116", 0.0112, a1["row116_117"]["eps1"]["max_le20"]), ("117", 0.0163, a1["row116_117"]["eps0p1"]["a40_interp"]),
    ("117", 0.0185, a1["row116_117"]["eps0p3"]["a40_interp"]), ("117", 0.0397, a1["row116_117"]["eps1"]["a40_interp"]),
    ("120", 0.084, a1["row118_121"]["64"]["median_cor_over_raw"]), ("120", 0.0928, a1["row118_121"]["32"]["median_cor_over_raw"]),
    ("120", 0.89, a1["row118_121"]["64"]["share_big"]), ("121", 5.24, a1["row118_121"]["64"]["median_quad_over_raw"]),
    ("121", 5.32, a1["row118_121"]["32"]["median_quad_over_raw"]),
    ("122", 0.00444, a1["row122"]["a10"][0]), ("122", 0.00687, a1["row122"]["a10"][1]),
    ("122", 0.0231, a1["row122"]["a20"][0]), ("122", 0.0345, a1["row122"]["a20"][1]),
    ("123", 16.2, a1["row123"][0]), ("123", 52.2, a1["row123"][1]),
    ("125", 0.999, -p3["row125"]["largest_corr"]), ("125", 5.48e-5, p3["row125"]["rms_ratio_min"]), ("125", 0.0408, p3["row125"]["rms_ratio_max"]),
    ("26", 1.21e-9, e["dav_t"]["east.00002.rst"]["rms_TT"]), ("26", 2.49e-9, e["dav_t"]["east.00013.rst"]["rms_TT"]),
    ("26", 1.28e-9, e["dav_t"]["east.00013.rst"]["rms_nonTT"] ** 2), ("26", 1.22e-9, e["dav_pcs4bt"]["east.00002.rst"]["rms_TT"]),
    ("26", 4.31e-9, e["dav_pcs4bt"]["east.00013.rst"]["rms_TT"]), ("26", 1.34e-9, e["dav_pcs4bt"]["east.00013.rst"]["rms_nonTT"] ** 2),
    ("27", 2.06e-10, e["dav_t"]["east.00013.rst"]["rms_Gq"]), ("27", 2.5e-9, e["dav_t"]["east.00013.rst"]["rms_TT_minus_Gq"]),
    ("27", 0.017, e["dav_t"]["east.00013.rst"]["kin"] / e["dav_t"]["east.00013.rst"]["grad"]),
    ("27", 2.23e-10, e["dav_pcs4bt"]["east.00013.rst"]["rms_Gq"]), ("27", 4.32e-9, e["dav_pcs4bt"]["east.00013.rst"]["rms_TT_minus_Gq"]),
    ("27", 0.0188, e["dav_pcs4bt"]["east.00013.rst"]["kin"] / e["dav_pcs4bt"]["east.00013.rst"]["grad"]),
    ("r3 P12", 7.8e-5, a2["p1_vs_p27"]["maxabs_2_40"]), ("r3 P12", 7.4e-5, a2["p8_vs_p27"]["maxabs_2_40"]),
    ("r3 P12", 3.4e-5, a2["p8_vs_p27"]["maxabs_80_140.5"]), ("r3 P12", 2.5e-4, a2["p1_vs_p27"]["maxabs_80_140.5"]),
    ("r3 P13", 1.6e-4, a2["n128p1_vs_n64p8"]["maxabs_2_40"]), ("r3 P13", 1.8e-4, a2["n128p1_vs_n64p1"]["maxabs_2_40"]),
    ("r3 P13", 1.30e-2, a2["n128p1_vs_n64p8"]["rms_80_140.5"]), ("r3 P13", 3.39e-2, a2["n64p8_vs_n32p8"]["rms_80_140.5"]),
    ("r3 eps2", 1.16, a2["eps2_test"]["n32"]["Q_d0025"]["20"]), ("r3 eps2", 1.10, a2["eps2_test"]["n64"]["Q_d0025"]["20"]),
    ("r3 eps2", 21.5, a2["eps2_test"]["n32"]["R_e0p3"]["20"]),
    ("r3 P16", 0.994, a2["p16"]["tau0.1"]["D_frac_ge16_round"]), ("r3 P16", 0.856, a2["p16"]["a2"]["D_frac_ge16_round"]),
    ("r3 P16", 0.27, a2["p16"]["a12"]["D_frac_ge16_round"]),
]
ratio = np.array([m / l for _, l, m in rows])
out = {"n": len(rows), "rows": [{"line": a, "ledger": l, "mine": m, "ratio": m / l} for a, l, m in rows],
       "n_within_1pct": int(np.sum(np.abs(ratio - 1) <= 0.01)), "n_within_5pct": int(np.sum(np.abs(ratio - 1) <= 0.05)),
       "worst": sorted([(abs(m / l - 1), a, l, m) for a, l, m in rows])[-8:]}
with open(os.path.join(OUT, "a3_summary.json"), "w") as f:
    json.dump(out, f, indent=1)

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle  # noqa: E402,F401

fig, ax = plt.subplots(figsize=(10, 3.8))
x = np.arange(len(rows))
ax.plot(x, ratio - 1, "o", ms=3)
ax.axhspan(-0.01, 0.01, color="0.9")
ax.set_yscale("symlog", linthresh=1e-3)
ax.set_xticks(x[::1]); ax.set_xticklabels([a for a, _, _ in rows], rotation=90, fontsize=5)
ax.set_ylabel("mine / ledger - 1")
ax.set_title(f"verifier_c18: {len(rows)} recomputed numbers ({out['n_within_1pct']} within 1 per cent of the printed value)", fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "a3_summary.png"), dpi=140)
print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
