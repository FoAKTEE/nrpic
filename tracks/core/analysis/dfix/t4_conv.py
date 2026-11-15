#!/usr/bin/env python3
"""Follow-up of test T4: the expanding cases at the step 0.002 (run of t4_newton.py) and
at 0.001 (cases/t4_conv_cpu.list): errors against the ODE solution and drift of C.

    t4_conv.py RUN_T4 RUN_HALF
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import t4_newton as t4   # noqa: E402


def one(d, phys):
    tr = t4.read_traj(d, "npmp")
    x0 = np.array([[0.6, 0.0, 0.0], [0.0, 0.0, -0.4]])
    p0 = np.array([[0.0, 0.9, 0.0], [1.0, 0.3, 0.0]])
    errs = []
    for tag in range(2):
        s = tr[tr[:, 1] == tag]
        ex = t4.expand_reference(x0[tag], p0[tag], s[-1, 0], phys)(s[:, 0])[:3].T
        dx = s[:, 2:5] - ex
        dx -= 4.0*np.round(dx/4.0)
        errs.append(float(np.linalg.norm(dx, axis=1).max()))
    nh = np.loadtxt(os.path.join(d, "npmp.newton.hst"))
    scale = np.abs(nh[:, 2]*nh[:, 5]).max()
    return {"max_position_error": errs, "t_end": float(nh[-1, 0]),
            "C_drift_over_aW": float(np.abs(nh[:, 7] - nh[0, 7]).max()/scale)}


def main():
    full, half = sys.argv[1], sys.argv[2]
    res = {}
    for name, phys in (("expand", False), ("expand_phys", True)):
        a = one(os.path.join(full, name), phys)
        b = one(os.path.join(half, name + "_h"), phys)
        res[name] = {"dt_0.002": a, "dt_0.001": b,
                     "ratio_position": [x/y for x, y in zip(a["max_position_error"],
                                                            b["max_position_error"])],
                     "ratio_C": a["C_drift_over_aW"]/b["C_drift_over_aW"]}
    print(json.dumps(res, indent=1))
    with open(os.path.join(half, "t4_conv.json"), "w") as fp:
        json.dump(res, fp, indent=1)
        fp.write("\n")


if __name__ == "__main__":
    main()
