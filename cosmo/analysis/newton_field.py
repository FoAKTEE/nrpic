"""Power spectrum of the Newtonian particle-mesh run of a random field against linear
theory (growth in proportion to the scale factor), next to the relativistic run of the
same field (energy-density contrast against its linear theory, as daverio_c.py).

    python3 newton_field.py NEWTON_DIR GR_DIR [--box 704 --cut 220]
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "cosmo", "ic"))
sys.path.insert(0, HERE)
import random_field as rf  # noqa: E402
import daverio_c as dc  # noqa: E402


def main():
    ndir, gdir = sys.argv[1], sys.argv[2]
    args = sys.argv[3:]
    opt = {args[i][2:]: args[i + 1] for i in range(0, len(args) - 1, 2)}
    box, cut = float(opt.get("box", "704")), float(opt.get("cut", "220"))
    kcut = 2.0*np.pi/cut
    d = np.load(os.path.join(ndir, "newton_field.npz"))
    g = dc.load(gdir, box)
    k0, p0, _ = rf.measure_power(d["delta"][0], box, nbins=None)
    keep = k0 <= kcut*1.0001
    print("shells (h/Mpc):", np.round(k0[keep], 4))
    res = {}
    for i in range(1, len(d["t"])):
        a = (1.0 + 0.5*d["t"][i])**2
        z = 1001.0/a - 1.0
        _, p, _ = rf.measure_power(d["delta"][i], box, nbins=None)
        _, pl, _ = rf.measure_power(d["delta"][0]*a, box, nbins=None)
        newton = (p/pl - 1.0)[keep]
        q = g["spec"][i]
        lin = dc.linear_field(g["spec"][0]["delta"], box, q["a"])
        _, pan, _ = rf.measure_power(lin, box, nbins=None)
        gr = (q["P"]/pan - 1.0)[keep]
        res[z] = (newton, gr)
        print(f"z = {z:7.2f}: rms contrast {d['delta'][i].std():.4f} (N) {q['rms']:.4f} (GR)")
        print("   Newtonian P/P_lin - 1 (percent):   " + " ".join(f"{100*v:+.3f}" for v in newton))
        print("   relativistic P/P_lin - 1 (percent): " + " ".join(f"{100*v:+.3f}" for v in gr))
        print("   difference GR - N (percent):        "
              + " ".join(f"{100*(u - v):+.3f}" for u, v in zip(gr, newton)))
    return res


if __name__ == "__main__":
    main()
