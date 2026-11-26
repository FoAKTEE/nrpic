#!/usr/bin/env python3
"""G3-C of SCOPE 4d.4 with 4d.9 A6: constraint scaling with three amplitudes, the track's own reader (risk R30).

    read_g3c.py OUT --run <G3C run dir> [--lo 2.0 --hi 6.6]

The run directory holds c_p1, c_m1, c_ph, c_mh, c_pq, c_mq (seed 0 at s = +-1, +-1/2, +-1/4, 128^3, 21 dumps with
constraint fields). Per dump and constraint (H; M = (Mx, My, Mz) together), box means removed per component:
E(s) = [C(+s) + C(-s)]/2, O(s) = [C(+s) - C(-s)]/2 per cell; D1 = E(1) - 4 E(1/2), D2 = E(1/2) - 4 E(1/4).
Model test (both must hold for the dump to be judged): rms(D2)/rms(D1) in [0.9, 1.1], corr(D1, D2) in
[-0.30, -0.17]. Level sigma^2 = [rms(D1)^2 + rms(D2)^2]/34. Factors f_a = sqrt(e1^2 - s^2)/sqrt(eh^2 - s^2),
f_b = sqrt(eh^2 - s^2)/sqrt(eq^2 - s^2), each judged where the smaller of its two even parts exceeds 3 sigma and
cN = N - N* (column efolds of usr.sf.con.hst at the dump's cycle) lies in [2.0, 6.6]. A6: each factor and each
constraint judged at >= 4 dumps of the range, else "not testable". Fails if a judged factor lies outside
4 +- 0.05 or the model test fails at more than a third of the dumps in the range. Reported beside it, not
judged: the two-amplitude estimator of 4c (g2prod/scripts/judge_g2.floor_halving: floor from the odd parts,
f^2 = (4 o_h^2 - o_1^2)/3) for both amplitude pairs. Writes OUT/g3c.json and OUT/fig_g3c.{png,pdf}.
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
import figstyle as fs  # noqa: E402

RUNS = {"p1": 1.0, "m1": -1.0, "ph": 0.5, "mh": -0.5, "pq": 0.25, "mq": -0.25}
GROUPS = {"H": ["H"], "M": ["Mx", "My", "Mz"]}


def rms(a):
    return float(np.sqrt(np.mean(a * a)))


def per_dump(run, i):
    f = {}
    for k in RUNS:
        p = cl.dump_list(os.path.join(run, "c_" + k))[i]
        h, d = cl.read_fields(p, ["H", "Mx", "My", "Mz"])
        f[k] = (h, d)
    cyc = {f[k][0]["cycle"] for k in RUNS}
    if len(cyc) != 1:
        raise SystemExit(f"dump {i}: cycles differ {cyc}")
    out = dict(cycle=int(cyc.pop()), t=float(f["p1"][0]["time"]))
    for g, comps in GROUPS.items():
        E, O = {}, {}
        for tag, (p, m) in (("1", ("p1", "m1")), ("h", ("ph", "mh")), ("q", ("pq", "mq"))):
            E[tag] = np.stack([0.5 * (f[p][1][c] + f[m][1][c]) - 0.5 * (f[p][1][c].mean() + f[m][1][c].mean())
                               for c in comps])
            O[tag] = np.stack([0.5 * (f[p][1][c] - f[m][1][c]) - 0.5 * (f[p][1][c].mean() - f[m][1][c].mean())
                               for c in comps])
        D1 = E["1"] - 4.0 * E["h"]
        D2 = E["h"] - 4.0 * E["q"]
        r1, r2 = rms(D1), rms(D2)
        corr = float(np.mean(D1 * D2) / (r1 * r2))
        sig2 = (r1**2 + r2**2) / 34.0
        e = {t: rms(E[t]) for t in E}
        o = {t: rms(O[t]) for t in O}

        def fac(a, b):
            num, den = e[a]**2 - sig2, e[b]**2 - sig2
            return float(np.sqrt(num) / np.sqrt(den)) if num > 0 and den > 0 else None

        def fac4c(a, b):     # judge_g2.floor_halving with the pair (a, b) as (s, s/2)
            f2 = max(0.0, (4.0 * o[b]**2 - o[a]**2) / 3.0)
            return dict(corr=float(np.sqrt(max(e[a]**2 - f2, 0.0)) / np.sqrt(max(e[b]**2 - f2, 1e-300))),
                        floor=float(np.sqrt(f2)), sel=bool(e[b] > 3.0 * np.sqrt(f2)))

        out[g] = dict(rms_D1=r1, rms_D2=r2, ratio=r2 / r1, corr=corr, sigma=float(np.sqrt(sig2)),
                      e=e, o=o, f_a=fac("1", "h"), f_b=fac("h", "q"),
                      big_a=bool(min(e["1"], e["h"]) > 3.0 * np.sqrt(sig2)),
                      big_b=bool(min(e["h"], e["q"]) > 3.0 * np.sqrt(sig2)),
                      model_ok=bool(0.9 <= r2 / r1 <= 1.1 and -0.30 <= corr <= -0.17),
                      est4c_a=fac4c("1", "h"), est4c_b=fac4c("h", "q"))
    del f
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--run", required=True)
    ap.add_argument("--lo", type=float, default=2.0)
    ap.add_argument("--hi", type=float, default=6.6)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    nd = min(len(cl.dump_list(os.path.join(a.run, "c_" + k))) for k in RUNS)
    con = cl.read_con(os.path.join(a.run, "c_p1", "usr.sf.con.hst"))
    cmap = {int(r[cl.C["cycle"]]): float(r[cl.C["efolds"]]) for r in con}
    rows = []
    for i in range(nd):
        r = per_dump(a.run, i)
        r["cN"] = cmap.get(r["cycle"])
        r["in_range"] = r["cN"] is not None and a.lo <= r["cN"] <= a.hi
        rows.append(r)
        print(f"dump {i}: cN={r['cN']:.3f} H f_a={r['H']['f_a']} f_b={r['H']['f_b']} model={r['H']['model_ok']}"
              f" | M f_a={r['M']['f_a']} f_b={r['M']['f_b']} model={r['M']['model_ok']}", flush=True)
    V = dict(n_dumps=nd, range=[a.lo, a.hi], n_in_range=int(sum(r["in_range"] for r in rows)))
    verdict = "PASS"
    for g in GROUPS:
        rr = [r for r in rows if r["in_range"]]
        nfail = sum(not r[g]["model_ok"] for r in rr)
        model_fail = nfail > len(rr) / 3.0
        res = dict(model_fail_dumps=nfail, model_test_fails=bool(model_fail))
        for fk, bk in (("f_a", "big_a"), ("f_b", "big_b")):
            jj = [r for r in rr if r[g]["model_ok"] and r[g][bk] and r[g][fk] is not None]
            vals = [r[g][fk] for r in jj]
            st = "not testable" if len(jj) < 4 else (
                "PASS" if all(abs(v - 4.0) <= 0.05 for v in vals) else "FAIL")
            res[fk] = dict(n_judged=len(jj), cN=[r["cN"] for r in jj], values=vals, status=st,
                           max_dev=float(max(abs(v - 4.0) for v in vals)) if vals else None)
            if st == "FAIL" or (st == "not testable" and verdict == "PASS"):
                verdict = "FAIL" if st == "FAIL" else ("not testable" if verdict != "FAIL" else verdict)
        if model_fail:
            verdict = "FAIL"
        V[g] = res
    V["verdict"] = verdict
    with open(os.path.join(a.out, "g3c.json"), "w") as fp:
        json.dump(dict(verdict=V, rows=rows), fp, indent=1)
    print(json.dumps(V, indent=1))
    figure(rows, a, os.path.join(a.out, "fig_g3c"))


def figure(rows, a, path):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 3, figsize=(10.5, 3.3))
    cN = np.array([r["cN"] for r in rows])
    for g, col in (("H", fs.PAL["blue"]), ("M", fs.PAL["red"])):
        for fk, bk, mk in (("f_a", "big_a", "o"), ("f_b", "big_b", "s")):
            v = np.array([np.nan if r[g][fk] is None else r[g][fk] for r in rows])
            ok = np.array([r[g]["model_ok"] and r[g][bk] and r["in_range"] for r in rows])
            ax[0].plot(cN, v, mk, mfc="none", color=col, ms=4, alpha=0.5)
            ax[0].plot(cN[ok], v[ok], mk, color=col, ms=4,
                       label=f"{g} {'1 / (1/2)' if fk == 'f_a' else '(1/2) / (1/4)'}")
        ax[1].plot(cN, [r[g]["ratio"] for r in rows], "o-", color=col, ms=3, lw=0.8, label=f"{g} rms D2/rms D1")
        ax[1].plot(cN, [-r[g]["corr"] for r in rows], "s--", color=col, ms=3, lw=0.8, label=f"{g} -corr(D1,D2)")
        for t, ls in (("1", "-"), ("h", "--"), ("q", ":")):
            ax[2].semilogy(cN, [r[g]["e"][t] for r in rows], ls, color=col, lw=1.0, label=f"{g} even s={t}")
        ax[2].semilogy(cN, [3 * r[g]["sigma"] for r in rows], "-.", color=col, lw=0.8, alpha=0.6,
                       label=f"{g} 3 sigma")
    for x in ax:
        x.axvspan(a.lo, a.hi, color="0.9", zorder=0)
        x.set_xlabel(r"$N - N_*$")
    ax[0].axhspan(3.95, 4.05, color=fs.PAL["green"], alpha=0.25)
    ax[0].set_ylim(3.0, 5.0)
    ax[0].set_ylabel("factor (filled: judged)")
    ax[1].axhspan(0.9, 1.1, color="0.7", alpha=0.3)
    ax[1].axhspan(0.17, 0.30, color=fs.PAL["green"], alpha=0.2)
    ax[1].axhline(4 / 17, color="k", lw=0.5)
    ax[1].set_ylabel("model test")
    ax[2].set_ylabel("rms of the even part")
    for x in ax:
        x.legend(fontsize=6)
    fig.tight_layout()
    fs.save(fig, path)


if __name__ == "__main__":
    main()
