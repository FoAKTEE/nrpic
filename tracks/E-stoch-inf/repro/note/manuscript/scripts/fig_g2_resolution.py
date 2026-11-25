"""Figure: the ultra-slow-roll lattice at 256^3 and 320^3 cells, same modes, same random amplitudes.

Reads judge_g2.json of E-20261123-024359-5dc3213 (checked against its sha256sums.txt):
- pairs.A.shell_max, pairs.R320.shell_max: per shell |n|^2, the largest departure D of the odd
  part (first order in the amplitude) of the curvature perturbation per mode from the code's own
  linear mode functions at N_f, on 256^3 and 320^3;
- U_R._k, U_R._rat: per shell, the power on 320^3 over that on 256^3, minus one.
Writes OUT/fig_g2_resolution.{pdf,png,json}.

    fig_g2_resolution.py OUT
"""
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figstyle as fs  # noqa: E402

JUDGE = "/data/haiyangw/nrpic/scratch/E-stoch-inf/E-20261123-024359-5dc3213"


def sha_ok(run_dir, rel):
    want = None
    for ln in open(os.path.join(run_dir, "sha256sums.txt")):
        h, f = ln.split(None, 1)
        if f.strip().lstrip("*").lstrip("./") == rel:
            want = h
    got = hashlib.sha256(open(os.path.join(run_dir, rel), "rb").read()).hexdigest()
    if want != got:
        sys.exit(f"checksum of {run_dir}/{rel} does not match its sha256sums.txt")


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    sha_ok(JUDGE, "judge_g2.json")
    J = json.load(open(os.path.join(JUDGE, "judge_g2.json")))
    sa, sr = J["pairs"]["A"]["shell_max"], J["pairs"]["R320"]["shell_max"]
    k2 = np.array(sorted(int(x) for x in sa))
    d256 = np.array([sa[str(x)] for x in k2])
    d320 = np.array([sr[str(x)] for x in k2])
    kk = np.sqrt(k2)
    rat = d256 / d320
    UR = J["U_R"]
    fs.use_style()
    import matplotlib.pyplot as plt
    cols = fs.SERIES
    fig, ax = plt.subplots(2, 1, figsize=(fs.COLUMN_WIDTH, 4.6), sharex=True)
    fig.subplots_adjust(left=0.17, right=0.97, top=0.98, bottom=0.1, hspace=0.08)
    a = ax[0]
    a.semilogy(kk, d256, ".", ms=2.2, color=cols[1], label=r"$256^3$")
    a.semilogy(kk, d320, ".", ms=2.2, color=cols[0], label=r"$320^3$")
    a.axvline(32.0, **fs.MASK_LINE)
    a.set_ylabel(r"largest departure per shell")
    a.legend(loc="upper left", frameon=False, markerscale=3)
    a.text(0.97, 0.06, "(a)", transform=a.transAxes, ha="right")
    b = ax[1]
    b.axhspan(2.0, 4.5, color="0.9", lw=0)
    b.plot(kk, rat, ".", ms=2.2, color=cols[3])
    b.axhline((320 / 256) ** 4, color="k", lw=1.0, ls="--", label=r"fourth order, $(5/4)^4$")
    b.axhline((320 / 256) ** 6, color="k", lw=1.0, ls=":", label=r"sixth order, $(5/4)^6$")
    b.axhline(1.0, color="0.6", lw=0.8)
    b.axvline(32.0, **fs.MASK_LINE)
    b.set_ylim(0.7, 4.6)
    b.set_xlabel(r"shell $|n|$")
    b.set_ylabel(r"$256^3$ over $320^3$")
    b.legend(loc="lower right", frameon=False, fontsize=6.5)
    b.text(0.03, 0.9, "(b)", transform=b.transAxes)
    fs.save(fig, os.path.join(out, "fig_g2_resolution"))
    lo, hi = kk <= 20, kk >= 40
    summary = dict(ratio_k_le_20_median=float(np.median(rat[lo])), ratio_k_ge_40_median=float(np.median(rat[hi])),
                   i_factor=UR["i_factor"], ii_max_k_le_32=UR["ii_max_k_le_32"], ii_max_to_64=UR["ii_max_to_64"],
                   n_shells=int(k2.size))
    json.dump(summary, open(os.path.join(out, "fig_g2_resolution.json"), "w"), indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
