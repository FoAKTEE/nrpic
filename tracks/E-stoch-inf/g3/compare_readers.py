#!/usr/bin/env python3
"""The two zeta readers cell by cell on one 128^3 pilot dump (g3/JOURNAL.md entry 5, P5-2; verifier's Request 3).

    compare_readers.py OUT --member <pilot member dir> --deck <usr_prod.athinput> --lead-json <zeta_tests.json>

Lead: zeta/zeta_reader.py (V, dV, map_rk4 verbatim through ast, 4000 steps in phi, its phi_e), v = Pi/(-K/3).
Verifier: g3/zeta_verify/scripts/zv_lib.py (own dump parser, long-double RK4 in N, h = 2e-3, Newton last step),
phi_e from the lockstep record of the dump integrated to N = 15 as analyse_pairs.py does, y = -3 Pi/K.
Both: zeta = -1/2 ln(chi/<chi>) + Delta N, box mean removed. Writes OUT/compare.json and OUT/fig_compare.png.
"""
import argparse
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TRK = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "zeta_verify", "scripts"))
sys.path.insert(0, os.path.join(TRK, "repro", "figs", "figures"))
import zv_lib as Z  # noqa: E402
import read_pilot as RP  # noqa: E402
import figstyle as fs  # noqa: E402

LD = Z.LD


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--member", required=True)
    ap.add_argument("--deck", required=True)
    ap.add_argument("--lead-json", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    L = json.load(open(a.lead_json))
    lam = RP.deck_value(a.deck, "scalar_field", "lambda")
    vev = RP.deck_value(a.deck, "scalar_field", "vev")
    dump = os.path.join(a.member, "usr.sf.00001.dump")
    t0 = time.time()
    # ---------------- verifier's reader
    f, head = Z.read_dump(dump)
    hdr = Z.read_modes_header(dump[:-len(".dump")] + ".modes")
    pot = Z.Inflection(lam, vev)
    phi_b, Pi_b, lna, Hl = LD(hdr["phi_b"]), LD(hdr["Pi_b"]), LD(hdr["ln_a"]), LD(hdr["H"])
    phi_e_v, _ = Z.integrate_to_N(pot, phi_b, Pi_b / Hl, LD(15) - lna, 1e-3)
    phi = f["phi"].astype(LD)
    y = -3 * f["Pi"].astype(LD) / f["K"].astype(LD)
    dN_v = Z.efolds_to_surface(pot, phi.ravel(), y.ravel(), phi_e_v, 2e-3).reshape(phi.shape)
    psi = -0.5 * np.log(f["chi"] / f["chi"].mean())
    zv = psi + np.asarray(dN_v - dN_v.mean(), dtype=float)
    zv = zv - zv.mean()
    t1 = time.time()
    # ---------------- lead's reader
    _, g = RP.fl.ll.read_dump(dump, ["phi", "Pi", "chi", "K"])
    ns = RP.lead_namespace(os.path.join(TRK, "zeta", "zeta_reader.py"), lam, vev, L["phi_e"], 4000)
    v = g["Pi"] / (-g["K"] / 3.0)
    dN_l = ns["map_rk4"](g["phi"].ravel(), v.ravel()).reshape(g["phi"].shape)
    zl = -0.5 * np.log(g["chi"] / g["chi"].mean()) + dN_l
    zl = zl - zl.mean()
    t2 = time.time()
    d = zl - zv
    sz = float(zl.std())
    same_input = dict(phi=float(np.max(np.abs(g["phi"] - f["phi"]))), Pi=float(np.max(np.abs(g["Pi"] - f["Pi"]))),
                      chi=float(np.max(np.abs(g["chi"] - f["chi"]))), K=float(np.max(np.abs(g["K"] - f["K"]))))
    res = dict(member=a.member, time=float(head["time"]), phi_e_lead=L["phi_e"], phi_e_verifier=float(phi_e_v),
               parsers_max_abs_diff=same_input, sigma_zeta=sz, max_abs_diff=float(np.max(np.abs(d))),
               rms_diff=float(np.sqrt(np.mean(d ** 2))), max_abs_diff_over_sigma=float(np.max(np.abs(d)) / sz),
               slope_diff_on_zeta=float(np.sum(d * zl) / np.sum(zl * zl)),
               quad_diff_on_zeta2=float(np.polyfit(zl.ravel()[::7], d.ravel()[::7], 2)[0]),
               F3_lead=[float(np.mean(zl > 3 * sz)), float(np.mean(zl < -3 * sz))],
               F3_verifier=[float(np.mean(zv > 3 * zv.std())), float(np.mean(zv < -3 * zv.std()))],
               F4_lead=[float(np.mean(zl > 4 * sz)), float(np.mean(zl < -4 * sz))],
               F4_verifier=[float(np.mean(zv > 4 * zv.std())), float(np.mean(zv < -4 * zv.std()))],
               cells_flipping_3sigma=int(np.sum((np.abs(zl) > 3 * sz) != (np.abs(zv) > 3 * zv.std()))),
               wall_verifier_s=t1 - t0, wall_lead_s=t2 - t1)
    with open(os.path.join(a.out, "compare.json"), "w") as fp:
        json.dump(res, fp, indent=1)
    print(json.dumps(res, indent=1), flush=True)
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(fs.COLUMN_WIDTH * 2.0, 2.8))
    rng = np.random.default_rng(7)
    idx = rng.choice(zl.size, 200000, replace=False)
    ax[0].plot(zl.ravel()[idx] / sz, d.ravel()[idx], ",", color=fs.SERIES[0], alpha=0.4)
    ax[0].set_xlabel(r"$\zeta_{\rm lead}/\sigma_\zeta$ (200000 random cells)")
    ax[0].set_ylabel(r"$\zeta_{\rm lead}-\zeta_{\rm verifier}$")
    ax[0].axhline(0.0, **fs.GUIDE)
    ax[1].hist(d.ravel(), bins=200, color=fs.SERIES[1], log=True)
    ax[1].set_xlabel(r"$\zeta_{\rm lead}-\zeta_{\rm verifier}$, all $128^3$ cells")
    ax[1].set_ylabel("cells")
    fig.tight_layout()
    fs.save(fig, os.path.join(a.out, "fig_compare"))


if __name__ == "__main__":
    main()
