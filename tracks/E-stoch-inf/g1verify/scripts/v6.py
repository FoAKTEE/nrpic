"""V6 (A6): temporal order from the Courant runs (g1verify, JOURNAL entry 3, P-V6).

usage: v6.py OUTDIR
Runs T25{p,m}, T12{p,m}, T06{p,m} of E-20261119-142317-c851f27 (N = 32, k_max/dk = 8,
Courant 0.25, 0.125, 0.0625, s = +-1, dumps at common times). Per common dump and quantity
X: D1 = X(0.25) - X(0.125), D2 = X(0.125) - X(0.0625), order p = log2(|D1|/|D2|) (max norm
and rms), for
- the box means of phi, Pi, K, chi (and their error against my Friedmann/KG integration);
- the parts odd and even in s of phi, Pi, chi, K, gxx, Axx (box mean removed) and of H, M_x;
- R^NR_n of the modes |n|^2 <= 8 (my extraction) and its odd part.
Every dump is read whole once and its sha256 checked against the run's sha256sums.txt.
"""
import os
import sys
import json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nrsf, alpha as A, rnr, ref, catalog as C  # noqa: E402

out = sys.argv[1]
os.makedirs(out, exist_ok=True)
runs = C.catalog()
RID = "E-20261119-142317-c851f27"
sums = C.sums(RID)
TH = ("T25", "T12", "T06")
FIELDS = ["phi", "Pi", "chi", "K", "gxx", "Axx"]
CON = ["H", "Mx"]
VARS = ["phi", "Pi", "chi", "K", "alpha", "H", "Mx"] + rnr.GT + ["Axx"]
DECK = dict(phi0=-2.66679478988261254e+00, pi0=2.97300406808996935e-02, mass=1.82877655899024605e-01)
bg = ref.CodeBackground(DECK["phi0"], DECK["pi0"], DECK["mass"], t_end=9.0)
nv = A.hemisphere(8)
shaok = {}


def load(key, path):
    f, dig, h = nrsf.read_hashed(path, VARS)
    rel = os.path.relpath(path, os.path.join(C.SCR, RID))
    shaok[f"{key}/{os.path.basename(path)}"] = sums.get(rel) == dig
    return {k: np.array(v) for k, v in f.items()}, h


files = {f"{t}{s}": nrsf.dumps(runs[f"{t}{s}"]["dir"]) for t in TH for s in "pm"}
nd = min(len(v) for v in files.values())
rows = []
for d in range(nd):
    F, T, CY = {}, {}, {}
    for key, fl in files.items():
        F[key], h = load(key, fl[d])
        T[key], CY[key] = h["time"], h["cycle"]
    t = T["T25p"]
    row = dict(dump=d, time=t, times={k: T[k] for k in T}, cycles={k: CY[k] for k in CY},
               time_spread=float(max(T.values()) - min(T.values())))
    q = {}
    for th in TH:
        p, m = F[th + "p"], F[th + "m"]
        e = {}
        for n in FIELDS + CON:
            xp = p[n] - (p[n].mean() if n in FIELDS else 0.0)
            xm = m[n] - (m[n].mean() if n in FIELDS else 0.0)
            e[f"odd_{n}"] = 0.5 * (xp - xm)
            e[f"even_{n}"] = 0.5 * (xp + xm)
        for n in ("phi", "Pi", "K", "chi"):
            e[f"mean_{n}"] = np.array([p[n].mean()])
        Rp, _ = rnr.rnr_coefficients(p, nv)
        Rm, _ = rnr.rnr_coefficients(m, nv)
        e["R_p"] = np.concatenate([Rp.real, Rp.imag])
        e["R_odd"] = np.concatenate([(0.5 * (Rp - Rm)).real, (0.5 * (Rp - Rm)).imag])
        q[th] = e
    orders = {}
    for name in q["T25"]:
        a, b, c = q["T25"][name], q["T12"][name], q["T06"][name]
        d1, d2 = a - b, b - c
        n1, n2 = float(np.max(np.abs(d1))), float(np.max(np.abs(d2)))
        r1, r2 = float(np.sqrt(np.mean(d1 ** 2))), float(np.sqrt(np.mean(d2 ** 2)))
        scale = float(np.max(np.abs(c)))
        orders[name] = dict(D1_max=n1, D2_max=n2, scale=scale,
                            p_max=float(np.log2(n1 / n2)) if n2 > 0 and n1 > 0 else None,
                            p_rms=float(np.log2(r1 / r2)) if r2 > 0 and r1 > 0 else None,
                            D2_over_scale=n2 / scale if scale > 0 else None)
    b0 = bg(t)
    row["background_error"] = {th: {n: float(q[th][f"mean_{n}"][0] / b0[n] - 1.0) for n in ("phi", "Pi", "K")}
                               for th in TH}
    row["orders"] = orders
    rows.append(row)
    print(d, f"t={t:.4f}", "spread", row["time_spread"],
          {k: (round(v["p_max"], 2) if v["p_max"] else None) for k, v in orders.items()
           if k in ("odd_phi", "odd_chi", "even_H", "odd_H", "R_odd", "mean_phi")}, flush=True)

res = dict(run_id=RID, rows=rows, sha_checked=shaok, sha_all_ok=bool(all(shaok.values())), ndumps=nd)
with open(os.path.join(out, "v6.json"), "w") as f:
    json.dump(res, f, indent=1)
print("sha_all_ok", res["sha_all_ok"], len(shaok))
