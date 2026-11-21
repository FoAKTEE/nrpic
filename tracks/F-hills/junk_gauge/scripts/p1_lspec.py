#!/usr/bin/env python3
"""J4c: what the J4b window of P1 holds, by multipole l and by frequency band.

Per sphere: the r psi4 modes of P1 on the record cut at u <= UCUT (J4b), the news by FFI
(omega_0 = 0.2, taper 4 M), then
  - E_l = (1/16 pi) sum_m int_{u0}^{u1} |N_lm|^2 du for l = 2..8 (the window's energy per l);
  - the share of the window's energy spectrum sum_lm |FFT(N_lm w)|^2 (w = 1 on [u0, u1] with
    4 M cosine ramps inside) in the bands |omega| < 0.2, 0.2-0.5, 0.5-1, > 1 (units 1/M);
  - the same band shares for the l = 2 modes alone.
Writes p1_lspec.json. Usage: p1_lspec.py <out | -> <P1 run dir> [--window=-35,6] [--ucut=14]
                         [--M=1.25] [--radii=40,48,70,90]
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import junk_lib as jl  # noqa: E402

BANDS = [(0.0, 0.2), (0.2, 0.5), (0.5, 1.0), (1.0, 1e9)]


def shares(Ns, u, w, dt):
    spec = sum(np.abs(np.fft.fft(N * w)) ** 2 for N in Ns)
    om = np.abs(2 * np.pi * np.fft.fftfreq(len(u), dt))
    tot = float(np.sum(spec))
    return {f"{a:g}-{b:g}": float(np.sum(spec[(om >= a) & (om < b)]) / tot) for a, b in BANDS}


def main():
    out = sys.argv[1] if sys.argv[1] != "-" else os.environ["NRPIC_RUN_DIR"]
    rd = sys.argv[2]
    u0, u1, ucut, M, radii = -35.0, 6.0, 14.0, 1.25, (40, 48, 70, 90)
    for a in sys.argv[3:]:
        if a.startswith("--window="):
            u0, u1 = (float(x) for x in a[9:].split(","))
        elif a.startswith("--ucut="):
            ucut = float(a[7:])
        elif a.startswith("--M="):
            M = float(a[4:])
        elif a.startswith("--radii="):
            radii = tuple(int(x) for x in a[8:].split(","))
    os.makedirs(out, exist_ok=True)
    res = dict(run_dir=rd, window_u=[u0, u1], ucut=ucut, M=M, bands=BANDS, radii={})
    for R in radii:
        t, modes = jl.load_modes(rd, R)
        u = t - jl.tortoise(R, M)
        keep = u <= ucut
        t, u = t[keep], u[keep]
        N = {k: jl.ffi(t, z[keep], 0.2, 4.0) for k, z in modes.items()}
        dt = float(np.median(np.diff(t)))
        El = {}
        for l in range(2, 9):
            rate = sum(np.abs(N[(l, m)]) ** 2 for m in range(-l, l + 1)) / (16 * np.pi)
            El[str(l)] = jl.window_integral(u, rate, u0, u1)
        sel = (u >= u0) & (u <= u1)
        w = np.zeros_like(u)
        w[sel] = jl.taper(u[sel], 4.0)
        r = dict(E_l=El, E_total=float(sum(El.values())),
                 E_l_share={k: v / sum(El.values()) for k, v in El.items()},
                 band_share_all=shares(list(N.values()), u, w, dt),
                 band_share_l2=shares([N[(2, m)] for m in range(-2, 3)], u, w, dt))
        res["radii"][str(R)] = r
        print(R, json.dumps(r, indent=1), flush=True)
    json.dump(res, open(os.path.join(out, "p1_lspec.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
