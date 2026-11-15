#!/usr/bin/env python3
"""V7 arithmetic: card-hours per 256^3 realisation from the track's inputs (2.0e7
zone-cycles/s, docs/TESTLOG.md:46; +15 percent for field and kicks and 3e12 flop/s for the
synthesis, SCOPE 8 [JUDGEMENT]), the cosmic-time spans of my V1 run (v1.json, t_span_Hstar)
and my operation count of the synthesis kernel (scalar_field_noise.cpp:596-652:
nf (M b + P b^2 + X b^3) complex multiply-adds per MeshBlock and stage, 8 flop each, 4 stages).
Second variant (after reading the track's review): calibrated with core's card measurement
core-20261115-143907-cea4c86 (summary.json: 128^3, 64^3 MeshBlocks, nmax2 = 1024; Z4c
1.983e7, field 1.389e7, field + noise 1.204e7 zone-cycles/s): the field factor 1/1.389e7 per
zone-cycle and the noise at the flop rate that the measured noise time implies for my count.
Usage: v7_cost_arithmetic.py <v1.json> <out.json> [core summary.json]"""
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
    if len(sys.argv) > 3:
        c = json.load(open(sys.argv[3]))
        n3 = c["n"] ** 3
        t_noise = n3 / c["noise"]["zone_cycles_per_s"] - n3 / c["field"]["zone_cycles_per_s"]
        f_meas = counts(c["n"], c["nmax2"], c["block"]) * 8 * 4
        rate = f_meas / t_noise
        t_field = 256**3 / c["field"]["zone_cycles_per_s"]
        out["calibrated"] = dict(noise_s_per_cycle_128=t_noise, flop_per_cycle_128=f_meas,
                                 implied_flop_rate=rate, field_s_per_step_256=t_field,
                                 card_hours={})
        print("core 128^3: noise %.4f s/cycle, %.3g flop -> %.3g flop/s" % (t_noise, f_meas, rate))
        for th in (0.25, 0.025):
            for case, t in span.items():
                n = 256 * t / (2 * math.pi * th)
                key = "%s theta=%g steps=%d" % (case, th, round(n))
                out["calibrated"]["card_hours"][key] = {
                    b: n * (t_field + f / rate) / 3600 for b, f in out["flop_per_step"].items()}
                print("calibrated", key, {b: round(v, 2) for b, v in
                                          out["calibrated"]["card_hours"][key].items()})
    json.dump(out, open(sys.argv[2], "w"), indent=1)


if __name__ == "__main__":
    main()
