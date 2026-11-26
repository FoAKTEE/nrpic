#!/usr/bin/env python3
"""Diagnostic of g3/JOURNAL.md entry 11: where the 1e-9 difference between the table and map_rk4 comes from.

    diag_table.py OUT --member <pilot member dir> --deck <usr_prod.athinput> --lead-json <zeta_tests.json> [--ncells 20000]

On ncells cells of the dump (every |R^NR| > 2.5 sigma_lin cell first, in random order, then random cells): (a) map_rk4
at 4000 steps, (b) at 16000, (c) the table (zeta_table.py) on 4000-step nodes, (d) on 16000-step nodes, (e) the
verifier's map (zv_lib, long double, h = 2e-3). Differences with their means removed. Writes OUT/diag.json, OUT/fig_diag.png.
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


def st(d):
    d = d - d.mean()
    return dict(max_abs=float(np.max(np.abs(d))), rms=float(np.sqrt(np.mean(d * d))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--member", required=True)
    ap.add_argument("--deck", required=True)
    ap.add_argument("--lead-json", required=True)
    ap.add_argument("--ncells", type=int, default=20000)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    L = json.load(open(a.lead_json))
    lam = RP.deck_value(a.deck, "scalar_field", "lambda")
    vev = RP.deck_value(a.deck, "scalar_field", "vev")
    dump = os.path.join(a.member, "usr.sf.00001.dump")
    Rx, _, _ = RP.RS.r_nr(dump, 1)
    sig_lin, _ = RP.RS.sigma_lin_of(dump[:-len(".dump")] + ".modes", Rx.shape[0])
    rng = np.random.default_rng(12)
    tail = np.nonzero(np.abs(Rx.ravel()) > 2.5 * sig_lin)[0]
    rest = np.setdiff1d(np.arange(Rx.size), tail)
    idx = np.concatenate([rng.permutation(tail), rng.permutation(rest)])[:a.ncells]
    _, g = RP.fl.ll.read_dump(dump, ["phi", "Pi", "chi", "K"])
    phi = g["phi"].ravel()
    v = (g["Pi"] / (-g["K"] / 3.0)).ravel()
    src = os.path.join(TRK, "zeta", "zeta_reader.py")
    ns4 = RP.lead_namespace(src, lam, vev, L["phi_e"], 4000)
    ns16 = RP.lead_namespace(src, lam, vev, L["phi_e"], 16000)
    t = {}
    t0 = time.time(); A = ns4["map_rk4"](phi[idx], v[idx]); t["a"] = time.time() - t0
    t0 = time.time(); B = ns16["map_rk4"](phi[idx], v[idx]); t["b"] = time.time() - t0
    t0 = time.time(); C = ZT.table_map(ns4["map_rk4"], phi, v)[0][idx]; t["c"] = time.time() - t0
    t0 = time.time(); D, info = ZT.table_map(ns16["map_rk4"], phi, v); D = D[idx]; t["d"] = time.time() - t0
    f, head = Z.read_dump(dump)
    hdr = Z.read_modes_header(dump[:-len(".dump")] + ".modes")
    pot = Z.Inflection(lam, vev)
    phi_b, Pi_b, lna, Hl = LD(hdr["phi_b"]), LD(hdr["Pi_b"]), LD(hdr["ln_a"]), LD(hdr["H"])
    phi_e_v, _ = Z.integrate_to_N(pot, phi_b, Pi_b / Hl, LD(15) - lna, 1e-3)
    y = -3 * f["Pi"].ravel()[idx].astype(LD) / f["K"].ravel()[idx].astype(LD)
    t0 = time.time()
    E = np.asarray(Z.efolds_to_surface(pot, f["phi"].ravel()[idx].astype(LD), y, phi_e_v, 2e-3), dtype=float)
    t["e"] = time.time() - t0
    res = dict(member=a.member, n_cells=int(idx.size), n_tail=int(min(tail.size, idx.size)), wall_s=t, table=info,
               c_a=st(C - A), d_b=st(D - B), b_a=st(B - A), a_e=st(A - E), b_e=st(B - E), c_e=st(C - E), d_e=st(D - E))
    p = res
    res["prediction"] = dict(step_error_cause=bool(p["b_e"]["rms"] < 1e-10 and p["d_e"]["rms"] < 1e-10 and p["d_b"]["rms"] < 1e-10),
                             interpolation_cause=bool(p["d_b"]["rms"] > 3e-10),
                             table16_bar=bool(p["d_b"]["max_abs"] <= 1e-9 and p["d_e"]["max_abs"] <= 4.3e-9))
    with open(os.path.join(a.out, "diag.json"), "w") as fp:
        json.dump(res, fp, indent=1)
    print(json.dumps(res, indent=1), flush=True)
    fs.use_style()
    import matplotlib.pyplot as plt
    x = -Rx.ravel()[idx] / sig_lin
    fig, ax = plt.subplots(1, 3, figsize=(fs.COLUMN_WIDTH * 3.0, 2.8))
    for k, (lab, d) in enumerate((("table4000 - rk4(4000)", C - A), ("table16000 - rk4(16000)", D - B),
                                  ("rk4(16000) - rk4(4000)", B - A))):
        ax[0].plot(x, d - d.mean(), ".", ms=1, alpha=0.4, color=fs.SERIES[k], label=lab)
    ax[0].set_xlabel(r"$-\mathcal{R}^{\rm NR}/\sigma_{\rm lin}$")
    ax[0].set_ylabel(r"difference in $\Delta N$")
    ax[0].legend(fontsize=5, markerscale=5)
    for k, (lab, d) in enumerate((("rk4(4000) - verifier", A - E), ("rk4(16000) - verifier", B - E),
                                  ("table16000 - verifier", D - E))):
        ax[1].plot(x, d - d.mean(), ".", ms=1, alpha=0.4, color=fs.SERIES[k], label=lab)
    ax[1].set_xlabel(r"$-\mathcal{R}^{\rm NR}/\sigma_{\rm lin}$")
    ax[1].legend(fontsize=5, markerscale=5)
    o = np.argsort(phi[idx])
    ax[2].plot(phi[idx][o] - info["phi_mean"], (A - E)[o] - (A - E).mean(), ".", ms=1, color=fs.SERIES[0])
    ax[2].set_xlabel(r"$u=\phi-\langle\phi\rangle$")
    ax[2].set_ylabel("rk4(4000) - verifier")
    fig.tight_layout()
    fs.save(fig, os.path.join(a.out, "fig_diag"))


if __name__ == "__main__":
    main()
