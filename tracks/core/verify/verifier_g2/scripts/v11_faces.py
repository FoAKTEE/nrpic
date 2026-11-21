#!/usr/bin/env python3
"""V11: outer faces of Z4c (core-v0.6, interfaces/z4c_faces.md), boundary-cell constraint.

Claims: (H1) with stock linear ghost extrapolation the monitor's H in the boundary cell
of a vacuum puncture after one step is 1.9e-3 = 0.79 of the stencil estimate
8 x 1.117 m/r^3; with extrapolation orders 3, 4: 0.18 and 0.048 of it (stencil 0.175,
0.041) (run core-20261119-143938-eded041, cases punc_e2..e4). (a0, a0b, c0) fall-off
ghosts lower the boundary layer about 12 times at every order.
Own derivation of the estimate: sixth-order second derivative
(2, -27, 270, -490, 270, -27, 2)/180 reading ghosts filled by Lagrange extrapolation of
p points, ghost error C_k(p) f^(p) dx^p with C_k = k(k+1)...(k+p-1)/p!; coefficient in
the boundary cell (270 C_1 - 27 C_2 + 2 C_3)/180 = 201/180, 182/180, 165/180 for p = 2,
3, 4; f = m/(2x) along the face normal (H ~ -8 psi^-5 lap psi, linear in the ghost error).
Fresh runs (release core-v0.6 processor executable): the same puncture input, one step,
extrap_order 2 and 4, stock and ghost_falloff = true.
Own reader of AthenaK .bin (outputs/binary.cpp: text preheader, 'header offset=N', N
bytes of parameters, per MeshBlock 10 int32, 6 float64 extents, nvar x cells values of
'size of variable' bytes). Reader check: chi of z4c.00000.bin against psi^-4,
psi = 1 + m/(2r), away from the puncture.

usage: v11_faces.py EXE INPUT A0B_RUNDIR OUTDIR
"""
import json
import os
import re
import subprocess
import sys

import numpy as np

M = 1.0
FACE = 16.0


def read_bin(path):
    b = open(path, "rb").read()
    head_end = b.find(b"header offset=")
    line_end = b.find(b"\n", head_end)
    head = b[:line_end].decode()
    hoff = int(re.search(r"header offset=(\d+)", head).group(1))
    vsize = int(re.search(r"size of variable=(\d+)", head).group(1))
    names = re.search(r"variables:\s*(.*)", head).group(1).split()
    t = float(re.search(r"time=(\S+)", head).group(1))
    off = line_end + 1 + hoff
    dt = "<f4" if vsize == 4 else "<f8"
    blocks = []
    while off < len(b):
        ii = np.frombuffer(b, "<i4", 10, off)
        off += 40
        ext = np.frombuffer(b, "<f8", 6, off)
        off += 48
        n1, n2, n3 = ii[1] - ii[0] + 1, ii[3] - ii[2] + 1, ii[5] - ii[4] + 1
        nc = n1 * n2 * n3
        d = np.frombuffer(b, dt, len(names) * nc, off).reshape(len(names), n3, n2, n1)
        off += vsize * len(names) * nc
        blocks.append((int(ii[9]), ext, d))
    assert off == len(b)
    return t, names, blocks


def cell_centres(ext, shape):
    n3, n2, n1 = shape
    x = ext[0] + (np.arange(n1) + 0.5) * (ext[1] - ext[0]) / n1
    y = ext[2] + (np.arange(n2) + 0.5) * (ext[3] - ext[2]) / n2
    z = ext[4] + (np.arange(n3) + 0.5) * (ext[5] - ext[4]) / n3
    Z, Y, X = np.meshgrid(z, y, x, indexing="ij")
    return X, Y, Z


def face_cells(path, var="con_H"):
    """|H| in the boundary cells next to the six face centres (|transverse| < dx)."""
    t, names, blocks = read_bin(path)
    k = names.index(var)
    vals = []
    for lev, ext, d in blocks:
        X, Y, Z = cell_centres(ext, d.shape[1:])
        dx = (ext[1] - ext[0]) / d.shape[3]
        for A, B, C in ((X, Y, Z), (Y, Z, X), (Z, X, Y)):
            sel = (np.abs(np.abs(A) - (FACE - dx / 2)) < 1e-9) & (np.abs(B) < dx) & (np.abs(C) < dx)
            vals.extend(np.abs(d[k][sel]).tolist())
    return t, np.array(vals), dx


def reader_check(path):
    t, names, blocks = read_bin(path)
    k = names.index("z4c_chi")
    worst = 0.0
    for lev, ext, d in blocks:
        X, Y, Z = cell_centres(ext, d.shape[1:])
        r = np.sqrt(X * X + Y * Y + Z * Z)
        psi = 1 + M / (2 * r)
        sel = r > 2.0
        if sel.any():
            worst = max(worst, float(np.max(np.abs(d[k][sel] - psi[sel] ** -4))))
    return t, worst


def coef(p):
    from math import factorial
    C = [np.prod([kk + j for j in range(p)]) / factorial(p) for kk in (1, 2, 3)]
    return (270 * C[0] - 27 * C[1] + 2 * C[2]) / 180.0


def main():
    exe, inp, a0b, outdir = sys.argv[1:5]
    os.makedirs(outdir, exist_ok=True)
    r_b = FACE - 0.5  # boundary cell centre at the face centre, dx = 1 on the root level
    est2 = 8 * coef(2) * M / r_b ** 3
    est = {"coef_p2": coef(2), "coef_p3": coef(3), "coef_p4": coef(4), "estimate_p2": est2,
           "ratio_p3_over_p2": coef(3) * 3 * 1.0 / r_b / coef(2),
           "ratio_p4_over_p2": coef(4) * 12 * 1.0 / r_b ** 2 / coef(2)}
    res = {"own_estimate": est, "a0b": {}, "fresh": {}}
    t0, chk = reader_check(os.path.join(a0b, "punc_e2", "bin", "punc.z4c.00000.bin"))
    res["reader_check_chi_vs_psi^-4_r>2_t0"] = chk
    for o in (2, 3, 4):
        t, v, dx = face_cells(os.path.join(a0b, f"punc_e{o}", "bin", "punc.con.00001.bin"))
        res["a0b"][f"e{o}"] = {"t": t, "n_cells": int(len(v)), "mean_abs_H": float(v.mean()),
                               "max_abs_H": float(v.max()), "dx": dx}
    e2 = res["a0b"]["e2"]["mean_abs_H"]
    res["a0b"]["e2_over_estimate"] = e2 / est2
    res["a0b"]["e3_over_e2"] = res["a0b"]["e3"]["mean_abs_H"] / e2
    res["a0b"]["e4_over_e2"] = res["a0b"]["e4"]["mean_abs_H"] / e2
    # fresh runs on the release executable
    for o in (2, 4):
        for fall in (False, True):
            name = f"e{o}_{'falloff' if fall else 'stock'}"
            d = os.path.join(outdir, name)
            os.makedirs(d, exist_ok=True)
            cmd = [exe, "-i", inp, "-d", d, "time/nlim=1", f"z4c/extrap_order={o}"]
            if fall:
                cmd.append("z4c/ghost_falloff=true")
            with open(os.path.join(d, "stdout.txt"), "w") as fh:
                rc = subprocess.call(cmd, cwd=d, stdout=fh, stderr=subprocess.STDOUT,
                                     env=dict(os.environ, OMP_NUM_THREADS="1"))
            ent = {"rc": rc}
            if rc == 0:
                for cyc in (0, 1):
                    t, v, dx = face_cells(os.path.join(d, "bin", f"punc.con.{cyc:05d}.bin"))
                    ent[f"cycle{cyc}"] = {"t": t, "mean_abs_H": float(v.mean()), "max_abs_H": float(v.max())}
            res["fresh"][name] = ent
    for o in (2, 4):
        s, f = res["fresh"].get(f"e{o}_stock", {}), res["fresh"].get(f"e{o}_falloff", {})
        if "cycle1" in s and "cycle1" in f:
            res["fresh"][f"gain_e{o}_cycle1"] = s["cycle1"]["mean_abs_H"] / f["cycle1"]["mean_abs_H"]
            res["fresh"][f"gain_e{o}_cycle0"] = s["cycle0"]["mean_abs_H"] / f["cycle0"]["mean_abs_H"]
    if "cycle1" in res["fresh"].get("e2_stock", {}):
        res["fresh"]["e2_stock_cycle1_vs_a0b_e2"] = res["fresh"]["e2_stock"]["cycle1"]["mean_abs_H"] / e2
    with open(os.path.join(outdir, "v11_faces.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(res, indent=1))

    import matplotlib
    matplotlib.use("Agg")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.8))
    orders = [2, 3, 4]
    meas = [res["a0b"][f"e{o}"]["mean_abs_H"] for o in orders]
    own = [est2, est2 * est["ratio_p3_over_p2"], est2 * est["ratio_p4_over_p2"]]
    axs[0].semilogy(orders, meas, "o-", color=fs.PAL["blue"], label="a0b runs (stock ghosts)")
    axs[0].semilogy(orders, own, "x--", color="k", label="own stencil estimate")
    axs[0].set_xticks(orders)
    axs[0].set_xlabel("extrapolation order")
    axs[0].set_ylabel("|H| in the boundary cell, face centre")
    axs[0].legend(fontsize=7)
    labels, vals, cols = [], [], []
    for o in (2, 4):
        for fall, c in ((False, fs.PAL["red"]), (True, fs.PAL["green"])):
            e = res["fresh"].get(f"e{o}_{'falloff' if fall else 'stock'}", {})
            if "cycle1" in e:
                labels.append(f"order {o}\n{'falloff' if fall else 'stock'}")
                vals.append(e["cycle1"]["mean_abs_H"])
                cols.append(c)
    axs[1].bar(range(len(vals)), vals, color=cols)
    axs[1].set_yscale("log")
    axs[1].set_xticks(range(len(vals)))
    axs[1].set_xticklabels(labels, fontsize=7)
    axs[1].set_ylabel("|H| boundary cell, after one step")
    fig.suptitle("V11: Z4c outer faces, puncture at 16 M (a0b core-20261119-143938-eded041; fresh runs on core-v0.6)", fontsize=8)
    fig.tight_layout()
    fs.save(fig, os.path.join(outdir, "fig_v11_faces"))


if __name__ == "__main__":
    main()
