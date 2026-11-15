#!/usr/bin/env python3
"""T-N5: the reader of the noise validation on real AthenaK `bin` output.

    python3 reader_test.py --athena EXE --input inputs/reader_test.athinput --out DIR

Runs the linear-wave initial data of AthenaK (processor executable, no evolution) with
1, 8 and 64 MeshBlocks, assembles z4c_gzz and z4c_gxy with athenak_io.assemble, and
compares (i) the three divisions bit for bit and (ii) the arrays with the formula of
athenak/src/pgen/tests/z4c_linear_wave.cpp (lines 88-145) at the cell centres;
(iii) the same comparison with x and z exchanged must fail (the reader's axis order).
Writes reader_test.json, summary.txt, fig_reader_test.png/pdf.
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import athenak_io as aio                                  # noqa: E402


def analytic(N, amp, k):
    kx1, kx2, kx3 = k
    th = np.arctan2(np.sqrt(kx2**2 + kx1**2), kx3)
    ph = np.arctan2(kx1, kx2)
    azz = np.sin(th)**2
    axy = -0.25 * (3 + np.cos(2 * th)) * np.sin(2 * ph)
    x = (np.arange(N) + 0.5) / N
    X, Y, Z = np.meshgrid(x, x, x, indexing="ij")
    s = np.sin(2 * np.pi * (kx1 * X + kx2 * Y + kx3 * Z))
    return 1 + azz * amp * s, axy * amp * s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--athena", required=True)
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    arrays = {}
    for b in (32, 16, 8):
        d = os.path.join(a.out, f"mb{b}")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "athena.log"), "w") as log:
            rc = subprocess.run([a.athena, "-i", os.path.abspath(a.input),
                                 f"meshblock/nx1={b}", f"meshblock/nx2={b}",
                                 f"meshblock/nx3={b}"], cwd=d, stdout=log,
                                stderr=subprocess.STDOUT).returncode
        if rc != 0:
            sys.exit(f"athena failed for b = {b}")
        files = sorted(f for f in os.listdir(os.path.join(d, "bin")) if f.endswith(".bin")) \
            if os.path.isdir(os.path.join(d, "bin")) else []
        path = os.path.join(d, "bin", files[0]) if files else None
        if path is None:
            cand = [os.path.join(r, f) for r, _, fs in os.walk(d) for f in fs
                    if f.endswith(".bin")]
            path = sorted(cand)[0]
        fd, prec = aio.read_bin_file(path)
        arrays[b] = dict(gzz=aio.assemble(fd, "z4c_gzz"), gxy=aio.assemble(fd, "z4c_gxy"),
                         n_mbs=int(fd["n_mbs"]), cycle=int(fd["cycle"]), prec=prec,
                         file=path)
    gzz_a, gxy_a = analytic(32, 0.1, (1, 2, 3))
    res = dict(n_meshblocks={b: v["n_mbs"] for b, v in arrays.items()},
               cycle={b: v["cycle"] for b, v in arrays.items()},
               precision=arrays[32]["prec"])
    res["bitwise_equal_1_8_64"] = bool(all(
        np.array_equal(arrays[32][v], arrays[b][v]) for b in (16, 8) for v in ("gzz", "gxy")))
    res["max_err_gzz"] = float(np.abs(arrays[8]["gzz"] - gzz_a).max())
    res["max_err_gxy"] = float(np.abs(arrays[8]["gxy"] - gxy_a).max())
    res["max_err_gzz_axes_exchanged"] = float(
        np.abs(arrays[8]["gzz"].transpose(2, 1, 0) - gzz_a).max())
    res["prediction_holds"] = bool(res["bitwise_equal_1_8_64"] and res["max_err_gzz"] < 1e-6
                                   and res["max_err_gxy"] < 1e-6
                                   and res["max_err_gzz_axes_exchanged"] > 1e-3)
    with open(os.path.join(a.out, "reader_test.json"), "w") as f:
        json.dump(res, f, indent=1)
    with open(os.path.join(a.out, "summary.txt"), "w") as f:
        f.write(json.dumps(res) + "\n")
    print(json.dumps(res, indent=1))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, os.path.join(aio.REPO, "python"))
    from nrpic import figstyle as fs
    fs.use_style()
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.7))
    k = 5
    ext = [0, 1, 0, 1]
    im0 = ax[0].imshow((arrays[8]["gzz"][:, :, k] - 1).T, origin="lower", extent=ext,
                       cmap=fs.CMAP["diverging"], vmin=-0.1, vmax=0.1)
    ax[0].set_title("read, 64 MeshBlocks", fontsize=9)
    ax[1].imshow((gzz_a[:, :, k] - 1).T, origin="lower", extent=ext,
                 cmap=fs.CMAP["diverging"], vmin=-0.1, vmax=0.1)
    ax[1].set_title("formula at cell centres", fontsize=9)
    err = (arrays[8]["gzz"][:, :, k] - gzz_a[:, :, k]).T
    im2 = ax[2].imshow(err / 1e-8, origin="lower", extent=ext, cmap=fs.CMAP["diverging"],
                       vmin=-6, vmax=6)
    ax[2].set_title(r"difference / $10^{-8}$", fontsize=9)
    for x in ax:
        x.set_xlabel("x")
    ax[0].set_ylabel("y")
    fs.side_colorbar(fig, ax[1], im0, r"$\tilde\gamma_{zz}-1$")
    fs.side_colorbar(fig, ax[2], im2, "")
    fig.tight_layout()
    fs.save(fig, os.path.join(a.out, "fig_reader_test"))


if __name__ == "__main__":
    main()
