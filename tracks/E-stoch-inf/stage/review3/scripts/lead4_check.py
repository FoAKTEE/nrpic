#!/usr/bin/env python3
"""Lead review, batch 3 (E-stoch-inf): own-code checks of the usr package's card results.
Predictions LU1-LU3 of ../../../JOURNAL.md (entry 2026-11-21T12:58Z).  Reads the raw dumps
with the verifier's reader (g1verify/scripts/nrsf.py, independent of usr/scripts/card_lib.py)
and the records with numpy; numpy FFT.

    lead4_check.py --out DIR

LU1  U256/U256m at N_f: R_phi = (H_b/Pi_b)(phi - <phi>), H_b = -<K>/(3<alpha>), Pi_b = <Pi>;
     rms, skewness, max|R|; even/odd ratio of the mode coefficients on the hemisphere
     0 < |n|^2 <= 1024 and <= 4096.
LU2  group 1 at 128^3, dumps 4, 6, 8: raw halving factors of the odd and even parts of H and
     M (rms over cells; even parts with box means removed) and the floor-corrected even
     factor, f^2 = (4 o_h^2 - o_1^2)/3.
LU3  records: max and final <|M|/[M]> of U256 and U256m.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
T = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(T, "g1verify", "scripts"))
sys.path.insert(0, HERE)
import nrsf  # noqa: E402

S = "/data/haiyangw/nrpic/scratch/E-stoch-inf"
U256 = os.path.join(S, "E-20261121-075255-8cf90e7", "U256")
U256M = os.path.join(S, "E-20261121-085221-1f579fe", "U256m")
G1 = os.path.join(S, "E-20261120-222621-ba66218")


def hemisphere_n2(N):
    k = np.fft.fftfreq(N, 1.0 / N)
    kx = np.arange(N // 2 + 1, dtype=float)
    KZ, KY, KX = np.meshgrid(k, k, kx, indexing="ij")
    n2 = KX**2 + KY**2 + KZ**2
    hemi = (KX > 0) | ((KX == 0) & (KY > 0)) | ((KX == 0) & (KY == 0) & (KZ > 0))
    return n2, hemi


def moments(x):
    d = x - x.mean()
    s2 = np.mean(d * d)
    return dict(rms=float(np.sqrt(s2)), skew=float(np.mean(d**3) / s2**1.5),
                exkurt=float(np.mean(d**4) / s2**2 - 3.0), maxabs=float(np.abs(x).max()))


def lu1():
    out = {}
    F = {}
    for tag, rd in (("U256", U256), ("U256m", U256M)):
        ds = nrsf.dumps(rd, base="usr")
        h = nrsf.header(ds[-1])
        f = nrsf.read(ds[-1], ["phi", "Pi", "K", "alpha"], h)
        hb = -f["K"].mean() / (3.0 * f["alpha"].mean())
        pib = f["Pi"].mean()
        R = (hb / pib) * (f["phi"] - f["phi"].mean())
        del f
        out[tag] = dict(time=h["time"], cycle=h["cycle"], H_b=float(hb), Pi_b=float(pib), **moments(R))
        F[tag] = np.fft.rfftn(R)
        del R
    N = F["U256"].shape[0]
    n2, hemi = hemisphere_n2(N)
    even = 0.5 * (F["U256"] + F["U256m"])
    odd = 0.5 * (F["U256"] - F["U256m"])
    for lab, lim in (("le1024", 1024), ("le4096", 4096)):
        m = hemi & (n2 > 0) & (n2 <= lim)
        out["even_over_odd_" + lab] = float(np.sqrt(np.sum(np.abs(even[m])**2) / np.sum(np.abs(odd[m])**2)))
        out["nmodes_" + lab] = int(m.sum())
    # spectrum of even/odd per shell for the figure
    sh = np.sqrt(n2[hemi & (n2 > 0) & (n2 <= 4096)])
    e2 = np.abs(even[hemi & (n2 > 0) & (n2 <= 4096)])**2
    o2 = np.abs(odd[hemi & (n2 > 0) & (n2 <= 4096)])**2
    kb = np.arange(1, 65)
    idx = np.clip(np.rint(sh).astype(int), 1, 64)
    E = np.bincount(idx, weights=e2, minlength=65)[1:]
    O = np.bincount(idx, weights=o2, minlength=65)[1:]
    out["shell_k"] = kb.tolist()
    out["shell_even_over_odd"] = np.sqrt(E / np.maximum(O, 1e-300)).tolist()
    return out


def parts(a, b):
    ho = 0.5 * (a["H"] - b["H"])
    he = 0.5 * (a["H"] + b["H"])
    he = he - he.mean()
    mo2 = sum((0.5 * (a[c] - b[c]))**2 for c in ("Mx", "My", "Mz"))
    me2 = 0.0
    for c in ("Mx", "My", "Mz"):
        e = 0.5 * (a[c] + b[c])
        me2 = me2 + (e - e.mean())**2
    return dict(H_odd=float(np.sqrt(np.mean(ho * ho))), H_even=float(np.sqrt(np.mean(he * he))),
                M_odd=float(np.sqrt(np.mean(mo2))), M_even=float(np.sqrt(np.mean(me2))))


def lu2():
    out = {}
    names = ["H", "Mx", "My", "Mz"]
    for i in (4, 6, 8):
        f = {}
        t = {}
        for r in ("U128p", "U128m", "U128hp", "U128hm"):
            p = nrsf.dumps(os.path.join(G1, r), base="usr")[i]
            h = nrsf.header(p)
            f[r] = nrsf.read(p, names, h)
            t[r] = h["time"]
        p1 = parts(f["U128p"], f["U128m"])
        ph = parts(f["U128hp"], f["U128hm"])
        d = dict(times=t)
        for c in ("H", "M"):
            o1, oh, e1, eh = p1[c + "_odd"], ph[c + "_odd"], p1[c + "_even"], ph[c + "_even"]
            f2 = (4 * oh**2 - o1**2) / 3.0
            d[c] = dict(raw_even=e1 / eh, raw_odd=o1 / oh, floor_f2=f2,
                        corrected_even=float(np.sqrt(e1**2 - f2) / np.sqrt(eh**2 - f2)) if (f2 > 0 and eh**2 > f2) else None,
                        parts_s1=dict(odd=o1, even=e1), parts_sh=dict(odd=oh, even=eh))
        out[f"dump{i}"] = d
        del f
    return out


def lu3():
    out = {}
    for tag, rd in (("U256", U256), ("U256m", U256M)):
        cols, data = nrsf.read_record(os.path.join(rd, "usr.sf.con.hst"))
        j = cols.index("<|M|/[M]>")
        e = cols.index("efolds=-ln<chi>/2")
        out[tag] = dict(M_ratio_max=float(data[:, j].max()), M_ratio_end=float(data[-1, j]),
                        cN_at_max=float(data[np.argmax(data[:, j]), e]), rows=int(data.shape[0]),
                        efolds=data[:, e].tolist()[::10], M_ratio=data[:, j].tolist()[::10])
    return out


def figure(res, out):
    sys.path.insert(0, HERE)
    import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 0.36 * fs.FULL_WIDTH))
    a = res["LU1"]
    ax[0].semilogy(a["shell_k"], a["shell_even_over_odd"], color=fs.PAL["blue"])
    ax[0].axhline(a["even_over_odd_le1024"], color=fs.PAL["red"], lw=0.8, ls="--")
    ax[0].axvline(32, color="grey", lw=0.6)
    ax[0].set_xlabel(r"shell $|n|$")
    ax[0].set_ylabel(r"even/odd of $\mathcal{R}_\phi$ at $N_f$")
    ax[0].set_title("(a) U256/U256m, own code", fontsize=8)
    b = res["LU2"]
    dumps = sorted(b)
    x = [2.06, 3.06, 4.05]
    for c, col in (("M", fs.PAL["blue"]), ("H", fs.PAL["green"])):
        ax[1].plot(x, [b[d][c]["raw_even"] for d in dumps], "o-", color=col, label=c + " even raw")
        ax[1].plot(x, [b[d][c]["corrected_even"] for d in dumps], "s--", color=col, mfc="none", label=c + " even corr.")
        ax[1].plot(x, [b[d][c]["raw_odd"] for d in dumps], "^:", color=col, label=c + " odd raw")
    ax[1].axhline(4, color="grey", lw=0.6)
    ax[1].axhline(2, color="grey", lw=0.6)
    ax[1].set_xlabel(r"$N - N_*$")
    ax[1].set_ylabel("halving factor (128$^3$)")
    ax[1].legend(fontsize=5, frameon=False)
    ax[1].set_title("(b) group 1, own code", fontsize=8)
    c = res["LU3"]
    for tag, col in (("U256", fs.PAL["blue"]), ("U256m", fs.PAL["red"])):
        ax[2].semilogy(c[tag]["efolds"], c[tag]["M_ratio"], color=col, label=tag, lw=1.2 if tag == "U256" else 0.8,
                       ls="-" if tag == "U256" else "--")
    ax[2].set_xlabel(r"$N - N_*$ (record)")
    ax[2].set_ylabel(r"$\langle|\mathcal{M}|/[\mathcal{M}]\rangle$")
    ax[2].legend(fontsize=6, frameon=False)
    ax[2].set_title("(c) records", fontsize=8)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(out, "fig_lead4." + ext), dpi=200)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = dict(LU3=lu3())
    print("LU3", json.dumps({k: {kk: v[kk] for kk in ("M_ratio_max", "M_ratio_end", "cN_at_max")} for k, v in res["LU3"].items()}), flush=True)
    res["LU2"] = lu2()
    print("LU2", json.dumps({d: {c: {k: res["LU2"][d][c][k] for k in ("raw_even", "raw_odd", "corrected_even")} for c in ("H", "M")} for d in res["LU2"]}), flush=True)
    res["LU1"] = lu1()
    print("LU1", json.dumps({k: v for k, v in res["LU1"].items() if not k.startswith("shell")}), flush=True)
    json.dump(res, open(os.path.join(a.out, "lead4_check.json"), "w"), indent=1)
    figure(res, a.out)


if __name__ == "__main__":
    main()
