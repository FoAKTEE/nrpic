#!/usr/bin/env python3
"""MeshBlock trees and card cost of the isolated binary at m/8, m/12, m/16 (binary_conv).

Tree model: tracks/F-hills/g2mesh/scripts/tree3.py (read only; exact against `athena -m` and
P1's restart trees, g2mesh JOURNAL G2M-1 outcome). Tracks: the Newtonian two-body problem
from the input (v = p/m), sampled every `--dt` M to `--tend`. Cost: cycles per M =
1/(cfl h_finest), MeshBlock-cycles per second from `--rate` (P1's chain segments 1963-2242,
p1/README.md ledger).

Usage: tree_cost.py <bin_mN.athinput> <out.json> [--tend 100] [--dt 0.5] [--rate 2000]
Variants: the input's own mesh, and the same cells on P1's domain +-256.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "tracks/F-hills/g2mesh/scripts"))
import tree3  # noqa: E402


def newton_tracks(punc_masses, x0, p0, tend, dt):
    m = np.asarray(punc_masses, float)
    x = np.asarray(x0, float).copy()
    v = np.asarray(p0, float) / m[:, None]
    ts = np.arange(0.0, tend + 1e-9, dt)
    out = [x.copy()]
    h = dt / 200.0

    def acc(x):
        d = x[0] - x[1]
        r3 = np.linalg.norm(d) ** 3
        return np.array([-m[1] * d / r3, m[0] * d / r3])

    for _ in ts[1:]:
        for _ in range(200):           # leapfrog
            v += 0.5 * h * acc(x)
            x += h * v
            v += 0.5 * h * acc(x)
        out.append(x.copy())
    return ts, np.array(out)


def main():
    args = sys.argv[1:]
    inp_path, out = args[0], args[1]
    opt = {"--tend": 100.0, "--dt": 0.5, "--rate": 2000.0}
    for i, a in enumerate(args):
        if a in opt:
            opt[a] = float(args[i + 1])
    inp = tree3.read_athinput(inp_path)
    prob = inp["problem"]
    ncomp = int(prob["ncomp"])
    masses = [float(prob[f"comp{c}_mass"]) for c in range(ncomp)]
    x0 = [[float(prob.get(f"comp{c}_x{a}", 0)) for a in (1, 2, 3)] for c in range(ncomp)]
    p0 = [[float(prob.get(f"comp{c}_p{a}", 0)) for a in (1, 2, 3)] for c in range(ncomp)]
    ts, X = newton_tracks(masses, x0, p0, opt["--tend"], opt["--dt"])
    cfl = float(inp["time"]["cfl_number"])
    # the input's own mesh, and the same cells on P1's domain +-256 (root doubled)
    msh = inp["mesh"]
    nx_in, L_in = int(msh["nx1"]), float(msh["x1max"])
    inp256 = {k: dict(v) for k, v in inp.items()}
    for a in ("1", "2", "3"):
        inp256["mesh"][f"x{a}min"], inp256["mesh"][f"x{a}max"] = "-256.0", "256.0"
    variants = {"input": (inp, dict()),
                "P1_domain_256": (inp256, dict(nx=int(nx_in * 256.0 / L_in)))}
    res = {"input": inp_path, "tend": opt["--tend"], "dt_sample": opt["--dt"],
           "rate_mbcps": opt["--rate"], "variants": {}}
    for name, (ivar, kw) in variants.items():
        T = tree3.Tree(ivar, **kw)
        start = tree3.total(T.build(np.array(x0), start=True))
        series = [tree3.total(T.build(X[i])) for i in range(len(ts))]
        hfin = T.h(T.lmax)
        cyc_per_M = 1.0 / (cfl * hfin)
        mean = float(np.mean(series))
        ch = opt["--tend"] * cyc_per_M * mean / opt["--rate"] / 3600.0
        res["variants"][name] = dict(start=start, max=int(max(series)), min=int(min(series)),
                                     mean=mean, h_finest=hfin, m_over_h=masses[0] / hfin,
                                     cycles_per_M=cyc_per_M,
                                     card_hours_to_tend=ch,
                                     M_per_card_hour=opt["--tend"] / ch,
                                     series=series)
        print(f"{name:10s} start {start:5d} max {max(series):5d} mean {mean:7.1f} "
              f"m/h {masses[0]/hfin:5.1f} cyc/M {cyc_per_M:6.1f} card-h to {opt['--tend']:.0f}: "
              f"{ch:5.2f}  ({opt['--tend']/ch:5.1f} M per card-hour)")
    res["t"] = ts.tolist()
    sep = np.linalg.norm(X[:, 0] - X[:, 1], axis=1)
    res["newton_sep_min_max"] = [float(sep.min()), float(sep.max())]
    with open(out, "w") as f:
        json.dump(res, f, indent=1)


if __name__ == "__main__":
    main()
