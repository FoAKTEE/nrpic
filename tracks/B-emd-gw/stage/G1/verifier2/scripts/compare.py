"""Comparison of the crossed-wave diagnostics (scan.py output) with the second-order
reference, the plane-symmetric null, linearity in eps, the two meshes and the two spatial
gauges (verifier2, my own code).

    python3 compare.py SCANDIR OUTDIR        (OUTDIR "-": $NRPIC_RUN_DIR)

Reference (derive_s.py, run B-20261119-140854-ec1f1c2): the + amplitude of h = tilde
gamma - delta at K1 = (k,k,0) obeys H'' + (4/eta) H' + K^2 H = K^2 s, K^2 = 2 k^2,
s = -(5/6) Phi_1 Phi_2, eta = t + 2 (a = eta^2/4 with a = 1, calH = 1 at t = 0).
Initial data: H(2) = 0 (conformally flat); H'(2) = 0, or the value measured from the TT
part of tilde A at t = 0 (zero shift: d_t tilde gamma = -2 alpha tilde A).
Phi_1 = -(3/2) delta / k^2 (dictionary of make_east.py, delta = 0.01, k = pi/2) and
Phi_2 = eps Phi_1; also measured: Phi from the sin(kx), sin(ky) amplitudes of alpha / <alpha>
in the first dump.
Writes OUTDIR/compare.json and the figures OUTDIR/{kk0_amplitude,null,res32_64,gauge}.{pdf,png}.
"""
import json
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle as fs  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

L = 4.0
k = 2*np.pi/L
K = np.sqrt(2.0)*k
DELTA = 0.01
PHI1 = -1.5*DELTA/k**2
EPS = {"eps0": 0.0, "eps0p1": 0.1, "eps0p3": 0.3, "eps1": 1.0, "eps1_gd": 1.0}


def load(scandir, label):
    with open(os.path.join(scandir, f"{label}.json")) as f:
        recs = json.load(f)["records"]
    out = {}
    for kind in ("bin", "rst"):
        r = [x for x in recs if x["kind"] == kind]
        out[kind] = r
    return out


def g_of_t(t, hp0=0.0):
    """H/s on eta = t + 2 with H(2) = 0, H'(2) = hp0 (in units of s)."""
    def rhs(eta, y):
        return [y[1], -4.0/eta*y[1] - K**2*(y[0] - 1.0)]
    eta = np.asarray(t) + 2.0
    sol = solve_ivp(rhs, (2.0, eta.max() + 1e-9), [0.0, hp0], method="DOP853", rtol=1e-12,
                    atol=1e-14, dense_output=True)
    return sol.sol(eta)[0]


def series(recs, key="h", mode="K1", comp=0):
    t = np.array([r["time"] for r in recs])
    c = np.array([r[key][mode][comp] for r in recs])
    return t, c


def a_of_t(t):
    return (1.0 + np.asarray(t)/2.0)**2


def main():
    scandir = sys.argv[1]
    outdir = sys.argv[2] if sys.argv[2] != "-" else os.environ["NRPIC_RUN_DIR"]
    os.makedirs(outdir, exist_ok=True)
    fs.use_style()
    res = {"Phi1_dictionary": PHI1, "K": K}
    D = {}
    for n in (64, 32):
        for e in EPS:
            D[(n, e)] = load(scandir, f"n{n}_{e}")

    # ---- amplitude against the reference, 64^3 and 32^3 ----
    amp = {}
    for n in (64, 32):
        for e in ("eps0p1", "eps0p3", "eps1", "eps1_gd"):
            eps = EPS[e]
            b = D[(n, e)]["bin"]
            t, c = series(b)
            _, d = series(b, comp=1)
            _, c2 = series(b, mode="K2")
            r0 = b[0]
            phi1m = r0["alpha_sin_x"]/r0["alpha_mean"]
            phi2m = r0["alpha_sin_y"]/r0["alpha_mean"]
            phi1c = r0["chi_sin_x"]/(2*r0["chi_mean"])
            phi2c = r0["chi_sin_y"]/(2*r0["chi_mean"])
            s_dict = -5.0/6.0*PHI1*PHI1*eps
            s_meas = -5.0/6.0*phi1m*phi2m
            cA0 = r0["A"]["K1"][0]
            hp0 = -2.0*cA0*r0["alpha_mean"]/s_dict
            g0 = g_of_t(t, 0.0)
            g1 = g_of_t(t, hp0)
            a = a_of_t(t)
            dev = (c - s_dict*g0)/abs(s_dict)
            dev_m = (c - s_meas*g0)/abs(s_meas)
            win = (a >= 2.0) & (a <= 10.0)
            sel = {}
            for at in (2, 3, 5, 10, 20, 30, 40, 60, 80, 100, 120, 140):
                i = int(np.argmin(np.abs(a - at)))
                sel[str(at)] = {"a": float(a[i]), "c_plus": float(c[i]), "c_over_s": float(c[i]/s_dict),
                                "g": float(g0[i]), "dev_pct": float(100*dev[i]),
                                "tt_box_fraction": b[i]["h"]["tt_box_fraction"]}
            amp[f"n{n}_{e}"] = {
                "eps": eps, "s_dictionary": s_dict, "s_measured_alpha": s_meas,
                "Phi1_alpha": phi1m, "Phi2_alpha": phi2m, "Phi1_chi": phi1c, "Phi2_chi": phi2c,
                "cA_plus_t0": cA0, "hprime0_over_s": hp0,
                "max_abs_dev_pct_a2_10": float(100*np.abs(dev[win]).max()),
                "max_abs_dev_pct_a2_10_s_measured": float(100*np.abs(dev_m[win]).max()),
                "max_abs_dev_pct_a2_10_with_hprime0": float(100*np.abs(((c - s_dict*g1)/abs(s_dict))[win]).max()),
                "max_abs_sin_part_over_s": float(np.abs(d/s_dict).max()),
                "max_abs_K1_plus_K2_over_s": float(np.abs((c + c2)/s_dict).max()),
                "at": sel,
            }
            if n == 64:
                D[(n, e)]["_ts"] = (t, c, g0, a, dev)
    res["amplitude"] = amp

    # ---- linearity in eps (64^3), c/eps against eps = 1 at the same dump index ----
    lin = {}
    t1, c1 = series(D[(64, "eps1")]["bin"])
    for e in ("eps0p1", "eps0p3"):
        t, c = series(D[(64, e)]["bin"])
        m = min(len(t), len(t1))
        assert np.allclose(t[:m], t1[:m], atol=1e-6), "dump times differ between eps"
        a = a_of_t(t[:m])
        rel = (c[:m]/EPS[e] - c1[:m])/np.abs(c1[:m])
        win = (a >= 2) & (a <= 10)
        lin[e] = {"max_abs_rel_a2_10": float(np.abs(rel[win]).max()),
                  "rel_at": {str(at): float(rel[int(np.argmin(np.abs(a - at)))])
                             for at in (10, 20, 40, 60, 80, 100, 140)}}
    res["linearity_vs_eps1"] = lin

    # ---- null (eps = 0) ----
    null = {}
    for n in (64, 32):
        for kind in ("bin", "rst"):
            r = D[(n, "eps0")][kind]
            if not r:
                continue
            null[f"n{n}_{kind}"] = {
                "ndumps": len(r), "a_max": float(a_of_t(r[-1]["time"])),
                "max_tt_amp_h": max(x["h"]["tt_max_amp"] for x in r),
                "max_tt_amp_A": max(x["A"]["tt_max_amp"] for x in r),
                "max_abs_K1_h": max(abs(x["h"]["K1"][0]) for x in r),
                "max_yy_zz_h": max(x["h"]["max_yy_zz"] for x in r),
                "max_yz_h": max(x["h"]["max_yz"] for x in r),
                "max_xy_h": max(x["h"]["max_xy"] for x in r),
                "max_yy_zz_A": max(x["A"]["max_yy_zz"] for x in r),
                "traceless_rms_h_first_last": [r[0]["h"]["traceless_rms"], r[-1]["h"]["traceless_rms"]],
            }
    res["null"] = null

    # ---- 32^3 against 64^3 ----
    rc = {}
    for e in ("eps0p1", "eps0p3", "eps1", "eps1_gd"):
        t6, c6 = series(D[(64, e)]["bin"])
        t3, c3 = series(D[(32, e)]["bin"])
        c3i = np.interp(t6, t3, c3)
        a = a_of_t(t6)
        rel = (c3i - c6)/np.abs(c6)
        rc[e] = {"rel_at": {str(at): float(rel[int(np.argmin(np.abs(a - at)))])
                            for at in (2, 5, 10, 20, 40, 60, 80, 100, 120, 140)},
                 "max_abs_rel_a_le_80": float(np.abs(rel[a <= 80]).max()),
                 "max_abs_rel_a_le_100": float(np.abs(rel[a <= 100]).max())}
        D[(64, e)]["_res"] = (a, c6, c3i, rel)
    res["res32_vs_64"] = rc

    # ---- two spatial gauges (raw, no correction) ----
    gg = {}
    for n in (64, 32):
        t0_, c0_ = series(D[(n, "eps1")]["bin"])
        tg, cg = series(D[(n, "eps1_gd")]["bin"])
        cgi = np.interp(t0_, tg, cg)
        a = a_of_t(t0_)
        s = -5.0/6.0*PHI1*PHI1
        rel = (cgi - c0_)/abs(s)
        gg[f"n{n}"] = {"raw_diff_over_s_at": {str(at): float(rel[int(np.argmin(np.abs(a - at)))])
                                              for at in (2, 5, 10, 20, 40, 60, 80, 100, 140)}}
        if n == 64:
            gauge_series = (a, c0_, cgi, rel)
    res["gauge_raw"] = gg

    with open(os.path.join(outdir, "compare.json"), "w") as f:
        json.dump(res, f, indent=1)

    # ---- figures ----
    col = {"eps0p1": fs.PAL["blue"], "eps0p3": fs.PAL["green"], "eps1": fs.PAL["red"],
           "eps1_gd": fs.PAL["orange"]}
    lab = {"eps0p1": r"$\epsilon=0.1$", "eps0p3": r"$\epsilon=0.3$", "eps1": r"$\epsilon=1$",
           "eps1_gd": r"$\epsilon=1$, $\Gamma$-driver"}
    fig, ax = plt.subplots(2, 1, figsize=(fs.FULL_WIDTH, 6.0), sharex=True)
    fig.subplots_adjust(left=0.11, right=0.97, bottom=0.09, top=0.97, hspace=0.06)
    s1 = -5.0/6.0*PHI1*PHI1
    for e in ("eps0p1", "eps0p3", "eps1"):
        t, c, g0, a, dev = D[(64, e)]["_ts"]
        ax[0].plot(a, c/EPS[e]/s1, color=col[e], label=lab[e] + r", $64^3$")
        ax[1].plot(a, 100*dev, color=col[e])
    t, c, g0, a, dev = D[(64, "eps1")]["_ts"]
    ax[0].plot(a, g0, **fs.GUIDE, label=r"$g(\eta)$, second order (own derivation)")
    ax[0].axhline(1.0, **fs.MASK_LINE)
    ax[0].set_ylabel(r"$c_+(k,k,0)\,/\,(\epsilon\, s_1)$")
    ax[0].set_xscale("log")
    ax[0].legend(loc="upper left", ncol=2)
    ax[0].set_ylim(-0.1, 2.8)
    ax[1].axhline(0.0, **fs.THIN)
    ax[1].axvspan(2, 10, color=fs.PAL["blue"], alpha=0.1)
    ax[1].set_yscale("symlog", linthresh=1.0)
    ax[1].set_ylabel(r"$(c_+ - s\,g)/|s|$ [%]")
    ax[1].set_xlabel(r"scale factor $a$ (homogeneous)")
    fs.save(fig, os.path.join(outdir, "kk0_amplitude"))
    plt.close(fig)

    fig, ax = plt.subplots(1, 1, figsize=(fs.FULL_WIDTH, 3.6))
    fig.subplots_adjust(left=0.11, right=0.97, bottom=0.14, top=0.96)
    for kind, ls in (("bin", "-"), ("rst", "o")):
        r = D[(64, "eps0")][kind]
        a = a_of_t([x["time"] for x in r])
        kw = dict(ls="-") if kind == "bin" else dict(ls="none", marker="o", ms=4)
        ax.plot(a, [x["h"]["tt_max_amp"] for x in r], color=fs.PAL["red"], **kw,
                label=r"max TT amplitude of $h$ (%s)" % kind)
        ax.plot(a, [x["A"]["tt_max_amp"] for x in r], color=fs.PAL["blue"], **kw,
                label=r"max TT amplitude of $\tilde A$ (%s)" % kind)
        if kind == "rst":
            ax.plot(a, [x["h"]["traceless_rms"] for x in r], color="k", ls="none", marker="s",
                    ms=3, label=r"rms traceless part of $h$ (rst)")
    ax.set_yscale("log")
    ax.set_xscale("log")
    ax.set_xlabel(r"scale factor $a$")
    ax.set_ylabel("amplitude")
    ax.legend(loc="center right", ncol=1)
    fs.save(fig, os.path.join(outdir, "null"))
    plt.close(fig)

    fig, ax = plt.subplots(2, 1, figsize=(fs.FULL_WIDTH, 5.5), sharex=True)
    fig.subplots_adjust(left=0.11, right=0.97, bottom=0.1, top=0.97, hspace=0.06)
    for e in ("eps0p1", "eps0p3", "eps1", "eps1_gd"):
        a, c6, c3i, rel = D[(64, e)]["_res"]
        ax[0].plot(a, c6/EPS[e]/s1, color=col[e], label=lab[e] + r" $64^3$")
        ax[0].plot(a, c3i/EPS[e]/s1, color=col[e], ls="--")
        ax[1].plot(a, 100*rel, color=col[e])
    ax[0].plot([], [], color="k", ls="--", label=r"$32^3$ (dashed)")
    ax[0].set_xscale("log")
    ax[0].set_ylabel(r"$c_+(k,k,0)/(\epsilon s_1)$")
    ax[0].legend(loc="upper left", ncol=2)
    ax[1].axhline(0.0, **fs.THIN)
    ax[1].set_yscale("symlog", linthresh=1.0)
    ax[1].set_ylabel(r"$(c_{32}-c_{64})/|c_{64}|$ [%]")
    ax[1].set_xlabel(r"scale factor $a$")
    fs.save(fig, os.path.join(outdir, "res32_64"))
    plt.close(fig)

    fig, ax = plt.subplots(1, 1, figsize=(fs.FULL_WIDTH, 3.4))
    fig.subplots_adjust(left=0.11, right=0.97, bottom=0.14, top=0.96)
    a, c0_, cgi, rel = gauge_series
    ax.plot(a, 100*rel, color=fs.PAL["red"], label=r"($\Gamma$-driver $-$ zero shift)$/|s|$, raw, $64^3$, $\epsilon=1$")
    ax.axhline(0.0, **fs.THIN)
    ax.set_xscale("log")
    ax.set_yscale("symlog", linthresh=0.1)
    ax.set_xlabel(r"scale factor $a$")
    ax.set_ylabel("[%]")
    ax.legend(loc="upper left")
    fs.save(fig, os.path.join(outdir, "gauge"))
    plt.close(fig)
    print(json.dumps({k_: v for k_, v in res.items() if k_ != "amplitude"}, indent=1)[:4000])
    for k_, v in amp.items():
        print(k_, {kk: v[kk] for kk in ("s_dictionary", "s_measured_alpha", "hprime0_over_s",
                                        "max_abs_dev_pct_a2_10", "max_abs_dev_pct_a2_10_s_measured",
                                        "max_abs_dev_pct_a2_10_with_hprime0")})
        print("   ", {at: round(x["dev_pct"], 3) for at, x in v["at"].items()})


if __name__ == "__main__":
    main()
