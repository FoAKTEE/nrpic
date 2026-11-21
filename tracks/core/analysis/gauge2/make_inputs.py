#!/usr/bin/env python3
"""Inputs of the tests of the source item gauge-2 (tracks/core/JOURNAL-gauge-2.md), built
from the committed parents with asserted replacements, so that a parent that changes
makes this script fail instead of silently changing a test.

    make_inputs.py            writes the files
    make_inputs.py --check    compares with the files on disk (exit status 1 on a difference)

Written (AthenaK takes on the command line only parameters that the input has, and the
options of the second pass are read only if present, so every variant needs a file):
  problems/es/es_gauge2.athinput     Einstein-Straus data for 100 M with the relaxation
                                     only in the matter (example of lapse_leak_rho)
  inputs/v8_rho.athinput             problems/es/v1_small.athinput + lapse_leak_rho
  inputs/v8_var.athinput             the same + a tracker at the puncture, lapse_leak_hole,
                                     lapse_leak_onset (all three options at zero = off)
  inputs/ball_rho.athinput           problems/ball/ball_leak.athinput + lapse_leak_rho = 0
  inputs/collapse_rho.athinput       problems/ball/ball_collapse.athinput + lapse_leak_rho = 0
  inputs/flrw_rho.athinput           problems/cosmo/flrw_leak.athinput + lapse_leak_rho = 0
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))


def build(parent, reps, header):
    with open(os.path.join(WT, parent)) as f:
        s = f.read()
    for old, new in reps:
        assert s.count(old) == 1, (parent, old, s.count(old))
        s = s.replace(old, new)
    return header + s


def after(line, add):
    return (line, line + "\n" + add)


RHO0 = "lapse_leak_rho  = 0.0      # rho_c: relaxation only where the matter density exceeds rho_c/2 (0: everywhere)"
FILES = {}

# ---- Einstein-Straus, 100 M
es = [(f"nx{a}       = 48\nx{a}min     = -96.0\nx{a}max     = 96.0",
       f"nx{a}       = 64\nx{a}min     = -128.0\nx{a}max     = 128.0") for a in "123"]
es += [(f"x{a}min = -80.0\nx{a}max = 80.0", f"x{a}min = -63.9\nx{a}max = 63.9") for a in "123"]
es += [("# root cells 4 M; 2 M for |x| < 80 M (rounded outward to the whole mesh); then halving\n"
        "# down to M/8 for |x| < 2 M around the puncture",
        "# root cells 4 M; 2 M for |x| < 64 M (the dust ends at 57 M in the coordinates and stays\n"
        "# there: zero shift, lapse near 1); then halving down to M/8 for |x| < 4 M")]
es += [("tlim       = 30.0", "tlim       = 100.0"),
       after("lapse_leak_alpha = 1.0     # reference lapse",
             "lapse_leak_rho  = 2.0e-7   # rho_c: the relaxation acts only where the matter density exceeds\n"
             "                           # rho_c/2 (in full above rho_c); 0.0: everywhere (first pass).\n"
             "                           # Dust plateau 3.7e-6 at the start, 1.1e-6 at 100 M"),
       ("basename  = es", "basename  = es"),
       ("snap_dt        = 10.0", "snap_dt        = 25.0")]
FILES["problems/es/es_gauge2.athinput"] = build(
    "problems/es/es_gauge.athinput", es,
    "# SECOND PASS OF THE RELAXED LAPSE (tracks/core/JOURNAL-gauge-2.md, interface\n"
    "# cosmo_gauge.md section 9): problems/es/es_gauge.athinput for 100 M with the\n"
    "# relaxation restricted to the matter (z4c/lapse_leak_rho), so that the vacuum bubble\n"
    "# and the black hole in it are sliced by plain 1+log. Changes against the parent:\n"
    "# outer faces at +-128 M (cells 4 M beyond 64 M), tlim = 100, lapse_leak_rho, snap_dt.\n"
    "# z4c/lapse_leak_rho=0.0 on the command line gives the condition of the first pass.\n"
    "# Built by tracks/core/analysis/gauge2/make_inputs.py. Header of the parent follows.\n#\n")

# ---- vacuum test V8
FILES["tracks/core/analysis/gauge2/inputs/v8_rho.athinput"] = build(
    "problems/es/v1_small.athinput",
    [after("lapse_leak_alpha = 1.0     # reference lapse", RHO0)],
    "# problems/es/v1_small.athinput with the parameter lapse_leak_rho (at zero: off).\n"
    "# Built by tracks/core/analysis/gauge2/make_inputs.py.\n#\n")
FILES["tracks/core/analysis/gauge2/inputs/v8_var.athinput"] = build(
    "problems/es/v1_small.athinput",
    [after("lapse_leak_alpha = 1.0     # reference lapse",
           RHO0 + "\n"
           "lapse_leak_hole = 0.0      # r_h: relaxation off within r_h of every tracker, in full beyond 2 r_h\n"
           "lapse_leak_onset = 0.0     # delta: smooth onset x^2/(x + delta) of the excess x = ln(alpha/alpha_0)\n"
           "co_0_type       = BH       # tracker at the puncture (for lapse_leak_hole)\n"
           "co_0_x          = 0.0\n"
           "co_0_y          = 0.0\n"
           "co_0_z          = 0.0")],
    "# problems/es/v1_small.athinput with a tracker at the puncture and the three\n"
    "# parameters of the second pass (all at zero: off).\n"
    "# Built by tracks/core/analysis/gauge2/make_inputs.py.\n#\n")

# ---- expanding ball, collapse, homogeneous universe
FILES["tracks/core/analysis/gauge2/inputs/ball_rho.athinput"] = build(
    "problems/ball/ball_leak.athinput",
    [after("lapse_leak_alpha = 1.0     # reference lapse", RHO0)],
    "# problems/ball/ball_leak.athinput with the parameter lapse_leak_rho (at zero: off).\n"
    "# Built by tracks/core/analysis/gauge2/make_inputs.py.\n#\n")
FILES["tracks/core/analysis/gauge2/inputs/collapse_rho.athinput"] = build(
    "problems/ball/ball_collapse.athinput",
    [after("lapse_leak_alpha = 1.0     # reference lapse", RHO0)],
    "# problems/ball/ball_collapse.athinput with the parameter lapse_leak_rho (at zero: off).\n"
    "# Built by tracks/core/analysis/gauge2/make_inputs.py.\n#\n")
FILES["tracks/core/analysis/gauge2/inputs/flrw_rho.athinput"] = build(
    "problems/cosmo/flrw_leak.athinput",
    [after("lapse_leak_alpha = 1.0                 # reference lapse", RHO0)],
    "# problems/cosmo/flrw_leak.athinput with the parameter lapse_leak_rho (at zero: off).\n"
    "# Built by tracks/core/analysis/gauge2/make_inputs.py.\n#\n")


def main():
    check = "--check" in sys.argv
    bad = 0
    for rel, text in FILES.items():
        path = os.path.join(WT, rel)
        if check:
            with open(path) as f:
                same = f.read() == text
            print(("same      " if same else "DIFFERENT ") + rel)
            bad += not same
        else:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                f.write(text)
            print("wrote " + rel)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
