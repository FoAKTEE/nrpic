#!/usr/bin/env python3
"""Mode file for core's Mukhanov-Sasaki noise model (format: scalar_field_noise.cpp:393-396,
rows |n|^2 Re R Im R Re dR/dtau Im dR/dtau). The values are a smooth, small, scale-free
choice (R ~ 1e-4 |n|^(-3/2), complex phase, nonzero derivative); the reproducibility test
does not need physical mode functions, only nonzero sources in Pi, Khat and At."""
import sys

import numpy as np

with open(sys.argv[1], "w") as fh:
    fh.write("# |n|^2 ReR ImR ReDR ImDR  (verifier V6, synthetic)\n")
    for n2 in range(1, 401):
        q = np.sqrt(n2)
        R = 1e-4 * q**-1.5
        fh.write("%d %.17e %.17e %.17e %.17e\n" % (n2, R, 0.3 * R, -0.2 * R * q, 0.1 * R))
