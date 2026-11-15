#!/usr/bin/env python3
"""The track's noise validator (noise/validate/validate_noise.py, unchanged) with the
reference's window increment of the tanh window formed without cancellation, as the
release executable forms it (athenak/src/scalar_field/scalar_field_noise.cpp:570-577):

    W(t1) - W(t0) = sinh(s hubble (t1 - t0)) / (2 cosh x1 cosh x0),  x = s ln(k_sigma/k),

instead of the difference of two numbers near 1 (noise/ref/noise_ref.py:155, 159). Only
`noise_ref.transfer` is replaced, in memory; every test and threshold of the validator
stays as it is. Arguments: those of validate_noise.py.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
VAL = os.path.normpath(os.path.join(HERE, "..", "..", "noise", "validate"))
sys.path.insert(0, VAL)
sys.path.insert(0, os.path.join(VAL, "..", "ref"))
import noise_ref as nr  # noqa: E402

_orig = nr.transfer


def increment(lat, t0, t1, p):
    if p["window"] != "tanh":
        return nr.window(lat, t1, p) - nr.window(lat, t0, p)
    t0w = p.get("t0w", 0.0)
    x0 = p["sharpness"] * np.log(p["ksigma0"] * np.exp(p["hubble"] * (t0 - t0w)) / lat.q)
    x1 = p["sharpness"] * np.log(p["ksigma0"] * np.exp(p["hubble"] * (t1 - t0w)) / lat.q)
    return 0.5 * np.sinh(p["sharpness"] * p["hubble"] * (t1 - t0)) / (np.cosh(x1) * np.cosh(x0))


def transfer_cf(lat, comp, cycle, p):
    if p["scheme"] == "frozen" and p.get("frozen_form", "rate") != "increment":
        return _orig(lat, comp, cycle, p)
    t = nr.out_time(cycle, p)
    dW = increment(lat, t - p["dt"], t, p)
    dW = np.where(dW > 0.0, dW, 0.0)
    g = nr.base_amplitude(lat, p) * (dW if p["scheme"] == "frozen" else np.sqrt(dW))
    return g * nr.component_factor(lat, comp, p)


nr.transfer = transfer_cf
import validate_noise  # noqa: E402

if __name__ == "__main__":
    validate_noise.main()
