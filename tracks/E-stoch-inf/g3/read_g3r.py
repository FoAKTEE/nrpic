#!/usr/bin/env python3
"""G3-R of SCOPE 4d.5 with 4d.9 A7: Richardson in the square of the amplitude, 128^3 against 160^3.

    read_g3r.py OUT --r128 <G3C run dir> --r160 <G3R run dir> [--seed 20262000] [--kmax 16]

Members at N_f (last dump): 128^3 c_p1, c_m1, c_ph, c_mh (G3C run), 160^3 r_p1, r_m1, r_ph, r_mh (G3R run).
Per mode (|n|^2 <= 1024, the coefficients of R^NR of card_lib.Extractor.curvature, linear chi part, the reader of
G2): O(s) = [c(+s) - c(-s)]/2, L = [8 O(1/2) - O(1)]/3, T = [O(1) - 2 O(1/2)] 4/3. Reference cref_n = L^-3/2 W_n
R_n alpha_n (card_lib.ShellReference on modes_usr_n1024.txt, alpha_n of rng_seed --seed, usr_reference.json code
inputs). D^L_n = |L_n/cref_n - 1| on modes with |n| <= kmax (k_max/2). Criterion (4d.5 + A7): max D^L(128)/max
D^L(160) in [2.0, 4.5]; the median over modes of D^L_n(128)/D^L_n(160) in [2.0, 4.5]; the sign of
Re(L_n/cref_n - 1) the same at both resolutions for >= 90 per cent of the modes (the scope's "sign" for a complex
ratio: its real part, stated here before the reading; the imaginary part is reported). Reported: the same for
O(1) alone (the G2 form), the change of T between resolutions (rms |T160 - T128| / rms |T128|).
Writes OUT/g3r.json and OUT/fig_g3r.{png,pdf}.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TRK = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(TRK, "usr", "scripts"))
import card_lib as cl  # noqa: E402
import usr_lib as ul  # noqa: E402
import figstyle as fs  # noqa: E402

MODEFILE = os.path.join(TRK, "usr", "inputs", "modes_usr_n1024.txt")
NMAX2 = 1024


def coeffs(rundir, prefix, seed, workers):
    out, t, N = {}, None, None
    for k in ("p1", "m1", "ph", "mh"):
        p = cl.dump_list(os.path.join(rundir, prefix + k))[-1]
        h, f = cl.read_fields(p, cl.CURV)
        if t is None:
            t, N = h["time"], h["nx"][0]
        elif abs(h["time"] - t) > 1e-12:
            raise SystemExit(f"{p}: time {h['time']} differs from {t}")
        modes = ul.Modes(N, NMAX2)
        out[k] = cl.Extractor(modes, workers).curvature(f)["lin"]
        del f
    modes = ul.Modes(N, NMAX2)
    return out, t, N, modes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--r128", required=True)
    ap.add_argument("--r160", required=True)
    ap.add_argument("--seed", type=int, default=20262000)
    ap.add_argument("--kmax", type=float, default=16.0)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    ci = json.load(open(os.path.join(TRK, "usr", "results", "usr_reference.json")))["code_inputs"]
    R = {}
    for lab, d, pre in (("128", a.r128, "c_"), ("160", a.r160, "r_")):
        c, t, N, modes = coeffs(d, pre, a.seed, a.workers)
        alpha = modes.alpha(seed=a.seed)
        sref = cl.ShellReference(ci, MODEFILE, NMAX2, [t])
        cref, st = sref.modes_ref(modes, alpha, 0)
        O1 = 0.5 * (c["p1"] - c["m1"])
        Oh = 0.5 * (c["ph"] - c["mh"])
        L = (8.0 * Oh - O1) / 3.0
        T = (O1 - 2.0 * Oh) * 4.0 / 3.0
        R[lab] = dict(N=N, t=t, modes=modes, cref=cref, O1=O1, Oh=Oh, L=L, T=T, cN=float(st["lna"]))
        print(f"{lab}: N={N} t={t:.6f} cN={st['lna']:.4f} modes={modes.M}", flush=True)
    m = R["128"]["modes"]
    assert np.array_equal(m.n, R["160"]["modes"].n)
    sel = m.k <= a.kmax + 1e-9
    V = dict(kmax=a.kmax, n_modes=int(sel.sum()), t=R["128"]["t"], cN=R["128"]["cN"])
    for form in ("L", "O1"):
        dev = {lab: R[lab][form][sel] / R[lab]["cref"][sel] - 1.0 for lab in R}
        D = {lab: np.abs(dev[lab]) for lab in R}
        per = D["128"] / D["160"]
        same = np.sign(dev["128"].real) == np.sign(dev["160"].real)
        same_im = np.sign(dev["128"].imag) == np.sign(dev["160"].imag)
        V[form] = dict(max128=float(D["128"].max()), max160=float(D["160"].max()),
                       factor_max=float(D["128"].max() / D["160"].max()),
                       median128=float(np.median(D["128"])), median160=float(np.median(D["160"])),
                       median_of_ratio=float(np.median(per)), sign_same_re=float(same.mean()),
                       sign_same_im=float(same_im.mean()))
    Tc = R["160"]["T"][sel] - R["128"]["T"][sel]
    V["T_change"] = float(np.sqrt(np.mean(np.abs(Tc)**2)) / np.sqrt(np.mean(np.abs(R["128"]["T"][sel])**2)))
    V["T_over_L_rms128"] = float(np.sqrt(np.mean(np.abs(R["128"]["T"][sel])**2) /
                                         np.mean(np.abs(R["128"]["L"][sel])**2)))
    L_ = V["L"]
    V["clauses"] = dict(factor_max=bool(2.0 <= L_["factor_max"] <= 4.5),
                        median_of_ratio=bool(2.0 <= L_["median_of_ratio"] <= 4.5),
                        sign=bool(L_["sign_same_re"] >= 0.9))
    V["verdict"] = "PASS" if all(V["clauses"].values()) else "FAIL"
    V["prediction_entry4"] = dict(factor_max_in_2p3_4p0=bool(2.3 <= L_["factor_max"] <= 4.0),
                                  median_in_2p3_4p0=bool(2.3 <= L_["median_of_ratio"] <= 4.0),
                                  sign_gt_0p9=bool(L_["sign_same_re"] > 0.9),
                                  T_change_below_0p1=bool(V["T_change"] < 0.1))
    with open(os.path.join(a.out, "g3r.json"), "w") as fp:
        json.dump(V, fp, indent=1)
    np.savez_compressed(os.path.join(a.out, "g3r_modes.npz"), n=m.n, k=m.k,
                        **{f"{f}_{lab}": R[lab][f] for lab in R for f in ("cref", "O1", "Oh", "L", "T")})
    print(json.dumps(V, indent=1))
    figure(R, sel, V, os.path.join(a.out, "fig_g3r"))


def figure(R, sel, V, path):
    import matplotlib.pyplot as plt
    k = R["128"]["modes"].k[sel]
    fig, ax = plt.subplots(1, 3, figsize=(10.5, 3.3))
    for lab, col in (("128", fs.PAL["blue"]), ("160", fs.PAL["red"])):
        for form, mk in (("L", "o"), ("O1", "x")):
            d = np.abs(R[lab][form][sel] / R[lab]["cref"][sel] - 1.0)
            ax[0].semilogy(k + (0.1 if lab == "160" else 0), d, mk, ms=2, color=col, alpha=0.4,
                           label=f"{lab}$^3$ {'$D^L$' if form == 'L' else '$D$ of $O(1)$'}")
    ax[0].set_xlabel(r"$|n|$")
    ax[0].set_ylabel("deviation from the reference")
    per = np.abs(R["128"]["L"][sel] / R["128"]["cref"][sel] - 1) / np.abs(R["160"]["L"][sel] / R["160"]["cref"][sel] - 1)
    ax[1].hist(np.log10(per), bins=60, color=fs.PAL["green"])
    for x in (2.0, 4.5):
        ax[1].axvline(np.log10(x), color="k", lw=0.8, ls="--")
    ax[1].axvline(np.log10(V["L"]["median_of_ratio"]), color=fs.PAL["red"], lw=1.2)
    ax[1].set_xlabel(r"$\log_{10} D^L_n(128)/D^L_n(160)$")
    ax[1].set_ylabel("modes")
    for lab, col in (("128", fs.PAL["blue"]), ("160", fs.PAL["red"])):
        ax[2].semilogy(k, np.abs(R[lab]["T"][sel] / R[lab]["cref"][sel]), ".", ms=2, color=col, alpha=0.4,
                       label=f"|T/cref| {lab}$^3$")
    ax[2].set_xlabel(r"$|n|$")
    for x in (ax[0], ax[2]):
        x.legend(fontsize=6)
    fig.suptitle(f"G3-R: factor of max {V['L']['factor_max']:.2f}, median of ratio {V['L']['median_of_ratio']:.2f}, "
                 f"sign agreement {V['L']['sign_same_re']:.2f}", fontsize=8)
    fig.tight_layout()
    fs.save(fig, path)


if __name__ == "__main__":
    main()
