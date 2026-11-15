#!/usr/bin/env python3
"""Follow-up of test T4: the expanding cases at the step 0.002 (run of t4_newton.py) and
at 0.001 (cases/t4_conv_cpu.list): errors against the ODE solution and drift of C.

    t4_conv.py RUN_T4 RUN_HALF [--fig PREFIX]

Writes t4_conv.json into $NRPIC_RUN_DIR (or into RUN_HALF) and, with --fig, the figure
PREFIX_conv.png: distance to the ODE solution and drift of C against time at both steps.
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


def curves(d, phys):
    """distance to the ODE solution per orbit and the drift of C over a|W| against time"""
    tr = t4.read_traj(d, "npmp")
    x0 = np.array([[0.6, 0.0, 0.0], [0.0, 0.0, -0.4]])
    p0 = np.array([[0.0, 0.9, 0.0], [1.0, 0.3, 0.0]])
    out = []
    for tag in range(2):
        s = tr[tr[:, 1] == tag]
        ex = t4.expand_reference(x0[tag], p0[tag], s[-1, 0], phys)(s[:, 0])[:3].T
        dx = s[:, 2:5] - ex
        dx -= 4.0*np.round(dx/4.0)
        out.append((s[:, 0], np.linalg.norm(dx, axis=1)))
    nh = np.loadtxt(os.path.join(d, "npmp.newton.hst"))
    scale = np.abs(nh[:, 2]*nh[:, 5]).max()
    return out, (nh[:, 0], np.abs(nh[:, 7] - nh[0, 7])/scale)


def figure(full, half, prefix):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "python")))
    from nrpic import figstyle as fs
    fs.use_style()
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.075, right=0.99, bottom=0.17, top=0.95, wspace=0.36)
    for k, (name, phys) in enumerate((("expand", False), ("expand_phys", True))):
        for d, ls, lab in ((os.path.join(full, name), "-", "dt = 0.002"),
                           (os.path.join(half, name + "_h"), "--", "dt = 0.001")):
            orb, cdr = curves(d, phys)
            for tag in range(2):
                t, e = orb[tag]
                ax[k].semilogy(t[1:], e[1:], color=fs.SERIES[tag], ls=ls,
                               label=f"orbit {tag + 1}, {lab}")
            if not phys:
                ax[2].semilogy(cdr[0][1:], cdr[1][1:] + 1e-16, color=fs.SERIES[0], ls=ls,
                               label=lab)
        ax[k].set_xlabel("conformal time")
        ax[k].set_ylabel("distance to the ODE solution")
        ax[k].set_ylim(1e-8, 1e-1)
        ax[k].text(0.97, 0.05, "softening " + ("physical" if phys else "comoving"),
                   transform=ax[k].transAxes, ha="right", fontsize=8)
        ax[k].legend(loc="upper left", fontsize=7)
    ax[2].set_xlabel("conformal time")
    ax[2].set_ylabel(r"$|C - C_0|/\max a|W|$ (comoving)")
    ax[2].legend(loc="upper left", fontsize=7)
    fs.save(fig, prefix + "_conv")
    plt.close(fig)


def main():
    full, half = sys.argv[1], sys.argv[2]
    fig = sys.argv[sys.argv.index("--fig") + 1] if "--fig" in sys.argv else None
    res = {}
    for name, phys in (("expand", False), ("expand_phys", True)):
        a = one(os.path.join(full, name), phys)
        b = one(os.path.join(half, name + "_h"), phys)
        res[name] = {"dt_0.002": a, "dt_0.001": b,
                     "ratio_position": [x/y for x, y in zip(a["max_position_error"],
                                                            b["max_position_error"])],
                     "ratio_C": a["C_drift_over_aW"]/b["C_drift_over_aW"]}
    print(json.dumps(res, indent=1))
    outdir = os.environ.get("NRPIC_RUN_DIR") or half
    with open(os.path.join(outdir, "t4_conv.json"), "w") as fp:
        json.dump(res, fp, indent=1)
        fp.write("\n")
    if fig:
        figure(full, half, fig)


if __name__ == "__main__":
    main()
