"""D2 of ../JOURNAL.md: MeshBlock-by-MeshBlock separable synthesis of a band-limited
real field against numpy.fft.ifftn, and the operation count of the method.

Usage: python3 -I d2_synthesis.py <outdir>     (writes d2.json and the figure d2_synthesis)
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "../../../../python")))
import synth                                     # noqa: E402
from nrpic import figstyle as fs                 # noqa: E402
import matplotlib.pyplot as plt                  # noqa: E402


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    rng = np.random.default_rng(20261115)
    res = {"cases": []}
    for N in (32, 64):
        nmax = N//4
        L = 2.0*np.pi          # k_min = 1
        n = synth.ball_modes(nmax)
        # coefficients with a red spectrum, Hermitian
        a = synth.hermitian_gaussian(n, rng)
        kk = np.sqrt((n**2).sum(axis=1))
        c = a*kk**-1.5
        ref = synth.synth_fft(n, c, N, L, x0=-np.pi)
        rms = np.sqrt(np.mean(ref.real**2))
        fields = {}
        for b in (N//4, N//2, N):
            t0 = time.time()
            f, ops = synth.synth_mesh(n, c, N, L, b, x0=-np.pi)
            dt = time.time() - t0
            fields[b] = f
            case = dict(N=N, nmax=nmax, block=b, modes=int(len(n)),
                        err_vs_fft=float(np.max(np.abs(f.real - ref.real))/rms),
                        imag_rel=float(np.max(np.abs(f.imag))/rms),
                        ops=int(ops), ops_formula=int(synth.synth_ops(N, nmax, b)),
                        seconds=dt)
            res["cases"].append(case)
            print(case)
        bs = sorted(fields)
        res.setdefault("cross_block", []).append(dict(
            N=N, blocks=bs,
            max_rel=float(max(np.max(np.abs(fields[b].real - fields[bs[-1]].real))
                              for b in bs)/rms)))
    # operation counts for the production sizes (formula, checked above on small sizes)
    table = []
    for N in (32, 64, 128, 256, 512):
        nmax = N//4
        for b in (32, 64, 128, 256):
            if b > N:
                continue
            ops = synth.synth_ops(N, nmax, b)
            opsh = synth.synth_ops(N, nmax, b, hermitian=True)
            table.append(dict(N=N, nmax=nmax, block=b, cmacs=int(ops),
                              cmacs_hermitian=int(opsh),
                              per_cell=ops/N**3, per_cell_hermitian=opsh/N**3,
                              fft_flops_est=float(5*N**3*np.log2(N**3))))
    res["ops_table"] = table
    with open(os.path.join(outdir, "d2.json"), "w") as fh:
        json.dump(res, fh, indent=1)

    # figure: left, error against the FFT per case; right, operations per cell
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.2))
    ax1 = fig.add_axes([0.08, 0.15, 0.38, 0.78])
    ax2 = fig.add_axes([0.58, 0.15, 0.38, 0.78])
    for N, col in ((32, fs.PAL["blue"]), (64, fs.PAL["red"])):
        cs = [c for c in res["cases"] if c["N"] == N]
        ax1.plot([c["block"] for c in cs], [c["err_vs_fft"] for c in cs], "o-",
                 color=col, label=f"N = {N}, real part")
        ax1.plot([c["block"] for c in cs], [c["imag_rel"] for c in cs], "s--",
                 color=col, label=f"N = {N}, imaginary part")
    ax1.axhline(1e-12, **fs.GUIDE)
    ax1.text(8.5, 1.6e-12, "refutation level", fontsize=8)
    ax1.set_xscale("log", base=2)
    ax1.set_yscale("log")
    ax1.set_ylim(1e-18, 1e-7)
    ax1.set_xlabel("MeshBlock size b (cells)")
    ax1.set_ylabel("max |f - f_FFT| / rms(f)")
    ax1.legend(fontsize=8, loc="upper left", ncol=1)
    for b, col in ((32, fs.PAL["blue"]), (64, fs.PAL["red"]), (128, fs.PAL["yellow"]),
                   (256, fs.PAL["green"])):
        rows = [r for r in table if r["block"] == b]
        ax2.plot([r["N"] for r in rows], [r["per_cell_hermitian"] for r in rows], "o-",
                 color=col, label=f"b = {b}")
    Ns = np.array([32, 64, 128, 256, 512])
    ax2.plot(Ns, 5*np.log2(Ns**3)/8, **fs.GUIDE, label="FFT, 5 N^3 log2 N^3 / 8")
    ax2.set_xscale("log", base=2)
    ax2.set_yscale("log")
    ax2.set_xlabel("cells per side N (n_max = N/4)")
    ax2.set_ylabel("complex multiply-adds per cell")
    ax2.legend(fontsize=8, loc="upper left", ncol=2)
    fs.save(fig, os.path.join(outdir, "d2_synthesis"))


if __name__ == "__main__":
    main(sys.argv[1])
