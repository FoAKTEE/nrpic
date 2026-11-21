#!/usr/bin/env python3
"""Lead review, wave 3 (B-emd-gw), check L2b of ../JOURNAL.md: where verifier3's X plus
amplitude at N = 64 comes from. Imports verifier3's own reader, basis and projector
(stage/G1/verifier3/scripts/diag.py, exact.py; read-only, not changed) and evaluates the
last x1 and x10 dumps of test X two ways:
  route V: tt_project(gt - 1) and tt_project(-2 alpha At), pol_components, mode_coeff
           (verifier3's v3_measure.do_X);
  route D: e_p : mode_coeff(gt - 1) and e_p : mode_coeff(-2 alpha At) directly, same basis.
Prints |Z_V|/|Z_D| - 1 per polarization (Z = H + i H'/|K|), and the same with the k = 0 and
Nyquist mask switched off in a copy of the projector.

    python3 lw3_route.py      (through nrpic-run; JSON to stdout and $NRPIC_RUN_DIR/lw3_route.json)
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TRACK = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(TRACK, "stage", "G1", "verifier3", "scripts"))
import diag  # noqa: E402
import exact  # noqa: E402

SCR = "/data/haiyangw/nrpic/scratch/B-emd-gw"
OUT = os.environ.get("NRPIC_RUN_DIR", os.path.join(SCR, "tmp", "lw3"))
DUMPS = {"x1": (os.path.join(SCR, "B-20261119-142124-feb2daf", "expN64", "bin",
                             "xw.z4c.00040.bin"), 1.0),
         "x10": (os.path.join(SCR, "B-20261119-155758-458cf17", "expN64x10", "bin",
                              "xw.z4c.00040.bin"), 10.0)}
EYE = np.eye(3)[:, :, None, None, None]


def tt_nomask(T, grid):
    kx, ky, kz = grid.kvecs(real=True)
    k2 = kx ** 2 + ky ** 2 + kz ** 2
    kk = [kx, ky, kz]
    Tk = np.fft.rfftn(T, axes=(-3, -2, -1))
    with np.errstate(invalid="ignore", divide="ignore"):
        inv = np.where(k2 > 0, 1.0 / k2, 0.0)
    P = np.empty((3, 3) + k2.shape)
    for a in range(3):
        for b in range(3):
            P[a, b] = (1.0 if a == b else 0.0) - kk[a] * kk[b] * inv
    PT = np.einsum("il...,lj...->ij...", P, Tk)
    PTP = np.einsum("il...,lj...->ij...", PT, P)
    tr = np.einsum("lm...,lm...->...", P, Tk)
    return np.fft.irfftn(PTP - 0.5 * P * tr, s=grid.n, axes=(-3, -2, -1))


def main():
    res = {}
    for tag, (path, scale) in DUMPS.items():
        d = diag.read_bin(path)
        g = d["grid"]
        gam, K, alp, chi, gt, At, trK = diag.z4c_to_adm(d)
        xw = exact.ExpandingWave(eps_p=2e-6 * scale, eps_x=1e-6 * scale)
        m, kn = (1, 1, 0), xw.kn
        h, hd = gt - EYE, -2.0 * alp * At
        out = {"time": d["time"]}
        Z = {}
        for route in ("V", "Vnomask", "D"):
            zz = []
            for pi, e in enumerate((xw.ep, xw.ex)):
                if route == "D":
                    ch = 2 * 0.5 * sum(e[a, b] * diag.mode_coeff(h[a, b], g, m)
                                       for a in range(3) for b in range(3))
                    cd = 2 * 0.5 * sum(e[a, b] * diag.mode_coeff(hd[a, b], g, m)
                                       for a in range(3) for b in range(3))
                else:
                    proj = diag.tt_project if route == "V" else tt_nomask
                    hp = diag.pol_components(proj(h, g), xw.K)[pi]
                    dp = diag.pol_components(proj(hd, g), xw.K)[pi]
                    ch, cd = 2 * diag.mode_coeff(hp, g, m), 2 * diag.mode_coeff(dp, g, m)
                zz.append(complex(ch + 1j * cd / kn))
            Z[route] = zz
        for route in ("V", "Vnomask"):
            out[route + "_over_D_minus_1"] = {
                p: float(abs(Z[route][i]) / abs(Z["D"][i]) - 1) for i, p in enumerate("+x")}
        out["absZ"] = {r: [abs(z) for z in Z[r]] for r in Z}
        res[tag] = out
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "lw3_route.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
