#!/usr/bin/env python3
"""Review check R9 (journal entry 10): the per-mode records of Track E's three slow-roll
ablation runs at 256^3 (read-only), level against level.

    ablation_modes.py --out DIR --l0 RUNDIR --l1 RUNDIR --l2 RUNDIR [--dumps 2 6 10 15]

For each dump: rms over the modes of |c_R^a/c_R^b - 1| for (level 1, level 0),
(level 2, level 1), (level 2, level 0), all modes and in bands of |n|; and the same
pairs for the shell power, P(|n|^2) = mean over the modes of the shell of |c_R|^2 (the
power of the mesh field R with the amplitudes of the realisation divided out): rms and
maximum over the shells of |P^a/P^b - 1|.  The .rmodes files hold the projections
divided by L^-3/2 alpha_n.  Writes DIR/ablation_modes.json, DIR/fig_ablation_modes.png
and DIR/fig_ablation_power.png."""
import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import nl2                     # noqa: E402
import numpy as np             # noqa: E402

BANDS = ((0, 8), (8, 16), (16, 32), (32, 48), (48, 65))


def read(rd, k):
    f = glob.glob(os.path.join(rd, f"*.sf.{k:05d}.rmodes"))[0]
    with open(f) as fp:
        t = float(fp.readline().split()[2])
    d = np.loadtxt(f, comments="#", usecols=(3, 4, 5))
    return t, d[:, 0], d[:, 1] + 1j*d[:, 2]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--l0", required=True)
    ap.add_argument("--l1", required=True)
    ap.add_argument("--l2", required=True)
    ap.add_argument("--dumps", type=int, nargs="+", default=[2, 6, 10, 15])
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rows = []
    for k in a.dumps:
        t0, n2, c0 = read(a.l0, k)
        t1, _, c1 = read(a.l1, k)
        t2, _, c2 = read(a.l2, k)
        q = np.sqrt(n2)
        row = dict(dump=k, times=[t0, t1, t2])
        for name, x, y in (("L1-L0", c1, c0), ("L2-L1", c2, c1), ("L2-L0", c2, c0)):
            d = np.abs(x/y - 1.0)
            row[name] = dict(rms=float(np.sqrt(np.mean(d*d))), max=float(d.max()),
                             bands=[float(np.sqrt(np.mean(d[(q >= lo) & (q < hi)]**2)))
                                    for lo, hi in BANDS])
        # shell power: one value per |n|^2
        idx = n2.astype(int)
        cnt = np.bincount(idx)
        occ = cnt > 0
        qs = np.sqrt(np.nonzero(occ)[0])
        pw = [np.bincount(idx, weights=np.abs(c)**2)[occ]/cnt[occ] for c in (c0, c1, c2)]
        row["power"] = {}
        for name, x, y in (("L1/L0", pw[1], pw[0]), ("L2/L1", pw[2], pw[1]),
                           ("L2/L0", pw[2], pw[0])):
            d = x/y - 1.0
            row["power"][name] = dict(
                rms=float(np.sqrt(np.mean(d*d))), max=float(np.abs(d).max()),
                bands_rms=[float(np.sqrt(np.mean(d[(qs >= lo) & (qs < hi)]**2)))
                           for lo, hi in BANDS],
                bands_mean=[float(np.mean(d[(qs >= lo) & (qs < hi)]))
                            for lo, hi in BANDS])
        if k == a.dumps[-1]:
            np.savez(os.path.join(a.out, "power_last.npz"), q=qs, count=cnt[occ],
                     l1_l0=pw[1]/pw[0] - 1.0, l2_l1=pw[2]/pw[1] - 1.0,
                     l2_l0=pw[2]/pw[0] - 1.0)
        rows.append(row)
        print(json.dumps(row))
    nl2.dump_json(dict(l0=a.l0, l1=a.l1, l2=a.l2, bands=BANDS, rows=rows),
                  os.path.join(a.out, "ablation_modes.json"))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.8))
    fig.subplots_adjust(left=0.09, right=0.99, bottom=0.17, top=0.9, wspace=0.28)
    sty = (("L1-L0", "0.4", "x", "level 1 $-$ level 0"),
           ("L2-L1", fs.PAL["orange"], "o", "level 2 $-$ level 1"),
           ("L2-L0", fs.PAL["blue"], "s", "level 2 $-$ level 0"))
    for name, cl, mk, lab in sty:
        ax[0].semilogy([r["times"][0] for r in rows], [r[name]["rms"] for r in rows],
                       mk + "-", ms=3, color=cl, label=lab)
        ax[1].semilogy([0.5*(lo + hi) for lo, hi in BANDS], rows[-1][name]["bands"],
                       mk + "-", ms=3, color=cl, label=lab)
    ax[0].set_xlabel("$t$ (1/H$_*$)")
    ax[0].set_ylabel(r"rms$_n$ $|c_R^{(1)}/c_R^{(2)}-1|$")
    ax[0].set_title("(a) all modes, $256^3$, slow roll", fontsize=8)
    ax[0].legend(fontsize=6, loc="lower right")
    ax[1].set_xlabel("$|n|$ (band centre)")
    ax[1].set_ylabel("rms in the band")
    ax[1].set_title(f"(b) dump {rows[-1]['dump']}, $t = {rows[-1]['times'][0]:.2f}$",
                    fontsize=8)
    ax[1].legend(fontsize=6, loc="lower right")
    fig.savefig(os.path.join(a.out, "fig_ablation_modes.png"), dpi=200)
    plt.close(fig)

    z = np.load(os.path.join(a.out, "power_last.npz"))
    fig, ax = plt.subplots(1, 1, figsize=(fs.FULL_WIDTH*0.6, 2.9))
    fig.subplots_adjust(left=0.16, right=0.98, bottom=0.17, top=0.9)
    for key, cl, lab in (("l2_l0", fs.PAL["blue"], "level 2 / level 0"),
                         ("l2_l1", fs.PAL["orange"], "level 2 / level 1"),
                         ("l1_l0", "0.3", "level 1 / level 0")):
        ax.semilogy(z["q"], np.maximum(np.abs(z[key]), 1e-18), ".", ms=1.2, color=cl,
                    label=lab, rasterized=True)
    ax.set_xlabel("$|n|$")
    ax.set_ylabel(r"$|P^{(1)}/P^{(2)}-1|$ per shell of the mesh $R$")
    ax.set_title(f"$256^3$, slow roll, $t = {rows[-1]['times'][0]:.2f}$", fontsize=8)
    ax.set_ylim(1e-10, 1e-1)
    ax.legend(fontsize=6, loc="upper left", markerscale=6, ncol=3)
    fig.savefig(os.path.join(a.out, "fig_ablation_power.png"), dpi=200)


if __name__ == "__main__":
    main()
