#!/usr/bin/env python3
"""Health and mirror checks of the 32^3 mirrored pairs (zeta/JOURNAL.md entry 1, P1-P2), and a preview
of the second order of the linear variable R_lin = (H/Pi) dphi on the pairs (not a criterion: Z0-Z2 judge
zeta once the reader exists).

    python3 pairs_check.py OUT --run <dir of E-20261125-153148-cfad424>

Per pair (zp4/zm4 at s = 1/4, zp2/zm2 at s = 1/2), last dump of each member (equal times required):
P2: |<phi>(+) - <phi>(-)| / rms(phi(+) - phi(-)). Odd part O = [X(+) - X(-)]/2 and even part
E = [X(+) + X(-)]/2 - <.> of X = R_lin; a = slope of E on O^2 - <O^2> (least squares); a s-independent
coefficient in R = O + a (O^2 - <O^2>) means a(1/4) = a(1/2) when O is measured at each s.
Also: skewness of dphi per member, finite-field check. Writes pairs_check.json and fig_pairs_check.png.
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "ladder", "scripts"))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..", "python")))
import ladder_lib as L  # noqa: E402
from nrpic import figstyle  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("out")
ap.add_argument("--run", required=True)
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
VARS = ["phi", "Pi", "chi", "K", "alpha"]


def last(member):
    f = sorted(glob.glob(os.path.join(a.run, member, "*.sf.*.dump")))[-1]
    h, d = L.read_dump(f, VARS)
    return f, h, d


def rlin(d):
    hb = -d["K"].mean() / (3.0 * d["alpha"].mean())
    pib = d["Pi"].mean()
    return (hb / pib) * (d["phi"] - d["phi"].mean()), hb, pib


def skew(x):
    c = x - x.mean()
    return float(np.mean(c ** 3) / np.mean(c ** 2) ** 1.5)


res = {}
figdat = {}
for tag, s, plus, minus in (("q", 0.25, "zp4", "zm4"), ("h", 0.5, "zp2", "zm2")):
    fp, hp, dp = last(plus)
    fm, hm, dm = last(minus)
    assert abs(hp["time"] - hm["time"]) < 1e-12, (hp["time"], hm["time"])
    finite = all(np.all(np.isfinite(d[v])) for d in (dp, dm) for v in VARS)
    rp, hb_p, pib_p = rlin(dp)
    rm, hb_m, pib_m = rlin(dm)
    dphi = dp["phi"] - dm["phi"]
    p2 = abs(dp["phi"].mean() - dm["phi"].mean()) / np.sqrt(np.mean((dphi - dphi.mean()) ** 2))
    O = 0.5 * (rp - rm)
    E = 0.5 * (rp + rm)
    E = E - E.mean()
    q = O ** 2 - np.mean(O ** 2)
    acoef = float(np.sum(E * q) / np.sum(q * q))
    resid = E - acoef * q
    res[tag] = dict(s=s, time=hp["time"], files=[fp, fm], finite=bool(finite), P2=float(p2),
                    sigma_O=float(np.std(O)), a=acoef, a_sigma=float(acoef * np.std(O)),
                    resid_over_E=float(np.std(resid) / np.std(E)) if np.std(E) > 0 else None,
                    skew_dphi_plus=skew(dp["phi"]), skew_dphi_minus=skew(dm["phi"]),
                    skew_O=skew(O), H=[hb_p, hb_m], Pi=[pib_p, pib_m])
    figdat[tag] = (O, E, q, acoef, s)
    print(tag, {k: v for k, v in res[tag].items() if k != "files"}, flush=True)
res["a_ratio_half_over_quarter"] = res["h"]["a"] / res["q"]["a"] if res["q"]["a"] != 0 else None
with open(os.path.join(a.out, "pairs_check.json"), "w") as f:
    json.dump(res, f, indent=1)

figstyle.use_style()
fig = plt.figure(figsize=(figstyle.FULL_WIDTH, 3.0))
a1 = figstyle.inch_axes(fig, 0.75, 0.55, 3.0, 2.2)
a2 = figstyle.inch_axes(fig, 4.75, 0.55, 3.0, 2.2)
cols = {"q": figstyle.PAL["blue"], "h": figstyle.PAL["red"]}
xs = np.linspace(-5, 5, 200)
a1.semilogy(xs, np.exp(-xs ** 2 / 2) / np.sqrt(2 * np.pi), **figstyle.GUIDE, label="Gaussian")
edges = np.linspace(-5, 5, 41)
for tag, (O, E, q, ac, s) in figdat.items():
    x = O.ravel() / np.std(O)
    h, _ = np.histogram(x, edges, density=True)
    cc = 0.5 * (edges[1:] + edges[:-1])
    ok = h > 0
    a1.semilogy(cc[ok], h[ok], "o", ms=2.5, color=cols[tag], label=f"odd part, $s=\\pm{s:g}$")
    qq = q.ravel() / np.std(O) ** 2
    ee = E.ravel() / np.std(O) ** 2
    bins = np.linspace(np.percentile(qq, 1), np.percentile(qq, 99.5), 16)
    idx = np.digitize(qq, bins)
    bx = [qq[idx == i].mean() for i in range(1, len(bins)) if np.any(idx == i)]
    by = [ee[idx == i].mean() for i in range(1, len(bins)) if np.any(idx == i)]
    a2.plot(bx, by, "o", ms=3, color=cols[tag], label=f"$s=\\pm{s:g}$: $a\\,\\sigma_O$ = {ac * np.std(O):.2e}")
    a2.plot(bins, ac * np.std(O) ** 2 * bins / np.std(O) ** 2 * 1.0, color=cols[tag], lw=0.8)
a1.set_xlabel("$O/\\sigma_O$ of $R_\\mathrm{lin}$")
a1.set_ylabel("probability density")
a1.set_ylim(1e-5, 1)
a1.legend(loc="lower center", fontsize=6.5)
a2.axhline(0.0, **figstyle.THIN)
a2.set_xlabel("$(O^2-\\langle O^2\\rangle)/\\sigma_O^2$")
a2.set_ylabel("even part $E/\\sigma_O^2$ (binned)")
a2.legend(loc="upper left", fontsize=6.5)
figstyle.save(fig, os.path.join(a.out, "fig_pairs_check"))
print("wrote", a.out)
