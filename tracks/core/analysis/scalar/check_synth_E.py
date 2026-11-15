#!/usr/bin/env python3
"""The stochastic fields of the code against Track E's reference synthesis
(`tracks/E-stoch-inf/codebase/ref/synth.py` on branch track/E-stoch-inf, request R4).

Takes the last dump of case B_cfl0.25 of a run of test4_noise.py (Mukhanov-Sasaki model,
16^3, box [0, 10]^3, so that the two phase conventions coincide), builds the coefficients
c_n = (shell factor of the record) x (twin alpha) x (stencil projector) for both
hemispheres and synthesizes the six fields with `synth_mesh` of Track E (three
one-dimensional sums per MeshBlock of 8^3 cells) and with its FFT reference.

Usage: check_synth_E.py <test 4 output directory> <path of synth.py>
"""
import glob
import importlib.util
import json
import os
import sys

import numpy as np

import common
from nrpic import scalar_field as sfr

SEED, NMAX2, N, L = 7, 36, 16, 10.0


def main():
    top, spath = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    spec = importlib.util.spec_from_file_location("synth_E", spath)
    synth = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(synth)
    f = sorted(glob.glob(os.path.join(top, "B_cfl0.25", "ms.sf.*.dump")))[1]
    d = sfr.read_dump(f)
    _, rows = sfr.read_modes(f.replace(".dump", ".modes"))
    n, n2 = sfr.mode_set(NMAX2)
    # the hemisphere of the code is the half space of Track E
    hs = synth.half_space(n)
    alpha = sfr.mode_alpha(SEED, 0, 0, n)
    smap = {int(s): rows[i, 5] + 1j*rows[i, 6] for i, s in enumerate(rows[:, 0])}
    sh = np.array([smap[int(s)] for s in n2])
    qh = np.stack([sfr.d1_symbol(2.0*np.pi*n[:, i]/N, 4) for i in range(3)], axis=1)
    q2 = (qh**2).sum(axis=1)
    pr = [np.ones(len(n)), qh[:, 0]**2/q2, qh[:, 0]*qh[:, 1]/q2, qh[:, 0]*qh[:, 2]/q2,
          qh[:, 1]**2/q2, qh[:, 1]*qh[:, 2]/q2]
    nall = np.concatenate([n, -n])
    out = {"dump": f, "time": d["time"], "all_in_half_space": bool(hs.all()),
           "modes": int(len(n)), "fields": {}}
    for k in range(6):
        c = sh*alpha*pr[k]
        call = np.concatenate([c, np.conj(c)])
        fb, ops = synth.synth_mesh(nall, call, N, L, 8)
        ff = synth.synth_fft(nall, call, N, L)
        code = d["fields"][f"noise{k}"]
        rms = np.sqrt(np.mean(d["fields"]["noise0"]**2))
        out["fields"][f"field{k}"] = dict(
            code_minus_blocks=float(np.abs(code - fb.real).max()/rms),
            code_minus_fft=float(np.abs(code - ff.real).max()/rms),
            imag_of_reference=float(np.abs(fb.imag).max()/rms))
    out["max_code_minus_blocks"] = max(v["code_minus_blocks"] for v in out["fields"].values())
    out["max_code_minus_fft"] = max(v["code_minus_fft"] for v in out["fields"].values())
    with open("synth_E.json", "w") as fp:
        json.dump(out, fp, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
