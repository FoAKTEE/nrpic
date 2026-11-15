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
# The cases "*_hot" use the temperature HOT of cases with the same metric: the residual
# of a scheme that is exact only in the non-relativistic limit grows with it.
HOT = 0.3
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
    "psi_iso_hot":  (0.0, 0.1, 0.0, 0.0, 0.0, 1),
    "well_tolman_hot": (-0.2, 0.1, 0.0, 1.0, 0.0, 1),
    "well_tolman_hot_f2": (-0.2, 0.1, 0.0, 1.0, 0.0, 2),
}


def theta_of(name):
    return HOT if "_hot" in name else THETA0


def metric(name):
    aa, ap, ash, _, _, _ = CASES[name]
    return scbox.Metric(nx=16, a_alpha=aa, a_psi=ap, a_shift=ash)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--npair", type=int, default=4000000)
    ap.add_argument("--only", default="")
    ap.add_argument("--no-balance", action="store_true",
                    help="particle mode without the detailed-balance acceptance")
    ap.add_argument("--tolman", type=float, default=0.0,
                    help="instead of the cases: the equilibrium of the well (alpha_amp "
                         "-0.2, psi_amp 0.1) at this theta_inf, positions with the "
                         "equilibrium density, cells weighted with their collision rate")
    args = ap.parse_args()
    if args.tolman > 0.0:
        met = scbox.Metric(nx=16, a_alpha=-0.2, a_psi=0.1)
        res = {}
        for mode in ("cell", "particle"):
            r = scbox.pair_reference(met, args.npair, 77, args.tolman, 1.0, 0.0, 1, mode,
                                     density="tolman")
            res[mode] = r
            print(f"tolman theta_inf {args.tolman} {mode:8s} dW = {r['dW']:+.4e} "
                  f"({r['dW_se']:.1e})  dH = {r['dH']:+.4e} ({r['dH_se']:.1e})  "
                  f"rejected {r['rejected']:.2e}  noroot {r['noroot']:.1e}", flush=True)
        with open(args.out, "w") as fp:
            json.dump(dict(theta_inf=args.tolman, results=res), fp, indent=1)
        return 0
    names = [n for n in args.only.split(",") if n] or list(CASES)
    res = {}
    for k, name in enumerate(names):
        _, _, _, sa, sp, f = CASES[name]
        met = metric(name)
        res[name] = {}
        for mode in ("cell", "particle"):
            r = scbox.pair_reference(met, args.npair, 1000 + k, theta_of(name), sa, sp, f,
                                     mode, balance=not args.no_balance)
            res[name][mode] = r
            print(f"{name:18s} {mode:8s} dW = {r['dW']:+.4e} ({r['dW_se']:.1e})  "
                  f"dH = {r['dH']:+.4e} ({r['dH_se']:.1e})  slope = {r['slope']:+.4e} "
                  f"({r['slope_se']:.1e})  noroot {r['noroot']:.1e}  "
                  f"max|lam-1| {r['max_dlam']:.2e}  rejected {r['rejected']:.2e}  "
                  f"max|R-1| {r['max_abs_R_minus_1']:.2e}", flush=True)
    with open(args.out, "w") as fp:
        json.dump(dict(theta0=THETA0, hot=HOT, cases=CASES, results=res,
                       balance=not args.no_balance), fp, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
