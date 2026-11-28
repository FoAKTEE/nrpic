#!/usr/bin/env python3
"""OH of threshold_ball (JOURNAL entry 18, batch 34): the Hamiltonian constraint recomputed offline
on the x line from the run's own ADM tables (gamma_ij, K_ij) and deposited E, under spherical
symmetry, against the code's pointwise con_H on the same line.

    offline_h_line.py --out DIR NAME=TABDIR [NAME=TABDIR ...] [--times 0 0.5 0.75 1.0]

The tab output samples the cells that contain y = z = 0.01, i.e. y = z = h/2 of each level (h read
from the spacing of consecutive rows). A spherically symmetric tensor in Cartesian components is
T_ij = b delta_ij + d n_i n_j; with n = (x, h/2, h/2)/r: T_xx - T_yy = d (n_x^2 - n_y^2),
b = T_yy - d n_y^2; radial A = b + d, tangential B = b. For dl^2 = A dr^2 + R^2 dOmega^2 with
R = r sqrt(B):  3R = -(4/(R sqrt A)) d/dr[(1/sqrt A) dR/dr] + (2/R^2)(1 - R'^2/A);
K = K_A/A + 2 K_B/B, K_ij K^ij = (K_A/A)^2 + 2 (K_B/B)^2;  H = 3R + K^2 - K_ij K^ij - 16 pi E.
Derivatives: quartic least-squares fits through the five nearest rows of the same level (x > 0 rows
only, none across a level face); rows closer than two rows to a face or with r < 0.15 are dropped.
Writes DIR/offline_h.json and DIR/fig_offline_h.{pdf,png}.
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def read_tab(path):
    with open(path) as f:
        first = f.readline()
        names = f.readline().strip("# \n").split()
    t = float(first.split("time=")[1].split()[0])
    d = np.loadtxt(path, comments="#", ndmin=2)
    return t, {n: d[:, i] for i, n in enumerate(names)}


def segments(x):
    """indices of runs of equal spacing (one refinement level each)."""
    dx = np.diff(x)
    segs, start = [], 0
    for i in range(1, len(dx)):
        if abs(dx[i] - dx[i - 1]) > 1e-9 * max(dx[i], dx[i - 1]):
            segs.append((start, i + 1))       # rows start..i inclusive share spacing dx[start..i-1]
            start = i
    segs.append((start, len(x)))
    return segs, dx


def deriv_fit(r, f, idx, k=2):
    """first and second derivative at r[idx] from a quartic fit through idx-k..idx+k."""
    sl = slice(idx - k, idx + k + 1)
    rr = r[sl] - r[idx]
    c = np.polyfit(rr, f[sl], 4)
    return c[-2], 2.0 * c[-3]


def offline(adm, tm, con):
    x = adm["x1v"]
    sel = x > 0
    x = x[sel]
    order = np.argsort(x)
    x = x[order]
    g = {k: adm["adm_" + k][sel][order] for k in ("gxx", "gyy", "gxy", "Kxx", "Kyy")}
    E = tm["tmunu_E"][sel][order]
    Hc = con["con_H"][sel][order]
    segs, dx = segments(x)
    h = np.empty_like(x)
    for a, b in segs:
        hh = (x[min(b - 1, a + 1)] - x[a]) if b - a > 1 else np.nan
        h[a:b] = hh
    yo = 0.5 * h
    r = np.sqrt(x * x + 2.0 * yo * yo)
    nx, ny = x / r, yo / r
    w = nx * nx - ny * ny
    dg = (g["gxx"] - g["gyy"]) / w
    B = g["gyy"] - dg * ny * ny
    A = B + dg
    dk = (g["Kxx"] - g["Kyy"]) / w
    KB = g["Kyy"] - dk * ny * ny
    KA = KB + dk
    Rr = r * np.sqrt(B)
    out = []
    for a, b in segs:
        for i in range(a + 2, b - 2):
            if r[i] < 0.15:
                continue
            Rp, Rpp = deriv_fit(r, Rr, i)
            Ap, _ = deriv_fit(r, A, i)
            dprod = Rpp / np.sqrt(A[i]) - 0.5 * Rp * Ap / A[i] ** 1.5   # d/dr[(1/sqrt A) dR/dr]
            R3 = -4.0 / (Rr[i] * np.sqrt(A[i])) * dprod + 2.0 / Rr[i] ** 2 * (1.0 - Rp * Rp / A[i])
            kA, kB = KA[i] / A[i], KB[i] / B[i]
            K = kA + 2.0 * kB
            KK = kA * kA + 2.0 * kB * kB
            Hoff = R3 + K * K - KK - 16.0 * np.pi * E[i]
            out.append(dict(x=float(x[i]), r=float(r[i]), h=float(h[i]), H_off=float(Hoff),
                            H_code=float(Hc[i]), E16=float(16.0 * np.pi * E[i]), R3=float(R3)))
    return out


def rms(v):
    v = np.asarray(v, float)
    return float(np.sqrt(np.mean(v * v))) if v.size else float("nan")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("members", nargs="+", help="NAME=TABDIR")
    ap.add_argument("--out", required=True)
    ap.add_argument("--times", type=float, nargs="*", default=[0.0, 0.25, 0.5, 0.75, 1.0])
    ap.add_argument("--rmax", type=float, default=4.5)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = {}
    for m in a.members:
        name, d = m.split("=", 1)
        files = sorted(glob.glob(os.path.join(d, "*.adm.*.tab")))
        rows = []
        for fa in files:
            num = fa.split(".adm.")[1]
            fc = fa.replace(".adm.", ".con.")
            ft = fa.replace(".adm.", ".tmunu.")
            if not (os.path.exists(fc) and os.path.exists(ft)):
                continue
            t, adm = read_tab(fa)
            if not any(abs(t - tt) < 1e-6 for tt in a.times):
                continue
            _, con = read_tab(fc)
            _, tm = read_tab(ft)
            pts = [p for p in offline(adm, tm, con) if p["r"] <= a.rmax]
            dH = [p["H_off"] - p["H_code"] for p in pts]
            rows.append(dict(t=t, file=num, n=len(pts), rms_code=rms([p["H_code"] for p in pts]),
                             rms_off=rms([p["H_off"] for p in pts]), rms_diff=rms(dH),
                             rms_E16=rms([p["E16"] for p in pts]), points=pts))
            print("%-8s t=%.3f n=%3d rms con_H=%.3e  rms H_off=%.3e  rms diff=%.3e  rms 16piE=%.3e"
                  % (name, t, len(pts), rows[-1]["rms_code"], rows[-1]["rms_off"], rows[-1]["rms_diff"],
                     rows[-1]["rms_E16"]))
        res[name] = rows
    json.dump(res, open(os.path.join(a.out, "offline_h.json"), "w"), indent=1)

    sys.path.insert(0, os.path.join(HERE, "..", "..", "note", "scripts"))
    import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.7))
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.18, top=0.86, wspace=0.42)
    cols = [fs.PAL["blue"], fs.PAL["red"], fs.PAL["green"], fs.PAL["yellow"]]
    for k, (name, rows) in enumerate(res.items()):
        c = cols[k % len(cols)]
        t = [q["t"] for q in rows]
        ax[0].semilogy(t, [q["rms_code"] for q in rows], color=c, marker="o", ms=3, label=name + ": code")
        ax[0].semilogy(t, [q["rms_off"] for q in rows], color=c, marker="s", ms=3, ls="--", label=name + ": offline")
        ax[0].semilogy(t, [q["rms_diff"] for q in rows], color=c, marker="^", ms=3, ls=":", label=name + ": diff")
        last = [q for q in rows if abs(q["t"] - max(t)) < 1e-9]
        if last:
            p = last[0]["points"]
            ax[1].semilogy([q["r"] for q in p], [abs(q["H_code"]) for q in p], color=c, lw=1.0, label=name + ": code")
            ax[1].semilogy([q["r"] for q in p], [abs(q["H_off"]) for q in p], color=c, lw=1.0, ls="--",
                           label=name + ": offline")
            ax[2].plot([q["r"] for q in p], [q["H_off"] - q["H_code"] for q in p], color=c, lw=1.0, label=name)
    ax[0].set_xlabel(r"$t/M$")
    ax[0].set_ylabel(r"rms of $H$ on the line")
    ax[0].set_title("(a) code, offline, difference", fontsize=8)
    ax[0].legend(fontsize=5, ncol=1)
    ax[1].set_xlabel(r"$r/M$")
    ax[1].set_ylabel(r"$|H|$ at the last time")
    ax[1].set_title("(b) profiles", fontsize=8)
    ax[1].legend(fontsize=5)
    ax[2].set_xlabel(r"$r/M$")
    ax[2].set_ylabel(r"$H_{\rm off} - H_{\rm code}$")
    ax[2].set_title("(c) difference at the last time", fontsize=8)
    ax[2].legend(fontsize=5)
    fs.save(fig, os.path.join(a.out, "fig_offline_h"))


if __name__ == "__main__":
    main()
