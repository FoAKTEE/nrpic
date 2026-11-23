"""Figure of the smoke test S0 (JOURNAL entry 0): for each deck, a mid-plane slice of [H] (Hmag) and
of |H|/[H] at the last dump, and the record <|H|/[H]>, <|M|/[M]> against cycle.
Usage: python3 fig_smoke.py <S0 run dir> <out png>"""
import glob
import os
import struct
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle  # noqa: E402


def read_dump(path):
    with open(path, "rb") as f:
        f.read(8)
        nmb, nx1, nx2, nx3, nvar, cycle, nnoise = struct.unpack("<7q", f.read(56))
        (time,) = struct.unpack("<d", f.read(8))
        names = [f.read(16).rstrip(b"\0").decode() for _ in range(nvar)]
        f.read(4 * 8 + 6 * 8)
        n = nx1 * nx2 * nx3
        data = {nm: np.fromfile(f, dtype="<f8", count=n).reshape(nx3, nx2, nx1) for nm in names}
    return time, cycle, data


def main(run, out):
    figstyle.use_style()
    fig, axs = plt.subplots(2, 3, figsize=(10.5, 6.2))
    for row, case in enumerate(("sr", "usr")):
        d = os.path.join(run, case)
        dump = sorted(glob.glob(os.path.join(d, "*.dump")))[-1]
        t, cyc, data = read_dump(dump)
        k = data["Hmag"].shape[0] // 2
        im = axs[row, 0].imshow(data["Hmag"][k], origin="lower", cmap="viridis")
        fig.colorbar(im, ax=axs[row, 0], shrink=0.8)
        axs[row, 0].set_title("%s: [H] at t = %.3f (cycle %d)" % (case, t, cyc))
        rel = np.abs(data["H"][k]) / data["Hmag"][k]
        im = axs[row, 1].imshow(np.log10(rel + 1e-300), origin="lower", cmap="magma")
        fig.colorbar(im, ax=axs[row, 1], shrink=0.8)
        axs[row, 1].set_title("log10 |H|/[H], mid-plane")
        con = glob.glob(os.path.join(d, "*.sf.con.hst"))[0]
        rec = np.loadtxt(con, comments="#")
        axs[row, 2].semilogy(rec[:, 1], rec[:, 3], "o-", label="<|H|/[H]>")
        axs[row, 2].semilogy(rec[:, 1], np.maximum(rec[:, 6], 1e-300), "s-", label="<|M|/[M]>")
        axs[row, 2].set_xlabel("cycle")
        axs[row, 2].legend()
        axs[row, 2].set_title("record (con.hst columns 4, 7)")
    fig.suptitle("S0: decks as in arXiv:2512.14649 at 32^3, nmax2 = 64, 8 cycles (release processor build)")
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    print("wrote", out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
