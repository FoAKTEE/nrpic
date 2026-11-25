#!/usr/bin/env python3
"""Lead's own check of finding B1 of g3/scope_review/SCOPE_REVIEW.md (batch 19).

    python3 bins_lead.py OUTDIR

The lattice-density variant of the one-patch reference (langevin/scripts/ref_spec.py,
lattice_factor_fn) multiplies the noise variance of the modes crossing at ln n by
r_i = C_i / V_i, C_i the number of integer vectors with |n| in bin i (0.05 wide in ln n),
V_i = 4 pi/3 (hi^3 - lo^3) the continuum volume of the bin. The band ends at |n| = NLAT.
In the linear limit the variant's variance is sum_i r_i int_{bin i, ln n <= ln NLAT} P(ln n) dln n,
the lattice sum is sum_{0 < |n| <= NLAT} P(|n|) / (4 pi |n|^3).

This script does not use ref_bins.py, ref_spec.py or lattice_shell_counts: its own integer-vector
count (bincount of n^2), its own bins (same rule as ref_spec, written again), and two weights:
(a) P = 1 (scale invariant; pure lattice geometry, no reference code at all), (b) the band's linear
P_R at N_e from sdn.linear.PR_late (the reference's linear module; the defect is not in it).
For each it reports the variant/lattice ratio as ref_spec builds the bins ("as is") and with the
top bin's volume truncated at NLAT ("fixed"), the top bin's factor both ways, and the top bin's
share of the band variance.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "python"))
sys.path.insert(0, os.path.join(WT, "tracks", "E-stoch-inf", "langevin"))
from nrpic import figstyle  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
W = 0.05


def shells(nlat):
    r = np.arange(-nlat, nlat + 1)
    n2 = (r[:, None, None] ** 2 + r[None, :, None] ** 2 + r[None, None, :] ** 2).ravel()
    cnt = np.bincount(n2, minlength=nlat * nlat + 1)[: nlat * nlat + 1]
    cnt[0] = 0
    m = np.nonzero(cnt)[0]
    return np.sqrt(m.astype(float)), cnt[m]


def bins(nlat, fixed):
    nb = int(np.floor(np.log(nlat) / W + 1e-12)) + 1     # bins whose lower edge is <= ln nlat
    lo = np.exp(W * np.arange(nb))
    hi = np.exp(W * np.arange(1, nb + 1))
    if fixed:
        hi = np.minimum(hi, nlat)
    return lo, hi


def ratios(nlat, Pfun, fixed):
    n, c = shells(nlat)
    lo, hi = bins(nlat, fixed)
    idx = np.floor(np.log(n) / W + 1e-12).astype(int)
    C = np.bincount(idx, weights=c, minlength=len(lo))[: len(lo)]
    r = C / (4 * np.pi / 3 * (hi ** 3 - lo ** 3))
    v_lat = float(np.sum(c * Pfun(n) / (4 * np.pi * n ** 3)))
    v_var, v_cont, top = 0.0, 0.0, 0.0
    for i in range(len(lo)):
        a, b = np.log(lo[i]), min(np.log(lo[i]) + W, np.log(nlat))
        x = np.linspace(a, b, 201)
        I = np.trapezoid(Pfun(np.exp(x)), x)
        v_var += r[i] * I
        v_cont += I
        if i == len(lo) - 1:
            top = I
    return dict(var_over_lattice=v_var / v_lat, lattice_over_cont=v_lat / v_cont,
                top_factor=float(r[-1]), top_bin=[float(np.log(lo[-1])), float(np.log(lo[-1]) + W)],
                top_share_of_cont=top / v_cont, nbins=len(lo), r=r.tolist(),
                lnlo=np.log(lo).tolist())


def pr_band(nlat):
    from sdn import models, linear
    model = models.HiggsInflection()
    phi0 = -1.2
    dpdN, _ = models.h0_fixing(model, phi0)
    bg = linear.ClassicalBackground(model, phi0, dpdN, N0=0.0, Nstar=3.0, N_extra=250.0)
    kmin = bg.aH(3.0)
    x = np.linspace(0.0, np.log(nlat), 121)
    P = np.array(linear.PR_late(bg, kmin * np.exp(x), 18.0))
    return lambda n: np.exp(np.interp(np.log(n), x, np.log(P)))


res = {}
for nlat in (32, 64):
    flat = lambda n: np.ones_like(np.asarray(n, dtype=float))
    pr = pr_band(nlat)
    res[str(nlat)] = {w: {k: ratios(nlat, f, fx) for k, fx in (("as_is", False), ("fixed", True))}
                      for w, f in (("flat", flat), ("PR_Ne", pr))}
    for w in ("flat", "PR_Ne"):
        d = res[str(nlat)][w]
        print(nlat, w, "as_is", round(d["as_is"]["var_over_lattice"], 5), "fixed",
              round(d["fixed"]["var_over_lattice"], 5), "top factor", round(d["as_is"]["top_factor"], 4),
              round(d["fixed"]["top_factor"], 4), "top share", round(d["as_is"]["top_share_of_cont"], 4),
              flush=True)

slim = {n: {w: {k: {kk: vv for kk, vv in v.items() if kk not in ("r", "lnlo")} for k, v in d.items()}
            for w, d in dd.items()} for n, dd in res.items()}
with open(os.path.join(OUT, "bins_lead.json"), "w") as f:
    json.dump(slim, f, indent=1)

figstyle.use_style()
fig = plt.figure(figsize=(figstyle.FULL_WIDTH, 3.0))
a1 = figstyle.inch_axes(fig, 0.75, 0.55, 3.0, 2.2)
a2 = figstyle.inch_axes(fig, 4.75, 0.55, 3.0, 2.2)
cols = {"32": figstyle.PAL["blue"], "64": figstyle.PAL["red"]}
for n, dd in res.items():
    for k, ls, mk in (("as_is", "-", "o"), ("fixed", ":", "s")):
        d = dd["PR_Ne"][k]
        x = np.array(d["lnlo"]) + W / 2
        a1.plot(x, d["r"], ls=ls, marker=mk, ms=2.5, color=cols[n],
                label=f"$|n|\\leq{n}$, {'as in ref_spec' if k == 'as_is' else 'top bin cut at NLAT'}")
    a1.axvline(np.log(int(n)), color=cols[n], lw=0.8, ls="--")
a1.axhline(1.0, **figstyle.THIN)
a1.set_xlim(2.4, 4.3)
a1.set_ylim(0.0, 1.3)
a1.set_xlabel("$\\ln|n|$ (bin centre)")
a1.set_ylabel("lattice factor $r_i=C_i/V_i$")
a1.legend(loc="lower left", fontsize=6)
labels, xs = [], []
for j, (n, w) in enumerate([("32", "flat"), ("32", "PR_Ne"), ("64", "flat"), ("64", "PR_Ne")]):
    for k, off, c in (("as_is", -0.12, figstyle.PAL["orange"]), ("fixed", 0.12, figstyle.PAL["green"])):
        a2.plot(j + off, res[n][w][k]["var_over_lattice"], "o", color=c,
                label=("as in ref_spec" if k == "as_is" else "top bin cut at NLAT") if j == 0 else None)
    labels.append(f"{n}, {'P=1' if w == 'flat' else '$P_R(N_e)$'}")
    xs.append(j)
a2.axhline(1.0, **figstyle.GUIDE)
a2.set_xticks(xs)
a2.set_xticklabels(labels, fontsize=7)
a2.set_ylabel("variant / lattice sum (linear)")
a2.legend(loc="lower right", fontsize=7)
figstyle.save(fig, os.path.join(OUT, "fig_bins_lead"))
print("wrote", OUT)
