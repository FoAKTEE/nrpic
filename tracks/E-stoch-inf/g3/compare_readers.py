#!/usr/bin/env python3
"""The two zeta readers cell by cell on one 128^3 pilot dump (g3/JOURNAL.md entry 5, P5-2; verifier's Request 3).

    compare_readers.py OUT --member <pilot member dir> --deck <usr_prod.athinput> --lead-json <zeta_tests.json>

Lead: zeta/zeta_reader.py (V, dV, map_rk4 verbatim through ast, 4000 steps in phi, its phi_e), v = Pi/(-K/3).
Verifier: g3/zeta_verify/scripts/zv_lib.py (own dump parser, long-double RK4 in N, h = 2e-3, Newton last step),
phi_e from the lockstep record of the dump integrated to N = 15 as analyse_pairs.py does, y = -3 Pi/K.
Both: zeta = -1/2 ln(chi/<chi>) + Delta N. Cells (--sample, batch 23 after the full-box run E-20261126-022448-9510ee9
was stopped: more than 23 core-minutes for the verifier's map alone on the loaded machine): --ncells random cells plus
every cell with |R^NR| > 2.5 sigma_lin (the tail cells, where a reader difference could move F(3), F(4)). The box mean of
zeta is a constant per reader; the comparison removes the sample mean of the difference (equivalent up to that constant).
Writes OUT/compare.json and OUT/fig_compare.png.
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
    ap.add_argument("--ncells", type=int, default=100000)
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
    Rx, _, _ = RP.RS.r_nr(dump, 1)
    sig_lin, _ = RP.RS.sigma_lin_of(dump[:-len(".dump")] + ".modes", Rx.shape[0])
    rng = np.random.default_rng(11)
    pick = np.zeros(Rx.size, bool)
    pick[rng.choice(Rx.size, a.ncells, replace=False)] = True
    pick |= np.abs(Rx.ravel()) > 2.5 * sig_lin
    idx = np.nonzero(pick)[0]
    phi = f["phi"].ravel()[idx].astype(LD)
    y = -3 * f["Pi"].ravel()[idx].astype(LD) / f["K"].ravel()[idx].astype(LD)
    dN_v = Z.efolds_to_surface(pot, phi, y, phi_e_v, 2e-3)
    psi = -0.5 * np.log(f["chi"] / f["chi"].mean()).ravel()[idx]
    zv = psi + np.asarray(dN_v, dtype=float)
    t1 = time.time()
    # ---------------- lead's reader
    _, g = RP.fl.ll.read_dump(dump, ["phi", "Pi", "chi", "K"])
    ns = RP.lead_namespace(os.path.join(TRK, "zeta", "zeta_reader.py"), lam, vev, L["phi_e"], 4000)
    v = (g["Pi"] / (-g["K"] / 3.0)).ravel()[idx]
    dN_l = ns["map_rk4"](g["phi"].ravel()[idx], v)
    zl = -0.5 * np.log(g["chi"] / g["chi"].mean()).ravel()[idx] + dN_l
    t2 = time.time()
    d = zl - zv
    d = d - d.mean()
    x = -Rx.ravel()[idx] / sig_lin                  # first-order zeta in units of sigma_lin, the cell's tail position
    zl = zl - zl.mean()
    zv = zv - zv.mean()
    sz = float(sig_lin)
    same_input = dict(phi=float(np.max(np.abs(g["phi"] - f["phi"]))), Pi=float(np.max(np.abs(g["Pi"] - f["Pi"]))),
                      chi=float(np.max(np.abs(g["chi"] - f["chi"]))), K=float(np.max(np.abs(g["K"] - f["K"]))))
    tail = np.abs(x) > 2.5
    res = dict(member=a.member, time=float(head["time"]), phi_e_lead=L["phi_e"], phi_e_verifier=float(phi_e_v),
               parsers_max_abs_diff=same_input, sigma_lin=sz, n_cells=int(idx.size), n_tail_cells=int(tail.sum()),
               max_abs_diff=float(np.max(np.abs(d))), rms_diff=float(np.sqrt(np.mean(d ** 2))),
               max_abs_diff_tail=float(np.max(np.abs(d[tail]))), max_abs_diff_over_sigma=float(np.max(np.abs(d)) / sz),
               slope_diff_on_x=float(np.sum(d * x) / np.sum(x * x)),
               quad_diff_on_x2=float(np.polyfit(x, d, 2)[0]),
               cells_flipping_3sigma=int(np.sum((zl > 3 * sz) != (zv > 3 * sz)) + np.sum((zl < -3 * sz) != (zv < -3 * sz))),
               cells_flipping_4sigma=int(np.sum((zl > 4 * sz) != (zv > 4 * sz)) + np.sum((zl < -4 * sz) != (zv < -4 * sz))),
               wall_verifier_s=t1 - t0, wall_lead_s=t2 - t1)
    with open(os.path.join(a.out, "compare.json"), "w") as fp:
        json.dump(res, fp, indent=1)
    print(json.dumps(res, indent=1), flush=True)
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(fs.COLUMN_WIDTH * 2.0, 2.8))
    ax[0].plot(x, d, ".", ms=1, color=fs.SERIES[0], alpha=0.4)
    ax[0].set_xlabel(r"$-\mathcal{R}^{\rm NR}/\sigma_{\rm lin}$ of the cell (sample and tail cells)")
    ax[0].set_ylabel(r"$\zeta_{\rm lead}-\zeta_{\rm verifier}$ (mean removed)")
    ax[0].axhline(0.0, **fs.GUIDE)
    ax[1].hist(d.ravel(), bins=200, color=fs.SERIES[1], log=True)
    ax[1].set_xlabel(r"$\zeta_{\rm lead}-\zeta_{\rm verifier}$ (mean removed)")
    ax[1].set_ylabel("cells")
    fig.tight_layout()
    fs.save(fig, os.path.join(a.out, "fig_compare"))


if __name__ == "__main__":
    main()
