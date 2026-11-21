#!/usr/bin/env python3
"""Numerical check of claim 697 (1707.06302v2 eq. lmax, kerrdm.tex L1372-1377).

Equatorial Kerr geodesics (G = M = c = 1, Q = 0, unit rest mass): the radial function is
R(x) = [E (x^2 + a^2) - a L]^2 - Delta [x^2 + (L - a E)^2], with Delta = x^2 - 2x + a^2.
The root L(x) of R = 0 is L = (-2 a E +- sqrt(x * D * (2 - (1 - E^2) x))) / (x - 2).
The check evaluates R at that root for D = Delta (D's correction) and for
D = a^2 - x(x - 2) (the printed form). Prints one row per case; exit 1 if the corrected
form fails. Standard library only; reads no paper text.
"""
import math
import sys

ok = True
print("a\tE\tx\tform\tsign\tL\tR(L)")
for a, E, x in [(0.5, 0.95, 6.0), (0.8, 0.9, 8.0), (0.3, 0.99, 12.0)]:
    delta = x * x - 2 * x + a * a
    for name, inner in (("Delta", delta), ("printed", a * a - x * (x - 2))):
        for s in (1, -1):
            arg = x * inner * (2 - (1 - E * E) * x)
            if arg < 0:
                print(f"{a}\t{E}\t{x}\t{name}\t{s}\tnan\tnegative argument")
                if name == "Delta":
                    ok = False
                continue
            L = (-2 * a * E + s * math.sqrt(arg)) / (x - 2)
            R = (E * (x * x + a * a) - a * L) ** 2 - delta * (x * x + (L - a * E) ** 2)
            print(f"{a}\t{E}\t{x}\t{name}\t{s}\t{L:.6f}\t{R:.3e}")
            if name == "Delta" and abs(R) > 1e-9 * max(1.0, x ** 4):
                ok = False
print("corrected root satisfies R = 0:", ok)
sys.exit(0 if ok else 1)
