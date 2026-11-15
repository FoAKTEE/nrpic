#!/usr/bin/env python3
"""Particle file for the periodic box of the collision tests (common.make_box).

  make_box.py OUT.nrp KIND N [--seed S] [--theta T] [--theta2 T2] [--u0 U]
"""
import argparse
import json

import common


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("kind", choices=["mj", "shell", "twotemp", "unequal", "mode"])
    ap.add_argument("n", type=int)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--theta", type=float, default=0.1)
    ap.add_argument("--theta2", type=float, default=None)
    ap.add_argument("--u0", type=float, default=0.3)
    ap.add_argument("--mass-ratio", type=float, default=4.0)
    ap.add_argument("--mode-eps", type=float, default=0.0)
    args = ap.parse_args()
    meta = common.make_box(args.out, args.kind, args.n, seed=args.seed, theta=args.theta,
                           theta2=args.theta2, u0=args.u0, mass_ratio=args.mass_ratio,
                           mode_eps=args.mode_eps)
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
