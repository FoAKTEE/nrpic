#!/usr/bin/env python3
"""V4: friends-of-friends catalogues of the population box with EQUAL particle masses
(every particle of a run given the run's mean mass), b = 0.2 of the mean spacing L/n,
groups of at least 100 particles; the common mass limit 100 m_N, m_N = rho_c L^3/64^3.

    python3 v5_halos.py OUTDIR NAME=SNAPSHOT ...
Pairs: GR against Newton (the ten largest Newtonian halos, partner within 0.1 of the
centre), and any two catalogues for counts above the common limit and the largest mass.
"""
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vlib  # noqa: E402

L = 8.0
RHO_C = 3.0/(8.0*np.pi)
M_N = RHO_C*L**3/64**3


def centre(x, L):
    """Periodic centre of mass (equal weights) by unwrapping about the circular mean."""
    ang = 2*np.pi*x/L
    cm = np.angle(np.exp(1j*ang).mean(0))*L/(2*np.pi)
    d = np.mod(x - cm + L/2, L) - L/2
    return np.mod(cm + d.mean(0), L)


def catalogue(fn):
    t0 = time.time()
    s = vlib.read_snapshot(fn)
    n = s["n"]
    ng = round(n**(1/3))
    mbar = float(s["m"].mean())
    x = s["x"]
    cnt, msum, lab, order = vlib.halo_counts(x, np.full(n, mbar), L, 0.2*L/ng, 100)
    cents = []
    for h in order[:30]:
        cents.append(centre(x[lab == h], L).tolist())
    M = cnt*mbar
    return {"file": fn, "t": s["t"], "a": float(vlib.scale(s["t"])), "n": n, "m_mean": mbar,
            "m_rel_spread": float(s["m"].std()/mbar), "n_halos_100": int(len(cnt)),
            "n_common": int((M >= 100*M_N).sum()), "N_largest": cnt[:30].tolist(),
            "M_largest": M[:30].tolist(), "centres": cents, "wall_s": time.time() - t0}


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    cats = {}
    for arg in sys.argv[2:]:
        name, fn = arg.split("=", 1)
        cats[name] = catalogue(fn)
        c = cats[name]
        print(name, f"a {c['a']:.2f} n100 {c['n_halos_100']} common {c['n_common']} M1 {c['M_largest'][0]:.5g}"
              f" spread {c['m_rel_spread']:.4f} wall {c['wall_s']:.0f}s", flush=True)
        json.dump(cats, open(os.path.join(out, "v5_halos.json"), "w"), indent=1)
    cmp_ = {}
    newt = [k for k in cats if k.startswith("newton")]
    for nk in newt:
        cn = cats[nk]
        for gk in [k for k in cats if not k.startswith("newton") and abs(cats[k]["a"] - cn["a"]) < 1.0]:
            cg = cats[gk]
            ratios = []
            for i in range(10):
                c0 = np.array(cn["centres"][i])
                best, bd = None, 1e9
                for j, cj in enumerate(cg["centres"]):
                    d = np.linalg.norm(np.mod(np.array(cj) - c0 + L/2, L) - L/2)
                    if d < bd:
                        bd, best = d, j
                ratios.append({"i": i, "j": best, "dist": float(bd),
                               "ratio": cg["M_largest"][best]/cn["M_largest"][i] if bd < 0.1 else None})
            ok = [r["ratio"] for r in ratios if r["ratio"] is not None]
            cmp_[gk + "_vs_" + nk] = {"partners_within_0.1": len(ok),
                                     "median_abs_dev": float(np.median(np.abs(np.array(ok) - 1))) if ok else None,
                                     "largest_ratio": cg["M_largest"][0]/cn["M_largest"][0],
                                     "counts_100": [cg["n_halos_100"], cn["n_halos_100"]], "pairs": ratios}
    json.dump({"catalogues": cats, "compare": cmp_}, open(os.path.join(out, "v5_halos.json"), "w"), indent=1)
    for k, v in cmp_.items():
        print(k, {kk: vv for kk, vv in v.items() if kk != "pairs"})


if __name__ == "__main__":
    main()
