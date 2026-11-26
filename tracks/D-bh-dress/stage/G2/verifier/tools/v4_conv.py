"""V4: convergence of item C2 from the finder summaries and region histories (own reader).
(a) particle number: FNQ (N/4), FK (N), FN4 (4N); (b) mesh of the growth: FF4 (M/4), ES-FL
(M/8), FL16 (M/16) with Delta M(t) = M_AH(t) - M_AH(20 M), raw and minus each mesh's own
vacuum control; (c) exterior Hamiltonian norms on shells against particle number.

python3 v4_conv.py --scratch <scratch/D-bh-dress> --out <dir>
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vio  # noqa: E402
import figstyle as fs  # noqa: E402

R = {"FNQ": ("D-20261124-172725-2f426b6", "esflkq"), "FK": ("D-20261123-022725-a553496", "esflk"),
     "FN4": ("D-20261124-134157-b17938b", "esflk4n"), "ES-FL": ("D-20261121-203150-15f2bad", "esfl"),
     "FL16": ("D-20261124-172745-72472ed", "esfl16"), "FF4": ("D-20261123-022727-1c17e73", "esfl4"),
     "V-1L": ("D-20261121-203124-a34cf1f", "v1l"), "V-1L16": ("D-20261121-203151-37e7b2d", "v1l16"),
     "V-1L4": ("D-20261123-022715-ab5d983", "v1l4")}


def mass(scr, lab):
    rid, base = R[lab]
    s, bad = vio.read_summary(os.path.join(scr, rid, f"{base}.horizon_summary_0.txt"))
    return s[~bad, 1], s[~bad, 2]


def at(t, M, T):
    return float(np.interp(T, t, M))


def shells(scr, lab):
    rid, base = R[lab]
    a = vio.read_text_table(os.path.join(scr, rid, f"{base}.region.hst"))
    t = a[:, 0]
    rev = t[::-1]
    _, idx = np.unique(rev, return_index=True)
    a = a[np.sort(len(t) - 1 - idx)]
    t = a[:, 0]
    col = lambda k: a[:, k - 1]  # 1-based header numbering
    Vh, Hh = col(55), col(56)
    V = [col(11), col(22), col(33), col(44)]
    H = [col(12), col(23), col(34), col(45)]
    inner = [(Vh, Hh)] + list(zip(V[:-1], H[:-1]))
    out = {}
    names = ["[1.2rAH,6]", "[6,12]", "[12,30]", "[30,60]"]
    for k, nm in enumerate(names):
        Va, Ha = inner[k]
        Vb, Hb = V[k], H[k]
        dV = Vb - Va
        out[nm] = np.sqrt(np.maximum(Vb * Hb ** 2 - Va * Ha ** 2, 0.0) / dV)
    return t, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = {}
    m = {lab: mass(a.scratch, lab) for lab in R}
    # (a) particle number
    pn = {}
    for T in [100.0, 200.0, 300.0, 399.5]:
        q, n, f = (at(*m["FNQ"], T), at(*m["FK"], T), at(*m["FN4"], T))
        pn[str(T)] = dict(M_Nq=q, M_N=n, M_4N=f, d_N_Nq=n - q, d_4N_N=f - n,
                          ordered=bool(abs(f - n) <= abs(n - q)))
    tg = np.arange(20.0, 399.6, 0.5)
    q, n, f = (np.interp(tg, *m["FNQ"]), np.interp(tg, *m["FK"]), np.interp(tg, *m["FN4"]))
    win = {}
    for lo, hi in [(20, 100), (100, 200), (200, 300), (300, 399.5)]:
        w = (tg >= lo) & (tg <= hi)
        r1 = np.sqrt(np.mean((n[w] - q[w]) ** 2))
        r2 = np.sqrt(np.mean((f[w] - n[w]) ** 2))
        win[f"{lo}-{hi}"] = dict(rms_N_Nq=float(r1), rms_4N_N=float(r2), ratio=float(r1 / r2))
    res["particle_number"] = dict(times=pn, windows=win,
                                  n_ordered=int(sum(v["ordered"] for v in pn.values())))
    # (b) mesh of the growth
    mesh = {}
    for T in [100.0, 200.0, 299.0]:
        d = {}
        for lab, ctl in [("FF4", "V-1L4"), ("ES-FL", "V-1L"), ("FL16", "V-1L16")]:
            dM = at(*m[lab], T) - at(*m[lab], 20.0)
            dC = at(*m[ctl], T) - at(*m[ctl], 20.0)
            d[lab] = dict(dM=dM, dM_minus_ctrl=dM - dC)
        mesh[str(T)] = dict(members=d,
                            d16_8=d["FL16"]["dM"] - d["ES-FL"]["dM"],
                            d8_4=d["ES-FL"]["dM"] - d["FF4"]["dM"],
                            d16_8_ctrl=d["FL16"]["dM_minus_ctrl"] - d["ES-FL"]["dM_minus_ctrl"],
                            d8_4_ctrl=d["ES-FL"]["dM_minus_ctrl"] - d["FF4"]["dM_minus_ctrl"])
    tt0 = np.arange(20.0, 299.1, 0.5)
    g = lambda lab: np.interp(tt0, *m[lab]) - at(*m[lab], 20.0)
    d168 = g("FL16") - g("ES-FL")
    d84 = g("ES-FL") - g("FF4")
    w = tt0 >= 250
    mesh["envelope_20_299"] = dict(d16_8_max_abs=float(np.max(np.abs(d168))),
                                   d16_8_mean_250_299=float(np.mean(d168[w])),
                                   d8_4_mean_250_299=float(np.mean(d84[w])),
                                   d8_4_max_abs=float(np.max(np.abs(d84))))
    pnoise = dict(sd_N_Nq=float(np.std(n - q)), sd_4N_N=float(np.std(f - n)))
    res["particle_number"]["sample_sd"] = pnoise
    res["mesh"] = mesh
    # (c) exterior shells, N/4 over 4N
    tq, sq = shells(a.scratch, "FNQ")
    t4, s4 = shells(a.scratch, "FN4")
    common, iq, i4 = np.intersect1d(tq, t4, return_indices=True)
    sh = {}
    for nm in sq:
        ratio = sq[nm][iq] / s4[nm][i4]
        w = (common >= 20) & (common <= 400)
        sh[nm] = dict(min=float(ratio[w].min()), max=float(ratio[w].max()),
                      median=float(np.median(ratio[w])),
                      median_20_150=float(np.median(ratio[(common >= 20) & (common <= 150)])),
                      median_150_400=float(np.median(ratio[(common > 150) & (common <= 400)])))
    res["shells_Nq_over_4N"] = sh
    json.dump(res, open(os.path.join(a.out, "v4_conv.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))

    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(8, 6.0))
    ax1 = fig.add_axes([0.09, 0.57, 0.38, 0.39])
    ax2 = fig.add_axes([0.59, 0.57, 0.38, 0.39])
    ax3 = fig.add_axes([0.09, 0.08, 0.88, 0.37])
    ax1.plot(tg, n - q, color=fs.PAL["green"], label=r"$M_N-M_{N/4}$")
    ax1.plot(tg, f - n, color=fs.PAL["yellow"], label=r"$M_{4N}-M_N$")
    ax1.axhline(0, color="k", lw=1)
    ax1.set_xlabel("t [M]")
    ax1.set_ylabel(r"$\Delta M_{AH}$ [M]")
    ax1.legend(loc="lower left", fontsize=8)
    tt = np.arange(20.0, 299.1, 0.5)
    base = lambda lab: np.interp(tt, *m[lab]) - at(*m[lab], 20.0)
    ax2.plot(tt, base("FL16") - base("ES-FL"), color=fs.PAL["blue"], label=r"$\Delta M_{16}-\Delta M_8$")
    ax2.plot(tt, base("ES-FL") - base("FF4"), color=fs.PAL["green"], label=r"$\Delta M_8-\Delta M_4$")
    ax2.axhline(0, color="k", lw=1)
    ax2.set_xlabel("t [M]")
    ax2.set_ylabel("difference of growth since 20 M [M]")
    ax2.legend(loc="lower left", fontsize=8)
    for nm, c in zip(sq, fs.SERIES):
        ax3.semilogy(common, sq[nm][iq] / s4[nm][i4], color=c, label=nm)
    ax3.axhline(4.0, color="k", ls="--", lw=1)
    ax3.axhline(1.0, color="grey", ls=":", lw=1)
    ax3.set_xlabel("t [M]")
    ax3.set_ylabel(r"$\|H\|_{N/4}/\|H\|_{4N}$ on shells")
    ax3.legend(loc="upper right", ncol=4, fontsize=8)
    fs.save(fig, os.path.join(a.out, "v4_conv"))


if __name__ == "__main__":
    main()
