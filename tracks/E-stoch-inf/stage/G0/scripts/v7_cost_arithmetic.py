#!/usr/bin/env python3
"""V7 arithmetic: card-hours per 256^3 realisation from the track's inputs (2.0e7
zone-cycles/s, docs/TESTLOG.md:46; +15 percent for field and kicks and 3e12 flop/s for the
synthesis, SCOPE 8 [JUDGEMENT]), the cosmic-time spans of my V1 run (v1.json, t_span_Hstar)
and my operation count of the synthesis kernel (scalar_field_noise.cpp:596-652:
nf (M b + P b^2 + X b^3) complex multiply-adds per MeshBlock and stage, 8 flop each, 4 stages).
Usage: v7_cost_arithmetic.py <v1.json> <out.json>"""
import json
import math
import sys


def counts(N, nmax2, b, nf=6):
    nmax = int(math.isqrt(nmax2))
    modes = [(x, y, z) for x in range(0, nmax + 1) for y in range(-nmax, nmax + 1)
             for z in range(-nmax, nmax + 1)
             if 1 <= x * x + y * y + z * z <= nmax2
             and (x > 0 or (x == 0 and y > 0) or (x == 0 and y == 0 and z > 0))]
    M = len(modes)
    P = len({(m[0], m[1]) for m in modes})
    X = len({m[0] for m in modes})
    nmb = (N // b) ** 3
    return nf * (M * b + P * b * b + X * b**3) * nmb


def main():
    v1 = json.load(open(sys.argv[1]))
    span = {"SR": v1["SR"]["t_span_Hstar"], "USR": v1["USR"]["t_span_Hstar"]}
    z4c = 256**3 / 2.0e7 * 1.15
    out = {"t_span_Hstar": span, "flop_per_step": {}, "card_hours": {}}
    for b in (128, 64, 32):
        out["flop_per_step"][b] = counts(256, 4096, b) * 8 * 4
    for th in (0.25, 0.025):
        for case, t in span.items():
            n = 256 * t / (2 * math.pi * th)
            key = "%s theta=%g steps=%d" % (case, th, round(n))
            out["card_hours"][key] = {b: n * (z4c + f / 3e12) / 3600
                                      for b, f in out["flop_per_step"].items()}
            print(key, {b: round(v, 2) for b, v in out["card_hours"][key].items()})
    json.dump(out, open(sys.argv[2], "w"), indent=1)


if __name__ == "__main__":
    main()
