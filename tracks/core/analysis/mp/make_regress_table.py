#!/usr/bin/env python3
"""Radial table (format of docs/FORMATS.md, columns r u alpha) for the regression input
problems/tests/regress_cf.athinput: the conformal factor of a Gaussian conformal source
of mass 0.3 and width 1, with the isotropic lapse. Usage: make_regress_table.py out.tab"""
import math
import sys

M, SIG, DR, N = 0.3, 1.0, 0.01, 1201
with open(sys.argv[1], "w") as f:
    f.write("# r u alpha (regression table)\n")
    for k in range(N):
        r = k * DR
        if k == 0:
            u = M / (math.sqrt(2.0 * math.pi) * SIG)
        else:
            u = 0.5 * M * math.erf(r / (math.sqrt(2.0) * SIG)) / r
        f.write("%.17e %.17e %.17e\n" % (r, u, (1.0 - u) / (1.0 + u)))
