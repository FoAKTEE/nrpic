#!/usr/bin/env python3
"""Particle file of the example input problems/tests/coll_box_static.athinput: a Tolman
gas (f ~ exp(-alpha W/theta_inf), theta_inf = 0.2) in the static potential well of that
deck (alpha_amp = -0.2, psi_amp = 0.1, 16 x 4 x 4 cells of [100, 101] x [100, 100.25]^2),
1e5 particles, as in the Tolman test (run_tolman.py).

  make_static_example.py OUT.nrp [--n 100000] [--theta 0.2] [--seed 1]
"""
import argparse

import scbox


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--n", type=int, default=100000)
    ap.add_argument("--theta", type=float, default=0.2)
    ap.add_argument("--seed", type=int, default=1)
    args = ap.parse_args()
    met = scbox.Metric(nx=16, a_alpha=-0.2, a_psi=0.1)
    info = scbox.make_particles(args.out, met, args.n, args.seed, args.theta, 1.0, 0.0,
                                [1.0, 0.25, 0.25], weight="tolman")
    print(info)


if __name__ == "__main__":
    main()
