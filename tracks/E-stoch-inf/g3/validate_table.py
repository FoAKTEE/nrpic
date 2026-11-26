#!/usr/bin/env python3
"""TB-1..TB-3 of g3/JOURNAL.md entry 10: the table map (zeta_table.py) against the full map on one pilot dump.

    validate_table.py OUT --member <pilot member dir> --deck <usr_prod.athinput> --lead-json <zeta_tests.json>

Cells as compare_readers.py picks them (seed 11: --ncells random plus every cell with |R^NR| > 2.5 sigma_lin).
TB-1: zeta of the table against zeta of map_rk4 (4000 steps) on all these cells. TB-2: the table against the
verifier's map (zv_lib, long double, h = 2e-3, phi_e from the lockstep record) on the tail cells. TB-3: cost.
Writes OUT/validate.json and OUT/fig_validate.png.
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
import zeta_table as ZT  # noqa: E402
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
    Rx, _, _ = RP.RS.r_nr(dump, 1)
    sig_lin, _ = RP.RS.sigma_lin_of(dump[:-len(".dump")] + ".modes", Rx.shape[0])
    rng = np.random.default_rng(11)
    pick = np.zeros(Rx.size, bool)
    pick[rng.choice(Rx.size, a.ncells, replace=False)] = True
    pick |= np.abs(Rx.ravel()) > 2.5 * sig_lin
    idx = np.nonzero(pick)[0]
    tail = np.abs(Rx.ravel()[idx]) > 2.5 * sig_lin
    _, g = RP.fl.ll.read_dump(dump, ["phi", "Pi", "chi", "K"])
    ns = RP.lead_namespace(os.path.join(TRK, "zeta", "zeta_reader.py"), lam, vev, L["phi_e"], 4000)
    phi = g["phi"].ravel()
    v = (g["Pi"] / (-g["K"] / 3.0)).ravel()
    psi = -0.5 * np.log(g["chi"] / g["chi"].mean()).ravel()
    # ---------------- table on the whole box (TB-3 cost)
    t0 = time.time()
    dn_t, info = ZT.table_map(ns["map_rk4"], phi, v)
    t1 = time.time()
    # ---------------- full map on the cells (TB-1)
    dn_f = ns["map_rk4"](phi[idx], v[idx])
    t2 = time.time()
    d1 = dn_t[idx] - dn_f
    # ---------------- verifier's map on the tail cells (TB-2)
    f, head = Z.read_dump(dump)
    hdr = Z.read_modes_header(dump[:-len(".dump")] + ".modes")
    pot = Z.Inflection(lam, vev)
    phi_b, Pi_b, lna, Hl = LD(hdr["phi_b"]), LD(hdr["Pi_b"]), LD(hdr["ln_a"]), LD(hdr["H"])
    phi_e_v, _ = Z.integrate_to_N(pot, phi_b, Pi_b / Hl, LD(15) - lna, 1e-3)
    it = idx[tail]
    y = -3 * f["Pi"].ravel()[it].astype(LD) / f["K"].ravel()[it].astype(LD)
    dn_v = np.asarray(Z.efolds_to_surface(pot, f["phi"].ravel()[it].astype(LD), y, phi_e_v, 2e-3), dtype=float)
    t3 = time.time()
    d2 = (psi[it] + dn_t[it]) - (psi[it] + dn_v)
    d2 = d2 - d2.mean()
    res = dict(member=a.member, time=float(head["time"]), sigma_lin=float(sig_lin), table=info,
               n_cells=int(idx.size), n_tail=int(tail.sum()),
               TB1=dict(max_abs=float(np.max(np.abs(d1))), rms=float(np.sqrt(np.mean(d1 ** 2))),
                        max_abs_tail=float(np.max(np.abs(d1[tail]))),
                        holds=bool(np.max(np.abs(d1)) <= 1e-10 and np.sqrt(np.mean(d1 ** 2)) <= 2e-11),
                        refuted=bool(np.max(np.abs(d1)) > 1e-9)),
               TB2=dict(max_abs=float(np.max(np.abs(d2))), rms=float(np.sqrt(np.mean(d2 ** 2))),
                        holds=bool(np.max(np.abs(d2)) < 1e-8 and np.sqrt(np.mean(d2 ** 2)) < 2e-9),
                        refuted=bool(np.max(np.abs(d2)) > 1e-6)),
               TB3=dict(table_and_eval_s=t1 - t0, full_map_cells_s=t2 - t1, verifier_tail_s=t3 - t2,
                        holds=bool(t1 - t0 < 180.0), refuted=bool(t1 - t0 > 600.0)))
    with open(os.path.join(a.out, "validate.json"), "w") as fp:
        json.dump(res, fp, indent=1)
    print(json.dumps(res, indent=1), flush=True)
    fs.use_style()
    import matplotlib.pyplot as plt
    x = -Rx.ravel()[idx] / sig_lin
    fig, ax = plt.subplots(1, 3, figsize=(fs.COLUMN_WIDTH * 3.0, 2.8))
    ax[0].plot(x, d1, ".", ms=1, color=fs.SERIES[0], alpha=0.4)
    ax[0].set_xlabel(r"$-\mathcal{R}^{\rm NR}/\sigma_{\rm lin}$ of the cell")
    ax[0].set_ylabel(r"$\Delta N_{\rm table}-\Delta N_{\rm rk4,4000}$")
    ax[0].axhline(0.0, **fs.GUIDE)
    ax[1].plot(x[tail], d2, ".", ms=1, color=fs.SERIES[1], alpha=0.4)
    ax[1].set_xlabel(r"$-\mathcal{R}^{\rm NR}/\sigma_{\rm lin}$ (tail cells)")
    ax[1].set_ylabel(r"$\zeta_{\rm table}-\zeta_{\rm verifier}$ (mean removed)")
    ax[1].axhline(0.0, **fs.GUIDE)
    u = phi - info["phi_mean"]
    w = v - info["v0"] - info["slope"] * u
    sub = np.random.default_rng(3).choice(u.size, 50000, replace=False)
    ax[2].plot(u[sub], w[sub], ".", ms=1, color=fs.SERIES[2], alpha=0.3)
    ax[2].set_xlabel(r"$u=\phi-\langle\phi\rangle$")
    ax[2].set_ylabel(r"$w=v-v_0-bu$ (band of the table)")
    fig.tight_layout()
    fs.save(fig, os.path.join(a.out, "fig_validate"))


if __name__ == "__main__":
    main()
