"""Gate reviewer's own check R of Track B, gate G2 (independent of the lead's analysis code).

    python3 review_check.py <outdir>

R-A  C7, growth rate of leg B (flrw_conv): from the raw line records <run>/east.line.bin
     (format from athenak/src/particles/nrpic_io.cpp NrpicWriteLine: records of 1 + 5 n
     doubles, time then chi, alpha, K, E, S_x at the n cells of the line), a least-squares fit
     E(x) = c0 + c1 sin kx + c2 cos kx per record, D = c1/c0, and the growth-rate error
     f - f_ref = d/d ln a [ln D - ln(a + 3/k^2)], estimated as the slope of a straight line over
     windows of width 0.5 in ln a. The reference f_ref = a/(a + 3/k^2) is the density contrast
     of linear Einstein-de Sitter dust in a slicing that is longitudinal at first order,
     delta propto (k^2/H_c^2 + 3) with H_c^2 = 1/a in units of the initial Hubble rate
     [BACKGROUND; the code's units of flrw_conv: a(t) = (1 + t/2)^2].
R-B  C7, scale factor of leg F: from <run>/flrw.nrpic.hst (columns by header name), the
     relative errors of alpha_min, alpha_max, (proper_volume/L^3)^(1/3) and (-mean_K/3)^(-2/3)
     against a(t) = (1 + t/2)^2, L from the cell centres of <run>/flrw.line.txt.
R-C  C2, particle-number leg of the band strain (8 against 1 particle per cell, 128^3, zero
     shift): band power sum_{1<=n<=8} S_n/n^2 of the corrected shell spectra in the analysis
     files (definition of compare_legs.py band_rms2), ratio of rms at matched a.
R-D  C2, gauge leg: the same band rms, Gamma-driver over zero shift, 128^3, at every dump.

Writes review_check.json and review_check.png into <outdir>.
"""
import json
import os
import sys

import numpy as np

ROOT = "/data/haiyangw/nrpic"
SCR = os.path.join(ROOT, "scratch/B-emd-gw")
sys.path.insert(0, os.path.join(ROOT, "python"))
from nrpic import figstyle as fs  # noqa: E402

LEG_B = {  # leg B runs named in tracks/B-emd-gw/flrw_conv/inputs/runs.json
    "b_n16_p1": "B-20261120-223006-24448ac/b_n16_p1",
    "b_n32_p1": "B-20261120-222955-c8e16e3/b_n32_p1",
    "b_n32_p2": "B-20261120-222955-c8e16e3/b_n32_p2",
    "b_n32_p3": "B-20261120-222955-c8e16e3/b_n32_p3",
    "b_n64_p1": "B-20261121-202304-dc3020e/b_n64_p1",
    "b_n128_p1": "B-20261121-202335-3e6a898",
}
LEG_F = {
    "f_n16_p1_a0": "B-20261120-223006-24448ac/f_n16_p1_a0",
    "f_n16_p1_a2": "B-20261120-223006-24448ac/f_n16_p1_a2",
    "f_n32_p1_a0": "B-20261120-222955-c8e16e3/f_n32_p1_a0",
    "f_n32_p1_a1": "B-20261120-222955-c8e16e3/f_n32_p1_a1",
    "f_n32_p1_a2": "B-20261120-222955-c8e16e3/f_n32_p1_a2",
    "f_n32_p2_a0": "B-20261120-222955-c8e16e3/f_n32_p2_a0",
    "f_n32_p2_a2": "B-20261120-222955-c8e16e3/f_n32_p2_a2",
    "f_n32_p3_a0": "B-20261120-222955-c8e16e3/f_n32_p3_a0",
    "f_n32_p3_a2": "B-20261120-222955-c8e16e3/f_n32_p3_a2",
    "f_n64_p1_a0": "B-20261121-202304-dc3020e/f_n64_p1_a0",
    "f_n64_p1_a2": "B-20261121-202304-dc3020e/f_n64_p1_a2",
}
BASE = "B-20261124-131918-e71996f/analysis_gr_s014.json"   # 128^3, 1 ppc, zero shift
P8 = "B-20261126-022838-27fab1b/analysis_gr_p8u.json"      # 128^3, 8 ppc, zero shift
GD = "B-20261125-115558-2ab4161/analysis_gr_gd.json"       # 128^3, 1 ppc, Gamma driver


def a_of_t(t):
    return (1.0 + 0.5*np.asarray(t))**2


def read_line(d, base):
    lines = open(os.path.join(d, f"{base}.line.txt")).read().split("\n")
    vals = [float(s) for s in lines[1:] if s.strip() and not s.startswith("#")]
    n = int(vals[0])
    x = np.array(vals[1:1 + n])
    raw = np.fromfile(os.path.join(d, f"{base}.line.bin"), dtype="<f8")
    m = len(raw)//(1 + 5*n)
    rec = raw[:m*(1 + 5*n)].reshape(m, 1 + 5*n)
    kept = []                      # a continued run repeats records from its restart time:
    for r in rec:                  # a record replaces every kept one at the same or later time
        while kept and kept[-1][0] >= r[0]:
            kept.pop()
        kept.append(r)
    rec = np.array(kept)
    return x, n, rec


def growth_check(d):
    x, n, rec = read_line(d, "east")
    L = n*(x[1] - x[0])
    k = 2*np.pi/L
    t = rec[:, 0]
    E = rec[:, 1 + 3*n:1 + 4*n]
    A = np.stack([np.ones(n), np.sin(k*x), np.cos(k*x)], axis=1)
    coef, *_ = np.linalg.lstsq(A, E.T, rcond=None)
    D = coef[1]/coef[0]
    a = a_of_t(t)
    g = np.log(D) - np.log(a + 3.0/k**2)
    la = np.log(a)
    centres = np.arange(np.log(3.0), la[-1] - 0.25, 0.05)
    df = []
    for c in centres:
        msk = np.abs(la - c) <= 0.25
        if msk.sum() < 5:
            df.append(np.nan)
            continue
        df.append(np.polyfit(la[msk], g[msk], 1)[0])
    df = np.array(df)
    early = (a >= 1.05) & (a <= 2.0)
    return {"L": float(L), "n": n, "records": int(len(t)), "a_end": float(a[-1]),
            "df_median": float(np.nanmedian(np.abs(df))), "df_max": float(np.nanmax(np.abs(df))),
            "drift_g_plateau": float(np.interp(la[-1] - 0.05, la, g) - np.interp(np.log(3.0), la, g)),
            "drift_g_early": float(g[early][-1] - g[early][0]) if early.sum() > 1 else float("nan"),
            "a_centres": np.exp(centres).tolist(), "df": df.tolist()}


def load_hst(path):
    names = None
    rows = []
    for line in open(path):
        if line.startswith("#"):
            if "[1]=" in line and names is None:
                names = [tok.split("=", 1)[1] for tok in line[1:].split() if "=" in tok]
            continue
        try:
            rows.append([float(v) for v in line.split()])
        except ValueError:
            pass
    ncol = len(names)
    arr = np.array([r for r in rows if len(r) == ncol])
    return {nm: arr[:, i] for i, nm in enumerate(names)}


def scale_check(d):
    h = load_hst(os.path.join(d, "flrw.nrpic.hst"))
    x = np.array([float(s) for s in open(os.path.join(d, "flrw.line.txt")).read().split("\n")[1:]
                  if s.strip() and not s.startswith("#")])
    n = int(x[0])
    L = n*(x[2] - x[1])
    t = h["time"]
    m = t > 0
    a = a_of_t(t[m])
    e = {"alpha_min": h["alpha_min"][m]/a - 1, "alpha_max": h["alpha_max"][m]/a - 1,
         "volume": (h["proper_volume"][m]/L**3)**(1/3)/a - 1,
         "mean_K": (-h["mean_K"][m]/3.0)**(-2.0/3.0)/a - 1}
    out = {f"max_{kk}": float(np.abs(v).max()) for kk, v in e.items()}
    out["max_all"] = max(out.values())
    out["a_end"] = float(a[-1])
    out["L"] = float(L)
    return out


def band(spec, nmax=8):
    s = np.asarray(spec, float)
    nn = np.arange(len(s))
    msk = (nn >= 1) & (nn <= nmax)
    return float((s[msk]/nn[msk]**2).sum())


def dumps(path):
    d = json.load(open(os.path.join(SCR, path)))
    return [(x["a"], band(x["spec_cor"]), band(x["spec_raw"])) for x in d["dumps"]
            if "spec_cor" in x]


def ratio(leg, base):
    out = []
    for a, bc, br in leg:
        j = int(np.argmin([abs(a - b[0]) for b in base]))
        ab, bbc, bbr = base[j]
        if abs(ab - a) > 0.01*a:
            continue
        out.append({"a": a, "a_base": ab, "rms_cor_ratio": float(np.sqrt(bc/bbc)),
                    "rms_raw_ratio": float(np.sqrt(br/bbr))})
    return out


def main():
    outdir = sys.argv[1]
    res = {"growth": {}, "scale": {}}
    for nm, sp in LEG_B.items():
        res["growth"][nm] = growth_check(os.path.join(SCR, sp))
    for nm, sp in LEG_F.items():
        res["scale"][nm] = scale_check(os.path.join(SCR, sp))
    base = dumps(BASE)
    res["particle_leg"] = ratio(dumps(P8), base)
    res["gauge_leg"] = ratio(dumps(GD), base)
    with open(os.path.join(outdir, "review_check.json"), "w") as f:
        json.dump(res, f, indent=1)
    for nm, g in res["growth"].items():
        print(f"{nm}: records {g['records']} a_end {g['a_end']:.1f} |df| median {g['df_median']:.3e}"
              f" max {g['df_max']:.3e} drift(3..end) {g['drift_g_plateau']:.3e}"
              f" drift(1.05..2) {g['drift_g_early']:.3e}")
    for nm, s in res["scale"].items():
        print(f"{nm}: a_end {s['a_end']:.1f} max_all {s['max_all']:.3e} " +
              " ".join(f"{k[4:]} {v:.2e}" for k, v in s.items() if k.startswith("max_") and k != "max_all"))
    for key in ("particle_leg", "gauge_leg"):
        print(key, " ".join(f"a={r['a']:.1f}:{r['rms_cor_ratio']:.4f}/{r['rms_raw_ratio']:.4f}"
                            for r in res[key]))

    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2, 2, figsize=(8, 6.4))
    plt.subplots_adjust(left=0.10, right=0.98, bottom=0.09, top=0.97, wspace=0.30, hspace=0.32)
    cols = fs.series_colors(6)
    for c, (nm, g) in zip(cols, res["growth"].items()):
        ax[0, 0].semilogy(g["a_centres"], np.abs(g["df"]), color=c, label=nm[2:])
    ax[0, 0].set_xscale("log")
    ax[0, 0].set_xlabel("a")
    ax[0, 0].set_ylabel(r"$|f - f_{\rm ref}|$ (window 0.5 in ln a)")
    ax[0, 0].legend(ncol=2, fontsize=8)
    mesh = [res["growth"][f"b_n{n}_p1"]["df_median"] for n in (16, 32, 64, 128)]
    ax[0, 1].loglog([16, 32, 64, 128], mesh, "o-", color=fs.PAL["red"], label="mesh, 1 per cell")
    ppc = [res["growth"][f"b_n32_p{p}"]["df_median"] for p in (1, 2, 3)]
    ax[0, 1].loglog([32, 32, 32], ppc, "s", color=fs.PAL["blue"], label="32 cells: 1, 8, 27 per cell")
    nn = np.array([16, 128])
    ax[0, 1].loglog(nn, mesh[0]*(nn/16.0)**-4, "k--", lw=1.0, label="fourth order")
    ax[0, 1].set_xlabel("cells per side")
    ax[0, 1].set_ylabel(r"median $|f - f_{\rm ref}|$, $a \geq 3$")
    ax[0, 1].legend(fontsize=8)
    names = list(res["scale"])
    ax[1, 0].semilogy(range(len(names)), [res["scale"][nm]["max_all"] for nm in names], "o",
                      color=fs.PAL["red"])
    ax[1, 0].set_xticks(range(len(names)))
    ax[1, 0].set_xticklabels([nm[2:] for nm in names], rotation=60, fontsize=7)
    ax[1, 0].axhline(1e-2, color="k", ls="--", lw=1.0)
    ax[1, 0].set_ylabel("largest relative error of a")
    for key, c, lab in (("particle_leg", fs.PAL["blue"], "8 / 1 per cell (zero shift)"),
                        ("gauge_leg", fs.PAL["red"], "Gamma driver / zero shift (1 per cell)")):
        rr = res[key]
        ax[1, 1].plot([r["a"] for r in rr], [r["rms_cor_ratio"] for r in rr], "o-", color=c, label=lab)
    ax[1, 1].axhline(1.0, color="k", ls="--", lw=1.0)
    ax[1, 1].set_xscale("log")
    ax[1, 1].set_xlabel("a")
    ax[1, 1].set_ylabel(r"band rms ratio, $|k| \leq 8 k_f$, 128$^3$")
    ax[1, 1].legend(fontsize=8)
    fig.savefig(os.path.join(outdir, "review_check.png"), dpi=150)


if __name__ == "__main__":
    main()
