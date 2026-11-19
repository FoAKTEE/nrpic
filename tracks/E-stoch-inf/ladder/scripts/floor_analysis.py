#!/usr/bin/env python3
"""The floor of the odd constraint parts on the k_max/dk = 8 ladder and the verdict on A5
"before the floor" (package tracks/E-stoch-inf/ladder, JOURNAL entry 9).

    floor_analysis.py --res DIR --out DIR

DIR is the res/ directory of the final ladder analysis (run E-20261115-194633-9e04ed8):
pair_L{32,64,128,256}p_L*m.json (odd and even parts of H and M_i per dump) and the halving
pairs pair_{L32,Q64,Q128}ph_*mh.json with their s = +-1 partners.

1. Floor model: at N = 256 the odd part grows with N at every dump to t = 3.5 (order
   128 -> 256 between -2.5 and -0.8), so it is taken as the floor there, and the floor at
   N is F(N, t) = odd_256(t) (N/256)^q, with q measured between 128 and 256 at the dumps
   with t <= 1.5 (where the odd part at 128 is not above the floor either).
2. A5 restricted to the points where the finer odd part exceeds FMULT times its floor.
3. Amplitude dependence of the odd part (halving pairs): factor 2 = first order in s
   (truncation), factor 1 = independent of s (floor).
4. First e-fold where the odd part of H exceeds the even part in the paper's set-up
   against ln(N/8), the crossing of the first shell with fewer than eight cells per
   wavelength (reference background of ladder_lib).
Writes floor.json and fig_floor.png/pdf.
"""
import argparse
import json
import os

import numpy as np

FMULT = 3.0


def rows(res, name):
    with open(os.path.join(res, name)) as fp:
        return json.load(fp)["rows"]


def col(rs, key):
    return np.array([r[key] for r in rs], float)


def interp_log(t_src, y_src, t):
    y = np.asarray(y_src, float)
    ok = y > 0
    return np.exp(np.interp(t, np.asarray(t_src)[ok], np.log(y[ok]), left=np.nan,
                            right=np.nan))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    L = {n: rows(a.res, f"pair_L{n}p_L{n}m.json") for n in (32, 64, 128, 256)}
    t32 = col(L[32], "time")
    sel = (t32 > 0.3) & (t32 < 3.7)          # the span covered by all four rungs
    tc = t32[sel]
    out = dict(times=tc.tolist(), efolds=col(L[32], "efolds")[sel].tolist(), parts={},
               floor={}, A5={}, halving={}, crossing={})
    for key in ("H_odd", "M_odd", "H_even", "M_even"):
        out["parts"][key] = {n: interp_log(col(L[n], "time"), col(L[n], key), tc).tolist()
                             for n in L}
    # 1. floor exponent q from 128 -> 256 at t <= 1.5
    for key in ("H_odd", "M_odd"):
        y128 = np.array(out["parts"][key][128])
        y256 = np.array(out["parts"][key][256])
        early = tc <= 1.6
        q = float(np.mean(np.log2(y256[early] / y128[early])))
        out["floor"][key] = dict(q=q, q_each=np.log2(y256[early] / y128[early]).tolist(),
                                 model={n: (y256 * (n / 256.0)**q).tolist() for n in L})
    # 2. A5 before the floor
    for key in ("H_odd", "M_odd"):
        q = out["floor"][key]["q"]
        y = {n: np.array(out["parts"][key][n]) for n in L}
        F = {n: np.array(out["floor"][key]["model"][n]) for n in L}
        res = {}
        for lo, hi in ((32, 64), (64, 128), (128, 256)):
            p = np.log2(y[lo] / y[hi])
            above = y[hi] > FMULT * F[hi]
            res[f"{lo}->{hi}"] = dict(order=p.tolist(), finer_over_floor=(y[hi] / F[hi]).tolist(),
                                      used=above.tolist(),
                                      orders_used=p[above].tolist())
        used = np.concatenate([np.array(v["orders_used"]) for v in res.values()])
        res["range_used"] = [float(used.min()), float(used.max())] if used.size else None
        res["pass_"] = bool(used.size and used.min() >= 4.0 and used.max() <= 6.0)
        out["A5"][key] = res
    # 3. halving of the odd part: factor between s = 1 and s = 1/2
    for tag, p1, ph in (("N32", "pair_L32p_L32m.json", "pair_L32ph_L32mh.json"),
                        ("N64", "pair_Q64p_Q64m.json", "pair_Q64ph_Q64mh.json"),
                        ("N128", "pair_Q128p_Q128m.json", "pair_Q128ph_Q128mh.json")):
        r1, rh = rows(a.res, p1), rows(a.res, ph)
        n = min(len(r1), len(rh))
        keep = [i for i in range(n) if r1[i]["cycle"] == rh[i]["cycle"]
                and abs(r1[i]["time"] - rh[i]["time"]) < 1e-9]
        out["halving"][tag] = dict(
            efolds=[r1[i]["efolds"] for i in keep],
            H_odd=[r1[i]["H_odd"] / rh[i]["H_odd"] for i in keep],
            H_even=[r1[i]["H_even"] / rh[i]["H_even"] for i in keep],
            M_odd=[r1[i]["M_odd"] / rh[i]["M_odd"] for i in keep],
            dropped=[r1[i]["time"] for i in range(n) if i not in keep])
    # 4. first e-fold with odd > even (paper's set-up) against ln(N/8)
    for tag, name in (("N32", "pair_L32p_L32m.json"), ("N64", "pair_Q64p_Q64m.json"),
                      ("N128", "pair_Q128p_Q128m.json"), ("N256", "pair_P256_P256m.json")):
        rs = rows(a.res, name)
        nn = int(tag[1:])
        first = next((r["efolds"] for r in rs if r["H_odd"] > r["H_even"] and r["time"] > 0.2),
                     None)
        prev = None
        for r in rs:
            if r["H_odd"] > r["H_even"] and r["time"] > 0.2:
                break
            prev = r["efolds"]
        out["crossing"][tag] = dict(first_dump_odd_gt_even=first, previous_dump=prev,
                                    ln_N_over_8=float(np.log(nn / 8.0)))
    with open(os.path.join(a.out, "floor.json"), "w") as fp:
        json.dump(out, fp, indent=1, default=float)
    print(json.dumps(dict(q={k: out["floor"][k]["q"] for k in out["floor"]},
                          A5={k: dict(range=v["range_used"], pass_=v["pass_"])
                              for k, v in out["A5"].items()},
                          crossing=out["crossing"]), indent=1, default=float))
    for k in ("H_odd", "M_odd"):
        for pr, v in out["A5"][k].items():
            if isinstance(v, dict):
                print(k, pr, "orders", np.round(v["order"], 2).tolist(),
                      "finer/floor", np.round(v["finer_over_floor"], 1).tolist())
    for tag, v in out["halving"].items():
        print("halving", tag, "odd H", np.round(v["H_odd"], 3).tolist(), "dropped", v["dropped"])
    figure(out, a.out)


def figure(out, outdir):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use_style()
    col = {32: fs.PAL["yellow"], 64: fs.PAL["green"], 128: fs.PAL["blue"], 256: fs.PAL["red"]}
    N = np.array(out["efolds"])
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
    a0 = ax[0]
    for n in (32, 64, 128, 256):
        a0.semilogy(N, out["parts"]["H_odd"][n], "o-", color=col[n], ms=3, label=f"$N={n}$")
        if n != 256:
            a0.semilogy(N, out["floor"]["H_odd"]["model"][n], ":", color=col[n], lw=1.0)
    a0.set_xlabel(r"e-folds $\mathcal{N}-\mathcal{N}_*$")
    a0.set_ylabel(r"odd part of $\mathcal{H}$ / $\langle[\mathcal{H}]\rangle$")
    a0.set_title(r"$k_{\max}/dk=8$; dotted: floor model", fontsize=8)
    a0.legend(fontsize=7, loc="lower left")
    a1 = ax[1]
    hcol = {"N32": fs.PAL["yellow"], "N64": fs.PAL["green"], "N128": fs.PAL["blue"]}
    for tag, v in out["halving"].items():
        a1.plot(v["efolds"], v["H_odd"], "o-", color=hcol[tag], ms=3,
                label=f"odd, ${tag[0]}={tag[1:]}$")
        a1.plot(v["efolds"], v["H_even"], "s--", color=hcol[tag], ms=3, lw=0.8)
    a1.axhline(2.0, **fs.GUIDE)
    a1.axhline(1.0, **fs.THIN)
    a1.axhline(4.0, **fs.THIN)
    a1.set_ylim(0, 5)
    a1.set_xlabel(r"e-folds $\mathcal{N}-\mathcal{N}_*$")
    a1.set_ylabel(r"factor between $s=1$ and $s=1/2$")
    a1.set_title(r"paper set-up; dashed: even part", fontsize=8)
    a1.legend(fontsize=7, loc="lower right")
    a2 = ax[2]
    pcol = {"32->64": fs.PAL["green"], "64->128": fs.PAL["blue"], "128->256": fs.PAL["red"]}
    for key, mk in (("H_odd", "o"), ("M_odd", "s")):
        for pr, v in out["A5"][key].items():
            if not isinstance(v, dict):
                continue
            p, used = np.array(v["order"]), np.array(v["used"])
            a2.plot(N, p, "-", color=pcol[pr], lw=0.8)
            a2.plot(N[used], p[used], mk, color=pcol[pr], ms=4,
                    label=f"{pr}, {key[0]}" if key == "H_odd" or pr == "32->64" else None)
            a2.plot(N[~used], p[~used], mk, mfc="none", color=pcol[pr], ms=4)
    a2.axhspan(4.0, 6.0, color="0.9", zorder=0)
    a2.set_ylim(-3, 7)
    a2.set_xlabel(r"e-folds $\mathcal{N}-\mathcal{N}_*$")
    a2.set_ylabel("order of the odd part")
    a2.set_title(rf"filled: finer part $>{FMULT:g}\times$ floor", fontsize=8)
    a2.legend(fontsize=6, loc="lower right")
    fig.tight_layout()
    fs.save(fig, os.path.join(outdir, "fig_floor"))
    plt.close(fig)


if __name__ == "__main__":
    main()
