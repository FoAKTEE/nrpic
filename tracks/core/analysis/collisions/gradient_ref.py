#!/usr/bin/env python3
"""Reference numbers for the collision tests in the static conformal metric with a
gradient (scbox.pair_reference): what one collision does, on average, to the sum of
the energies of the two partners measured with the metric at each of them.

  gradient_ref.py OUT.json [--npair 4000000] [--only NAME,...]

Configurations: see CASES (name: metric amplitudes, temperature law, cell factor).
Each is evaluated for the collision of coll_energy = cell and of coll_energy = particle.
"""
import argparse
import json
import sys

import scbox

THETA0 = 0.05
# name: (a_alpha, a_psi, a_shift, s_alpha, s_psi, f)
CASES = {
    "psi_iso":      (0.0, 0.1, 0.0, 0.0, 0.0, 1),
    "psi_iso_f2":   (0.0, 0.1, 0.0, 0.0, 0.0, 2),
    "psi_iso_f4":   (0.0, 0.1, 0.0, 0.0, 0.0, 4),
    "psi_iso_half": (0.0, 0.05, 0.0, 0.0, 0.0, 1),
    "psi_null":     (0.0, 0.1, 0.0, 0.0, 4.0, 1),
    "psi_inverted": (0.0, 0.1, 0.0, 0.0, 8.0, 1),
    "lapse_tolman": (-0.2, 0.0, 0.0, 1.0, 0.0, 1),
    "lapse_iso":    (-0.2, 0.0, 0.0, 0.0, 0.0, 1),
    "well_tolman":  (-0.2, 0.1, 0.0, 1.0, 0.0, 1),
    "well_tolman_f2": (-0.2, 0.1, 0.0, 1.0, 0.0, 2),
    "well_shift":   (-0.2, 0.1, 0.05, 1.0, 0.0, 1),
}


def metric(name):
    aa, ap, ash, _, _, _ = CASES[name]
    return scbox.Metric(nx=16, a_alpha=aa, a_psi=ap, a_shift=ash)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--npair", type=int, default=4000000)
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    names = [n for n in args.only.split(",") if n] or list(CASES)
    res = {}
    for k, name in enumerate(names):
        _, _, _, sa, sp, f = CASES[name]
        met = metric(name)
        res[name] = {}
        for mode in ("cell", "particle"):
            r = scbox.pair_reference(met, args.npair, 1000 + k, THETA0, sa, sp, f, mode)
            res[name][mode] = r
            print(f"{name:16s} {mode:8s} dW = {r['dW']:+.4e} ({r['dW_se']:.1e})  "
                  f"dH = {r['dH']:+.4e} ({r['dH_se']:.1e})  slope = {r['slope']:+.4e} "
                  f"({r['slope_se']:.1e})  noroot {r['noroot']:.1e}  "
                  f"max|lam-1| {r['max_dlam']:.2e}", flush=True)
    with open(args.out, "w") as fp:
        json.dump(dict(theta0=THETA0, cases=CASES, results=res), fp, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
