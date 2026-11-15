"""Figures of the lead's wave-2 review (R1-R9 of ../JOURNAL.md), style python/nrpic/figstyle.py.

    rv_plots.py FIRST_SOURCE_RUN_DIR NEWTON_RUN_DIR [OUTDIR]

rv_review_first_source.png: top left, c_+(K1)/s for eps = 0.1, 0.3, 1 at 64^3 (lead's own
reading of the dumps) and the second-order reference g(tau); top right, |c_+/(s g) - 1|;
bottom left, difference between the zero-shift and Gamma-driver runs, raw and after the
helper's G_tot, in units of |s|; bottom right, |c_+(32^3)/c_+(64^3) - 1|.
rv_review_newton.png: left, measured/predicted (H1) largest sheet error against a for
n = 16, 32, 64; right, |t_x - t_x(Richardson)| and |E/M - E/M(Richardson)| against N.
Also prints the junk envelope |g - 1| at a = 60 from the lead's g(tau) (check of verifier C3).
"""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

WT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 5))
sys.path.insert(0, os.path.join(WT, "python"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nrpic import figstyle as fs  # noqa: E402
import rv_first_source as rv  # noqa: E402


def main():
    fsdir, nwdir = sys.argv[1], sys.argv[2]
    out = sys.argv[3] if len(sys.argv) > 3 else os.environ["NRPIC_RUN_DIR"]
    os.makedirs(out, exist_ok=True)
    fs.use_style()
    D = json.load(open(f"{fsdir}/rv_first_source.json"))
    S, ser = D["summary"], D["series"]

    # junk envelope from the lead's g(tau): max |g - 1| over one period around a = 60
    tau = np.linspace(0, 30, 300001)
    a = (1 + tau / 2) ** 2
    g = rv.g_of_tau(tau)
    per = 2 * np.pi / rv.KK
    t60 = 2 * (np.sqrt(60.0) - 1)
    sel = np.abs(tau - t60) <= per / 2
    env60 = float(np.max(np.abs(g[sel] - 1)))
    print(f"junk envelope |g-1| near a = 60 (one period): {env60:.5f}")

    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 6.2))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.08, top=0.97, wspace=0.28, hspace=0.25)
    cols = {"eps0p1": fs.PAL["yellow"], "eps0p3": fs.PAL["red"], "eps1": fs.PAL["blue"]}
    labs = {"eps0p1": r"$\epsilon = 0.1$", "eps0p3": r"$\epsilon = 0.3$", "eps1": r"$\epsilon = 1$"}
    ax, ax2 = axs[0]
    for cs in ("eps0p1", "eps0p3", "eps1"):
        rows = ser[f"64/{cs}"]
        t = np.array([r["time"] for r in rows]); aa = (1 + t / 2) ** 2
        c = np.array([r["K1"][0] for r in rows]); s = S["cases"][f"64/{cs}"]["s"]
        gg = rv.g_of_tau(t)
        ax.plot(aa, c / s, color=cols[cs], label=labs[cs])
        ax2.plot(aa[1:], np.abs(c[1:] / (s * gg[1:]) - 1), color=cols[cs], label=labs[cs])
    ax.plot(a[a <= 140], g[a <= 140], label=r"$g(\tau)$, second order", **fs.GUIDE)
    ax.set_xscale("log"); ax.set_xlabel(r"$a$"); ax.set_ylabel(r"$c_+(K_1)/s$, 64$^3$")
    ax.legend(loc="upper left", ncol=1)
    ax2.set_xscale("log"); ax2.set_yscale("log"); ax2.set_xlabel(r"$a$")
    ax2.set_ylabel(r"$|c_+/(s\,g) - 1|$")
    ax2.axvspan(2, 10, color="grey", alpha=0.1)
    ax2.axhline(5e-3, **fs.MASK_LINE)
    ax2.legend(loc="upper left")
    ax3, ax4 = axs[1]
    for N, col in (("64", fs.PAL["blue"]), ("32", fs.PAL["red"])):
        P = S[f"P6_{N}_series"] if f"P6_{N}_series" in S else None
        if P is None:
            continue
        aa = np.array(P["a"]); s1 = abs(S["s_eps1"])
        ax3.plot(aa, np.abs(P["raw"]) / s1, color=col, label=f"raw, {N}$^3$")
        ax3.plot(aa, np.abs(P["corr"]) / s1, color=col, ls="--", label=f"after $G_{{tot}}$, {N}$^3$")
    ax3.set_xscale("log"); ax3.set_yscale("log"); ax3.set_xlabel(r"$a$")
    ax3.set_ylabel(r"$|\Delta c_+|/|s|$, zero shift vs Gamma driver")
    ax3.legend(loc="upper left", ncol=2, fontsize="small"); ax3.set_ylim(1e-7, 3)
    for cs in ("eps0p1", "eps0p3", "eps1"):
        r64, r32 = ser[f"64/{cs}"], ser[f"32/{cs}"]
        t64 = np.array([r["time"] for r in r64]); t32 = np.array([r["time"] for r in r32])
        c64 = np.array([r["K1"][0] for r in r64])
        c32 = np.interp(t64, t32, np.array([r["K1"][0] for r in r32]))
        aa = (1 + t64 / 2) ** 2
        ax4.plot(aa[1:], np.abs(c32[1:] / c64[1:] - 1), color=cols[cs], label=labs[cs])
    ax4.set_xscale("log"); ax4.set_yscale("log"); ax4.set_xlabel(r"$a$")
    ax4.set_ylabel(r"$|c_+(32^3)/c_+(64^3) - 1|$")
    ax4.axhline(1e-3, **fs.MASK_LINE); ax4.legend(loc="upper left")
    fs.save(fig, f"{out}/rv_review_first_source")

    R = json.load(open(f"{nwdir}/rv_newton.json"))
    fig, (b1, b2) = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.15, top=0.96, wspace=0.3)
    for n, col in (("16", fs.PAL["yellow"]), ("32", fs.PAL["red"]), ("64", fs.PAL["blue"])):
        v = R["R7"][n]
        b1.plot(v["a"], v["meas_over_pred_lead"], "o-", color=col, label=f"n = {n}")
    b1.axhline(1.0, **fs.GUIDE); b1.axhspan(0.98, 1.02, color="grey", alpha=0.15)
    b1.set_xlabel(r"$a$"); b1.set_ylabel("measured / H1 (lead's integration)")
    b1.legend(loc="upper left")
    Ns = np.array([32, 64, 128])
    p_t, tinf = R["R8"]["richardson_t_x"]; p_e, einf = R["R8"]["richardson_E_over_M"]
    tx = np.array([R["R8"][str(n)]["t_x"] for n in Ns])
    em = np.array([R["R8"][str(n)]["E_over_M"] for n in Ns])
    b2.loglog(Ns, np.abs(tx - tinf) / tinf, "o-", color=fs.PAL["blue"],
              label=r"$|t_x - t_\infty|/t_\infty$, order %.2f" % p_t)
    b2.loglog(Ns, np.abs(em - einf) / einf, "s-", color=fs.PAL["red"],
              label=r"$|E - E_\infty|/E_\infty$, order %.2f" % p_e)
    b2.set_xlabel("cells per side $N$"); b2.set_ylabel("distance from Richardson value")
    b2.set_xticks(Ns); b2.set_xticklabels([str(n) for n in Ns]); b2.minorticks_off()
    b2.legend(loc="lower left")
    fs.save(fig, f"{out}/rv_review_newton")
    json.dump({"junk_envelope_a60": env60}, open(f"{out}/rv_plots.json", "w"))


if __name__ == "__main__":
    main()
