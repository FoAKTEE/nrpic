#!/usr/bin/env python3
"""V4, energies of the TT part of the first-source scan (JOURNAL entry 14).

For every z4c dump with a >= 12 (t >= 2 (sqrt 12 - 1)) of the scan runs:
  h = Lambda(ht), ht = gt/det(gt)^(1/3) - delta;  hdot = -2 Lambda(At) (proper time of the
  normal observers, gw_diag's definition);
  rho_kin  ~ < hdot_ij hdot_ij >,  rho_grad ~ chibar < d_k h_ij d_k h_ij >  (chibar = mean chi),
  ratio = rho_kin / rho_grad (the common factor 1/(64 pi G) cancels);
  the same restricted to the modes |m| = sqrt 2 (the (k,k,0) family).
Writes $NRPIC_RUN_DIR/v4_energy.json and v4_energy.png/pdf. Env: V4E_WORKERS (default 4).
"""
import glob
import json
import os
import sys
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import diag  # noqa: E402
import figstyle as fs  # noqa: E402
import v4lib  # noqa: E402

OUT = os.environ.get("NRPIC_RUN_DIR", os.path.join(HERE, "..", "results", "tmp_v4e"))
os.makedirs(OUT, exist_ok=True)
SCR = "/data/haiyangw/nrpic/scratch/B-emd-gw"
RUNS = {"64 eps1 zs": "B-20261115-165353-b592d43/cw_eps1",
        "64 eps1 gd": "B-20261115-165353-b592d43/cw_eps1_gd",
        "64 eps0.3 zs": "B-20261115-164059-d802e82/cw_eps0p3",
        "64 eps0.1 zs": "B-20261115-164059-d802e82/cw_eps0p1",
        "64 eps0 zs": "B-20261115-164059-d802e82/cw_eps0",
        "32 eps1 zs": "B-20261115-165525-f7c2004/cw_eps1",
        "32 eps1 gd": "B-20261115-165525-f7c2004/cw_eps1_gd"}
T12 = 2 * (np.sqrt(12.0) - 1)
EYE = np.eye(3)[:, :, None, None, None]


def header_time(path):
    with open(path, "rb") as f:
        raw = f.read(400).decode("latin1")
    for line in raw.splitlines():
        if line.strip().startswith("time="):
            return float(line.split("=", 1)[1])
    raise ValueError(path)


def work(item):
    label, path = item
    d = diag.read_bin(path)
    g = d["grid"]
    gt = diag.sym_from(d["vars"], "z4c_g")
    At = diag.sym_from(d["vars"], "z4c_A")
    chib = float(d["vars"]["z4c_chi"].mean())
    h = diag.tt_project(v4lib.conformal(gt) - EYE, g)
    hd = diag.tt_project(-2.0 * At, g)
    kx, ky, kz = g.kvecs(real=False)
    k2 = kx ** 2 + ky ** 2 + kz ** 2
    Fh = np.fft.fftn(h, axes=(-3, -2, -1)) / np.prod(g.n)
    Fd = np.fft.fftn(hd, axes=(-3, -2, -1)) / np.prod(g.n)
    Ph = np.sum(np.abs(Fh) ** 2, axis=(0, 1))
    Pd = np.sum(np.abs(Fd) ** 2, axis=(0, 1))
    kin = float(np.sum(Pd))
    grad = chib * float(np.sum(k2 * Ph))
    k0 = 2 * np.pi / g.L[0]
    sel = np.isclose(k2, 2 * k0 ** 2)
    kin_s = float(np.sum(Pd[sel]))
    grad_s = chib * float(np.sum(k2[sel] * Ph[sel]))
    a = (1 + d["time"] / 2) ** 2
    return {"run": label, "t": d["time"], "a": a, "a_chi": chib ** -0.5, "kin": kin, "grad": grad,
            "ratio": kin / grad if grad > 0 else None,
            "ratio |m|=sqrt2": kin_s / grad_s if grad_s > 0 else None}


def main():
    items = []
    for label, sub in RUNS.items():
        for f in sorted(glob.glob(f"{SCR}/{sub}/bin/*.z4c.*.bin")):
            if header_time(f) >= T12 - 1e-9:
                items.append((label, f))
    with Pool(int(os.environ.get("V4E_WORKERS", "4"))) as pool:
        res = pool.map(work, items, chunksize=4)
    out = {}
    for label in RUNS:
        S = sorted([r for r in res if r["run"] == label], key=lambda r: r["t"])
        if not S:
            continue
        rr = np.array([r["ratio"] for r in S], float)
        rs = np.array([r["ratio |m|=sqrt2"] for r in S], float)
        i = int(np.nanargmax(rr))
        j = int(np.nanargmax(rs))
        out[label] = {"n_dumps": len(S), "a range": [S[0]["a"], S[-1]["a"]],
                      "max ratio": float(rr[i]), "at a": S[i]["a"],
                      "ratio at a=12": float(rr[0]), "ratio at end": float(rr[-1]),
                      "max ratio |m|=sqrt2": float(rs[j]), "at a (|m|=sqrt2)": S[j]["a"],
                      "series": S}
        print(label, {k: v for k, v in out[label].items() if k != "series"}, flush=True)
    with open(os.path.join(OUT, "v4_energy.json"), "w") as fh:
        json.dump(out, fh)

    fs.use_style()
    import matplotlib.pyplot as plt  # noqa: E402
    fig, ax = plt.subplots(figsize=(fs.COLUMN_WIDTH * 1.6, 3.4))
    fig.subplots_adjust(left=0.13, right=0.97, bottom=0.15, top=0.96)
    cols = [fs.PAL["blue"], fs.PAL["red"], fs.PAL["yellow"], fs.PAL["green"], "k", "grey", "purple"]
    for (label, rec), col in zip(out.items(), cols):
        S = rec["series"]
        ls = "--" if label.startswith("32") else "-"
        ax.semilogy([r["a"] for r in S], [r["ratio"] for r in S], ls, color=col, lw=1.0, label=label)
    a = np.linspace(12, 140, 200)
    ax.semilogy(a, 4 * (1 / np.sqrt(a)) ** 2 / (2 * (np.pi / 2) ** 2), ":", color="grey", lw=0.8,
                label=r"$4\mathcal{H}^2/k^2$, $k=|(k_0,k_0,0)|$")
    ax.set_xlabel("a", labelpad=-2)
    ax.set_ylabel(r"$\rho_{\rm kin}/\rho_{\rm grad}$ of the TT part")
    ax.legend(loc="upper right", fontsize=6, ncol=2)
    fs.save(fig, os.path.join(OUT, "v4_energy"))


if __name__ == "__main__":
    main()
