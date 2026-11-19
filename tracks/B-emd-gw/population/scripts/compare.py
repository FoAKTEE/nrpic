"""Checks of the predictions P3-P7 and P9 of JOURNAL.md from the analysis outputs.

    python3 compare.py     (reads ../results/analysis_{fid,amp2,nc4}.json; writes
                            $NRPIC_RUN_DIR/compare.json and pop_compare.png, copies)

P3  seed 2 against seed 1: halo counts at a = 30.
P4  amplitude doubled: in the matter era with growing-mode initial data the Newtonian
    evolution depends on sigma1 a only [BACKGROUND], so amp2 at a should match fid at 2a.
P5  32 against 64 cells (same modes): halos of >= 300 particles of the 64-cell run at
    a = 30 with a 32-cell halo within one 32-cell spacing; mass ratios of the pairs.
P6  nc = 4 against nc = 3.2: halo counts at a = 30.
P7  Layzer-Irvine constant.
P9  signal against amplitude at equal stage: amp2 at a against fid at 2a. Velocities
    scale as Hc delta/k, so at equal delta they are sqrt(2) larger in amp2 (Hc ~ a^-1/2),
    potentials 2 times: the radiated Omega should be 2^(7/2) = 11.3 times larger
    (sigma^(7/2), E/M ~ v^7, emitted at half the scale factor and compared at half the
    scale factor), the quasi-static one 2^4/2 = 8 times (Omega_qs ~ Phi^4 a) [JUDGEMENT].
"""
import json
import os
import shutil
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
PKG = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(ROOT, "python"))
from nrpic import figstyle as fs   # noqa: E402

L = 4.0


def load(tag):
    fn = os.path.join(PKG, "results", f"analysis_{tag}.json")
    return {r["name"]: r for r in json.load(open(fn))} if os.path.exists(fn) else {}


def cat_at(r, a, tol=0.04):
    c = min(r["catalogs"], key=lambda c: abs(c["a"] - a))
    return c if abs(c["a"] - a)/a < tol else None


def gw_at(r, a):
    rows = np.array(r["gw"]["rows"])
    i = int(np.argmin(np.abs(rows[:, 1] - a)))
    return rows[i]


def main():
    od = os.environ.get("NRPIC_RUN_DIR") or os.path.join(ROOT, "..", "..", "scratch",
                                                         "B-emd-gw", "tmp", "compare")
    os.makedirs(od, exist_ok=True)
    runs = {}
    for tag in ("fid", "amp2", "nc4"):
        runs.update(load(tag))
    out = {}
    fid = runs["fid"]
    c30 = cat_at(fid, 30)
    if "seed2" in runs:
        out["P3"] = {"fid_a30": c30["n_halos"], "seed2_a30": cat_at(runs["seed2"], 30)["n_halos"]}
    if "amp2" in runs:
        rows = []
        for c in runs["amp2"]["catalogs"]:
            cf = cat_at(fid, 2*c["a"])
            if cf is None:
                continue
            rows.append({"a_amp2": c["a"], "a_fid": cf["a"], "n_amp2": c["n_halos"],
                         "n_fid": cf["n_halos"],
                         "Mmax_amp2": max(c["masses"]) if c["masses"] else 0.0,
                         "Mmax_fid": max(cf["masses"]) if cf["masses"] else 0.0,
                         "fmass_amp2": c["f_mass_in_halos"], "fmass_fid": cf["f_mass_in_halos"]})
        out["P4"] = rows
        g = []
        for a in (5.0, 7.5, 10.0, 15.0, 20.0, 25.0, 30.0, 40.0, 50.0):
            ra, rf = gw_at(runs["amp2"], a), gw_at(fid, 2*a)
            g.append({"a_amp2": ra[1], "a_fid": rf[1], "rad_ratio": ra[8]/rf[8],
                      "qs_ratio": ra[9]/rf[9], "switchoff_ratio": ra[6]/rf[6]})
        out["P9"] = {"expected_rad": 2**3.5, "expected_qs": 8.0, "rows": g}
    if "n32" in runs:
        c32 = cat_at(runs["n32"], 30)
        big = [(np.array(x), M) for x, M, N in zip(c30["x"], c30["masses"], c30["N"])
               if N >= 300]
        pairs = []
        for x, M in big:
            if not c32["x"]:
                break
            d = [np.sqrt((((np.array(y) - x + L/2) % L - L/2)**2).sum()) for y in c32["x"]]
            j = int(np.argmin(d))
            pairs.append({"M64": M, "M32": c32["masses"][j], "d": d[j],
                          "matched": d[j] <= L/32})
        out["P5"] = {"n_big": len(big), "n_matched": sum(p["matched"] for p in pairs),
                     "pairs": pairs}
    if "nc4" in runs:
        out["P6"] = {"fid_a30": c30["n_halos"], "nc4_a30": cat_at(runs["nc4"], 30)["n_halos"]}
    out["P7"] = {k: r["layzer_irvine"]["max_abs_C_change_over_max_aW"] for k, r in runs.items()}
    with open(os.path.join(od, "compare.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    # figure
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.8))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.17, top=0.92, wspace=0.36)
    ax = axs[0]
    sty = {"fid": (fs.PAL["blue"], 1.0), "seed2": (fs.PAL["red"], 1.0),
           "amp2": (fs.PAL["green"], 2.0), "n32": (fs.PAL["yellow"], 1.0),
           "nc4": (fs.PAL["orange"], 1.0)}
    for k, r in runs.items():
        col, fac = sty.get(k, ("k", 1.0))
        a = np.array([c["a"] for c in r["catalogs"]])*fac
        ax.plot(a, [c["n_halos"] for c in r["catalogs"]], "-o", ms=3, color=col,
                label=k + (r" ($a\times 2$)" if fac != 1.0 else ""))
    ax.set_xscale("log")
    ax.set_xlabel(r"$a\,\sigma_1/0.0562$")
    ax.set_ylabel(r"halos ($\geq 100$ particles)")
    ax.legend(fontsize=7)
    ax = axs[1]
    if "amp2" in runs:
        rf = np.array(fid["gw"]["rows"])
        ra = np.array(runs["amp2"]["gw"]["rows"])
        ax.loglog(rf[1:, 1], rf[1:, 8], color=fs.PAL["blue"], label="fid, radiated")
        ax.loglog(2*ra[1:, 1], ra[1:, 8]/2**3.5, color=fs.PAL["green"], ls="--",
                  label=r"amp2 at $a/2$, $/2^{7/2}$")
        ax.loglog(rf[1:, 1], rf[1:, 9], color=fs.PAL["blue"], lw=1.0, ls=":",
                  label="fid, near field")
        ax.loglog(2*ra[1:, 1], ra[1:, 9]/8, color=fs.PAL["green"], lw=1.0, ls="-.",
                  label=r"amp2 near field $/8$")
        ax.set_ylim(1e-12, 1e-5)
    ax.set_xlabel(r"$a$ (fid)")
    ax.set_ylabel(r"$\rho_{\rm GW}/\bar\rho$")
    ax.legend(fontsize=7)
    ax = axs[2]
    if "P5" in out and out["P5"]["pairs"]:
        p = out["P5"]["pairs"]
        m64 = np.array([q["M64"] for q in p])
        m32 = np.array([q["M32"] for q in p])
        ok = np.array([q["matched"] for q in p])
        ax.loglog(m64[ok], m32[ok], "o", ms=4, color=fs.PAL["red"], label="matched")
        ax.loglog(m64[~ok], m32[~ok], "x", ms=4, color="grey", label="not matched")
        lim = [0.5*min(m64.min(), m32.min()), 2*max(m64.max(), m32.max())]
        ax.plot(lim, lim, **fs.GUIDE)
        ax.set_xlabel(r"$M$, 64 cells ($a = 30$)")
        ax.set_ylabel(r"$M$, nearest halo, 32 cells")
        ax.legend(fontsize=7)
    fs.save(fig, os.path.join(od, "pop_compare"))
    plt.close(fig)
    if os.environ.get("NRPIC_RUN_DIR"):
        shutil.copy(os.path.join(od, "compare.json"), os.path.join(PKG, "results"))
        shutil.copy(os.path.join(od, "pop_compare.png"), os.path.join(PKG, "figs"))
    print(json.dumps({k: v for k, v in out.items() if k != "P5"}, indent=1, default=float))
    if "P5" in out:
        print("P5", out["P5"]["n_big"], out["P5"]["n_matched"],
              [(round(q["M64"], 3), round(q["M32"], 3), round(q["d"], 3)) for q in out["P5"]["pairs"]])


if __name__ == "__main__":
    main()
